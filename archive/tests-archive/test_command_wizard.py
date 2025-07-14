#!/usr/bin/env python3
"""
Test script for command wizard template selection
"""
import sys
from command_wizard import CommandWizard

def test_template_selection():
    """Test template selection"""
    # Initialize wizard
    wizard = CommandWizard()
    
    # Call the select_instruction_templates method
    try:
        wizard.select_instruction_templates()
        print("Template selection successful!")
    except Exception as e:
        print(f"Error in template selection: {e}")

if __name__ == "__main__":
    test_template_selection()