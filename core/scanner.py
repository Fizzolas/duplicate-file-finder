"""File scanner for detecting duplicates."""

import os
import hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Callable, Optional
import threading

from core.analyzers import ImageAnalyzer, VideoAnalyzer, FileHasher


class DuplicateScanner:
    """Scanner for finding duplicate files."""
    
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic', '.heif'}
    SUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
    
    def __init__(self, options: Dict):
        self.options = options
        self.files = []
        self.file_hashes = {}
        self.perceptual_hashes = {}
        self.video_signatures = {}
        self.progress_callback: Optional[Callable] = None
        self._stop_flag = threading.Event()
        
        self.image_analyzer = ImageAnalyzer(options.get('similarity_threshold', 90))
        self.video_analyzer = VideoAnalyzer(options.get('similarity_threshold', 90))
        self.hasher = FileHasher()
    
    def scan_directory(self, directory: str):
        """Scan directory for media files."""
        directory_path = Path(directory)
        
        if not directory_path.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        
        all_formats = self.SUPPORTED_IMAGE_FORMATS | self.SUPPORTED_VIDEO_FORMATS
        
        for root, _, files in os.walk(directory):
            if self._stop_flag.is_set():
                break
            
            for file in files:
                if self._stop_flag.is_set():
                    break
                
                file_path = Path(root) / file
                if file_path.suffix.lower() in all_formats:
                    self.files.append(str(file_path))
    
    def find_duplicates(self) -> List[List[Dict]]:
        """Find all duplicate files based on configured options."""
        if not self.files:
            return []
        
        duplicate_groups = []
        thread_count = self.options.get('thread_count', 4)
        total_files = len(self.files)
        
        # Step 1: Hash all files if exact match is enabled
        if self.options.get('exact_match', True):
            self._hash_files(thread_count, total_files)
            duplicate_groups.extend(self._find_exact_duplicates())
        
        # Step 2: Analyze images for perceptual similarity
        if self.options.get('similar_images', False):
            self._analyze_images(thread_count, total_files)
            duplicate_groups.extend(self._find_similar_images())
        
        # Step 3: Analyze videos for content similarity
        if self.options.get('similar_videos', False):
            self._analyze_videos(thread_count, total_files)
            duplicate_groups.extend(self._find_similar_videos())
        
        return self._merge_duplicate_groups(duplicate_groups)
    
    def _hash_files(self, thread_count: int, total_files: int):
        """Calculate file hashes using multiple threads."""
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = {executor.submit(self._hash_file, f): f for f in self.files}
            
            for i, future in enumerate(as_completed(futures)):
                if self._stop_flag.is_set():
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                
                file_path = futures[future]
                try:
                    file_hash = future.result()
                    if file_hash:
                        self.file_hashes[file_path] = file_hash
                except Exception as e:
                    pass
                
                if self.progress_callback:
                    progress = int((i + 1) / total_files * 33)
                    self.progress_callback(progress, file_path, i + 1, total_files)
    
    def _hash_file(self, file_path: str) -> Optional[str]:
        """Calculate SHA256 hash of a file."""
        try:
            return self.hasher.hash_file(file_path)
        except Exception:
            return None
    
    def _analyze_images(self, thread_count: int, total_files: int):
        """Analyze images for perceptual hashes."""
        image_files = [f for f in self.files if Path(f).suffix.lower() in self.SUPPORTED_IMAGE_FORMATS]
        
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = {executor.submit(self._analyze_image, f): f for f in image_files}
            
            for i, future in enumerate(as_completed(futures)):
                if self._stop_flag.is_set():
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                
                file_path = futures[future]
                try:
                    phash = future.result()
                    if phash:
                        self.perceptual_hashes[file_path] = phash
                except Exception:
                    pass
                
                if self.progress_callback:
                    progress = 33 + int((i + 1) / len(image_files) * 33)
                    self.progress_callback(progress, file_path, i + 1, len(image_files))
    
    def _analyze_image(self, file_path: str) -> Optional[Dict]:
        """Analyze a single image."""
        try:
            return self.image_analyzer.analyze(file_path)
        except Exception:
            return None
    
    def _analyze_videos(self, thread_count: int, total_files: int):
        """Analyze videos for signatures."""
        video_files = [f for f in self.files if Path(f).suffix.lower() in self.SUPPORTED_VIDEO_FORMATS]
        
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = {executor.submit(self._analyze_video, f): f for f in video_files}
            
            for i, future in enumerate(as_completed(futures)):
                if self._stop_flag.is_set():
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                
                file_path = futures[future]
                try:
                    signature = future.result()
                    if signature:
                        self.video_signatures[file_path] = signature
                except Exception:
                    pass
                
                if self.progress_callback:
                    progress = 66 + int((i + 1) / len(video_files) * 34)
                    self.progress_callback(progress, file_path, i + 1, len(video_files))
    
    def _analyze_video(self, file_path: str) -> Optional[Dict]:
        """Analyze a single video."""
        try:
            return self.video_analyzer.analyze(file_path)
        except Exception:
            return None
    
    def _find_exact_duplicates(self) -> List[List[Dict]]:
        """Find exact duplicates based on file hash."""
        hash_groups = {}
        
        for file_path, file_hash in self.file_hashes.items():
            if file_hash not in hash_groups:
                hash_groups[file_hash] = []
            hash_groups[file_hash].append(self._create_file_info(file_path, file_hash))
        
        return [group for group in hash_groups.values() if len(group) > 1]
    
    def _find_similar_images(self) -> List[List[Dict]]:
        """Find similar images based on perceptual hash."""
        similar_groups = []
        processed = set()
        threshold = self.options.get('similarity_threshold', 90)
        
        for file1, hash1 in self.perceptual_hashes.items():
            if file1 in processed:
                continue
            
            group = [self._create_file_info(file1, hash1.get('hash', ''))]
            
            for file2, hash2 in self.perceptual_hashes.items():
                if file1 == file2 or file2 in processed:
                    continue
                
                if self.image_analyzer.compare(hash1, hash2, threshold):
                    group.append(self._create_file_info(file2, hash2.get('hash', '')))
                    processed.add(file2)
            
            if len(group) > 1:
                similar_groups.append(group)
                processed.add(file1)
        
        return similar_groups
    
    def _find_similar_videos(self) -> List[List[Dict]]:
        """Find similar videos based on content signature."""
        similar_groups = []
        processed = set()
        threshold = self.options.get('similarity_threshold', 90)
        
        for file1, sig1 in self.video_signatures.items():
            if file1 in processed:
                continue
            
            group = [self._create_file_info(file1, '')]
            
            for file2, sig2 in self.video_signatures.items():
                if file1 == file2 or file2 in processed:
                    continue
                
                if self.video_analyzer.compare(sig1, sig2, threshold):
                    group.append(self._create_file_info(file2, ''))
                    processed.add(file2)
            
            if len(group) > 1:
                similar_groups.append(group)
                processed.add(file1)
        
        return similar_groups
    
    def _create_file_info(self, file_path: str, file_hash: str = '') -> Dict:
        """Create file information dictionary."""
        path = Path(file_path)
        info = {
            'path': str(file_path),
            'size': path.stat().st_size,
            'format': path.suffix.lower(),
            'hash': file_hash
        }
        
        # Add resolution for images and videos
        if path.suffix.lower() in self.SUPPORTED_IMAGE_FORMATS:
            hash_data = self.perceptual_hashes.get(file_path, {})
            info['resolution'] = hash_data.get('resolution', 'Unknown')
        elif path.suffix.lower() in self.SUPPORTED_VIDEO_FORMATS:
            sig_data = self.video_signatures.get(file_path, {})
            info['resolution'] = sig_data.get('resolution', 'Unknown')
        
        return info
    
    def _merge_duplicate_groups(self, groups: List[List[Dict]]) -> List[List[Dict]]:
        """Merge overlapping duplicate groups."""
        if not groups:
            return []
        
        # Simple deduplication - remove groups with overlapping files
        seen_files = set()
        unique_groups = []
        
        for group in groups:
            file_paths = {item['path'] for item in group}
            if not file_paths & seen_files:
                unique_groups.append(group)
                seen_files.update(file_paths)
        
        return unique_groups
    
    def stop(self):
        """Stop the scanning process."""
        self._stop_flag.set()
