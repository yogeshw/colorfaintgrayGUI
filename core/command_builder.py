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
        
        # Add HDU/extension parameters
        if params.get('hdu') and params['hdu'].strip():
            # Handle multiple HDUs separated by commas
            hdus = [h.strip() for h in params['hdu'].split(',') if h.strip()]
            for hdu in hdus:
                cmd.extend(['--hdu', hdu])
        
        if params.get('rhdu') and params['rhdu'].strip():
            cmd.extend(['--rhdu', params['rhdu']])
        
        if params.get('globalhdu') and params['globalhdu'].strip():
            cmd.extend(['--globalhdu', params['globalhdu']])
        else:
            # Add the required -g 0 flag for proper operation when no global HDU specified
            cmd.extend(['-g', '0'])
        
        # Add input files (Red, Green, Blue channels)
        cmd.extend([
            params['red_path'],
            params['green_path'], 
            params['blue_path']
        ])
        
        # Add weight parameters
        if params.get('weight') and params['weight'].strip():
            weights = [w.strip() for w in params['weight'].split(',') if w.strip()]
            for weight in weights:
                cmd.extend(['--weight', weight])
        
        # Add minimum value parameters
        if params.get('minimum') and params['minimum'].strip():
            minimums = [m.strip() for m in params['minimum'].split(',') if m.strip()]
            for minimum in minimums:
                cmd.extend(['--minimum', minimum])
        
        # Add zero point calibration
        if params.get('zeropoint') and params['zeropoint'].strip():
            zeropoints = [z.strip() for z in params['zeropoint'].split(',') if z.strip()]
            for zp in zeropoints:
                cmd.extend(['--zeropoint', zp])
        
        # Add core transformation parameters (always include as our defaults differ)
        cmd.extend(['--qbright', str(params.get('qbright', 50.0))])
        cmd.extend(['--stretch', str(params.get('stretch', 0.1))])
        
        # Add contrast, bias, and gamma parameters
        if params.get('bias') is not None and params['bias'] != 0.0:
            cmd.extend(['--bias', str(params['bias'])])
        
        cmd.extend(['--contrast', str(params.get('contrast', 4.0))])
        cmd.extend(['--gamma', str(params.get('gamma', 0.5))])
        
        # Add mark options
        if params.get('markoptions') and params['markoptions'].strip():
            cmd.extend(['--markoptions', params['markoptions']])
        
        # Add color/grayscale parameters (always include as our defaults differ)
        if params.get('coloronly', False):
            cmd.append('--coloronly')
        
        if params.get('regions') and params['regions'].strip():
            cmd.extend(['--regions', params['regions']])
        
        cmd.extend(['--grayval', str(params.get('grayval', 14.0))])
        cmd.extend(['--colorval', str(params.get('colorval', 15.0))])
        
        # Add kernel FWHM parameters
        if params.get('graykernelfwhm') is not None and params['graykernelfwhm'] != 1.0:
            cmd.extend(['--graykernelfwhm', str(params['graykernelfwhm'])])
        
        if params.get('colorkernelfwhm') is not None and params['colorkernelfwhm'] != 1.0:
            cmd.extend(['--colorkernelfwhm', str(params['colorkernelfwhm'])])
        
        # Add output specification
        if 'output_path' in params:
            cmd.extend(['--output', params['output_path']])
        
        # Add debug/output options
        if params.get('keeptmp', False):
            cmd.append('--keeptmp')
        
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
            # Input parameters
            'hdu': None,
            'rhdu': None,
            'globalhdu': None,
            'weight': None,
            'minimum': None,
            'zeropoint': None,
            
            # Asinh scaling parameters (our defaults differ from astscript)
            'qbright': 50.0,
            'stretch': 0.1,
            
            # Contrast, bias, and marks
            'bias': 0.0,
            'contrast': 4.0,
            'gamma': 0.5,
            'markoptions': None,
            
            # Color and gray parameters (our defaults differ from astscript)
            'coloronly': False,
            'regions': None,
            'grayval': 14.0,
            'colorval': 15.0,
            'graykernelfwhm': 1.0,
            'colorkernelfwhm': 1.0,
            
            # Output
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
