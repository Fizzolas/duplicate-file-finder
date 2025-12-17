"""Deletion manager with backup functionality."""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from send2trash import send2trash


class DeletionManager:
    """Manages file deletion with automatic backup."""
    
    def __init__(self, config):
        self.config = config
        self.backup_dir = Path(config.get('backup_directory', './backups'))
        self.backup_dir.mkdir(exist_ok=True)
    
    def delete_duplicates(self, duplicate_groups: List[List[Dict]], mode: str) -> str:
        """Delete duplicates based on mode and create backup.
        
        Args:
            duplicate_groups: List of duplicate file groups
            mode: 'keep_one', 'keep_best', or 'custom'
            
        Returns:
            Path to backup ZIP file
        """
        files_to_delete = self._select_files_for_deletion(duplicate_groups, mode)
        
        if not files_to_delete:
            raise ValueError("No files selected for deletion")
        
        # Create backup
        backup_path = self._create_backup(files_to_delete)
        
        # Delete files
        self._delete_files(files_to_delete)
        
        return backup_path
    
    def _select_files_for_deletion(self, groups: List[List[Dict]], mode: str) -> List[str]:
        """Select which files to delete based on mode."""
        files_to_delete = []
        
        for group in groups:
            if mode == 'keep_one':
                # Keep first file, delete rest
                files_to_delete.extend([f['path'] for f in group[1:]])
            
            elif mode == 'keep_best':
                # Keep highest quality (largest size or highest resolution)
                best_file = max(group, key=lambda x: x['size'])
                files_to_delete.extend([f['path'] for f in group if f['path'] != best_file['path']])
            
            elif mode == 'custom':
                # Custom selection would be handled by UI
                pass
        
        return files_to_delete
    
    def _create_backup(self, files: List[str]) -> str:
        """Create ZIP backup of files to be deleted."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"backup_{timestamp}.zip"
        backup_path = self.backup_dir / backup_filename
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files:
                if os.path.exists(file_path):
                    # Preserve directory structure in ZIP
                    arcname = Path(file_path).name
                    zipf.write(file_path, arcname)
        
        return str(backup_path)
    
    def _delete_files(self, files: List[str]):
        """Delete files safely."""
        use_trash = self.config.get('use_trash', True)
        
        for file_path in files:
            try:
                if use_trash:
                    send2trash(file_path)
                else:
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
    
    def restore_backup(self, backup_path: str, restore_dir: str):
        """Restore files from backup ZIP."""
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(restore_dir)
