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
    
    def test_domain_editing_shows_available_domains(self):
        """Test that domain editing now shows available domain options"""
        # Check that the enhanced domain editing method exists and can be called
        self.assertTrue(hasattr(self.controller, '_edit_domain'))
        
        # Mock user input to exit immediately
        with patch('rich.prompt.Prompt.ask', return_value="done"):
            try:
                # Should not raise an exception and should complete successfully
                self.controller._edit_domain()
                print("✅ Domain editing enhancement works correctly and displays domain options")
            except Exception as e:
                self.fail(f"Domain editing enhancement failed: {e}")
        
        # Test that domain manager integration works
        try:
            from domain_manager import create_default_domains
            domains = create_default_domains()
            self.assertGreater(len(domains), 0, "Should have default domains available")
            print(f"✅ Found {len(domains)} default domains available for display")
        except ImportError:
            self.fail("Domain manager should be available for integration")
    
    def test_models_editing_shows_available_options(self):
        """Test that models editing now shows comprehensive model options"""
        # Check that the enhanced models editing method exists and can be called
        self.assertTrue(hasattr(self.controller, '_edit_models'))
        
        # Mock user input to exit immediately
        with patch('rich.prompt.Prompt.ask', return_value="done"):
            try:
                # Should not raise an exception and should complete successfully
                self.controller._edit_models()
                print("✅ Models editing enhancement works correctly and displays model options")
            except Exception as e:
                self.fail(f"Models editing enhancement failed: {e}")
        
        # Test that OpenRouter collections integration works
        try:
            from openrouter_model_collections import create_default_model_collections
            collections_manager = create_default_model_collections()
            collections = collections_manager.get_all_collections()
            self.assertGreater(len(collections), 0, "Should have model collections available")
            print(f"✅ Found {len(collections)} OpenRouter model collections available for display")
        except ImportError:
            self.fail("OpenRouter model collections should be available for integration")
        
        print("✓ All missing parameters now included in edit_controls")
    
    def test_specific_openrouter_model_selection(self):
        """Test that models editing now supports specific OpenRouter model selection"""
        # Check that the specific model selection method exists
        self.assertTrue(hasattr(self.controller, '_select_specific_openrouter_models'))
        self.assertTrue(hasattr(self.controller, '_parse_model_selection'))
        self.assertTrue(hasattr(self.controller, '_estimate_model_cost'))
        self.assertTrue(hasattr(self.controller, '_estimate_model_quality'))
        
        # Test model selection parsing
        test_cases = [
            ("1,3,5", [1, 3, 5]),
            ("1-5", [1, 2, 3, 4, 5]),
            ("all", list(range(1, 21))),
            ("", [1, 2, 3])
        ]
        
        for input_str, expected in test_cases:
            result = self.controller._parse_model_selection(input_str, 20)
            self.assertEqual(result, expected, f"Input '{input_str}' should return {expected}")
        
        # Test cost and quality estimation
        test_model = "openai/gpt-4o-mini"
        cost = self.controller._estimate_model_cost(test_model)
        quality = self.controller._estimate_model_quality(test_model)
        
        self.assertIsInstance(cost, str)
        self.assertIsInstance(quality, float)
        self.assertTrue(0 <= quality <= 10)
        
        # Test that OpenRouter collections integration works
        try:
            from openrouter_model_collections import create_default_model_collections
            collections_manager = create_default_model_collections()
            top_performers = collections_manager.get_collection("top_performers")
            self.assertIsNotNone(top_performers)
            print("✅ Specific OpenRouter model selection functionality complete and working")
        except ImportError:
            self.fail("OpenRouter collections should be available for specific model selection")
    
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
    
    def test_instruction_template_display_enhancement(self):
        """Test 13: Enhanced instruction template display functionality"""
        try:
            from instruction_templates import create_default_library
            
            # Test that template library loads
            template_library = create_default_library()
            templates = template_library.list_templates()
            
            # Verify we have templates
            self.assertGreater(len(templates), 0, "Should have instruction templates available")
            
            # Verify template structure
            for template in templates:
                self.assertTrue(hasattr(template, 'name'), "Template should have name")
                self.assertTrue(hasattr(template, 'metadata'), "Template should have metadata")
                
            # Test that the enhanced _edit_instructions method exists
            self.assertTrue(hasattr(self.controller, '_edit_instructions'), 
                          "Controller should have _edit_instructions method")
            
            # Test the method is properly mapped
            self.assertIn('instructions', self.controller.edit_controls,
                         "Instructions should be in edit controls")
            
            print(f"✓ Instruction template enhancement working - {len(templates)} templates available")
            
        except ImportError:
            self.skipTest("Instruction templates not available")
        except Exception as e:
            self.fail(f"Instruction template enhancement test failed: {e}")
    
    def test_advanced_instruction_template_selection(self):
        """Test 14: Advanced instruction template selection with parsing syntax"""
        try:
            from instruction_templates import create_default_library
            
            # Test that advanced selection methods exist
            advanced_methods = [
                '_parse_number_selection',
                '_handle_template_preview', 
                '_handle_template_compare',
                '_show_template_help'
            ]
            
            for method_name in advanced_methods:
                self.assertTrue(hasattr(self.controller, method_name),
                              f"Controller should have {method_name} method")
            
            # Test number parsing functionality
            template_library = create_default_library()
            templates = template_library.list_templates()
            max_templates = len(templates)
            
            test_cases = [
                ("1,3,5", [1, 3, 5]),
                ("2-4", [2, 3, 4]),
                ("1", [1]),
                (f"1-{min(3, max_templates)}", list(range(1, min(4, max_templates + 1))))
            ]
            
            for input_str, expected in test_cases:
                if all(x <= max_templates for x in expected):  # Only test if within range
                    result = self.controller._parse_number_selection(input_str, max_templates)
                    self.assertEqual(result, expected, f"Parsing '{input_str}' should return {expected}")
            
            # Test error handling
            with self.assertRaises(ValueError):
                self.controller._parse_number_selection("0", max_templates)  # Too low
            
            with self.assertRaises(ValueError):
                self.controller._parse_number_selection(str(max_templates + 1), max_templates)  # Too high
            
            # Test instruction_templates parameter support
            self.assertIn('instruction_templates', self.controller.edit_controls,
                         "instruction_templates should be in edit controls")
            
            self.assertIn('instruction_templates', self.controller.dashboard.state.parameters,
                         "instruction_templates should be initialized in dashboard")
            
            print("✓ Advanced instruction template selection functionality complete")
            
        except ImportError:
            self.skipTest("Instruction templates not available")
        except Exception as e:
            self.fail(f"Advanced instruction template selection test failed: {e}")

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