import os
import uuid
import subprocess
import json
import time
from flask import Flask, render_template, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename
import google.generativeai as genai
from dotenv import load_dotenv
import logging
import shutil

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')

# Directories
SCRIPTS_DIR = os.path.join(app.root_path, 'scripts')
VIDEOS_DIR = os.path.join(app.root_path, 'static', 'videos')
TEMP_DIR = os.path.join(app.root_path, 'temp')

# Ensure directories exist
os.makedirs(SCRIPTS_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

class VideoGenerator:
    def __init__(self):
        self.generation_status = {}
    
    def generate_manim_script(self, user_prompt, fix_errors=None):
        """Generate Manim script using Gemini AI with optimized prompts"""
        
        if fix_errors:
            system_prompt = f"""You are an expert Manim developer. The previous script had compilation errors.
            Please fix the following errors and generate a corrected Manim script:
            
            ERRORS TO FIX:
            {fix_errors}
            
            REQUIREMENTS:
            1. Always import: from manim import *
            2. Create a class that inherits from Scene
            3. Implement the construct method
            4. Fix all syntax and runtime errors
            5. Use proper Manim syntax and objects
            6. Ensure the code compiles and runs successfully
            7. Keep animations simple but functional
            
            Generate ONLY the corrected Python code, no explanations."""
        else:
            system_prompt = """You are an expert Manim (Mathematical Animation Engine) developer. 
            Generate clean, working Python code using Manim that creates educational animations.
            
            CRITICAL REQUIREMENTS:
            1. Always import: from manim import *
            2. Create a class that inherits from Scene
            3. Implement the construct method
            4. Use proper Manim syntax and objects (Text, MathTex, Circle, Square, etc.)
            5. Add appropriate animations (Create, Transform, Write, FadeIn, FadeOut, etc.)
            6. Keep animations simple but engaging
            7. Use self.play() for animations and self.wait() for pauses
            8. Ensure the code is syntactically correct
            9. Use appropriate colors and positioning
            10. Make sure all imports and class definitions are complete
            
            AVOID:
            - Complex mathematical formulas unless specifically requested
            - External file dependencies
            - User input during animation
            - Overly complex animations that might fail
            - Using deprecated Manim syntax
            - Undefined variables or functions
            
            Generate ONLY the Python code, no explanations or markdown formatting.
            """
        
        full_prompt = f"{system_prompt}\n\nUser Request: {user_prompt}\n\nGenerate a complete Manim script:"
        
        try:
            response = model.generate_content(full_prompt)
            script_content = response.text.strip()
            
            # Clean up the response - remove markdown formatting if present
            if script_content.startswith('```python'):
                script_content = script_content[9:]
            if script_content.startswith('```'):
                script_content = script_content[3:]
            if script_content.endswith('```'):
                script_content = script_content[:-3]
            
            return script_content.strip()
            
        except Exception as e:
            logger.error(f"Error generating script: {str(e)}")
            raise Exception(f"Failed to generate script: {str(e)}")
    
    def compile_manim_script(self, script_content, job_id, user_prompt, retry_count=0):
        """Compile Manim script and generate video with error fixing"""
        max_retries = 2
        
        try:
            # Create unique filename
            script_filename = f"scene_{job_id}_{retry_count}.py"
            script_path = os.path.join(SCRIPTS_DIR, script_filename)
            
            # Write script to file
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Extract scene class name from script
            scene_class = self.extract_scene_class(script_content)
            if not scene_class:
                raise Exception("No valid Scene class found in generated script")
            
            # Run Manim command
            output_dir = os.path.join(TEMP_DIR, job_id)
            os.makedirs(output_dir, exist_ok=True)
            
            cmd = [
                'manim', 
                '-pql',  # Preview quality, low resolution for faster generation
                '--output_file', f'video_{job_id}',
                '--media_dir', output_dir,
                script_path, 
                scene_class
            ]
            
            logger.info(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300,  # 5 minute timeout
                cwd=app.root_path
            )
            
            if result.returncode != 0:
                error_details = f"Stdout: {result.stdout}\nStderr: {result.stderr}"
                logger.error(f"Manim compilation failed: {error_details}")
                
                # Try to fix the errors with AI if we haven't exceeded retry limit
                if retry_count < max_retries:
                    logger.info(f"Attempting to fix errors (retry {retry_count + 1}/{max_retries})")
                    
                    # Update status
                    if job_id in self.generation_status:
                        self.generation_status[job_id]['message'] = f'Fixing compilation errors (attempt {retry_count + 1})'
                        self.generation_status[job_id]['progress'] = 40 + (retry_count * 10)
                    
                    # Generate fixed script
                    fixed_script = self.generate_manim_script(user_prompt, fix_errors=error_details)
                    
                    # Retry compilation with fixed script
                    return self.compile_manim_script(fixed_script, job_id, user_prompt, retry_count + 1)
                else:
                    raise Exception(f"Manim compilation failed after {max_retries} attempts:\n{error_details}")
            
            # Find generated video file
            video_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(('.mp4', '.mov', '.avi')):
                        video_files.append(os.path.join(root, file))
            
            if not video_files:
                raise Exception("No video file was generated")
            
            # Move video to static directory
            source_video = video_files[0]
            final_video_path = os.path.join(VIDEOS_DIR, f'video_{job_id}.mp4')
            shutil.move(source_video, final_video_path)
            
            # Cleanup temp directory
            shutil.rmtree(output_dir, ignore_errors=True)
            
            return f'video_{job_id}.mp4'
            
        except subprocess.TimeoutExpired:
            raise Exception("Video generation timed out. Please try with a simpler animation.")
        except Exception as e:
            if "No valid Scene class found" in str(e) and retry_count < max_retries:
                logger.info(f"Attempting to fix scene class issue (retry {retry_count + 1}/{max_retries})")
                
                # Update status
                if job_id in self.generation_status:
                    self.generation_status[job_id]['message'] = f'Fixing script structure (attempt {retry_count + 1})'
                    self.generation_status[job_id]['progress'] = 40 + (retry_count * 10)
                
                # Generate fixed script
                fixed_script = self.generate_manim_script(user_prompt, fix_errors=str(e))
                
                # Retry compilation with fixed script
                return self.compile_manim_script(fixed_script, job_id, user_prompt, retry_count + 1)
            
            logger.error(f"Error compiling script: {str(e)}")
            raise Exception(f"Failed to compile video: {str(e)}")
    
    def extract_scene_class(self, script_content):
        """Extract the Scene class name from the script"""
        lines = script_content.split('\n')
        for line in lines:
            if 'class ' in line and 'Scene' in line:
                # Extract class name
                parts = line.strip().split()
                if len(parts) >= 2:
                    class_name = parts[1].split('(')[0].rstrip(':')
                    return class_name
        return None
    
    def generate_video_async(self, user_prompt, job_id):
        """Generate video asynchronously"""
        try:
            # Initialize status
            self.generation_status[job_id] = {
                'status': 'generating_script',
                'message': 'Generating Manim script...',
                'progress': 25
            }
            
            # Generate script
            script_content = self.generate_manim_script(user_prompt)
            
            # Update status
            self.generation_status[job_id] = {
                'status': 'compiling',
                'message': 'Compiling video...',
                'progress': 50,
                'script': script_content
            }
            
            # Compile video with retry capability
            video_filename = self.compile_manim_script(script_content, job_id, user_prompt)
            
            # Final success status
            self.generation_status[job_id] = {
                'status': 'completed',
                'message': 'Video generated successfully!',
                'progress': 100,
                'video_url': url_for('static', filename=f'videos/{video_filename}'),
                'script': script_content
            }
            
        except Exception as e:
            logger.error(f"Video generation failed for job {job_id}: {str(e)}")
            self.generation_status[job_id] = {
                'status': 'error',
                'message': str(e),
                'progress': 0,
                'error_details': str(e)
            }

# Initialize video generator
video_generator = VideoGenerator()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_video():
    """Start video generation process"""
    try:
        data = request.get_json()
        user_prompt = data.get('prompt', '').strip()
        
        if not user_prompt:
            return jsonify({'error': 'Please provide a description for your video'}), 400
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Start async generation
        import threading
        thread = threading.Thread(
            target=video_generator.generate_video_async,
            args=(user_prompt, job_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'message': 'Video generation started'
        })
        
    except Exception as e:
        logger.error(f"Error starting video generation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/status/<job_id>')
def get_status(job_id):
    """Get generation status"""
    if job_id in video_generator.generation_status:
        status = video_generator.generation_status[job_id]
        logger.info(f"Status for job {job_id}: {status}")
        return jsonify(status)
    else:
        logger.warning(f"Job {job_id} not found in generation_status")
        # Return a more informative response
        return jsonify({
            'status': 'not_found',
            'message': 'Job not found. The job may have expired or never existed.',
            'progress': 0,
            'error_details': f'Job ID {job_id} was not found in the system. Please try generating a new video.'
        }), 404

@app.route('/examples')
def get_examples():
    """Get example prompts"""
    examples = [
        "Create an animation showing the Pythagorean theorem with a right triangle",
        "Animate a simple pendulum swinging back and forth",
        "Show how a circle transforms into a square",
        "Create a visualization of the quadratic formula",
        "Animate text that says 'Hello Manim!' with colorful effects",
        "Show a bouncing ball with physics",
        "Create a simple bar chart animation",
        "Animate a sine wave being drawn",
        "Show geometric shapes morphing into each other",
        "Create a simple introduction animation with your name"
    ]
    return jsonify(examples)

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true', host='0.0.0.0', port=5000)