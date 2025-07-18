"""
WebSocket routes for real-time task updates.
Provides WebSocket endpoints for live task monitoring.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List
import json

from ...system import MultiAgentSystem
from ...logger import setup_logger
from ...config.settings import get_settings, BackendSettings
from ..dependencies import get_agent_system, active_connections

logger = setup_logger(__name__)
router = APIRouter()

@router.websocket("/tasks/{task_id}")
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
