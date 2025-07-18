"""
Task-related API routes for the multi-agent system.
Handles task creation, status checking, results, and management.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from typing import Dict, List, Any
import json
import asyncio
from datetime import datetime

from ...models import TaskRequest, TaskStatus
from ...system import MultiAgentSystem
from ...logger import setup_logger
from ...config.settings import get_settings, BackendSettings
from ..dependencies import get_agent_system, notify_task_update, process_task_and_notify

logger = setup_logger(__name__)
router = APIRouter()

@router.post("", response_model=Dict[str, Any])
async def create_task(task_request: TaskRequest, background_tasks: BackgroundTasks,
                     settings: BackendSettings = Depends(get_settings)):
    """Create a new task for the multi-agent system with async processing"""
    try:
        logger.info(f"Creating task: {task_request.task_id}")
        # Start processing in background with real-time updates
        background_tasks.add_task(process_task_and_notify, task_request, settings)
        
        return {
            "task_id": task_request.task_id,
            "status": "accepted",
            "message": "Task submitted for processing",
            "websocket_url": f"/ws/tasks/{task_request.task_id}"
        }
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}", response_model=Dict[str, Any])
async def get_task_status(task_id: str, 
                         agent_system: MultiAgentSystem = Depends(get_agent_system),
                         settings: BackendSettings = Depends(get_settings)):
    """Get the current status of a task"""
    logger.info(f"Fetching status for task {task_id}")
    state = agent_system.get_task_status(task_id)
    if not state:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task_id,
        "status": state.status,
        "current_agent": state.current_agent,
        "next_agent": state.next_agent,
        "completed_agents": state.completed_agents,
        "results": state.results,
        "errors": state.errors,
        "iteration_count": state.iteration_count,
        "max_iterations": state.max_iterations,
        "progress": len(state.completed_agents) / settings.DEFAULT_AGENT_COUNT * 100,
        "websocket_url": f"/ws/tasks/{task_id}"
    }

@router.get("/{task_id}/results", response_model=Dict[str, Any])
async def get_task_results(task_id: str, 
                          agent_system: MultiAgentSystem = Depends(get_agent_system)):
    """Get the final results of a completed task"""
    state = agent_system.get_task_status(task_id)
    if not state:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if state.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=409, detail="Task not completed yet")
    
    return {
        "task_id": task_id,
        "results": state.results,
        "messages": state.messages,
        "completed_agents": state.completed_agents,
        "final_report": state.final_report,
        "status": state.status,
        "iteration_count": state.iteration_count
    }

@router.get("", response_model=List[Dict[str, Any]])
async def list_tasks(agent_system: MultiAgentSystem = Depends(get_agent_system),
                    settings: BackendSettings = Depends(get_settings)):
    """List all active tasks"""
    active_tasks = agent_system.list_active_tasks()
    return [
        {
            "task_id": task_id,
            "status": state.status,
            "current_agent": state.current_agent,
            "next_agent": state.next_agent,
            "task_type": state.task_type,
            "query": state.query[:100] + "..." if len(state.query) > 100 else state.query,
            "progress": len(state.completed_agents) / settings.DEFAULT_AGENT_COUNT * 100,
            "iteration_count": state.iteration_count,
            "errors_count": len(state.errors),
            "created_at": state.metadata.get("created_at", ""),
            "websocket_url": f"/ws/tasks/{task_id}"
        }
        for task_id, state in active_tasks.items()
    ]

@router.delete("/{task_id}")
async def cancel_task(task_id: str, 
                     agent_system: MultiAgentSystem = Depends(get_agent_system)):
    """Cancel a task"""
    state = agent_system.get_task_status(task_id)
    if not state:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Mark as cancelled
    state.status = TaskStatus.FAILED
    state.errors.append("Task cancelled by user")
    
    # Notify connected clients
    await notify_task_update(task_id, {
        "status": "cancelled",
        "message": "Task cancelled by user"
    })
    
    return {"message": "Task cancelled"}

@router.get("/{task_id}/stream")
async def stream_task_progress(task_id: str,
                              agent_system: MultiAgentSystem = Depends(get_agent_system),
                              settings: BackendSettings = Depends(get_settings)):
    """Stream task progress updates (Server-Sent Events alternative to WebSocket)"""
    
    async def generate_updates():
        while True:
            state = agent_system.get_task_status(task_id)
            if not state:
                yield f"data: {json.dumps({'error': 'Task not found'})}\n\n"
                break
                
            update = {
                "task_id": task_id,
                "status": state.status,
                "current_agent": state.current_agent,
                "completed_agents": state.completed_agents,
                "progress": len(state.completed_agents) / settings.DEFAULT_AGENT_COUNT * 100,
                "iteration_count": state.iteration_count,
                "timestamp": datetime.now().isoformat()
            }
            
            yield f"data: {json.dumps(update)}\n\n"
            
            if state.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break
                
            await asyncio.sleep(settings.WS_HEARTBEAT_INTERVAL // 15)  # Update every 2 seconds (30/15)
    
    return StreamingResponse(generate_updates(), media_type="text/plain")
