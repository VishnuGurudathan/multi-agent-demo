"""
FastAPI application entrypoint for the multi-agent system.
Provides clean modular architecture with separated route concerns.
Enhanced with dependency injection and proper async task handling.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from ..logger import setup_logger, configure_root_logging
from .dependencies import get_agent_system, active_connections
from .routes import tasks, websocket, agents, health

# Configure root logging early to ensure all logs are visible
configure_root_logging()

logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown"""
    # Startup
    logger.info("🚀 Starting Multi-Agent System API v2.0")
    
    # Initialize the agent system (singleton pattern)
    agent_system = get_agent_system()
    logger.info("✅ Agent system initialized")
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
    description="Multi-agent AI system with LangGraph orchestration, async task support, and modular architecture",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"],  # Streamlit and React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules with proper prefixes and tags
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
app.include_router(agents.router, prefix="/agents", tags=["Agents"])
app.include_router(health.router, tags=["System"])

# Example usage with uvicorn:
# uvicorn backend.src.api.entrypoint:app --host 0.0.0.0 --port 8000 --reload
