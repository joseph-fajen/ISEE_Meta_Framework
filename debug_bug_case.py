#!/usr/bin/env python3
"""
Debug the exact bug reproduction case
"""

import json
from app import app

def debug_bug_case():
    """Debug the exact parameters from the failing test"""
    print("🐛 Debugging Bug Reproduction Case...")
    
    with app.test_client() as client:
        # Exact test data from the failing test
        test_data = {
            "query": "How might I design a highly appealing web UI for a prompt meta framework tool?",
            "cognitive_frameworks": ["Analytical Framework", "Integrative Framework", 
                                   "First Principles Framework", "Contrarian Framework"],
            "selected_models": ["openai/o3-pro", "google/gemini-2.5-pro-preview", 
                               "deepseek/deepseek-r1-0528-qwen3-8b:free", "anthropic/claude-sonnet-4"],
            "selected_domains": ["Education", "Technology Innovation", 
                               "Learning Experience Design", "Content Strategy"]
        }
        
        print(f"📤 Testing with frameworks: {test_data['cognitive_frameworks']}")
        print(f"📤 Testing with models: {test_data['selected_models']}")
        print(f"📤 Testing with domains: {test_data['selected_domains']}")
        
        response = client.post('/api/preview-queries', 
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = json.loads(response.get_data(as_text=True))
            queries = response_data.get('queries', [])
            
            print(f"📊 Generated {len(queries)} queries")
            
            # Analyze what we got vs what we expected
            template_names = set()
            model_names = set()
            domain_names = set()
            
            for query in queries:
                template_names.add(query.get('template_name', 'Unknown'))
                model_names.add(query.get('model', 'Unknown'))
                domain_names.add(query.get('domain_name', 'Unknown'))
            
            print(f"\n📋 Analysis:")
            print(f"Expected frameworks: {set(test_data['cognitive_frameworks'])}")
            print(f"Found frameworks: {template_names}")
            print(f"Missing frameworks: {set(test_data['cognitive_frameworks']) - template_names}")
            
            print(f"\nExpected models: {set(test_data['selected_models'])}")
            print(f"Found models: {model_names}")
            print(f"Missing models: {set(test_data['selected_models']) - model_names}")
            
            print(f"\nExpected domains: {set(test_data['selected_domains'])}")
            print(f"Found domains: {domain_names}")
            print(f"Missing domains: {set(test_data['selected_domains']) - domain_names}")
            
        else:
            print(f"❌ API call failed: {response.get_data(as_text=True)}")

if __name__ == "__main__":
    debug_bug_case()