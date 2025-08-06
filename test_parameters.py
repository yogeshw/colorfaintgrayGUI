#!/usr/bin/env python3
"""Test script for parameter panel functionality."""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from core.config import Config
from gui.parameter_panel import ParameterPanel


def test_parameter_panel():
    """Test the parameter panel functionality."""
    app = QApplication(sys.argv)
    
    config = Config()
    panel = ParameterPanel(config)
    
    # Test getting current parameters
    params = panel.get_current_parameters()
    print("Current parameters:")
    for name, value in params.items():
        print(f"  {name}: {value}")
    
    # Test command display
    panel.update_command_display()
    command_text = panel.command_display.toPlainText()
    print(f"\nGenerated command:\n{command_text}")
    
    # Show the panel
    window = QMainWindow()
    window.setCentralWidget(panel)
    window.show()
    
    # Exit after testing
    print("\nParameter panel test completed successfully!")
    app.quit()


if __name__ == "__main__":
    test_parameter_panel()
