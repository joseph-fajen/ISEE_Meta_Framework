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
        # Mock functions that would try to access files or external resources
        with patch('command_wizard.CommandWizard._get_potential_config_files', return_value=["sample_config.json"]):
            with patch('command_wizard.CommandWizard._select_config_file'):
                self.wizard._select_config_file([])
                
        # Check that "Step 2: Configuration File Selection" was printed
        step2_calls = [call for call in mock_print.call_args_list 
                     if isinstance(call[0][0], str) and "Step 2: Configuration File Selection" in call[0][0]]
        self.assertTrue(len(step2_calls) > 0, "Step 2 label was not found in output")
        
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
        
    @patch('builtins.print')
    def test_visual_separation_in_help(self, mock_print):
        """Test that help content has proper visual separation with separator lines."""
        # Skip test if parameter context is not available
        if not PARAMETER_CONTEXT_AVAILABLE:
            self.skipTest("Parameter context not available")
            
        # Test showing help for a parameter
        with patch('command_wizard.RICH_AVAILABLE', False):
            with patch('command_wizard.CommandWizard._show_parameter_context'):
                with patch('command_wizard.ParameterContext.get_parameter_context') as mock_get_context:
                    # Mock a basic parameter context
                    mock_get_context.return_value = {
                        'short': 'Test description',
                        'long': 'Longer test description',
                        'impact': 'Test impact',
                        'examples': ['example1', 'example2'],
                        'related': []
                    }
                    
                    self.wizard._show_parameter_help("test")
                    
        # Check that separator lines were printed
        separator_calls = [call for call in mock_print.call_args_list 
                         if isinstance(call[0][0], str) and "-" * 50 in call[0][0]]
        
        # Should have at least 2 separator lines (before and after content)
        self.assertGreaterEqual(len(separator_calls), 2, 
                              "Help content should have separator lines before and after")

if __name__ == "__main__":
    unittest.main()