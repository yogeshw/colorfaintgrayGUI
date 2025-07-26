"""
File utilities for handling astronomical images and FITS files.

This module provides utilities for file operations, validation,
and basic image processing tasks.
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


import os
import mimetypes
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import tempfile


class FileUtils:
    """Utility functions for file operations."""
    
    @staticmethod
    def is_fits_file(file_path: str) -> bool:
        """Check if file is a FITS file.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file appears to be FITS format
        """
        if not os.path.exists(file_path):
            return False
        
        path = Path(file_path)
        
        # Check extension
        if path.suffix.lower() in ['.fits', '.fit', '.fts']:
            return True
        
        # Check compressed FITS
        if path.suffix.lower() == '.fz' and path.stem.endswith(('.fits', '.fit', '.fts')):
            return True
        
        # Check magic bytes
        try:
            with open(file_path, 'rb') as f:
                header = f.read(80)
                if header.startswith(b'SIMPLE  =') or header.startswith(b'XTENSION='):
                    return True
        except IOError:
            pass
        
        return False
    
    @staticmethod
    def validate_fits_file(file_path: str) -> Tuple[bool, Optional[str]]:
        """Validate FITS file and return error message if invalid.
        
        Args:
            file_path: Path to FITS file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not os.path.exists(file_path):
            return False, f"File does not exist: {file_path}"
        
        if not FileUtils.is_fits_file(file_path):
            return False, f"File is not a FITS file: {file_path}"
        
        try:
            # Try to import astropy for validation
            from astropy.io import fits
            
            # Open and validate FITS file
            with fits.open(file_path) as hdul:
                if len(hdul) == 0:
                    return False, "FITS file contains no HDUs"
                
                # Check if primary HDU has data
                primary = hdul[0]
                if primary.data is None and len(hdul) == 1:
                    return False, "Primary HDU contains no image data"
                
                # If primary is empty, check for image extensions
                if primary.data is None:
                    has_image = any(
                        hdu.data is not None and len(hdu.data.shape) >= 2
                        for hdu in hdul[1:]
                    )
                    if not has_image:
                        return False, "No image data found in any HDU"
            
            return True, None
            
        except ImportError:
            # astropy not available, do basic validation
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(2880)  # Standard FITS block size
                    if not (header.startswith(b'SIMPLE  =') or header.startswith(b'XTENSION=')):
                        return False, "Invalid FITS header"
                return True, None
            except IOError as e:
                return False, f"Error reading file: {e}"
        
        except Exception as e:
            return False, f"FITS validation error: {e}"
    
    @staticmethod
    def get_fits_info(file_path: str) -> Optional[Dict[str, Any]]:
        """Get basic information about a FITS file.
        
        Args:
            file_path: Path to FITS file
            
        Returns:
            Dictionary with file information or None if error
        """
        if not FileUtils.is_fits_file(file_path):
            return None
        
        try:
            from astropy.io import fits
            
            info = {
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'hdus': []
            }
            
            with fits.open(file_path) as hdul:
                for i, hdu in enumerate(hdul):
                    hdu_info = {
                        'index': i,
                        'name': hdu.name,
                        'type': type(hdu).__name__,
                        'has_data': hdu.data is not None
                    }
                    
                    if hdu.data is not None:
                        hdu_info.update({
                            'dimensions': hdu.data.shape,
                            'dtype': str(hdu.data.dtype)
                        })
                    
                    # Get some header keywords
                    hdu_info['header_keywords'] = {}
                    for key in ['OBJECT', 'FILTER', 'EXPTIME', 'DATE-OBS']:
                        if key in hdu.header:
                            hdu_info['header_keywords'][key] = hdu.header[key]
                    
                    info['hdus'].append(hdu_info)
            
            return info
            
        except ImportError:
            # Basic info without astropy
            return {
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'hdus': [{'index': 0, 'name': 'PRIMARY', 'has_data': True}]
            }
        except Exception:
            return None
    
    @staticmethod
    def get_supported_image_formats() -> List[str]:
        """Get list of supported image file extensions.
        
        Returns:
            List of supported file extensions
        """
        return ['.fits', '.fit', '.fts', '.fits.fz', '.fit.fz', '.fts.fz']
    
    @staticmethod
    def get_output_formats() -> List[str]:
        """Get list of supported output image formats.
        
        Returns:
            List of output format extensions
        """
        return ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.tif']
    
    @staticmethod
    def suggest_output_filename(input_files: List[str], 
                               parameters: Optional[Dict[str, Any]] = None,
                               output_format: str = "tif") -> str:
        """Suggest output filename based on inputs and parameters.
        
        Args:
            input_files: List of input file paths
            parameters: Generation parameters
            output_format: Output format extension (without dot)
            
        Returns:
            Suggested filename
        """
        if not input_files:
            base_name = "color_image"
        else:
            # Use first input file as base
            first_file = Path(input_files[0])
            base_name = first_file.stem
            
            # Remove common suffixes
            for suffix in ['_r', '_g', '_b', '_red', '_green', '_blue']:
                if base_name.lower().endswith(suffix):
                    base_name = base_name[:-len(suffix)]
                    break
        
        # Add parameter info if significant
        if parameters:
            param_parts = []
            if parameters.get('qbright') != 1.0:
                param_parts.append(f"q{parameters['qbright']}")
            if parameters.get('stretch') != 1.0:
                param_parts.append(f"s{parameters['stretch']}")
            if parameters.get('coloronly'):
                param_parts.append("coloronly")
            
            if param_parts:
                base_name += "_" + "_".join(param_parts)
        
        # Ensure proper extension
        output_format = output_format.lstrip('.')
        return f"{base_name}_color.{output_format}"
    
    @staticmethod
    def create_temp_directory() -> str:
        """Create temporary directory for processing.
        
        Returns:
            Path to temporary directory
        """
        temp_dir = tempfile.mkdtemp(prefix="astscript_gui_")
        return temp_dir
    
    @staticmethod
    def cleanup_temp_directory(temp_dir: str) -> None:
        """Clean up temporary directory.
        
        Args:
            temp_dir: Path to temporary directory to remove
        """
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except OSError:
            pass  # Ignore cleanup errors
    
    @staticmethod
    def get_file_type_description(file_path: str) -> str:
        """Get human-readable description of file type.
        
        Args:
            file_path: Path to file
            
        Returns:
            File type description
        """
        if not os.path.exists(file_path):
            return "File not found"
        
        if FileUtils.is_fits_file(file_path):
            path = Path(file_path)
            if path.suffix.lower() == '.fz':
                return "Compressed FITS Image"
            else:
                return "FITS Image"
        
        # Try to determine type from mime
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            if mime_type.startswith('image/'):
                return f"Image ({mime_type.split('/')[-1].upper()})"
            else:
                return mime_type
        
        return "Unknown file type"
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format.
        
        Args:
            size_bytes: File size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                if unit == 'B':
                    return f"{size_bytes} {unit}"
                else:
                    return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    @staticmethod
    def check_file_permissions(file_path: str) -> Dict[str, bool]:
        """Check file permissions.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with permission flags
        """
        if not os.path.exists(file_path):
            return {'exists': False, 'readable': False, 'writable': False}
        
        return {
            'exists': True,
            'readable': os.access(file_path, os.R_OK),
            'writable': os.access(file_path, os.W_OK)
        }
    
    @staticmethod
    def validate_output_path(output_path: str) -> Tuple[bool, Optional[str]]:
        """Validate output file path.
        
        Args:
            output_path: Proposed output path
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(output_path)
        
        # Check if parent directory exists or can be created
        parent_dir = path.parent
        if not parent_dir.exists():
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                return False, f"Cannot create output directory: {e}"
        
        # Check if parent directory is writable
        if not os.access(parent_dir, os.W_OK):
            return False, f"Output directory is not writable: {parent_dir}"
        
        # Check if file already exists and is writable
        if path.exists() and not os.access(path, os.W_OK):
            return False, f"Output file exists and is not writable: {output_path}"
        
        # Check file extension
        if path.suffix.lower() not in FileUtils.get_output_formats():
            return False, f"Unsupported output format: {path.suffix}"
        
        return True, None
