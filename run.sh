#!/bin/bash

# Text to Manim Video Generator - Start Script

echo "🎬 Starting Text to Manim Video Generator..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Please copy .env.example to .env and configure your settings:"
    echo "   cp .env.example .env"
    echo "   nano .env  # Edit with your API keys"
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg not found! Please install FFmpeg:"
    echo "   Ubuntu/Debian: sudo apt install ffmpeg"
    echo "   macOS: brew install ffmpeg"
    echo "   Windows: Download from https://ffmpeg.org/"
fi

# Check if LaTeX is installed
if ! command -v latex &> /dev/null; then
    echo "⚠️  LaTeX not found! Some animations may not work properly."
    echo "   Ubuntu/Debian: sudo apt install texlive-full"
    echo "   macOS: brew install --cask mactex"
    echo "   Windows: Install MiKTeX from https://miktex.org/"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p static/videos scripts temp

# Start the Flask application
echo "🚀 Starting Flask application..."
echo "📱 Open your browser and go to: http://localhost:5000"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

export FLASK_APP=app.py
python app.py