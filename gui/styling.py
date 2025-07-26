"""
Application styling and theming.

This module provides application-wide styling and theme support
for a polished user interface.
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


from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor


class ApplicationStyle:
    """Manages application styling and themes."""
    
    @staticmethod
    def apply_dark_theme(app: QApplication):
        """Apply dark theme to the application."""
        app.setStyle("Fusion")
        
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(0, 0, 0))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        
        app.setPalette(dark_palette)
        
    @staticmethod
    def apply_light_theme(app: QApplication):
        """Apply light theme to the application."""
        app.setStyle("Fusion")
        app.setPalette(app.style().standardPalette())
        
    @staticmethod
    def get_stylesheet() -> str:
        """Get custom stylesheet for enhanced appearance."""
        return """
        /* Main Window */
        QMainWindow {
            background-color: #f0f0f0;
        }
        
        /* Tab Widget */
        QTabWidget::pane {
            border: 1px solid #c0c0c0;
            background-color: white;
        }
        
        QTabWidget::tab-bar {
            alignment: left;
        }
        
        QTabBar::tab {
            background-color: #e0e0e0;
            padding: 8px 12px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 2px solid #2196F3;
        }
        
        QTabBar::tab:hover {
            background-color: #f0f0f0;
        }
        
        /* Group Boxes */
        QGroupBox {
            font-weight: bold;
            border: 2px solid #c0c0c0;
            border-radius: 5px;
            margin-top: 1ex;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        
        /* Buttons */
        QPushButton {
            background-color: #e0e0e0;
            border: 1px solid #c0c0c0;
            border-radius: 3px;
            padding: 6px 12px;
            min-width: 60px;
        }
        
        QPushButton:hover {
            background-color: #f0f0f0;
            border-color: #a0a0a0;
        }
        
        QPushButton:pressed {
            background-color: #d0d0d0;
        }
        
        QPushButton:disabled {
            background-color: #f5f5f5;
            color: #a0a0a0;
            border-color: #e0e0e0;
        }
        
        /* Primary Action Buttons */
        QPushButton.primary {
            background-color: #2196F3;
            color: white;
            border-color: #1976D2;
        }
        
        QPushButton.primary:hover {
            background-color: #1976D2;
        }
        
        QPushButton.primary:pressed {
            background-color: #0D47A1;
        }
        
        /* Success Buttons */
        QPushButton.success {
            background-color: #4CAF50;
            color: white;
            border-color: #45a049;
        }
        
        QPushButton.success:hover {
            background-color: #45a049;
        }
        
        /* Warning Buttons */
        QPushButton.warning {
            background-color: #FF9800;
            color: white;
            border-color: #e68900;
        }
        
        QPushButton.warning:hover {
            background-color: #e68900;
        }
        
        /* Danger Buttons */
        QPushButton.danger {
            background-color: #f44336;
            color: white;
            border-color: #d32f2f;
        }
        
        QPushButton.danger:hover {
            background-color: #d32f2f;
        }
        
        /* Sliders */
        QSlider::groove:horizontal {
            height: 6px;
            background: #e0e0e0;
            border-radius: 3px;
        }
        
        QSlider::handle:horizontal {
            background: #2196F3;
            border: 1px solid #1976D2;
            width: 18px;
            height: 18px;
            border-radius: 9px;
            margin: -6px 0;
        }
        
        QSlider::handle:horizontal:hover {
            background: #1976D2;
        }
        
        /* Progress Bar */
        QProgressBar {
            border: 1px solid #c0c0c0;
            border-radius: 3px;
            text-align: center;
            background-color: #f0f0f0;
        }
        
        QProgressBar::chunk {
            background-color: #2196F3;
            border-radius: 2px;
        }
        
        /* Status Bar */
        QStatusBar {
            background-color: #e0e0e0;
            border-top: 1px solid #c0c0c0;
        }
        
        /* Tool Tips */
        QToolTip {
            background-color: #333;
            color: white;
            border: 1px solid #555;
            padding: 4px;
            border-radius: 3px;
        }
        
        /* Scroll Areas */
        QScrollArea {
            border: 1px solid #c0c0c0;
            background-color: white;
        }
        
        /* List Widgets */
        QListWidget {
            border: 1px solid #c0c0c0;
            background-color: white;
            selection-background-color: #2196F3;
            selection-color: white;
        }
        
        QListWidget::item {
            padding: 4px;
            border-bottom: 1px solid #f0f0f0;
        }
        
        QListWidget::item:hover {
            background-color: #f5f5f5;
        }
        
        /* Text Edits */
        QTextEdit, QPlainTextEdit {
            border: 1px solid #c0c0c0;
            background-color: white;
            selection-background-color: #2196F3;
            selection-color: white;
        }
        
        /* Line Edits */
        QLineEdit {
            border: 1px solid #c0c0c0;
            border-radius: 3px;
            padding: 4px;
            background-color: white;
            selection-background-color: #2196F3;
            selection-color: white;
        }
        
        QLineEdit:focus {
            border-color: #2196F3;
        }
        
        /* Spin Boxes */
        QSpinBox, QDoubleSpinBox {
            border: 1px solid #c0c0c0;
            border-radius: 3px;
            padding: 2px 4px;
            background-color: white;
        }
        
        QSpinBox:focus, QDoubleSpinBox:focus {
            border-color: #2196F3;
        }
        
        /* Combo Boxes */
        QComboBox {
            border: 1px solid #c0c0c0;
            border-radius: 3px;
            padding: 2px 4px;
            background-color: white;
            min-width: 60px;
        }
        
        QComboBox:focus {
            border-color: #2196F3;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #c0c0c0;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid #666;
        }
        
        /* Splitters */
        QSplitter::handle {
            background-color: #e0e0e0;
        }
        
        QSplitter::handle:horizontal {
            width: 6px;
            image: none;
        }
        
        QSplitter::handle:vertical {
            height: 6px;
            image: none;
        }
        
        QSplitter::handle:hover {
            background-color: #2196F3;
        }
        """
