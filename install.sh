#!/bin/bash
# install.sh - Smart installation script

set -e

# Nexa Bot Installer
echo "🤖 Installing Nexa Bot..."

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
else
    echo "❌ Unsupported OS: $OSTYPE"
    exit 1
fi

echo "✓ Detected: $OS"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "📦 Installing Python 3.11..."

    if [ "$OS" == "linux" ]; then
        sudo apt update
        sudo apt install -y python3.11 python3.11-venv python3-pip
    elif [ "$OS" == "macos" ]; then
        brew install python@3.11
    fi
fi

echo "✓ Python installed"

# Create directory
INSTALL_DIR="$HOME/.nexa"
mkdir -p "$INSTALL_DIR"

# Handle source code download/location
if [ ! -f "setup.py" ]; then
    echo "📥 Downloading Nexa Bot source..."
    # In a real scenario, we would download from GitHub
    # For now, we simulate the structure
    # curl -sSL https://github.com/nexa-bot/nexa/releases/latest/download/nexa.tar.gz | tar -xz -C "$INSTALL_DIR"
    # cd "$INSTALL_DIR"
    echo "⚠️  Note: In this environment, please run the installer from the repository root."
else
    echo "✓ Source code found in current directory."
    INSTALL_SOURCE_DIR=$(pwd)
fi

# Create virtual environment
echo "🔧 Setting up environment in $INSTALL_DIR/venv..."
python3 -m venv "$INSTALL_DIR/venv"
source "$INSTALL_DIR/venv/bin/activate"

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Nexa
echo "🚀 Installing Nexa Bot package..."
if [ -n "$INSTALL_SOURCE_DIR" ]; then
    pip install -e "$INSTALL_SOURCE_DIR"
else
    pip install -e .
fi

# Create symlink
echo "🔗 Creating symlink /usr/local/bin/nexa (may require sudo)..."
if [ "$OS" != "windows" ]; then
    sudo ln -sf "$INSTALL_DIR/venv/bin/nexa" /usr/local/bin/nexa || {
        echo "⚠️  Could not create symlink in /usr/local/bin. You can run nexa from $INSTALL_DIR/venv/bin/nexa"
    }
fi

echo "✅ Installation complete!"
echo ""
echo "Run 'nexa' to start setup"
