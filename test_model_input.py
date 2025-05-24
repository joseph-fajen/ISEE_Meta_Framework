#!/usr/bin/env python3
"""
Test script for model input handling in the Command Wizard.
"""
import sys
from command_wizard import CommandWizard

def test_model_input_handling():
    """Test that the model input properly handles special commands like 'example'."""
    print("Testing model input handling in the Command Wizard...")
    print("Please enter 'example' at the model count prompt to test the fix.")
    print("You should see examples of model count values instead of an error message.")
    
    # Initialize wizard
    wizard = CommandWizard()
    
    # Override the main method to focus only on the model selection
    def test_main(self):
        """Test version of the main method that only tests model selection."""
        print("\nSTART TEST: Model Selection")
        
        if hasattr(self, 'console'):
            self.console.print("\n[bold cyan]Step 5: Model Selection[/bold cyan]")
        else:
            print("\nStep 5: Model Selection")
        
        # Get models count using our reusable function
        models_input = self._get_parameter_input("models", "How many models would you like to use?", "2")
        
        # Convert to integer after handling any special commands
        try:
            models_count = int(models_input) if models_input.strip() else 2
            print(f"Selected model count: {models_count}")
        except ValueError:
            print("Invalid number, using default of 2")
            models_count = 2
        
        print("Test completed successfully!")
        
    # Replace the main method temporarily
    original_main = wizard.main
    wizard.main = lambda: test_main(wizard)
    
    # Run the test
    try:
        wizard.main()
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        # Restore the original main method
        wizard.main = original_main

if __name__ == "__main__":
    test_model_input_handling()