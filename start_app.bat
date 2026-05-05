@echo off
title BehavioralSense Launcher
echo.
echo  ===================================
echo    BehavioralSense - Starting Up
echo  ===================================
echo.

:: Start Backend (FastAPI)
echo [1/2] Starting Backend API on port 8000...
start "BehavioralSense Backend" cmd /k "cd /d "%~dp0backend" && pip install -r requirements.txt -q && python main.py"

:: Wait for backend to initialize
timeout /t 3 /nobreak >nul

:: Start Frontend (Vite React)
echo [2/2] Starting Frontend on port 5173...
start "BehavioralSense Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo  Both services are starting. Open your browser at:
echo    http://localhost:5173
echo.
pause
