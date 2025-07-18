#!/bin/bash
# Run script for Multi-Agent System
# Usage: ./run.sh [backend|ui|both]

set -e

MODE=${1:-both}
export PYTHONPATH=$(pwd)

case $MODE in
    "backend")
        echo "🚀 Starting Backend API Server..."
        cd backend
        python api_server.py
        ;;
    "ui")
        echo "🎨 Starting Streamlit UI..."
        streamlit run ui/src/app.py --server.address 0.0.0.0 --server.port 8501
        ;;
    "both")
        echo "🚀 Starting both Backend and UI..."
        echo "Backend will be available at: http://localhost:8000"
        echo "UI will be available at: http://localhost:8501"
        echo "API docs available at: http://localhost:8000/docs"
        
        # Start backend in background
        cd backend
        python api_server.py &
        BACKEND_PID=$!
        
        # Wait a moment for backend to start
        sleep 3
        
        # Start UI
        cd ..
        streamlit run ui/src/app.py --server.address 0.0.0.0 --server.port 8501 &
        UI_PID=$!
        
        echo "Backend PID: $BACKEND_PID"
        echo "UI PID: $UI_PID"
        
        # Wait for both processes
        wait $BACKEND_PID $UI_PID
        ;;
    *)
        echo "Usage: $0 [backend|ui|both]"
        exit 1
        ;;
esac
