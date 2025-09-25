"""
Cache grid view widget for displaying cached images as thumbnails.

This module provides the cache grid tab that shows all cached images
in a thumbnail grid with search and sorting capabilities.
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
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QScrollArea, QFrame, QMessageBox, QMenu,
    QSizePolicy, QSpacerItem, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QPixmap, QFont, QAction, QCursor

from core.cache_manager import CacheManager, CacheEntry


class ThumbnailWidget(QFrame):
    """Widget representing a single cached image thumbnail."""
    
    clicked = pyqtSignal(str, object)  # entry_id, entry
    context_menu_requested = pyqtSignal(str, object, object)  # entry_id, entry, position
    
    def __init__(self, entry_id: str, entry: CacheEntry, parent=None):
        """Initialize thumbnail widget.
        
        Args:
            entry_id: Cache entry identifier
            entry: Cache entry data
            parent: Parent widget
        """
        super().__init__(parent)
        self.entry_id = entry_id
        self.entry = entry
        
        self.setup_ui()
        self.setFixedSize(180, 220)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            ThumbnailWidget {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
            ThumbnailWidget:hover {
                border-color: #4CAF50;
                background-color: #f8f8f8;
            }
        """)
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def setup_ui(self):
        """Setup thumbnail UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)
        
        # Thumbnail image area
        self.image_label = QLabel()
        self.image_label.setFixedSize(160, 120)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
        """)
        
        # Load thumbnail or show placeholder
        self.load_thumbnail()
        
        layout.addWidget(self.image_label)
        
        # Entry info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(1)
        
        # Timestamp
        timestamp = datetime.fromisoformat(self.entry.timestamp)
        time_str = timestamp.strftime("%Y-%m-%d %H:%M")
        time_label = QLabel(time_str)
        time_label.setFont(QFont("", 8))
        time_label.setStyleSheet("color: #666;")
        info_layout.addWidget(time_label)
        
        # Parameters summary
        param_summary = self.create_parameter_summary()
        param_label = QLabel(param_summary)
        param_label.setFont(QFont("", 8))
        param_label.setWordWrap(True)
        param_label.setMaximumHeight(40)
        param_label.setStyleSheet("color: #333;")
        info_layout.addWidget(param_label)
        
        # File size
        size_str = self.format_file_size(self.entry.file_size)
        size_label = QLabel(size_str)
        size_label.setFont(QFont("", 7))
        size_label.setStyleSheet("color: #888;")
        info_layout.addWidget(size_label)
        
        layout.addLayout(info_layout)
    
    def load_thumbnail(self):
        """Load thumbnail image or show placeholder."""
        if self.entry.thumbnail_path and os.path.exists(self.entry.thumbnail_path):
            # Load actual thumbnail
            pixmap = QPixmap(self.entry.thumbnail_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    160, 120,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                return
        
        # Show placeholder for PDF or missing thumbnail
        file_type = "PDF" if self.entry.image_path.endswith('.pdf') else "Image"
        placeholder_text = f"{file_type}\nPreview"
        self.image_label.setText(placeholder_text)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #e8e8e8;
                border: 1px solid #ccc;
                border-radius: 3px;
                color: #666;
                font-size: 12px;
            }
        """)
    
    def create_parameter_summary(self) -> str:
        """Create summary of key parameters.
        
        Returns:
            Parameter summary string
        """
        params = self.entry.parameters
        summary_parts = []
        
        # Key parameters
        if 'qbright' in params and params['qbright'] != 1.0:
            summary_parts.append(f"q={params['qbright']:.2f}")
        
        if 'stretch' in params and params['stretch'] != 1.0:
            summary_parts.append(f"s={params['stretch']:.1f}")

        if 'contrast' in params and params['contrast'] not in (None, 4.0):
            summary_parts.append(f"c={params['contrast']:.1f}")
        
        if 'gamma' in params and params['gamma'] != 1.0:
            summary_parts.append(f"γ={params['gamma']:.2f}")
        
        if params.get('coloronly'):
            summary_parts.append("color-only")
        
        if summary_parts:
            return ", ".join(summary_parts)
        else:
            return "Default parameters"
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size for display.
        
        Args:
            size_bytes: File size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB']:
            if size_bytes < 1024.0:
                if unit == 'B':
                    return f"{size_bytes} {unit}"
                else:
                    return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} GB"
    
    def mousePressEvent(self, event):
        """Handle mouse press for selection."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.entry_id, self.entry)
        super().mousePressEvent(event)
    
    def show_context_menu(self, position):
        """Show context menu for thumbnail."""
        self.context_menu_requested.emit(self.entry_id, self.entry, position)


class CacheGridView(QWidget):
    """Grid view for displaying cached image thumbnails."""
    
    image_selected = pyqtSignal(str, object)  # entry_id, entry
    cache_changed = pyqtSignal()  # Cache was modified
    add_to_comparison = pyqtSignal(str, object)  # entry_id, entry
    
    def __init__(self, cache_manager: CacheManager, parent=None):
        """Initialize cache grid view.
        
        Args:
            cache_manager: Cache manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.cache_manager = cache_manager
        
        # Current state
        self.thumbnails = {}  # entry_id -> ThumbnailWidget
        self.current_search = ""
        self.current_sort = "timestamp"
        
        # Update timer for search
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """Setup grid view UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        self.setup_header(layout)
        
        # Grid area
        self.setup_grid_area(layout)
        
        # Footer
        self.setup_footer(layout)
    
    def setup_header(self, parent_layout):
        """Setup header with search and controls."""
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("Cached Images")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Search box
        search_label = QLabel("Search:")
        header_layout.addWidget(search_label)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search parameters, files...")
        self.search_box.setMaximumWidth(200)
        self.search_box.textChanged.connect(self.on_search_changed)
        header_layout.addWidget(self.search_box)
        
        # Sort selector
        sort_label = QLabel("Sort:")
        header_layout.addWidget(sort_label)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Newest First", "Oldest First"])
        self.sort_combo.currentTextChanged.connect(self.on_sort_changed)
        header_layout.addWidget(self.sort_combo)
        
        parent_layout.addLayout(header_layout)
    
    def setup_grid_area(self, parent_layout):
        """Setup scrollable grid area."""
        # Scroll area for thumbnails
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Grid widget
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        self.scroll_area.setWidget(self.grid_widget)
        parent_layout.addWidget(self.scroll_area)
    
    def setup_footer(self, parent_layout):
        """Setup footer with stats and actions."""
        footer_layout = QHBoxLayout()
        
        # Cache stats
        self.stats_label = QLabel()
        self.update_stats_display()
        footer_layout.addWidget(self.stats_label)
        
        footer_layout.addStretch()
        
        # Action buttons
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        footer_layout.addWidget(refresh_btn)
        
        clear_btn = QPushButton("Clear Cache")
        clear_btn.clicked.connect(self.clear_cache)
        footer_layout.addWidget(clear_btn)
        
        export_btn = QPushButton("Export All...")
        export_btn.clicked.connect(self.export_cache)
        footer_layout.addWidget(export_btn)
        
        parent_layout.addLayout(footer_layout)
    
    def refresh(self):
        """Refresh the grid display."""
        # Clear existing thumbnails
        self.clear_grid()
        
        # Get cache entries
        if self.current_search:
            entries = self.cache_manager.search_entries(self.current_search)
        else:
            entries = self.cache_manager.get_all_entries(self.current_sort)
        
        # Create thumbnails
        self.create_thumbnails(entries)
        
        # Update stats
        self.update_stats_display()
    
    def clear_grid(self):
        """Clear all thumbnails from grid."""
        # Remove all thumbnail widgets
        for thumbnail in self.thumbnails.values():
            thumbnail.setParent(None)
            thumbnail.deleteLater()
        
        self.thumbnails.clear()
        
        # Clear grid layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
    
    def create_thumbnails(self, entries: List[Tuple[str, CacheEntry]]):
        """Create thumbnail widgets for entries.
        
        Args:
            entries: List of (entry_id, entry) tuples
        """
        if not entries:
            # Show empty state
            empty_label = QLabel("No cached images found")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #888; font-size: 14px; padding: 50px;")
            self.grid_layout.addWidget(empty_label, 0, 0)
            return
        
        # Calculate grid dimensions
        columns = max(1, self.scroll_area.width() // 200)  # Approximate column count
        
        # Create thumbnail widgets
        for i, (entry_id, entry) in enumerate(entries):
            row = i // columns
            col = i % columns
            
            # Create thumbnail widget
            thumbnail = ThumbnailWidget(entry_id, entry, self)
            thumbnail.clicked.connect(self.on_thumbnail_clicked)
            thumbnail.context_menu_requested.connect(self.on_context_menu_requested)
            
            # Add to grid
            self.grid_layout.addWidget(thumbnail, row, col)
            self.thumbnails[entry_id] = thumbnail
    
    def on_search_changed(self, text):
        """Handle search text change."""
        self.current_search = text.strip()
        # Debounce search to avoid too many updates
        self.search_timer.start(300)
    
    def perform_search(self):
        """Perform the actual search."""
        self.refresh()
    
    def on_sort_changed(self, sort_text):
        """Handle sort option change."""
        if sort_text == "Newest First":
            self.current_sort = "timestamp"
        elif sort_text == "Oldest First":
            self.current_sort = "timestamp_asc"
        
        self.refresh()
    
    def on_thumbnail_clicked(self, entry_id: str, entry: CacheEntry):
        """Handle thumbnail click."""
        self.image_selected.emit(entry_id, entry)
    
    def on_context_menu_requested(self, entry_id: str, entry: CacheEntry, position):
        """Handle context menu request."""
        menu = QMenu(self)
        
        # View action
        view_action = QAction("View Image", self)
        view_action.triggered.connect(lambda: self.image_selected.emit(entry_id, entry))
        menu.addAction(view_action)
        
        menu.addSeparator()
        
        # Add to comparison action
        add_comparison_action = QAction("Add to Comparison", self)
        add_comparison_action.triggered.connect(lambda: self.add_to_comparison.emit(entry_id, entry))
        menu.addAction(add_comparison_action)
        
        # Copy command action
        copy_action = QAction("Copy Command", self)
        copy_action.triggered.connect(lambda: self.copy_command(entry))
        menu.addAction(copy_action)
        
        # Show info action
        info_action = QAction("Show Info", self)
        info_action.triggered.connect(lambda: self.show_entry_info(entry_id, entry))
        menu.addAction(info_action)
        
        menu.addSeparator()
        
        # Delete action
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_entry(entry_id))
        menu.addAction(delete_action)
        
        # Show menu
        thumbnail = self.thumbnails[entry_id]
        global_pos = thumbnail.mapToGlobal(position)
        menu.exec(global_pos)
    
    def copy_command(self, entry: CacheEntry):
        """Copy astscript command to clipboard.
        
        Args:
            entry: Cache entry
        """
        from core.command_builder import CommandBuilder
        
        # Build command
        command_builder = CommandBuilder()
        
        # Prepare parameters
        params = entry.parameters.copy()
        params.update(entry.input_files)
        params['output_path'] = 'output.tif'  # Generic output path
        
        try:
            command_str = command_builder.format_command_string(params)
            
            # Copy to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(command_str)
            
            # Show confirmation (could be a status message instead)
            QMessageBox.information(self, "Command Copied", 
                                   "Command copied to clipboard!")
        except Exception as e:
            QMessageBox.warning(self, "Copy Failed", 
                               f"Failed to copy command:\n{e}")
    
    def show_entry_info(self, entry_id: str, entry: CacheEntry):
        """Show detailed entry information.
        
        Args:
            entry_id: Entry identifier
            entry: Cache entry
        """
        timestamp = datetime.fromisoformat(entry.timestamp)
        
        info_text = (
            f"Cache Entry Information:\n\n"
            f"Entry ID: {entry_id}\n"
            f"Created: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"File Size: {self.format_file_size(entry.file_size)}\n"
            f"Image Path: {entry.image_path}\n\n"
            f"Input Files:\n"
            f"  Red: {entry.input_files.get('red_path', 'N/A')}\n"
            f"  Green: {entry.input_files.get('green_path', 'N/A')}\n"
            f"  Blue: {entry.input_files.get('blue_path', 'N/A')}\n\n"
            f"Parameters:\n"
        )
        
        for key, value in entry.parameters.items():
            info_text += f"  {key}: {value}\n"
        
        QMessageBox.information(self, "Entry Information", info_text)
    
    def delete_entry(self, entry_id: str):
        """Delete cache entry.
        
        Args:
            entry_id: Entry to delete
        """
        reply = QMessageBox.question(
            self,
            "Delete Entry",
            "Are you sure you want to delete this cached image?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.cache_manager.remove_entry(entry_id):
                self.refresh()
                self.cache_changed.emit()
    
    def clear_cache(self):
        """Clear entire cache."""
        if not self.cache_manager.get_all_entries():
            QMessageBox.information(self, "Empty Cache", "Cache is already empty.")
            return
        
        reply = QMessageBox.question(
            self,
            "Clear Cache",
            "Are you sure you want to clear all cached images?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            count = self.cache_manager.clear_cache()
            self.refresh()
            self.cache_changed.emit()
            QMessageBox.information(self, "Cache Cleared", 
                                   f"Deleted {count} cached images.")
    
    def export_cache(self):
        """Export all cached images."""
        from PyQt6.QtWidgets import QFileDialog
        
        if not self.cache_manager.get_all_entries():
            QMessageBox.information(self, "Empty Cache", "No cached images to export.")
            return
        
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Export Directory",
            os.path.expanduser("~")
        )
        
        if directory:
            try:
                exported = self.cache_manager.export_cache(directory)
                QMessageBox.information(
                    self, 
                    "Export Complete", 
                    f"Exported {len(exported)} images to:\n{directory}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", 
                                    f"Failed to export cache:\n{e}")
    
    def update_stats_display(self):
        """Update cache statistics display."""
        stats = self.cache_manager.get_cache_stats()
        self.stats_label.setText(
            f"Cache: {stats['total_entries']}/{stats['max_entries']} images, "
            f"{stats['total_size_mb']:.1f} MB"
        )
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size for display."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                if unit == 'B':
                    return f"{size_bytes} {unit}"
                else:
                    return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
