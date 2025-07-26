"""
Comprehensive error handling and logging for the application.

This module provides centralized error handling, logging, and
user-friendly error reporting.
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


import sys
import traceback
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QLabel, QCheckBox, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon


class ErrorReporter:
    """Centralized error reporting system."""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.log_file = config_dir / "error.log"
        self.setup_logging()
        
    def setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('ColorFaintGray')
        
    def log_error(self, error: Exception, context: str = ""):
        """Log an error with context."""
        error_msg = f"Error in {context}: {str(error)}"
        self.logger.error(error_msg, exc_info=True)
        
    def log_info(self, message: str):
        """Log an informational message."""
        self.logger.info(message)
        
    def log_warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
        
    def show_error_dialog(self, error: Exception, context: str = "", parent=None):
        """Show user-friendly error dialog."""
        dialog = ErrorDialog(error, context, parent)
        return dialog.exec()


class ErrorDialog(QDialog):
    """User-friendly error dialog with details."""
    
    def __init__(self, error: Exception, context: str = "", parent=None):
        super().__init__(parent)
        self.error = error
        self.context = context
        self.setWindowTitle("Application Error")
        self.resize(500, 400)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the error dialog UI."""
        layout = QVBoxLayout(self)
        
        # Error icon and message
        header_layout = QHBoxLayout()
        
        # Error message
        error_label = QLabel(f"An error occurred: {str(self.error)}")
        error_label.setWordWrap(True)
        error_label.setFont(QFont("", 10, QFont.Weight.Bold))
        header_layout.addWidget(error_label)
        
        layout.addLayout(header_layout)
        
        # Context information
        if self.context:
            context_label = QLabel(f"Context: {self.context}")
            context_label.setWordWrap(True)
            layout.addWidget(context_label)
            
        # Show details checkbox
        self.show_details_cb = QCheckBox("Show technical details")
        self.show_details_cb.toggled.connect(self.toggle_details)
        layout.addWidget(self.show_details_cb)
        
        # Details text area
        self.details_text = QTextEdit()
        self.details_text.setFont(QFont("monospace", 9))
        self.details_text.setVisible(False)
        self.details_text.setPlainText(self.get_error_details())
        layout.addWidget(self.details_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        copy_button = QPushButton("Copy Details")
        copy_button.clicked.connect(self.copy_details)
        button_layout.addWidget(copy_button)
        
        button_layout.addStretch()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        
    def get_error_details(self) -> str:
        """Get formatted error details."""
        details = f"Error Type: {type(self.error).__name__}\\n"
        details += f"Error Message: {str(self.error)}\\n"
        if self.context:
            details += f"Context: {self.context}\\n"
        details += f"Timestamp: {datetime.now()}\\n\\n"
        details += "Traceback:\\n"
        details += traceback.format_exc()
        return details
        
    def toggle_details(self, show: bool):
        """Toggle details visibility."""
        self.details_text.setVisible(show)
        if show:
            self.resize(500, 600)
        else:
            self.resize(500, 200)
            
    def copy_details(self):
        """Copy error details to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.get_error_details())
        
        # Show feedback
        self.sender().setText("Copied!")
        QTimer.singleShot(2000, lambda: self.sender().setText("Copy Details"))


class GlobalExceptionHandler:
    """Global exception handler for unhandled exceptions."""
    
    def __init__(self, error_reporter: ErrorReporter):
        self.error_reporter = error_reporter
        self.original_excepthook = sys.excepthook
        sys.excepthook = self.handle_exception
        
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handle unhandled exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Allow keyboard interrupt to work normally
            self.original_excepthook(exc_type, exc_value, exc_traceback)
            return
            
        # Log the error
        self.error_reporter.log_error(exc_value, "Unhandled exception")
        
        # Show error dialog if Qt application is available
        try:
            app = QApplication.instance()
            if app:
                dialog = ErrorDialog(exc_value, "Unhandled exception")
                dialog.exec()
        except:
            pass
            
        # Call original handler
        self.original_excepthook(exc_type, exc_value, exc_traceback)


def safe_execute(func, *args, error_reporter: Optional[ErrorReporter] = None, 
                context: str = "", show_dialog: bool = True, **kwargs):
    """Safely execute a function with error handling."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if error_reporter:
            error_reporter.log_error(e, context)
            if show_dialog:
                error_reporter.show_error_dialog(e, context)
        else:
            print(f"Error in {context}: {e}")
            traceback.print_exc()
        return None


class ValidationError(Exception):
    """Exception for validation errors."""
    pass


class ConfigurationError(Exception):
    """Exception for configuration errors."""
    pass


class GenerationError(Exception):
    """Exception for image generation errors."""
    pass


def validate_fits_file(filepath: str) -> bool:
    """Validate FITS file format and readability."""
    try:
        from astropy.io import fits
        with fits.open(filepath) as hdul:
            # Check if file has data
            if len(hdul) == 0:
                raise ValidationError(f"FITS file {filepath} contains no data")
            
            # Check if primary HDU has data
            primary = hdul[0]
            if primary.data is None and len(hdul) == 1:
                raise ValidationError(f"FITS file {filepath} has no image data")
                
        return True
    except Exception as e:
        raise ValidationError(f"Invalid FITS file {filepath}: {e}")


def validate_astscript_parameters(parameters: dict) -> bool:
    """Validate astscript parameters."""
    required_params = ['r_channel', 'g_channel', 'b_channel']
    
    for param in required_params:
        if param not in parameters or not parameters[param]:
            raise ValidationError(f"Missing required parameter: {param}")
            
    # Validate parameter ranges
    param_ranges = {
        'qbright': (0.0, 100.0),
        'stretch': (0.0, 100.0),
        'gamma': (0.1, 10.0),
        'colorval': (0.0, None),  # No upper limit
        'grayval': (0.0, None),   # No upper limit
    }
    
    for param, (min_val, max_val) in param_ranges.items():
        if param in parameters:
            value = parameters[param]
            if value < min_val:
                raise ValidationError(f"Parameter {param} ({value}) below minimum ({min_val})")
            if max_val is not None and value > max_val:
                raise ValidationError(f"Parameter {param} ({value}) above maximum ({max_val})")
                
    return True
