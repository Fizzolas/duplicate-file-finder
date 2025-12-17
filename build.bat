@echo off
echo ========================================
echo Duplicate File Finder - Build Script
echo ========================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Installing/upgrading PyInstaller...
python -m pip install --upgrade pyinstaller

echo.
echo Building executable...
python build.py

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo The executable is located in the 'dist' folder.
echo You can now distribute 'DuplicateFileFinder.exe'
echo.
pause
