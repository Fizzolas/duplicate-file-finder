#!/bin/bash
# Build script for creating standalone executable (Linux/Mac)

echo "================================================"
echo " Duplicate File Finder - Build Script"
echo "================================================"
echo ""

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller not found. Installing..."
    pip3 install pyinstaller
    echo ""
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist DuplicateFileFinder.spec
echo ""

# Build the executable
echo "Building executable..."
echo "This may take a few minutes..."
echo ""

pyinstaller --name="DuplicateFileFinder" \
    --onefile \
    --windowed \
    --add-data="core:core" \
    --add-data="gui:gui" \
    --add-data="utils:utils" \
    --hidden-import="PyQt6.QtCore" \
    --hidden-import="PyQt6.QtGui" \
    --hidden-import="PyQt6.QtWidgets" \
    --hidden-import="PIL" \
    --hidden-import="cv2" \
    --hidden-import="imagehash" \
    --hidden-import="psutil" \
    --hidden-import="numpy" \
    --collect-all="cv2" \
    --noconfirm \
    main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "BUILD FAILED!"
    echo "Check the error messages above."
    exit 1
fi

echo ""
echo "================================================"
echo " Build Complete!"
echo "================================================"
echo ""
echo "Executable location: dist/DuplicateFileFinder"
echo ""
echo "You can now:"
echo "1. Run ./dist/DuplicateFileFinder to test"
echo "2. Copy the executable anywhere you want"
echo "3. Share it with others (no Python needed!)"
echo ""
