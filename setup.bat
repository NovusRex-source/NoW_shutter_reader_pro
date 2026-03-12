@echo off
REM Complete setup script for Canon Shutter Counter

echo ================================================
echo   Canon R-Series Shutter Counter - Setup
echo ================================================
echo.
echo This will install all required dependencies.
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Install Python packages
echo Installing Python dependencies...
echo.
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [WARNING] Some packages may have failed to install
    echo This is normal - optional packages may skip on some systems
) else (
    echo.
    echo [OK] Python packages installed successfully
)

echo.
echo ================================================
echo   Checking for ExifTool...
echo ================================================
echo.

REM Check if ExifTool is installed
exiftool -ver >nul 2>&1
if not errorlevel 1 (
    echo [OK] ExifTool is already installed
    exiftool -ver
    goto :finish
)

REM Check if ExifTool exists locally
if exist "exiftool.exe" (
    echo [OK] ExifTool found in current directory
    goto :finish
)

echo [INFO] ExifTool not found. Attempting installation...
echo.

REM Try to install via winget
winget --version >nul 2>&1
if not errorlevel 1 (
    echo Attempting to install via winget...
    winget install exiftool
    if not errorlevel 1 (
        echo [OK] ExifTool installed via winget
        goto :finish
    )
)

echo.
echo [INFO] Automatic installation not available
echo.
echo Please install ExifTool manually:
echo   1. Download from: https://exiftool.org/
echo   2. Extract exiftool.exe to this folder
echo   OR
echo   3. Install using: winget install exiftool
echo.

:finish
echo.
echo ================================================
echo   Setup Complete!
echo ================================================
echo.
echo You can now use the Canon Shutter Counter:
echo.
echo   [GUI] Modern Interface
echo     - Run: launch_gui.bat
echo.
echo   [CLI] Enhanced Command Line
echo     - Run: python shutter_reader_modern.py your_image.CR3
echo.
echo   [WEB] Dashboard
echo     - Run: open_dashboard.bat
echo.
echo   [EASIEST] EOSInfo (for USB reading)
echo     - Run: download_eosinfo.bat
echo.
echo ================================================
pause
