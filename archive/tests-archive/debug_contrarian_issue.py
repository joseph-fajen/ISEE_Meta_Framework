#!/usr/bin/env python3
"""
Debug the specific Contrarian Framework issue
"""

import json
from app import app

def debug_contrarian_issue():
    """Debug why Contrarian Framework is missing"""
    print("🔍 Debugging Contrarian Framework Issue...")
    
    with app.test_client() as client:
        # Test data with only Contrarian Framework
        test_data = {
            "query": "Test contrarian framework",
            "cognitive_frameworks": ["Contrarian Framework"],
            "selected_models": ["openai/o3-pro"],
            "selected_domains": ["Education"]
        }
        
        print(f"📤 Testing with: {test_data['cognitive_frameworks']}")
        
        response = client.post('/api/preview-queries', 
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = json.loads(response.get_data(as_text=True))
            queries = response_data.get('queries', [])
            
            print(f"📊 Generated {len(queries)} queries")
            
            # Check what templates are actually being used
            template_names = set()
            for query in queries:
                template_name = query.get('template_name', 'Unknown')
                template_names.add(template_name)
                print(f"   Query: template='{template_name}', model='{query.get('model')}', domain='{query.get('domain_name')}'")
            
            print(f"📋 Unique templates found: {template_names}")
            
            if 'Contrarian Framework' in template_names:
                print("✅ Contrarian Framework found!")
            else:
                print("❌ Contrarian Framework missing!")
                print("Available templates:", template_names)
        else:
            print(f"❌ API call failed: {response.get_data(as_text=True)}")

if __name__ == "__main__":
    debug_contrarian_issue()