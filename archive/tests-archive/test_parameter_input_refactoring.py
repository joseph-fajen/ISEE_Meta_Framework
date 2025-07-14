#!/usr/bin/env python3
"""
Test script for verifying the refactored parameter input handling in the Command Wizard.
"""
import sys
from command_wizard import CommandWizard

def test_parameter_input_refactoring():
    """Test that all refactored parameter input functions handle special commands properly."""
    print("Testing refactored parameter input handling in the Command Wizard...")
    print("This test will focus on a few key parameters to verify the refactoring.")
    print("\nPlease enter 'help' or 'example' at any prompt to test the special command handling.")
    print("You should see help text or examples instead of validation errors.\n")
    
    # Initialize wizard
    wizard = CommandWizard()
    
    # Override the main method to focus only on specific inputs
    def test_main(self):
        """Test version of the main method that tests key parameter inputs."""
        print("\n===== TESTING REFACTORED PARAMETER INPUT =====")
        
        # Test 1: Numeric Input (variations)
        print("\nTEST 1: Numeric Input (variations)")
        if hasattr(self, 'console'):
            self.console.print("\n[bold cyan]Testing Variations Input[/bold cyan]")
        else:
            print("\nTesting Variations Input")
        
        # Get variations count using our refactored input method
        variations_input = self._get_parameter_input("variations", "How many variations would you like?", "2")
        
        try:
            variations_count = int(variations_input) if variations_input.strip() else 2
            print(f"Selected variations count: {variations_count}")
        except ValueError:
            print("Invalid number, using default of 2")
            variations_count = 2
            
        # Test 2: Boolean Input (balanced_models)
        print("\nTEST 2: Boolean Input (balanced_models)")
        if hasattr(self, 'console'):
            self.console.print("\n[bold cyan]Testing Boolean Input[/bold cyan]")
        else:
            print("\nTesting Boolean Input")
        
        # Get boolean input using our refactored method
        balanced = self._get_boolean_input(
            "balanced_models", 
            "Would you like to balance models across providers?", 
            "y"
        )
        
        print(f"Selected value: {balanced}")
            
        # Test 3: Selection Input (sampling_method)
        print("\nTEST 3: Selection Input (sampling_method)")
        if hasattr(self, 'console'):
            self.console.print("\n[bold cyan]Testing Selection Input[/bold cyan]")
        else:
            print("\nTesting Selection Input")
        
        # Use our selection input function
        sampling_options = ["exhaustive", "random", "stratified"]
        descriptions = [
            "Try all combinations", 
            "Randomly sample combinations", 
            "Ensure representative sample"
        ]
        
        sampling_choice_idx = self._get_selection_input(
            "sampling_method",
            "Select a sampling method",
            sampling_options,
            descriptions,
            "1"
        )
        
        print(f"Selected option: {sampling_options[sampling_choice_idx]}")
        
        print("\nTest completed successfully!")
        
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
    test_parameter_input_refactoring()