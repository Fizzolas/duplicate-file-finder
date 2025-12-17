"""File analyzers for images, videos, and general files."""

import hashlib
import cv2
import imagehash
from pathlib import Path
from PIL import Image
from typing import Dict, Optional
import numpy as np
import os


class FileHasher:
    """File hasher for exact duplicate detection."""
    
    CHUNK_SIZE = 65536  # 64KB chunks
    
    def hash_file(self, file_path: str) -> str:
        """Calculate SHA256 hash of file."""
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(self.CHUNK_SIZE)
                if not chunk:
                    break
                sha256.update(chunk)
        
        return sha256.hexdigest()


class ImageAnalyzer:
    """Image analyzer using perceptual hashing."""
    
    def __init__(self, threshold: int = 90):
        self.threshold = threshold
    
    def analyze(self, file_path: str) -> Optional[Dict]:
        """Analyze image and return perceptual hashes."""
        try:
            img = Image.open(file_path)
            
            # Calculate multiple perceptual hashes
            ahash = imagehash.average_hash(img)
            dhash = imagehash.dhash(img)
            phash = imagehash.phash(img)
            whash = imagehash.whash(img)
            
            return {
                'ahash': ahash,
                'dhash': dhash,
                'phash': phash,
                'whash': whash,
                'resolution': f"{img.width}x{img.height}",
                'hash': str(phash)  # Use phash as primary
            }
        except Exception:
            return None
    
    def compare(self, hash1: Dict, hash2: Dict, threshold: int) -> bool:
        """Compare two image hashes."""
        try:
            distances = [
                hash1['ahash'] - hash2['ahash'],
                hash1['dhash'] - hash2['dhash'],
                hash1['phash'] - hash2['phash'],
                hash1['whash'] - hash2['whash']
            ]
            avg_distance = sum(distances) / len(distances)
            similarity = (1 - (avg_distance / 64)) * 100
            return similarity >= threshold
        except Exception:
            return False


class VideoAnalyzer:
    """Video analyzer for content-based comparison with hard timeouts."""
    
    def __init__(self, threshold: int = 90, max_seconds_per_video: float = 3.0):
        self.threshold = threshold
        self.sample_frames = 8  # fewer samples = faster, less chance to hang
        self.max_seconds_per_video = max_seconds_per_video
    
    def analyze(self, file_path: str) -> Optional[Dict]:
        """Analyze video and create content signature.
        
        Hard-caps processing time per video so a single bad file cannot stall the scan.
        """
        start_time = cv2.getTickCount()
        tick_freq = cv2.getTickFrequency() or 1.0
        
        try:
            # Quick file size sanity check
            file_size = os.path.getsize(file_path)
            if file_size < 1024:  # < 1KB
                return None
            
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                return None
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            if fps <= 0 or frame_count <= 0 or width <= 0 or height <= 0:
                cap.release()
                return None
            
            duration = frame_count / fps if fps > 0 else 0
            sample_count = min(self.sample_frames, max(3, frame_count // 20))
            frame_indices = np.linspace(0, max(0, frame_count - 1), sample_count, dtype=int)
            frame_hashes = []
            
            for idx in frame_indices:
                # Time guard: bail out if this video is taking too long
                elapsed = (cv2.getTickCount() - start_time) / tick_freq
                if elapsed > self.max_seconds_per_video:
                    cap.release()
                    return None
                
                try:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                    ret, frame = cap.read()
                    if not ret or frame is None:
                        continue
                    
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    resized = cv2.resize(gray, (16, 16))
                    frame_hash = hashlib.md5(resized.tobytes()).hexdigest()
                    frame_hashes.append(frame_hash)
                except Exception:
                    continue
            
            cap.release()
            
            if len(frame_hashes) < 2:
                return None
            
            return {
                'frame_hashes': frame_hashes,
                'duration': duration,
                'resolution': f"{width}x{height}",
                'fps': fps,
                'frame_count': frame_count
            }
        except Exception:
            return None
    
    def compare(self, sig1: Dict, sig2: Dict, threshold: int) -> bool:
        """Compare two video signatures."""
        try:
            hashes1 = sig1.get('frame_hashes', [])
            hashes2 = sig2.get('frame_hashes', [])
            if not hashes1 or not hashes2:
                return False
            
            matches = sum(1 for h1, h2 in zip(hashes1, hashes2) if h1 == h2)
            similarity = (matches / min(len(hashes1), len(hashes2))) * 100
            
            duration1 = sig1.get('duration', 0)
            duration2 = sig2.get('duration', 0)
            if duration1 > 0 and duration2 > 0:
                duration_diff = abs(duration1 - duration2) / max(duration1, duration2)
                if duration_diff > 0.05:
                    similarity *= 0.8
            
            return similarity >= threshold
        except Exception:
            return False
