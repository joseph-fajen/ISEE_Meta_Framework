#!/usr/bin/env python3
"""
Debug framework conversion from Web UI to backend
"""

from app import ISEEWebDemo

def debug_framework_conversion():
    """Debug the framework conversion process"""
    print("🔄 Debugging Framework Conversion...")
    
    demo = ISEEWebDemo()
    
    # Test the exact parameters from the failing test
    test_params = {
        "query": "How might I design a highly appealing web UI for a prompt meta framework tool?",
        "cognitive_frameworks": ["Analytical Framework", "Integrative Framework", 
                               "First Principles Framework", "Contrarian Framework"],
        "selected_models": ["openai/o3-pro", "google/gemini-2.5-pro-preview", 
                           "deepseek/deepseek-r1-0528-qwen3-8b:free", "anthropic/claude-sonnet-4"],
        "selected_domains": ["Education", "Technology Innovation", 
                           "Learning Experience Design", "Content Strategy"]
    }
    
    # Convert parameters
    converted = demo._convert_web_params_to_isee(test_params)
    
    print(f"📤 Original frameworks: {test_params['cognitive_frameworks']}")
    print(f"📥 Converted instruction_templates: {converted.get('instruction_templates')}")
    print(f"📥 Converted instructions count: {converted.get('instructions')}")
    
    # Check if all frameworks mapped correctly
    if converted.get('instruction_templates'):
        template_ids = converted['instruction_templates'].split(',')
        print(f"📋 Template IDs: {template_ids}")
        
        # Check what templates are available in the config
        import json
        with open('openrouter_config.json', 'r') as f:
            config = json.load(f)
        
        available_template_ids = [t['id'] for t in config.get('instructions', [])]
        print(f"🗂️ Available template IDs: {available_template_ids}")
        
        # Check which template IDs are missing
        missing_ids = set(template_ids) - set(available_template_ids)
        if missing_ids:
            print(f"❌ Missing template IDs: {missing_ids}")
        else:
            print("✅ All template IDs found in config")

if __name__ == "__main__":
    debug_framework_conversion()