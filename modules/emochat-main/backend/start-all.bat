@echo off
echo ============================================
echo   Starting EmoHeal Platform
echo ============================================
 
echo.
echo [1/2] Starting Backend (FastAPI)...
start cmd /k "cd /d %~dp0backend && venv\Scripts\activate && python run.py"
 
echo [2/2] Starting Frontend (React)...
timeout /t 3 /nobreak >nul
start cmd /k "cd /d %~dp0frontend && npm run dev"
 
echo.
echo ============================================
echo   EmoHeal is starting up!
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo ============================================
pause