"""Main application window."""

import os
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QTableWidget,
    QTableWidgetItem, QFileDialog, QListWidget, QTabWidget,
    QCheckBox, QSpinBox, QGroupBox, QMessageBox, QHeaderView,
    QAbstractItemView, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QPixmap

from core.scanner import DuplicateScanner
from core.deletion import DeletionManager
from utils.config import ConfigManager
from gui.styles import APP_STYLESHEET


class ScannerThread(QThread):
    """Worker thread for scanning operations."""
    progress = pyqtSignal(int, str)
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
        
        self.init_ui()
        self.setup_timer()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Duplicate File Finder")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(APP_STYLESHEET)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Top section: Folder selection and options
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Folder selection panel
        folder_panel = self.create_folder_panel()
        top_splitter.addWidget(folder_panel)
        
        # Options panel
        options_panel = self.create_options_panel()
        top_splitter.addWidget(options_panel)
        
        top_splitter.setStretchFactor(0, 1)
        top_splitter.setStretchFactor(1, 1)
        layout.addWidget(top_splitter)
        
        # Control buttons
        control_layout = self.create_control_buttons()
        layout.addLayout(control_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to scan")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Results table
        self.create_results_section(layout)
        
        # Deletion buttons
        deletion_layout = self.create_deletion_buttons()
        layout.addLayout(deletion_layout)
    
    def create_folder_panel(self):
        """Create folder selection panel."""
        group = QGroupBox("Scan Folders")
        layout = QVBoxLayout()
        
        self.folder_list = QListWidget()
        layout.addWidget(self.folder_list)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Folder")
        add_btn.clicked.connect(self.add_folder)
        btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_folder)
        btn_layout.addWidget(remove_btn)
        
        layout.addLayout(btn_layout)
        group.setLayout(layout)
        return group
    
    def create_options_panel(self):
        """Create scan options panel."""
        group = QGroupBox("Scan Options")
        layout = QVBoxLayout()
        
        self.exact_match_cb = QCheckBox("Exact Match (Hash-based)")
        self.exact_match_cb.setChecked(True)
        layout.addWidget(self.exact_match_cb)
        
        self.similar_images_cb = QCheckBox("Similar Images (Perceptual)")
        self.similar_images_cb.setChecked(True)
        layout.addWidget(self.similar_images_cb)
        
        self.similar_videos_cb = QCheckBox("Similar Videos (Content)")
        self.similar_videos_cb.setChecked(True)
        layout.addWidget(self.similar_videos_cb)
        
        self.diff_resolution_cb = QCheckBox("Different Resolutions")
        self.diff_resolution_cb.setChecked(True)
        layout.addWidget(self.diff_resolution_cb)
        
        self.diff_format_cb = QCheckBox("Different Formats")
        self.diff_format_cb.setChecked(True)
        layout.addWidget(self.diff_format_cb)
        
        # Similarity threshold
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Similarity Threshold (%):" ))
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(50, 100)
        self.threshold_spin.setValue(self.config.get('similarity_threshold', 90))
        threshold_layout.addWidget(self.threshold_spin)
        layout.addLayout(threshold_layout)
        
        # Thread count
        thread_layout = QHBoxLayout()
        thread_layout.addWidget(QLabel("Thread Count:"))
        self.thread_spin = QSpinBox()
        self.thread_spin.setRange(1, 16)
        self.thread_spin.setValue(self.config.get('thread_count', 4))
        thread_layout.addWidget(self.thread_spin)
        layout.addLayout(thread_layout)
        
        layout.addStretch()
        group.setLayout(layout)
        return group
    
    def create_control_buttons(self):
        """Create control buttons."""
        layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Scan")
        self.start_btn.setObjectName("startButton")
        self.start_btn.clicked.connect(self.start_scan)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_scan)
        layout.addWidget(self.stop_btn)
        
        self.background_btn = QPushButton("Run in Background")
        self.background_btn.setEnabled(False)
        self.background_btn.clicked.connect(self.run_background)
        layout.addWidget(self.background_btn)
        
        layout.addStretch()
        return layout
    
    def create_results_section(self, parent_layout):
        """Create results display section."""
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "Group", "File Path", "Size (MB)", "Resolution", 
            "Format", "Hash", "Keep/Delete"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        parent_layout.addWidget(self.results_table)
    
    def create_deletion_buttons(self):
        """Create deletion control buttons."""
        layout = QHBoxLayout()
        
        delete_all_but_one = QPushButton("Delete All But One")
        delete_all_but_one.setObjectName("deleteButton")
        delete_all_but_one.clicked.connect(lambda: self.delete_duplicates('keep_one'))
        layout.addWidget(delete_all_but_one)
        
        delete_all_but_best = QPushButton("Delete All But Best Quality")
        delete_all_but_best.setObjectName("deleteButton")
        delete_all_but_best.clicked.connect(lambda: self.delete_duplicates('keep_best'))
        layout.addWidget(delete_all_but_best)
        
        layout.addStretch()
        
        clear_btn = QPushButton("Clear Results")
        clear_btn.clicked.connect(self.clear_results)
        layout.addWidget(clear_btn)
        
        return layout
    
    def setup_timer(self):
        """Setup timer for elapsed time display."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_elapsed_time)
    
    def add_folder(self):
        """Add folder to scan list."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Scan")
        if folder:
            self.folder_list.addItem(folder)
    
    def remove_folder(self):
        """Remove selected folder from list."""
        current_row = self.folder_list.currentRow()
        if current_row >= 0:
            self.folder_list.takeItem(current_row)
    
    def start_scan(self):
        """Start the scanning process."""
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
            'similarity_threshold': self.threshold_spin.value(),
            'thread_count': self.thread_spin.value()
        }
        
        self.start_time = datetime.now()
        self.timer.start(1000)
        
        self.scanner_thread = ScannerThread(folders, options)
        self.scanner_thread.progress.connect(self.update_progress)
        self.scanner_thread.finished.connect(self.scan_finished)
        self.scanner_thread.error.connect(self.scan_error)
        
        self.scanner_thread.start()
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.background_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Scanning...")
    
    def stop_scan(self):
        """Stop the scanning process."""
        if self.scanner_thread:
            self.scanner_thread.stop()
            self.scanner_thread.wait()
        
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.background_btn.setEnabled(False)
        self.status_label.setText("Scan stopped")
    
    def run_background(self):
        """Minimize to system tray and continue scanning."""
        self.showMinimized()
        self.status_label.setText("Running in background...")
    
    def update_progress(self, percent, current_file):
        """Update progress bar and status."""
        self.progress_bar.setValue(percent)
        self.status_label.setText(f"Scanning: {Path(current_file).name}")
    
    def update_elapsed_time(self):
        """Update elapsed time display."""
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            self.status_label.setText(
                f"{self.status_label.text()} | Elapsed: {elapsed.seconds // 60}m {elapsed.seconds % 60}s"
            )
    
    def scan_finished(self, duplicates):
        """Handle scan completion."""
        self.timer.stop()
        self.current_duplicates = duplicates
        self.display_results(duplicates)
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.background_btn.setEnabled(False)
        self.progress_bar.setValue(100)
        self.status_label.setText(f"Scan complete! Found {len(duplicates)} duplicate groups.")
        
        if self.isMinimized():
            self.showNormal()
    
    def scan_error(self, error_msg):
        """Handle scan error."""
        self.timer.stop()
        QMessageBox.critical(self, "Scan Error", f"An error occurred during scanning:\n{error_msg}")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.background_btn.setEnabled(False)
    
    def display_results(self, duplicates):
        """Display duplicate groups in table."""
        self.results_table.setRowCount(0)
        
        for group_id, group in enumerate(duplicates, 1):
            for file_info in group:
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                
                self.results_table.setItem(row, 0, QTableWidgetItem(str(group_id)))
                self.results_table.setItem(row, 1, QTableWidgetItem(file_info['path']))
                self.results_table.setItem(row, 2, QTableWidgetItem(f"{file_info['size'] / (1024*1024):.2f}"))
                self.results_table.setItem(row, 3, QTableWidgetItem(file_info.get('resolution', 'N/A')))
                self.results_table.setItem(row, 4, QTableWidgetItem(file_info.get('format', 'N/A')))
                self.results_table.setItem(row, 5, QTableWidgetItem(file_info.get('hash', '')[:16]))
                self.results_table.setItem(row, 6, QTableWidgetItem("Keep" if row == 0 else "Delete"))
    
    def delete_duplicates(self, mode):
        """Delete duplicates based on selected mode."""
        if not self.current_duplicates:
            QMessageBox.warning(self, "No Results", "No duplicates to delete.")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"This will delete duplicates and create a backup.\nMode: {mode}\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                backup_path = self.deletion_manager.delete_duplicates(self.current_duplicates, mode)
                QMessageBox.information(
                    self, "Success",
                    f"Duplicates deleted successfully!\n\nBackup created at:\n{backup_path}"
                )
                self.clear_results()
            except Exception as e:
                QMessageBox.critical(self, "Deletion Error", f"Error during deletion:\n{str(e)}")
    
    def clear_results(self):
        """Clear results table."""
        self.results_table.setRowCount(0)
        self.current_duplicates = []
        self.status_label.setText("Ready to scan")
        self.progress_bar.setValue(0)
