#!/bin/bash

echo "========================================"
echo "Duplicate File Finder - Build Script"
echo "========================================"
echo ""

echo "Checking Python installation..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python is not installed or not in PATH"
    exit 1
fi

echo ""
echo "Installing/upgrading PyInstaller..."
python3 -m pip install --upgrade pyinstaller

echo ""
echo "Building executable..."
python3 build.py

echo ""
echo "========================================"
echo "Build Complete!"
echo "========================================"
echo ""
echo "The executable is located in the 'dist' folder."
echo ""
