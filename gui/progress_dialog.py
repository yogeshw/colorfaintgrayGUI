"""
Progress dialog for showing generation progress.

This module provides a progress dialog that shows the progress of
image generation and allows cancellation.
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


from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QProgressBar, 
    QPushButton, QLabel, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class ProgressDialog(QDialog):
    """Progress dialog for image generation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generating Image...")
        self.setModal(True)
        self.resize(400, 200)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        
        self.generator = None
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Generating color image...")
        title.setFont(QFont("", 10, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Preparing...")
        layout.addWidget(self.status_label)
        
        # Command display (expandable)
        self.command_text = QTextEdit()
        self.command_text.setMaximumHeight(60)
        self.command_text.setReadOnly(True)
        self.command_text.setFont(QFont("monospace", 8))
        layout.addWidget(self.command_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_generation)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Timer for progress updates
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        
    def start_generation(self, generator, command, params):
        """Start image generation with progress tracking."""
        self.generator = generator
        self.params = params
        self.command_text.setPlainText(command)
        
        # Connect signals with correct names
        generator.started.connect(self.on_started)
        generator.progress_updated.connect(self.on_status_changed)
        generator.finished.connect(self.on_finished)
        generator.error_occurred.connect(self.on_error)
        
        # Start generation
        generator.generate_image(params)
        
        # Start progress animation
        self.progress_timer.start(100)
        
    def on_started(self):
        """Handle generation start."""
        self.status_label.setText("Generation started...")
        
    def update_progress(self):
        """Update progress bar animation if indeterminate."""
        if self.progress_bar.value() < 100:
            # Pulse animation
            current = self.progress_bar.value()
            if current >= 90:
                self.progress_bar.setValue(10)
            else:
                self.progress_bar.setValue(current + 5)
                
    def on_progress(self, value):
        """Handle progress updates."""
        self.progress_bar.setValue(value)
        
    def on_status_changed(self, status):
        """Handle status updates."""
        self.status_label.setText(status)
        
    def on_finished(self, output_path, parameters):
        """Handle generation completion."""
        self.progress_timer.stop()
        self.progress_bar.setValue(100)
        self.status_label.setText("Generation completed!")
        self.accept()
            
    def on_error(self, error_msg):
        """Handle generation errors."""
        self.progress_timer.stop()
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Error: {error_msg}")
        self.cancel_button.setText("Close")
        
    def cancel_generation(self):
        """Cancel the generation process."""
        if self.generator:
            self.generator.cancel_generation()
            
        self.reject()
