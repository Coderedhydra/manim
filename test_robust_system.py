#!/usr/bin/env python3
"""
Test script to verify the robust video generation system
"""

import requests
import time
import json

def test_robust_generation():
    """Test the robust video generation system"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Robust Video Generation System")
    print("=" * 50)
    
    # Test 1: Simple animation that should work
    print("\n📹 Test 1: Simple animation")
    prompt1 = "Create a simple animation with a red circle"
    test_generation(base_url, prompt1, "Test 1")
    
    # Test 2: More complex animation that might need error fixing
    print("\n📹 Test 2: Complex animation (may need AI error fixing)")
    prompt2 = "Create an animation showing a mathematical equation with a bouncing ball"
    test_generation(base_url, prompt2, "Test 2")
    
    print("\n🎉 Robust system testing completed!")

def test_generation(base_url, prompt, test_name):
    """Test a single generation"""
    print(f"\n{test_name}: '{prompt}'")
    
    try:
        # Start generation
        response = requests.post(f"{base_url}/generate", 
                               json={"prompt": prompt},
                               headers={"Content-Type": "application/json"})
        
        if response.status_code != 200:
            print(f"❌ Failed to start: {response.text}")
            return False
        
        data = response.json()
        job_id = data.get("job_id")
        print(f"✅ Started with job ID: {job_id}")
        
        # Poll for status with detailed logging
        max_attempts = 90  # 3 minutes max
        attempt = 0
        last_status = None
        
        while attempt < max_attempts:
            response = requests.get(f"{base_url}/status/{job_id}")
            
            if response.status_code == 404:
                print(f"❌ Job not found: {response.text}")
                return False
            
            if response.status_code != 200:
                print(f"❌ Status check failed: {response.text}")
                return False
            
            status = response.json()
            current_status = status.get('status')
            message = status.get('message', 'No message')
            progress = status.get('progress', 0)
            
            # Only print if status changed
            if current_status != last_status:
                print(f"📊 {current_status}: {message} ({progress}%)")
                last_status = current_status
            
            if current_status == 'completed':
                print(f"✅ {test_name} completed successfully!")
                print(f"🎬 Video URL: {status.get('video_url', 'N/A')}")
                return True
            elif current_status == 'error':
                print(f"❌ {test_name} failed: {message}")
                error_details = status.get('error_details', 'No details')
                print(f"🔍 Error details: {error_details[:200]}...")
                return False
            elif current_status in ['fixing_errors', 'compilation_failed']:
                print(f"🔧 AI is fixing errors: {message}")
            
            time.sleep(2)
            attempt += 1
        
        print(f"⏰ {test_name} timed out")
        return False
        
    except Exception as e:
        print(f"💥 {test_name} exception: {str(e)}")
        return False

def test_job_persistence():
    """Test that jobs persist correctly"""
    print("\n🔍 Testing job persistence...")
    
    base_url = "http://localhost:5000"
    prompt = "Create a simple blue square"
    
    # Start generation
    response = requests.post(f"{base_url}/generate", 
                           json={"prompt": prompt},
                           headers={"Content-Type": "application/json"})
    
    if response.status_code != 200:
        print(f"❌ Failed to start job: {response.text}")
        return False
    
    data = response.json()
    job_id = data.get("job_id")
    print(f"✅ Job started: {job_id}")
    
    # Wait a bit then check status
    time.sleep(1)
    
    response = requests.get(f"{base_url}/status/{job_id}")
    if response.status_code == 200:
        status = response.json()
        print(f"✅ Job found: {status.get('status')} - {status.get('message')}")
        return True
    else:
        print(f"❌ Job not found: {response.text}")
        return False

if __name__ == "__main__":
    print("🚀 Starting comprehensive system tests...")
    
    # Test job persistence first
    if not test_job_persistence():
        print("❌ Job persistence test failed!")
        exit(1)
    
    # Test robust generation
    test_robust_generation()
    
    print("\n✅ All tests completed!")