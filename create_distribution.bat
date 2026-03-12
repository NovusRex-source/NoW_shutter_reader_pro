@echo off
REM Distribution Package Creator for Canon Shutter Counter Pro
REM Developer: Noel Wangler - NoW Photography (noelwangler.ch)

echo ================================================================
echo   Canon Shutter Counter Pro - Distribution Package Creator
echo ================================================================
echo.
echo Developer: Noel Wangler - NoW Photography
echo Website: https://noelwangler.ch
echo.

REM Check if dist folder exists
if not exist "dist\CanonShutterCounter.exe" (
    echo [ERROR] CanonShutterCounter.exe not found in dist folder
    echo Please run build_exe.bat first!
    pause
    exit /b 1
)

REM Check if exiftool exists
if not exist "exiftool.exe" (
    echo [WARNING] exiftool.exe not found in current directory
    echo.
    echo Please download ExifTool from: https://exiftool.org/
    echo And place exiftool.exe in this folder before creating distribution package.
    echo.
    pause
    exit /b 1
)

REM Create distribution folder
set DIST_FOLDER=CanonShutterCounter_v2.0_Distribution
if exist "%DIST_FOLDER%" rmdir /s /q "%DIST_FOLDER%"
mkdir "%DIST_FOLDER%"

echo Creating distribution package...
echo.

REM Copy main executable
echo [1/5] Copying CanonShutterCounter.exe...
copy "dist\CanonShutterCounter.exe" "%DIST_FOLDER%\" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy executable
    pause
    exit /b 1
)

REM Copy ExifTool
echo [2/5] Copying exiftool.exe...
copy "exiftool.exe" "%DIST_FOLDER%\" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy ExifTool
    pause
    exit /b 1
)

REM Copy documentation
echo [3/5] Copying documentation...
copy "CREDITS.txt" "%DIST_FOLDER%\" >nul
copy "LICENSE.txt" "%DIST_FOLDER%\" >nul
copy "README.txt" "%DIST_FOLDER%\" >nul
copy "BUILD_INFO.txt" "%DIST_FOLDER%\" >nul

REM Create quick start guide
echo [4/5] Creating Quick Start Guide...
echo ================================================================ > "%DIST_FOLDER%\QUICK_START.txt"
echo   CANON SHUTTER COUNTER PRO v2.0 - QUICK START >> "%DIST_FOLDER%\QUICK_START.txt"
echo ================================================================ >> "%DIST_FOLDER%\QUICK_START.txt"
echo. >> "%DIST_FOLDER%\QUICK_START.txt"
echo DEVELOPER >> "%DIST_FOLDER%\QUICK_START.txt"
echo --------- >> "%DIST_FOLDER%\QUICK_START.txt"
echo Noel Wangler - NoW Photography >> "%DIST_FOLDER%\QUICK_START.txt"
echo Website: https://noelwangler.ch >> "%DIST_FOLDER%\QUICK_START.txt"
echo. >> "%DIST_FOLDER%\QUICK_START.txt"
echo. >> "%DIST_FOLDER%\QUICK_START.txt"
echo HOW TO START >> "%DIST_FOLDER%\QUICK_START.txt"
echo ------------ >> "%DIST_FOLDER%\QUICK_START.txt"
echo 1. Double-click CanonShutterCounter.exe >> "%DIST_FOLDER%\QUICK_START.txt"
echo 2. No installation required! >> "%DIST_FOLDER%\QUICK_START.txt"
echo 3. No Python required! >> "%DIST_FOLDER%\QUICK_START.txt"
echo. >> "%DIST_FOLDER%\QUICK_START.txt"
echo. >> "%DIST_FOLDER%\QUICK_START.txt"
echo FEATURES >> "%DIST_FOLDER%\QUICK_START.txt"
echo -------- >> "%DIST_FOLDER%\QUICK_START.txt"
echo - Read CR3 file metadata >> "%DIST_FOLDER%\QUICK_START.txt"
echo - USB camera detection >> "%DIST_FOLDER%\QUICK_START.txt"
echo - Batch folder processing >> "%DIST_FOLDER%\QUICK_START.txt"
echo - Modern professional interface >> "%DIST_FOLDER%\QUICK_START.txt"
echo. >> "%DIST_FOLDER%\QUICK_START.txt"
echo. >> "%DIST_FOLDER%\QUICK_START.txt"
echo SUPPORTED CAMERAS >> "%DIST_FOLDER%\QUICK_START.txt"
echo ----------------- >> "%DIST_FOLDER%\QUICK_START.txt"
echo Canon EOS R, R1, R3, R5, R5 II, R6, R6 II, R6 III, R7, R8, RP >> "%DIST_FOLDER%\QUICK_START.txt"
echo. >> "%DIST_FOLDER%\QUICK_START.txt"
echo. >> "%DIST_FOLDER%\QUICK_START.txt"
echo SYSTEM REQUIREMENTS >> "%DIST_FOLDER%\QUICK_START.txt"
echo ------------------- >> "%DIST_FOLDER%\QUICK_START.txt"
echo - Windows 10/11 (64-bit) >> "%DIST_FOLDER%\QUICK_START.txt"
echo - 100 MB RAM >> "%DIST_FOLDER%\QUICK_START.txt"
echo - 50 MB disk space >> "%DIST_FOLDER%\QUICK_START.txt"
echo. >> "%DIST_FOLDER%\QUICK_START.txt"
echo. >> "%DIST_FOLDER%\QUICK_START.txt"
echo For full documentation, see README.txt >> "%DIST_FOLDER%\QUICK_START.txt"
echo For credits and licenses, see CREDITS.txt >> "%DIST_FOLDER%\QUICK_START.txt"
echo. >> "%DIST_FOLDER%\QUICK_START.txt"

REM Create ZIP if possible
echo [5/5] Creating ZIP archive...
where powershell >nul 2>&1
if %errorlevel% equ 0 (
    powershell -command "Compress-Archive -Path '%DIST_FOLDER%\*' -DestinationPath '%DIST_FOLDER%.zip' -Force"
    if errorlevel 1 (
        echo [WARNING] Failed to create ZIP, but folder is ready
    ) else (
        echo [SUCCESS] ZIP created: %DIST_FOLDER%.zip
    )
) else (
    echo [INFO] PowerShell not found, ZIP not created
    echo You can manually ZIP the folder: %DIST_FOLDER%
)

echo.
echo ================================================================
echo   Distribution Package Created Successfully!
echo ================================================================
echo.
echo Package contents:
echo - CanonShutterCounter.exe (main application)
echo - exiftool.exe (metadata tool)
echo - CREDITS.txt (full attribution)
echo - LICENSE.txt (license information)
echo - README.txt (user guide)
echo - BUILD_INFO.txt (technical details)
echo - QUICK_START.txt (quick start guide)
echo.
echo Folder: %DIST_FOLDER%
if exist "%DIST_FOLDER%.zip" (
    echo ZIP: %DIST_FOLDER%.zip
)
echo.
echo Ready for distribution!
echo.
echo Developer: Noel Wangler - NoW Photography
echo Website: https://noelwangler.ch
echo.
pause

