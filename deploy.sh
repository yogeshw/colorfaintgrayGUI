#!/bin/bash
# Deployment script for ColorFaintGray GUI
# Creates distribution packages for multiple platforms

set -e

VERSION="1.0.0"
APP_NAME="colorfaintgray"
BUILD_DIR="dist"

log_info() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

log_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

log_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

# Clean previous builds
clean_build() {
    log_info "Cleaning previous builds..."
    rm -rf "$BUILD_DIR"
    rm -rf build
    rm -rf *.spec
    mkdir -p "$BUILD_DIR"
}

# Create source distribution
create_source_dist() {
    log_info "Creating source distribution..."
    
    DIST_NAME="${APP_NAME}-${VERSION}-source"
    DIST_DIR="$BUILD_DIR/$DIST_NAME"
    
    mkdir -p "$DIST_DIR"
    
    # Copy source files
    cp -r core gui utils *.py *.md *.txt *.sh *.bat "$DIST_DIR/"
    
    # Create README for distribution
    cat > "$DIST_DIR/README_DIST.txt" << EOF
ColorFaintGray GUI v${VERSION}
=============================

Installation:
1. Run the appropriate installer for your platform:
   - Linux/macOS: ./install.sh
   - Windows: install.bat

2. Or install manually:
   - Install Python 3.8+
   - Install GNU Astronomy Utilities
   - pip install -r requirements.txt
   - python main.py

For detailed instructions, see README.md and USER_MANUAL.md
EOF
    
    # Create archive
    cd "$BUILD_DIR"
    tar -czf "${DIST_NAME}.tar.gz" "$DIST_NAME"
    zip -r "${DIST_NAME}.zip" "$DIST_NAME"
    cd ..
    
    log_success "Source distribution created"
}

# Create PyInstaller executable (if available)
create_executable() {
    if ! command -v pyinstaller >/dev/null 2>&1; then
        log_info "PyInstaller not found, skipping executable creation"
        return
    fi
    
    log_info "Creating standalone executable..."
    
    # Create PyInstaller spec
    cat > "${APP_NAME}.spec" << EOF
# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get source directory
src_dir = Path.cwd()

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[str(src_dir)],
    binaries=[],
    datas=[
        ('gui', 'gui'),
        ('core', 'core'),  
        ('utils', 'utils'),
        ('*.md', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'astropy',
        'numpy',
        'PIL',
        'matplotlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='${APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='${APP_NAME}',
)
EOF
    
    # Build executable
    pyinstaller "${APP_NAME}.spec" --distpath "$BUILD_DIR" --clean
    
    # Create archive
    cd "$BUILD_DIR"
    PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    EXEC_NAME="${APP_NAME}-${VERSION}-${PLATFORM}-${ARCH}"
    
    mv "$APP_NAME" "$EXEC_NAME"
    tar -czf "${EXEC_NAME}.tar.gz" "$EXEC_NAME"
    cd ..
    
    log_success "Executable created"
}

# Create Docker image
create_docker_image() {
    if ! command -v docker >/dev/null 2>&1; then
        log_info "Docker not found, skipping Docker image creation"
        return
    fi
    
    log_info "Creating Docker image..."
    
    # Create Dockerfile
    cat > Dockerfile << EOF
FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    python3 \\
    python3-pip \\
    python3-venv \\
    gnuastro \\
    qt6-base-dev \\
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy application files
COPY requirements.txt .
COPY main.py .
COPY core/ core/
COPY gui/ gui/
COPY utils/ utils/
COPY *.md .

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Create non-root user
RUN useradd -m -u 1000 astrouser
USER astrouser

# Set display environment for GUI
ENV DISPLAY=:0

# Expose volume for data
VOLUME ["/data"]

# Run application
CMD ["python3", "main.py"]
EOF
    
    # Build image
    docker build -t "${APP_NAME}:${VERSION}" .
    docker tag "${APP_NAME}:${VERSION}" "${APP_NAME}:latest"
    
    # Save image
    docker save "${APP_NAME}:${VERSION}" | gzip > "$BUILD_DIR/${APP_NAME}-${VERSION}-docker.tar.gz"
    
    log_success "Docker image created"
}

# Create documentation package
create_docs() {
    log_info "Creating documentation package..."
    
    DOCS_DIR="$BUILD_DIR/${APP_NAME}-${VERSION}-docs"
    mkdir -p "$DOCS_DIR"
    
    # Copy documentation
    cp README.md USER_MANUAL.md TASKS.md "$DOCS_DIR/"
    
    # Create additional docs
    cat > "$DOCS_DIR/INSTALLATION.md" << EOF
# Installation Guide

## Quick Start

### Linux/macOS
\`\`\`bash
./install.sh
\`\`\`

### Windows
\`\`\`cmd
install.bat
\`\`\`

## Manual Installation

### Prerequisites
- Python 3.8+
- GNU Astronomy Utilities
- Qt6 libraries

### Steps
1. Install system dependencies
2. Create virtual environment: \`python -m venv venv\`
3. Activate environment: \`source venv/bin/activate\` (Linux/macOS) or \`venv\\Scripts\\activate\` (Windows)
4. Install packages: \`pip install -r requirements.txt\`
5. Run application: \`python main.py\`

## Verification
Test installation with: \`python main.py --help\`

For detailed information, see USER_MANUAL.md
EOF
    
    # Create archive
    cd "$BUILD_DIR"
    tar -czf "${APP_NAME}-${VERSION}-docs.tar.gz" "${APP_NAME}-${VERSION}-docs"
    cd ..
    
    log_success "Documentation package created"
}

# Generate checksums
generate_checksums() {
    log_info "Generating checksums..."
    
    cd "$BUILD_DIR"
    
    # Generate SHA256 checksums
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum *.tar.gz *.zip > checksums.sha256
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 *.tar.gz *.zip > checksums.sha256
    fi
    
    cd ..
    log_success "Checksums generated"
}

# Main deployment function
main() {
    echo "======================================"
    echo "   ColorFaintGray GUI Deployment"
    echo "======================================"
    echo
    
    clean_build
    create_source_dist
    create_executable
    create_docker_image
    create_docs
    generate_checksums
    
    echo
    log_success "Deployment completed!"
    echo
    log_info "Distribution files created in: $BUILD_DIR"
    echo
    ls -la "$BUILD_DIR"
    echo
}

# Run main function
main "$@"
