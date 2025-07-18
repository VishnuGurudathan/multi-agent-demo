"""
FastAPI endpoints for the multi-agent system.
Provides REST API interface for task management and monitoring.
Enhanced with proper async task handling for long-running workflows.
Uses dependency injection for better testability and maintainability.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, List, Any
import json
from datetime import datetime

from ..models import TaskRequest, AgentState, TaskStatus
from ..system import MultiAgentSystem
from ..logger import setup_logger
from ..config.settings import get_settings, BackendSettings

logger = setup_logger(__name__)

# Global variables
agent_system = None
active_connections: Dict[str, List[WebSocket]] = {}

def get_agent_system() -> MultiAgentSystem:
    """
    Dependency injection factory for MultiAgentSystem.
    Provides a singleton instance for use across endpoints.
    """
    global agent_system
    if agent_system is None:
        agent_system = MultiAgentSystem()
    return agent_system

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Simple lifespan handler for startup and shutdown"""
    # Startup
    logger.info("🚀 Starting Multi-Agent System API")
    global agent_system
    agent_system = MultiAgentSystem()
    logger.info("✅ System ready")
    
    yield  # Server running
    
    # Shutdown
    logger.info("🛑 Shutting down...")
    
    # Close all WebSocket connections
    for task_id, connections in active_connections.items():
        for ws in connections:
            try:
                await ws.close(code=1001, reason="Server shutdown")
            except:
                pass
    
    active_connections.clear()
    logger.info("✅ Shutdown complete")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Multi-Agent System API",
    version="2.0.0",
    description="Multi-agent AI system with LangGraph orchestration and async task support",
    lifespan=lifespan
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"],  # Streamlit and React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Task status storage for real-time updates
task_updates: Dict[str, Dict] = {}

async def notify_task_update(task_id: str, update: Dict):
    """Notify all connected clients about task updates"""
    if task_id in active_connections:
        message = json.dumps({
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "update": update
        })
        
        # Send to all connected websockets for this task
        for connection in active_connections[task_id]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending websocket message: {e}")

async def process_task_and_notify(task_request: TaskRequest, settings: BackendSettings):
    """Process task and send real-time updates"""
    task_id = task_request.task_id
    agent_system = get_agent_system()

    try:
        # Send initial status
        await notify_task_update(task_id, {
            "status": "started",
            "message": "Task processing started"
        })

        # Process the task
        result = await agent_system.process_task(task_request)

        # Send completion status
        await notify_task_update(task_id, {
            "status": "completed" if result.status == TaskStatus.COMPLETED else "failed",
            "message": "Task processing completed",
            "result": {
                "status": result.status,
                "completed_agents": result.completed_agents,
                "errors": result.errors
            }
        })

    except Exception as e:
        logger.error(f"Error processing task {task_id}: {str(e)}")
        await notify_task_update(task_id, {
            "status": "error",
            "message": f"Task processing error: {str(e)}"
        })

@app.websocket("/ws/tasks/{task_id}")
async def websocket_task_updates(websocket: WebSocket, task_id: str, 
                                agent_system: MultiAgentSystem = Depends(get_agent_system),
                                settings: BackendSettings = Depends(get_settings)):
    """WebSocket endpoint for real-time task updates"""
    await websocket.accept()
    
    # Add connection to active connections
    if task_id not in active_connections:
        active_connections[task_id] = []
    active_connections[task_id].append(websocket)
    
    try:
        # Send any existing task status
        task_state = agent_system.get_task_status(task_id)
        if task_state:
            await websocket.send_text(json.dumps({
                "task_id": task_id,
                "status": task_state.status,
                "current_agent": task_state.current_agent,
                "completed_agents": task_state.completed_agents,
                "progress": len(task_state.completed_agents) / settings.DEFAULT_AGENT_COUNT * 100
            }))
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        # Remove connection when client disconnects
        if task_id in active_connections:
            active_connections[task_id].remove(websocket)
            if not active_connections[task_id]:
                del active_connections[task_id]

@app.post("/tasks", response_model=Dict[str, Any])
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

@app.get("/tasks/{task_id}", response_model=Dict[str, Any])
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

@app.get("/tasks/{task_id}/results", response_model=Dict[str, Any])
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

@app.get("/tasks", response_model=List[Dict[str, Any]])
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

@app.delete("/tasks/{task_id}")
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

@app.get("/tasks/{task_id}/stream")
async def stream_task_progress(task_id: str,
                              agent_system: MultiAgentSystem = Depends(get_agent_system),
                              settings: BackendSettings = Depends(get_settings)):
    """Stream task progress updates (Server-Sent Events alternative to WebSocket)"""
    from fastapi.responses import StreamingResponse
    import asyncio
    
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

@app.get("/health")
async def health_check(agent_system: MultiAgentSystem = Depends(get_agent_system)):
    """Health check endpoint"""
    logger.info("Health check requested")
    active_tasks = agent_system.list_active_tasks()
    return {
        "status": "healthy",
        "active_tasks": len(active_tasks),
        "system": "Multi-Agent System with LangGraph",
        "version": "1.0.0",
        "features": {
            "websocket_support": True,
            "real_time_updates": True,
            "async_processing": True,
            "task_streaming": True
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/agents")
async def get_agent_info(settings: BackendSettings = Depends(get_settings)):
    """Get information about available agents"""
    from ..models.enums import AgentRole, AGENT_CAPABILITIES
    
    return {
        "agents": {
            role.value: {
                "role": role.value,
                "capabilities": role.capabilities,
                "description": f"{role.value.title()} agent for {', '.join(role.capabilities)}"
            }
            for role in AgentRole
        },
        "workflow": {
            "entry_point": AgentRole.SUPERVISOR.value,
            "routing": "Dynamic routing based on task requirements",
            "max_iterations": settings.MAX_ITERATIONS,
            "max_agents": settings.MAX_AGENTS
        }
    }

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Multi-Agent System API v1.0",
        "description": "Multi-agent AI system with async task processing",
        "features": {
            "real_time_updates": "WebSocket support for live task progress",
            "async_processing": "Background task processing with status tracking",
            "agent_orchestration": "LangGraph-based multi-agent workflow",
            "api_documentation": "Interactive API docs available"
        },
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "tasks": "/tasks",
            "agents": "/agents",
            "websocket": "/ws/tasks/{task_id}",
            "streaming": "/tasks/{task_id}/stream"
        },
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Example usage with uvicorn:
# uvicorn backend.src.api.endpoints:app --host 0.0.0.0 --port 8000 --reload
