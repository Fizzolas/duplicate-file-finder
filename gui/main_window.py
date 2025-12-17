"""Main application window."""

import os
import psutil
import subprocess
import platform
from pathlib import Path
from datetime import datetime, timedelta
from collections import deque
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QTableWidget,
    QTableWidgetItem, QFileDialog, QListWidget, QTabWidget,
    QCheckBox, QSpinBox, QGroupBox, QMessageBox, QHeaderView,
    QAbstractItemView, QSplitter, QSlider, QFormLayout, QStyledItemDelegate,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPoint, QPropertyAnimation, QEasingCurve, QUrl, QSize
from PyQt6.QtGui import QDesktopServices, QCursor

from core.scanner import DuplicateScanner
from core.deletion import DeletionManager
from utils.config import ConfigManager
from gui.styles import APP_STYLESHEET


class ScannerThread(QThread):
    """Worker thread for scanning operations."""
    progress = pyqtSignal(int, str, int, int)  # percent, file, current_count, total_count
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, folders, options):
        super().__init__()
        self.folders = folders
        self.options = options
        self.scanner = None
        self._stop_requested = False
    
    def run(self):
        try:
            self.scanner = DuplicateScanner(self.options)
            self.scanner.progress_callback = self.progress.emit
            
            for folder in self.folders:
                if self._stop_requested:
                    break
                self.scanner.scan_directory(folder)
            
            if not self._stop_requested:
                duplicates = self.scanner.find_duplicates()
                self.finished.emit(duplicates)
        except Exception as e:
            self.error.emit(str(e))
    
    def stop(self):
        self._stop_requested = True
        if self.scanner:
            self.scanner.stop()


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.scanner_thread = None
        self.deletion_manager = DeletionManager(self.config)
        self.current_duplicates = []
        self.start_time = None
        self.files_processed = 0
        self.total_files = 0
        
        # For stable ETA: use coarse rolling window over last N seconds
        self.last_eta_update = None
        self.last_eta_files_processed = 0
        
        # Get system memory
        self.total_ram_mb = int(psutil.virtual_memory().total / (1024 * 1024))
        self.available_ram_mb = int(psutil.virtual_memory().available / (1024 * 1024))
        
        self.init_ui()
        self.setup_timer()
    
    # ... UI setup methods unchanged ...

    def start_scan(self):
        if self.folder_list.count() == 0:
            QMessageBox.warning(self, "No Folders", "Please add at least one folder to scan.")
            return
        
        folders = [self.folder_list.item(i).text() for i in range(self.folder_list.count())]
        
        options = {
            'exact_match': self.exact_match_cb.isChecked(),
            'similar_images': self.similar_images_cb.isChecked(),
            'similar_videos': self.similar_videos_cb.isChecked(),
            'diff_resolution': self.diff_resolution_cb.isChecked(),
            'diff_format': self.diff_format_cb.isChecked(),
            'similarity_threshold': self.config.get('similarity_threshold', 90),
            'thread_count': self.config.get('thread_count', 4),
            'max_memory_mb': self.config.get('max_memory_mb', 2048)
        }
        
        self.start_time = datetime.now()
        self.files_processed = 0
        self.total_files = 0
        self.last_eta_update = None
        self.last_eta_files_processed = 0
        self.timer.start(500)
        
        self.scanner_thread = ScannerThread(folders, options)
        self.scanner_thread.progress.connect(self.update_progress)
        self.scanner_thread.finished.connect(self.scan_finished)
        self.scanner_thread.error.connect(self.scan_error)
        
        self.scanner_thread.start()
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.background_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Scanning…")
        self.eta_label.setText("Calculating ETA…")
    
    def update_progress(self, percent, current_file, current_count, total_count):
        """Update progress bar, status, and a smoothed ETA."""
        self.progress_bar.setValue(percent)
        self.files_processed = current_count
        self.total_files = total_count
        
        file_name = Path(current_file).name
        self.status_label.setText(f"Scanning: {file_name} ({current_count}/{total_count})")
        
        # Only recompute ETA at most once per second to avoid flicker
        now = datetime.now()
        if self.last_eta_update is None:
            self.last_eta_update = now
            self.last_eta_files_processed = current_count
            return
        
        delta_t = (now - self.last_eta_update).total_seconds()
        delta_files = current_count - self.last_eta_files_processed
        
        # Need at least 1s and some files progressed to update ETA
        if delta_t >= 1.0 and delta_files > 0:
            rate = delta_files / delta_t  # files per second over last window
            remaining_files = max(0, total_count - current_count)
            eta_seconds = remaining_files / rate if rate > 0 else 0
            
            if eta_seconds <= 0:
                self.eta_label.setText("ETA: --")
            elif eta_seconds < 60:
                self.eta_label.setText(f"ETA: {int(eta_seconds)}s")
            elif eta_seconds < 3600:
                self.eta_label.setText(f"ETA: {int(eta_seconds/60)}m {int(eta_seconds%60)}s")
            else:
                hours = int(eta_seconds/3600)
                minutes = int((eta_seconds%3600)/60)
                self.eta_label.setText(f"ETA: {hours}h {minutes}m")
            
            # Update window for next smoothing interval
            self.last_eta_update = now
            self.last_eta_files_processed = current_count
