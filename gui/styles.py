"""Application stylesheet definitions."""

APP_STYLESHEET = """
QMainWindow {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}

QPushButton {
    background-color: #2d2d30;
    color: #e0e0e0;
    border: 1px solid #3f3f46;
    padding: 8px 16px;
    border-radius: 4px;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #3e3e42;
    border: 1px solid #007acc;
}

QPushButton:pressed {
    background-color: #007acc;
}

QPushButton:disabled {
    background-color: #252526;
    color: #656565;
    border: 1px solid #3f3f46;
}

QPushButton#startButton {
    background-color: #0e639c;
    font-weight: bold;
}

QPushButton#startButton:hover {
    background-color: #1177bb;
}

QPushButton#deleteButton {
    background-color: #a83232;
}

QPushButton#deleteButton:hover {
    background-color: #c44242;
}

QGroupBox {
    border: 1px solid #3f3f46;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 8px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

QListWidget {
    background-color: #252526;
    border: 1px solid #3f3f46;
    border-radius: 4px;
    padding: 4px;
}

QListWidget::item {
    padding: 4px;
    border-radius: 2px;
}

QListWidget::item:selected {
    background-color: #094771;
}

QListWidget::item:hover {
    background-color: #2a2d2e;
}

QTableWidget {
    background-color: #252526;
    alternate-background-color: #2d2d30;
    border: 1px solid #3f3f46;
    gridline-color: #3f3f46;
}

QTableWidget::item {
    padding: 4px;
}

QTableWidget::item:selected {
    background-color: #094771;
}

QHeaderView::section {
    background-color: #2d2d30;
    color: #e0e0e0;
    padding: 6px;
    border: 1px solid #3f3f46;
    font-weight: bold;
}

QProgressBar {
    border: 1px solid #3f3f46;
    border-radius: 4px;
    text-align: center;
    background-color: #252526;
    height: 24px;
}

QProgressBar::chunk {
    background-color: #0e639c;
    border-radius: 3px;
}

QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #3f3f46;
    border-radius: 3px;
    background-color: #252526;
}

QCheckBox::indicator:checked {
    background-color: #0e639c;
    border: 1px solid #0e639c;
}

QCheckBox::indicator:hover {
    border: 1px solid #007acc;
}

QSpinBox {
    background-color: #252526;
    border: 1px solid #3f3f46;
    border-radius: 4px;
    padding: 4px;
    min-width: 80px;
}

QSpinBox:hover {
    border: 1px solid #007acc;
}

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #2d2d30;
    border: 1px solid #3f3f46;
    width: 16px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #3e3e42;
}

QLabel {
    color: #e0e0e0;
}

QSplitter::handle {
    background-color: #3f3f46;
    width: 2px;
}

QSplitter::handle:hover {
    background-color: #007acc;
}
"""
