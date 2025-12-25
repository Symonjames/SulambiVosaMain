@echo off
echo Starting Sulambi Backend and Frontend...

REM Start Backend in new window
start "Sulambi Backend" cmd /k "cd /d "c:\Users\Symon\Desktop\CODE FOR SULAMBI\Technology Transfer _ Sulambi VMS\Source Code\sulambi-backend-main\sulambi-backend-main" && python server.py"

REM Wait 2 seconds
timeout /t 2 /nobreak >nul

REM Start Frontend in new window
start "Sulambi Frontend" cmd /k "cd /d "C:\Users\Symon\Desktop\CODE FOR SULAMBI\Technology Transfer _ Sulambi VMS\Source Code\sulambi-frontend-main\sulambi-frontend-main" && npm install && npm run dev"

echo.
echo Both servers are starting in separate windows...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
pause

