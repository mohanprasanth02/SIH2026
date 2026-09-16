@echo off
title SatQuery AI - Launcher
echo ====================================================
echo  SatQuery AI - Starting Backend and Frontend
echo ====================================================

set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe
if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python
)

echo [1/2] Launching Backend on http://localhost:8000 ...
start "SatQuery AI - Backend (FastAPI)" cmd /k "cd /d %~dp0backend && "%PYTHON_EXE%" -m uvicorn app.main:app --reload --port 8000"

echo [2/2] Launching Frontend on http://localhost:5173 ...
start "SatQuery AI - Frontend (Vite)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ====================================================
echo Services started!
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/api/docs
echo ====================================================
