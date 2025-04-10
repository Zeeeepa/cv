#!/usr/bin/env python3
"""
CV Cache Manager - Manages caching for the CV Generator.

This module provides functionality for caching generated CVs to improve performance,
including:
- Caching generated LaTeX files
- Caching compiled PDFs
- Managing cache expiration and cleanup
"""

import os
import time
import hashlib
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('cv_cache_manager')

# Default cache settings
DEFAULT_CACHE_DIR = Path.home() / '.cv_generator' / 'cache'
DEFAULT_CACHE_EXPIRATION = 60 * 60 * 24 * 7  # 7 days in seconds
DEFAULT_MAX_CACHE_SIZE = 100 * 1024 * 1024  # 100 MB in bytes


class CacheManager:
    """Cache manager for CV Generator."""
    
    def __init__(self, cache_dir: Optional[Union[str, Path]] = None, 
                 cache_expiration: int = DEFAULT_CACHE_EXPIRATION,
                 max_cache_size: int = DEFAULT_MAX_CACHE_SIZE):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory to store cache files (default: ~/.cv_generator/cache)
            cache_expiration: Cache expiration time in seconds (default: 7 days)
            max_cache_size: Maximum cache size in bytes (default: 100 MB)
        """
        self.cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
        self.cache_expiration = cache_expiration
        self.max_cache_size = max_cache_size
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Create index file if it doesn't exist
        self.index_file = self.cache_dir / 'cache_index.json'
        if not self.index_file.exists():
            self._create_index()
        
        # Load cache index
        self.cache_index = self._load_index()
        
        # Clean up expired cache entries
        self._cleanup()
    
    def _create_index(self) -> None:
        """Create a new cache index file."""
        index = {
            'entries': {},
            'last_cleanup': time.time()
        }
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def _load_index(self) -> Dict[str, Any]:
        """Load the cache index from file."""
        try:
            with open(self.index_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning("Cache index corrupted or missing, creating new one")
            self._create_index()
            with open(self.index_file, 'r') as f:
                return json.load(f)
    
    def _save_index(self) -> None:
        """Save the cache index to file."""
        with open(self.index_file, 'w') as f:
            json.dump(self.cache_index, f, indent=2)
    
    def _cleanup(self) -> None:
        """Clean up expired cache entries and enforce size limits."""
        now = time.time()
        
        # Only run cleanup once per day
        if now - self.cache_index.get('last_cleanup', 0) < 86400:  # 24 hours in seconds
            return
        
        logger.info("Running cache cleanup")
        
        # Remove expired entries
        expired_keys = []
        for key, entry in self.cache_index.get('entries', {}).items():
            if now - entry.get('timestamp', 0) > self.cache_expiration:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.remove(key)
        
        # Check cache size and remove oldest entries if needed
        total_size = self._get_cache_size()
        if total_size > self.max_cache_size:
            # Sort entries by timestamp (oldest first)
            sorted_entries = sorted(
                self.cache_index.get('entries', {}).items(),
                key=lambda x: x[1].get('timestamp', 0)
            )
            
            # Remove oldest entries until we're under the size limit
            for key, _ in sorted_entries:
                self.remove(key)
                total_size = self._get_cache_size()
                if total_size <= self.max_cache_size:
                    break
        
        # Update last cleanup timestamp
        self.cache_index['last_cleanup'] = now
        self._save_index()
    
    def _get_cache_size(self) -> int:
        """Get the total size of the cache in bytes."""
        total_size = 0
        for entry in self.cache_index.get('entries', {}).values():
            total_size += entry.get('size', 0)
        return total_size
    
    def _generate_key(self, data: Dict[str, Any], style: str) -> str:
        """
        Generate a cache key from CV data and style.
        
        Args:
            data: CV data dictionary
            style: CV style name
            
        Returns:
            str: Cache key
        """
        # Convert data to a stable string representation
        data_str = json.dumps(data, sort_keys=True)
        
        # Generate a hash of the data and style
        key_str = f"{data_str}_{style}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Path]:
        """
        Get a cached file by key.
        
        Args:
            key: Cache key
            
        Returns:
            Optional[Path]: Path to the cached file, or None if not found
        """
        if key not in self.cache_index.get('entries', {}):
            return None
        
        entry = self.cache_index['entries'][key]
        file_path = self.cache_dir / entry['filename']
        
        if not file_path.exists():
            # File is missing, remove from index
            self.remove(key)
            return None
        
        # Update access timestamp
        entry['last_accessed'] = time.time()
        self._save_index()
        
        return file_path
    
    def put(self, key: str, file_path: Union[str, Path], file_type: str) -> Path:
        """
        Add a file to the cache.
        
        Args:
            key: Cache key
            file_path: Path to the file to cache
            file_type: Type of file (e.g., 'latex', 'pdf')
            
        Returns:
            Path: Path to the cached file
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Create a filename with the key and original extension
        cached_filename = f"{key}_{file_type}{file_path.suffix}"
        cached_path = self.cache_dir / cached_filename
        
        # Copy the file to the cache directory
        shutil.copy2(file_path, cached_path)
        
        # Add entry to index
        self.cache_index.setdefault('entries', {})
        self.cache_index['entries'][key] = {
            'filename': cached_filename,
            'timestamp': time.time(),
            'last_accessed': time.time(),
            'size': cached_path.stat().st_size,
            'type': file_type
        }
        
        self._save_index()
        return cached_path
    
    def remove(self, key: str) -> None:
        """
        Remove a file from the cache.
        
        Args:
            key: Cache key
        """
        if key not in self.cache_index.get('entries', {}):
            return
        
        entry = self.cache_index['entries'][key]
        file_path = self.cache_dir / entry['filename']
        
        # Remove the file if it exists
        if file_path.exists():
            file_path.unlink()
        
        # Remove entry from index
        del self.cache_index['entries'][key]
        self._save_index()
    
    def clear(self) -> None:
        """Clear all cache entries."""
        # Remove all files in the cache directory
        for file_path in self.cache_dir.glob('*'):
            if file_path.is_file() and file_path.name != 'cache_index.json':
                file_path.unlink()
        
        # Reset the index
        self.cache_index['entries'] = {}
        self.cache_index['last_cleanup'] = time.time()
        self._save_index()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict[str, Any]: Dictionary of cache statistics
        """
        entries = self.cache_index.get('entries', {})
        total_size = self._get_cache_size()
        
        # Count entries by type
        type_counts = {}
        for entry in entries.values():
            file_type = entry.get('type', 'unknown')
            type_counts[file_type] = type_counts.get(file_type, 0) + 1
        
        return {
            'entry_count': len(entries),
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'max_size_mb': round(self.max_cache_size / (1024 * 1024), 2),
            'usage_percent': round((total_size / self.max_cache_size) * 100, 2) if self.max_cache_size > 0 else 0,
            'last_cleanup': self.cache_index.get('last_cleanup', 0),
            'type_counts': type_counts
        }


# Global cache manager instance
_cache_manager = None


def get_cache_manager() -> CacheManager:
    """
    Get the global cache manager instance.
    
    Returns:
        CacheManager: Global cache manager instance
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cache_cv_data(data: Dict[str, Any], style: str) -> str:
    """
    Generate a cache key for CV data and style.
    
    Args:
        data: CV data dictionary
        style: CV style name
        
    Returns:
        str: Cache key
    """
    cache_manager = get_cache_manager()
    return cache_manager._generate_key(data, style)


def get_cached_pdf(data: Dict[str, Any], style: str) -> Optional[Path]:
    """
    Get a cached PDF for CV data and style.
    
    Args:
        data: CV data dictionary
        style: CV style name
        
    Returns:
        Optional[Path]: Path to the cached PDF, or None if not found
    """
    cache_manager = get_cache_manager()
    key = cache_manager._generate_key(data, style)
    return cache_manager.get(key)


def cache_pdf(data: Dict[str, Any], style: str, pdf_path: Union[str, Path]) -> Path:
    """
    Cache a PDF for CV data and style.
    
    Args:
        data: CV data dictionary
        style: CV style name
        pdf_path: Path to the PDF file
        
    Returns:
        Path: Path to the cached PDF
    """
    cache_manager = get_cache_manager()
    key = cache_manager._generate_key(data, style)
    return cache_manager.put(key, pdf_path, 'pdf')


def clear_cache() -> None:
    """Clear the CV cache."""
    cache_manager = get_cache_manager()
    cache_manager.clear()


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics.
    
    Returns:
        Dict[str, Any]: Dictionary of cache statistics
    """
    cache_manager = get_cache_manager()
    return cache_manager.get_stats()
