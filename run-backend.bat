@echo off
cd /d "%~dp0backend"
echo.
echo ========================================
echo  PET Debug System - Starting Backend
echo ========================================
echo.
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload