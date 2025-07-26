# ColorFaintGray GUI

A professional Qt6-based graphical interface for GNU Astronomy Utilities' `astscript-color-faint-gray` script, designed to make astronomical color image generation accessible and efficient.

## Features

- **Intuitive GUI**: Easy-to-use interface for astronomical image processing
- **Parameter Control**: Visual controls for all astscript-color-faint-gray parameters
- **Image Cache**: Automatic caching of generated images with metadata
- **Batch Processing**: Compare different parameter combinations
- **Export Options**: Save images in various formats (PDF, PNG, JPEG, TIFF)
- **Real-time Preview**: Immediate visual feedback of parameter changes

## Requirements

### System Dependencies
- Python 3.8 or higher
- GNU Astronomy Utilities (Gnuastro) with `astscript-color-faint-gray`
- Qt6 libraries

### Python Dependencies
- PyQt6 >= 6.5.0
- numpy >= 1.24.0
- astropy >= 5.2.0
- Pillow >= 9.5.0
- matplotlib >= 3.7.0
- psutil >= 5.9.0

## Installation

1. **Install GNU Astronomy Utilities**:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install gnuastro
   
   # On macOS with Homebrew
   brew install gnuastro
   
   # Or compile from source: https://www.gnu.org/software/gnuastro/
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify astscript-color-faint-gray is available**:
   ```bash
   astscript-color-faint-gray --help
   ```

## Usage

### Starting the Application

```bash
python main.py
```

### Basic Workflow

1. **Load Images**: 
   - Go to the "Image Loader" tab
   - Select FITS images for Red, Green, and Blue channels
   - Verify that all images are valid

2. **Adjust Parameters**:
   - Use the parameter panel on the left to adjust settings
   - Key parameters include:
     - `qbright`: Brightness quantile (0-10)
     - `stretch`: Color stretch factor (0.1-200)
     - `gamma`: Gamma correction (0.1-5.0)

3. **Generate Image**:
   - Click "Generate Image" button
   - Monitor progress in the status bar
   - View result in "Preview" tab

4. **Review and Compare**:
   - Generated images are automatically cached
   - Use "Cache Grid" tab to view all generated images
   - Compare different parameter combinations

5. **Export Results**:
   - Save individual images or export entire cache
   - Choose from multiple output formats

### Key Parameters

Based on the GNU Astronomy Utilities documentation:

- **qbright**: Controls the brightness quantile used for the asinh transformation
- **stretch**: Linear stretch factor for fainter regions  
- **gamma**: Gamma correction applied to the final image
- **colorval**: Threshold between color and black regions
- **grayval**: Threshold between black and gray regions
- **coloronly**: Show only color regions (no grayscale background)

### Advanced Features

- **Parameter Presets**: Save and load common parameter combinations
- **Command Export**: Copy exact astscript commands to clipboard
- **Batch Processing**: Queue multiple parameter sets for generation
- **Cache Management**: Automatic cleanup and manual cache control

## Project Structure

```
astscript-color-faint-gray-gui/
├── main.py                 # Application entry point
├── gui/                    # GUI components
│   ├── main_window.py      # Main application window
│   ├── image_loader.py     # Image loading interface
│   ├── parameter_panel.py  # Parameter controls
│   ├── image_viewer.py     # Image preview widget
│   ├── grid_view.py        # Cache grid view
│   └── dialogs.py          # Settings and utility dialogs
├── core/                   # Core functionality
│   ├── config.py          # Configuration management
│   ├── command_builder.py  # Command line construction
│   ├── image_generator.py  # Image generation workflow
│   └── cache_manager.py    # Image caching system
├── utils/                  # Utility functions
│   └── file_utils.py       # File operations
├── resources/              # Application resources
│   ├── icons/             # Application icons
│   └── styles/            # Stylesheets
└── cache/                 # Generated image cache
    ├── images/            # Cached image files
    └── metadata.json      # Cache metadata
```

## Configuration

The application stores configuration in:
- Linux/macOS: `~/.config/astscript-color-faint-gray/config.json`
- Windows: `%APPDATA%/astscript-color-faint-gray/config.json`

### Key Configuration Options

```json
{
  "parameters": {
    "qbright": 1.0,
    "stretch": 1.0,
    "gamma": 1.0
  },
  "app": {
    "cache_size": 25,
    "astscript_path": "astscript-color-faint-gray"
  },
  "ui": {
    "parameter_panel_width": 300,
    "grid_thumbnail_size": 150
  }
}
```

## Troubleshooting

### Common Issues

1. **"astscript-color-faint-gray not found"**
   - Ensure GNU Astronomy Utilities is installed
   - Check that `astscript-color-faint-gray` is in your PATH
   - Set custom path in Settings > Advanced

2. **"Failed to load FITS file"**
   - Verify file is valid FITS format
   - Check file permissions
   - Ensure astropy is installed correctly

3. **"Generation failed"**
   - Check that all three input images are provided
   - Verify images have compatible dimensions
   - Review parameter ranges (especially qbright, stretch)

### Performance Tips

- Use compressed FITS files (.fits.fz) to save disk space
- Limit cache size for better performance
- Close unused applications when processing large images
- Use SSD storage for cache directory if possible

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to branch: `git push origin feature-name`
6. Submit a pull request

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## Acknowledgments

- GNU Astronomy Utilities team for the excellent astscript-color-faint-gray tool
- PyQt6 developers for the GUI framework
- The astronomical community for feedback and testing

## References

- [GNU Astronomy Utilities Manual](https://www.gnu.org/software/gnuastro/manual/)
- [astscript-color-faint-gray Documentation](https://www.gnu.org/software/gnuastro/manual/html_node/Color-for-bright-regions-and-grayscale-for-faint.html)
- [PyQt6 Documentation](https://doc.qt.io/qtforpython/)

---

For questions, issues, or contributions, please visit the project repository or contact the maintainers.
