"""Main application window."""

import os
import psutil
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QTableWidget,
    QTableWidgetItem, QFileDialog, QListWidget, QTabWidget,
    QCheckBox, QSpinBox, QGroupBox, QMessageBox, QHeaderView,
    QAbstractItemView, QSplitter, QSlider, QFormLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QDesktopServices, QUrl

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
        
        # Get system memory
        self.total_ram_mb = int(psutil.virtual_memory().total / (1024 * 1024))
        self.available_ram_mb = int(psutil.virtual_memory().available / (1024 * 1024))
        
        self.init_ui()
        self.setup_timer()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Duplicate File Finder")
        self.setGeometry(100, 100, 1250, 820)
        self.setStyleSheet(APP_STYLESHEET)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header / description
        header_box = QGroupBox("Quick Tips")
        header_layout = QVBoxLayout()
        header_label = QLabel(
            "1) Add one or more folders on the left.  "
            "2) Adjust scan behavior on the right.  "
            "3) Click 'Apply Settings' then 'Start Scan'."
        )
        header_label.setObjectName("headerLabel")
        header_layout.addWidget(header_label)
        
        # Backup location info
        backup_dir = self.config.get('backup_directory')
        backup_info = QLabel(f"Backups are saved to: {backup_dir}")
        backup_info.setObjectName("hintLabel")
        backup_info.setWordWrap(True)
        header_layout.addWidget(backup_info)
        
        # Open backups folder button
        open_backups_btn = QPushButton("Open Backups Folder")
        open_backups_btn.setMaximumWidth(150)
        open_backups_btn.clicked.connect(self.open_backups_folder)
        header_layout.addWidget(open_backups_btn)
        
        header_box.setLayout(header_layout)
        main_layout.addWidget(header_box)
        
        # Top section: Folder selection and options
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        folder_panel = self.create_folder_panel()
        top_splitter.addWidget(folder_panel)
        
        options_panel = self.create_options_panel()
        top_splitter.addWidget(options_panel)
        
        top_splitter.setStretchFactor(0, 1)
        top_splitter.setStretchFactor(1, 1)
        main_layout.addWidget(top_splitter)
        
        control_layout = self.create_control_buttons()
        main_layout.addLayout(control_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to scan • Press 'Apply Settings' after changes")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setObjectName("statusLabel")
        main_layout.addWidget(self.status_label)
        
        self.create_results_section(main_layout)
        
        deletion_layout = self.create_deletion_buttons()
        main_layout.addLayout(deletion_layout)
    
    def open_backups_folder(self):
        """Open the backups folder in file explorer."""
        backup_dir = self.config.get('backup_directory')
        if backup_dir and os.path.exists(backup_dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(backup_dir))
        else:
            QMessageBox.information(
                self, "Backups Folder",
                f"Backup folder will be created at:\n{backup_dir}\n\nIt will appear after your first deletion."
            )
    
    def create_folder_panel(self):
        group = QGroupBox("1. Choose folders")
        layout = QVBoxLayout()
        
        hint = QLabel("Add one or more folders to scan. Subfolders are included automatically.")
        hint.setObjectName("hintLabel")
        layout.addWidget(hint)
        
        self.folder_list = QListWidget()
        layout.addWidget(self.folder_list)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Folder…")
        add_btn.clicked.connect(self.add_folder)
        btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_folder)
        btn_layout.addWidget(remove_btn)
        
        layout.addLayout(btn_layout)
        group.setLayout(layout)
        return group
    
    def create_options_panel(self):
        group = QGroupBox("2. Scan settings")
        layout = QVBoxLayout()
        
        mode_box = QGroupBox("What to look for")
        mode_layout = QVBoxLayout()
        self.exact_match_cb = QCheckBox("Exact duplicates (fast, safe)")
        self.exact_match_cb.setChecked(True)
        mode_layout.addWidget(self.exact_match_cb)
        
        self.similar_images_cb = QCheckBox("Similar images (content-based)")
        self.similar_images_cb.setChecked(True)
        mode_layout.addWidget(self.similar_images_cb)
        
        self.similar_videos_cb = QCheckBox("Similar videos (content-based)")
        self.similar_videos_cb.setChecked(True)
        mode_layout.addWidget(self.similar_videos_cb)
        
        self.diff_resolution_cb = QCheckBox("Treat different resolutions as duplicates")
        self.diff_resolution_cb.setChecked(True)
        mode_layout.addWidget(self.diff_resolution_cb)
        
        self.diff_format_cb = QCheckBox("Treat different formats as duplicates")
        self.diff_format_cb.setChecked(True)
        mode_layout.addWidget(self.diff_format_cb)
        mode_box.setLayout(mode_layout)
        layout.addWidget(mode_box)
        
        resources_box = QGroupBox("Performance")
        form = QFormLayout()
        
        # CPU threads
        cpu_count = psutil.cpu_count(logical=True) or 4
        self.thread_spin = QSpinBox()
        self.thread_spin.setRange(1, cpu_count)
        self.thread_spin.setValue(min(self.config.get('thread_count', 4), cpu_count))
        self.thread_spin.setToolTip(f"How many CPU threads to use while scanning. Your system has {cpu_count} logical cores.")
        form.addRow("CPU threads:", self.thread_spin)
        
        # RAM slider - use actual system memory
        saved_ram = self.config.get('max_memory_mb', 2048)
        # Clamp saved value to available range
        default_ram = min(saved_ram, self.available_ram_mb)
        
        self.ram_slider = QSlider(Qt.Orientation.Horizontal)
        self.ram_slider.setRange(256, self.total_ram_mb)
        self.ram_slider.setSingleStep(256)
        self.ram_slider.setPageStep(512)
        self.ram_slider.setValue(default_ram)
        self.ram_slider.setToolTip(
            f"Maximum RAM in MB the scanner is allowed to use.\n"
            f"Total system RAM: {self.total_ram_mb} MB\n"
            f"Currently available: {self.available_ram_mb} MB"
        )
        
        self.ram_label = QLabel()
        self.update_ram_label(self.ram_slider.value())
        self.ram_slider.valueChanged.connect(self.update_ram_label)
        
        ram_layout = QHBoxLayout()
        ram_layout.addWidget(self.ram_slider)
        ram_layout.addWidget(self.ram_label)
        ram_container = QWidget()
        ram_container.setLayout(ram_layout)
        form.addRow("RAM limit:", ram_container)
        
        # System info label
        system_info = QLabel(
            f"System: {self.total_ram_mb:,} MB total, {self.available_ram_mb:,} MB available"
        )
        system_info.setObjectName("hintLabel")
        form.addRow("", system_info)
        
        # Similarity threshold
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(50, 100)
        self.threshold_spin.setValue(self.config.get('similarity_threshold', 90))
        self.threshold_spin.setToolTip("Higher = stricter matching, fewer loose matches.")
        form.addRow("Similarity threshold:", self.threshold_spin)
        
        resources_box.setLayout(form)
        layout.addWidget(resources_box)
        
        apply_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply Settings")
        self.apply_btn.setObjectName("applyButton")
        self.apply_btn.setToolTip("Save these settings and use them for the next scan.")
        self.apply_btn.clicked.connect(self.apply_settings)
        apply_layout.addWidget(self.apply_btn)
        apply_layout.addStretch()
        layout.addLayout(apply_layout)
        
        layout.addStretch()
        group.setLayout(layout)
        return group
    
    def update_ram_label(self, value: int):
        """Update RAM label with current slider value and percentage."""
        percentage = (value / self.total_ram_mb) * 100
        self.ram_label.setText(f"{value:,} MB ({percentage:.0f}%)")
    
    def create_control_buttons(self):
        layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Scan")
        self.start_btn.setObjectName("startButton")
        self.start_btn.setToolTip("Begin scanning using the folders and settings above.")
        self.start_btn.clicked.connect(self.start_scan)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setToolTip("Attempt to cancel the current scan.")
        self.stop_btn.clicked.connect(self.stop_scan)
        layout.addWidget(self.stop_btn)
        
        self.background_btn = QPushButton("Run in Background")
        self.background_btn.setEnabled(False)
        self.background_btn.setToolTip("Minimize while scan continues.")
        self.background_btn.clicked.connect(self.run_background)
        layout.addWidget(self.background_btn)
        
        layout.addStretch()
        return layout
    
    def create_results_section(self, parent_layout):
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "Group", "File Path", "Size (MB)", "Resolution",
            "Format", "Hash", "Keep/Delete"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setToolTip("Each row represents a file. Files with the same group number are duplicates.")
        parent_layout.addWidget(self.results_table)
    
    def create_deletion_buttons(self):
        layout = QHBoxLayout()
        
        delete_all_but_one = QPushButton("Delete All But One per Group")
        delete_all_but_one.setObjectName("deleteButton")
        delete_all_but_one.setToolTip("For each group, keep one file and back up everything else before deletion.")
        delete_all_but_one.clicked.connect(lambda: self.delete_duplicates('keep_one'))
        layout.addWidget(delete_all_but_one)
        
        delete_all_but_best = QPushButton("Keep Best Quality per Group")
        delete_all_but_best.setObjectName("deleteButton")
        delete_all_but_best.setToolTip("For each group, keep the largest file (often highest quality) and delete the rest.")
        delete_all_but_best.clicked.connect(lambda: self.delete_duplicates('keep_best'))
        layout.addWidget(delete_all_but_best)
        
        layout.addStretch()
        
        clear_btn = QPushButton("Clear Results")
        clear_btn.setToolTip("Clear the table without touching any files.")
        clear_btn.clicked.connect(self.clear_results)
        layout.addWidget(clear_btn)
        
        return layout
    
    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_elapsed_time)
    
    def apply_settings(self):
        """Persist settings to config so the scanner can use them."""
        self.config.set('thread_count', self.thread_spin.value())
        self.config.set('max_memory_mb', self.ram_slider.value())
        self.config.set('similarity_threshold', self.threshold_spin.value())
        self.status_label.setText("Settings applied • Ready to scan")
    
    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Scan")
        if folder:
            self.folder_list.addItem(folder)
    
    def remove_folder(self):
        current_row = self.folder_list.currentRow()
        if current_row >= 0:
            self.folder_list.takeItem(current_row)
    
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
        self.status_label.setText("Scanning… (press Stop to cancel)")
    
    def stop_scan(self):
        if self.scanner_thread:
            self.scanner_thread.stop()
            self.scanner_thread.wait()
        
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.background_btn.setEnabled(False)
        self.status_label.setText("Scan stopped")
    
    def run_background(self):
        self.showMinimized()
        self.status_label.setText("Running in background…")
    
    def update_progress(self, percent, current_file):
        self.progress_bar.setValue(percent)
        self.status_label.setText(f"Scanning: {Path(current_file).name}")
    
    def update_elapsed_time(self):
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            base_text = self.status_label.text().split("|")[0].strip()
            self.status_label.setText(
                f"{base_text} | Elapsed: {elapsed.seconds // 60}m {elapsed.seconds % 60}s"
            )
    
    def scan_finished(self, duplicates):
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
        self.timer.stop()
        QMessageBox.critical(self, "Scan Error", f"An error occurred during scanning:\n{error_msg}")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.background_btn.setEnabled(False)
    
    def display_results(self, duplicates):
        self.results_table.setRowCount(0)
        
        for group_id, group in enumerate(duplicates, 1):
            first_row_for_group = True
            for file_info in group:
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                
                self.results_table.setItem(row, 0, QTableWidgetItem(str(group_id)))
                self.results_table.setItem(row, 1, QTableWidgetItem(file_info['path']))
                self.results_table.setItem(row, 2, QTableWidgetItem(f"{file_info['size'] / (1024*1024):.2f}"))
                self.results_table.setItem(row, 3, QTableWidgetItem(file_info.get('resolution', 'N/A')))
                self.results_table.setItem(row, 4, QTableWidgetItem(file_info.get('format', 'N/A')))
                self.results_table.setItem(row, 5, QTableWidgetItem(file_info.get('hash', '')[:16]))
                self.results_table.setItem(row, 6, QTableWidgetItem("Keep" if first_row_for_group else "Delete"))
                first_row_for_group = False
    
    def delete_duplicates(self, mode):
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
        self.results_table.setRowCount(0)
        self.current_duplicates = []
        self.status_label.setText("Ready to scan • Press 'Apply Settings' after changes")
        self.progress_bar.setValue(0)
