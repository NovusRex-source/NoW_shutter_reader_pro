@echo off
REM Canon R-Series Shutter Counter - Main Launcher

echo ================================================
echo   Canon R-Series Shutter Counter v2.0
echo ================================================
echo.
echo Starting main application...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Launch the integrated application
python CanonShutterCounter.py

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to launch application
    echo.
    pause
)
