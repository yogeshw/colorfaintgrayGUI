#!/usr/bin/env python3
"""
astscript-color-faint-gray GUI Application

A Qt6-based GUI application that provides an intuitive interface for 
GNU Astronomy Utilities' astscript-color-faint-gray script.

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

Author: Yogesh Wadadekar
Date: 2025-07-23
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow
from core.config import Config
from utils.error_handling import ErrorReporter, GlobalExceptionHandler


def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import numpy
        import astropy
        from PIL import Image
        import matplotlib
        return True
    except ImportError as e:
        QMessageBox.critical(
            None,
            "Missing Dependencies",
            f"Required dependency not found: {e}\n\n"
            "Please install dependencies with:\n"
            "pip install -r requirements.txt"
        )
        return False


def check_astscript():
    """Check if astscript-color-faint-gray is available."""
    import subprocess
    try:
        result = subprocess.run(
            ['astscript-color-faint-gray', '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def main():
    """Main entry point for the application."""
    print("Starting application...")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='astscript-color-faint-gray GUI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Start GUI
  %(prog)s --config           # Show config path
  %(prog)s --version          # Show version
        """.strip()
    )
    
    parser.add_argument(
        '--config',
        action='store_true',
        help='Show configuration file path'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='astscript-color-faint-gray GUI v1.0.0'
    )
    
    args = parser.parse_args()
    print(f"Arguments parsed: {args}")
    
    # Handle non-GUI options
    if args.config:
        config = Config()
        print(f"Configuration file: {config.config_file}")
        return 0
    
    print("Initializing Qt application...")
    # Initialize Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("ColorFaintGray GUI")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("GNU Astronomy Tools")
    
    # Apply styling
    from gui.styling import ApplicationStyle
    app.setStyleSheet(ApplicationStyle.get_stylesheet())
    
    # Set up error handling
    config = Config()
    error_reporter = ErrorReporter(config.get_config_dir())
    exception_handler = GlobalExceptionHandler(error_reporter)
    
    print("Checking dependencies...")
    # Check dependencies
    if not check_dependencies():
        return 1
    
    print("Checking astscript...")
    if not check_astscript():
        return 1
    
    print("Creating main window...")
    # Create and show main window
    window = MainWindow(config, error_reporter)
    window.show()
    
    print("Starting event loop...")
    # Start event loop
    return app.exec()


if __name__ == "__main__":
    import argparse
    
    print("Script started", flush=True)
    
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
