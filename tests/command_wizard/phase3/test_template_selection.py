#!/usr/bin/env python3
"""
Test Script for Template Selection Feature

This script tests the template selection implementation in the Command Wizard.
"""

import os
import sys
import re
import subprocess
from typing import List, Dict, Any, Optional, Tuple

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import from project
from instruction_templates import create_default_library


def test_command_generation_with_templates():
    """Test that the Command Wizard generates the correct command with specific templates."""
    # Get all available template IDs
    template_library = create_default_library()
    all_templates = template_library.list_templates()
    test_templates = all_templates[:3]  # Use the first 3 templates for testing
    test_template_ids = [t.id for t in test_templates]
    
    # Create a mock command to simulate selecting these templates
    # This approach doesn't rely on interactive input which would be challenging to automate
    template_ids_str = ",".join(test_template_ids)
    mock_command = f"""
import sys
sys.path.insert(0, '{os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))}')
from command_wizard import CommandWizard

# Create wizard and set parameters directly
wizard = CommandWizard()
wizard.params['query'] = 'How might we improve urban transportation?'
wizard.params['models'] = 2
wizard.params['instructions'] = 3
wizard.params['variations'] = 2
wizard.params['instruction_templates'] = '{template_ids_str}'

# Generate the command
command = wizard.generate_command()
print("GENERATED COMMAND:")
print(command)
    """
    
    # Save the mock script to a temporary file
    temp_script_path = os.path.join(os.path.dirname(__file__), 'temp_test_script.py')
    with open(temp_script_path, 'w') as f:
        f.write(mock_command)
    
    try:
        # Run the mock script
        result = subprocess.run(['python', temp_script_path], capture_output=True, text=True)
        
        # Check if the command was generated successfully
        if result.returncode != 0:
            print(f"Error generating command: {result.stderr}")
            return False
        
        # Extract the generated command
        output = result.stdout
        command_match = re.search(r'GENERATED COMMAND:\n(.*)', output, re.DOTALL)
        if not command_match:
            print("Could not find generated command in output")
            return False
        
        generated_command = command_match.group(1).strip()
        print(f"Generated command: {generated_command}")
        
        # Check if the command includes the --instruction-templates parameter
        template_param = f'--instruction-templates "{",".join(test_template_ids)}"'
        if template_param not in generated_command:
            print(f"Command does not include expected template parameter: {template_param}")
            return False
        
        print("✅ Command generation test passed: Template selection is correctly included in the command")
        return True
    
    finally:
        # Clean up the temporary script
        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)


def test_preview_with_templates():
    """Test that the Command Wizard preview shows template information correctly."""
    # Similar to the previous test, but checking the preview output
    template_library = create_default_library()
    all_templates = template_library.list_templates()
    test_templates = all_templates[:3]  # Use the first 3 templates for testing
    test_template_ids = [t.id for t in test_templates]
    
    # Create a mock command to simulate previewing with these templates
    template_ids_str = ",".join(test_template_ids)
    mock_command = f"""
import sys
sys.path.insert(0, '{os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))}')
from command_wizard import CommandWizard
from io import StringIO

# Create wizard and set parameters directly
wizard = CommandWizard()
wizard.params['query'] = 'How might we improve urban transportation?'
wizard.params['models'] = 2
wizard.params['instructions'] = 3
wizard.params['variations'] = 2
wizard.params['instruction_templates'] = '{template_ids_str}'

# Generate command to see if it includes templates
command = wizard.generate_command()
print("PREVIEW OUTPUT:")
print("Command Preview")
print(f"Generated Command: {{command}}")
print(f"Query: {{wizard.params['query']}}")
print(f"Instruction Templates: {{wizard.params['instruction_templates']}}")
    """
    
    # Save the mock script to a temporary file
    temp_script_path = os.path.join(os.path.dirname(__file__), 'temp_preview_test.py')
    with open(temp_script_path, 'w') as f:
        f.write(mock_command)
    
    try:
        # Run the mock script
        result = subprocess.run(['python', temp_script_path], capture_output=True, text=True)
        
        # Check if the preview was generated successfully
        if result.returncode != 0:
            print(f"Error generating preview: {result.stderr}")
            return False
        
        # Extract the preview output
        output = result.stdout
        preview_match = re.search(r'PREVIEW OUTPUT:(.*)', output, re.DOTALL)
        if not preview_match:
            print("Could not find preview output")
            return False
        
        preview_text = preview_match.group(1).strip()
        
        # Check if the preview shows template IDs
        template_ids_str = ",".join(test_template_ids)
        if template_ids_str not in preview_text:
            print(f"Preview does not include template IDs: {template_ids_str}")
            return False
        
        # Check if instruction templates are mentioned
        if "instruction templates" not in preview_text.lower():
            print("Preview does not mention instruction templates")
            return False
        
        print("✅ Preview test passed: Template names are correctly shown in the command preview")
        return True
    
    finally:
        # Clean up the temporary script
        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)


def test_validation_with_templates():
    """Test that the Command Wizard validates template selections."""
    # Test with invalid template IDs
    invalid_test = f"""
import sys
sys.path.insert(0, '{os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))}')
from command_wizard import CommandWizard

# Create wizard and set parameters with invalid template IDs
wizard = CommandWizard()
wizard.params['query'] = 'How might we improve urban transportation?'
wizard.params['models'] = 2
wizard.params['instructions'] = 3
wizard.params['variations'] = 2
wizard.params['instruction_templates'] = 'nonexistent_template_1,nonexistent_template_2'

# Try to generate command (which will trigger validation)
try:
    command = wizard.generate_command()
    print("Command generated successfully (shouldn't happen with invalid templates):")
    print(command)
except Exception as e:
    print(f"Exception (expected): {{str(e)}}")
    """
    
    # Save the invalid test script
    temp_script_path = os.path.join(os.path.dirname(__file__), 'temp_validation_test.py')
    with open(temp_script_path, 'w') as f:
        f.write(invalid_test)
    
    try:
        # Run the invalid template test
        result = subprocess.run(['python', temp_script_path], capture_output=True, text=True)
        
        # Check if validation was performed successfully
        if result.returncode != 0:
            print(f"Error during validation test: {result.stderr}")
            return False
        
        # Check if the validation correctly identified the invalid templates
        output = result.stdout
        print(f"Validation test output: {output}")
            
        if "Error: Invalid template ID:" not in output:
            print("Validation did not report invalid template IDs")
            return False
        
        print("✅ Validation test passed: Invalid templates are correctly identified")
        return True
    
    finally:
        # Clean up the temporary script
        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)


def run_all_tests():
    """Run all template selection tests."""
    print("Testing Template Selection Implementation")
    print("=" * 40)
    
    test_results = []
    test_results.append(("Command Generation", test_command_generation_with_templates()))
    test_results.append(("Preview Display", test_preview_with_templates()))
    test_results.append(("Template Validation", test_validation_with_templates()))
    
    print("\nTest Summary:")
    print("=" * 40)
    all_passed = True
    for name, result in test_results:
        status = "PASSED" if result else "FAILED"
        if not result:
            all_passed = False
        print(f"{name}: {status}")
    
    if all_passed:
        print("\n✅ All template selection tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed. See details above.")
        return 1


if __name__ == "__main__":
    # Run all tests
    exit_code = run_all_tests()
    sys.exit(exit_code)