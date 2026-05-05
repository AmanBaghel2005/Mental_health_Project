@echo off
echo Starting backend...
start cmd /k "cd backend && python main.py"

echo Starting frontend...
start cmd /k "cd frontend && npm run dev"

echo Project started!
pause