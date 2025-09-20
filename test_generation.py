#!/usr/bin/env python3
"""
Test script to verify video generation is working
"""

import requests
import time
import json

def test_video_generation():
    """Test the video generation API"""
    base_url = "http://localhost:5000"
    
    # Test prompt
    prompt = "Create a simple animation with a red circle moving from left to right"
    
    print(f"🧪 Testing video generation with prompt: '{prompt}'")
    
    # Start generation
    response = requests.post(f"{base_url}/generate", 
                           json={"prompt": prompt},
                           headers={"Content-Type": "application/json"})
    
    if response.status_code != 200:
        print(f"❌ Failed to start generation: {response.text}")
        return False
    
    data = response.json()
    job_id = data.get("job_id")
    
    if not job_id:
        print("❌ No job ID returned")
        return False
    
    print(f"✅ Generation started with job ID: {job_id}")
    
    # Poll for status
    max_attempts = 60  # 2 minutes max
    attempt = 0
    
    while attempt < max_attempts:
        response = requests.get(f"{base_url}/status/{job_id}")
        
        if response.status_code == 404:
            print("❌ Job not found")
            return False
        
        if response.status_code != 200:
            print(f"❌ Status check failed: {response.text}")
            return False
        
        status = response.json()
        print(f"📊 Status: {status.get('message', 'Unknown')} ({status.get('progress', 0)}%)")
        
        if status.get('status') == 'completed':
            print(f"✅ Video generation completed!")
            print(f"🎬 Video URL: {status.get('video_url', 'N/A')}")
            return True
        elif status.get('status') == 'error':
            print(f"❌ Generation failed: {status.get('message', 'Unknown error')}")
            return False
        
        time.sleep(2)
        attempt += 1
    
    print("❌ Generation timed out")
    return False

if __name__ == "__main__":
    if test_video_generation():
        print("\n🎉 Video generation test passed!")
    else:
        print("\n💥 Video generation test failed!")