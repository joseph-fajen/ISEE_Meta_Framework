#!/usr/bin/env python3
"""
Debug the parameter mapping in detail
"""

from app import ISEEWebDemo

def debug_param_mapping():
    """Debug the parameter mapping step by step"""
    print("🔍 Debugging Parameter Mapping...")
    
    demo = ISEEWebDemo()
    
    # Test input with explicit max_combinations
    web_params = {
        "query": "Test query",
        "cognitive_frameworks": ["Analytical Framework"],
        "selected_models": ["openai/o3-pro"],
        "selected_domains": ["Education"],
        "max_combinations": 48  # Explicit value
    }
    
    print(f"📤 Input web_params: {web_params}")
    
    # Step through the conversion manually
    converted = {}
    
    # Core parameter mapping (from the actual code)
    param_mapping = {
        "query": "query",
        "variations": "variations", 
        "max_combinations": "max_combinations",
        "output_format": "output_format",
        "generate_reports": "generate_reports",
        "report_format": "report_format", 
        "export_csv": "export_csv",
        "analyze_results": "analyze_results",
        "no_visualizations": "no_visualizations"
    }
    
    print(f"\n📋 Applying param_mapping...")
    for web_key, isee_key in param_mapping.items():
        if web_key in web_params and web_params[web_key] is not None:
            converted[isee_key] = web_params[web_key]
            print(f"   {web_key} -> {isee_key}: {web_params[web_key]}")
    
    print(f"\n📊 After param_mapping: {converted}")
    
    # Check if max_combinations is in converted
    if "max_combinations" in converted:
        print(f"✅ max_combinations found: {converted['max_combinations']}")
    else:
        print(f"❌ max_combinations NOT found, will use default")
    
    # Now call the actual conversion to see what happens
    result = demo._convert_web_params_to_isee(web_params)
    print(f"\n📥 Final result: max_combinations = {result.get('max_combinations')}")

if __name__ == "__main__":
    debug_param_mapping()