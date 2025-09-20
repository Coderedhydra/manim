import os
import uuid
import subprocess
import json
import time
import threading
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
        self.job_lock = {}  # To prevent concurrent access to same job
    
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
    
    def compile_manim_script_safe(self, script_content, job_id, attempt=0):
        """Safely compile Manim script and generate video"""
        try:
            # Create unique filename
            script_filename = f"scene_{job_id}_attempt_{attempt}.py"
            script_path = os.path.join(SCRIPTS_DIR, script_filename)
            
            # Write script to file
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Extract scene class name from script
            scene_class = self.extract_scene_class(script_content)
            if not scene_class:
                raise Exception("No valid Scene class found in generated script. The script must contain a class that inherits from Scene.")
            
            # Run Manim command
            output_dir = os.path.join(TEMP_DIR, f"{job_id}_attempt_{attempt}")
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
                error_details = f"Exit code: {result.returncode}\n\nStdout:\n{result.stdout}\n\nStderr:\n{result.stderr}"
                logger.error(f"Manim compilation failed: {error_details}")
                raise Exception(f"Manim compilation failed:\n{error_details}")
            
            # Find generated video file
            video_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(('.mp4', '.mov', '.avi')):
                        video_files.append(os.path.join(root, file))
            
            if not video_files:
                raise Exception("No video file was generated. The Manim script may not have produced any output.")
            
            # Move video to static directory
            source_video = video_files[0]
            final_video_path = os.path.join(VIDEOS_DIR, f'video_{job_id}.mp4')
            
            # Ensure the directory exists
            os.makedirs(VIDEOS_DIR, exist_ok=True)
            
            # Copy instead of move to avoid cross-device link issues
            shutil.copy2(source_video, final_video_path)
            
            # Cleanup temp directory
            shutil.rmtree(output_dir, ignore_errors=True)
            
            return f'video_{job_id}.mp4'
            
        except subprocess.TimeoutExpired:
            raise Exception("Video generation timed out after 5 minutes. Please try with a simpler animation.")
        except Exception as e:
            logger.error(f"Error in compile_manim_script_safe: {str(e)}")
            raise e
    
    def update_job_status(self, job_id, status, message, progress, **kwargs):
        """Update job status safely"""
        if job_id not in self.generation_status:
            self.generation_status[job_id] = {}
            logger.info(f"Creating new job status for {job_id}")
        
        self.generation_status[job_id].update({
            'status': status,
            'message': message,
            'progress': progress,
            'timestamp': time.time(),
            **kwargs
        })
        logger.info(f"Job {job_id} status updated: {status} - {message} ({progress}%) - Total jobs: {len(self.generation_status)}")

    def generate_video_async(self, user_prompt, job_id):
        """Generate video asynchronously with robust error handling"""
        logger.info(f"Starting async generation for job {job_id}")
        max_retries = 3
        current_script = None
        
        try:
            # Lock this job
            self.job_lock[job_id] = True
            logger.info(f"Job {job_id} locked and starting processing")
            
            # Initialize status
            self.update_job_status(job_id, 'initializing', 'Starting video generation...', 10)
            
            for attempt in range(max_retries):
                try:
                    # Generate or regenerate script
                    self.update_job_status(job_id, 'generating_script', 
                                         f'Generating Manim script... (attempt {attempt + 1})', 
                                         20 + (attempt * 5))
                    
                    if attempt == 0:
                        # First attempt - generate new script
                        current_script = self.generate_manim_script(user_prompt)
                    else:
                        # Retry attempts - ask AI to fix errors
                        error_info = self.generation_status[job_id].get('last_error', 'Unknown compilation error')
                        self.update_job_status(job_id, 'fixing_errors', 
                                             f'AI is fixing compilation errors... (attempt {attempt + 1})', 
                                             25 + (attempt * 5))
                        current_script = self.generate_manim_script(user_prompt, fix_errors=error_info)
                    
                    # Update status with script
                    self.update_job_status(job_id, 'compiling', 
                                         f'Compiling video... (attempt {attempt + 1})', 
                                         40 + (attempt * 10), 
                                         script=current_script)
                    
                    # Try to compile
                    video_filename = self.compile_manim_script_safe(current_script, job_id, attempt)
                    
                    # Success!
                    video_url = f'/static/videos/{video_filename}'
                    self.update_job_status(job_id, 'completed', 
                                         'Video generated successfully!', 
                                         100,
                                         video_url=video_url,
                                         script=current_script,
                                         final_script=current_script)
                    return
                    
                except Exception as compile_error:
                    error_msg = str(compile_error)
                    logger.error(f"Compilation attempt {attempt + 1} failed for job {job_id}: {error_msg}")
                    
                    # Store error for next attempt
                    self.update_job_status(job_id, 'compilation_failed', 
                                         f'Compilation failed (attempt {attempt + 1}): {error_msg[:100]}...', 
                                         30 + (attempt * 15),
                                         last_error=error_msg,
                                         script=current_script)
                    
                    if attempt == max_retries - 1:
                        # Final failure
                        raise Exception(f"Failed to generate video after {max_retries} attempts. Last error: {error_msg}")
                    
                    # Wait a bit before retry
                    time.sleep(1)
            
        except Exception as e:
            logger.error(f"Video generation completely failed for job {job_id}: {str(e)}")
            self.update_job_status(job_id, 'error', 
                                 f'Generation failed: {str(e)}', 
                                 0,
                                 error_details=str(e),
                                 script=current_script)
        finally:
            # Release lock
            if job_id in self.job_lock:
                del self.job_lock[job_id]
    
    def cleanup_old_jobs(self):
        """Clean up jobs older than 1 hour"""
        current_time = time.time()
        jobs_to_remove = []
        
        for job_id, status in self.generation_status.items():
            job_time = status.get('timestamp', 0)
            if current_time - job_time > 3600:  # 1 hour
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            logger.info(f"Cleaning up old job: {job_id}")
            del self.generation_status[job_id]

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
        
        # Initialize the job status immediately
        video_generator.update_job_status(job_id, 'queued', 'Job queued for processing...', 5)
        
        # Start async generation with error handling wrapper
        def safe_async_wrapper():
            try:
                with app.app_context():
                    video_generator.generate_video_async(user_prompt, job_id)
            except Exception as e:
                logger.error(f"Async thread failed for job {job_id}: {str(e)}")
                video_generator.update_job_status(job_id, 'error', f'Thread error: {str(e)}', 0)
        
        thread = threading.Thread(target=safe_async_wrapper)
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
    # Clean up old jobs periodically
    video_generator.cleanup_old_jobs()
    
    if job_id in video_generator.generation_status:
        status = video_generator.generation_status[job_id]
        logger.info(f"Status for job {job_id}: {status.get('status', 'unknown')} - {status.get('message', 'no message')}")
        return jsonify(status)
    else:
        logger.warning(f"Job {job_id} not found in generation_status. Available jobs: {list(video_generator.generation_status.keys())}")
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

@app.route('/debug/jobs')
def debug_jobs():
    """Debug endpoint to see current jobs"""
    if not os.getenv('FLASK_DEBUG', 'False').lower() == 'true':
        return jsonify({'error': 'Debug mode not enabled'}), 403
    
    jobs_info = {}
    for job_id, status in video_generator.generation_status.items():
        jobs_info[job_id] = {
            'status': status.get('status', 'unknown'),
            'message': status.get('message', 'no message'),
            'progress': status.get('progress', 0),
            'timestamp': status.get('timestamp', 0),
            'age_seconds': time.time() - status.get('timestamp', time.time())
        }
    
    return jsonify({
        'total_jobs': len(jobs_info),
        'jobs': jobs_info,
        'locks': list(video_generator.job_lock.keys())
    })

if __name__ == '__main__':
    # Disable auto-reload to prevent losing job status when script files are created
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true', 
            use_reloader=False, 
            host='0.0.0.0', 
            port=5000)