@echo off
REM Build script for creating standalone Windows executable

echo ================================================
echo  Duplicate File Finder - Build Script
echo ================================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    echo.
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "DuplicateFileFinder.spec" del "DuplicateFileFinder.spec"
echo.

REM Build the executable
echo Building executable...
echo This may take a few minutes...
echo.

python -m PyInstaller --name="DuplicateFileFinder" ^
    --onefile ^
    --windowed ^
    --icon=NONE ^
    --add-data="core;core" ^
    --add-data="gui;gui" ^
    --add-data="utils;utils" ^
    --hidden-import="PyQt6.QtCore" ^
    --hidden-import="PyQt6.QtGui" ^
    --hidden-import="PyQt6.QtWidgets" ^
    --hidden-import="PIL" ^
    --hidden-import="cv2" ^
    --hidden-import="imagehash" ^
    --hidden-import="psutil" ^
    --hidden-import="numpy" ^
    --collect-all="cv2" ^
    --noconfirm ^
    main.py

if errorlevel 1 (
    echo.
    echo BUILD FAILED!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ================================================
echo  Build Complete!
echo ================================================
echo.
echo Executable location: dist\DuplicateFileFinder.exe
echo.
echo You can now:
echo 1. Run dist\DuplicateFileFinder.exe to test
echo 2. Copy the .exe file anywhere you want
echo 3. Share it with others (no Python needed!)
echo.

pause
