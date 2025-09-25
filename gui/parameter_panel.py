"""
Parameter panel widget for adjusting astscript-color-faint-gray parameters.

This module provides the parameter control panel with sliders, spinboxes,
and other controls for adjusting image generation parameters.
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


from typing import Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel,
    QSlider, QDoubleSpinBox, QSpinBox, QCheckBox, QPushButton, QComboBox,
    QScrollArea, QFrame, QSizePolicy, QTextEdit, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont


class ParameterControl(QWidget):
    """Base class for parameter controls."""
    
    value_changed = pyqtSignal(str, object)  # parameter_name, value
    
    def __init__(self, param_name: str, label: str, parent=None):
        """Initialize parameter control.
        
        Args:
            param_name: Parameter name
            label: Display label
            parent: Parent widget
        """
        super().__init__(parent)
        self.param_name = param_name
        self.label_text = label
        
    def get_value(self):
        """Get current parameter value."""
        raise NotImplementedError
    
    def set_value(self, value):
        """Set parameter value."""
        raise NotImplementedError


class SliderSpinBoxControl(ParameterControl):
    """Combined slider and spinbox control for numeric parameters."""
    
    def __init__(self, param_name: str, label: str, min_val: float, max_val: float,
                 step: float = 0.1, decimals: int = 2, default: float = 1.0, parent=None):
        """Initialize slider-spinbox control.
        
        Args:
            param_name: Parameter name
            label: Display label
            min_val: Minimum value
            max_val: Maximum value
            step: Step size
            decimals: Number of decimal places
            default: Default value
            parent: Parent widget
        """
        super().__init__(param_name, label, parent)
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.decimals = decimals
        self.default = default
        
        self.setup_ui()
        self.set_value(default)
    
    def setup_ui(self):
        """Setup control UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        self.label = QLabel(self.label_text)
        self.label.setFont(QFont("", 9))
        layout.addWidget(self.label)
        
        # Slider and spinbox layout
        control_layout = QHBoxLayout()
        
        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(int(self.min_val / self.step))
        self.slider.setMaximum(int(self.max_val / self.step))
        self.slider.valueChanged.connect(self.on_slider_changed)
        control_layout.addWidget(self.slider, 2)
        
        # Spinbox
        self.spinbox = QDoubleSpinBox()
        self.spinbox.setMinimum(self.min_val)
        self.spinbox.setMaximum(self.max_val)
        self.spinbox.setSingleStep(self.step)
        self.spinbox.setDecimals(self.decimals)
        self.spinbox.setMinimumWidth(65)
        self.spinbox.valueChanged.connect(self.on_spinbox_changed)
        control_layout.addWidget(self.spinbox, 0)
        
        layout.addLayout(control_layout)
    
    def on_slider_changed(self, value):
        """Handle slider value change."""
        float_value = value * self.step
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(float_value)
        self.spinbox.blockSignals(False)
        self.value_changed.emit(self.param_name, float_value)
    
    def on_spinbox_changed(self, value):
        """Handle spinbox value change."""
        slider_value = int(value / self.step)
        self.slider.blockSignals(True)
        self.slider.setValue(slider_value)
        self.slider.blockSignals(False)
        self.value_changed.emit(self.param_name, value)
    
    def get_value(self):
        """Get current value."""
        return self.spinbox.value()
    
    def set_value(self, value):
        """Set value."""
        self.spinbox.blockSignals(True)
        self.slider.blockSignals(True)
        
        self.spinbox.setValue(value)
        self.slider.setValue(int(value / self.step))
        
        self.spinbox.blockSignals(False)
        self.slider.blockSignals(False)


class CheckBoxControl(ParameterControl):
    """Checkbox control for boolean parameters."""
    
    def __init__(self, param_name: str, label: str, default: bool = False, parent=None):
        """Initialize checkbox control.
        
        Args:
            param_name: Parameter name
            label: Display label
            default: Default value
            parent: Parent widget
        """
        super().__init__(param_name, label, parent)
        self.default = default
        
        self.setup_ui()
        self.set_value(default)
    
    def setup_ui(self):
        """Setup control UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.checkbox = QCheckBox(self.label_text)
        self.checkbox.stateChanged.connect(self.on_changed)
        layout.addWidget(self.checkbox)
    
    def on_changed(self, state):
        """Handle checkbox state change."""
        checked = state == Qt.CheckState.Checked
        self.value_changed.emit(self.param_name, checked)
    
    def get_value(self):
        """Get current value."""
        return self.checkbox.isChecked()
    
    def set_value(self, value):
        """Set value."""
        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(bool(value))
        self.checkbox.blockSignals(False)


class SpinBoxOnlyControl(ParameterControl):
    """Double spinbox control for numeric parameters (no slider)."""
    
    def __init__(self, param_name: str, label: str, min_val: float, max_val: float,
                 step: float = 0.1, decimals: int = 2, default: float = 1.0, parent=None):
        """Initialize spinbox-only control.
        
        Args:
            param_name: Parameter name
            label: Display label
            min_val: Minimum value
            max_val: Maximum value
            step: Step size
            decimals: Number of decimal places
            default: Default value
            parent: Parent widget
        """
        super().__init__(param_name, label, parent)
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.decimals = decimals
        self.default = default
        
        self.setup_ui()
        self.set_value(default)
    
    def setup_ui(self):
        """Setup control UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        self.label = QLabel(self.label_text)
        self.label.setFont(QFont("", 9))
        layout.addWidget(self.label)
        
        # Spinbox
        self.spinbox = QDoubleSpinBox()
        self.spinbox.setMinimum(self.min_val)
        self.spinbox.setMaximum(self.max_val)
        self.spinbox.setSingleStep(self.step)
        self.spinbox.setDecimals(self.decimals)
        self.spinbox.setMinimumWidth(80)
        self.spinbox.valueChanged.connect(self.on_changed)
        layout.addWidget(self.spinbox)
    
    def on_changed(self, value):
        """Handle spinbox value change."""
        self.value_changed.emit(self.param_name, value)
    
    def get_value(self):
        """Get current value."""
        return self.spinbox.value()
    
    def set_value(self, value):
        """Set value."""
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(value)
        self.spinbox.blockSignals(False)


class SpinBoxControl(ParameterControl):
    """Spinbox control for integer parameters."""
    
    def __init__(self, param_name: str, label: str, min_val: int, max_val: int,
                 default: int = 1, parent=None):
        """Initialize spinbox control.
        
        Args:
            param_name: Parameter name
            label: Display label
            min_val: Minimum value
            max_val: Maximum value
            default: Default value
            parent: Parent widget
        """
        super().__init__(param_name, label, parent)
        self.min_val = min_val
        self.max_val = max_val
        self.default = default
        
        self.setup_ui()
        self.set_value(default)
    
    def setup_ui(self):
        """Setup control UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        self.label = QLabel(self.label_text)
        self.label.setFont(QFont("", 9))
        layout.addWidget(self.label)
        
        # Spinbox
        self.spinbox = QSpinBox()
        self.spinbox.setMinimum(self.min_val)
        self.spinbox.setMaximum(self.max_val)
        self.spinbox.valueChanged.connect(self.on_changed)
        layout.addWidget(self.spinbox)
    
    def on_changed(self, value):
        """Handle spinbox value change."""
        self.value_changed.emit(self.param_name, value)
    
    def get_value(self):
        """Get current value."""
        return self.spinbox.value()
    
    def set_value(self, value):
        """Set value."""
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(int(value))
        self.spinbox.blockSignals(False)


class LineEditControl(ParameterControl):
    """Line edit control for string parameters."""
    
    def __init__(self, param_name: str, label: str, default: str = "", placeholder: str = "", parent=None):
        """Initialize line edit control.
        
        Args:
            param_name: Parameter name
            label: Display label
            default: Default value
            placeholder: Placeholder text
            parent: Parent widget
        """
        super().__init__(param_name, label, parent)
        self.default = default
        self.placeholder = placeholder
        
        self.setup_ui()
        self.set_value(default)
    
    def setup_ui(self):
        """Setup control UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        self.label = QLabel(self.label_text)
        self.label.setFont(QFont("", 9))
        layout.addWidget(self.label)
        
        # Line edit
        self.line_edit = QLineEdit()
        if self.placeholder:
            self.line_edit.setPlaceholderText(self.placeholder)
        self.line_edit.textChanged.connect(self.on_changed)
        layout.addWidget(self.line_edit)
    
    def on_changed(self, text):
        """Handle text change."""
        self.value_changed.emit(self.param_name, text if text else None)
    
    def get_value(self):
        """Get current value."""
        text = self.line_edit.text().strip()
        return text if text else None
    
    def set_value(self, value):
        """Set value."""
        self.line_edit.blockSignals(True)
        self.line_edit.setText(str(value) if value is not None else "")
        self.line_edit.blockSignals(False)


class CollapsibleGroupBox(QGroupBox):
    """Collapsible group box for organizing parameters."""
    
    def __init__(self, title: str, collapsed: bool = False, parent=None):
        """Initialize collapsible group box.
        
        Args:
            title: Group box title
            collapsed: Initial collapsed state
            parent: Parent widget
        """
        super().__init__(title, parent)
        self.setCheckable(True)
        self.setChecked(not collapsed)
        self.toggled.connect(self.on_toggled)
        
        # Create content widget
        self.content_widget = QWidget()
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.content_widget)
        
        self.on_toggled(not collapsed)
    
    def on_toggled(self, checked):
        """Handle toggle state change."""
        self.content_widget.setVisible(checked)
    
    def get_content_layout(self):
        """Get layout for adding content."""
        if not self.content_widget.layout():
            layout = QVBoxLayout(self.content_widget)
            layout.setContentsMargins(5, 3, 5, 3)
            return layout
        return self.content_widget.layout()


class ParameterPanel(QWidget):
    """Main parameter control panel."""
    
    parameters_changed = pyqtSignal(dict)  # Updated parameters
    generate_requested = pyqtSignal()      # Generate button clicked
    
    def __init__(self, config, parent=None):
        """Initialize parameter panel.
        
        Args:
            config: Application configuration
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config
        self.controls = {}
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.emit_parameters_changed)
        
        self.setup_ui()
        self.connect_signals()
        
        # Load initial parameters
        self.load_parameters(config.get_parameters())
    
    def setup_ui(self):
        """Setup parameter panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        
        # Title
        title = QLabel("Parameters")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Scroll area for parameters
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Input parameters group
        self.setup_input_parameters(scroll_layout)
        
        # Basic parameters group
        self.setup_basic_parameters(scroll_layout)
        
        # Advanced parameters group  
        self.setup_advanced_parameters(scroll_layout)
        
        # Output settings group
        self.setup_output_settings(scroll_layout)
        
        # Command display section
        self.setup_command_display(scroll_layout)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # Action buttons
        self.setup_action_buttons(layout)
    
    def setup_input_parameters(self, parent_layout):
        """Setup input parameter controls."""
        group = CollapsibleGroupBox("Input Settings", collapsed=True)
        layout = group.get_content_layout()
        
        # HDU/extension for input channels
        hdu_control = LineEditControl(
            "hdu", "HDU/Extension:", "", "e.g., 0, SCI, or HDU0,HDU1,HDU2"
        )
        self.controls["hdu"] = hdu_control
        layout.addWidget(hdu_control)
        
        # HDU for regions image
        rhdu_control = LineEditControl(
            "rhdu", "Regions HDU:", "", "HDU for regions image"
        )
        self.controls["rhdu"] = rhdu_control
        layout.addWidget(rhdu_control)
        
        # Global HDU for all inputs
        globalhdu_control = LineEditControl(
            "globalhdu", "Global HDU:", "", "Use this HDU for all inputs"
        )
        self.controls["globalhdu"] = globalhdu_control
        layout.addWidget(globalhdu_control)
        
        # Weight for each channel
        weight_control = LineEditControl(
            "weight", "Channel Weights:", "", "e.g., 1.0,1.0,1.0 or single value"
        )
        self.controls["weight"] = weight_control
        layout.addWidget(weight_control)
        
        # Minimum value for each channel
        minimum_control = LineEditControl(
            "minimum", "Minimum Values:", "", "e.g., 0.0,0.0,0.0 or single value"
        )
        self.controls["minimum"] = minimum_control
        layout.addWidget(minimum_control)
        
        # Zero point magnitude
        zeropoint_control = LineEditControl(
            "zeropoint", "Zero Points:", "", "e.g., 25.0,25.0,25.0 or single value"
        )
        self.controls["zeropoint"] = zeropoint_control
        layout.addWidget(zeropoint_control)
        
        parent_layout.addWidget(group)
    
    def setup_basic_parameters(self, parent_layout):
        """Setup basic parameter controls."""
        group = QGroupBox("Basic Settings")
        layout = QVBoxLayout(group)
        
        # qbright parameter - brightness quantile (expanded max to 500)
        qbright_control = SpinBoxOnlyControl(
            "qbright", "Brightness Quantile:", 0.0, 500.0, 0.01, 2, 50.0
        )
        self.controls["qbright"] = qbright_control
        layout.addWidget(qbright_control)
        
        # stretch parameter - stretch 0.1
        stretch_control = SpinBoxOnlyControl(
            "stretch", "Color Stretch:", 0.01, 200.0, 0.01, 2, 0.1
        )
        self.controls["stretch"] = stretch_control
        layout.addWidget(stretch_control)
        
        # contrast parameter - contrast 4.0
        contrast_control = SpinBoxOnlyControl(
            "contrast", "Contrast:", 0.1, 20.0, 0.1, 2, 4.0
        )
        self.controls["contrast"] = contrast_control
        layout.addWidget(contrast_control)
        
        # gamma parameter - gamma 0.5
        gamma_control = SpinBoxOnlyControl(
            "gamma", "Gamma Correction:", 0.1, 5.0, 0.1, 2, 0.5
        )
        self.controls["gamma"] = gamma_control
        layout.addWidget(gamma_control)
        
        parent_layout.addWidget(group)
    
    def setup_advanced_parameters(self, parent_layout):
        """Setup advanced parameter controls."""
        group = CollapsibleGroupBox("Advanced Settings", collapsed=True)
        layout = group.get_content_layout()
        
        # Bias parameter
        bias_control = SpinBoxOnlyControl(
            "bias", "Bias (Constant Addition):", -100.0, 100.0, 0.1, 2, 0.0
        )
        self.controls["bias"] = bias_control
        layout.addWidget(bias_control)
        
        # Mark options
        markoptions_control = LineEditControl(
            "markoptions", "Mark Options:", "", "Options for adding marks"
        )
        self.controls["markoptions"] = markoptions_control
        layout.addWidget(markoptions_control)
        
        # Color/gray thresholds - color threshold 15.0, grey threshold 14.0
        colorval_control = SpinBoxOnlyControl(
            "colorval", "Color Threshold:", 0.0, 100.0, 0.1, 1, 15.0
        )
        self.controls["colorval"] = colorval_control
        layout.addWidget(colorval_control)
        
        grayval_control = SpinBoxOnlyControl(
            "grayval", "Gray Threshold:", 0.0, 100.0, 0.1, 1, 14.0
        )
        self.controls["grayval"] = grayval_control
        layout.addWidget(grayval_control)
        
        # Color only option
        coloronly_control = CheckBoxControl("coloronly", "Color Only (No Gray)", False)
        self.controls["coloronly"] = coloronly_control
        layout.addWidget(coloronly_control)
        
        # Regions image
        regions_control = LineEditControl(
            "regions", "Regions Image:", "", "Path to regions labeled image"
        )
        self.controls["regions"] = regions_control
        layout.addWidget(regions_control)
        
        # Kernel FWHM parameters
        graykernelfwhm_control = SpinBoxOnlyControl(
            "graykernelfwhm", "Gray Kernel FWHM:", 0.1, 20.0, 0.1, 2, 1.0
        )
        self.controls["graykernelfwhm"] = graykernelfwhm_control
        layout.addWidget(graykernelfwhm_control)
        
        colorkernelfwhm_control = SpinBoxOnlyControl(
            "colorkernelfwhm", "Color Kernel FWHM:", 0.1, 20.0, 0.1, 2, 1.0
        )
        self.controls["colorkernelfwhm"] = colorkernelfwhm_control
        layout.addWidget(colorkernelfwhm_control)
        
        parent_layout.addWidget(group)
    
    def setup_output_settings(self, parent_layout):
        """Setup output parameter controls."""
        group = CollapsibleGroupBox("Output Settings", collapsed=True)
        layout = group.get_content_layout()
        
        # Quality parameter
        quality_control = SpinBoxControl("quality", "Output Quality:", 1, 100, 95)
        self.controls["quality"] = quality_control
        layout.addWidget(quality_control)
        
        # Debug options
        keeptmp_control = CheckBoxControl("keeptmp", "Keep Temporary Files", False)
        self.controls["keeptmp"] = keeptmp_control
        layout.addWidget(keeptmp_control)
        
        checkparams_control = CheckBoxControl("checkparams", "Show Parameter Info", False)
        self.controls["checkparams"] = checkparams_control
        layout.addWidget(checkparams_control)
        
        parent_layout.addWidget(group)
    
    def setup_command_display(self, parent_layout):
        """Setup command display section."""
        group = QGroupBox("Generated Command")
        layout = QVBoxLayout(group)
        
        self.command_display = QTextEdit()
        self.command_display.setMaximumHeight(80)
        self.command_display.setReadOnly(True)
        self.command_display.setPlainText("No command generated yet")
        self.command_display.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                font-family: monospace;
                font-size: 10px;
            }
        """)
        layout.addWidget(self.command_display)
        
        parent_layout.addWidget(group)
    
    def setup_action_buttons(self, parent_layout):
        """Setup action buttons."""
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        parent_layout.addWidget(line)
        
        # Button layout
        button_layout = QVBoxLayout()
        
        # Generate button
        self.generate_button = QPushButton("Generate Image")
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.generate_button.clicked.connect(self.generate_requested.emit)
        button_layout.addWidget(self.generate_button)
        
        # Reset button
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_button)
        
        # Load/Save preset buttons
        preset_layout = QHBoxLayout()
        
        load_preset_button = QPushButton("Load Preset...")
        load_preset_button.clicked.connect(self.load_preset)
        preset_layout.addWidget(load_preset_button)
        
        save_preset_button = QPushButton("Save Preset...")
        save_preset_button.clicked.connect(self.save_preset)
        preset_layout.addWidget(save_preset_button)
        
        button_layout.addLayout(preset_layout)
        
        parent_layout.addLayout(button_layout)
    
    def connect_signals(self):
        """Connect control signals."""
        for control in self.controls.values():
            control.value_changed.connect(self.on_parameter_changed)
    
    def on_parameter_changed(self, param_name: str, value):
        """Handle parameter change.
        
        Args:
            param_name: Name of changed parameter
            value: New parameter value
        """
        # Debounce updates to avoid too frequent signals
        self.update_timer.start(100)
    
    def emit_parameters_changed(self):
        """Emit parameters changed signal with current values."""
        parameters = self.get_current_parameters()
        self.parameters_changed.emit(parameters)
        
        # Update command display
        self.update_command_display()
    
    def get_current_parameters(self) -> Dict[str, Any]:
        """Get current parameter values.
        
        Returns:
            Dictionary of current parameter values
        """
        parameters = {}
        for name, control in self.controls.items():
            value = control.get_value()
            # Always include all parameters to ensure complete command generation
            parameters[name] = value
        
        return parameters
    
    def load_parameters(self, parameters: Dict[str, Any]):
        """Load parameters into controls.
        
        Args:
            parameters: Parameter values to load
        """
        # Block signals during loading
        for control in self.controls.values():
            control.blockSignals(True)
        
        # Get defaults from command builder
        from core.command_builder import CommandBuilder
        command_builder = CommandBuilder()
        defaults = command_builder.get_default_params()
        
        # Set values
        for name, control in self.controls.items():
            if name in parameters and parameters[name] is not None:
                value = parameters[name]
                control.set_value(value)
            elif name in defaults and defaults[name] is not None:
                default_value = defaults[name]
                control.set_value(default_value)
            # For controls not in defaults, keep their initialization values
        
        # Restore signals
        for control in self.controls.values():
            control.blockSignals(False)
    
    def reset_to_defaults(self):
        """Reset all parameters to defaults."""
        # Get defaults from command builder to ensure completeness
        from core.command_builder import CommandBuilder
        command_builder = CommandBuilder()
        defaults = command_builder.get_default_params()
        
        # Update config with the complete defaults
        self.config.reset_parameters()
        
        # Load the defaults into controls
        self.load_parameters(defaults)
        self.emit_parameters_changed()
    
    def update_command_display(self, command_list=None):
        """Update the command display with the current command.
        
        Args:
            command_list: List of command arguments, or None to generate from current params
        """
        if command_list is None:
            # Generate command from current parameters
            try:
                from core.command_builder import CommandBuilder
                command_builder = CommandBuilder()
                params = self.get_current_parameters()
                
                # Add dummy file paths for display
                if 'red_path' not in params:
                    params['red_path'] = 'R.fits'
                if 'green_path' not in params:
                    params['green_path'] = 'G.fits'
                if 'blue_path' not in params:
                    params['blue_path'] = 'B.fits'
                if 'output_path' not in params:
                    params['output_path'] = 'output.tif'
                
                # Skip file validation for display purposes
                command_list = command_builder.build_command(params, validate_files=False)
            except Exception as e:
                self.command_display.setPlainText(f"Error generating command: {e}")
                return
        
        # Format command for display
        command_str = ' '.join(command_list)
        self.command_display.setPlainText(command_str)
    
    def load_preset(self):
        """Load parameter preset from file."""
        from gui.preset_manager import PresetManager, PresetDialog
        
        preset_manager = PresetManager(self.config.get_config_dir())
        current_params = self.get_current_parameters()
        
        dialog = PresetDialog(preset_manager, current_params, self)
        dialog.preset_selected.connect(self.apply_preset)
        dialog.exec()
    
    def save_preset(self):
        """Save current parameters as preset."""
        from gui.preset_manager import PresetManager, PresetDialog
        
        preset_manager = PresetManager(self.config.get_config_dir())
        current_params = self.get_current_parameters()
        
        dialog = PresetDialog(preset_manager, current_params, self)
        dialog.exec()
        
    def apply_preset(self, parameters):
        """Apply loaded preset parameters.
        
        Args:
            parameters: Dictionary of parameter values to apply
        """
        self.load_parameters(parameters)
        self.emit_parameters_changed()
