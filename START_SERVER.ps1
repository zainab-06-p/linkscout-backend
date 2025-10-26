# LinkScout Server Startup Script (PowerShell)
# Smart Analysis. Simple Answers.

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LinkScout Server" -ForegroundColor Cyan
Write-Host "  Smart Analysis. Simple Answers." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[✓] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[✗] ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "    Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[1/3] Checking dependencies..." -ForegroundColor Yellow

try {
    $flaskInstalled = pip show flask 2>&1 | Out-Null
    Write-Host "[✓] Dependencies appear to be installed" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "[!] Some dependencies are missing. Installing..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[✗] ERROR: Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[✓] Dependencies installed successfully" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/3] Checking server health..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host ""
    Write-Host "[!] WARNING: Server appears to be already running on port 5000" -ForegroundColor Yellow
    Write-Host "    If you want to restart it, press Ctrl+C and kill the existing process" -ForegroundColor Yellow
    Start-Sleep -Seconds 3
} catch {
    Write-Host "[✓] Port 5000 is available" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/3] Starting LinkScout server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Server: http://localhost:5000" -ForegroundColor Green
Write-Host "  Status: http://localhost:5000/health" -ForegroundColor Green
Write-Host ""
Write-Host "  Press Ctrl+C to stop server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start the server
python combined_server.py

Read-Host "Press Enter to exit"
