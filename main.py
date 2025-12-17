#!/usr/bin/env python3
"""
Duplicate File Finder
Advanced GUI application for finding and removing duplicate images and videos.
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import setup_logger

def main():
    """Main entry point for the application."""
    setup_logger()
    
    app = QApplication(sys.argv)
    app.setApplicationName("Duplicate File Finder")
    app.setOrganizationName("DupFinder")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
