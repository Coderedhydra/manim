#!/bin/bash

# Text to Manim Video Generator - Dependency Installation Script

echo "🔧 Installing system dependencies for Text to Manim Video Generator..."

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "🐧 Detected Linux system"
    
    # Update package list
    echo "📦 Updating package list..."
    sudo apt update
    
    # Install FFmpeg
    echo "🎥 Installing FFmpeg..."
    sudo apt install -y ffmpeg
    
    # Install LaTeX
    echo "📄 Installing LaTeX (this may take a while)..."
    sudo apt install -y texlive-latex-base texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra
    
    # Install Python development headers
    echo "🐍 Installing Python development headers..."
    sudo apt install -y python3-dev python3-pip python3-venv
    
    # Install additional system dependencies
    echo "🔧 Installing additional dependencies..."
    sudo apt install -y build-essential cmake pkg-config
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "🍎 Detected macOS system"
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "🍺 Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install FFmpeg
    echo "🎥 Installing FFmpeg..."
    brew install ffmpeg
    
    # Install LaTeX
    echo "📄 Installing LaTeX..."
    brew install --cask mactex
    
    # Install Python if needed
    echo "🐍 Installing Python..."
    brew install python
    
else
    echo "❌ Unsupported operating system: $OSTYPE"
    echo "Please install the following manually:"
    echo "  - FFmpeg"
    echo "  - LaTeX distribution"
    echo "  - Python 3.8+"
    exit 1
fi

echo "✅ System dependencies installed successfully!"
echo "🚀 Run './run.sh' to start the application"