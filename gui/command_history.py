"""
Command history and clipboard utilities.

This module provides functionality to track command history
and copy commands to the clipboard for easy reuse.
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
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QTextEdit, QLabel, QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QClipboard
from PyQt6.QtWidgets import QApplication


class CommandHistory:
    """Manages command history persistence."""
    
    def __init__(self, config_dir: Path):
        self.history_file = config_dir / "command_history.json"
        self.max_entries = 100
        self._history = self._load_history()
        
    def _load_history(self) -> List[Dict]:
        """Load command history from file."""
        if not self.history_file.exists():
            return []
            
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading command history: {e}")
            return []
            
    def _save_history(self):
        """Save command history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self._history, f, indent=2)
        except Exception as e:
            print(f"Error saving command history: {e}")
            
    def add_command(self, command: str, parameters: Dict, input_files: Dict):
        """Add a command to history."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'parameters': parameters,
            'input_files': input_files
        }
        
        # Add to beginning of list
        self._history.insert(0, entry)
        
        # Trim to max entries
        if len(self._history) > self.max_entries:
            self._history = self._history[:self.max_entries]
            
        self._save_history()
        
    def get_history(self) -> List[Dict]:
        """Get command history."""
        return self._history.copy()
        
    def clear_history(self):
        """Clear command history."""
        self._history = []
        self._save_history()


class CommandHistoryDialog(QDialog):
    """Dialog for viewing and managing command history."""
    
    def __init__(self, command_history: CommandHistory, parent=None):
        super().__init__(parent)
        self.command_history = command_history
        self.setWindowTitle("Command History")
        self.resize(700, 500)
        
        self.setup_ui()
        self.refresh_history()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Splitter for list and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - command list
        left_widget = self.setup_command_list()
        splitter.addWidget(left_widget)
        
        # Right side - command details
        right_widget = self.setup_command_details()
        splitter.addWidget(right_widget)
        
        splitter.setSizes([350, 350])
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.copy_button = QPushButton("Copy Command")
        self.copy_button.clicked.connect(self.copy_selected_command)
        self.copy_button.setEnabled(False)
        button_layout.addWidget(self.copy_button)
        
        self.copy_params_button = QPushButton("Copy Parameters")
        self.copy_params_button.clicked.connect(self.copy_selected_parameters)
        self.copy_params_button.setEnabled(False)
        button_layout.addWidget(self.copy_params_button)
        
        clear_button = QPushButton("Clear History")
        clear_button.clicked.connect(self.clear_history)
        button_layout.addWidget(clear_button)
        
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
    def setup_command_list(self):
        """Set up the command list widget."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Command History:"))
        
        self.command_list = QListWidget()
        self.command_list.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.command_list)
        
        return widget
        
    def setup_command_details(self):
        """Set up the command details widget."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Command Details:"))
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setFont(QFont("monospace", 9))
        layout.addWidget(self.details_text)
        
        return widget
        
    def refresh_history(self):
        """Refresh the command history list."""
        self.command_list.clear()
        
        history = self.command_history.get_history()
        for i, entry in enumerate(history):
            timestamp = entry.get('timestamp', 'Unknown')
            try:
                # Format timestamp
                dt = datetime.fromisoformat(timestamp)
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                formatted_time = timestamp
                
            item_text = f"{formatted_time}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.command_list.addItem(item)
            
    def on_selection_changed(self):
        """Handle command selection change."""
        current = self.command_list.currentItem()
        has_selection = current is not None
        
        self.copy_button.setEnabled(has_selection)
        self.copy_params_button.setEnabled(has_selection)
        
        if has_selection:
            entry = current.data(Qt.ItemDataRole.UserRole)
            self.show_command_details(entry)
        else:
            self.details_text.clear()
            
    def show_command_details(self, entry: Dict):
        """Show details of the selected command."""
        timestamp = entry.get('timestamp', 'Unknown')
        try:
            dt = datetime.fromisoformat(timestamp)
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatted_time = timestamp
            
        details = f"Timestamp: {formatted_time}\\n\\n"
        details += f"Command:\\n{entry.get('command', 'N/A')}\\n\\n"
        
        details += "Input Files:\\n"
        for key, value in entry.get('input_files', {}).items():
            details += f"  {key}: {value}\\n"
            
        details += "\\nParameters:\\n"
        for key, value in entry.get('parameters', {}).items():
            if key not in ['r_channel', 'g_channel', 'b_channel']:  # Skip file paths
                details += f"  {key}: {value}\\n"
            
        self.details_text.setPlainText(details)
        
    def copy_selected_command(self):
        """Copy selected command to clipboard."""
        current = self.command_list.currentItem()
        if not current:
            return
            
        entry = current.data(Qt.ItemDataRole.UserRole)
        command = entry.get('command', '')
        
        clipboard = QApplication.clipboard()
        clipboard.setText(command)
        
        # Show temporary feedback
        self.show_copy_feedback("Command copied to clipboard!")
        
    def copy_selected_parameters(self):
        """Copy selected parameters to clipboard."""
        current = self.command_list.currentItem()
        if not current:
            return
            
        entry = current.data(Qt.ItemDataRole.UserRole)
        parameters = entry.get('parameters', {})
        
        # Format parameters as JSON
        param_text = json.dumps(parameters, indent=2)
        
        clipboard = QApplication.clipboard()
        clipboard.setText(param_text)
        
        self.show_copy_feedback("Parameters copied to clipboard!")
        
    def show_copy_feedback(self, message: str):
        """Show temporary feedback message."""
        # Change button text temporarily
        original_text = self.copy_button.text()
        self.copy_button.setText(message)
        
        # Reset after 2 seconds
        QTimer.singleShot(2000, lambda: self.copy_button.setText(original_text))
        
    def clear_history(self):
        """Clear command history."""
        reply = QMessageBox.question(
            self, "Clear History",
            "Clear all command history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.command_history.clear_history()
            self.refresh_history()
            QMessageBox.information(self, "Success", "Command history cleared!")
