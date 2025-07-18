#!/usr/bin/env python3
"""
Cross-platform run script for Multi-Agent System
Usage: python run.py [backend|ui|both]
"""
import sys
import os
import subprocess
import time
import signal
from pathlib import Path

def run_backend():
    """Start the backend API server"""
    print("🚀 Starting Backend API Server...")
    print("Backend will be available at: http://localhost:8000")
    print("API docs available at: http://localhost:8000/docs")
    
    os.chdir("backend")
    subprocess.run([sys.executable, "-m", "uvicorn", "src.api.entrypoint:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])

def run_ui():
    """Start the Streamlit UI"""
    print("🎨 Starting Streamlit UI...")
    print("UI will be available at: http://localhost:8501")
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "ui/src/app.py", 
        "--server.address", "0.0.0.0", 
        "--server.port", "8501"
    ])

def run_both():
    """Start both backend and UI"""
    print("🚀 Starting both Backend and UI...")
    print("Backend will be available at: http://localhost:8000")
    print("UI will be available at: http://localhost:8501") 
    print("API docs available at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop both services")
    
    # Start backend process
    os.chdir("backend")
    backend_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "src.api.entrypoint:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])
    
    # Wait for backend to start
    print("Waiting for backend to start...")
    time.sleep(3)
    
    # Start UI process
    os.chdir("..")
    ui_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run",
        "ui/src/app.py",
        "--server.address", "0.0.0.0",
        "--server.port", "8501"
    ])
    
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down services...")
        backend_process.terminate()
        ui_process.terminate()
        
        # Wait for graceful shutdown
        try:
            backend_process.wait(timeout=5)
            ui_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
            ui_process.kill()
        
        print("✅ Services stopped")
        sys.exit(0)
    
    # Handle Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Wait for both processes
        backend_process.wait()
        ui_process.wait()
    except Exception as e:
        print(f"Error: {e}")
        signal_handler(None, None)

def main():
    """Main entry point"""
    # Set PYTHONPATH to current directory
    current_dir = Path(__file__).parent.absolute()
    os.environ["PYTHONPATH"] = str(current_dir)
    
    # Get mode from command line
    mode = sys.argv[1] if len(sys.argv) > 1 else "both"
    
    if mode == "backend":
        run_backend()
    elif mode == "ui":
        run_ui()
    elif mode == "both":
        run_both()
    else:
        print("Usage: python run.py [backend|ui|both]")
        sys.exit(1)

if __name__ == "__main__":
    main()
