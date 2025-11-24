@echo off
cd /d "%~dp0"
python -m uvicorn backend.main:app --reload --port 8000
