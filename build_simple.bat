@echo off
REM Simple build - Creates standalone EXE with everything bundled

echo ================================================
echo   Building Standalone EXE
echo ================================================
echo.

REM Install PyInstaller if needed
pip install pyinstaller 2>nul

echo Building... Please wait...
echo.

REM Create single executable with all dependencies
pyinstaller --onefile --windowed --name "CanonShutterCounter" --icon="Icon\now_shuttercount.png" --add-data "Icon;Icon" --clean CanonShutterCounter.py

if exist "dist\CanonShutterCounter.exe" (
    echo.
    echo ================================================
    echo   SUCCESS!
    echo ================================================
    echo.
    echo Executable created: dist\CanonShutterCounter.exe
    echo.
    echo IMPORTANT: Copy exiftool.exe to the same folder
    echo as CanonShutterCounter.exe for full functionality
    echo.
    echo The EXE is portable - copy it anywhere!
    echo.
) else (
    echo.
    echo Build failed. Check errors above.
    echo.
)

pause
