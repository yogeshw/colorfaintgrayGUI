"""
Image viewer widget for displaying generated color images.

This module provides the image viewer tab that displays generated images
with zoom, pan, and navigation capabilities.
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
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QFrame, QSizePolicy, QToolBar, QSlider, QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint, QSize
from PyQt6.QtGui import QPixmap, QImage, QPainter, QWheelEvent, QMouseEvent, QPen, QBrush


class ImageDisplayWidget(QLabel):
    """Custom widget for displaying and interacting with images."""
    
    def __init__(self, parent=None):
        """Initialize image display widget."""
        super().__init__(parent)
        
        # Image data
        self.original_pixmap = None
        self.scaled_pixmap = None
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 10.0
        
        # Pan support
        self.last_pan_point = QPoint()
        self.pan_offset = QPoint(0, 0)
        self.is_panning = False
        
        # Widget setup
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(400, 400)
        self.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.setScaledContents(False)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Mouse tracking for pan
        self.setMouseTracking(True)
        
        # Initial state
        self.set_placeholder_text("No image loaded")
    
    def load_image(self, image_path: str) -> bool:
        """Load image from file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if image loaded successfully
        """
        if not os.path.exists(image_path):
            self.set_placeholder_text("Image file not found")
            return False
        
        # For PDF files, we'd need a PDF rendering library
        # For now, show a placeholder for PDFs
        if image_path.lower().endswith('.pdf'):
            self.set_placeholder_text(f"PDF Image\n{Path(image_path).name}\n\n(PDF preview not implemented)")
            return True
        
        try:
            # Load pixmap
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                self.set_placeholder_text("Failed to load image")
                return False
            
            self.original_pixmap = pixmap
            self.reset_view()
            return True
            
        except Exception as e:
            self.set_placeholder_text(f"Error loading image:\n{e}")
            return False
    
    def set_placeholder_text(self, text: str):
        """Set placeholder text when no image is loaded.
        
        Args:
            text: Placeholder text to display
        """
        self.original_pixmap = None
        self.scaled_pixmap = None
        self.setText(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def reset_view(self):
        """Reset zoom and pan to default view."""
        if not self.original_pixmap:
            return
        
        self.zoom_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self.fit_to_window()
    
    def fit_to_window(self):
        """Fit image to window size."""
        if not self.original_pixmap:
            return
        
        # Get the scroll area size instead of widget size for better fitting
        scroll_area = self.parent()
        if hasattr(scroll_area, 'viewport'):
            available_size = scroll_area.viewport().size()
        else:
            available_size = self.size()
        
        image_size = self.original_pixmap.size()
        
        # Add some padding to account for potential scrollbars
        padding = 20
        available_size = QSize(available_size.width() - padding, available_size.height() - padding)
        
        scale_x = available_size.width() / image_size.width()
        scale_y = available_size.height() / image_size.height()
        scale = min(scale_x, scale_y)  # Allow scaling beyond 100% to fill space
        
        self.zoom_factor = scale
        self.update_display()
    
    def fill_window(self):
        """Fill the window with the image (may crop some parts)."""
        if not self.original_pixmap:
            return
        
        # Get the scroll area size for better filling
        scroll_area = self.parent()
        if hasattr(scroll_area, 'viewport'):
            available_size = scroll_area.viewport().size()
        else:
            available_size = self.size()
        
        image_size = self.original_pixmap.size()
        
        scale_x = available_size.width() / image_size.width()
        scale_y = available_size.height() / image_size.height()
        scale = max(scale_x, scale_y)  # Use max to fill entire space
        
        self.zoom_factor = scale
        self.update_display()
    
    def zoom_in(self):
        """Zoom in by 25%."""
        self.set_zoom(self.zoom_factor * 1.25)
    
    def zoom_out(self):
        """Zoom out by 25%."""
        self.set_zoom(self.zoom_factor / 1.25)
    
    def set_zoom(self, zoom_factor: float):
        """Set specific zoom factor.
        
        Args:
            zoom_factor: New zoom factor
        """
        if not self.original_pixmap:
            return
        
        # Clamp zoom factor
        zoom_factor = max(self.min_zoom, min(self.max_zoom, zoom_factor))
        
        if zoom_factor != self.zoom_factor:
            self.zoom_factor = zoom_factor
            self.update_display()
    
    def update_display(self):
        """Update the displayed image."""
        if not self.original_pixmap:
            return
        
        # Calculate scaled size
        scaled_size = QSize(
            int(self.original_pixmap.width() * self.zoom_factor),
            int(self.original_pixmap.height() * self.zoom_factor)
        )
        
        # Create scaled pixmap
        self.scaled_pixmap = self.original_pixmap.scaled(
            scaled_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Resize the widget to match the scaled image size
        self.resize(scaled_size)
        
        # Clear text and set pixmap
        self.setText("")
        self.setPixmap(self.scaled_pixmap)
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zooming."""
        if not self.original_pixmap:
            return
        
        # Get wheel delta
        delta = event.angleDelta().y()
        
        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
        
        event.accept()
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for starting pan."""
        if event.button() == Qt.MouseButton.LeftButton and self.original_pixmap:
            self.is_panning = True
            self.last_pan_point = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for panning."""
        if self.is_panning and self.original_pixmap:
            # Calculate pan delta
            delta = event.pos() - self.last_pan_point
            self.last_pan_point = event.pos()
            
            # Pan by adjusting the parent scroll area's scrollbars
            parent_scroll = self.parent()
            if hasattr(parent_scroll, 'horizontalScrollBar') and hasattr(parent_scroll, 'verticalScrollBar'):
                h_bar = parent_scroll.horizontalScrollBar()
                v_bar = parent_scroll.verticalScrollBar()
                
                # Invert delta for natural panning direction
                h_bar.setValue(h_bar.value() - delta.x())
                v_bar.setValue(v_bar.value() - delta.y())
            
        elif self.original_pixmap:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release for ending pan."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_panning = False
            if self.original_pixmap:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        
        super().mouseReleaseEvent(event)
    
    def get_zoom_factor(self) -> float:
        """Get current zoom factor."""
        return self.zoom_factor
    
    def has_image(self) -> bool:
        """Check if an image is currently loaded."""
        return self.original_pixmap is not None


class ImageViewer(QWidget):
    """Image viewer widget with controls."""
    
    def __init__(self, parent=None):
        """Initialize image viewer."""
        super().__init__(parent)
        
        # Current image info
        self.current_image_path = None
        
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Setup viewer UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Toolbar
        self.setup_toolbar(layout)
        
        # Image display area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)  # Changed to False for better zoom/pan
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Image display widget
        self.image_display = ImageDisplayWidget()
        self.scroll_area.setWidget(self.image_display)
        
        layout.addWidget(self.scroll_area)
        
        # Status bar
        self.setup_status_bar(layout)
    
    def setup_toolbar(self, parent_layout):
        """Setup viewer toolbar."""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(3, 3, 3, 3)
        
        # Zoom controls
        zoom_label = QLabel("Zoom:")
        toolbar_layout.addWidget(zoom_label)
        
        self.zoom_out_btn = QPushButton("-")
        self.zoom_out_btn.setMaximumWidth(30)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        toolbar_layout.addWidget(self.zoom_out_btn)
        
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(10)  # 10% zoom
        self.zoom_slider.setMaximum(1000)  # 1000% zoom
        self.zoom_slider.setValue(100)  # 100% zoom
        self.zoom_slider.setMaximumWidth(120)
        self.zoom_slider.valueChanged.connect(self.on_zoom_slider_changed)
        toolbar_layout.addWidget(self.zoom_slider)
        
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setMaximumWidth(30)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        toolbar_layout.addWidget(self.zoom_in_btn)
        
        self.zoom_spinbox = QSpinBox()
        self.zoom_spinbox.setMinimum(10)
        self.zoom_spinbox.setMaximum(1000)
        self.zoom_spinbox.setValue(100)
        self.zoom_spinbox.setSuffix("%")
        self.zoom_spinbox.setMaximumWidth(70)
        self.zoom_spinbox.valueChanged.connect(self.on_zoom_spinbox_changed)
        toolbar_layout.addWidget(self.zoom_spinbox)
        
        # Add separator (spacer)
        spacer = QWidget()
        spacer.setFixedWidth(10)
        toolbar_layout.addWidget(spacer)
        
        # View controls
        self.fit_btn = QPushButton("Fit")
        self.fit_btn.setToolTip("Fit entire image to window (may show white space)")
        self.fit_btn.clicked.connect(self.fit_to_window)
        toolbar_layout.addWidget(self.fit_btn)
        
        self.fill_btn = QPushButton("Fill")
        self.fill_btn.setToolTip("Fill window with image (may crop parts of image)")
        self.fill_btn.clicked.connect(self.fill_window)
        toolbar_layout.addWidget(self.fill_btn)
        
        self.actual_size_btn = QPushButton("100%")
        self.actual_size_btn.setToolTip("Show image at actual size (100% zoom)")
        self.actual_size_btn.clicked.connect(self.actual_size)
        toolbar_layout.addWidget(self.actual_size_btn)
        
        toolbar_layout.addStretch()
        
        # Info button
        self.info_btn = QPushButton("Image Info")
        self.info_btn.clicked.connect(self.show_image_info)
        self.info_btn.setEnabled(False)
        toolbar_layout.addWidget(self.info_btn)
        
        parent_layout.addWidget(toolbar)
    
    def setup_status_bar(self, parent_layout):
        """Setup status bar."""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(3, 3, 3, 3)
        
        self.status_label = QLabel("No image loaded")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.zoom_label = QLabel("Zoom: --")
        status_layout.addWidget(self.zoom_label)
        
        parent_layout.addWidget(status_frame)
    
    def connect_signals(self):
        """Connect widget signals."""
        # Update zoom display when image zoom changes
        # Note: In a full implementation, we'd connect to image display zoom change signal
        pass
    
    def load_image(self, image_path: str) -> bool:
        """Load image for viewing.
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if image loaded successfully
        """
        self.current_image_path = image_path
        
        success = self.image_display.load_image(image_path)
        
        if success:
            filename = Path(image_path).name
            self.status_label.setText(f"Loaded: {filename}")
            self.info_btn.setEnabled(True)
            self.update_zoom_controls()
            
            # Automatically fit image to window for maximum space utilization
            self.fit_to_window()
        else:
            self.status_label.setText("Failed to load image")
            self.info_btn.setEnabled(False)
            self.zoom_slider.setValue(100)
            self.zoom_spinbox.setValue(100)
            self.zoom_label.setText("Zoom: --")
        
        # Enable/disable controls based on whether image is loaded
        has_image = self.image_display.has_image()
        self.zoom_out_btn.setEnabled(has_image)
        self.zoom_in_btn.setEnabled(has_image)
        self.zoom_slider.setEnabled(has_image)
        self.zoom_spinbox.setEnabled(has_image)
        self.fit_btn.setEnabled(has_image)
        self.fill_btn.setEnabled(has_image)
        self.actual_size_btn.setEnabled(has_image)
        
        return success
    
    def zoom_in(self):
        """Zoom in the image."""
        self.image_display.zoom_in()
        self.update_zoom_controls()
    
    def zoom_out(self):
        """Zoom out the image."""
        self.image_display.zoom_out()
        self.update_zoom_controls()
    
    def fit_to_window(self):
        """Fit image to window."""
        self.image_display.fit_to_window()
        self.update_zoom_controls()
    
    def fill_window(self):
        """Fill window with image (may crop some parts)."""
        self.image_display.fill_window()
        self.update_zoom_controls()
    
    def actual_size(self):
        """Show image at actual size (100% zoom)."""
        self.image_display.set_zoom(1.0)
        self.update_zoom_controls()
    
    def on_zoom_slider_changed(self, value):
        """Handle zoom slider change."""
        zoom_factor = value / 100.0
        self.image_display.set_zoom(zoom_factor)
        
        # Update spinbox
        self.zoom_spinbox.blockSignals(True)
        self.zoom_spinbox.setValue(value)
        self.zoom_spinbox.blockSignals(False)
        
        self.update_zoom_label()
    
    def on_zoom_spinbox_changed(self, value):
        """Handle zoom spinbox change."""
        zoom_factor = value / 100.0
        self.image_display.set_zoom(zoom_factor)
        
        # Update slider
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(value)
        self.zoom_slider.blockSignals(False)
        
        self.update_zoom_label()
    
    def update_zoom_controls(self):
        """Update zoom controls to match current zoom."""
        if not self.image_display.has_image():
            return
        
        zoom_percent = int(self.image_display.get_zoom_factor() * 100)
        
        self.zoom_slider.blockSignals(True)
        self.zoom_spinbox.blockSignals(True)
        
        self.zoom_slider.setValue(zoom_percent)
        self.zoom_spinbox.setValue(zoom_percent)
        
        self.zoom_slider.blockSignals(False)
        self.zoom_spinbox.blockSignals(False)
        
        self.update_zoom_label()
    
    def update_zoom_label(self):
        """Update zoom label in status bar."""
        if self.image_display.has_image():
            zoom_percent = int(self.image_display.get_zoom_factor() * 100)
            self.zoom_label.setText(f"Zoom: {zoom_percent}%")
        else:
            self.zoom_label.setText("Zoom: --")
    
    def show_image_info(self):
        """Show information about current image."""
        if not self.current_image_path or not os.path.exists(self.current_image_path):
            return
        
        # Get file info
        file_path = Path(self.current_image_path)
        file_size = file_path.stat().st_size
        
        info_text = (
            f"Image Information:\n\n"
            f"File: {file_path.name}\n"
            f"Path: {file_path.parent}\n"
            f"Size: {file_size / (1024*1024):.1f} MB\n"
            f"Type: {file_path.suffix.upper()}"
        )
        
        if self.image_display.has_image() and self.image_display.original_pixmap:
            pixmap = self.image_display.original_pixmap
            info_text += (
                f"\n\nImage Dimensions:\n"
                f"Width: {pixmap.width()} pixels\n"
                f"Height: {pixmap.height()} pixels\n"
                f"Current Zoom: {int(self.image_display.get_zoom_factor() * 100)}%"
            )
        
        QMessageBox.information(self, "Image Information", info_text)
