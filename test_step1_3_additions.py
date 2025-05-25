#!/usr/bin/env python3
"""
Test script for Step 1.3 additions to Command Wizard

Tests:
1. Auto-display of all parameters after query entry
2. Automatic configuration file selection (unified_config.json)
3. Proper step numbering after config selection removal
"""

import os
import sys
import io
from unittest.mock import patch, MagicMock

# Import the command wizard
from command_wizard import CommandWizard

def test_automatic_config_selection():
    """Test that unified_config.json is automatically selected."""
    print("Testing automatic config selection...")
    
    wizard = CommandWizard()
    config_file = wizard._get_default_config_file()
    
    # Check if unified_config.json exists and is selected
    if os.path.exists("unified_config.json"):
        assert config_file == "unified_config.json", f"Expected unified_config.json, got {config_file}"
        print("✓ unified_config.json automatically selected")
    else:
        print("✓ No config file found (expected when unified_config.json doesn't exist)")
    
    return True

def test_parameter_display():
    """Test that the parameter display function works."""
    print("Testing parameter display...")
    
    wizard = CommandWizard()
    
    # Capture output
    captured_output = io.StringIO()
    with patch('sys.stdout', captured_output):
        wizard._show_all_parameters_help()
    
    output = captured_output.getvalue()
    
    # Check that key elements are in the output
    assert "All Available Parameters" in output, "Parameter display missing title"
    assert "query" in output.lower(), "Query parameter missing from display"
    assert "models" in output.lower(), "Models parameter missing from display"
    print("✓ Parameter display working correctly")
    
    return True

def test_config_selection_removal():
    """Test that config selection step is removed from main flow."""
    print("Testing config selection removal...")
    
    wizard = CommandWizard()
    
    # Mock input to simulate query entry and then exit
    with patch('builtins.input', side_effect=['test query', KeyboardInterrupt()]):
        with patch.object(wizard, '_show_all_parameters_help') as mock_help:
            try:
                wizard.main()
            except KeyboardInterrupt:
                pass  # Expected when we interrupt the flow
    
    # Verify that show_all_parameters_help was called (auto-display after query)
    mock_help.assert_called_once()
    print("✓ Parameters auto-displayed after query entry")
    
    return True

def test_step_numbering():
    """Test that step numbering is correct after removing config selection."""
    print("Testing step numbering...")
    
    # Read the command_wizard.py file to check step numbering in main flow
    with open('command_wizard.py', 'r') as f:
        content = f.read()
    
    # Find the main function and check the active step numbering
    main_func_start = content.find("def main(self):")
    main_func_content = content[main_func_start:main_func_start + 5000]  # First 5000 chars of main
    
    # Check that steps are numbered correctly in the main function
    assert "Step 1: Query" in main_func_content, "Step 1 (Query) not found in main"
    assert "Step 2: Domain Selection" in main_func_content, "Step 2 (Domain Selection) not found in main"
    
    # Check that the old config selection is not in the main flow
    assert "Step 2: Configuration File Selection" not in main_func_content, "Old Step 2 (Config Selection) still in main flow"
    
    # Check that we're using the new automatic config method
    assert "_get_default_config_file" in main_func_content, "New automatic config method not found in main"
    
    print("✓ Step numbering updated correctly in main flow")
    
    return True

def main():
    """Run all tests for Step 1.3 additions."""
    print("Running tests for Step 1.3 Command Wizard additions...\n")
    
    tests = [
        test_automatic_config_selection,
        test_parameter_display,
        test_step_numbering,
        test_config_selection_removal,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"✗ Test failed: {e}\n")
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Step 1.3 addition tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)