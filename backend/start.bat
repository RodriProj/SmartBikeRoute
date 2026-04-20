@echo off
echo A iniciar SmartBike Routes Backend...
cd /d %~dp0
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
