#!/bin/bash
# Installation script for ColorFaintGray GUI
# Supports Ubuntu/Debian, CentOS/RHEL, macOS, and other Linux distributions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get >/dev/null 2>&1; then
            OS="ubuntu"
        elif command -v yum >/dev/null 2>&1; then
            OS="centos"
        elif command -v dnf >/dev/null 2>&1; then
            OS="fedora"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        OS="unknown"
    fi
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check Python version
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
            log_success "Python $PYTHON_VERSION found"
        else
            log_error "Python 3.8+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        log_error "Python 3 not found"
        exit 1
    fi
    
    # Check pip
    if command -v pip3 >/dev/null 2>&1 || command -v pip >/dev/null 2>&1; then
        log_success "pip found"
    else
        log_error "pip not found"
        exit 1
    fi
}

# Install system dependencies
install_system_deps() {
    log_info "Installing system dependencies for $OS..."
    
    case $OS in
        ubuntu)
            sudo apt-get update
            sudo apt-get install -y python3-pip python3-venv gnuastro qt6-base-dev
            ;;
        centos|fedora)
            if [[ $OS == "centos" ]]; then
                sudo yum install -y python3-pip python3-venv gnuastro qt6-qtbase-devel
            else
                sudo dnf install -y python3-pip python3-venv gnuastro qt6-qtbase-devel
            fi
            ;;
        macos)
            if command -v brew >/dev/null 2>&1; then
                brew install gnuastro qt@6
            else
                log_warning "Homebrew not found. Please install gnuastro manually"
            fi
            ;;
        *)
            log_warning "Unknown OS. Please install gnuastro manually"
            ;;
    esac
}

# Check GNU Astronomy Utilities
check_gnuastro() {
    log_info "Checking GNU Astronomy Utilities..."
    
    if command -v astscript-color-faint-gray >/dev/null 2>&1; then
        VERSION=$(astscript-color-faint-gray --version | head -n1 | grep -o '[0-9]\+\.[0-9]\+')
        log_success "astscript-color-faint-gray found (version $VERSION)"
    else
        log_error "astscript-color-faint-gray not found"
        log_info "Please install GNU Astronomy Utilities:"
        log_info "  Ubuntu/Debian: sudo apt-get install gnuastro"
        log_info "  CentOS/RHEL:   sudo yum install gnuastro"
        log_info "  macOS:         brew install gnuastro"
        log_info "  From source:   https://www.gnu.org/software/gnuastro/"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    log_info "Creating virtual environment..."
    
    if [[ -d "venv" ]]; then
        log_warning "Virtual environment already exists"
        read -p "Remove existing environment? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
        else
            log_info "Using existing virtual environment"
            return
        fi
    fi
    
    python3 -m venv venv
    log_success "Virtual environment created"
}

# Install Python dependencies
install_python_deps() {
    log_info "Installing Python dependencies..."
    
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        log_success "Python dependencies installed"
    else
        log_error "requirements.txt not found"
        exit 1
    fi
    
    deactivate
}

# Create desktop entry (Linux only)
create_desktop_entry() {
    if [[ $OS != "linux" && $OS != "ubuntu" && $OS != "centos" && $OS != "fedora" ]]; then
        return
    fi
    
    log_info "Creating desktop entry..."
    
    INSTALL_DIR=$(pwd)
    DESKTOP_FILE="$HOME/.local/share/applications/colorfaintgray.desktop"
    
    mkdir -p "$(dirname "$DESKTOP_FILE")"
    
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=ColorFaintGray GUI
Comment=Astronomical color image generation
Exec=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/main.py
Icon=$INSTALL_DIR/resources/icon.png
Terminal=false
Categories=Science;Astronomy;
StartupNotify=true
EOF
    
    chmod +x "$DESKTOP_FILE"
    log_success "Desktop entry created"
}

# Create launcher script
create_launcher() {
    log_info "Creating launcher script..."
    
    cat > colorfaintgray << 'EOF'
#!/bin/bash
# ColorFaintGray GUI launcher script

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment and run application
source "$SCRIPT_DIR/venv/bin/activate"
cd "$SCRIPT_DIR"
python main.py "$@"
EOF
    
    chmod +x colorfaintgray
    log_success "Launcher script created"
}

# Test installation
test_installation() {
    log_info "Testing installation..."
    
    source venv/bin/activate
    if python main.py --version >/dev/null 2>&1; then
        log_success "Installation test passed"
    else
        log_error "Installation test failed"
        exit 1
    fi
    deactivate
}

# Main installation function
main() {
    echo "======================================"
    echo "   ColorFaintGray GUI Installer"
    echo "======================================"
    echo
    
    detect_os
    log_info "Detected OS: $OS"
    
    check_requirements
    
    # Ask for system dependency installation
    read -p "Install system dependencies? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        install_system_deps
    fi
    
    check_gnuastro
    create_venv
    install_python_deps
    create_launcher
    
    if [[ $OS == "linux" || $OS == "ubuntu" || $OS == "centos" || $OS == "fedora" ]]; then
        read -p "Create desktop entry? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            create_desktop_entry
        fi
    fi
    
    test_installation
    
    echo
    log_success "Installation completed successfully!"
    echo
    log_info "To run the application:"
    log_info "  ./colorfaintgray"
    echo
    log_info "Or activate the virtual environment and run directly:"
    log_info "  source venv/bin/activate"
    log_info "  python main.py"
    echo
}

# Run main function
main "$@"
