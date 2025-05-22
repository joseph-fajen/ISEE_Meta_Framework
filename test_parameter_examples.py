#!/usr/bin/env python3
"""
Test script for validating example command handling in command_wizard.py
"""
import unittest
from unittest.mock import patch, MagicMock
from command_wizard import CommandWizard, PARAMETER_CONTEXT_AVAILABLE

class TestParameterExampleHandling(unittest.TestCase):
    """Test cases for parameter example handling in CommandWizard."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wizard = CommandWizard()
        
        # Ensure we have parameter context available
        self.original_context_available = PARAMETER_CONTEXT_AVAILABLE
        
    def tearDown(self):
        """Clean up after tests."""
        # Restore original parameter context availability
        # Note: we can't actually modify the module constant in the test,
        # but this is good practice for real implementations
        pass
        
    @patch('command_wizard.CommandWizard._show_parameter_examples')
    def test_handle_special_input_example(self, mock_show_examples):
        """Test that _handle_special_input properly handles 'example' command."""
        # Skip test if parameter context is not available
        if not PARAMETER_CONTEXT_AVAILABLE:
            self.skipTest("Parameter context not available")
            
        # Test handling of 'example' command
        result = self.wizard._handle_special_input("example", "query")
        
        # Check that example was shown and True was returned
        mock_show_examples.assert_called_once_with("query")
        self.assertTrue(result, "Should return True when handling example command")
        
    @patch('command_wizard.CommandWizard._show_parameter_examples')
    def test_handle_special_input_not_example(self, mock_show_examples):
        """Test that _handle_special_input ignores non-example inputs."""
        # Test handling of non-example command
        result = self.wizard._handle_special_input("not_example", "query")
        
        # Check that example was not shown and False was returned
        mock_show_examples.assert_not_called()
        self.assertFalse(result, "Should return False when not handling example command")
        
    @patch('command_wizard.CommandWizard._handle_special_input')
    def test_get_parameter_input_example(self, mock_handle_special):
        """Test that _get_parameter_input properly handles example command."""
        # Configure mock to return True when 'example' is entered, then False
        mock_handle_special.side_effect = [True, False]
        
        # Mock the input function to first return 'example', then 'real_input'
        with patch('builtins.input', side_effect=["example", "real_input"]):
            # Run the test (non-Rich version)
            result = self.wizard._get_parameter_input("query", "Enter your query")
            
        # Verify that _handle_special_input was called with 'example'
        mock_handle_special.assert_any_call("example", "query")
        
        # Verify that the result is the second input
        self.assertEqual(result, "real_input", "Should return the non-special input")
        
    @patch('command_wizard.Prompt.ask')
    @patch('command_wizard.CommandWizard._handle_special_input')
    def test_get_parameter_input_example_rich(self, mock_handle_special, mock_prompt_ask):
        """Test that _get_parameter_input properly handles example command with Rich UI."""
        # Skip test if Rich is not available
        if not hasattr(self.wizard, 'console'):
            self.skipTest("Rich library not available")
            
        # Configure mock to return True when 'example' is entered, then False
        mock_handle_special.side_effect = [True, False]
        
        # Mock Prompt.ask to first return 'example', then 'real_input'
        mock_prompt_ask.side_effect = ["example", "real_input"]
        
        # Run the test (Rich version)
        result = self.wizard._get_parameter_input("query", "Enter your query")
        
        # Verify that _handle_special_input was called with 'example'
        mock_handle_special.assert_any_call("example", "query")
        
        # Verify that the result is the second input
        self.assertEqual(result, "real_input", "Should return the non-special input")
        
    @patch('command_wizard.CommandWizard._show_parameter_examples')
    def test_query_input_example_handling(self, mock_show_examples):
        """Test that query input in main() properly handles example command."""
        # We can't easily test the main method directly, but we can test the underlying
        # _handle_special_input method which is used by the main method
        
        # Mock user input first returning 'example', then a valid query
        with patch('builtins.input', side_effect=["example", "test query"]):
            # Skip testing the entire main method and focus on handling 'example'
            result = self.wizard._handle_special_input("example", "query")
            
            # Verify that examples were shown
            if PARAMETER_CONTEXT_AVAILABLE:
                mock_show_examples.assert_called_once_with("query")
                self.assertTrue(result, "Should return True when handling example command")
            else:
                mock_show_examples.assert_not_called()
                self.assertFalse(result, "Should return False when parameter context is not available")
        
if __name__ == "__main__":
    unittest.main()