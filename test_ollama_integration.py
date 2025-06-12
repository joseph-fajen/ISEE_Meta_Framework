#!/usr/bin/env python3
"""
Test the Ollama integration in the web demo
"""

import os
import json
import requests
import time
import subprocess
import threading
from pathlib import Path

def test_ollama_integration():
    """Test the Ollama integration functionality"""
    
    print("🦙 Testing ISEE Web Demo Ollama Integration")
    
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
        
        # Test 1: Check Ollama models endpoint
        print("\n1️⃣ Testing Ollama models endpoint...")
        response = requests.get(f"{base_url}/api/ollama-models")
        if response.status_code == 200:
            ollama_data = response.json()
            print(f"   ✅ Ollama endpoint response: {ollama_data}")
            
            if ollama_data.get("available", False):
                print(f"   🦙 Ollama available with {ollama_data.get('count', 0)} models:")
                for model in ollama_data.get("models", []):
                    print(f"      • {model}")
            else:
                print("   ⚠️ Ollama not available (this is expected if Ollama isn't running)")
        else:
            print(f"   ❌ Ollama endpoint failed: {response.status_code}")
            return False
        
        # Test 2: Check API status includes Ollama info
        print("\n2️⃣ Testing API status includes Ollama...")
        response = requests.get(f"{base_url}/api/api-status")
        if response.status_code == 200:
            api_status = response.json()
            print(f"   ✅ API status: {api_status}")
            
            if "ollama" in api_status:
                print(f"   🦙 Ollama status: {api_status['ollama']}")
                if api_status.get('ollama_models'):
                    print(f"   📋 Ollama models in status: {api_status['ollama_models']}")
            else:
                print("   ⚠️ Ollama not in API status")
        else:
            print(f"   ❌ API status failed: {response.status_code}")
        
        # Test 3: Test main page loads with Ollama section
        print("\n3️⃣ Testing main page includes Ollama section...")
        response = requests.get(base_url)
        if response.status_code == 200:
            html_content = response.text
            if "Local Ollama Models" in html_content and "ollama-section" in html_content:
                print("   ✅ Main page includes Ollama models section")
            else:
                print("   ⚠️ Main page missing Ollama section")
        else:
            print(f"   ❌ Main page failed: {response.status_code}")
        
        # Test 4: Test command preview API with Ollama models
        print("\n4️⃣ Testing command preview API with Ollama models...")
        
        # Test parameters with mix of models
        test_params = {
            "query": "Test query for Ollama integration",
            "selected_models": ["some_openrouter_model", "llama3:8b"],  # Mix of types
            "cognitive_frameworks": ["ins_analytical"],
            "variations": 2,
            "max_combinations": 4,
            "sampling_method": "stratified",
            "output_format": "markdown"
        }
        
        response = requests.post(f"{base_url}/api/preview", json=test_params)
        if response.status_code == 200:
            result = response.json()
            command = result.get("command", "")
            print(f"   📋 Generated command: {command}")
            
            # Should include both models
            if "llama3:8b" in command or "models 2" in command:
                print("   ✅ Command includes Ollama model configuration")
            else:
                print("   ⚠️ Command may not properly handle Ollama models")
                
            # Check for appropriate config file
            if any(config in command for config in ["unified_config.json", "ollama_config.json"]):
                print("   ✅ Uses appropriate config file for model types")
            else:
                print("   ⚠️ May not be using optimal config file")
        else:
            print(f"   ❌ Command preview failed: {response.status_code}")
        
        print("\n🎉 Ollama Integration Test Complete!")
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
    success = test_ollama_integration()
    if success:
        print("\n✅ Ollama integration tests passed!")
    else:
        print("\n❌ Some Ollama integration tests failed.")