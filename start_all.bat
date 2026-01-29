@echo off
echo.
echo ===============================================
echo    CyberSentryAI - Full Stack Startup
echo ===============================================
echo.

cd /d "%~dp0"

echo [1/3] Starting Backend Server...
start "CyberSentryAI Backend" cmd /k "cd backend && C:\Users\yashkumar\Desktop\Projects\.venv\Scripts\python.exe simple_server.py"
timeout /t 3 /nobreak >nul

echo [2/3] Installing Frontend Dependencies...
cd frontend
if not exist "node_modules" (
    echo Installing npm packages...
    call npm install
)

echo [3/3] Starting Frontend Dev Server...
start "CyberSentryAI Frontend" cmd /k "npm run dev"

echo.
echo ===============================================
echo    Both servers started successfully!
echo ===============================================
echo    Backend:  http://localhost:8000
echo    Frontend: http://localhost:5173
echo    API Docs: http://localhost:8000/docs
echo ===============================================
echo.
pause
