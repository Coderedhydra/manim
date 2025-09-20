# Setup Guide - Text to Manim Video Generator

This guide will help you set up the Text to Manim Video Generator on your system.

## 🚀 Quick Setup (Recommended)

### Option 1: Automated Setup Script

1. **Run the automated setup**:
   ```bash
   ./install_dependencies.sh  # Install system dependencies
   ./run.sh                   # Start the application
   ```

### Option 2: Manual Setup

Follow these steps if the automated setup doesn't work for your system.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space for dependencies

### Required Software
1. **Python 3.8+**
2. **FFmpeg** (for video processing)
3. **LaTeX** (for mathematical text rendering)
4. **Git** (for cloning the repository)

## 🔧 Step-by-Step Installation

### Step 1: Install System Dependencies

#### Ubuntu/Debian Linux
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv ffmpeg texlive-latex-base texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra build-essential cmake pkg-config
```

#### macOS (using Homebrew)
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python ffmpeg
brew install --cask mactex
```

#### Windows
1. **Python**: Download from [python.org](https://python.org)
2. **FFmpeg**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
3. **LaTeX**: Download MiKTeX from [miktex.org](https://miktex.org/download)

### Step 2: Clone and Setup Project

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd text-to-manim-generator

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit the .env file with your settings
nano .env  # or use your preferred editor
```

**Required environment variables:**
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
FLASK_SECRET_KEY=your_secret_key_here
FLASK_DEBUG=True
```

### Step 4: Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key
5. Paste it in your `.env` file

### Step 5: Test Installation

```bash
# Run the test script
python test_app.py

# If all tests pass, start the application
python app.py
```

## 🌐 Accessing the Application

Once started, open your web browser and go to:
- **Local**: http://localhost:5000
- **Network**: http://your-ip-address:5000

## 🐳 Docker Setup (Alternative)

If you prefer using Docker:

```bash
# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Build and run with Docker Compose
docker-compose up --build
```

## 🧪 Testing Your Setup

### Test 1: Run System Test
```bash
python test_app.py
```

### Test 2: Generate Demo Video
```bash
python demo_script.py
```

### Test 3: Test Web Interface
1. Start the application: `python app.py`
2. Open http://localhost:5000
3. Try generating a simple animation

## 🔍 Troubleshooting

### Common Issues and Solutions

#### "ModuleNotFoundError: No module named 'manim'"
**Solution**: Install requirements in virtual environment
```bash
source venv/bin/activate  # Activate venv first
pip install -r requirements.txt
```

#### "FFmpeg not found"
**Solution**: Install FFmpeg and ensure it's in PATH
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows: Download from ffmpeg.org and add to PATH
```

#### "LaTeX Error"
**Solution**: Install LaTeX distribution
```bash
# Ubuntu/Debian
sudo apt install texlive-full

# macOS
brew install --cask mactex

# Windows: Install MiKTeX
```

#### "Gemini API Error"
**Solutions**:
1. Check API key is correct in `.env`
2. Verify API key has proper permissions
3. Check internet connection
4. Try regenerating API key

#### "Permission Denied" on scripts
**Solution**: Make scripts executable
```bash
chmod +x run.sh install_dependencies.sh test_app.py demo_script.py
```

#### "Port 5000 already in use"
**Solution**: Change port in app.py or kill existing process
```bash
# Find process using port 5000
lsof -i :5000

# Kill process (replace PID with actual process ID)
kill -9 PID

# Or change port in app.py:
app.run(port=5001)
```

### Performance Issues

#### Slow video generation
- Use simpler animations
- Reduce video quality in app.py
- Ensure sufficient RAM/CPU
- Close other applications

#### Out of memory errors
- Reduce animation complexity
- Restart the application
- Use lower quality settings

### Getting Help

1. **Check logs**: Look at console output for detailed error messages
2. **Enable debug mode**: Set `FLASK_DEBUG=True` in `.env`
3. **Test components individually**: Use test scripts to isolate issues
4. **Check system resources**: Ensure sufficient RAM/disk space

## 📝 Configuration Options

### Video Quality Settings
Edit `app.py` to change video quality:
```python
cmd = [
    'manim', 
    '-pql',  # Change this:
             # -pql: Preview (480p, 15fps) - Fast
             # -ql:  Low (480p, 30fps) - Medium  
             # -qm:  Medium (720p, 30fps) - Slow
             # -qh:  High (1080p, 60fps) - Very Slow
    '--output_file', f'video_{job_id}',
    # ... rest of command
]
```

### Timeout Settings
Increase timeout for complex animations:
```python
result = subprocess.run(
    cmd, 
    capture_output=True, 
    text=True, 
    timeout=600,  # Increase from 300 to 600 seconds
    cwd=app.root_path
)
```

## 🎯 Next Steps

Once everything is working:

1. **Create your first video**: Try the example prompts
2. **Experiment**: Test different types of animations
3. **Customize**: Modify the AI prompts in `app.py`
4. **Deploy**: Use Docker or cloud hosting for production

## 📚 Additional Resources

- [Manim Documentation](https://docs.manim.community/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

**Need more help?** Check the main README.md file or create an issue on GitHub.