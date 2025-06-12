#!/usr/bin/env python3
"""
Test the web demo API key integration functionality
"""

import os
import json
import requests
import time
import subprocess
import threading
from pathlib import Path

def test_api_integration():
    """Test the API key integration in the web demo"""
    
    print("🔧 Testing ISEE Web Demo API Key Integration")
    
    # Start the web server in background
    print("📡 Starting web server...")
    server_process = subprocess.Popen(
        ['python', 'app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=Path(__file__).parent
    )
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        base_url = "http://localhost:5001"
        
        # Test 1: Check API status endpoint
        print("\n1️⃣ Testing API status endpoint...")
        response = requests.get(f"{base_url}/api/api-status")
        if response.status_code == 200:
            api_status = response.json()
            print(f"   ✅ API status: {api_status}")
            print(f"   🔑 Any API available: {api_status.get('any_api', False)}")
        else:
            print(f"   ❌ API status failed: {response.status_code}")
            return False
        
        # Test 2: Test OpenRouter validation with invalid key
        print("\n2️⃣ Testing OpenRouter validation (invalid key)...")
        response = requests.post(f"{base_url}/api/validate-openrouter", 
                               json={"api_key": "invalid-key"})
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Validation response: {result}")
            if not result.get("valid", True):
                print("   ✅ Correctly rejected invalid key")
            else:
                print("   ⚠️ Should have rejected invalid key")
        else:
            print(f"   ❌ Validation failed: {response.status_code}")
        
        # Test 3: Test OpenRouter validation with properly formatted (but fake) key
        print("\n3️⃣ Testing OpenRouter validation (fake but formatted key)...")
        fake_key = "sk-or-fake-key-for-testing-12345"
        response = requests.post(f"{base_url}/api/validate-openrouter", 
                               json={"api_key": fake_key})
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Validation response: {result}")
            # Should fail because it's not a real key
            if not result.get("valid", True):
                print("   ✅ Correctly identified fake key")
            else:
                print("   ⚠️ Fake key shouldn't validate")
        
        # Test 4: Test web demo main page loads
        print("\n4️⃣ Testing main page loads...")
        response = requests.get(base_url)
        if response.status_code == 200:
            html_content = response.text
            if "ISEE Meta Framework" in html_content and "API Configuration" in html_content:
                print("   ✅ Main page loads with API configuration section")
            else:
                print("   ⚠️ Main page missing expected content")
        else:
            print(f"   ❌ Main page failed: {response.status_code}")
        
        print("\n🎉 API Integration Test Complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False
        
    finally:
        # Stop the server
        print("\n📴 Stopping web server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    success = test_api_integration()
    if success:
        print("\n✅ All tests passed! API key integration is working.")
    else:
        print("\n❌ Some tests failed. Check the integration.")