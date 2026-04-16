@echo off
title TINDI CMMS Server
cd /d "C:\Users\Jungle\Desktop\byron22"

echo ========================================
echo   TINDI CMMS - Starting Server...
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Virtual environment activated.
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo Virtual environment activated.
) else (
    echo No virtual environment found, using system Python.
)

echo Starting TINDI CMMS on http://localhost:5000
echo Auto-launching browser...
timeout /t 3 /nobreak > nul
start http://localhost:5000

echo.
echo Press Ctrl+C to stop the server.
echo.

python run.py

pause
