@echo off
echo ======================================================================
echo    Starting LexiGuard AI - Contract Intelligence & Risk Scoring
echo ======================================================================
echo.

start "LexiGuard AI Backend (FastAPI :8000)" cmd /k "cd /d %~dp0backend && python run.py"
start "LexiGuard AI Frontend (Vite :5173)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Servers starting up!
echo   * Backend API docs: http://localhost:8000/docs
echo   * Frontend Web UI:  http://localhost:5173
echo.
