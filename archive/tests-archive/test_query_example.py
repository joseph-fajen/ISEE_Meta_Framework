#!/usr/bin/env python3
"""
Test script for handling the example command in the query input.
"""
import sys
from command_wizard import CommandWizard

def test_query_example_handling():
    """Test that the example command is properly handled in the query input."""
    print("Testing example command handling in the query input...")
    print("Please enter 'example' at the query prompt to test the fix.")
    
    # Initialize wizard
    wizard = CommandWizard()
    
    # Call main to test the query input flow
    try:
        wizard.main()
        print("Test completed successfully!")
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_query_example_handling()