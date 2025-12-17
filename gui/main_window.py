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
        self.last_progress_update = None
        
        # Rolling average for ETA calculation (last 10 progress updates)
        self.recent_progress_times = deque(maxlen=10)
        self.recent_file_counts = deque(maxlen=10)
        
        # Get system memory
        self.total_ram_mb = int(psutil.virtual_memory().total / (1024 * 1024))
        self.available_ram_mb = int(psutil.virtual_memory().available / (1024 * 1024))
        
        self.init_ui()
        self.setup_timer()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Duplicate File Finder")
        self.setMinimumSize(900, 600)
        self.resize(1200, 800)
        self.setStyleSheet(APP_STYLESHEET)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Compact header
        header_layout = QHBoxLayout()
        header_label = QLabel("1) Add folders  •  2) Configure settings  •  3) Apply & Scan")
        header_label.setObjectName("compactHeaderLabel")
        header_layout.addWidget(header_label)
        
        open_backups_btn = QPushButton("Backups Folder")
        open_backups_btn.setMaximumWidth(120)
        open_backups_btn.setToolTip(f"Open: {self.config.get('backup_directory')}")
        open_backups_btn.clicked.connect(self.open_backups_folder)
        header_layout.addWidget(open_backups_btn)
        
        main_layout.addLayout(header_layout)
        
        # Main vertical splitter: top section vs results
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top section widget
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(6)
        
        # Folders and options in horizontal splitter
        config_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        folder_panel = self.create_folder_panel()
        config_splitter.addWidget(folder_panel)
        
        options_panel = self.create_options_panel()
        config_splitter.addWidget(options_panel)
        
        config_splitter.setStretchFactor(0, 1)
        config_splitter.setStretchFactor(1, 1)
        top_layout.addWidget(config_splitter)
        
        # Control buttons
        control_layout = self.create_control_buttons()
        top_layout.addLayout(control_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMaximumHeight(22)
        top_layout.addWidget(self.progress_bar)
        
        # Status and ETA
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready to scan")
        self.status_label.setObjectName("statusLabel")
        status_layout.addWidget(self.status_label, 1)
        
        self.eta_label = QLabel("")
        self.eta_label.setObjectName("etaLabel")
        status_layout.addWidget(self.eta_label)
        top_layout.addLayout(status_layout)
        
        main_splitter.addWidget(top_widget)
        
        # Bottom section: Results table
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        results_layout.setContentsMargins(0, 0, 0, 0)
        results_layout.setSpacing(4)
        
        results_hint = QLabel("Results (hover over rows to reveal actions)")
        results_hint.setObjectName("hintLabel")
        results_layout.addWidget(results_hint)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels([
            "Group", "File Path", "Size (MB)", "Resolution",
            "Format", "Hash", "Keep/Delete", "Actions"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setMouseTracking(True)
        self.results_table.cellEntered.connect(self.on_cell_hover)
        self.results_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        results_layout.addWidget(self.results_table)
        
        # Deletion buttons
        deletion_layout = self.create_deletion_buttons()
        results_layout.addLayout(deletion_layout)
        
        main_splitter.addWidget(results_widget)
        
        # Set initial splitter sizes: 30% top, 70% results
        main_splitter.setStretchFactor(0, 3)
        main_splitter.setStretchFactor(1, 7)
        
        main_layout.addWidget(main_splitter)
    
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
        group = QGroupBox("Folders to Scan")
        layout = QVBoxLayout()
        layout.setSpacing(4)
        
        self.folder_list = QListWidget()
        self.folder_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.folder_list)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_folder)
        btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_folder)
        btn_layout.addWidget(remove_btn)
        
        layout.addLayout(btn_layout)
        group.setLayout(layout)
        return group
    
    def create_options_panel(self):
        group = QGroupBox("Scan Options")
        layout = QVBoxLayout()
        layout.setSpacing(4)
        
        # Detection options in compact layout
        self.exact_match_cb = QCheckBox("Exact duplicates")
        self.exact_match_cb.setChecked(True)
        layout.addWidget(self.exact_match_cb)
        
        self.similar_images_cb = QCheckBox("Similar images")
        self.similar_images_cb.setChecked(True)
        layout.addWidget(self.similar_images_cb)
        
        self.similar_videos_cb = QCheckBox("Similar videos")
        self.similar_videos_cb.setChecked(True)
        layout.addWidget(self.similar_videos_cb)
        
        self.diff_resolution_cb = QCheckBox("Different resolutions")
        self.diff_resolution_cb.setChecked(True)
        layout.addWidget(self.diff_resolution_cb)
        
        self.diff_format_cb = QCheckBox("Different formats")
        self.diff_format_cb.setChecked(True)
        layout.addWidget(self.diff_format_cb)
        
        # Performance settings in compact form
        perf_layout = QFormLayout()
        perf_layout.setVerticalSpacing(4)
        perf_layout.setHorizontalSpacing(8)
        
        cpu_count = psutil.cpu_count(logical=True) or 4
        self.thread_spin = QSpinBox()
        self.thread_spin.setRange(1, cpu_count)
        self.thread_spin.setValue(min(self.config.get('thread_count', 4), cpu_count))
        perf_layout.addRow("Threads:", self.thread_spin)
        
        saved_ram = self.config.get('max_memory_mb', 2048)
        default_ram = min(saved_ram, self.available_ram_mb)
        
        self.ram_slider = QSlider(Qt.Orientation.Horizontal)
        self.ram_slider.setRange(256, self.total_ram_mb)
        self.ram_slider.setSingleStep(256)
        self.ram_slider.setPageStep(512)
        self.ram_slider.setValue(default_ram)
        
        self.ram_label = QLabel()
        self.update_ram_label(self.ram_slider.value())
        self.ram_slider.valueChanged.connect(self.update_ram_label)
        
        ram_layout = QHBoxLayout()
        ram_layout.addWidget(self.ram_slider, 1)
        ram_layout.addWidget(self.ram_label)
        perf_layout.addRow("RAM:", ram_layout)
        
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(50, 100)
        self.threshold_spin.setValue(self.config.get('similarity_threshold', 90))
        perf_layout.addRow("Threshold:", self.threshold_spin)
        
        layout.addLayout(perf_layout)
        
        self.apply_btn = QPushButton("Apply Settings")
        self.apply_btn.setObjectName("applyButton")
        self.apply_btn.clicked.connect(self.apply_settings)
        layout.addWidget(self.apply_btn)
        
        layout.addStretch()
        group.setLayout(layout)
        return group
    
    def update_ram_label(self, value: int):
        """Update RAM label with current slider value."""
        if value >= 1024:
            self.ram_label.setText(f"{value/1024:.1f} GB")
        else:
            self.ram_label.setText(f"{value} MB")
    
    def create_control_buttons(self):
        layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Scan")
        self.start_btn.setObjectName("startButton")
        self.start_btn.clicked.connect(self.start_scan)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_scan)
        layout.addWidget(self.stop_btn)
        
        self.background_btn = QPushButton("Minimize")
        self.background_btn.setEnabled(False)
        self.background_btn.clicked.connect(self.run_background)
        layout.addWidget(self.background_btn)
        
        layout.addStretch()
        return layout
    
    def on_cell_hover(self, row, column):
        """Handle cell hover to show/hide action buttons."""
        for r in range(self.results_table.rowCount()):
            widget = self.results_table.cellWidget(r, 7)
            if widget:
                widget.setVisible(r == row)
    
    def show_in_folder(self, file_path: str):
        """Open file explorer and highlight the file."""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found", f"File no longer exists:\n{file_path}")
            return
        
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.run(['explorer', '/select,', os.path.normpath(file_path)])
            elif system == "Darwin":
                subprocess.run(['open', '-R', file_path])
            else:
                folder = os.path.dirname(file_path)
                subprocess.run(['xdg-open', folder])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open file location:\n{str(e)}")
    
    def create_deletion_buttons(self):
        layout = QHBoxLayout()
        
        delete_all_but_one = QPushButton("Delete All But One per Group")
        delete_all_but_one.setObjectName("deleteButton")
        delete_all_but_one.clicked.connect(lambda: self.delete_duplicates('keep_one'))
        layout.addWidget(delete_all_but_one)
        
        delete_all_but_best = QPushButton("Keep Best Quality per Group")
        delete_all_but_best.setObjectName("deleteButton")
        delete_all_but_best.clicked.connect(lambda: self.delete_duplicates('keep_best'))
        layout.addWidget(delete_all_but_best)
        
        layout.addStretch()
        
        clear_btn = QPushButton("Clear Results")
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
        self.files_processed = 0
        self.total_files = 0
        self.last_progress_update = datetime.now()
        self.recent_progress_times.clear()
        self.recent_file_counts.clear()
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
    
    def stop_scan(self):
        if self.scanner_thread:
            self.scanner_thread.stop()
            self.scanner_thread.wait()
        
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.background_btn.setEnabled(False)
        self.status_label.setText("Scan stopped")
        self.eta_label.setText("")
    
    def run_background(self):
        self.showMinimized()
    
    def update_progress(self, percent, current_file, current_count, total_count):
        """Update progress bar, status, and ETA with rolling average."""
        self.progress_bar.setValue(percent)
        self.files_processed = current_count
        self.total_files = total_count
        
        file_name = Path(current_file).name
        self.status_label.setText(f"Scanning: {file_name} ({current_count}/{total_count})")
        
        # Track recent progress for rolling average ETA
        current_time = datetime.now()
        self.recent_progress_times.append(current_time)
        self.recent_file_counts.append(current_count)
        
        # Calculate ETA using rolling average (more responsive to recent speed)
        if len(self.recent_progress_times) >= 2:
            time_diff = (self.recent_progress_times[-1] - self.recent_progress_times[0]).total_seconds()
            file_diff = self.recent_file_counts[-1] - self.recent_file_counts[0]
            
            if time_diff > 0 and file_diff > 0:
                recent_rate = file_diff / time_diff  # files per second based on recent progress
                
                if recent_rate > 0:
                    remaining_files = total_count - current_count
                    eta_seconds = remaining_files / recent_rate
                    
                    if eta_seconds < 60:
                        eta_text = f"ETA: {int(eta_seconds)}s"
                    elif eta_seconds < 3600:
                        eta_text = f"ETA: {int(eta_seconds / 60)}m {int(eta_seconds % 60)}s"
                    else:
                        hours = int(eta_seconds / 3600)
                        minutes = int((eta_seconds % 3600) / 60)
                        eta_text = f"ETA: {hours}h {minutes}m"
                    
                    # Show rate for transparency
                    if recent_rate >= 1:
                        eta_text += f" ({int(recent_rate)}/s)"
                    else:
                        eta_text += f" ({recent_rate:.1f}/s)"
                    
                    self.eta_label.setText(eta_text)
                else:
                    self.eta_label.setText("ETA: Calculating...")
    
    def update_elapsed_time(self):
        """Update elapsed time display periodically."""
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            minutes = elapsed.seconds // 60
            seconds = elapsed.seconds % 60
            
            if "Scanning:" not in self.status_label.text():
                self.status_label.setText(f"Scanning… | Elapsed: {minutes}m {seconds}s")
    
    def scan_finished(self, duplicates):
        self.timer.stop()
        self.current_duplicates = duplicates
        self.display_results(duplicates)
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.background_btn.setEnabled(False)
        self.progress_bar.setValue(100)
        
        elapsed = datetime.now() - self.start_time
        elapsed_text = f"{elapsed.seconds // 60}m {elapsed.seconds % 60}s"
        self.status_label.setText(f"Scan complete! Found {len(duplicates)} duplicate groups in {elapsed_text}.")
        self.eta_label.setText("")
        
        if self.isMinimized():
            self.showNormal()
    
    def scan_error(self, error_msg):
        self.timer.stop()
        QMessageBox.critical(self, "Scan Error", f"An error occurred during scanning:\n{error_msg}")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.background_btn.setEnabled(False)
        self.eta_label.setText("")
    
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
                
                # Add "Show in Folder" button
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(4, 2, 4, 2)
                
                show_btn = QPushButton("Show in Folder")
                show_btn.setObjectName("showInFolderButton")
                show_btn.setMaximumWidth(120)
                show_btn.clicked.connect(lambda checked, path=file_info['path']: self.show_in_folder(path))
                btn_layout.addWidget(show_btn)
                btn_layout.addStretch()
                
                btn_widget.setVisible(False)
                self.results_table.setCellWidget(row, 7, btn_widget)
                
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
        self.status_label.setText("Ready to scan")
        self.eta_label.setText("")
        self.progress_bar.setValue(0)
