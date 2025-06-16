#!/usr/bin/env python3
"""
Debug the combination generation parameters
"""

import json
from app import app, ISEEWebDemo

def debug_combination_params():
    """Debug what parameters are passed to generate_combinations"""
    print("⚙️ Debugging Combination Generation Parameters...")
    
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
    
    print(f"📊 Converted parameters:")
    for key, value in converted.items():
        print(f"   {key}: {value}")
    
    print(f"\n🔍 Key parameters for combination generation:")
    print(f"   instruction_count (instructions): {converted.get('instructions')}")
    print(f"   instruction_templates: {converted.get('instruction_templates')}")
    print(f"   model_count (models): {converted.get('models')}")
    print(f"   selected_models: {converted.get('selected_models')}")
    print(f"   domains: {converted.get('domains')}")
    print(f"   max_combinations: {converted.get('max_combinations')}")

if __name__ == "__main__":
    debug_combination_params()