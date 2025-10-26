@echo off
REM LinkScout Server Startup Script
REM Smart Analysis. Simple Answers.

echo ========================================
echo   LinkScout Server
echo   Smart Analysis. Simple Answers.
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo.
    echo Some dependencies are missing. Installing...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [2/3] Checking server health...
curl -s http://localhost:5000/health >nul 2>&1
if not errorlevel 1 (
    echo.
    echo WARNING: Server appears to be already running on port 5000
    echo If you want to restart it, press Ctrl+C and kill the existing process
    timeout /t 3 >nul
)

echo [3/3] Starting LinkScout server...
echo.
echo ========================================
echo   Server: http://localhost:5000
echo   Status: http://localhost:5000/health
echo.
echo   Press Ctrl+C to stop server
echo ========================================
echo.

python combined_server.py

pause
