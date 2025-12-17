# Build script for creating distributable package
# Run with: python build.py

import PyInstaller.__main__
import shutil
import os
from pathlib import Path

def build_executable():
    """Build standalone executable using PyInstaller."""
    print("Building Duplicate File Finder executable...")
    
    PyInstaller.__main__.run([
        'main.py',
        '--name=DuplicateFileFinder',
        '--onefile',
        '--windowed',
        '--icon=NONE',
        '--add-data=README.md;.',
        '--hidden-import=PIL._tkinter_finder',
        '--collect-all=cv2',
        '--noconfirm',
    ])
    
    print("\nBuild complete!")
    print("Executable location: dist/DuplicateFileFinder.exe")

if __name__ == "__main__":
    build_executable()
