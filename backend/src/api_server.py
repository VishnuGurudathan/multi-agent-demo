"""
API Server launcher for the multi-agent system.
Provides a convenient way to start the FastAPI server.
"""
import sys
import os
from pathlib import Path
import uvicorn

def start_server():
    """Start the FastAPI server"""
    # Add the backend directory to Python path
    backend_dir = Path(__file__).parent.parent.absolute()
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    
    # Set PYTHONPATH environment variable
    os.environ["PYTHONPATH"] = str(backend_dir)
    
    # Import settings after path setup
    from .config.settings import get_settings
    settings = get_settings()
    
    # Start the server using configuration
    uvicorn.run(
        "src.api.entrypoint:app",  # Updated to use new entrypoint
        host=settings.HOST, 
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.RELOAD  # Now uses environment-based setting
    )

if __name__ == "__main__":
    start_server()
