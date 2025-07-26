"""
Cache manager for storing and managing generated images.

This module provides functionality to cache generated images with metadata,
manage cache size limits, and provide access to cached images.
"""
"""
Copyright (C) 2025 Yogesh Wadadekar

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""


import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict


@dataclass
class CacheEntry:
    """Represents a cached image entry."""
    image_path: str
    timestamp: str
    parameters: Dict[str, Any]
    input_files: Dict[str, str]  # red, green, blue paths
    file_size: int
    thumbnail_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Create from dictionary."""
        return cls(**data)


class CacheManager:
    """Manages image cache with metadata and size limits."""
    
    def __init__(self, cache_dir: Path, max_entries: int = 25):
        """Initialize cache manager.
        
        Args:
            cache_dir: Directory for cache storage
            max_entries: Maximum number of cached entries
        """
        self.cache_dir = Path(cache_dir)
        self.images_dir = self.cache_dir / "images"
        self.thumbnails_dir = self.cache_dir / "thumbnails"
        self.metadata_file = self.cache_dir / "metadata.json"
        self.max_entries = max_entries
        
        # Create directories
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(exist_ok=True)
        self.thumbnails_dir.mkdir(exist_ok=True)
        
        # Load existing metadata
        self._entries = self._load_metadata()
    
    def add_image(self, image_path: str, parameters: Dict[str, Any], 
                  input_files: Dict[str, str]) -> str:
        """Add image to cache.
        
        Args:
            image_path: Path to generated image
            parameters: Parameters used for generation
            input_files: Dictionary of input file paths (red, green, blue)
            
        Returns:
            Cache entry ID
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Generate unique cache entry ID
        timestamp = datetime.now().isoformat()
        entry_id = self._generate_entry_id(timestamp, parameters)
        
        # Copy image to cache
        cached_image_path = self.images_dir / f"{entry_id}.tif"
        shutil.copy2(image_path, cached_image_path)
        
        # Get file size
        file_size = os.path.getsize(cached_image_path)
        
        # Create cache entry
        entry = CacheEntry(
            image_path=str(cached_image_path),
            timestamp=timestamp,
            parameters=parameters.copy(),
            input_files=input_files.copy(),
            file_size=file_size
        )
        
        # Add to cache
        self._entries[entry_id] = entry
        
        # Generate thumbnail
        self._generate_thumbnail(entry_id, cached_image_path)
        
        # Enforce cache size limit
        self._enforce_cache_limit()
        
        # Save metadata
        self._save_metadata()
        
        return entry_id
    
    def get_entry(self, entry_id: str) -> Optional[CacheEntry]:
        """Get cache entry by ID.
        
        Args:
            entry_id: Cache entry identifier
            
        Returns:
            Cache entry or None if not found
        """
        return self._entries.get(entry_id)
    
    def get_all_entries(self, sort_by: str = "timestamp") -> List[Tuple[str, CacheEntry]]:
        """Get all cache entries.
        
        Args:
            sort_by: Sort criteria ("timestamp", "parameters")
            
        Returns:
            List of (entry_id, entry) tuples sorted by criteria
        """
        entries = list(self._entries.items())
        
        if sort_by == "timestamp":
            entries.sort(key=lambda x: x[1].timestamp, reverse=True)
        
        return entries
    
    def remove_entry(self, entry_id: str) -> bool:
        """Remove entry from cache.
        
        Args:
            entry_id: Entry to remove
            
        Returns:
            True if entry was removed, False if not found
        """
        if entry_id not in self._entries:
            return False
        
        entry = self._entries[entry_id]
        
        # Remove files
        try:
            if os.path.exists(entry.image_path):
                os.remove(entry.image_path)
            if entry.thumbnail_path and os.path.exists(entry.thumbnail_path):
                os.remove(entry.thumbnail_path)
        except OSError:
            pass  # Continue even if file removal fails
        
        # Remove from entries
        del self._entries[entry_id]
        
        # Save metadata
        self._save_metadata()
        
        return True
    
    def clear_cache(self) -> int:
        """Clear all cache entries.
        
        Returns:
            Number of entries removed
        """
        count = len(self._entries)
        
        # Remove all files
        try:
            shutil.rmtree(self.images_dir)
            shutil.rmtree(self.thumbnails_dir)
            self.images_dir.mkdir(exist_ok=True)
            self.thumbnails_dir.mkdir(exist_ok=True)
        except OSError:
            pass
        
        # Clear entries
        self._entries.clear()
        
        # Save metadata
        self._save_metadata()
        
        return count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_size = sum(entry.file_size for entry in self._entries.values())
        
        return {
            "total_entries": len(self._entries),
            "max_entries": self.max_entries,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "cache_dir": str(self.cache_dir)
        }
    
    def search_entries(self, query: str) -> List[Tuple[str, CacheEntry]]:
        """Search cache entries.
        
        Args:
            query: Search query
            
        Returns:
            List of matching (entry_id, entry) tuples
        """
        query_lower = query.lower()
        matches = []
        
        for entry_id, entry in self._entries.items():
            # Search in parameters
            param_str = str(entry.parameters).lower()
            if query_lower in param_str:
                matches.append((entry_id, entry))
                continue
            
            # Search in input file names
            input_str = str(entry.input_files).lower()
            if query_lower in input_str:
                matches.append((entry_id, entry))
                continue
        
        return matches
    
    def export_cache(self, destination_dir: str) -> Dict[str, str]:
        """Export all cached images to destination directory.
        
        Args:
            destination_dir: Destination directory path
            
        Returns:
            Dictionary mapping entry_id to exported file path
        """
        dest_path = Path(destination_dir)
        dest_path.mkdir(parents=True, exist_ok=True)
        
        exported = {}
        
        for entry_id, entry in self._entries.items():
            if os.path.exists(entry.image_path):
                # Create descriptive filename
                timestamp = entry.timestamp[:10]  # Just date part
                filename = f"{timestamp}_{entry_id}.tif"
                dest_file = dest_path / filename
                
                # Copy file
                shutil.copy2(entry.image_path, dest_file)
                exported[entry_id] = str(dest_file)
        
        return exported
    
    def _generate_entry_id(self, timestamp: str, parameters: Dict[str, Any]) -> str:
        """Generate unique entry ID.
        
        Args:
            timestamp: ISO timestamp string
            parameters: Generation parameters
            
        Returns:
            Unique entry identifier
        """
        import hashlib
        
        # Use timestamp + parameter hash
        param_str = str(sorted(parameters.items()))
        param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
        
        # Format: YYYYMMDD_HHMMSS_HASH
        time_part = timestamp.replace(":", "").replace("-", "")[:15]
        return f"{time_part}_{param_hash}"
    
    def _generate_thumbnail(self, entry_id: str, image_path: str) -> None:
        """Generate thumbnail for cached image.
        
        Args:
            entry_id: Cache entry ID
            image_path: Path to original image
        """
        try:
            from PIL import Image
            
            # Check if it's a supported image format
            if not str(image_path).lower().endswith(('.tif', '.tiff', '.png', '.jpg', '.jpeg')):
                # For unsupported formats (e.g., PDF), skip thumbnail generation
                return
            
            # Generate thumbnail
            thumbnail_path = self.thumbnails_dir / f"{entry_id}.png"
            
            # Open and resize image
            with Image.open(image_path) as img:
                # Calculate thumbnail size while maintaining aspect ratio
                img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                
                # Save as PNG
                img.save(str(thumbnail_path), "PNG")
                
                # Update entry with thumbnail path
                self._entries[entry_id].thumbnail_path = str(thumbnail_path)
            
        except ImportError:
            # PIL not available, skip thumbnail generation
            pass
        except Exception as e:
            # Error generating thumbnail, skip
            print(f"Warning: Failed to generate thumbnail for {image_path}: {e}")
            pass
    
    def _enforce_cache_limit(self) -> None:
        """Enforce maximum cache size by removing oldest entries."""
        while len(self._entries) > self.max_entries:
            # Find oldest entry
            oldest_id = min(
                self._entries.keys(),
                key=lambda k: self._entries[k].timestamp
            )
            self.remove_entry(oldest_id)
    
    def _load_metadata(self) -> Dict[str, CacheEntry]:
        """Load metadata from file.
        
        Returns:
            Dictionary of cache entries
        """
        if not self.metadata_file.exists():
            return {}
        
        try:
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
            
            entries = {}
            for entry_id, entry_data in data.items():
                try:
                    entries[entry_id] = CacheEntry.from_dict(entry_data)
                except (KeyError, TypeError):
                    # Skip malformed entries
                    continue
            
            # Verify that image files still exist and fix paths if needed
            valid_entries = {}
            for entry_id, entry in entries.items():
                # Check if image path exists
                if os.path.exists(entry.image_path):
                    valid_entries[entry_id] = entry
                else:
                    # Try to fix the path - check if the image exists in our current cache
                    expected_path = self.images_dir / f"{entry_id}.tif"
                    if expected_path.exists():
                        # Update the path and add to valid entries
                        entry.image_path = str(expected_path)
                        valid_entries[entry_id] = entry
                        print(f"Fixed cache path for {entry_id}: {expected_path}")
                
                # Also fix thumbnail path if needed
                if entry_id in valid_entries and entry.thumbnail_path:
                    if not os.path.exists(entry.thumbnail_path):
                        expected_thumbnail = self.thumbnails_dir / f"{entry_id}.png"
                        if expected_thumbnail.exists():
                            entry.thumbnail_path = str(expected_thumbnail)
                            print(f"Fixed thumbnail path for {entry_id}: {expected_thumbnail}")

            return valid_entries
            
        except (json.JSONDecodeError, IOError):
            # Return empty cache if metadata is corrupted
            return {}
    
    def _save_metadata(self) -> None:
        """Save metadata to file."""
        try:
            data = {
                entry_id: entry.to_dict()
                for entry_id, entry in self._entries.items()
            }
            
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except IOError:
            # Continue silently if save fails
            pass
