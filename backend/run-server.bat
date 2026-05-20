@echo off
cd /d M:\dev\PET\backend
echo Starting backend with debug module...
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload