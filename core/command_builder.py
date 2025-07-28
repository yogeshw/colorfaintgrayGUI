"""
Command builder for astscript-color-faint-gray.

This module provides functionality to build command-line arguments for the
astscript-color-faint-gray script based on user parameters.
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
from typing import Dict, List, Optional, Any
from pathlib import Path


class CommandBuilder:
    """Builds astscript-color-faint-gray commands from parameters."""
    
    def __init__(self, astscript_path: str = "astscript-color-faint-gray"):
        """Initialize command builder.
        
        Args:
            astscript_path: Path to astscript-color-faint-gray executable
        """
        self.astscript_path = astscript_path
    
    def build_command(self, params: Dict[str, Any], validate_files: bool = True) -> List[str]:
        """Build complete command line from parameters.
        
        Args:
            params: Dictionary containing all parameters
            validate_files: Whether to validate that input files exist
            
        Returns:
            List of command line arguments
            
        Raises:
            ValueError: If required parameters are missing or files don't exist (when validate_files=True)
        """
        # Validate required parameters
        self._validate_required_params(params, validate_files)
        
        # Start with base command
        cmd = [self.astscript_path]
        
        # Add the required -g 0 flag for proper operation
        cmd.extend(['-g', '0'])
        
        # Add input files (Red, Green, Blue channels)
        cmd.extend([
            params['red_path'],
            params['green_path'], 
            params['blue_path']
        ])
        
        # Add output specification
        if 'output_path' in params:
            cmd.extend(['--output', params['output_path']])
        
        # Add core transformation parameters
        if params.get('qbright') is not None and params['qbright'] != 50.0:
            cmd.extend(['--qbright', str(params['qbright'])])
        
        if params.get('stretch') is not None and params['stretch'] != 0.1:
            cmd.extend(['--stretch', str(params['stretch'])])
        
        if params.get('contrast') is not None and params['contrast'] != 4.0:
            cmd.extend(['--contrast', str(params['contrast'])])
        
        if params.get('gamma') is not None and params['gamma'] != 0.5:
            cmd.extend(['--gamma', str(params['gamma'])])
        
        # Add brightness limit parameters
        if params.get('minimum') is not None:
            if isinstance(params['minimum'], list):
                for min_val in params['minimum']:
                    cmd.extend(['--minimum', str(min_val)])
            else:
                cmd.extend(['--minimum', str(params['minimum'])])
        
        if params.get('maximum') is not None:
            if isinstance(params['maximum'], list):
                for max_val in params['maximum']:
                    cmd.extend(['--maximum', str(max_val)])
            else:
                cmd.extend(['--maximum', str(params['maximum'])])
        
        # Add zero point calibration
        if params.get('zeropoint') is not None:
            if isinstance(params['zeropoint'], list):
                for zp in params['zeropoint']:
                    cmd.extend(['--zeropoint', str(zp)])
            else:
                cmd.extend(['--zeropoint', str(params['zeropoint'])])
        
        # Add region control parameters
        if params.get('colorval') is not None:
            cmd.extend(['--colorval', str(params['colorval'])])
        
        if params.get('grayval') is not None:
            cmd.extend(['--grayval', str(params['grayval'])])
        
        # Add boolean flags
        if params.get('coloronly', False):
            cmd.append('--coloronly')
        
        # Add quality parameter for output
        if params.get('quality') is not None and params['quality'] != 95:
            cmd.extend(['--quality', str(params['quality'])])
        
        # Add HDU specifications if provided
        if params.get('hdu'):
            if isinstance(params['hdu'], list):
                for hdu in params['hdu']:
                    cmd.extend(['--hdu', str(hdu)])
            else:
                cmd.extend(['--hdu', str(params['hdu'])])
        
        # Add temporary directory option
        if params.get('tmpdir'):
            cmd.extend(['--tmpdir', params['tmpdir']])
        
        # Add keep temporary files option
        if params.get('keeptmp', False):
            cmd.append('--keeptmp')
        
        # Add check parameters option
        if params.get('checkparams', False):
            cmd.append('--checkparams')
        
        return cmd
    
    def _validate_required_params(self, params: Dict[str, Any], validate_files: bool = True) -> None:
        """Validate that required parameters are present.
        
        Args:
            params: Parameters dictionary
            validate_files: Whether to validate that input files exist
            
        Raises:
            ValueError: If required parameters are missing or files don't exist (when validate_files=True)
        """
        required = ['red_path', 'green_path', 'blue_path']
        missing = [p for p in required if p not in params or not params[p]]
        
        if missing:
            raise ValueError(f"Missing required parameters: {missing}")
        
        # Check that input files exist only if validation is requested
        if validate_files:
            for param in required:
                path = params[param]
                if not os.path.exists(path):
                    raise ValueError(f"Input file does not exist: {path}")
    
    def format_command_string(self, params: Dict[str, Any], validate_files: bool = True) -> str:
        """Format command as a single string for display.
        
        Args:
            params: Parameters dictionary
            validate_files: Whether to validate that input files exist
            
        Returns:
            Command as a formatted string
        """
        cmd_list = self.build_command(params, validate_files)
        
        # Format for readability with line breaks
        formatted_parts = []
        current_line = cmd_list[0]  # Start with executable name
        
        i = 1
        while i < len(cmd_list):
            arg = cmd_list[i]
            
            # If this is an option (starts with -), start a new line
            if arg.startswith('-'):
                if current_line != cmd_list[0]:  # Don't add line break after executable
                    formatted_parts.append(current_line + ' \\')
                current_line = f"  {arg}"
                
                # Add the option value if it exists and doesn't start with -
                if i + 1 < len(cmd_list) and not cmd_list[i + 1].startswith('-'):
                    i += 1
                    current_line += f" {cmd_list[i]}"
            else:
                # This is a positional argument (input file)
                current_line += f" {arg}"
            
            i += 1
        
        formatted_parts.append(current_line)
        return '\n'.join(formatted_parts)
    
    def get_default_params(self) -> Dict[str, Any]:
        """Get default parameters for astscript-color-faint-gray.
        
        Returns:
            Dictionary with default parameter values
        """
        return {
            'qbright': 50.0,
            'stretch': 0.1,
            'contrast': 4.0,
            'gamma': 0.5,
            'minimum': None,
            'maximum': None,
            'zeropoint': None,
            'colorval': 15.0,  # Color threshold
            'grayval': 14.0,   # Gray threshold
            'coloronly': False,
            'quality': 95,
            'hdu': None,
            'tmpdir': None,
            'keeptmp': False,
            'checkparams': False
        }
    
    def validate_param_ranges(self, params: Dict[str, Any]) -> List[str]:
        """Validate parameter value ranges.
        
        Args:
            params: Parameters to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Validate numeric ranges
        if 'qbright' in params and params['qbright'] is not None:
            if not (0.0 <= params['qbright'] <= 100.0):
                errors.append("qbright must be between 0.0 and 100.0")
        
        if 'stretch' in params and params['stretch'] is not None:
            if params['stretch'] < 0:
                errors.append("stretch must be positive")
        
        if 'gamma' in params and params['gamma'] is not None:
            if params['gamma'] <= 0:
                errors.append("gamma must be positive")
        
        if 'quality' in params and params['quality'] is not None:
            if not (1 <= params['quality'] <= 100):
                errors.append("quality must be between 1 and 100")
        
        return errors
