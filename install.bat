@echo off
REM Installation script for ColorFaintGray GUI on Windows
REM Requires Python 3.8+ and GNU Astronomy Utilities

setlocal enabledelayedexpansion

echo ======================================
echo    ColorFaintGray GUI Installer
echo ======================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Found Python %PYTHON_VERSION%

REM Check if version is 3.8+
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.8+ required, found %PYTHON_VERSION%
    pause
    exit /b 1
)

REM Check pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip not found
    pause
    exit /b 1
)

echo [SUCCESS] Python and pip found

REM Check astscript-color-faint-gray
astscript-color-faint-gray --help >nul 2>&1
if errorlevel 1 (
    echo [ERROR] astscript-color-faint-gray not found
    echo Please install GNU Astronomy Utilities:
    echo   - Download from: https://www.gnu.org/software/gnuastro/
    echo   - Or use Windows package manager
    pause
    exit /b 1
)

echo [SUCCESS] astscript-color-faint-gray found

REM Create virtual environment
echo [INFO] Creating virtual environment...
if exist venv (
    echo [WARNING] Virtual environment already exists
    set /p REPLY="Remove existing environment? (y/N): "
    if /i "!REPLY!"=="y" (
        rmdir /s /q venv
    ) else (
        echo [INFO] Using existing virtual environment
        goto skip_venv
    )
)

python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [SUCCESS] Virtual environment created

:skip_venv
REM Activate virtual environment and install dependencies
echo [INFO] Installing Python dependencies...
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install requirements
if exist requirements.txt (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install Python dependencies
        pause
        exit /b 1
    )
    echo [SUCCESS] Python dependencies installed
) else (
    echo [ERROR] requirements.txt not found
    pause
    exit /b 1
)

REM Create launcher batch file
echo [INFO] Creating launcher script...
echo @echo off > colorfaintgray.bat
echo REM ColorFaintGray GUI launcher >> colorfaintgray.bat
echo cd /d "%%~dp0" >> colorfaintgray.bat
echo call venv\Scripts\activate.bat >> colorfaintgray.bat
echo python main.py %%* >> colorfaintgray.bat

echo [SUCCESS] Launcher script created

REM Test installation
echo [INFO] Testing installation...
python main.py --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Installation test failed
    pause
    exit /b 1
)

echo [SUCCESS] Installation test passed

deactivate

echo.
echo [SUCCESS] Installation completed successfully!
echo.
echo To run the application:
echo   colorfaintgray.bat
echo.
echo Or activate the virtual environment and run directly:
echo   venv\Scripts\activate.bat
echo   python main.py
echo.

pause
