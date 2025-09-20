# Text to Manim Video Generator

A powerful web application that transforms text descriptions into beautiful mathematical animations using AI-powered script generation and Manim rendering.

## 🌟 Features

- **AI-Powered Script Generation**: Uses Google's Gemini AI to generate Manim scripts from natural language descriptions
- **Modern Web Interface**: Beautiful, responsive UI with real-time progress tracking
- **Automatic Video Compilation**: Seamlessly compiles and renders Manim animations
- **Error Handling**: Robust error handling with helpful feedback
- **Script Display**: View and copy the generated Manim Python code
- **Example Prompts**: Built-in examples to get you started
- **Real-time Progress**: Live updates during video generation process

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for video processing)
- LaTeX distribution (for mathematical text rendering)
- Google Gemini API key

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd text-to-manim-generator
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install system dependencies**:

   **Ubuntu/Debian**:
   ```bash
   sudo apt update
   sudo apt install ffmpeg texlive-full
   ```

   **macOS** (using Homebrew):
   ```bash
   brew install ffmpeg
   brew install --cask mactex
   ```

   **Windows**:
   - Download and install FFmpeg from https://ffmpeg.org/download.html
   - Download and install MiKTeX from https://miktex.org/download

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your configuration:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   FLASK_SECRET_KEY=your_secret_key_here
   FLASK_DEBUG=True
   ```

5. **Get a Gemini API key**:
   - Go to [Google AI Studio](https://aistudio.google.com/)
   - Create a new API key
   - Add it to your `.env` file

### Running the Application

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## 📖 Usage

1. **Enter your description**: Type what kind of animation you want to create
2. **Generate video**: Click "Generate Video" to start the process
3. **Watch progress**: Monitor real-time progress updates
4. **View results**: Watch your generated video and copy the script
5. **Create more**: Generate as many videos as you want!

### Example Prompts

- "Create an animation showing the Pythagorean theorem with a right triangle"
- "Animate a simple pendulum swinging back and forth"
- "Show how a circle transforms into a square"
- "Create a visualization of the quadratic formula"
- "Animate text that says 'Hello Manim!' with colorful effects"

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Your Google Gemini API key | Required |
| `FLASK_SECRET_KEY` | Flask session secret key | Required |
| `FLASK_DEBUG` | Enable debug mode | `False` |

### Manim Settings

The application uses Manim's preview quality (`-pql`) for faster generation. You can modify the quality settings in `app.py`:

- `-pql`: Preview quality (480p, 15fps) - Fast
- `-ql`: Low quality (480p, 30fps) - Medium
- `-qm`: Medium quality (720p, 30fps) - Slow
- `-qh`: High quality (1080p, 60fps) - Very slow

## 📁 Project Structure

```
text-to-manim-generator/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
├── static/
│   ├── css/
│   │   └── style.css     # Application styles
│   ├── js/
│   │   └── app.js        # Frontend JavaScript
│   └── videos/           # Generated videos (auto-created)
├── templates/
│   └── index.html        # Main HTML template
├── scripts/              # Generated Manim scripts (auto-created)
└── temp/                 # Temporary files (auto-created)
```

## 🔧 API Endpoints

### `POST /generate`
Start video generation process.

**Request Body**:
```json
{
  "prompt": "Your animation description"
}
```

**Response**:
```json
{
  "job_id": "unique-job-identifier",
  "message": "Video generation started"
}
```

### `GET /status/<job_id>`
Get generation status.

**Response**:
```json
{
  "status": "completed|generating_script|compiling|error",
  "message": "Status message",
  "progress": 75,
  "video_url": "/static/videos/video_id.mp4",
  "script": "Generated Manim script"
}
```

### `GET /examples`
Get example prompts.

**Response**:
```json
[
  "Example prompt 1",
  "Example prompt 2",
  ...
]
```

## 🎨 Customization

### Modifying the AI Prompt

Edit the `system_prompt` in the `generate_manim_script` method in `app.py` to customize how the AI generates scripts:

```python
system_prompt = """Your custom instructions here..."""
```

### Styling the Interface

Modify `static/css/style.css` to customize the appearance of the web interface.

### Adding New Features

The modular structure makes it easy to add new features:
- Add new endpoints in `app.py`
- Extend the frontend in `static/js/app.js`
- Add new UI components in `templates/index.html`

## 🐛 Troubleshooting

### Common Issues

1. **"No module named 'manim'"**:
   - Ensure you've installed all requirements: `pip install -r requirements.txt`

2. **"FFmpeg not found"**:
   - Install FFmpeg using your system's package manager
   - Ensure FFmpeg is in your PATH

3. **"LaTeX not found"**:
   - Install a LaTeX distribution (TeX Live, MiKTeX, etc.)
   - Some mathematical animations require LaTeX

4. **"Gemini API key not found"**:
   - Ensure your `.env` file exists and contains your API key
   - Verify the API key is correct and has proper permissions

5. **Video generation timeout**:
   - Complex animations may take longer than the 5-minute timeout
   - Try simpler descriptions or increase the timeout in `app.py`

### Debug Mode

Enable debug mode by setting `FLASK_DEBUG=True` in your `.env` file for detailed error messages.

### Logs

Check the console output for detailed logs about the generation process.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Manim Community](https://www.manim.community/) for the amazing animation library
- [Google AI](https://ai.google.dev/) for the Gemini API
- [Flask](https://flask.palletsprojects.com/) for the web framework

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Search existing issues on GitHub
3. Create a new issue with detailed information about your problem

---

**Happy animating!** 🎬✨