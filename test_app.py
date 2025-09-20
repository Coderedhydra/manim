#!/usr/bin/env python3
"""
Test script for the Text to Manim Video Generator
"""

import os
import sys
import subprocess
import time
from dotenv import load_dotenv

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python packages
    try:
        import flask
        import google.generativeai
        print("✅ Flask and Google AI packages installed")
    except ImportError as e:
        print(f"❌ Missing Python package: {e}")
        return False
    
    # Check FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg is installed")
        else:
            print("❌ FFmpeg not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ FFmpeg not found")
        return False
    
    # Check LaTeX (optional)
    try:
        result = subprocess.run(['latex', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ LaTeX is installed")
        else:
            print("⚠️  LaTeX not working (some animations may fail)")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  LaTeX not found (some animations may fail)")
    
    return True

def check_environment():
    """Check environment configuration"""
    print("\n🔧 Checking environment configuration...")
    
    # Load environment variables
    load_dotenv()
    
    # Check Gemini API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        print("   Please set your Gemini API key in .env file")
        return False
    elif api_key == 'your_gemini_api_key_here':
        print("❌ Please replace the placeholder with your actual Gemini API key")
        return False
    else:
        print("✅ Gemini API key configured")
    
    # Check Flask secret key
    secret_key = os.getenv('FLASK_SECRET_KEY')
    if not secret_key or secret_key == 'your_secret_key_here':
        print("⚠️  Flask secret key not configured (using default)")
    else:
        print("✅ Flask secret key configured")
    
    return True

def test_manim_installation():
    """Test if Manim is properly installed"""
    print("\n🎬 Testing Manim installation...")
    
    # Create a simple test script
    test_script = '''
from manim import *

class TestScene(Scene):
    def construct(self):
        text = Text("Test")
        self.add(text)
'''
    
    # Write test script
    test_file = 'test_manim.py'
    try:
        with open(test_file, 'w') as f:
            f.write(test_script)
        
        # Try to run Manim
        cmd = ['manim', '-pql', '--dry_run', test_file, 'TestScene']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Manim is working properly")
            return True
        else:
            print(f"❌ Manim test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Manim test error: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)

def test_gemini_api():
    """Test Gemini API connection"""
    print("\n🤖 Testing Gemini API connection...")
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ No API key to test")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Simple test
        response = model.generate_content("Say 'API test successful'")
        
        if response and response.text:
            print("✅ Gemini API is working")
            return True
        else:
            print("❌ Gemini API test failed - no response")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Text to Manim Video Generator - System Test")
    print("=" * 50)
    
    all_good = True
    
    # Run all checks
    if not check_dependencies():
        all_good = False
    
    if not check_environment():
        all_good = False
    
    if not test_manim_installation():
        all_good = False
    
    if not test_gemini_api():
        all_good = False
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 All tests passed! Your system is ready.")
        print("🚀 Run './run.sh' to start the application")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        print("📖 See README.md for troubleshooting help")
        sys.exit(1)

if __name__ == "__main__":
    main()