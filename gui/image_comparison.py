"""
Image comparison widget for comparing different parameter configurations.

This module provides a side-by-side comparison view for generated images
to help users evaluate different parameter combinations.
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
import json
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QPushButton, QComboBox, QCheckBox, QSplitter,
    QGroupBox, QTextEdit, QSlider, QSpinBox, QMessageBox,
    QFileDialog, QToolTip, QMenu, QApplication, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QTimer
from PyQt6.QtGui import QPixmap, QFont, QMouseEvent, QWheelEvent, QCursor


class ComparisonImageWidget(QFrame):
    """Widget for displaying a single image in comparison view."""
    
    selected = pyqtSignal()
    zoom_changed = pyqtSignal(float)  # zoom_factor
    position_changed = pyqtSignal(QPoint)  # pan_position
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(2)
        self.is_selected = False
        self.image_path = None
        self.cache_entry = None
        
        # Zoom and pan state
        self.original_pixmap = None
        self.zoom_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self.last_pan_point = QPoint()
        self.is_panning = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header with title and controls
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("Image")
        self.title_label.setFont(QFont("", 10, QFont.Weight.Bold))
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Zoom controls
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("Zoom:"))
        
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(25)  # 25%
        self.zoom_slider.setMaximum(400) # 400%
        self.zoom_slider.setValue(100)   # 100%
        self.zoom_slider.setMaximumWidth(80)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        zoom_layout.addWidget(self.zoom_slider)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(35)
        zoom_layout.addWidget(self.zoom_label)
        
        header_layout.addLayout(zoom_layout)
        layout.addLayout(header_layout)
        
        # Image display with scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setMinimumSize(300, 200)
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray;")
        self.image_label.mousePressEvent = self.image_mouse_press
        self.image_label.mouseMoveEvent = self.image_mouse_move
        self.image_label.mouseReleaseEvent = self.image_mouse_release
        self.image_label.wheelEvent = self.image_wheel_event
        
        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area, 1)  # Give it most of the space
        
        # Info panel
        info_widget = QGroupBox("Details")
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(5, 5, 5, 5)
        
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(120)
        self.info_text.setReadOnly(True)
        self.info_text.setFont(QFont("monospace", 8))
        info_layout.addWidget(self.info_text)
        
        layout.addWidget(info_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.select_checkbox = QCheckBox("Select")
        self.select_checkbox.toggled.connect(self.on_select_toggled)
        controls_layout.addWidget(self.select_checkbox)
        
        # Quick action buttons
        self.fit_button = QPushButton("Fit")
        self.fit_button.setMaximumWidth(40)
        self.fit_button.clicked.connect(self.fit_to_view)
        controls_layout.addWidget(self.fit_button)
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.setMaximumWidth(50)
        self.reset_button.clicked.connect(self.reset_view)
        controls_layout.addWidget(self.reset_button)
        
        controls_layout.addStretch()
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.setMaximumWidth(60)
        self.remove_button.clicked.connect(self.remove_from_comparison)
        controls_layout.addWidget(self.remove_button)
        
        layout.addLayout(controls_layout)
        
    def load_image(self, image_path, cache_entry=None):
        """Load an image for comparison."""
        self.image_path = image_path
        self.cache_entry = cache_entry
        
        # Debug print
        print(f"Loading image for comparison: {image_path}")
        print(f"File exists: {os.path.exists(image_path) if image_path else 'No path'}")
        
        try:
            # Check if it's a PDF file
            if image_path and image_path.lower().endswith('.pdf'):
                self.image_label.setText(f"PDF Image\n{Path(image_path).name}\n\n(PDF preview not implemented)")
                # Update info even for PDFs
                self.update_info()
                return
                
            # Load original pixmap
            self.original_pixmap = QPixmap(image_path)
            if not self.original_pixmap.isNull():
                # Set title
                filename = Path(image_path).name
                self.title_label.setText(filename[:20] + "..." if len(filename) > 20 else filename)
                
                # Initial display
                self.update_image_display()
            else:
                self.image_label.setText(f"Failed to load image\n{Path(image_path).name if image_path else 'No path'}")
                
            # Update info
            self.update_info()
            
        except Exception as e:
            self.image_label.setText(f"Error loading image: {e}")
            print(f"Error loading image for comparison: {e}")
    
    def update_image_display(self):
        """Update the image display with current zoom and pan."""
        if not self.original_pixmap:
            return
            
        # Calculate scaled size
        scaled_size = self.original_pixmap.size()
        scaled_size.setWidth(int(scaled_size.width() * self.zoom_factor))
        scaled_size.setHeight(int(scaled_size.height() * self.zoom_factor))
        
        # Create scaled pixmap
        scaled_pixmap = self.original_pixmap.scaled(
            scaled_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Resize label to match scaled image
        self.image_label.resize(scaled_size)
        self.image_label.setPixmap(scaled_pixmap)
        
        # Update zoom label
        self.zoom_label.setText(f"{int(self.zoom_factor * 100)}%")
            
    def update_info(self):
        """Update image information display."""
        if not self.cache_entry:
            info = "No detailed information available"
            if self.image_path:
                file_size = os.path.getsize(self.image_path) / (1024 * 1024)  # MB
                info += f"\nFile size: {file_size:.1f} MB"
        else:
            info = f"Created: {self.cache_entry.timestamp}\n"
            info += f"Input files: {len(self.cache_entry.input_files)} images\n\n"
            
            # Show key parameters
            key_params = ['qbright', 'stretch', 'contrast', 'gamma', 'colorval', 'grayval', 'qthresh']
            info += "Key Parameters:\n"
            for param in key_params:
                value = self.cache_entry.parameters.get(param)
                if value is not None:
                    info += f"  {param}: {value}\n"
                    
        self.info_text.setPlainText(info)
    
    def on_zoom_changed(self, value):
        """Handle zoom slider change."""
        self.zoom_factor = value / 100.0
        self.update_image_display()
        self.zoom_changed.emit(self.zoom_factor)
    
    def set_zoom(self, zoom_factor):
        """Set zoom factor from external source."""
        self.zoom_factor = zoom_factor
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(int(zoom_factor * 100))
        self.zoom_slider.blockSignals(False)
        self.update_image_display()
    
    def fit_to_view(self):
        """Fit image to the available view area."""
        if not self.original_pixmap:
            return
            
        # Get available size
        available_size = self.scroll_area.viewport().size()
        image_size = self.original_pixmap.size()
        
        # Calculate scale to fit
        scale_x = available_size.width() / image_size.width()
        scale_y = available_size.height() / image_size.height()
        scale = min(scale_x, scale_y, 1.0)  # Don't zoom beyond 100%
        
        self.set_zoom(scale)
    
    def reset_view(self):
        """Reset zoom and pan to defaults."""
        self.set_zoom(1.0)
        self.pan_offset = QPoint(0, 0)
        
    # Mouse event handlers for pan functionality
    def image_mouse_press(self, event: QMouseEvent):
        """Handle mouse press on image."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_panning = True
            self.last_pan_point = event.pos()
            self.image_label.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
    
    def image_mouse_move(self, event: QMouseEvent):
        """Handle mouse move on image."""
        if self.is_panning:
            # Calculate pan delta
            delta = event.pos() - self.last_pan_point
            self.last_pan_point = event.pos()
            
            # Update scroll bars
            h_bar = self.scroll_area.horizontalScrollBar()
            v_bar = self.scroll_area.verticalScrollBar()
            
            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())
            
            # Emit position change for sync
            self.position_changed.emit(QPoint(h_bar.value(), v_bar.value()))
    
    def image_mouse_release(self, event: QMouseEvent):
        """Handle mouse release on image."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_panning = False
            self.image_label.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
    
    def image_wheel_event(self, event: QWheelEvent):
        """Handle mouse wheel for zooming."""
        if not self.original_pixmap:
            return
            
        # Get wheel delta
        delta = event.angleDelta().y()
        
        # Calculate new zoom
        zoom_change = 1.1 if delta > 0 else 1/1.1
        new_zoom = max(0.25, min(4.0, self.zoom_factor * zoom_change))
        
        self.set_zoom(new_zoom)
        
    def sync_view(self, zoom_factor, position):
        """Sync view with another image widget."""
        # Set zoom without emitting signal
        self.zoom_factor = zoom_factor
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(int(zoom_factor * 100))
        self.zoom_slider.blockSignals(False)
        self.update_image_display()
        
        # Set scroll position
        self.scroll_area.horizontalScrollBar().setValue(position.x())
        self.scroll_area.verticalScrollBar().setValue(position.y())
        
    def on_select_toggled(self, checked):
        """Handle selection toggle."""
        self.is_selected = checked
        if checked:
            self.setStyleSheet("QFrame { border: 3px solid #2196F3; background-color: #E3F2FD; }")
            self.selected.emit()
        else:
            self.setStyleSheet("QFrame { border: 2px solid #CCCCCC; }")
            
    def remove_from_comparison(self):
        """Remove this image from comparison."""
        parent_widget = self.parent()
        while parent_widget and not hasattr(parent_widget, 'remove_comparison_image'):
            parent_widget = parent_widget.parent()
        if parent_widget:
            parent_widget.remove_comparison_image(self)
        
    def set_selected(self, selected):
        """Set selection state."""
        self.select_checkbox.setChecked(selected)


class ImageComparisonWidget(QWidget):
    """Widget for comparing multiple images side by side."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.comparison_images = []
        self.max_images = 6  # Increased from 4
        self.sync_enabled = True
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title and controls
        header_layout = QHBoxLayout()
        
        title = QLabel("Image Comparison")
        title.setFont(QFont("", 14, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # View controls
        view_controls = QHBoxLayout()
        
        # Layout options
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["Grid (2x3)", "Horizontal", "Vertical"])
        self.layout_combo.currentTextChanged.connect(self.change_layout)
        view_controls.addWidget(QLabel("Layout:"))
        view_controls.addWidget(self.layout_combo)
        
        # Sync controls
        self.sync_zoom_checkbox = QCheckBox("Sync Zoom")
        self.sync_zoom_checkbox.setChecked(True)
        self.sync_zoom_checkbox.toggled.connect(self.toggle_sync)
        view_controls.addWidget(self.sync_zoom_checkbox)
        
        self.sync_pan_checkbox = QCheckBox("Sync Pan")
        self.sync_pan_checkbox.setChecked(True)
        view_controls.addWidget(self.sync_pan_checkbox)
        
        # Global zoom controls
        view_controls.addWidget(QLabel("All:"))
        
        fit_all_btn = QPushButton("Fit All")
        fit_all_btn.clicked.connect(self.fit_all_images)
        view_controls.addWidget(fit_all_btn)
        
        reset_all_btn = QPushButton("Reset All")
        reset_all_btn.clicked.connect(self.reset_all_views)
        view_controls.addWidget(reset_all_btn)
        
        # Action buttons
        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self.clear_all_images)
        view_controls.addWidget(clear_button)
        
        header_layout.addLayout(view_controls)
        layout.addLayout(header_layout)
        
        # Images container with splitter for flexible layout
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Scroll area for images
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Images container widget
        self.images_widget = QWidget()
        self.images_layout = QGridLayout(self.images_widget)  # Default grid to match combo
        self.scroll_area.setWidget(self.images_widget)
        
        self.main_splitter.addWidget(self.scroll_area)
        
        # Analysis panel (initially hidden)
        self.analysis_panel = self.create_analysis_panel()
        self.analysis_panel.setVisible(False)
        self.main_splitter.addWidget(self.analysis_panel)
        
        layout.addWidget(self.main_splitter, 1)
        
        # Comparison tools at bottom
        tools_widget = self.setup_comparison_tools()
        layout.addWidget(tools_widget)
    
    def create_analysis_panel(self):
        """Create the analysis panel."""
        panel = QGroupBox("Analysis")
        layout = QVBoxLayout(panel)
        
        # Parameter comparison table
        self.param_comparison = QTextEdit()
        self.param_comparison.setFont(QFont("monospace", 9))
        self.param_comparison.setReadOnly(True)
        layout.addWidget(self.param_comparison)
        
        # Quick stats
        self.stats_label = QLabel()
        self.stats_label.setFont(QFont("", 9))
        layout.addWidget(self.stats_label)
        
        return panel
        
    def setup_comparison_tools(self):
        """Set up comparison analysis tools."""
        tools_widget = QGroupBox("Comparison Tools")
        layout = QVBoxLayout(tools_widget)
        
        # Tool buttons row
        button_layout = QHBoxLayout()
        
        # Selection tools
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all_images)
        self.select_all_button.setEnabled(False)
        button_layout.addWidget(self.select_all_button)
        
        self.deselect_all_button = QPushButton("Deselect All")
        self.deselect_all_button.clicked.connect(self.deselect_all_images)
        self.deselect_all_button.setEnabled(False)
        button_layout.addWidget(self.deselect_all_button)
        
        button_layout.addWidget(QLabel("|"))  # Separator
        
        # Analysis tools
        self.show_diff_button = QPushButton("Show Differences")
        self.show_diff_button.clicked.connect(self.show_parameter_differences)
        self.show_diff_button.setEnabled(False)
        button_layout.addWidget(self.show_diff_button)
        
        self.show_analysis_button = QPushButton("Toggle Analysis")
        self.show_analysis_button.clicked.connect(self.toggle_analysis_panel)
        self.show_analysis_button.setEnabled(False)
        button_layout.addWidget(self.show_analysis_button)
        
        button_layout.addWidget(QLabel("|"))  # Separator
        
        # Export tools
        self.export_selected_button = QPushButton("Export Selected")
        self.export_selected_button.clicked.connect(self.export_selected_images)
        self.export_selected_button.setEnabled(False)
        button_layout.addWidget(self.export_selected_button)
        
        self.export_comparison_button = QPushButton("Export All")
        self.export_comparison_button.clicked.connect(self.export_comparison)
        self.export_comparison_button.setEnabled(False)
        button_layout.addWidget(self.export_comparison_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Status and info
        status_layout = QHBoxLayout()
        self.status_label = QLabel("No images loaded")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.selection_label = QLabel("Selected: 0")
        status_layout.addWidget(self.selection_label)
        
        layout.addLayout(status_layout)
        
        # Difference display (collapsible)
        self.diff_text = QTextEdit()
        self.diff_text.setMaximumHeight(100)
        self.diff_text.setReadOnly(True)
        self.diff_text.setFont(QFont("monospace", 9))
        self.diff_text.setVisible(False)
        layout.addWidget(self.diff_text)
        
        return tools_widget
    
    def change_layout(self, layout_type):
        """Change the layout of comparison images."""
        if not self.comparison_images:
            return
        
        # Keep a stable list of widgets to re-add
        widgets = list(self.comparison_images)

        # Detach widgets from current layout without nuking parents
        if self.images_layout is not None:
            while self.images_layout.count():
                item = self.images_layout.takeAt(0)
                # Do not change the widget's parent; removing from layout is enough
                # QWidget will be re-inserted into the new layout below
                _ = item.widget()

            # Delete the old layout safely
            try:
                self.images_layout.deleteLater()
            except Exception:
                pass

        # Create new layout based on type (no parent here)
        if layout_type == "Horizontal":
            new_layout = QHBoxLayout()
        elif layout_type == "Vertical":
            new_layout = QVBoxLayout()
        else:  # Grid
            new_layout = QGridLayout()

        # Install the new layout on the container
        self.images_widget.setLayout(new_layout)
        self.images_layout = new_layout

        # Re-add all widgets according to the chosen layout
        if layout_type == "Grid (2x3)":
            for i, widget in enumerate(widgets):
                row = i // 3
                col = i % 3
                self.images_layout.addWidget(widget, row, col)
        else:
            for widget in widgets:
                self.images_layout.addWidget(widget)
    
    def toggle_sync(self, enabled):
        """Toggle synchronization of zoom and pan."""
        self.sync_enabled = enabled
    
    def fit_all_images(self):
        """Fit all images to their view areas."""
        for img_widget in self.comparison_images:
            img_widget.fit_to_view()
    
    def reset_all_views(self):
        """Reset all image views."""
        for img_widget in self.comparison_images:
            img_widget.reset_view()
    
    def select_all_images(self):
        """Select all images."""
        for img_widget in self.comparison_images:
            img_widget.set_selected(True)
    
    def deselect_all_images(self):
        """Deselect all images."""
        for img_widget in self.comparison_images:
            img_widget.set_selected(False)
    
    def toggle_analysis_panel(self):
        """Toggle the analysis panel visibility."""
        visible = self.analysis_panel.isVisible()
        self.analysis_panel.setVisible(not visible)
        
        if not visible:
            self.update_analysis()
            
    def update_analysis(self):
        """Update the analysis panel with current comparison data."""
        if not self.comparison_images:
            return
            
        # Parameter comparison table
        analysis_text = "PARAMETER COMPARISON\n"
        analysis_text += "=" * 50 + "\n\n"
        
        # Get all unique parameters
        all_params = set()
        for img in self.comparison_images:
            if img.cache_entry:
                all_params.update(img.cache_entry.parameters.keys())
        
        # Create comparison table
        important_params = ['qbright', 'stretch', 'contrast', 'gamma', 'colorval', 'grayval', 'qthresh']
        
        for param_group in [important_params, sorted(all_params - set(important_params))]:
            if not param_group:
                continue
                
            if param_group == important_params:
                analysis_text += "Key Parameters:\n"
            else:
                analysis_text += "\nOther Parameters:\n"
                
            analysis_text += "-" * 30 + "\n"
            
            for param in param_group:
                if param not in all_params:
                    continue
                    
                values = []
                for i, img in enumerate(self.comparison_images):
                    if img.cache_entry:
                        value = img.cache_entry.parameters.get(param, "default")
                        values.append(f"Img{i+1}: {value}")
                    else:
                        values.append(f"Img{i+1}: N/A")
                
                # Only show if values differ or it's an important parameter
                unique_values = set(v.split(": ", 1)[1] for v in values)
                if len(unique_values) > 1 or param in important_params:
                    analysis_text += f"{param}:\n"
                    for value in values:
                        analysis_text += f"  {value}\n"
                    analysis_text += "\n"
        
        self.param_comparison.setPlainText(analysis_text)
        
        # Update stats
        stats = f"Images: {len(self.comparison_images)}"
        selected_count = sum(1 for img in self.comparison_images if img.is_selected)
        stats += f" | Selected: {selected_count}"
        self.stats_label.setText(stats)
        
    def add_image_for_comparison(self, image_path, cache_entry=None):
        """Add an image to the comparison view."""
        if len(self.comparison_images) >= self.max_images:
            QMessageBox.warning(
                self, "Comparison Limit",
                f"Maximum {self.max_images} images can be compared at once."
            )
            return False
            
        # Create comparison widget
        comp_widget = ComparisonImageWidget(self)
        comp_widget.load_image(image_path, cache_entry)
        comp_widget.selected.connect(self.on_image_selected)
        
        # Connect sync signals if enabled
        if self.sync_enabled:
            comp_widget.zoom_changed.connect(self.sync_zoom_to_others)
            comp_widget.position_changed.connect(self.sync_position_to_others)
        
        self.comparison_images.append(comp_widget)
        
        # Add to current layout
        current_layout = self.layout_combo.currentText()
        if current_layout == "Grid (2x3)":
            row = (len(self.comparison_images) - 1) // 3
            col = (len(self.comparison_images) - 1) % 3
            self.images_layout.addWidget(comp_widget, row, col)
        else:
            self.images_layout.addWidget(comp_widget)
        
        self.update_comparison_tools()
        return True
    
    def sync_zoom_to_others(self, zoom_factor):
        """Sync zoom to other images."""
        if not self.sync_zoom_checkbox.isChecked():
            return
            
        sender = self.sender()
        for img_widget in self.comparison_images:
            if img_widget != sender:
                img_widget.set_zoom(zoom_factor)
    
    def sync_position_to_others(self, position):
        """Sync pan position to other images."""
        if not self.sync_pan_checkbox.isChecked():
            return
            
        sender = self.sender()
        for img_widget in self.comparison_images:
            if img_widget != sender:
                # Set scroll position without triggering signals
                img_widget.scroll_area.horizontalScrollBar().setValue(position.x())
                img_widget.scroll_area.verticalScrollBar().setValue(position.y())
        
    def remove_comparison_image(self, comp_widget):
        """Remove an image from comparison."""
        if comp_widget in self.comparison_images:
            self.comparison_images.remove(comp_widget)
            # Safely remove from layout
            try:
                self.images_layout.removeWidget(comp_widget)
            except Exception:
                pass
            # Hide before deletion to avoid any paint events
            comp_widget.setParent(None)
            comp_widget.deleteLater()
            
            # Re-arrange remaining widgets if using grid layout
            if self.layout_combo.currentText() == "Grid (2x3)":
                self.change_layout("Grid (2x3)")
            
        self.update_comparison_tools()
        
    def clear_all_images(self):
        """Clear all comparison images."""
        reply = QMessageBox.question(
            self, "Clear All Images",
            "Are you sure you want to remove all images from comparison?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Detach and delete widgets safely
            for widget in self.comparison_images:
                try:
                    self.images_layout.removeWidget(widget)
                except Exception:
                    pass
                widget.setParent(None)
                widget.deleteLater()

            # Reset list
            self.comparison_images.clear()

            # Also clear any items left in the layout
            try:
                while self.images_layout.count():
                    item = self.images_layout.takeAt(0)
                    w = item.widget()
                    if w is not None:
                        w.setParent(None)
                        w.deleteLater()
            except Exception:
                pass

            # Update UI state
            self.update_comparison_tools()
        
    def on_image_selected(self):
        """Handle image selection changes."""
        selected_count = sum(1 for img in self.comparison_images if img.is_selected)
        self.selection_label.setText(f"Selected: {selected_count}")
        
        # Update button states
        self.show_diff_button.setEnabled(selected_count >= 2)
        self.export_selected_button.setEnabled(selected_count > 0)
        
        # Update analysis if panel is visible
        if self.analysis_panel.isVisible():
            self.update_analysis()
        
    def update_comparison_tools(self):
        """Update comparison tool availability."""
        has_images = len(self.comparison_images) > 0
        has_multiple = len(self.comparison_images) > 1
        
        # Update status
        if has_images:
            self.status_label.setText(f"Loaded: {len(self.comparison_images)} images")
        else:
            self.status_label.setText("No images loaded")
            
        # Update button states
        self.select_all_button.setEnabled(has_images)
        self.deselect_all_button.setEnabled(has_images)
        self.show_analysis_button.setEnabled(has_images)
        self.export_comparison_button.setEnabled(has_images)
        
        selected_count = sum(1 for img in self.comparison_images if img.is_selected)
        self.selection_label.setText(f"Selected: {selected_count}")
        self.show_diff_button.setEnabled(selected_count >= 2)
        self.export_selected_button.setEnabled(selected_count > 0)
        
        # Clear difference display if not enough images
        if not has_multiple:
            self.diff_text.clear()
            self.diff_text.setVisible(False)
            
    def show_parameter_differences(self):
        """Show parameter differences between selected images."""
        selected_images = [img for img in self.comparison_images if img.is_selected]
        
        if len(selected_images) < 2:
            self.diff_text.setPlainText("Select at least 2 images to compare parameters.")
            self.diff_text.setVisible(True)
            return
            
        # Compare parameters
        diff_text = f"PARAMETER DIFFERENCES ({len(selected_images)} images)\n"
        diff_text += "=" * 60 + "\n\n"
        
        # Get all parameter keys from selected images
        all_params = set()
        for img in selected_images:
            if img.cache_entry:
                all_params.update(img.cache_entry.parameters.keys())
                
        if not all_params:
            diff_text += "No parameter information available for comparison."
        else:
            # Group parameters by importance
            important_params = ['qbright', 'stretch', 'contrast', 'gamma', 'colorval', 'grayval', 'qthresh']
            other_params = sorted(all_params - set(important_params))
            
            for param_group, title in [(important_params, "Key Parameters"), (other_params, "Other Parameters")]:
                if not param_group:
                    continue
                    
                diff_text += f"{title}:\n"
                diff_text += "-" * len(title) + "\n"
                
                differences_found = False
                for param in param_group:
                    if param not in all_params:
                        continue
                        
                    values = []
                    for i, img in enumerate(selected_images):
                        if img.cache_entry and param in img.cache_entry.parameters:
                            value = img.cache_entry.parameters[param]
                            values.append(f"Image {i+1}: {value}")
                        else:
                            values.append(f"Image {i+1}: default")
                    
                    # Only show if values actually differ
                    unique_values = set(v.split(": ", 1)[1] for v in values)
                    if len(unique_values) > 1:
                        diff_text += f"\n{param}:\n"
                        for value in values:
                            diff_text += f"  {value}\n"
                        differences_found = True
                
                if not differences_found and param_group == important_params:
                    diff_text += "  All key parameters are identical\n"
                
                diff_text += "\n"
        
        self.diff_text.setPlainText(diff_text)
        self.diff_text.setVisible(True)
    
    def export_selected_images(self):
        """Export only the selected images."""
        selected_images = [img for img in self.comparison_images if img.is_selected]
        
        if not selected_images:
            QMessageBox.warning(self, "No Selection", "Please select images to export.")
            return
            
        self._export_images(selected_images, "selected")
    
    def export_comparison(self):
        """Export all comparison images and data."""
        if not self.comparison_images:
            QMessageBox.warning(self, "No Images", "No images to export.")
            return
            
        self._export_images(self.comparison_images, "all")
    
    def _export_images(self, images_to_export, export_type):
        """Internal method to export images."""
        directory = QFileDialog.getExistingDirectory(
            self, f"Export {export_type.title()} Images", ""
        )
        
        if not directory:
            return
            
        try:
            import shutil
            export_dir = Path(directory)
            
            # Create comparison data structure
            comparison_data = {
                'exported_at': datetime.now().isoformat(),
                'export_type': export_type,
                'total_images': len(images_to_export),
                'images': []
            }
            
            # Process each image
            for i, img in enumerate(images_to_export):
                if img.image_path:
                    # Determine file extension
                    original_ext = Path(img.image_path).suffix
                    dest_filename = f"comparison_{export_type}_{i+1}{original_ext}"
                    dest_path = export_dir / dest_filename
                    
                    # Copy image file
                    shutil.copy2(img.image_path, dest_path)
                    
                    # Collect metadata
                    image_data = {
                        'file': dest_filename,
                        'original_path': str(img.image_path),
                        'index': i + 1
                    }
                    
                    if img.cache_entry:
                        image_data.update({
                            'parameters': img.cache_entry.parameters,
                            'input_files': getattr(img.cache_entry, 'input_files', {}),
                            'timestamp': img.cache_entry.timestamp,
                            'creation_time': getattr(img.cache_entry, 'creation_time', None)
                        })
                    
                    comparison_data['images'].append(image_data)
            
            # Save comparison metadata
            metadata_file = export_dir / f"comparison_{export_type}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(comparison_data, f, indent=2, default=str)
            
            # Create a readable summary
            summary_file = export_dir / f"comparison_{export_type}_summary.txt"
            with open(summary_file, 'w') as f:
                f.write(f"Image Comparison Export Summary\n")
                f.write(f"{'='*40}\n\n")
                f.write(f"Export Date: {comparison_data['exported_at']}\n")
                f.write(f"Export Type: {export_type.title()}\n")
                f.write(f"Number of Images: {len(images_to_export)}\n\n")
                
                for i, img_data in enumerate(comparison_data['images']):
                    f.write(f"Image {i+1}: {img_data['file']}\n")
                    if 'parameters' in img_data:
                        f.write("  Key Parameters:\n")
                        key_params = ['qbright', 'stretch', 'contrast', 'gamma', 'colorval', 'grayval']
                        for param in key_params:
                            value = img_data['parameters'].get(param, 'default')
                            f.write(f"    {param}: {value}\n")
                    f.write("\n")
            
            QMessageBox.information(
                self, "Export Complete",
                f"Successfully exported {len(images_to_export)} images to:\n{export_dir}\n\n"
                f"Files created:\n"
                f"• {len(images_to_export)} image files\n"
                f"• 1 metadata file (JSON)\n"
                f"• 1 summary file (TXT)"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, "Export Error", 
                f"Failed to export comparison:\n\n{str(e)}"
            )
