"""
Preset manager for saving and loading parameter configurations.

This module provides functionality to save, load, and manage
parameter presets for quick access to common configurations.
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
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QInputDialog, QMessageBox, QLabel, QTextEdit,
    QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class PresetManager:
    """Manages saving and loading of parameter presets."""
    
    def __init__(self, config_dir: Path):
        self.presets_dir = config_dir / "presets"
        self.presets_dir.mkdir(exist_ok=True)
        
    def save_preset(self, name: str, parameters: Dict, description: str = "") -> bool:
        """Save a parameter preset."""
        try:
            preset_data = {
                'name': name,
                'description': description,
                'created': datetime.now().isoformat(),
                'parameters': parameters
            }
            
            filename = f"{name.replace(' ', '_').lower()}.json"
            filepath = self.presets_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(preset_data, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving preset: {e}")
            return False
            
    def load_preset(self, name: str) -> Optional[Dict]:
        """Load a parameter preset."""
        try:
            filename = f"{name.replace(' ', '_').lower()}.json"
            filepath = self.presets_dir / filename
            
            if not filepath.exists():
                return None
                
            with open(filepath, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"Error loading preset: {e}")
            return None
            
    def list_presets(self) -> List[Dict]:
        """List all available presets."""
        presets = []
        
        for filepath in self.presets_dir.glob("*.json"):
            try:
                with open(filepath, 'r') as f:
                    preset_data = json.load(f)
                    presets.append(preset_data)
            except Exception as e:
                print(f"Error reading preset {filepath}: {e}")
                
        return sorted(presets, key=lambda x: x.get('created', ''))
        
    def delete_preset(self, name: str) -> bool:
        """Delete a preset."""
        try:
            filename = f"{name.replace(' ', '_').lower()}.json"
            filepath = self.presets_dir / filename
            
            if filepath.exists():
                filepath.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting preset: {e}")
            return False


class PresetDialog(QDialog):
    """Dialog for managing presets."""
    
    preset_selected = pyqtSignal(dict)  # Emits preset parameters
    
    def __init__(self, preset_manager: PresetManager, current_parameters: Dict, parent=None):
        super().__init__(parent)
        self.preset_manager = preset_manager
        self.current_parameters = current_parameters
        self.setWindowTitle("Parameter Presets")
        self.resize(600, 400)
        
        self.setup_ui()
        self.refresh_presets()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Splitter for list and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - preset list
        left_widget = self.setup_preset_list()
        splitter.addWidget(left_widget)
        
        # Right side - preset details
        right_widget = self.setup_preset_details()
        splitter.addWidget(right_widget)
        
        splitter.setSizes([300, 300])
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Current")
        self.save_button.clicked.connect(self.save_current_preset)
        button_layout.addWidget(self.save_button)
        
        self.load_button = QPushButton("Load Selected")
        self.load_button.clicked.connect(self.load_selected_preset)
        self.load_button.setEnabled(False)
        button_layout.addWidget(self.load_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_selected_preset)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
    def setup_preset_list(self):
        """Set up the preset list widget."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Saved Presets:"))
        
        self.preset_list = QListWidget()
        self.preset_list.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.preset_list)
        
        return widget
        
    def setup_preset_details(self):
        """Set up the preset details widget."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Preset Details:"))
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setFont(QFont("monospace", 9))
        layout.addWidget(self.details_text)
        
        return widget
        
    def refresh_presets(self):
        """Refresh the preset list."""
        self.preset_list.clear()
        
        presets = self.preset_manager.list_presets()
        for preset in presets:
            item = QListWidgetItem(preset['name'])
            item.setData(Qt.ItemDataRole.UserRole, preset)
            self.preset_list.addItem(item)
            
    def on_selection_changed(self):
        """Handle preset selection change."""
        current = self.preset_list.currentItem()
        has_selection = current is not None
        
        self.load_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        
        if has_selection:
            preset = current.data(Qt.ItemDataRole.UserRole)
            self.show_preset_details(preset)
        else:
            self.details_text.clear()
            
    def show_preset_details(self, preset: Dict):
        """Show details of the selected preset."""
        details = f"Name: {preset['name']}\\n"
        details += f"Created: {preset.get('created', 'Unknown')}\\n"
        details += f"Description: {preset.get('description', 'No description')}\\n\\n"
        details += "Parameters:\\n"
        
        for key, value in preset.get('parameters', {}).items():
            details += f"  {key}: {value}\\n"
            
        self.details_text.setPlainText(details)
        
    def save_current_preset(self):
        """Save current parameters as a new preset."""
        name, ok = QInputDialog.getText(
            self, "Save Preset", "Enter preset name:"
        )
        
        if not ok or not name.strip():
            return
            
        name = name.strip()
        
        # Check if preset exists
        if self.preset_manager.load_preset(name):
            reply = QMessageBox.question(
                self, "Preset Exists",
                f"Preset '{name}' already exists. Overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
                
        description, ok = QInputDialog.getText(
            self, "Preset Description", "Enter description (optional):"
        )
        
        if not ok:
            description = ""
            
        if self.preset_manager.save_preset(name, self.current_parameters, description):
            QMessageBox.information(self, "Success", f"Preset '{name}' saved!")
            self.refresh_presets()
        else:
            QMessageBox.warning(self, "Error", "Failed to save preset.")
            
    def load_selected_preset(self):
        """Load the selected preset."""
        current = self.preset_list.currentItem()
        if not current:
            return
            
        preset = current.data(Qt.ItemDataRole.UserRole)
        parameters = preset.get('parameters', {})
        
        self.preset_selected.emit(parameters)
        QMessageBox.information(self, "Success", f"Preset '{preset['name']}' loaded!")
        
    def delete_selected_preset(self):
        """Delete the selected preset."""
        current = self.preset_list.currentItem()
        if not current:
            return
            
        preset = current.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "Delete Preset",
            f"Delete preset '{preset['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.preset_manager.delete_preset(preset['name']):
                QMessageBox.information(self, "Success", "Preset deleted!")
                self.refresh_presets()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete preset.")
