# ColorFaintGray GUI - User Manual

## Overview

ColorFaintGray GUI is a PyQt6-based graphical interface for GNU Astronomy Utilities' `astscript-color-faint-gray` script. This application allows you to create color astronomical images from separate R, G, and B channel FITS files with an intuitive interface, powerful parameter controls, and comprehensive image management features.

## Getting Started

### System Requirements

- Python 3.8 or later
- PyQt6 (≥6.5.0)
- GNU Astronomy Utilities with `astscript-color-faint-gray` installed and in PATH
- Scientific Python packages: numpy, astropy, matplotlib, Pillow

### Installation

1. Ensure GNU Astronomy Utilities is installed and `astscript-color-faint-gray` is in your PATH:
   ```bash
   which astscript-color-faint-gray
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Interface Overview

The application features a modern tabbed interface with five main areas:

### Parameter Panel (Left Side)
- **Basic Parameters**: Common adjustments (qbright, stretch, contrast, gamma)
- **Advanced Parameters**: Detailed color/grayscale controls and quality settings  
- **Output Settings**: File format and quality options
- **Command Display**: Shows the exact astscript command that will be/was executed
- **Action Buttons**: Generate Image, Reset to Defaults, Load/Save Presets

### Main Tab Area (Center)

#### 1. Image Loader Tab
- **Purpose**: Load and validate R, G, B channel FITS files
- **Features**:
  - Individual file selection with browse buttons for each channel
  - Automatic FITS file validation with green checkmarks
  - File information display showing dimensions, data ranges, and headers
  - Thumbnail previews of each channel

#### 2. Preview Tab  
- **Purpose**: View generated color images with full interaction
- **Features**:
  - High-quality image display with smooth rendering
  - Mouse wheel zoom (zoom in/out around cursor position)
  - Left-click drag to pan around large images
  - Image information overlay
  - Direct save functionality

#### 3. Cache Grid Tab
- **Purpose**: Browse and manage previously generated images
- **Features**:
  - Thumbnail grid view of all cached images
  - Click thumbnails to view full-size in Preview tab
  - Automatic parameter restoration when selecting cached images
  - Cache statistics and management tools
  - Search and filter capabilities

#### 4. Compare Tab
- **Purpose**: Side-by-side comparison of different parameter combinations
- **Features**:
  - Add up to 4 images for simultaneous comparison
  - Parameter difference analysis and highlighting
  - Synchronized zoom and pan across comparison images
  - Export comparison data and images

## Basic Workflow

### 1. Load Images
1. Go to the **Image Loader** tab (usually active by default)
2. Click **Browse** for each channel (R, G, B) to select FITS files
3. Verify files are valid (green checkmarks indicate success)
4. Review file information in the display panel below

### 2. Adjust Parameters
Use the **Parameter Panel** on the left to adjust image processing settings:

#### Basic Parameters:
- **qbright (0-100)**: Controls bright feature enhancement - higher values make bright regions more prominent
- **stretch (0-100)**: Linear stretching for faint features - higher values reveal more faint detail  
- **contrast (0-100)**: Linear contrast adjustment - default is 3.0, higher values increase contrast
- **gamma (0.1-10.0)**: Nonlinear brightness adjustment - default is 0.8, values > 1 brighten, < 1 darken

#### Advanced Parameters (expand section):
- **colorval**: Threshold for color regions - areas above this value appear in color
- **grayval**: Threshold for grayscale regions - areas below this value appear in grayscale  
- **coloronly**: Checkbox to disable grayscale regions entirely (background in color/black)
- **quality (1-100)**: Output image quality percentage - default is 95

### 3. Generate Image
1. Click the large green **Generate Image** button in the Parameter Panel
2. Alternative methods: Use F5, Ctrl+G, or Tools → Generate Image
3. Monitor progress in the progress dialog that appears
4. Wait for completion - processing time depends on image size and complexity

### 4. View and Evaluate Results
1. The application automatically switches to the **Preview** tab when generation completes
2. Use mouse wheel to zoom in/out around the cursor position
3. Left-click and drag to pan around the image
4. Evaluate the result and return to step 2 if adjustments are needed

### 5. Save and Manage
1. **Save images**: Use File → Save Image (Ctrl+S) to export the current image
2. **Cache management**: Images are automatically cached - view them in the Cache Grid tab
3. **Presets**: Save successful parameter combinations using Presets → Save Current as Preset
4. **Commands**: Copy the exact command used via Tools → Copy Current Command

## Advanced Features

### Preset Management
- **Save Presets**: Store current parameter combinations for reuse
  - Access: Presets → Save Current as Preset (Ctrl+Shift+S)
  - Enter a descriptive name for the preset
  - Presets are saved as JSON files in the configuration directory

- **Load Presets**: Apply saved parameter sets instantly
  - Access: Presets → Manage Presets (Ctrl+P) or Load Preset button in Parameter Panel
  - Browse, preview, and select from saved presets
  - Parameters are immediately applied to the interface

- **Manage Presets**: Organize and delete saved presets
  - Access: Presets → Manage Presets (Ctrl+P)
  - View preset details, rename, or delete unwanted presets
  - Import/export presets for sharing with other users

### Cache Management System
- **Automatic Caching**: All generated images are automatically cached as .tif files
- **Thumbnail Generation**: PNG thumbnails are created for quick browsing
- **Parameter Preservation**: Each cached entry stores the exact parameters used
- **Command History**: The astscript command for each image is preserved
- **Cache Browsing**: Click any thumbnail in Cache Grid to view full-size and restore parameters
- **Cache Limits**: Default maximum of 25 cached images (configurable in settings)
- **Manual Management**: Clear cache or change settings via View → Settings

### Command History and Integration
- **Command Display**: Real-time display of the current astscript command in Parameter Panel
- **Command History**: View all previous commands via Tools → Command History (Ctrl+H)
- **Command Copying**: Copy current or historical commands via Tools → Copy Current Command (Ctrl+Shift+C)
- **CLI Integration**: Run copied commands directly in terminal for batch processing or scripting
- **Reproducibility**: Every parameter combination is preserved for exact reproduction

### Image Comparison System
- **Multi-Image Comparison**: Compare up to 4 different parameter combinations simultaneously
- **Add to Comparison**: Use Tools → Add Current to Comparison (Ctrl+M) to add images
- **Synchronized Viewing**: Zoom and pan are synchronized across comparison images
- **Parameter Analysis**: View parameter differences between compared images
- **Export Options**: Save comparison results including images and parameter data

### Keyboard Shortcuts

| Action | Shortcut | Description |
|--------|----------|-------------|
| Generate Image | F5, Ctrl+G | Create color image with current parameters |
| Open Images | Ctrl+O | Open file dialog to load R, G, B channels |
| Save Image | Ctrl+S | Save current generated image to file |
| Reset Parameters | Ctrl+R | Restore all parameters to default values |
| Manage Presets | Ctrl+P | Open preset management dialog |
| Save Current Preset | Ctrl+Shift+S | Save current parameters as new preset |
| Command History | Ctrl+H | View complete command history |
| Copy Current Command | Ctrl+Shift+C | Copy current command to clipboard |
| Add to Comparison | Ctrl+M | Add current image to comparison view |
| Switch to Tab 1 | Ctrl+1 | Switch to Image Loader tab |
| Switch to Tab 2 | Ctrl+2 | Switch to Preview tab |
| Switch to Tab 3 | Ctrl+3 | Switch to Cache Grid tab |
| Switch to Tab 4 | Ctrl+4 | Switch to Compare tab |
| Toggle Parameters | F9 | Show/hide parameter panel |

## Parameter Reference

### Basic Parameters

- **qbright** (0-100, default 1.0): Parameter for bringing out brighter features. Higher values enhance bright regions like star cores and bright nebula areas.

- **stretch** (0-100, default 1.0): Linear stretching parameter for faint features. Higher values stretch the dynamic range to reveal faint background details.

- **contrast** (0-100, default 3.0): Linear contrast adjustment applied to the final image. Higher values increase overall contrast.

- **gamma** (0.1-10.0, default 0.8): Nonlinear brightness adjustment using gamma correction. Values > 1 brighten the image, < 1 darken it. This is applied after linear processing.

### Advanced Parameters

- **colorval** (auto-estimated): Lowest value threshold for color regions. Pixels above this value are rendered in color using RGB data. If not specified, astscript estimates this automatically.

- **grayval** (auto-estimated): Highest value threshold for grayscale regions. Pixels below this value are rendered in grayscale. If not specified, astscript estimates this automatically.

- **coloronly** (checkbox, default false): If enabled, no grayscale regions are created. Background appears either in color or black, eliminating the transition zone.

### Output Settings

- **quality** (1-100, default 95): Output image quality percentage. Higher values produce better quality but larger file sizes.

### Technical Parameters (rarely used)

- **minimum**: Minimum value for each input channel (usually auto-determined)
- **maximum**: Maximum value for each input channel (usually auto-determined)  
- **zeropoint**: Zero point magnitude for each input channel
- **hdu**: Specific HDU to use from multi-extension FITS files
- **tmpdir**: Temporary directory for processing (uses system default)
- **keeptmp**: Keep temporary files for debugging
- **checkparams**: Enable parameter validation mode

## Tips and Best Practices

### Image Loading Best Practices
- Ensure R, G, B files have identical dimensions and world coordinate systems
- Use properly calibrated files (flat-fielded, dark-subtracted, bias-corrected)
- Verify exposure times are appropriate for the color combination you want
- Check file headers for consistent calibration and astrometric solutions

### Parameter Tuning Strategy
1. **Start with defaults**: Begin with the provided default values (qbright=1.0, stretch=1.0, contrast=3.0, gamma=0.8)
2. **Adjust systematically**: Change one parameter at a time to understand its effect
3. **Use qbright first**: Adjust bright feature enhancement before other parameters
4. **Fine-tune with gamma**: Use gamma for overall brightness balance after linear adjustments
5. **Color thresholds last**: Adjust colorval/grayval after basic parameters are set

### Performance Optimization
- **Cache utilization**: Use the Cache Grid to avoid regenerating identical images
- **Save successful combinations**: Create presets for parameter sets that work well
- **Clear old cache**: Periodically clear cache to free disk space (default limit: 25 images)
- **Use appropriate quality**: Lower quality settings (80-90) for preview, higher (95-100) for final images

### Workflow Efficiency
- **Keyboard shortcuts**: Learn common shortcuts like F5 (generate), Ctrl+S (save), Ctrl+M (add to comparison)
- **Parameter panel**: Keep the parameter panel visible for quick adjustments
- **Command copying**: Use Ctrl+Shift+C to copy commands for batch processing or documentation
- **Presets organization**: Create descriptive preset names for different object types

### Quality Control
- **Use comparison mode**: Compare different parameter combinations side-by-side
- **Check the command display**: Verify the exact astscript command being executed
- **Review cache entries**: Browse previous attempts in the Cache Grid
- **Save intermediate results**: Don't overwrite good results - save them as separate images

### File Management
- **Output formats**: The application generates TIFF files for caching, but you can save in various formats
- **Backup important results**: Save successful images and their parameter presets
- **Organize by object type**: Use descriptive filenames and preset names
- **Keep parameter records**: The command history maintains a record of all successful combinations

## Troubleshooting

### Installation and Startup Issues

**"Missing Dependencies" Error**
- Ensure all Python packages are installed: `pip install -r requirements.txt`
- Verify PyQt6 is properly installed: `python -c "import PyQt6; print('PyQt6 OK')"`
- Check Python version: requires Python 3.8 or later

**"astscript-color-faint-gray not found" Error**  
- Verify GNU Astronomy Utilities is installed: `which astscript-color-faint-gray`
- Check PATH environment variable includes the astscript location
- Test manual execution: `astscript-color-faint-gray --help`

**Application won't start**
- Check console for specific error messages
- Verify configuration directory permissions: `~/.config/astscript-color-faint-gray/`
- Try deleting config file to reset: `rm ~/.config/astscript-color-faint-gray/config.json`

### File Loading Issues

**"Invalid FITS File" Error**
- Check file integrity with: `python -c "from astropy.io import fits; fits.info('yourfile.fits')"`
- Ensure files contain image data (not just headers or tables)
- Verify file permissions and accessibility
- Check that files are standard FITS format, not compressed or proprietary

**"Dimension Mismatch" Error**
- All three input files must have identical dimensions
- Check image sizes: `fits info -s yourfile.fits` (GNU Astronomy Utilities)
- Verify world coordinate systems are compatible
- Consider reprocessing images to match dimensions

### Generation Problems

**Generation Fails with Parameter Errors**
- Check parameter ranges in the GUI (values outside ranges are highlighted in red)
- Try default parameters first to isolate the issue
- Review the specific astscript error message in the error dialog
- Verify input files are not corrupted

**"Out of Memory" Error**
- Reduce image size or use smaller test images first
- Close other memory-intensive applications
- Check available system memory
- Consider processing in chunks for very large images

**Very Slow Processing**
- Normal for large images (>4000x4000 pixels)
- Check CPU usage - astscript should use near 100% of one core
- Ensure adequate free disk space for temporary files
- Consider using tmpdir parameter to specify fast storage

### Interface Issues

**Parameter Panel Not Responding**
- Try resetting parameters with Ctrl+R
- Check if values are within valid ranges
- Restart the application if controls become unresponsive

**Cache Thumbnails Not Showing**
- Check cache directory permissions: `ls -la ~/.cache/astscript-color-faint-gray/`
- Verify disk space is available for thumbnail generation
- Try clearing and regenerating cache

**Image Display Problems**
- For very large images, zoom out to see the full image
- Check if GPU drivers are updated for smooth rendering
- Try software rendering if hardware acceleration causes issues

### Getting Help

1. **Error Dialogs**: Check error dialogs for specific astscript messages and guidance
2. **Parameter Tooltips**: Hover over parameter controls for detailed descriptions
3. **Command Display**: Check the command being executed in the Parameter Panel
4. **Console Output**: Run from terminal to see detailed error messages
5. **GNU Astronomy Documentation**: Consult official astscript-color-faint-gray documentation
6. **Log Files**: Check application logs in the configuration directory

## Configuration and File Management

### Configuration Directory
- **Location**: `~/.config/astscript-color-faint-gray/` (Linux/macOS) or equivalent on Windows
- **Contents**:
  - `config.json`: Application settings and parameter defaults
  - `presets/`: Saved parameter presets
  - `command_history.json`: Command history log
  - `error.log`: Application error log

### Cache Management
- **Default location**: Application directory `/cache/`
- **Contents**:
  - `images/`: Generated TIFF images
  - `thumbnails/`: PNG thumbnail images
  - `metadata.json`: Image metadata and parameters
- **Settings**: Configurable via View → Settings
- **Limits**: Default maximum of 25 images (oldest removed automatically)
- **Manual cleanup**: Use Cache → Clear Cache or delete files manually

### Data Export and Backup
- **Save Images**: Use File → Save Image for individual exports
- **Export Cache**: Batch export all cached images
- **Preset Backup**: Copy preset files from configuration directory
- **Configuration Backup**: Copy entire config directory for full backup

## Advanced Usage

### Command Line Integration
The GUI generates standard astscript-color-faint-gray commands that can be used independently:

```bash
# Example generated command:
astscript-color-faint-gray -g r.fits -r g.fits -b b.fits \
  -q qbright,stretch,contrast,gamma \
  --colorval 0.5 --grayval 0.1 --quality 95 output.tif
```

### Batch Processing
1. Use the GUI to find optimal parameters for your images
2. Copy commands from Command History (Ctrl+H)
3. Create shell scripts for batch processing multiple image sets
4. Use presets to maintain consistent parameters across batches

### Scripting and Automation
- Parameter presets are stored as JSON files for easy programmatic access
- Command history provides templates for automated workflows
- Configuration files can be modified programmatically for custom setups

## Appendix

### File Format Support
- **Input**: FITS files (single or multi-extension)
- **Output**: TIFF (cache), PDF, PNG, JPEG (save options)
- **Thumbnails**: PNG format for cache browsing

### Performance Notes
- Processing time scales roughly with image size squared
- Memory usage is proportional to total pixel count across all channels
- Disk space needed: ~3x total input file size for processing and cache

### Version Information
This manual applies to ColorFaintGray GUI v1.0 and later, designed for GNU Astronomy Utilities 0.18+.

---

*For additional technical details about the underlying astscript parameters and algorithms, consult the official GNU Astronomy Utilities documentation at: https://www.gnu.org/software/gnuastro/*
