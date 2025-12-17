"""File analyzers for images, videos, and general files."""

import hashlib
import cv2
import imagehash
from pathlib import Path
from PIL import Image
from typing import Dict, Optional
import numpy as np
import signal
import os


class TimeoutError(Exception):
    """Raised when analysis times out."""
    pass


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
        except Exception as e:
            return None
    
    def compare(self, hash1: Dict, hash2: Dict, threshold: int) -> bool:
        """Compare two image hashes.
        
        Args:
            hash1: First image hash dictionary
            hash2: Second image hash dictionary
            threshold: Similarity threshold (0-100)
            
        Returns:
            True if images are similar enough
        """
        try:
            # Calculate hamming distance for each hash type
            distances = [
                hash1['ahash'] - hash2['ahash'],
                hash1['dhash'] - hash2['dhash'],
                hash1['phash'] - hash2['phash'],
                hash1['whash'] - hash2['whash']
            ]
            
            # Average distance
            avg_distance = sum(distances) / len(distances)
            
            # Convert to similarity percentage (lower distance = higher similarity)
            # Max distance is 64 bits for these hash types
            similarity = (1 - (avg_distance / 64)) * 100
            
            return similarity >= threshold
        except Exception:
            return False


class VideoAnalyzer:
    """Video analyzer for content-based comparison."""
    
    def __init__(self, threshold: int = 90, timeout_seconds: int = 10):
        self.threshold = threshold
        self.sample_frames = 10  # Number of frames to sample
        self.timeout_seconds = timeout_seconds
    
    def analyze(self, file_path: str) -> Optional[Dict]:
        """Analyze video and create content signature with timeout protection."""
        try:
            # Quick file size check - skip if corrupted or too large
            file_size = os.path.getsize(file_path)
            if file_size < 1024:  # Less than 1KB, likely corrupted
                return None
            
            cap = cv2.VideoCapture(file_path)
            
            if not cap.isOpened():
                return None
            
            # Get video properties with timeout protection
            try:
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            except Exception:
                cap.release()
                return None
            
            # Validate properties
            if fps <= 0 or frame_count <= 0 or width <= 0 or height <= 0:
                cap.release()
                return None
            
            duration = frame_count / fps if fps > 0 else 0
            
            # Sample fewer frames for very long videos or if fps is weird
            sample_count = min(self.sample_frames, max(3, frame_count // 10))
            
            # Sample frames evenly throughout video
            frame_indices = np.linspace(0, max(0, frame_count - 1), sample_count, dtype=int)
            frame_hashes = []
            
            successful_reads = 0
            for idx in frame_indices:
                try:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                    ret, frame = cap.read()
                    
                    if ret and frame is not None:
                        # Convert to grayscale and resize for consistent comparison
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        resized = cv2.resize(gray, (16, 16))
                        
                        # Calculate hash of frame
                        frame_hash = hashlib.md5(resized.tobytes()).hexdigest()
                        frame_hashes.append(frame_hash)
                        successful_reads += 1
                    
                    # If we can't read enough frames, skip this video
                    if len(frame_hashes) == 0 and successful_reads == 0 and idx > frame_count // 2:
                        cap.release()
                        return None
                        
                except Exception:
                    continue
            
            cap.release()
            
            # Need at least a few frames to be valid
            if len(frame_hashes) < 2:
                return None
            
            return {
                'frame_hashes': frame_hashes,
                'duration': duration,
                'resolution': f"{width}x{height}",
                'fps': fps,
                'frame_count': frame_count
            }
        except Exception as e:
            # Silently skip problematic videos
            return None
    
    def compare(self, sig1: Dict, sig2: Dict, threshold: int) -> bool:
        """Compare two video signatures.
        
        Args:
            sig1: First video signature
            sig2: Second video signature
            threshold: Similarity threshold (0-100)
            
        Returns:
            True if videos are similar enough
        """
        try:
            # Compare frame hashes
            hashes1 = sig1.get('frame_hashes', [])
            hashes2 = sig2.get('frame_hashes', [])
            
            if not hashes1 or not hashes2:
                return False
            
            # Calculate percentage of matching frames
            matches = sum(1 for h1, h2 in zip(hashes1, hashes2) if h1 == h2)
            similarity = (matches / min(len(hashes1), len(hashes2))) * 100
            
            # Also check if durations are similar (within 5%)
            duration1 = sig1.get('duration', 0)
            duration2 = sig2.get('duration', 0)
            
            if duration1 > 0 and duration2 > 0:
                duration_diff = abs(duration1 - duration2) / max(duration1, duration2)
                if duration_diff > 0.05:  # More than 5% difference
                    similarity *= 0.8  # Reduce similarity score
            
            return similarity >= threshold
        except Exception:
            return False
