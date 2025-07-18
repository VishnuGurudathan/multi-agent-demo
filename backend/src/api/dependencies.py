"""
Shared dependencies for API routes.
Contains dependency injection factories and shared utilities.
"""
from typing import Dict, List, Any
import json
from datetime import datetime

from ..models import TaskRequest, TaskStatus
from ..system import MultiAgentSystem
from ..logger import setup_logger
from ..config.settings import BackendSettings

logger = setup_logger(__name__)

# Global variables for dependency injection
agent_system = None
active_connections: Dict[str, List[Any]] = {}

def get_agent_system() -> MultiAgentSystem:
    """
    Dependency injection factory for MultiAgentSystem.
    Provides a singleton instance for use across endpoints.
    """
    global agent_system
    if agent_system is None:
        agent_system = MultiAgentSystem()
    return agent_system

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
