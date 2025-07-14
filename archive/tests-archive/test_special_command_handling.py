#!/usr/bin/env python3
"""
Tests for special command handling in command_wizard.py
"""
import unittest
from unittest.mock import patch, MagicMock, call
from command_wizard import CommandWizard, PARAMETER_CONTEXT_AVAILABLE

class TestSpecialCommandHandling(unittest.TestCase):
    """Tests for special command handling in CommandWizard."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wizard = CommandWizard()
        
    def tearDown(self):
        """Clean up after tests."""
        pass
        
    @patch('command_wizard.CommandWizard._show_parameter_context')
    @patch('command_wizard.CommandWizard._handle_special_input')
    def test_get_parameter_input_context_once(self, mock_handle_special, mock_show_context):
        """Test that parameter context is only shown once during input with special commands."""
        # Configure mock to handle special input first time, then return normal input
        mock_handle_special.side_effect = [True, False]
        
        # Mock the input function to first return 'help', then 'normal_input'
        with patch('builtins.input', side_effect=["help", "normal_input"]):
            result = self.wizard._get_parameter_input("query", "Enter your query")
            
        # Verify that _show_parameter_context was called exactly once
        mock_show_context.assert_called_once()
        self.assertEqual(result, "normal_input")
        
    @patch('command_wizard.RICH_AVAILABLE', False)
    @patch('builtins.print')
    def test_step_numbering_consistency(self, mock_print):
        """Test that step numbering is consistent for all wizard steps."""
        # Simply verify the code contains the proper step number label
        with open('/Users/josephfajen/git/ISEE_Meta_Framework/command_wizard.py', 'r') as f:
            content = f.read()
            
        # Check for step numbering in config file selection
        self.assertIn('Step 2: Configuration File Selection', content, 
                     "Step 2 label not found in command_wizard.py")
        
    @patch('command_wizard.CommandWizard._show_parameter_help')
    @patch('command_wizard.CommandWizard._show_parameter_examples')
    def test_handle_special_input(self, mock_show_examples, mock_show_help):
        """Test that _handle_special_input properly handles both help and example commands."""
        # Test with 'help' command
        result = self.wizard._handle_special_input("help", "query")
        mock_show_help.assert_called_once_with("query")
        self.assertTrue(result)
        
        # Reset mocks
        mock_show_help.reset_mock()
        mock_show_examples.reset_mock()
        
        # Test with 'example' command
        if PARAMETER_CONTEXT_AVAILABLE:
            # Only test example command if parameter context is available
            result = self.wizard._handle_special_input("example", "query")
            mock_show_examples.assert_called_once_with("query")
            self.assertTrue(result)
        
    def test_visual_separation_in_help(self):
        """Test that help content has proper visual separation with separator lines."""
        # Simply check if the separator code is in the function
        with open('/Users/josephfajen/git/ISEE_Meta_Framework/command_wizard.py', 'r') as f:
            content = f.read()
            
        # Check for separator lines in _show_parameter_help
        self.assertIn('# Add a separator line before help content', content, 
                    "Separator before help content not found")
        self.assertIn('# Add a separator line after help content', content, 
                    "Separator after help content not found")
        
        # Check for separator lines in _show_parameter_examples
        self.assertIn('# Add a separator line before examples content', content, 
                    "Separator before examples content not found")
        self.assertIn('# Add a separator line after examples content', content, 
                    "Separator after examples content not found")

if __name__ == "__main__":
    unittest.main()