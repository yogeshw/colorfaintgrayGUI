"""
Image generator for astscript-color-faint-gray.

This module provides functionality to generate color images using the
astscript-color-faint-gray script through subprocess management.
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
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, Callable
from PyQt6.QtCore import QObject, pyqtSignal, QThread

from core.command_builder import CommandBuilder


class ImageGenerationError(Exception):
    """Exception raised when image generation fails."""
    pass


class ImageGenerator(QObject):
    """Manages image generation using astscript-color-faint-gray."""
    
    # Signals for progress tracking
    started = pyqtSignal()
    progress_updated = pyqtSignal(str)  # Progress message
    finished = pyqtSignal(str, dict)    # (output_path, params)
    error_occurred = pyqtSignal(str)    # Error message
    
    def __init__(self, config, parent=None):
        """Initialize image generator.
        
        Args:
            config: Application configuration object
            parent: Parent QObject
        """
        super().__init__(parent)
        self.config = config
        self.command_builder = CommandBuilder(config.get_astscript_path())
        self._process = None
        self._cancelled = False
    
    def generate_image(self, params: Dict[str, Any], output_path: Optional[str] = None) -> None:
        """Generate color image asynchronously.
        
        This method starts image generation in a separate thread.
        
        Args:
            params: Generation parameters
            output_path: Output file path. If None, generates temporary path.
        """
        # Create worker thread for generation
        self.worker = ImageGenerationWorker(
            self.command_builder,
            params.copy(),
            output_path
        )
        
        # Connect worker signals
        self.worker.started.connect(self.started.emit)
        self.worker.progress_updated.connect(self.progress_updated.emit)
        self.worker.finished.connect(self.finished.emit)
        self.worker.error_occurred.connect(self.error_occurred.emit)
        
        # Start worker thread
        self.worker.start()
    
    def generate_image_sync(self, params: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """Generate color image synchronously.
        
        Args:
            params: Generation parameters
            output_path: Output file path. If None, generates temporary path.
            
        Returns:
            Path to generated image
            
        Raises:
            ImageGenerationError: If generation fails
        """
        try:
            # Validate parameters
            validation_errors = self.command_builder.validate_param_ranges(params)
            if validation_errors:
                raise ImageGenerationError(f"Parameter validation failed: {validation_errors}")
            
            # Generate output path if not provided
            if output_path is None:
                output_path = self._generate_output_path(params)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Add output path to parameters
            params['output_path'] = output_path
            
            # Build command
            cmd = self.command_builder.build_command(params)
            
            # Execute command
            self._execute_command(cmd)
            
            # Verify output exists
            if not os.path.exists(output_path):
                raise ImageGenerationError(f"Output file was not created: {output_path}")
            
            return output_path
            
        except Exception as e:
            raise ImageGenerationError(f"Image generation failed: {e}")
    
    def cancel_generation(self):
        """Cancel ongoing image generation."""
        self._cancelled = True
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.cancel()
    
    def _execute_command(self, cmd: list) -> None:
        """Execute astscript command.
        
        Args:
            cmd: Command list to execute
            
        Raises:
            ImageGenerationError: If command execution fails
        """
        try:
            # Start process
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Wait for completion
            stdout, stderr = self._process.communicate()
            
            # Check for cancellation
            if self._cancelled:
                raise ImageGenerationError("Generation cancelled by user")
            
            # Check return code
            if self._process.returncode != 0:
                error_msg = f"astscript-color-faint-gray failed (exit code {self._process.returncode})"
                if stderr.strip():
                    error_msg += f":\n{stderr.strip()}"
                raise ImageGenerationError(error_msg)
            
        except subprocess.TimeoutExpired:
            if self._process:
                self._process.kill()
            raise ImageGenerationError("Generation timed out")
        except FileNotFoundError:
            raise ImageGenerationError(
                "astscript-color-faint-gray not found. "
                "Please ensure GNU Astronomy Utilities is installed."
            )
        finally:
            self._process = None
    
    def _generate_output_path(self, params: Dict[str, Any]) -> str:
        """Generate unique output path for image.
        
        Args:
            params: Generation parameters
            
        Returns:
            Generated output path
        """
        # Create timestamp-based filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate parameter hash for uniqueness
        param_hash = self._generate_param_hash(params)
        
        # Create filename
        filename = f"color_image_{timestamp}_{param_hash}.tif"
        
        # Use cache directory
        cache_dir = self.config.get_cache_dir() / "images"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        return str(cache_dir / filename)
    
    def _generate_param_hash(self, params: Dict[str, Any]) -> str:
        """Generate short hash from parameters for filename uniqueness.
        
        Args:
            params: Parameters dictionary
            
        Returns:
            Short hash string
        """
        import hashlib
        
        # Create string representation of key parameters
        key_params = {
            'qbright': params.get('qbright'),
            'stretch': params.get('stretch'),
            'gamma': params.get('gamma'),
            'colorval': params.get('colorval'),
            'grayval': params.get('grayval'),
            'coloronly': params.get('coloronly', False)
        }
        
        param_str = str(sorted(key_params.items()))
        return hashlib.md5(param_str.encode()).hexdigest()[:8]


class ImageGenerationWorker(QThread):
    """Worker thread for image generation."""
    
    started = pyqtSignal()
    progress_updated = pyqtSignal(str)
    finished = pyqtSignal(str, dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, command_builder: CommandBuilder, params: Dict[str, Any], 
                 output_path: Optional[str] = None):
        """Initialize worker.
        
        Args:
            command_builder: Command builder instance
            params: Generation parameters
            output_path: Output file path
        """
        super().__init__()
        self.command_builder = command_builder
        self.params = params
        self.output_path = output_path
        self._cancelled = False
    
    def run(self):
        """Run image generation in thread."""
        try:
            self.started.emit()
            self.progress_updated.emit("Validating parameters...")
            
            # Validate parameters
            validation_errors = self.command_builder.validate_param_ranges(self.params)
            if validation_errors:
                self.error_occurred.emit(f"Parameter validation failed: {validation_errors}")
                return
            
            self.progress_updated.emit("Preparing output path...")
            
            # Generate output path if not provided
            if self.output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_dir = Path(tempfile.gettempdir()) / "astscript_gui"
                temp_dir.mkdir(exist_ok=True)
                self.output_path = str(temp_dir / f"color_image_{timestamp}.tif")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            
            # Add output path to parameters
            self.params['output_path'] = self.output_path
            
            self.progress_updated.emit("Building command...")
            
            # Build command
            cmd = self.command_builder.build_command(self.params)
            
            self.progress_updated.emit("Executing astscript-color-faint-gray...")
            
            # Execute command
            self._execute_command(cmd)
            
            if self._cancelled:
                return
            
            self.progress_updated.emit("Verifying output...")
            
            # Verify output exists
            if not os.path.exists(self.output_path):
                self.error_occurred.emit(f"Output file was not created: {self.output_path}")
                return
            
            self.progress_updated.emit("Generation completed successfully!")
            self.finished.emit(self.output_path, self.params)
            
        except Exception as e:
            self.error_occurred.emit(f"Image generation failed: {e}")
    
    def cancel(self):
        """Cancel the worker thread."""
        self._cancelled = True
        if hasattr(self, '_process') and self._process:
            try:
                self._process.terminate()
            except:
                pass
    
    def _execute_command(self, cmd: list):
        """Execute the astscript command."""
        try:
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for completion
            stdout, stderr = self._process.communicate()
            
            if self._cancelled:
                return
            
            # Check return code
            if self._process.returncode != 0:
                error_msg = f"astscript-color-faint-gray failed (exit code {self._process.returncode})"
                if stderr.strip():
                    error_msg += f":\n{stderr.strip()}"
                raise Exception(error_msg)
                
        except subprocess.TimeoutExpired:
            if self._process:
                self._process.kill()
            raise Exception("Generation timed out")
        except FileNotFoundError:
            raise Exception(
                "astscript-color-faint-gray not found. "
                "Please ensure GNU Astronomy Utilities is installed."
            )
        finally:
            self._process = None
