@echo off
echo.
echo ========================================
echo   LinkScout Web Interface
echo   Smart Analysis. Simple Answers.
echo ========================================
echo.
echo [1/2] Checking if backend server is running...
timeout /t 2 /nobreak >nul

echo [2/2] Starting Next.js Development Server...
echo.
echo Web interface will be available at:
echo http://localhost:3000
echo.
echo ========================================
echo.

cd web_interface\LinkScout
call npm run dev

pause
