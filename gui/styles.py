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
    font-size: 10pt;
}

#headerLabel {
    font-size: 10pt;
    color: #c4c4c4;
}

#hintLabel {
    font-size: 9pt;
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
    padding: 8px 16px;
    border-radius: 4px;
    min-width: 90px;
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
}

QPushButton#applyButton:hover {
    background-color: #2563eb;
}

QPushButton#showInFolderButton {
    background-color: #374151;
    border: 1px solid #4b5563;
    padding: 4px 12px;
    font-size: 9pt;
    min-width: 100px;
}

QPushButton#showInFolderButton:hover {
    background-color: #4b5563;
    border: 1px solid #6b7280;
}

QGroupBox {
    border: 1px solid #27272f;
    border-radius: 6px;
    margin-top: 14px;
    padding-top: 10px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}

QListWidget {
    background-color: #111827;
    border: 1px solid #27272f;
    border-radius: 4px;
    padding: 4px;
}

QListWidget::item {
    padding: 4px;
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
}

QTableWidget::item {
    padding: 4px;
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
    padding: 6px;
    border: 1px solid #111827;
    font-weight: 600;
}

QProgressBar {
    border: 1px solid #27272f;
    border-radius: 4px;
    text-align: center;
    background-color: #020617;
    height: 24px;
}

QProgressBar::chunk {
    background-color: #0ea5e9;
    border-radius: 3px;
}

QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #4b5563;
    border-radius: 4px;
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
    height: 22px;
}

QSlider::handle:horizontal {
    background-color: #22c55e;
    width: 14px;
    border-radius: 7px;
    margin: -4px 0;
}

QSlider::groove:horizontal:hover {
    border-color: #38bdf8;
}

QSpinBox {
    padding: 4px;
    min-width: 80px;
}

QSpinBox:hover {
    border: 1px solid #38bdf8;
}

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #111827;
    border: 1px solid #1f2937;
    width: 16px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #1f2937;
}

QLabel {
    color: #e5e5e5;
}

QSplitter::handle {
    background-color: #111827;
    width: 2px;
}

QSplitter::handle:hover {
    background-color: #38bdf8;
}
"""
