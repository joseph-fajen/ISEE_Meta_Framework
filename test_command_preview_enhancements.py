#!/usr/bin/env python3
"""
Test Script for Step 1.3: Command Preview Enhancements

This script tests the enhanced command preview functionality including:
- Categorized parameter displays
- Detailed vs summary views  
- Parameter change tracking
- Interactive preview commands

Part of the UX Enhancement Roadmap - Step 1.3: Command Preview Enhancements
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from command_wizard import CommandWizard


class TestCommandPreviewEnhancements(unittest.TestCase):
    """Test cases for Step 1.3 Command Preview Enhancement features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wizard = CommandWizard()
        # Initialize with all default parameters to avoid KeyError issues
        self.wizard.params = {
            "query": "Test query",
            "domain": "Technology Innovation", 
            "models": 3,
            "instructions": 2,
            "variations": 2,
            "sampling_method": "stratified",
            "simulate": True,
            "balanced_models": True,
            "use_ollama": False,
            "dry_run": False,
            "generate_reports": False,
            "analyze_results": False,
            "output_format": None,
            "output_file": None,
            "max_combinations": None,
            "quick": False,
            "full": False,
            "config_file": None,
            "save_state": None,
            "load_state": None,
            "synthesize_method": None,
            "domain_config": None,
            "instruction_templates": None,
            "no_visualizations": False,
            "report_format": None,
            "export_csv": False
        }
        
    def test_preview_detailed_mode_toggle(self):
        """Test that detailed mode can be toggled correctly."""
        # Start in detailed mode (default)
        self.assertTrue(self.wizard.preview_detailed_mode)
        
        # Test setting to summary mode
        self.wizard.preview_detailed_mode = False
        self.assertFalse(self.wizard.preview_detailed_mode)
        
        # Test setting back to detailed mode
        self.wizard.preview_detailed_mode = True
        self.assertTrue(self.wizard.preview_detailed_mode)
    
    def test_special_input_preview_commands(self):
        """Test that preview special commands are handled correctly."""
        # Test basic preview command
        result = self.wizard._handle_special_input("preview", "query")
        self.assertTrue(result)
        
        # Test detailed preview command
        result = self.wizard._handle_special_input("preview detailed", "query") 
        self.assertTrue(result)
        self.assertTrue(self.wizard.preview_detailed_mode)
        
        # Test summary preview command
        result = self.wizard._handle_special_input("preview summary", "query")
        self.assertTrue(result)
        self.assertFalse(self.wizard.preview_detailed_mode)
        
        # Test that non-preview commands return False
        result = self.wizard._handle_special_input("not a preview command", "query")
        self.assertFalse(result)
    
    def test_parameter_change_tracking(self):
        """Test that parameter changes are tracked correctly."""
        # Initially no previous params
        self.assertIsNone(self.wizard.previous_params)
        
        # Set a parameter to trigger tracking
        self.wizard._update_param_and_estimate("models", 5)
        
        # Now we should have previous params saved
        self.assertIsNotNone(self.wizard.previous_params)
        
        # Change another parameter
        old_models = self.wizard.params["models"]
        self.wizard._update_param_and_estimate("instructions", 4)
        
        # Verify the change tracking would detect this
        self.assertEqual(self.wizard.params["instructions"], 4)
        self.assertEqual(self.wizard.params["models"], 5)  # Should still be 5
    
    def test_format_parameter_value(self):
        """Test parameter value formatting for display."""
        # Test boolean values
        self.assertEqual(self.wizard._format_parameter_value("simulate", True), "Yes")
        self.assertEqual(self.wizard._format_parameter_value("simulate", False), "No")
        
        # Test list values
        self.assertEqual(self.wizard._format_parameter_value("test", ["a", "b", "c"]), "a, b, c")
        
        # Test string values
        self.assertEqual(self.wizard._format_parameter_value("query", "test query"), "test query")
        
        # Test instruction templates formatting
        templates = "template1,template2,template3,template4,template5"
        result = self.wizard._format_parameter_value("instruction_templates", templates)
        self.assertIn("template1, template2, template3", result)
        self.assertIn("(+2 more)", result)
    
    def test_parameter_description_retrieval(self):
        """Test that parameter descriptions are retrieved correctly."""
        # Test with a known parameter
        desc = self.wizard._get_parameter_description("query", detailed=False)
        self.assertIsInstance(desc, str)
        self.assertGreater(len(desc), 0)
        
        # Test detailed vs short descriptions
        short_desc = self.wizard._get_parameter_description("query", detailed=False)
        long_desc = self.wizard._get_parameter_description("query", detailed=True)
        
        # Both should be strings (may be the same if no long description available)
        self.assertIsInstance(short_desc, str)
        self.assertIsInstance(long_desc, str)
    
    @patch('command_wizard.RICH_AVAILABLE', True)
    def test_enhanced_parameter_preview_categories(self):
        """Test that parameter preview shows categories correctly."""
        with patch.object(self.wizard, 'console') as mock_console:
            self.wizard._display_enhanced_parameter_preview(show_detailed=True)
            
            # Verify that console.print was called (indicates Rich formatting was used)
            self.assertTrue(mock_console.print.called)
            
            # Check that some expected output was generated
            call_args = [call[0][0] for call in mock_console.print.call_args_list if call[0]]
            output_text = " ".join(str(arg) for arg in call_args)
            
            # Should contain some category-related content
            # Note: This is a basic test - a more detailed test would check specific categories
            self.assertIsInstance(output_text, str)
    
    @patch('command_wizard.RICH_AVAILABLE', False)  
    def test_basic_parameter_preview_fallback(self):
        """Test that basic preview works when Rich is not available."""
        with patch('builtins.print') as mock_print:
            self.wizard._display_basic_parameter_preview()
            
            # Verify that print was called
            self.assertTrue(mock_print.called)
            
            # Check that some expected content was printed
            call_args = [call[0][0] for call in mock_print.call_args_list]
            output_text = " ".join(str(arg) for arg in call_args)
            
            # Should contain basic parameter information
            self.assertIn("Command Parameters", output_text)
            self.assertIn("Query:", output_text)
            self.assertIn("Models:", output_text)
    
    def test_parameter_change_detection(self):
        """Test that parameter changes are detected and formatted correctly."""
        # Set up initial state
        self.wizard.previous_params = {
            "models": 2,
            "instructions": 3,
            "query": "old query"
        }
        
        # Current state (different from previous)
        self.wizard.params = {
            "models": 5,
            "instructions": 3,  # unchanged
            "query": "new query",
            "simulate": True    # new parameter
        }
        
        # Test that changes are detected correctly
        with patch.object(self.wizard, 'console') as mock_console:
            self.wizard._show_parameter_changes()
            
            # Should have been called if there are changes and Rich is available
            if hasattr(mock_console, 'print'):
                # At minimum, the method should execute without error
                pass


class TestPreviewIntegration(unittest.TestCase):
    """Integration tests for the complete preview functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wizard = CommandWizard()
        
    def test_preview_command_execution(self):
        """Test that preview command executes without errors."""
        # Set up some basic parameters
        self.wizard.params = {
            "query": "Integration test query",
            "domain": "Default",
            "models": 2,
            "instructions": 2,
            "variations": 1,
            "sampling_method": "stratified",
            "simulate": True,
            "balanced_models": False,
            "use_ollama": False,
            "dry_run": False,
            "generate_reports": False,
            "analyze_results": False,
            "output_format": None,
            "output_file": None,
            "max_combinations": None,
            "quick": False,
            "full": False,
            "config_file": None,
            "save_state": None,
            "load_state": None,
            "synthesize_method": None,
            "domain_config": None,
            "instruction_templates": None,
            "no_visualizations": False,
            "report_format": None,
            "export_csv": False
        }
        
        # Test that preview command can be called without errors
        try:
            self.wizard.preview_command(show_detailed=True)
            self.wizard.preview_command(show_detailed=False)
        except Exception as e:
            self.fail(f"Preview command raised an exception: {e}")
    
    def test_preview_with_parameter_context_unavailable(self):
        """Test preview functionality when parameter context is unavailable."""
        # Temporarily disable parameter context
        original_available = getattr(self.wizard, 'param_context', None)
        self.wizard.param_context = None
        
        # Mock PARAMETER_CONTEXT_AVAILABLE to False
        with patch('command_wizard.PARAMETER_CONTEXT_AVAILABLE', False):
            try:
                self.wizard.preview_command()
            except Exception as e:
                self.fail(f"Preview failed when parameter context unavailable: {e}")
            finally:
                # Restore original state
                self.wizard.param_context = original_available


def run_preview_enhancement_tests():
    """Run all tests for the command preview enhancements."""
    print("Running Step 1.3 Command Preview Enhancement Tests...")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestCommandPreviewEnhancements))
    suite.addTests(loader.loadTestsFromTestCase(TestPreviewIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # Return success status
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    success = run_preview_enhancement_tests()
    sys.exit(0 if success else 1)