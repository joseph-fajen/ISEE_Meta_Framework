#!/usr/bin/env python3
"""
Test that the command preview no longer includes --dry-run
"""

from app import ISEEWebDemo

def test_command_preview():
    """Test command preview generation"""
    
    demo = ISEEWebDemo()
    
    # Test parameters similar to user's example
    test_params = {
        "query": "How might I select a particularly effective mental model as a framework for writing a blog to a general audience about a highly technical software development project?",
        "selected_domains": ["Educational Content Development"],
        "cognitive_frameworks": ["ins_analytical", "ins_creative", "ins_pragmatic"],
        "selected_models": ["model1", "model2", "model3"],  # 3 models
        "variations": 3,
        "max_combinations": 12,
        "sampling_method": "stratified",
        "output_format": "markdown"
    }
    
    # Generate command preview
    command = demo.generate_command_preview(test_params)
    
    print("Generated command:")
    print(command)
    print()
    
    # Check if --dry-run is present
    if "--dry-run" in command:
        print("❌ FAIL: Command still contains --dry-run")
        return False
    else:
        print("✅ PASS: Command does not contain --dry-run")
    
    # Check if other expected parameters are present
    expected_parts = [
        "--query",
        "--domain",
        "--instruction-templates", 
        "--config openrouter_config.json",
        "--models 3",
        "--variations 3",
        "--max-combinations 12",
        "--sampling-method stratified",
        "--output-format markdown"
    ]
    
    missing_parts = []
    for part in expected_parts:
        if part not in command:
            missing_parts.append(part)
    
    if missing_parts:
        print(f"⚠️  Missing expected parts: {missing_parts}")
    else:
        print("✅ All expected parameters present")
    
    return "--dry-run" not in command

if __name__ == "__main__":
    success = test_command_preview()
    if success:
        print("\n🎉 Command preview fix successful!")
    else:
        print("\n❌ Command preview still has issues.")