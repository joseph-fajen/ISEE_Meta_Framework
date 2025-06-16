#!/usr/bin/env python3
"""
Debug the original test case with high max_combinations
"""

import json
from app import app

def debug_original_high_limit():
    """Debug the exact original test with high limit"""
    print("🔬 Debugging Original Test Case with High Limit...")
    
    with app.test_client() as client:
        # Exact test data from the failing test but with high max_combinations
        test_data = {
            "query": "How might I design a highly appealing web UI for a prompt meta framework tool?",
            "cognitive_frameworks": ["Analytical Framework", "Integrative Framework", 
                                   "First Principles Framework", "Contrarian Framework"],
            "selected_models": ["openai/o3-pro", "google/gemini-2.5-pro-preview", 
                               "deepseek/deepseek-r1-0528-qwen3-8b:free", "anthropic/claude-sonnet-4"],
            "selected_domains": ["Education", "Technology Innovation", 
                               "Learning Experience Design", "Content Strategy"],
            "max_combinations": 200  # High limit instead of 48
        }
        
        print(f"📤 Expected combinations: 4 frameworks × 4 models × 4 domains = 64")
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
    debug_original_high_limit()