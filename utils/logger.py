"""Logging configuration."""

import logging
import sys
from pathlib import Path
from utils.config import ConfigManager


def setup_logger(log_file: str = None, level=logging.INFO):
    """Setup application logger.
    
    Args:
        log_file: Optional log file path. If None, uses app data directory.
        level: Logging level (default: INFO)
    """
    if log_file is None:
        # Store logs in app data directory
        app_dir = ConfigManager.get_app_data_dir()
        log_dir = app_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / 'app.log'
    
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
