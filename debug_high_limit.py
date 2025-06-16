#!/usr/bin/env python3
"""
Debug with high max_combinations to see true behavior
"""

import json
from app import app

def debug_high_limit():
    """Debug with high max_combinations limit"""
    print("🔬 Debugging with High Max Combinations Limit...")
    
    with app.test_client() as client:
        # Test data with high max_combinations
        test_data = {
            "query": "Test query",
            "cognitive_frameworks": ["Analytical Framework", "Integrative Framework", 
                                   "First Principles Framework", "Contrarian Framework"],
            "selected_models": ["openai/o3-pro", "anthropic/claude-sonnet-4"],  # Only 2 models for clarity
            "selected_domains": ["Education", "Technology Innovation"],  # Only 2 domains for clarity
            "max_combinations": 200  # High limit
        }
        
        print(f"📤 Expected combinations: 4 frameworks × 2 models × 2 domains = 16")
        print(f"📤 Max combinations: {test_data['max_combinations']}")
        
        response = client.post('/api/preview-queries', 
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = json.loads(response.get_data(as_text=True))
            queries = response_data.get('queries', [])
            
            print(f"📊 Generated {len(queries)} queries")
            
            # Analyze frameworks used
            template_names = set()
            for query in queries:
                template_names.add(query.get('template_name', 'Unknown'))
            
            print(f"📋 Frameworks found: {len(template_names)}")
            for framework in sorted(template_names):
                print(f"   - {framework}")
            
            expected_frameworks = set(test_data['cognitive_frameworks'])
            missing_frameworks = expected_frameworks - template_names
            if missing_frameworks:
                print(f"❌ Missing frameworks: {missing_frameworks}")
            else:
                print(f"✅ All frameworks found!")
        else:
            print(f"❌ API call failed: {response.get_data(as_text=True)}")

if __name__ == "__main__":
    debug_high_limit()