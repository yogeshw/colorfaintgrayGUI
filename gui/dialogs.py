"""
Dialog windows for the astscript-color-faint-gray GUI application.

This module provides various dialog windows including settings,
about dialog, and other utility dialogs.
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
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget,
    QGroupBox, QLabel, QPushButton, QLineEdit, QSpinBox, QCheckBox,
    QFileDialog, QTextEdit, QFrame, QComboBox, QDialogButtonBox,
    QMessageBox, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QIcon


class SettingsDialog(QDialog):
    """Settings dialog for application configuration."""
    
    def __init__(self, config, parent=None):
        """Initialize settings dialog.
        
        Args:
            config: Application configuration object
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config
        self.original_config = {}
        
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(500, 400)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)
        
        # Tab widget for different setting categories
        self.tab_widget = QTabWidget()
        
        # General settings tab
        self.setup_general_tab()
        
        # Cache settings tab
        self.setup_cache_tab()
        
        # Advanced settings tab
        self.setup_advanced_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
        button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self.restore_defaults)
        
        layout.addWidget(button_box)
    
    def setup_general_tab(self):
        """Setup general settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Application settings group
        app_group = QGroupBox("Application")
        app_layout = QGridLayout(app_group)
        
        # Default directories
        app_layout.addWidget(QLabel("Default Input Directory:"), 0, 0)
        self.input_dir_edit = QLineEdit()
        app_layout.addWidget(self.input_dir_edit, 0, 1)
        input_browse_btn = QPushButton("Browse...")
        input_browse_btn.clicked.connect(self.browse_input_dir)
        app_layout.addWidget(input_browse_btn, 0, 2)
        
        app_layout.addWidget(QLabel("Default Output Directory:"), 1, 0)
        self.output_dir_edit = QLineEdit()
        app_layout.addWidget(self.output_dir_edit, 1, 1)
        output_browse_btn = QPushButton("Browse...")
        output_browse_btn.clicked.connect(self.browse_output_dir)
        app_layout.addWidget(output_browse_btn, 1, 2)
        
        # Default output format
        app_layout.addWidget(QLabel("Default Output Format:"), 2, 0)
        self.output_format_combo = QComboBox()
        self.output_format_combo.addItems(["PDF", "PNG", "JPEG", "TIFF"])
        app_layout.addWidget(self.output_format_combo, 2, 1)
        
        layout.addWidget(app_group)
        
        # UI settings group
        ui_group = QGroupBox("User Interface")
        ui_layout = QGridLayout(ui_group)
        
        # Parameter panel width
        ui_layout.addWidget(QLabel("Parameter Panel Width:"), 0, 0)
        self.panel_width_spin = QSpinBox()
        self.panel_width_spin.setRange(200, 500)
        self.panel_width_spin.setSuffix(" px")
        ui_layout.addWidget(self.panel_width_spin, 0, 1)
        
        # Grid thumbnail size
        ui_layout.addWidget(QLabel("Grid Thumbnail Size:"), 1, 0)
        self.thumbnail_size_spin = QSpinBox()
        self.thumbnail_size_spin.setRange(100, 300)
        self.thumbnail_size_spin.setSuffix(" px")
        ui_layout.addWidget(self.thumbnail_size_spin, 1, 1)
        
        # Show advanced parameters by default
        self.show_advanced_check = QCheckBox("Show Advanced Parameters by Default")
        ui_layout.addWidget(self.show_advanced_check, 2, 0, 1, 2)
        
        layout.addWidget(ui_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "General")
    
    def setup_cache_tab(self):
        """Setup cache settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Cache settings group
        cache_group = QGroupBox("Cache Settings")
        cache_layout = QGridLayout(cache_group)
        
        # Cache size
        cache_layout.addWidget(QLabel("Maximum Cache Entries:"), 0, 0)
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(5, 100)
        self.cache_size_spin.setSuffix(" images")
        cache_layout.addWidget(self.cache_size_spin, 0, 1)
        
        # Cache directory
        cache_layout.addWidget(QLabel("Cache Directory:"), 1, 0)
        self.cache_dir_edit = QLineEdit()
        cache_layout.addWidget(self.cache_dir_edit, 1, 1)
        cache_browse_btn = QPushButton("Browse...")
        cache_browse_btn.clicked.connect(self.browse_cache_dir)
        cache_layout.addWidget(cache_browse_btn, 1, 2)
        
        layout.addWidget(cache_group)
        
        # Cache actions group
        actions_group = QGroupBox("Cache Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        # Clear cache button
        clear_cache_btn = QPushButton("Clear Cache Now")
        clear_cache_btn.clicked.connect(self.clear_cache)
        actions_layout.addWidget(clear_cache_btn)
        
        # Cache info
        self.cache_info_label = QLabel()
        self.update_cache_info()
        actions_layout.addWidget(self.cache_info_label)
        
        layout.addWidget(actions_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Cache")
    
    def setup_advanced_tab(self):
        """Setup advanced settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # astscript settings group
        astscript_group = QGroupBox("astscript-color-faint-gray")
        astscript_layout = QGridLayout(astscript_group)
        
        # astscript path
        astscript_layout.addWidget(QLabel("Executable Path:"), 0, 0)
        self.astscript_path_edit = QLineEdit()
        astscript_layout.addWidget(self.astscript_path_edit, 0, 1)
        astscript_browse_btn = QPushButton("Browse...")
        astscript_browse_btn.clicked.connect(self.browse_astscript_path)
        astscript_layout.addWidget(astscript_browse_btn, 0, 2)
        
        # Test astscript button
        test_astscript_btn = QPushButton("Test astscript")
        test_astscript_btn.clicked.connect(self.test_astscript)
        astscript_layout.addWidget(test_astscript_btn, 1, 0, 1, 3)
        
        layout.addWidget(astscript_group)
        
        # Debug settings group
        debug_group = QGroupBox("Debug Options")
        debug_layout = QVBoxLayout(debug_group)
        
        # Keep temporary files
        self.keep_temp_check = QCheckBox("Keep Temporary Files by Default")
        debug_layout.addWidget(self.keep_temp_check)
        
        # Show parameter info
        self.show_params_check = QCheckBox("Show Parameter Info by Default")
        debug_layout.addWidget(self.show_params_check)
        
        layout.addWidget(debug_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Advanced")
    
    def load_settings(self):
        """Load current settings into controls."""
        # Save original config for restore
        self.original_config = {
            'app': self.config.config['app'].copy(),
            'ui': self.config.config['ui'].copy(),
            'parameters': self.config.config['parameters'].copy()
        }
        
        # Load general settings
        self.input_dir_edit.setText(self.config.get("app.last_input_dir", ""))
        self.output_dir_edit.setText(self.config.get("app.last_output_dir", ""))
        self.output_format_combo.setCurrentText(self.config.get("app.default_output_format", "PDF"))
        
        # Load UI settings
        self.panel_width_spin.setValue(self.config.get("ui.parameter_panel_width", 300))
        self.thumbnail_size_spin.setValue(self.config.get("ui.grid_thumbnail_size", 150))
        self.show_advanced_check.setChecked(self.config.get("app.show_advanced_params", False))
        
        # Load cache settings
        self.cache_size_spin.setValue(self.config.get("app.cache_size", 25))
        self.cache_dir_edit.setText(self.config.get("app.cache_dir", ""))
        
        # Load advanced settings
        self.astscript_path_edit.setText(self.config.get("app.astscript_path", "astscript-color-faint-gray"))
        self.keep_temp_check.setChecked(self.config.get("parameters.keeptmp", False))
        self.show_params_check.setChecked(self.config.get("parameters.checkparams", False))
        
        self.update_cache_info()
    
    def apply_settings(self):
        """Apply current settings."""
        # Apply general settings
        self.config.set("app.last_input_dir", self.input_dir_edit.text())
        self.config.set("app.last_output_dir", self.output_dir_edit.text())
        self.config.set("app.default_output_format", self.output_format_combo.currentText())
        
        # Apply UI settings
        self.config.set("ui.parameter_panel_width", self.panel_width_spin.value())
        self.config.set("ui.grid_thumbnail_size", self.thumbnail_size_spin.value())
        self.config.set("app.show_advanced_params", self.show_advanced_check.isChecked())
        
        # Apply cache settings
        self.config.set("app.cache_size", self.cache_size_spin.value())
        self.config.set("app.cache_dir", self.cache_dir_edit.text())
        
        # Apply advanced settings
        self.config.set("app.astscript_path", self.astscript_path_edit.text())
        self.config.set("parameters.keeptmp", self.keep_temp_check.isChecked())
        self.config.set("parameters.checkparams", self.show_params_check.isChecked())
        
        # Save configuration
        self.config.save()
    
    def restore_defaults(self):
        """Restore default settings."""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset to defaults
            defaults = self.config.defaults
            
            # Reset general settings
            self.input_dir_edit.setText(str(Path.home()))
            self.output_dir_edit.setText(str(Path.home()))
            self.output_format_combo.setCurrentText(defaults['app']['default_output_format'])
            
            # Reset UI settings
            self.panel_width_spin.setValue(defaults['ui']['parameter_panel_width'])
            self.thumbnail_size_spin.setValue(defaults['ui']['grid_thumbnail_size'])
            self.show_advanced_check.setChecked(defaults['app']['show_advanced_params'])
            
            # Reset cache settings
            self.cache_size_spin.setValue(defaults['app']['cache_size'])
            self.cache_dir_edit.setText(defaults['app']['cache_dir'])
            
            # Reset advanced settings
            self.astscript_path_edit.setText(defaults['app']['astscript_path'])
            self.keep_temp_check.setChecked(defaults['parameters']['keeptmp'])
            self.show_params_check.setChecked(defaults['parameters']['checkparams'])
    
    def accept(self):
        """Accept dialog and apply settings."""
        self.apply_settings()
        super().accept()
    
    def reject(self):
        """Reject dialog and restore original settings."""
        # Restore original config
        self.config.config.update(self.original_config)
        super().reject()
    
    # Browse methods
    def browse_input_dir(self):
        """Browse for input directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Default Input Directory", self.input_dir_edit.text()
        )
        if directory:
            self.input_dir_edit.setText(directory)
    
    def browse_output_dir(self):
        """Browse for output directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Default Output Directory", self.output_dir_edit.text()
        )
        if directory:
            self.output_dir_edit.setText(directory)
    
    def browse_cache_dir(self):
        """Browse for cache directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Cache Directory", self.cache_dir_edit.text()
        )
        if directory:
            self.cache_dir_edit.setText(directory)
    
    def browse_astscript_path(self):
        """Browse for astscript executable."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select astscript-color-faint-gray Executable", 
            self.astscript_path_edit.text()
        )
        if file_path:
            self.astscript_path_edit.setText(file_path)
    
    def test_astscript(self):
        """Test astscript executable."""
        import subprocess
        
        astscript_path = self.astscript_path_edit.text()
        
        try:
            result = subprocess.run(
                [astscript_path, '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                QMessageBox.information(
                    self, "Test Successful", 
                    f"astscript-color-faint-gray is working correctly!\n\n"
                    f"Path: {astscript_path}"
                )
            else:
                QMessageBox.warning(
                    self, "Test Failed",
                    f"astscript-color-faint-gray returned error code {result.returncode}\n\n"
                    f"Error: {result.stderr}"
                )
        
        except subprocess.TimeoutExpired:
            QMessageBox.warning(self, "Test Failed", "astscript-color-faint-gray timed out")
        except FileNotFoundError:
            QMessageBox.critical(
                self, "Test Failed", 
                f"astscript-color-faint-gray not found at:\n{astscript_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Test Failed", f"Error testing astscript:\n{e}")
    
    def clear_cache(self):
        """Clear application cache."""
        # This would need to be connected to the actual cache manager
        QMessageBox.information(self, "Clear Cache", 
                               "Cache clearing should be implemented with cache manager reference")
    
    def update_cache_info(self):
        """Update cache information display."""
        # This would need to be connected to the actual cache manager
        self.cache_info_label.setText("Cache info would be shown here")


class AboutDialog(QDialog):
    """About dialog with application information."""
    
    def __init__(self, parent=None):
        """Initialize about dialog."""
        super().__init__(parent)
        
        self.setWindowTitle("About colorfaintgrayGUI")
        self.setModal(True)
        self.setFixedSize(600, 500)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup about dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Application icon and title
        header_layout = QHBoxLayout()
        
        # Icon placeholder
        icon_label = QLabel()
        icon_label.setFixedSize(64, 64)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setText("GUI")
        icon_label.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(icon_label)
        
        # Title and version
        title_layout = QVBoxLayout()
        
        title_label = QLabel("colorfaintgrayGUI")
        title_label.setFont(QFont("", 18, QFont.Weight.Bold))
        title_layout.addWidget(title_label)
        
        version_label = QLabel("Version 1.0.0")
        version_label.setStyleSheet("color: #666; font-size: 12px;")
        title_layout.addWidget(version_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Description
        description = QLabel(
            "colorfaintgrayGUI is a Qt6-based GUI application that provides an intuitive interface for "
            "GNU Astronomy Utilities' astscript-color-faint-gray script, enabling "
            "users to create color astronomical images with full dynamic range and "
            "enhanced visualization capabilities."
        )
        description.setWordWrap(True)
        description.setStyleSheet("margin: 10px 0px; font-size: 12px; line-height: 1.4;")
        layout.addWidget(description)
        
        # Create tabbed information area
        tab_widget = QTabWidget()
        
        # About tab
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        
        # Author and project information
        author_info = QLabel(
            "<b>Author:</b> Yogesh Wadadekar<br>"
            "<b>Development Year:</b> 2025<br>"
            "<b>Project:</b> colorfaintgrayGUI - GUI Frontend for astscript-color-faint-gray<br><br>"
            
            "<b>Built with:</b><br>"
            "• Python 3.x<br>"
            "• PyQt6 GUI Framework<br>"
            "• GNU Astronomy Utilities<br>"
            "• astscript-color-faint-gray backend<br><br>"
            
            "<b>Features:</b><br>"
            "• Interactive parameter adjustment<br>"
            "• Real-time image preview<br>"
            "• Image caching and comparison<br>"
            "• Preset management<br>"
            "• Command history and export"
        )
        author_info.setWordWrap(True)
        author_info.setTextFormat(Qt.TextFormat.RichText)
        author_info.setStyleSheet("font-size: 11px; line-height: 1.3;")
        about_layout.addWidget(author_info)
        about_layout.addStretch()
        
        tab_widget.addTab(about_tab, "About")
        
        # License tab
        license_tab = QWidget()
        license_layout = QVBoxLayout(license_tab)
        
        # License information
        license_header = QLabel(
            "<b>GNU General Public License v3.0</b><br>"
            "Copyright (C) 2025 Yogesh Wadadekar"
        )
        license_header.setTextFormat(Qt.TextFormat.RichText)
        license_header.setStyleSheet("font-size: 12px; font-weight: bold; margin-bottom: 10px;")
        license_layout.addWidget(license_header)
        
        # License summary
        license_summary = QLabel(
            "This program is free software: you can redistribute it and/or modify "
            "it under the terms of the GNU General Public License as published by "
            "the Free Software Foundation, either version 3 of the License, or "
            "(at your option) any later version.<br><br>"
            
            "This program is distributed in the hope that it will be useful, "
            "but WITHOUT ANY WARRANTY; without even the implied warranty of "
            "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the "
            "GNU General Public License for more details.<br><br>"
            
            "<b>Key License Features:</b><br>"
            "• Freedom to use the software for any purpose<br>"
            "• Freedom to study and modify the source code<br>"
            "• Freedom to distribute copies<br>"
            "• Freedom to distribute modified versions<br><br>"
            
            "You should have received a copy of the GNU General Public License "
            "along with this program. If not, see "
            "<a href='https://www.gnu.org/licenses/'>https://www.gnu.org/licenses/</a>."
        )
        license_summary.setWordWrap(True)
        license_summary.setTextFormat(Qt.TextFormat.RichText)
        license_summary.setOpenExternalLinks(True)
        license_summary.setStyleSheet("font-size: 11px; line-height: 1.3;")
        license_layout.addWidget(license_summary)
        license_layout.addStretch()
        
        tab_widget.addTab(license_tab, "License")
        
        # Credits tab
        credits_tab = QWidget()
        credits_layout = QVBoxLayout(credits_tab)
        
        credits_info = QLabel(
            "<b>Acknowledgments and Credits:</b><br><br>"
            
            "<b>GNU Astronomy Utilities:</b><br>"
            "This application is built upon the excellent work of the GNU Astronomy "
            "Utilities project, specifically the astscript-color-faint-gray script "
            "which provides the core image processing functionality.<br><br>"
            
            "<b>PyQt6:</b><br>"
            "The graphical user interface is built using PyQt6, the Python bindings "
            "for the Qt framework, providing a modern and responsive user experience.<br><br>"
            
            "<b>Python Community:</b><br>"
            "This project leverages the power of Python and its extensive ecosystem "
            "of libraries for scientific computing and GUI development.<br><br>"
            
            "<b>Open Source Community:</b><br>"
            "Special thanks to all the contributors and maintainers of the open source "
            "projects that make this software possible."
        )
        credits_info.setWordWrap(True)
        credits_info.setTextFormat(Qt.TextFormat.RichText)
        credits_info.setStyleSheet("font-size: 11px; line-height: 1.3;")
        credits_layout.addWidget(credits_info)
        credits_layout.addStretch()
        
        tab_widget.addTab(credits_tab, "Credits")
        
        layout.addWidget(tab_widget)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.setMinimumWidth(100)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)


class PresetDialog(QDialog):
    """Dialog for loading/saving parameter presets."""
    
    def __init__(self, mode="load", parent=None):
        """Initialize preset dialog.
        
        Args:
            mode: "load" or "save"
            parent: Parent widget
        """
        super().__init__(parent)
        self.mode = mode
        
        self.setWindowTitle(f"{'Load' if mode == 'load' else 'Save'} Preset")
        self.setModal(True)
        self.resize(400, 300)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup preset dialog UI."""
        layout = QVBoxLayout(self)
        
        if self.mode == "save":
            # Preset name input
            name_layout = QHBoxLayout()
            name_layout.addWidget(QLabel("Preset Name:"))
            
            self.name_edit = QLineEdit()
            self.name_edit.setPlaceholderText("Enter preset name...")
            name_layout.addWidget(self.name_edit)
            
            layout.addLayout(name_layout)
            
            # Description input
            layout.addWidget(QLabel("Description (optional):"))
            self.description_edit = QTextEdit()
            self.description_edit.setMaximumHeight(100)
            self.description_edit.setPlaceholderText("Enter description...")
            layout.addWidget(self.description_edit)
        
        else:
            # Preset list for loading
            layout.addWidget(QLabel("Available Presets:"))
            
            # TODO: Implement preset list widget
            self.preset_list = QLabel("Preset loading not yet implemented")
            layout.addWidget(self.preset_list)
        
        layout.addStretch()
        
        # Button box
        button_box = QDialogButtonBox()
        
        if self.mode == "save":
            button_box.setStandardButtons(
                QDialogButtonBox.StandardButton.Save |
                QDialogButtonBox.StandardButton.Cancel
            )
        else:
            button_box.setStandardButtons(
                QDialogButtonBox.StandardButton.Ok |
                QDialogButtonBox.StandardButton.Cancel
            )
        
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
