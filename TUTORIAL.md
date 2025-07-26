# ColorFaintGray GUI Tutorial

Welcome to the ColorFaintGray GUI tutorial! This guide will walk you through creating your first astronomical color image step by step using the PyQt6-based graphical interface for GNU Astronomy Utilities' `astscript-color-faint-gray`.

## Prerequisites

Before starting, ensure you have:
- ColorFaintGray GUI installed and working
- GNU Astronomy Utilities with `astscript-color-faint-gray` in your PATH
- Sample FITS files for R, G, B channels
- Basic understanding of astronomical imaging

## Quick Start: Creating Your First Color Image

### Step 1: Launch the Application

Start the application from the command line:
```bash
python main.py
```

You should see the main window with:
- **Parameter Panel** on the left with controls and a "Generate Image" button
- **Four tabs** in the center: Image Loader, Preview, Cache Grid, Compare
- **Menu bar** with File, Presets, Tools, View, and Help menus
- **Status bar** showing application status and cache information

### Step 2: Load Your Images

1. **The Image Loader tab** should be active by default
2. **Load R channel**: Click "Browse" next to "R Channel" and select your red FITS file
3. **Load G channel**: Click "Browse" next to "G Channel" and select your green FITS file  
4. **Load B channel**: Click "Browse" next to "B Channel" and select your blue FITS file

**Validation**: You should see green checkmarks next to each file if they're valid. The file information panel will show details about your images including dimensions and data ranges.

**Important**: All three images should have the same dimensions and coordinate system for best results.

### Step 3: Basic Parameter Adjustment

With your images loaded, it's time to adjust the basic parameters. The Parameter Panel on the left contains all controls:

#### Basic Parameters (always visible):
1. **qbright (0-100)**: Controls how bright features appear
   - Default: 1.0
   - Try values between 0.5-2.0
   - Higher values = brighter features become more prominent

2. **stretch (0-100)**: Linear stretching for faint features  
   - Default: 1.0
   - Try values between 0.5-3.0
   - Higher values = more faint detail becomes visible

3. **contrast (0-100)**: Linear contrast adjustment
   - Default: 3.0 (updated from 1.0)
   - Higher values increase overall contrast

4. **gamma (0.1-10.0)**: Nonlinear brightness curve adjustment
   - Default: 0.8 (updated from 1.0) 
   - Values > 1.0 brighten, < 1.0 darken
   - Try small adjustments between 0.6-1.2

#### Advanced Parameters (expand section if needed):
- **colorval**: Minimum value for color regions
- **grayval**: Maximum value for grayscale regions  
- **coloronly**: Checkbox to disable grayscale regions entirely

### Step 4: Generate Your First Image

1. **Click the "Generate Image" button** in the Parameter Panel (large green button)
   - Alternatively: Use F5 or Ctrl+G keyboard shortcuts
2. **Monitor progress** in the progress dialog that appears
3. **Wait for completion** - this may take a few moments depending on image size
4. **View result** - the application will automatically switch to the Preview tab

**Success**: You should now see your color image in the Preview tab with zoom and pan controls!

### Step 5: Evaluate and Refine

Look at your result in the Preview tab and consider:
- **Are bright stars well-exposed?** Adjust qbright if needed
- **Can you see faint details?** Increase stretch gradually
- **Is the overall contrast good?** Adjust contrast parameter
- **Is the overall brightness good?** Adjust gamma
- **Do colors look natural?** Check coloronly option or color/grayscale thresholds

Use mouse wheel to zoom and left-click-drag to pan around the image.

### Step 6: Advanced Parameter Tuning

For better results, try adjusting advanced parameters:

1. **Expand "Advanced Parameters"** in the parameter panel if not already open
2. **Color thresholds**:
   - **colorval**: Minimum value for color regions (try 0.1-1.0)
   - **grayval**: Maximum value for grayscale regions (try 0.01-0.1)
3. **Quality settings**:
   - **quality**: Output quality percentage (default 95)
4. **Special options**:
   - **coloronly**: Enable to eliminate grayscale regions entirely

### Step 7: Save Your Work and Use Cache

1. **Save the image**: File → Save Image (Ctrl+S) or click save icon
2. **Save parameters**: Presets → Save Current as Preset (Ctrl+Shift+S)
3. **Check cache**: Switch to the Cache Grid tab to see your automatically cached image
4. **View command**: The command used is displayed in the Parameter Panel under "Command Display"

**Cache Features**:
- All generated images are automatically cached as .tif files
- Thumbnails are created for quick browsing in the Cache Grid
- Click any cached thumbnail to view it in full size and see its parameters
- The command used to create each image is preserved

## Example Parameter Sets

Here are some starting points for different object types:

### Galaxies and Nebulae
```
qbright: 1.5
stretch: 2.0
contrast: 3.5
gamma: 0.9
colorval: 0.3
grayval: 0.05
```

### Star Fields
```
qbright: 0.8
stretch: 1.2
contrast: 2.5
gamma: 0.8
colorval: 0.5
grayval: 0.02
```

### Bright Objects (Planets, Moon)
```
qbright: 0.5
stretch: 0.8
contrast: 2.0
gamma: 0.7
colorval: 1.0
grayval: 0.1
```

## Advanced Workflows

### Comparison Workflow

1. Generate your first image with default parameters
2. Use **Tools → Add Current to Comparison** (Ctrl+M) to add it to comparison
3. Adjust parameters and generate another image
4. Add the new image to comparison
5. Switch to the **Compare tab** to evaluate differences side-by-side
6. Compare up to 4 different parameter combinations

### Cache Grid Workflow

1. Generate multiple images with different parameters
2. Switch to the **Cache Grid tab** to browse all cached images as thumbnails
3. Click any thumbnail to:
   - View the full-size image in the Preview tab
   - See the exact parameters used (displayed in Parameter Panel)
   - Copy the command that was used
4. Use cached images as starting points for further refinement

### Preset Management Workflow

1. Find parameter combinations that work well for specific object types
2. Save them using **Presets → Save Current as Preset** (Ctrl+Shift+S)
3. Manage your presets with **Presets → Manage Presets** (Ctrl+P)
4. Load saved presets when working with similar objects
5. Share preset files with other users

### Command Line Integration

1. Generate images in the GUI
2. Use the **Command Display** in the Parameter Panel to see exact commands
3. Use **Tools → Command History** (Ctrl+H) to see all previous commands
4. Copy commands with **Tools → Copy Current Command** (Ctrl+Shift+C)
5. Run commands directly in terminal: `astscript-color-faint-gray [parameters]`

## Troubleshooting Tips

### "Generation Failed"
- Check that all three input files are selected and valid
- Verify files have compatible dimensions and coordinates
- Try simpler parameter values first (use defaults)
- Check the error dialog for specific astscript messages
- Ensure `astscript-color-faint-gray` is installed and in your PATH

### "Poor Color Balance"
- Adjust colorval and grayval thresholds in Advanced Parameters
- Try enabling the "coloronly" option for different aesthetics
- Check that input channels have similar calibration and exposure times

### "Too Bright/Dark"
- Primary: Adjust gamma parameter (try 0.6-1.2 range)
- Secondary: Adjust qbright for bright regions
- Tertiary: Adjust contrast for overall linear scaling

### "Missing Faint Details"  
- Increase stretch parameter gradually
- Lower grayval to show more in grayscale
- Check that input images are properly calibrated and dark-subtracted

### "Application Won't Start"
- Ensure Python 3.8+ and PyQt6 are installed
- Check that all dependencies in requirements.txt are installed
- Verify GNU Astronomy Utilities are installed

## Best Practices

1. **Start Simple**: Begin with default parameters, make small adjustments
2. **Save Often**: Use presets to save successful parameter combinations
3. **Use Cache**: Browse the Cache Grid to compare different attempts
4. **Compare**: Use the Compare tab to evaluate different parameter approaches
5. **Document**: Keep notes about what works for different object types
6. **Backup**: Export your cache and presets periodically

## Key Features Summary

### Interface Layout
- **Parameter Panel** (left): All controls, command display, generate button
- **Image Loader Tab**: File selection and validation
- **Preview Tab**: Generated image viewing with zoom/pan
- **Cache Grid Tab**: Thumbnail browsing of all cached images  
- **Compare Tab**: Side-by-side comparison of up to 4 images

### Keyboard Shortcuts
- **F5 or Ctrl+G**: Generate image
- **Ctrl+S**: Save current image
- **Ctrl+O**: Open images dialog
- **Ctrl+P**: Manage presets
- **Ctrl+H**: Command history
- **Ctrl+Shift+C**: Copy current command
- **Ctrl+M**: Add to comparison
- **Ctrl+R**: Reset parameters

### Auto-Features
- **Auto-caching**: All generated images are automatically cached
- **Auto-thumbnails**: PNG thumbnails created for quick browsing
- **Auto-command tracking**: Every command is preserved for reproducibility
- **Auto-parameter preservation**: Parameters are saved with each cached image

## Next Steps

After mastering the basics:

1. **Explore Advanced Features**:
   - Experiment with colorval/grayval thresholds for different aesthetics
   - Use quality settings for output optimization
   - Try coloronly mode for pure color/black images

2. **Optimize Workflow**:
   - Create presets for common object types (galaxies, nebulae, star fields)
   - Use keyboard shortcuts for efficiency
   - Organize your cache with descriptive saved images

3. **Share Results**:
   - Export high-quality images from the Preview tab
   - Share parameter presets with other astronomical imagers
   - Use command history to create reproducible workflows

## Getting Help

- **Built-in Help**: Check error dialogs for specific astscript messages
- **Parameter Tooltips**: Hover over controls for parameter descriptions
- **Command Display**: See exact commands in the Parameter Panel
- **USER_MANUAL.md**: Complete reference for all features and troubleshooting

Happy imaging! 🌟

---

*This tutorial covers basic usage. For advanced techniques, complete feature reference, and detailed troubleshooting, consult USER_MANUAL.md*
