"""
Health check and system information routes.
Provides health status and API documentation endpoints.
"""
from fastapi import APIRouter, Depends
from datetime import datetime

from ...system import MultiAgentSystem
from ...logger import setup_logger
from ..dependencies import get_agent_system

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check(agent_system: MultiAgentSystem = Depends(get_agent_system)):
    """Health check endpoint"""
    logger.info("Health check requested")
    active_tasks = agent_system.list_active_tasks()
    return {
        "status": "healthy",
        "active_tasks": len(active_tasks),
        "system": "Multi-Agent System with LangGraph",
        "version": "2.0.0",
        "features": {
            "websocket_support": True,
            "real_time_updates": True,
            "async_processing": True,
            "task_streaming": True,
            "dependency_injection": True,
            "modular_routing": True
        },
        "timestamp": datetime.now().isoformat()
    }

@router.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Multi-Agent System API v2.0",
        "description": "Multi-agent AI system with async task processing and modular architecture",
        "features": {
            "real_time_updates": "WebSocket support for live task progress",
            "async_processing": "Background task processing with status tracking",
            "agent_orchestration": "LangGraph-based multi-agent workflow",
            "api_documentation": "Interactive API docs available",
            "dependency_injection": "Clean dependency injection pattern",
            "modular_routing": "Organized route structure with separation of concerns"
        },
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "tasks": "/tasks",
            "agents": "/agents",
            "websocket": "/ws/tasks/{task_id}",
            "streaming": "/tasks/{task_id}/stream"
        },
        "architecture": {
            "pattern": "Modular FastAPI with APIRouter",
            "dependency_injection": "Singleton pattern with FastAPI Depends",
            "real_time": "WebSocket + Server-Sent Events",
            "async": "Background task processing"
        },
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }
