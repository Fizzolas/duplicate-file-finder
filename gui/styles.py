"""Application stylesheet definitions."""

APP_STYLESHEET = """
QMainWindow {
    background-color: #18181b;
    color: #e5e5e5;
}

QWidget {
    background-color: #18181b;
    color: #e5e5e5;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 9pt;
}

#compactHeaderLabel {
    font-size: 10pt;
    color: #c4c4c4;
    font-weight: 600;
}

#hintLabel {
    font-size: 8pt;
    color: #a1a1aa;
}

#statusLabel {
    font-size: 9pt;
    color: #a1a1aa;
}

#etaLabel {
    font-size: 9pt;
    color: #22c55e;
    font-weight: 600;
}

QPushButton {
    background-color: #27272f;
    color: #e5e5e5;
    border: 1px solid #3f3f46;
    padding: 6px 12px;
    border-radius: 4px;
    min-width: 70px;
    font-size: 9pt;
}

QPushButton:hover {
    background-color: #32323a;
    border: 1px solid #38bdf8;
}

QPushButton:pressed {
    background-color: #0ea5e9;
}

QPushButton:disabled {
    background-color: #1f2933;
    color: #6b7280;
    border: 1px solid #374151;
}

QPushButton#startButton {
    background-color: #0f766e;
    font-weight: 600;
}

QPushButton#startButton:hover {
    background-color: #0d9488;
}

QPushButton#deleteButton {
    background-color: #b91c1c;
}

QPushButton#deleteButton:hover {
    background-color: #dc2626;
}

QPushButton#applyButton {
    background-color: #1d4ed8;
    font-weight: 600;
}

QPushButton#applyButton:hover {
    background-color: #2563eb;
}

QPushButton#showInFolderButton {
    background-color: #374151;
    border: 1px solid #4b5563;
    padding: 3px 10px;
    font-size: 8pt;
    min-width: 100px;
}

QPushButton#showInFolderButton:hover {
    background-color: #4b5563;
    border: 1px solid #6b7280;
}

QGroupBox {
    border: 1px solid #27272f;
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 8px;
    font-weight: 600;
    font-size: 9pt;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}

QListWidget {
    background-color: #111827;
    border: 1px solid #27272f;
    border-radius: 4px;
    padding: 3px;
    font-size: 8pt;
}

QListWidget::item {
    padding: 3px;
    border-radius: 2px;
}

QListWidget::item:selected {
    background-color: #1d4ed8;
}

QListWidget::item:hover {
    background-color: #1f2937;
}

QTableWidget {
    background-color: #0b1120;
    alternate-background-color: #020617;
    border: 1px solid #111827;
    gridline-color: #1f2937;
    font-size: 8pt;
}

QTableWidget::item {
    padding: 3px;
}

QTableWidget::item:selected {
    background-color: #1d4ed8;
}

QTableWidget::item:hover {
    background-color: #1f2937;
}

QHeaderView::section {
    background-color: #020617;
    color: #e5e5e5;
    padding: 5px;
    border: 1px solid #111827;
    font-weight: 600;
    font-size: 8pt;
}

QProgressBar {
    border: 1px solid #27272f;
    border-radius: 4px;
    text-align: center;
    background-color: #020617;
    height: 20px;
    font-size: 8pt;
}

QProgressBar::chunk {
    background-color: #0ea5e9;
    border-radius: 3px;
}

QCheckBox {
    spacing: 6px;
    font-size: 9pt;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #4b5563;
    border-radius: 3px;
    background-color: #020617;
}

QCheckBox::indicator:checked {
    background-color: #22c55e;
    border: 1px solid #22c55e;
}

QCheckBox::indicator:hover {
    border: 1px solid #38bdf8;
}

QSpinBox, QSlider::groove:horizontal {
    background-color: #020617;
    border: 1px solid #27272f;
    border-radius: 4px;
    height: 20px;
    font-size: 9pt;
}

QSlider::handle:horizontal {
    background-color: #22c55e;
    width: 12px;
    border-radius: 6px;
    margin: -3px 0;
}

QSlider::groove:horizontal:hover {
    border-color: #38bdf8;
}

QSpinBox {
    padding: 3px;
    min-width: 70px;
}

QSpinBox:hover {
    border: 1px solid #38bdf8;
}

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #111827;
    border: 1px solid #1f2937;
    width: 14px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #1f2937;
}

QLabel {
    color: #e5e5e5;
}

QSplitter::handle {
    background-color: #27272f;
    height: 4px;
}

QSplitter::handle:hover {
    background-color: #38bdf8;
}

QSplitter::handle:vertical {
    height: 4px;
}

QSplitter::handle:horizontal {
    width: 4px;
}

QFormLabel {
    font-size: 9pt;
}
"""
