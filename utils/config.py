"""Configuration management."""

import json
import os
from pathlib import Path
from typing import Any, Dict


class ConfigManager:
    """Manages application configuration."""
    
    @staticmethod
    def get_app_data_dir() -> Path:
        """Get the application data directory in user's Documents folder."""
        if os.name == 'nt':  # Windows
            documents = Path.home() / 'Documents'
        else:  # Linux/Mac
            documents = Path.home() / 'Documents'
        
        app_dir = documents / 'DuplicateFileFinder'
        app_dir.mkdir(exist_ok=True)
        return app_dir
    
    @staticmethod
    def get_default_backup_dir() -> str:
        """Get the default backup directory path."""
        backup_dir = ConfigManager.get_app_data_dir() / 'backups'
        backup_dir.mkdir(exist_ok=True)
        return str(backup_dir)
    
    DEFAULT_CONFIG = {
        'similarity_threshold': 90,
        'thread_count': 4,
        'max_memory_mb': 2048,
        'backup_enabled': True,
        'backup_directory': None,  # Will be set dynamically
        'use_trash': True
    }
    
    def __init__(self, config_file: str = None):
        if config_file is None:
            # Store config in app data directory
            config_file = self.get_app_data_dir() / 'config.json'
        
        self.config_file = Path(config_file)
        self.config = self._load_config()
        
        # Set backup directory if not already set
        if not self.config.get('backup_directory'):
            self.config['backup_directory'] = self.get_default_backup_dir()
            self.save_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    config = {**self.DEFAULT_CONFIG, **loaded_config}
                    return config
            except Exception:
                return self.DEFAULT_CONFIG.copy()
        else:
            default = self.DEFAULT_CONFIG.copy()
            default['backup_directory'] = self.get_default_backup_dir()
            self.save_config(default)
            return default
    
    def save_config(self, config: Dict = None):
        """Save configuration to file."""
        if config is None:
            config = self.config
        
        # Ensure parent directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value
        self.save_config()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.config['backup_directory'] = self.get_default_backup_dir()
        self.save_config()
