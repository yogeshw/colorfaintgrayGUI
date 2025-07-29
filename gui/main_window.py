"""
Main window for astscript-color-faint-gray GUI application.

This module provides the main application window with tabbed interface,
menus, toolbars, and overall layout management.
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
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTabWidget, QMenuBar, QToolBar, QStatusBar, QLabel, QProgressBar,
    QMessageBox, QFileDialog, QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QKeySequence, QAction

from gui.image_loader import ImageLoaderWidget
from gui.parameter_panel import ParameterPanel
from gui.image_viewer import ImageViewer
from gui.grid_view import CacheGridView
from gui.dialogs import AboutDialog, SettingsDialog
from gui.progress_dialog import ProgressDialog
from gui.preset_manager import PresetManager, PresetDialog
from gui.command_history import CommandHistory, CommandHistoryDialog
from gui.image_comparison import ImageComparisonWidget
from core.config import Config
from core.image_generator import ImageGenerator
from core.cache_manager import CacheManager


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, config: Config, error_reporter=None, parent=None):
        """Initialize main window.
        
        Args:
            config: Application configuration
            error_reporter: Error reporting system
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config
        self.error_reporter = error_reporter
        
        # Initialize core components
        self.image_generator = ImageGenerator(config, self)
        self.cache_manager = CacheManager(
            config.get_cache_dir(),
            config.get("app.cache_size", 25)
        )
        self.preset_manager = PresetManager(config.get_config_dir())
        self.command_history = CommandHistory(config.get_config_dir())
        
        # Current state
        self.current_parameters = config.get_parameters()
        self.current_image_path = None
        
        # Setup UI
        self.setup_ui()
        self.apply_light_theme_styling()
        self.setup_menus()
        self.setup_toolbars()
        self.setup_status_bar()
        self.connect_signals()
        
        # Load settings
        self.load_settings()
        
        # Set window properties
        self.setWindowTitle("colorfaintgrayGUI")
        self.setMinimumSize(1400, 900)
    
    def apply_light_theme_styling(self):
        """Apply light theme styling to override dark system themes."""
        light_theme_style = """
        QMainWindow {
            background-color: #f0f0f0;
            color: #000000;
        }
        
        QWidget {
            background-color: #f0f0f0;
            color: #000000;
        }
        
        QTabWidget {
            background-color: #f0f0f0;
        }
        
        QTabWidget::pane {
            border: 1px solid #c0c0c0;
            background-color: #ffffff;
            margin: 0px;
            padding: 1px;
        }
        
        QTabBar::tab {
            background-color: #e0e0e0;
            color: #000000;
            padding: 8px 12px;
            margin-right: 2px;
            border: 1px solid #c0c0c0;
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff;
            border-bottom: 1px solid #ffffff;
        }
        
        QTabBar::tab:hover {
            background-color: #f5f5f5;
        }
        
        QPushButton {
            background-color: #e0e0e0;
            color: #000000;
            border: 1px solid #c0c0c0;
            padding: 6px 12px;
            border-radius: 4px;
        }
        
        QPushButton:hover {
            background-color: #d0d0d0;
        }
        
        QPushButton:pressed {
            background-color: #c0c0c0;
        }
        
        QPushButton:disabled {
            background-color: #f5f5f5;
            color: #808080;
        }
        
        QLineEdit, QSpinBox, QDoubleSpinBox {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #c0c0c0;
            padding: 4px;
            border-radius: 2px;
        }
        
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
            border: 2px solid #0078d4;
        }
        
        QTextEdit {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #c0c0c0;
        }
        
        QLabel {
            color: #000000;
            background-color: transparent;
        }
        
        QGroupBox {
            color: #000000;
            border: 1px solid #c0c0c0;
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 8px;
        }
        
        QGroupBox::title {
            color: #000000;
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        
        QScrollArea {
            background-color: #ffffff;
            border: 1px solid #c0c0c0;
        }
        
        QSlider::groove:horizontal {
            border: 1px solid #c0c0c0;
            height: 6px;
            background-color: #e0e0e0;
            border-radius: 3px;
        }
        
        QSlider::handle:horizontal {
            background-color: #0078d4;
            border: 1px solid #005a9e;
            width: 16px;
            margin: -5px 0;
            border-radius: 8px;
        }
        
        QSlider::handle:horizontal:hover {
            background-color: #106ebe;
        }
        
        QCheckBox {
            color: #000000;
        }
        
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #c0c0c0;
            background-color: #ffffff;
        }
        
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border: 1px solid #005a9e;
        }
        
        QStatusBar {
            background-color: #f0f0f0;
            color: #000000;
            border-top: 1px solid #c0c0c0;
        }
        
        QMenuBar {
            background-color: #f0f0f0;
            color: #000000;
            border-bottom: 1px solid #c0c0c0;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
        }
        
        QMenuBar::item:selected {
            background-color: #e0e0e0;
        }
        
        QMenu {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #c0c0c0;
        }
        
        QMenu::item {
            padding: 6px 20px;
        }
        
        QMenu::item:selected {
            background-color: #e0e0e0;
        }
        
        QToolBar {
            background-color: #f0f0f0;
            border: 1px solid #c0c0c0;
            spacing: 3px;
        }
        
        QToolBar::separator {
            background-color: #c0c0c0;
            width: 1px;
            margin: 0 4px;
        }
        """
        
        self.setStyleSheet(light_theme_style)
    
    def setup_ui(self):
        """Setup main user interface layout."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(2, 2, 2, 2)
        
        # Create main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Left panel - Parameters
        self.parameter_panel = ParameterPanel(self.config, self)
        self.parameter_panel.setMaximumWidth(280)
        self.parameter_panel.setMinimumWidth(200)
        main_splitter.addWidget(self.parameter_panel)
        
        # Center area - Tabs
        self.setup_center_area()
        main_splitter.addWidget(self.tab_widget)
        
        # Set splitter proportions
        main_splitter.setStretchFactor(0, 0)  # Parameter panel doesn't stretch
        main_splitter.setStretchFactor(1, 1)  # Tab area stretches
        
        # Set initial splitter sizes - heavily favor image area
        main_splitter.setSizes([220, 1180])
    
    def setup_center_area(self):
        """Setup center tabbed area."""
        self.tab_widget = QTabWidget()
        
        # Reduce tab widget margins for more image space
        self.tab_widget.setContentsMargins(0, 0, 0, 0)
        
        # Image Loader Tab
        self.image_loader = ImageLoaderWidget(self.config, self)
        self.tab_widget.addTab(self.image_loader, "Image Loader")
        
        # Preview Tab
        self.image_viewer = ImageViewer(self)
        self.tab_widget.addTab(self.image_viewer, "Preview")
        
        # Cache Grid Tab
        self.cache_grid = CacheGridView(self.cache_manager, self)
        self.tab_widget.addTab(self.cache_grid, "Cache Grid")
        
        # Comparison Tab
        self.comparison_widget = ImageComparisonWidget(self)
        self.tab_widget.addTab(self.comparison_widget, "Compare")
        
        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
    
    def setup_menus(self):
        """Setup application menus."""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        # Open images action
        open_action = QAction("&Open Images...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("Open R, G, B channel images")
        open_action.triggered.connect(self.open_images)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Save image action
        self.save_action = QAction("&Save Image...", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.setStatusTip("Save current generated image")
        self.save_action.setEnabled(False)
        self.save_action.triggered.connect(self.save_current_image)
        file_menu.addAction(self.save_action)
        
        # Export cache action
        export_cache_action = QAction("&Export Cache...", self)
        export_cache_action.setStatusTip("Export all cached images")
        export_cache_action.triggered.connect(self.export_cache)
        file_menu.addAction(export_cache_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        
        # Reset parameters action
        reset_action = QAction("&Reset Parameters", self)
        reset_action.setStatusTip("Reset all parameters to defaults")
        reset_action.triggered.connect(self.reset_parameters)
        edit_menu.addAction(reset_action)
        
        edit_menu.addSeparator()
        
        # Settings action
        settings_action = QAction("&Settings...", self)
        settings_action.setStatusTip("Open application settings")
        settings_action.triggered.connect(self.open_settings)
        edit_menu.addAction(settings_action)
        
        # Presets Menu
        presets_menu = menubar.addMenu("&Presets")
        
        # Manage presets action
        manage_presets_action = QAction("&Manage Presets...", self)
        manage_presets_action.setShortcut("Ctrl+P")
        manage_presets_action.setStatusTip("Save, load, and manage parameter presets")
        manage_presets_action.triggered.connect(self.manage_presets)
        presets_menu.addAction(manage_presets_action)
        
        presets_menu.addSeparator()
        
        # Save current preset action
        save_preset_action = QAction("&Save Current as Preset...", self)
        save_preset_action.setShortcut("Ctrl+Shift+S")
        save_preset_action.setStatusTip("Save current parameters as a new preset")
        save_preset_action.triggered.connect(self.save_current_preset)
        presets_menu.addAction(save_preset_action)
        
        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")
        
        # Command history action
        history_action = QAction("Command &History...", self)
        history_action.setShortcut("Ctrl+H")
        history_action.setStatusTip("View command history and copy commands")
        history_action.triggered.connect(self.show_command_history)
        tools_menu.addAction(history_action)
        
        tools_menu.addSeparator()
        
        # Copy current command action
        copy_command_action = QAction("&Copy Current Command", self)
        copy_command_action.setShortcut("Ctrl+Shift+C")
        copy_command_action.setStatusTip("Copy current command to clipboard")
        copy_command_action.triggered.connect(self.copy_current_command)
        tools_menu.addAction(copy_command_action)
        
        tools_menu.addSeparator()
        
        # Add to comparison action
        add_comparison_action = QAction("Add Current to &Comparison", self)
        add_comparison_action.setShortcut("Ctrl+M")
        add_comparison_action.setStatusTip("Add current image to comparison view")
        add_comparison_action.triggered.connect(self.add_current_to_comparison)
        tools_menu.addAction(add_comparison_action)
        
        # View Menu
        view_menu = menubar.addMenu("&View")
        
        # Toggle parameter panel
        toggle_params_action = QAction("Toggle &Parameter Panel", self)
        toggle_params_action.setShortcut("F9")
        toggle_params_action.setCheckable(True)
        toggle_params_action.setChecked(True)
        toggle_params_action.triggered.connect(self.toggle_parameter_panel)
        view_menu.addAction(toggle_params_action)
        
        # Cache Menu
        cache_menu = menubar.addMenu("&Cache")
        
        # Clear cache action
        clear_cache_action = QAction("&Clear Cache", self)
        clear_cache_action.setStatusTip("Clear all cached images")
        clear_cache_action.triggered.connect(self.clear_cache)
        cache_menu.addAction(clear_cache_action)
        
        # Cache info action
        cache_info_action = QAction("Cache &Info", self)
        cache_info_action.setStatusTip("Show cache information")
        cache_info_action.triggered.connect(self.show_cache_info)
        cache_menu.addAction(cache_info_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("About this application")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbars(self):
        """Setup application toolbars."""
        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setObjectName("MainToolBar")  # Set object name to avoid warning
        self.addToolBar(toolbar)
        
        # Generate image action
        self.generate_action = QAction("Generate Image", self)
        self.generate_action.setStatusTip("Generate color image with current parameters")
        self.generate_action.setEnabled(False)
        self.generate_action.triggered.connect(self.generate_image)
        toolbar.addAction(self.generate_action)
        
        toolbar.addSeparator()
        
        # Load images action
        load_action = QAction("Load Images", self)
        load_action.setStatusTip("Load R, G, B channel images")
        load_action.triggered.connect(self.open_images)
        toolbar.addAction(load_action)
        
        toolbar.addSeparator()
        
        # Clear cache action
        clear_cache_action = QAction("Clear Cache", self)
        clear_cache_action.setStatusTip("Clear all cached images")
        clear_cache_action.triggered.connect(self.clear_cache)
        toolbar.addAction(clear_cache_action)
    
    def setup_status_bar(self):
        """Setup status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Cache info
        self.cache_info_label = QLabel()
        self.update_cache_info_display()
        self.status_bar.addPermanentWidget(self.cache_info_label)
    
    def connect_signals(self):
        """Connect signals between components."""
        # Parameter panel signals
        self.parameter_panel.parameters_changed.connect(self.on_parameters_changed)
        self.parameter_panel.generate_requested.connect(self.generate_image)
        
        # Image loader signals
        self.image_loader.images_loaded.connect(self.on_images_loaded)
        self.image_loader.validation_changed.connect(self.on_validation_changed)
        
        # Image generator signals
        self.image_generator.started.connect(self.on_generation_started)
        self.image_generator.progress_updated.connect(self.on_generation_progress)
        self.image_generator.finished.connect(self.on_generation_finished)
        self.image_generator.error_occurred.connect(self.on_generation_error)
        
        # Cache grid signals
        self.cache_grid.image_selected.connect(self.on_cached_image_selected)
        self.cache_grid.cache_changed.connect(self.update_cache_info_display)
        self.cache_grid.add_to_comparison.connect(self.on_add_to_comparison_from_cache)
    
    def load_settings(self):
        """Load application settings."""
        import base64
        from PyQt6.QtCore import QByteArray
        
        # Restore window geometry
        geometry = self.config.get("app.window_geometry")
        if geometry:
            try:
                # Convert base64 string back to QByteArray
                geometry_bytes = base64.b64decode(geometry.encode('utf-8'))
                self.restoreGeometry(QByteArray(geometry_bytes))
            except Exception as e:
                print(f"Warning: Failed to restore window geometry: {e}")
        
        # Restore window state
        state = self.config.get("app.window_state")
        if state:
            try:
                # Convert base64 string back to QByteArray
                state_bytes = base64.b64decode(state.encode('utf-8'))
                self.restoreState(QByteArray(state_bytes))
            except Exception as e:
                print(f"Warning: Failed to restore window state: {e}")
    
    def save_settings(self):
        """Save application settings."""
        # Save window geometry and state (convert QByteArray to base64 string)
        import base64
        geometry = self.saveGeometry()
        state = self.saveState()
        
        self.config.set("app.window_geometry", base64.b64encode(geometry).decode('utf-8'))
        self.config.set("app.window_state", base64.b64encode(state).decode('utf-8'))
        
        # Note: Parameters are no longer saved automatically
        # They are only saved/loaded through explicit preset functionality
        
        # Save configuration (only UI settings, not parameters)
        self.config.save()
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save settings
        self.save_settings()
        
        # Cancel any ongoing generation
        self.image_generator.cancel_generation()
        
        # Accept close event
        event.accept()
    
    # Slot methods
    def on_parameters_changed(self, parameters):
        """Handle parameter changes."""
        self.current_parameters.update(parameters)
        self.status_label.setText("Parameters updated")
    
    def on_images_loaded(self, image_paths):
        """Handle images being loaded."""
        self.status_label.setText(f"Loaded {len(image_paths)} images")
        self.tab_widget.setCurrentIndex(1)  # Switch to preview tab
    
    def on_validation_changed(self, is_valid):
        """Handle validation state changes."""
        self.generate_action.setEnabled(is_valid)
    
    def on_generation_started(self):
        """Handle generation start."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.generate_action.setEnabled(False)
        self.status_label.setText("Generating image...")
    
    def on_generation_progress(self, message):
        """Handle generation progress updates."""
        self.status_label.setText(message)
    
    def on_generation_finished(self, image_path, parameters):
        """Handle generation completion."""
        self.progress_bar.setVisible(False)
        self.generate_action.setEnabled(True)
        self.current_image_path = image_path
        self.save_action.setEnabled(True)
        
        # Display image in viewer
        self.image_viewer.load_image(image_path)
        
        # Add to cache
        input_files = self.image_loader.get_current_files()
        if input_files:
            self.cache_manager.add_image(image_path, parameters, input_files)
            self.cache_grid.refresh()
            self.update_cache_info_display()
            
            # Add to command history
            from core.command_builder import CommandBuilder
            command_builder = CommandBuilder()
            command = command_builder.build_command(parameters)
            self.command_history.add_command(" ".join(command), parameters, input_files)
        
        self.status_label.setText("Image generated successfully")
        
        # Switch to preview tab
        self.tab_widget.setCurrentIndex(1)
    
    def on_generation_error(self, error_message):
        """Handle generation error."""
        self.progress_bar.setVisible(False)
        self.generate_action.setEnabled(True)
        
        QMessageBox.critical(self, "Generation Error", f"Failed to generate image:\n\n{error_message}")
        self.status_label.setText("Generation failed")
    
    def on_cached_image_selected(self, entry_id, entry):
        """Handle cached image selection."""
        if os.path.exists(entry.image_path):
            self.image_viewer.load_image(entry.image_path)
            self.current_image_path = entry.image_path
            self.save_action.setEnabled(True)
            
            # Load parameters from cache entry
            self.parameter_panel.load_parameters(entry.parameters)
            
            # Update command display with the cached entry command
            self.update_parameter_panel_command_from_cache(entry)
            
            # Switch to preview tab
            self.tab_widget.setCurrentIndex(1)
            
            self.status_label.setText(f"Loaded cached image: {entry_id}")
    
    def update_parameter_panel_command_from_cache(self, entry):
        """Update parameter panel command display from cache entry.
        
        Args:
            entry: Cache entry containing command information
        """
        try:
            # Rebuild the command from the cache entry parameters
            from core.command_builder import CommandBuilder
            command_builder = CommandBuilder()

            # Add the file paths from the cache entry
            params = entry.parameters.copy()
            if hasattr(entry, 'input_files'):
                input_files = entry.input_files
                def get_file(key):
                    # Try both 'red' and 'red_path' style keys
                    return input_files.get(key) or input_files.get(f"{key}_path")
                params.update({
                    'red_path': get_file('red'),
                    'green_path': get_file('green'),
                    'blue_path': get_file('blue'),
                    'output_path': entry.image_path
                })

            command_list = command_builder.build_command(params)
            self.parameter_panel.update_command_display(command_list)
        except Exception as e:
            # If command reconstruction fails, clear the display
            self.parameter_panel.command_display.setPlainText(f"Error retrieving command: {e}")
    
    def on_tab_changed(self, index):
        """Handle tab change."""
        if index == 2:  # Cache grid tab
            self.cache_grid.refresh()
    
    # Action methods
    def open_images(self):
        """Open dialog to select input images."""
        last_dir = self.config.get("app.last_input_dir", str(Path.home()))
        
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select R, G, B Channel Images",
            last_dir,
            "FITS Files (*.fits *.fit *.fts *.fits.fz);;All Files (*)"
        )
        
        if files:
            # Save last directory
            self.config.set("app.last_input_dir", str(Path(files[0]).parent))
            
            # Load files in image loader
            if len(files) >= 3:
                self.image_loader.load_files(files[:3])
            else:
                self.image_loader.load_files(files)
    
    def generate_image(self):
        """Generate color image with current parameters."""
        # Get current input files
        input_files = self.image_loader.get_current_files()
        if not input_files or not all(input_files.values()):
            QMessageBox.warning(self, "Missing Input", "Please load R, G, B channel images first.")
            return
        
        # Prepare parameters
        params = self.current_parameters.copy()
        params.update(input_files)
        
        # Show progress dialog
        from core.command_builder import CommandBuilder
        command_builder = CommandBuilder()
        command = command_builder.build_command(params)
        
        # Update command display in parameter panel
        self.parameter_panel.update_command_display(command)
        
        progress_dialog = ProgressDialog(self)
        progress_dialog.start_generation(self.image_generator, " ".join(command), params)
        
        # Show dialog and wait for completion
        progress_dialog.exec()
    
    def save_current_image(self):
        """Save current image to file."""
        if not self.current_image_path or not os.path.exists(self.current_image_path):
            QMessageBox.warning(self, "No Image", "No image available to save.")
            return
        
        last_dir = self.config.get("app.last_output_dir", str(Path.home()))
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            str(Path(last_dir) / "color_image.pdf"),
            "PDF Files (*.pdf);;PNG Files (*.png);;All Files (*)"
        )
        
        if filename:
            try:
                import shutil
                shutil.copy2(self.current_image_path, filename)
                self.config.set("app.last_output_dir", str(Path(filename).parent))
                self.status_label.setText(f"Image saved: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save image:\n{e}")
    
    def reset_parameters(self):
        """Reset parameters to defaults."""
        # Get complete defaults from command builder
        from core.command_builder import CommandBuilder
        command_builder = CommandBuilder()
        defaults = command_builder.get_default_params()
        
        # Reset config and current parameters
        self.config.reset_parameters()
        self.current_parameters = defaults.copy()
        
        # Update UI
        self.parameter_panel.load_parameters(self.current_parameters)
        self.status_label.setText("Parameters reset to defaults")
    
    def toggle_parameter_panel(self, visible):
        """Toggle parameter panel visibility."""
        self.parameter_panel.setVisible(visible)
    
    def clear_cache(self):
        """Clear all cached images."""
        reply = QMessageBox.question(
            self,
            "Clear Cache",
            "Are you sure you want to clear all cached images?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            count = self.cache_manager.clear_cache()
            self.cache_grid.refresh()
            self.update_cache_info_display()
            self.status_label.setText(f"Cleared {count} cached images")
    
    def export_cache(self):
        """Export all cached images."""
        if len(self.cache_manager.get_all_entries()) == 0:
            QMessageBox.information(self, "Empty Cache", "No cached images to export.")
            return
        
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Export Directory",
            self.config.get("app.last_output_dir", str(Path.home()))
        )
        
        if directory:
            try:
                exported = self.cache_manager.export_cache(directory)
                self.config.set("app.last_output_dir", directory)
                self.status_label.setText(f"Exported {len(exported)} images to {directory}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export cache:\n{e}")
    
    def show_cache_info(self):
        """Show cache information dialog."""
        stats = self.cache_manager.get_cache_stats()
        info_text = (
            f"Cache Statistics:\n\n"
            f"Total entries: {stats['total_entries']}\n"
            f"Maximum entries: {stats['max_entries']}\n"
            f"Total size: {stats['total_size_mb']:.1f} MB\n"
            f"Cache directory: {stats['cache_dir']}"
        )
        QMessageBox.information(self, "Cache Information", info_text)
    
    def open_settings(self):
        """Open settings dialog."""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            # Settings were changed, update cache manager if needed
            self.cache_manager.max_entries = self.config.get("app.cache_size", 25)
            self.update_cache_info_display()
    
    def show_about(self):
        """Show about dialog."""
        dialog = AboutDialog(self)
        dialog.exec()
    
    def update_cache_info_display(self):
        """Update cache info in status bar."""
        stats = self.cache_manager.get_cache_stats()
        self.cache_info_label.setText(
            f"Cache: {stats['total_entries']}/{stats['max_entries']} images"
        )
    
    def manage_presets(self):
        """Open preset management dialog."""
        current_params = self.parameter_panel.get_all_parameters()
        dialog = PresetDialog(self.preset_manager, current_params, self)
        dialog.preset_selected.connect(self.load_preset_parameters)
        dialog.exec()
        
    def save_current_preset(self):
        """Save current parameters as a preset."""
        from PyQt6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(
            self, "Save Preset", "Enter preset name:"
        )
        
        if not ok or not name.strip():
            return
            
        name = name.strip()
        current_params = self.parameter_panel.get_all_parameters()
        
        # Check if preset exists
        if self.preset_manager.load_preset(name):
            from PyQt6.QtWidgets import QMessageBox
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
            
        if self.preset_manager.save_preset(name, current_params, description):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Success", f"Preset '{name}' saved!")
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "Failed to save preset.")
            
    def load_preset_parameters(self, parameters):
        """Load parameters from preset."""
        self.parameter_panel.set_all_parameters(parameters)
        
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QKeySequence
        
        key = event.key()
        modifiers = event.modifiers()
        
        # F5 - Generate image
        if key == Qt.Key.Key_F5:
            self.generate_image()
            return
            
        # Ctrl+G - Generate image  
        if modifiers == Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_G:
            self.generate_image()
            return
            
        # Ctrl+R - Reset parameters
        if modifiers == Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_R:
            self.reset_parameters()
            return
            
        # Ctrl+1/2/3/4 - Switch tabs
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_1:
                self.tab_widget.setCurrentIndex(0)
                return
            elif key == Qt.Key.Key_2:
                self.tab_widget.setCurrentIndex(1) 
                return
            elif key == Qt.Key.Key_3:
                self.tab_widget.setCurrentIndex(2)
                return
            elif key == Qt.Key.Key_4:
                self.tab_widget.setCurrentIndex(3)
                return
                
        super().keyPressEvent(event)
    
    def show_command_history(self):
        """Show command history dialog."""
        dialog = CommandHistoryDialog(self.command_history, self)
        dialog.exec()
        
    def copy_current_command(self):
        """Copy current command to clipboard."""
        # Get current input files
        input_files = self.image_loader.get_current_files()
        if not input_files or not all(input_files.values()):
            QMessageBox.warning(self, "Missing Input", "Please load R, G, B channel images first.")
            return
        
        # Prepare parameters
        params = self.current_parameters.copy()
        params.update(input_files)
        
        # Build command
        from core.command_builder import CommandBuilder
        command_builder = CommandBuilder()
        command = command_builder.build_command(params)
        
        # Copy to clipboard
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(" ".join(command))
        
        self.status_label.setText("Command copied to clipboard")
    
    def add_current_to_comparison(self):
        """Add current image to comparison view."""
        if not self.current_image_path:
            QMessageBox.warning(self, "No Image", "Please generate an image first.")
            return
            
        # Find cache entry for current image
        cache_entry = None
        input_files = self.image_loader.get_current_files()
        if input_files:
            # Look for matching cache entry
            all_entries = self.cache_manager.get_all_entries()
            for entry in all_entries:
                if entry.output_path == self.current_image_path:
                    cache_entry = entry
                    break
                    
        # Add to comparison
        success = self.comparison_widget.add_image_for_comparison(
            self.current_image_path, cache_entry
        )
        
        if success:
            # Switch to comparison tab
            self.tab_widget.setCurrentIndex(3)
            self.status_label.setText("Image added to comparison")
        else:
            QMessageBox.warning(
                self, "Comparison Limit",
                "Cannot add more images to comparison."
            )
    
    def on_add_to_comparison_from_cache(self, entry_id: str, entry):
        """Add cached image to comparison view."""
        print(f"Adding to comparison: {entry_id}, image_path: {entry.image_path}")
        print(f"File exists: {os.path.exists(entry.image_path)}")
        
        success = self.comparison_widget.add_image_for_comparison(
            entry.image_path, entry
        )
        
        if success:
            # Switch to comparison tab
            self.tab_widget.setCurrentIndex(3)
            self.status_label.setText("Cached image added to comparison")
        else:
            QMessageBox.warning(
                self, "Comparison Limit",
                "Cannot add more images to comparison."
            )
