#!/usr/bin/env python3
"""
Debug script to test the /api/preview-queries endpoint
"""

import json
from app import app

def test_preview_api():
    """Test the preview-queries API endpoint"""
    print("🔍 Testing /api/preview-queries endpoint...")
    
    with app.test_client() as client:
        # Test data from the failing test
        test_data = {
            "query": "Test query for debugging",
            "cognitive_frameworks": ["Analytical Framework"],
            "selected_models": ["openai/o3-pro"],
            "selected_domains": ["Education"]
        }
        
        print(f"📤 Sending request data: {json.dumps(test_data, indent=2)}")
        
        response = client.post('/api/preview-queries', 
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        
        response_text = response.get_data(as_text=True)
        print(f"📥 Response text (first 500 chars): {response_text[:500]}...")
        
        if response.status_code == 200:
            try:
                response_json = json.loads(response_text)
                print(f"✅ JSON Response keys: {list(response_json.keys())}")
                
                if 'queries' in response_json:
                    print(f"✅ Number of queries: {len(response_json['queries'])}")
                    if response_json['queries']:
                        first_query = response_json['queries'][0]
                        print(f"✅ First query keys: {list(first_query.keys())}")
                        print(f"✅ First query model: {first_query.get('model')}")
                        print(f"✅ First query domain: {first_query.get('domain_name')}")
                        print(f"✅ First query template: {first_query.get('template_name')}")
                        
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON: {e}")
        else:
            print(f"❌ API call failed: {response_text}")

if __name__ == "__main__":
    test_preview_api()