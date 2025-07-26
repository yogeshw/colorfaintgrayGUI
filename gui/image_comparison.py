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


from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QPushButton, QComboBox, QCheckBox, QSplitter,
    QGroupBox, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont


class ComparisonImageWidget(QFrame):
    """Widget for displaying a single image in comparison view."""
    
    selected = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(2)
        self.is_selected = False
        self.image_path = None
        self.cache_entry = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(300, 200)
        self.image_label.setStyleSheet("border: 1px solid gray;")
        self.image_label.setScaledContents(True)
        layout.addWidget(self.image_label)
        
        # Info panel
        info_widget = QGroupBox("Image Information")
        info_layout = QVBoxLayout(info_widget)
        
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(100)
        self.info_text.setReadOnly(True)
        self.info_text.setFont(QFont("monospace", 8))
        info_layout.addWidget(self.info_text)
        
        layout.addWidget(info_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.select_checkbox = QCheckBox("Select for comparison")
        self.select_checkbox.toggled.connect(self.on_select_toggled)
        controls_layout.addWidget(self.select_checkbox)
        
        controls_layout.addStretch()
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_from_comparison)
        controls_layout.addWidget(self.remove_button)
        
        layout.addLayout(controls_layout)
        
    def load_image(self, image_path, cache_entry=None):
        """Load an image for comparison."""
        self.image_path = image_path
        self.cache_entry = cache_entry
        
        try:
            # Load and scale image
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Scale to fit while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.image_label.setText("Failed to load image")
                
            # Update info
            self.update_info()
            
        except Exception as e:
            self.image_label.setText(f"Error loading image: {e}")
            
    def update_info(self):
        """Update image information display."""
        if not self.cache_entry:
            self.info_text.setPlainText("No information available")
            return
            
        info = f"Created: {self.cache_entry.timestamp}\\n"
        info += f"Parameters:\\n"
        
        # Show key parameters
        key_params = ['qbright', 'stretch', 'gamma', 'colorval', 'grayval']
        for param in key_params:
            value = self.cache_entry.parameters.get(param)
            if value is not None:
                info += f"  {param}: {value}\\n"
                
        self.info_text.setPlainText(info)
        
    def on_select_toggled(self, checked):
        """Handle selection toggle."""
        self.is_selected = checked
        if checked:
            self.setStyleSheet("QFrame { border: 2px solid blue; }")
            self.selected.emit()
        else:
            self.setStyleSheet("QFrame { border: 1px solid gray; }")
            
    def remove_from_comparison(self):
        """Remove this image from comparison."""
        self.parent().remove_comparison_image(self)
        
    def set_selected(self, selected):
        """Set selection state."""
        self.select_checkbox.setChecked(selected)


class ImageComparisonWidget(QWidget):
    """Widget for comparing multiple images side by side."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.comparison_images = []
        self.max_images = 4
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Title and controls
        header_layout = QHBoxLayout()
        
        title = QLabel("Image Comparison")
        title.setFont(QFont("", 12, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Comparison mode
        self.sync_zoom_checkbox = QCheckBox("Sync Zoom/Pan")
        self.sync_zoom_checkbox.setChecked(True)
        header_layout.addWidget(self.sync_zoom_checkbox)
        
        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self.clear_all_images)
        header_layout.addWidget(clear_button)
        
        layout.addLayout(header_layout)
        
        # Scroll area for images
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Images container
        self.images_widget = QWidget()
        self.images_layout = QHBoxLayout(self.images_widget)
        scroll_area.setWidget(self.images_widget)
        
        layout.addWidget(scroll_area)
        
        # Comparison tools
        tools_widget = self.setup_comparison_tools()
        layout.addWidget(tools_widget)
        
    def setup_comparison_tools(self):
        """Set up comparison analysis tools."""
        tools_widget = QGroupBox("Comparison Tools")
        layout = QVBoxLayout(tools_widget)
        
        # Parameter difference analysis
        diff_layout = QHBoxLayout()
        
        diff_layout.addWidget(QLabel("Parameter Differences:"))
        
        self.show_diff_button = QPushButton("Show Differences")
        self.show_diff_button.clicked.connect(self.show_parameter_differences)
        self.show_diff_button.setEnabled(False)
        diff_layout.addWidget(self.show_diff_button)
        
        self.export_comparison_button = QPushButton("Export Comparison")
        self.export_comparison_button.clicked.connect(self.export_comparison)
        self.export_comparison_button.setEnabled(False)
        diff_layout.addWidget(self.export_comparison_button)
        
        diff_layout.addStretch()
        layout.addLayout(diff_layout)
        
        # Difference display
        self.diff_text = QTextEdit()
        self.diff_text.setMaximumHeight(80)
        self.diff_text.setReadOnly(True)
        self.diff_text.setFont(QFont("monospace", 9))
        layout.addWidget(self.diff_text)
        
        return tools_widget
        
    def add_image_for_comparison(self, image_path, cache_entry=None):
        """Add an image to the comparison view."""
        if len(self.comparison_images) >= self.max_images:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, "Comparison Limit",
                f"Maximum {self.max_images} images can be compared at once."
            )
            return False
            
        # Create comparison widget
        comp_widget = ComparisonImageWidget(self)
        comp_widget.load_image(image_path, cache_entry)
        comp_widget.selected.connect(self.on_image_selected)
        
        self.comparison_images.append(comp_widget)
        self.images_layout.addWidget(comp_widget)
        
        self.update_comparison_tools()
        return True
        
    def remove_comparison_image(self, comp_widget):
        """Remove an image from comparison."""
        if comp_widget in self.comparison_images:
            self.comparison_images.remove(comp_widget)
            self.images_layout.removeWidget(comp_widget)
            comp_widget.deleteLater()
            
        self.update_comparison_tools()
        
    def clear_all_images(self):
        """Clear all comparison images."""
        for widget in self.comparison_images:
            self.images_layout.removeWidget(widget)
            widget.deleteLater()
            
        self.comparison_images.clear()
        self.update_comparison_tools()
        
    def on_image_selected(self):
        """Handle image selection."""
        # Update button states based on selections
        selected_count = sum(1 for img in self.comparison_images if img.is_selected)
        self.show_diff_button.setEnabled(selected_count >= 2)
        
    def update_comparison_tools(self):
        """Update comparison tool availability."""
        has_images = len(self.comparison_images) > 0
        has_multiple = len(self.comparison_images) > 1
        
        self.export_comparison_button.setEnabled(has_images)
        self.show_diff_button.setEnabled(has_multiple)
        
        if not has_multiple:
            self.diff_text.clear()
            
    def show_parameter_differences(self):
        """Show parameter differences between selected images."""
        selected_images = [img for img in self.comparison_images if img.is_selected]
        
        if len(selected_images) < 2:
            self.diff_text.setPlainText("Select at least 2 images to compare parameters.")
            return
            
        # Compare parameters
        diff_text = "Parameter Differences:\\n"
        diff_text += "=" * 50 + "\\n"
        
        # Get all parameter keys
        all_params = set()
        for img in selected_images:
            if img.cache_entry:
                all_params.update(img.cache_entry.parameters.keys())
                
        # Compare each parameter
        for param in sorted(all_params):
            values = []
            for i, img in enumerate(selected_images):
                if img.cache_entry:
                    value = img.cache_entry.parameters.get(param, "N/A")
                    values.append(f"Image {i+1}: {value}")
                else:
                    values.append(f"Image {i+1}: N/A")
                    
            # Only show if values differ
            unique_values = set(values)
            if len(unique_values) > 1:
                diff_text += f"\\n{param}:\\n"
                for value in values:
                    diff_text += f"  {value}\\n"
                    
        self.diff_text.setPlainText(diff_text)
        
    def export_comparison(self):
        """Export comparison images and data."""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        directory = QFileDialog.getExistingDirectory(
            self, "Export Comparison", ""
        )
        
        if not directory:
            return
            
        try:
            import shutil
            from pathlib import Path
            import json
            
            export_dir = Path(directory)
            
            # Copy images and create comparison data
            comparison_data = {
                'exported_at': str(datetime.now()),
                'images': []
            }
            
            for i, img in enumerate(self.comparison_images):
                if img.image_path and img.cache_entry:
                    # Copy image
                    dest_path = export_dir / f"comparison_{i+1}.pdf"
                    shutil.copy2(img.image_path, dest_path)
                    
                    # Add to data
                    comparison_data['images'].append({
                        'file': dest_path.name,
                        'parameters': img.cache_entry.parameters,
                        'input_files': img.cache_entry.input_files,
                        'timestamp': img.cache_entry.timestamp
                    })
                    
            # Save comparison data
            with open(export_dir / "comparison_data.json", 'w') as f:
                json.dump(comparison_data, f, indent=2)
                
            QMessageBox.information(
                self, "Export Complete",
                f"Comparison exported to: {export_dir}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, "Export Error", 
                f"Failed to export comparison: {e}"
            )
