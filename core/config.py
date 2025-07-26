"""
Configuration management for astscript-color-faint-gray GUI application.

Handles application settings, default parameters, and user preferences.
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
from typing import Dict, Any, Optional


class Config:
    """Application configuration manager."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration manager.
        
        Args:
            config_dir: Custom configuration directory. If None, uses default.
        """
        if config_dir is None:
            self.config_dir = Path.home() / ".config" / "astscript-color-faint-gray"
        else:
            self.config_dir = Path(config_dir)
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        
        # Default configuration
        self.defaults = {
            # astscript-color-faint-gray default parameters
            "parameters": {
                "qbright": 1.0,
                "stretch": 1.0,
                "contrast": 3.0,
                "gamma": 0.8,
                "minimum": None,
                "maximum": None,
                "zeropoint": None,
                "colorval": None,  # Auto-estimated by script
                "grayval": None,   # Auto-estimated by script
                "coloronly": False,
                "quality": 95,
                "hdu": None,
                "tmpdir": None,
                "keeptmp": False,
                "checkparams": False
            },
            
            # Application settings
            "app": {
                "cache_size": 25,
                "cache_dir": str(Path.cwd() / "cache"),
                "default_output_format": "JPEG",
                "window_geometry": None,
                "window_state": None,
                "last_input_dir": str(Path.home()),
                "last_output_dir": str(Path.home()),
                "astscript_path": "astscript-color-faint-gray",
                "show_advanced_params": False
            },
            
            # UI preferences
            "ui": {
                "theme": "default",
                "parameter_panel_width": 300,
                "grid_thumbnail_size": 150,
                "preview_zoom_fit": True,
                "show_histograms": True
            }
        }
        
        # Load existing configuration
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_configs(self.defaults, config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load config file: {e}")
        
        return self.defaults.copy()
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Recursively merge loaded config with defaults."""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Warning: Failed to save config file: {e}")
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to config value (e.g., "parameters.qbright")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to config value
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get astscript-color-faint-gray parameters."""
        return self.config["parameters"].copy()
    
    def set_parameters(self, params: Dict[str, Any]):
        """Set astscript-color-faint-gray parameters."""
        self.config["parameters"].update(params)
    
    def reset_parameters(self):
        """Reset parameters to defaults."""
        self.config["parameters"] = self.defaults["parameters"].copy()
    
    def get_cache_dir(self) -> Path:
        """Get cache directory path."""
        cache_dir = Path(self.get("app.cache_dir"))
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    def get_config_dir(self) -> Path:
        """Get configuration directory path."""
        return self.config_dir
    
    def get_astscript_path(self) -> str:
        """Get astscript-color-faint-gray executable path."""
        return self.get("app.astscript_path", "astscript-color-faint-gray")
