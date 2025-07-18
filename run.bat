@echo off
REM Run script for Multi-Agent System (Windows)
REM Usage: run.bat [backend|ui|both]

set MODE=%1
if "%MODE%"=="" set MODE=both
set PYTHONPATH=%cd%

if "%MODE%"=="backend" (
    echo 🚀 Starting Backend API Server...
    cd backend
    python api_server.py
) else if "%MODE%"=="ui" (
    echo 🎨 Starting Streamlit UI...
    streamlit run ui/src/app.py --server.address 0.0.0.0 --server.port 8501
) else if "%MODE%"=="both" (
    echo 🚀 Starting both Backend and UI...
    echo Backend will be available at: http://localhost:8000
    echo UI will be available at: http://localhost:8501
    echo API docs available at: http://localhost:8000/docs
    
    REM Start backend in background
    cd backend
    start "Backend" python api_server.py
    
    REM Wait a moment for backend to start
    timeout /t 3 /nobreak >nul
    
    REM Start UI
    cd ..
    streamlit run ui/src/app.py --server.address 0.0.0.0 --server.port 8501
) else (
    echo Usage: %0 [backend^|ui^|both]
    exit /b 1
)
