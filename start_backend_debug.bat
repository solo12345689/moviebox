@echo off
cd backend
python -m uvicorn main:app --reload --port 8000 > ../backend_debug.log 2>&1
