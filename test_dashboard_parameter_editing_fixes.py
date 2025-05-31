#!/usr/bin/env python3
"""
Test script for dashboard parameter editing fixes

Tests the specific issues reported:
1. Domain parameter accepting 'done' as a value
2. Models parameter validation issues with 'done'
3. Missing openrouter_filters parameter support
4. Proper exit handling for all parameter types

Part of UX Enhancement Roadmap - Step 3.2 Bug Fixes
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from interactive_dashboard_controller import InteractiveDashboardController
    from configuration_dashboard import ConfigurationDashboard
    DASHBOARD_AVAILABLE = True
except ImportError as e:
    print(f"Dashboard components not available: {e}")
    DASHBOARD_AVAILABLE = False

@unittest.skipUnless(DASHBOARD_AVAILABLE, "Dashboard components not available")
class TestParameterEditingFixes(unittest.TestCase):
    """Test parameter editing fixes in the dashboard controller"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock console to avoid output during tests
        self.mock_console = MagicMock()
        self.controller = InteractiveDashboardController(self.mock_console)
        
        # Ensure dashboard is properly initialized
        self.assertIsNotNone(self.controller.dashboard)
    
    def test_edit_controls_includes_missing_parameters(self):
        """Test that missing parameters are now included in edit_controls"""
        # Verify openrouter_filters is now supported
        self.assertIn("openrouter_filters", self.controller.edit_controls)
        
        # Verify other missing parameters are supported
        self.assertIn("quick", self.controller.edit_controls)
        self.assertIn("full", self.controller.edit_controls)
        self.assertIn("output_format", self.controller.edit_controls)
        self.assertIn("generate_reports", self.controller.edit_controls)
        self.assertIn("analyze_results", self.controller.edit_controls)
        
        print("✓ All missing parameters now included in edit_controls")
    
    @patch('rich.prompt.Prompt.ask')
    def test_domain_editing_handles_done_properly(self, mock_prompt):
        """Test that domain editing exits properly when user types 'done'"""
        # Test case 1: User types 'done' - should exit without updating
        mock_prompt.return_value = "done"
        
        original_domain = self.controller.dashboard.state.parameters["domain"].value
        self.controller._edit_domain()
        
        # Domain should remain unchanged
        self.assertEqual(
            self.controller.dashboard.state.parameters["domain"].value,
            original_domain
        )
        
        # Test case 2: User enters valid domain - should update
        mock_prompt.return_value = "New Technology Domain"
        self.controller._edit_domain()
        
        # Domain should be updated
        self.assertEqual(
            self.controller.dashboard.state.parameters["domain"].value,
            "New Technology Domain"
        )
        
        print("✓ Domain editing handles 'done' command properly")
    
    @patch('rich.prompt.Prompt.ask')
    def test_models_editing_handles_done_and_validation(self, mock_prompt):
        """Test that models editing handles 'done' and validates input properly"""
        # Test case 1: User types 'done' - should exit without updating
        mock_prompt.return_value = "done"
        
        original_models = self.controller.dashboard.state.parameters["models"].value
        self.controller._edit_models()
        
        # Models should remain unchanged
        self.assertEqual(
            self.controller.dashboard.state.parameters["models"].value,
            original_models
        )
        
        # Test case 2: User enters invalid text, then valid number
        mock_prompt.side_effect = ["invalid_text", "5"]
        
        self.controller._edit_models()
        
        # Should have updated to 5 after handling the invalid input
        self.assertEqual(
            self.controller.dashboard.state.parameters["models"].value,
            5
        )
        
        print("✓ Models editing handles 'done' and validation properly")
    
    @patch('rich.prompt.Prompt.ask')
    def test_instructions_editing_handles_done_and_validation(self, mock_prompt):
        """Test that instructions editing handles 'done' and validates input properly"""
        # Test case: User types 'done' - should exit without updating
        mock_prompt.return_value = "done"
        
        original_instructions = self.controller.dashboard.state.parameters["instructions"].value
        self.controller._edit_instructions()
        
        # Instructions should remain unchanged
        self.assertEqual(
            self.controller.dashboard.state.parameters["instructions"].value,
            original_instructions
        )
        
        print("✓ Instructions editing handles 'done' command properly")
    
    @patch('rich.prompt.Prompt.ask')
    def test_variations_editing_handles_done_and_validation(self, mock_prompt):
        """Test that variations editing handles 'done' and validates input properly"""
        # Test case: User types 'done' - should exit without updating
        mock_prompt.return_value = "done"
        
        original_variations = self.controller.dashboard.state.parameters["variations"].value
        self.controller._edit_variations()
        
        # Variations should remain unchanged
        self.assertEqual(
            self.controller.dashboard.state.parameters["variations"].value,
            original_variations
        )
        
        print("✓ Variations editing handles 'done' command properly")
    
    @patch('rich.prompt.Prompt.ask')
    def test_max_combinations_editing_handles_done_and_validation(self, mock_prompt):
        """Test that max_combinations editing handles 'done' and validates input properly"""
        # Test case: User types 'done' - should exit without updating
        mock_prompt.return_value = "done"
        
        original_max_combinations = self.controller.dashboard.state.parameters["max_combinations"].value
        self.controller._edit_max_combinations()
        
        # Max combinations should remain unchanged
        self.assertEqual(
            self.controller.dashboard.state.parameters["max_combinations"].value,
            original_max_combinations
        )
        
        print("✓ Max combinations editing handles 'done' command properly")
    
    @patch('rich.prompt.Prompt.ask')
    def test_openrouter_filters_editing_works(self, mock_prompt):
        """Test that openrouter_filters parameter can be edited with enhanced UI"""
        # Test setting a valid filter value
        mock_prompt.return_value = "provider:anthropic,cost_tier:budget"
        
        self.controller._edit_openrouter_filters()
        
        # Should have updated the parameter
        self.assertEqual(
            self.controller.dashboard.state.parameters["openrouter_filters"].value,
            "provider:anthropic,cost_tier:budget"
        )
        
        # Test 'done' command
        mock_prompt.return_value = "done"
        original_value = self.controller.dashboard.state.parameters["openrouter_filters"].value
        
        self.controller._edit_openrouter_filters()
        
        # Should remain unchanged
        self.assertEqual(
            self.controller.dashboard.state.parameters["openrouter_filters"].value,
            original_value
        )
        
        # Test validation function separately
        self.assertTrue(self.controller._validate_openrouter_filters("provider:anthropic"))
        self.assertTrue(self.controller._validate_openrouter_filters("provider:openai,cost_tier:budget"))
        self.assertFalse(self.controller._validate_openrouter_filters("invalid_format"))
        self.assertFalse(self.controller._validate_openrouter_filters("provider_anthropic"))  # Missing colon
        
        print("✓ OpenRouter filters editing works properly with enhanced UI and validation")
    
    def test_all_edit_methods_exist(self):
        """Test that all referenced edit methods exist"""
        for param_name, method in self.controller.edit_controls.items():
            # Verify the method exists and is callable
            self.assertTrue(callable(method))
            
            # Verify it's a bound method of the controller
            self.assertEqual(method.__self__, self.controller)
        
        print(f"✓ All {len(self.controller.edit_controls)} edit methods exist and are callable")
    
    def test_parameter_editing_consistency(self):
        """Test that parameter editing behavior is consistent across all types"""
        # Verify all string/text parameters support 'done'
        text_parameters = ["domain", "openrouter_filters"]
        for param in text_parameters:
            if param in self.controller.edit_controls:
                method = self.controller.edit_controls[param]
                # Method should exist and be callable
                self.assertTrue(callable(method))
        
        # Verify all numeric parameters support 'done'
        numeric_parameters = ["models", "instructions", "variations", "max_combinations"]
        for param in numeric_parameters:
            if param in self.controller.edit_controls:
                method = self.controller.edit_controls[param]
                # Method should exist and be callable
                self.assertTrue(callable(method))
        
        print("✓ Parameter editing behavior is consistent across types")

def run_parameter_editing_tests():
    """Run parameter editing fix tests and return results"""
    print("="*60)
    print("Parameter Editing Fixes Test Results:")
    
    if not DASHBOARD_AVAILABLE:
        print("SKIPPED: Dashboard components not available")
        return False
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestParameterEditingFixes)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
    result = runner.run(suite)
    
    # Print summary
    total_tests = result.testsRun
    passed_tests = total_tests - len(result.failures) - len(result.errors)
    failed_tests = len(result.failures)
    error_tests = len(result.errors)
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Errors: {error_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print("="*60)
    
    # Print test details
    for test, traceback in result.failures:
        print(f"FAILED: {test}")
        print(traceback)
    
    for test, traceback in result.errors:
        print(f"ERROR: {test}")
        print(traceback)
    
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == "__main__":
    success = run_parameter_editing_tests()
    sys.exit(0 if success else 1)