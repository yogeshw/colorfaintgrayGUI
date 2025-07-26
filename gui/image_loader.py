"""
Image loader widget for selecting and validating input images.

This module provides the image loader tab that allows users to select
R, G, B channel images and validate them for processing.
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
from pathlib import Path
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFileDialog, QGroupBox, QTextEdit, QFrame, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QFont

from utils.file_utils import FileUtils


class ImageChannelWidget(QWidget):
    """Widget for a single image channel (R, G, or B)."""
    
    file_changed = pyqtSignal(str, str)  # channel, file_path
    
    def __init__(self, channel_name: str, channel_label: str, color: str, parent=None):
        """Initialize channel widget.
        
        Args:
            channel_name: Internal channel name (red, green, blue)
            channel_label: Display label for channel
            color: Color for styling
            parent: Parent widget
        """
        super().__init__(parent)
        self.channel_name = channel_name
        self.channel_label = channel_label
        self.color = color
        self.current_file = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Channel header
        header_layout = QHBoxLayout()
        
        # Channel label
        label = QLabel(f"{self.channel_label} Channel:")
        label.setStyleSheet(f"color: {self.color}; font-weight: bold; font-size: 14px;")
        header_layout.addWidget(label)
        
        header_layout.addStretch()
        
        # Browse button
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_file)
        header_layout.addWidget(self.browse_button)
        
        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_file)
        self.clear_button.setEnabled(False)
        header_layout.addWidget(self.clear_button)
        
        layout.addLayout(header_layout)
        
        # File info area
        self.info_frame = QFrame()
        self.info_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.info_frame.setMinimumHeight(120)
        info_layout = QVBoxLayout(self.info_frame)
        
        # File path label
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setWordWrap(True)
        self.file_path_label.setStyleSheet("color: gray; font-style: italic;")
        info_layout.addWidget(self.file_path_label)
        
        # File details
        self.details_label = QLabel("")
        self.details_label.setWordWrap(True)
        self.details_label.setFont(QFont("monospace", 9))
        info_layout.addWidget(self.details_label)
        
        # Validation status
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        info_layout.addWidget(self.status_label)
        
        layout.addWidget(self.info_frame)
    
    def browse_file(self):
        """Open file browser to select image."""
        current_dir = ""
        if self.current_file:
            current_dir = str(Path(self.current_file).parent)
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {self.channel_label} Channel Image",
            current_dir,
            "FITS Files (*.fits *.fit *.fts *.fits.fz);;All Files (*)"
        )
        
        if file_path:
            self.load_file(file_path)
    
    def load_file(self, file_path: str):
        """Load and validate file.
        
        Args:
            file_path: Path to image file
        """
        self.current_file = file_path
        self.clear_button.setEnabled(True)
        
        # Update file path display
        self.file_path_label.setText(str(Path(file_path).name))
        self.file_path_label.setStyleSheet("color: black;")
        
        # Validate and show file details
        self.validate_and_display_file()
        
        # Emit signal
        self.file_changed.emit(self.channel_name, file_path)
    
    def clear_file(self):
        """Clear current file selection."""
        self.current_file = None
        self.clear_button.setEnabled(False)
        
        # Reset displays
        self.file_path_label.setText("No file selected")
        self.file_path_label.setStyleSheet("color: gray; font-style: italic;")
        self.details_label.setText("")
        self.status_label.setText("")
        
        # Emit signal
        self.file_changed.emit(self.channel_name, "")
    
    def validate_and_display_file(self):
        """Validate file and display information."""
        if not self.current_file:
            return
        
        # Validate FITS file
        is_valid, error_msg = FileUtils.validate_fits_file(self.current_file)
        
        # Get file info
        file_info = FileUtils.get_fits_info(self.current_file)
        
        # Display file details
        if file_info:
            details_text = self.format_file_details(file_info)
            self.details_label.setText(details_text)
        
        # Display validation status
        if is_valid:
            self.status_label.setText("✓ Valid FITS file")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.status_label.setText(f"✗ {error_msg}")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
    
    def format_file_details(self, file_info: Dict) -> str:
        """Format file information for display.
        
        Args:
            file_info: File information dictionary
            
        Returns:
            Formatted details string
        """
        details = []
        
        # File size
        size_str = FileUtils.format_file_size(file_info.get('file_size', 0))
        details.append(f"Size: {size_str}")
        
        # HDU information
        hdus = file_info.get('hdus', [])
        if hdus:
            primary = hdus[0]
            if primary.get('has_data') and 'dimensions' in primary:
                dims = primary['dimensions']
                details.append(f"Dimensions: {' × '.join(map(str, dims))}")
                if len(dims) >= 2:
                    details.append(f"Image size: {dims[-1]} × {dims[-2]} pixels")
            
            if len(hdus) > 1:
                details.append(f"HDUs: {len(hdus)}")
        
        return "\n".join(details)
    
    def get_file_path(self) -> Optional[str]:
        """Get current file path.
        
        Returns:
            Current file path or None
        """
        return self.current_file
    
    def is_valid(self) -> bool:
        """Check if current file is valid.
        
        Returns:
            True if file is valid FITS file
        """
        if not self.current_file:
            return False
        
        is_valid, _ = FileUtils.validate_fits_file(self.current_file)
        return is_valid


class ImageLoaderWidget(QWidget):
    """Main image loader widget with R, G, B channel selection."""
    
    images_loaded = pyqtSignal(dict)  # file paths dict
    validation_changed = pyqtSignal(bool)  # is_valid
    
    def __init__(self, config, parent=None):
        """Initialize image loader widget.
        
        Args:
            config: Application configuration
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config
        
        # Channel widgets
        self.red_widget = None
        self.green_widget = None
        self.blue_widget = None
        
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Setup widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Image Channel Loader")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "Select FITS images for each color channel. The images will be used to create "
            "a color composite using astscript-color-faint-gray."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; margin-bottom: 20px;")
        layout.addWidget(instructions)
        
        # Channel widgets in scroll area
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Red channel
        self.red_widget = ImageChannelWidget("red_path", "Red", "#CC0000", self)
        scroll_layout.addWidget(self.red_widget)
        
        # Green channel
        self.green_widget = ImageChannelWidget("green_path", "Green", "#00AA00", self)
        scroll_layout.addWidget(self.green_widget)
        
        # Blue channel
        self.blue_widget = ImageChannelWidget("blue_path", "Blue", "#0066CC", self)
        scroll_layout.addWidget(self.blue_widget)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        # Load all button
        self.load_all_button = QPushButton("Load All Channels...")
        self.load_all_button.clicked.connect(self.load_all_channels)
        button_layout.addWidget(self.load_all_button)
        
        # Load default images button
        self.load_default_button = QPushButton("Load Default Images")
        self.load_default_button.clicked.connect(self.load_default_images)
        button_layout.addWidget(self.load_default_button)
        
        # Validate button
        self.validate_button = QPushButton("Validate Images")
        self.validate_button.clicked.connect(self.validate_all_images)
        button_layout.addWidget(self.validate_button)
        
        button_layout.addStretch()
        
        # Clear all button
        self.clear_all_button = QPushButton("Clear All")
        self.clear_all_button.clicked.connect(self.clear_all_channels)
        button_layout.addWidget(self.clear_all_button)
        
        layout.addLayout(button_layout)
        
        # Status area
        self.status_area = QTextEdit()
        self.status_area.setMaximumHeight(100)
        self.status_area.setReadOnly(True)
        self.status_area.setPlaceholderText("Validation messages will appear here...")
        layout.addWidget(self.status_area)
    
    def connect_signals(self):
        """Connect widget signals."""
        # Connect channel file change signals
        for widget in [self.red_widget, self.green_widget, self.blue_widget]:
            widget.file_changed.connect(self.on_file_changed)
    
    def load_all_channels(self):
        """Open dialog to select multiple files for all channels."""
        last_dir = self.config.get("app.last_input_dir", str(Path.home()))
        
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images for R, G, B Channels",
            last_dir,
            "FITS Files (*.fits *.fit *.fts *.fits.fz);;All Files (*)"
        )
        
        if files:
            self.load_files(files)
    
    def load_files(self, files: List[str]):
        """Load files into channels.
        
        Args:
            files: List of file paths
        """
        # Clear existing files
        self.clear_all_channels()
        
        # Assign files to channels
        widgets = [self.red_widget, self.green_widget, self.blue_widget]
        
        for i, file_path in enumerate(files):
            if i < len(widgets):
                widgets[i].load_file(file_path)
        
        # Update last directory
        if files:
            self.config.set("app.last_input_dir", str(Path(files[0]).parent))
        
        # Validate all
        self.validate_all_images()
    
    def load_default_images(self):
        """Load default SDSS9 M51 images into the channels."""
        # Define the default image paths
        default_files = [
            "SDSS9_M51_i.fits",  # Red channel (i-band)
            "SDSS9_M51_r.fits",  # Green channel (r-band) 
            "SDSS9_M51_g.fits"   # Blue channel (g-band)
        ]
        
        # Convert to absolute paths
        workspace_dir = Path.cwd()
        absolute_paths = []
        missing_files = []
        
        for filename in default_files:
            file_path = workspace_dir / filename
            if file_path.exists():
                absolute_paths.append(str(file_path))
            else:
                missing_files.append(filename)
        
        # Check if any files are missing
        if missing_files:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Default Images Not Found",
                f"Some default image files are missing:\n\n" +
                "\n".join(missing_files) +
                f"\n\nPlease ensure these files are in the application directory:\n{workspace_dir}"
            )
            return
        
        # Load the files using the existing load_files method
        self.load_files(absolute_paths)
        
        # Update status
        self.status_area.append("✓ Default SDSS9 M51 images loaded successfully")
    
    def clear_all_channels(self):
        """Clear all channel selections."""
        for widget in [self.red_widget, self.green_widget, self.blue_widget]:
            widget.clear_file()
        
        self.status_area.clear()
    
    def validate_all_images(self):
        """Validate all loaded images."""
        messages = []
        all_valid = True
        
        # Check each channel
        channels = [
            (self.red_widget, "Red"),
            (self.green_widget, "Green"),
            (self.blue_widget, "Blue")
        ]
        
        loaded_count = 0
        for widget, name in channels:
            if widget.get_file_path():
                loaded_count += 1
                if widget.is_valid():
                    messages.append(f"✓ {name} channel: Valid")
                else:
                    messages.append(f"✗ {name} channel: Invalid")
                    all_valid = False
            else:
                messages.append(f"○ {name} channel: Not loaded")
        
        # Check if we have enough images
        if loaded_count < 3:
            messages.append(f"\n⚠ Need 3 images, only {loaded_count} loaded")
            all_valid = False
        elif loaded_count == 3 and all_valid:
            messages.append("\n✓ All channels ready for processing!")
        
        # Display messages
        self.status_area.setText("\n".join(messages))
        
        # Emit validation status
        is_ready = loaded_count == 3 and all_valid
        self.validation_changed.emit(is_ready)
        
        if is_ready:
            self.images_loaded.emit(self.get_current_files())
    
    def on_file_changed(self, channel: str, file_path: str):
        """Handle file change in a channel.
        
        Args:
            channel: Channel name that changed
            file_path: New file path (empty if cleared)
        """
        # Auto-validate when files change
        QTimer.singleShot(100, self.validate_all_images)
    
    def get_current_files(self) -> Dict[str, str]:
        """Get current file paths for all channels.
        
        Returns:
            Dictionary with channel names and file paths
        """
        return {
            'red_path': self.red_widget.get_file_path() or "",
            'green_path': self.green_widget.get_file_path() or "",
            'blue_path': self.blue_widget.get_file_path() or ""
        }
    
    def are_all_valid(self) -> bool:
        """Check if all channels have valid files.
        
        Returns:
            True if all three channels have valid FITS files
        """
        widgets = [self.red_widget, self.green_widget, self.blue_widget]
        return all(widget.is_valid() for widget in widgets)
