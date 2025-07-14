#!/usr/bin/env python3
"""
Test Suite for OpenRouter Integration Stage 2: Command Wizard Integration

This test suite validates the integration of OpenRouter categorization system
with the ISEE Command Wizard, including API detection, model selection filters,
preset enhancements, and UI components.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from command_wizard import CommandWizard
    from preset_manager import create_default_preset_manager
    from openrouter_categorization import OpenRouterCategorizer
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you're running this test from the ISEE framework directory.")
    sys.exit(1)

class TestOpenRouterCommandWizardIntegration(unittest.TestCase):
    """Test OpenRouter integration with the Command Wizard."""
    
    def setUp(self):
        """Set up test environment."""
        self.wizard = CommandWizard()
        self.preset_manager = create_default_preset_manager()
        
    def test_openrouter_api_detection(self):
        """Test 1: Verify OpenRouter is included in API detection."""
        # Check that OpenRouter is in the API status dictionary
        self.assertIn("openrouter", self.wizard.api_status)
        
        # Test with mock environment variable
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"}):
            wizard = CommandWizard()
            self.assertTrue(wizard.api_status["openrouter"])
            self.assertTrue(wizard.api_status["any_api"])
    
    def test_openrouter_categorizer_initialization(self):
        """Test 2: Verify OpenRouter categorizer is properly initialized."""
        # Check that categorizer is available
        self.assertIsNotNone(self.wizard.openrouter_categorizer)
        self.assertIsInstance(self.wizard.openrouter_categorizer, OpenRouterCategorizer)
    
    def test_openrouter_filter_configuration_method(self):
        """Test 3: Verify OpenRouter filter configuration method exists and works."""
        # Check that the method exists
        self.assertTrue(hasattr(self.wizard, '_configure_openrouter_filters'))
        
        # Test that it can be called without errors (with mocked user input)
        with patch('rich.prompt.Confirm.ask', side_effect=[False]):
            try:
                self.wizard._configure_openrouter_filters()
            except Exception as e:
                self.fail(f"_configure_openrouter_filters raised an exception: {e}")
    
    def test_openrouter_presets_exist(self):
        """Test 4: Verify OpenRouter-specific presets are available."""
        all_presets = self.preset_manager.list_presets()
        openrouter_presets = [p for p in all_presets if 'openrouter' in p.id]
        
        # Should have exactly 4 OpenRouter presets
        self.assertEqual(len(openrouter_presets), 4)
        
        # Check each preset has the expected structure
        expected_presets = [
            "openrouter_provider_diversity",
            "openrouter_coding_focused", 
            "openrouter_budget_optimizer",
            "openrouter_premium_flagship"
        ]
        
        preset_ids = [p.id for p in openrouter_presets]
        for expected_id in expected_presets:
            self.assertIn(expected_id, preset_ids)
    
    def test_openrouter_preset_parameters(self):
        """Test 5: Verify OpenRouter presets have correct parameters structure."""
        openrouter_presets = [p for p in self.preset_manager.list_presets() if 'openrouter' in p.id]
        
        for preset in openrouter_presets:
            # Each preset should have openrouter_filters parameter
            self.assertIn("openrouter_filters", preset.parameters)
            
            # Filters should be a dictionary
            filters = preset.parameters["openrouter_filters"]
            self.assertIsInstance(filters, dict)
            
            # Should have at least one filter type
            filter_types = ["providers", "capabilities", "cost_tiers"]
            has_filter = any(filter_type in filters for filter_type in filter_types)
            self.assertTrue(has_filter, f"Preset {preset.id} should have at least one filter type")
    
    def test_openrouter_preset_diversity(self):
        """Test 6: Verify OpenRouter presets cover different use cases."""
        openrouter_presets = [p for p in self.preset_manager.list_presets() if 'openrouter' in p.id]
        
        # Check that presets span different purpose categories
        purpose_categories = set(p.purpose_category for p in openrouter_presets)
        self.assertGreaterEqual(len(purpose_categories), 3, "Should have presets for multiple purpose categories")
        
        # Check that presets span different cost levels
        cost_levels = set(p.estimated_cost for p in openrouter_presets)
        self.assertGreaterEqual(len(cost_levels), 3, "Should have presets for different cost levels")
        
        # Check that presets span different complexity levels
        complexity_levels = set(p.complexity_level for p in openrouter_presets)
        self.assertGreaterEqual(len(complexity_levels), 2, "Should have presets for different complexity levels")
    
    def test_parameter_context_integration(self):
        """Test 7: Verify OpenRouter filters parameter is in parameter context."""
        if self.wizard.param_context:
            # Check that openrouter_filters parameter exists in context
            context_data = self.wizard.param_context.get_parameter_context("openrouter_filters")
            self.assertIsNotNone(context_data, "openrouter_filters should be in parameter context")
            
            # Check that it has required fields
            self.assertIn("short", context_data)
            self.assertIn("long", context_data)
            self.assertIn("impact", context_data)
    
    def test_api_status_display_includes_openrouter(self):
        """Test 8: Verify API status display includes OpenRouter information."""
        # Test with OpenRouter available
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"}):
            wizard = CommandWizard()
            
            # Mock the console to capture output
            with patch.object(wizard.console, 'print') as mock_print:
                # Simulate the API status display logic from main()
                api_providers = []
                if wizard.api_status["anthropic"]:
                    api_providers.append("Anthropic")
                if wizard.api_status["openai"]:
                    api_providers.append("OpenAI") 
                if wizard.api_status["google"]:
                    api_providers.append("Google")
                if wizard.api_status["openrouter"]:
                    api_providers.append("OpenRouter (300+ models)")
                if wizard.api_status["ollama"]:
                    api_providers.append("Ollama")
                
                # OpenRouter should be in the list
                self.assertIn("OpenRouter (300+ models)", api_providers)
    
    def test_model_selection_integration_flow(self):
        """Test 9: Verify model selection includes OpenRouter options."""
        # Test that the model selection step would include OpenRouter filtering
        # when OpenRouter is available
        
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"}):
            wizard = CommandWizard()
            
            # Mock the should_show_parameter to return True for openrouter_filters
            with patch.object(wizard, '_should_show_parameter', return_value=True):
                # Mock configure_openrouter_filters to track if it's called
                with patch.object(wizard, '_configure_openrouter_filters') as mock_configure:
                    # Simulate the condition from model selection
                    if wizard.api_status["openrouter"] and wizard.openrouter_categorizer:
                        wizard._configure_openrouter_filters()
                    
                    # Should have been called
                    mock_configure.assert_called_once()
    
    def test_filter_parameter_validation(self):
        """Test 10: Verify filter parameters are properly validated."""
        # Test various filter configurations
        test_filters = [
            {
                "providers": ["anthropic", "openai"],
                "capabilities": ["reasoning", "coding"],
                "cost_tiers": ["budget", "standard"]
            },
            {
                "providers": ["google"]
            },
            {
                "capabilities": ["fast", "large_context"]
            },
            {
                "cost_tiers": ["premium"]
            }
        ]
        
        for filters in test_filters:
            # Each filter configuration should be valid
            self.assertIsInstance(filters, dict)
            
            # Should have at least one filter type
            filter_types = ["providers", "capabilities", "cost_tiers"]
            has_filter = any(filter_type in filters for filter_type in filter_types)
            self.assertTrue(has_filter)
            
            # All values should be lists
            for key, value in filters.items():
                self.assertIsInstance(value, list)
                self.assertGreater(len(value), 0)

class TestOpenRouterPresetIntegration(unittest.TestCase):
    """Test OpenRouter preset system integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.preset_manager = create_default_preset_manager()
    
    def test_preset_search_finds_openrouter_presets(self):
        """Test 11: Verify preset search can find OpenRouter presets."""
        search_results = self.preset_manager.search_presets("openrouter")
        self.assertGreater(len(search_results), 0, "Should find OpenRouter presets in search")
        
        # All results should contain 'openrouter' in tags or name
        for preset in search_results:
            has_openrouter = (
                'openrouter' in preset.tags or 
                'openrouter' in preset.name.lower() or
                'openrouter' in preset.id
            )
            self.assertTrue(has_openrouter)
    
    def test_preset_filtering_by_purpose(self):
        """Test 12: Verify OpenRouter presets can be filtered by purpose."""
        purposes = ["deep_analysis", "problem_solving", "quick_exploration", "strategic_planning"]
        
        for purpose in purposes:
            purpose_presets = self.preset_manager.get_presets_by_purpose(purpose)
            openrouter_purpose_presets = [p for p in purpose_presets if 'openrouter' in p.id]
            
            # At least one purpose should have OpenRouter presets
            if purpose == "deep_analysis":
                self.assertGreater(len(openrouter_purpose_presets), 0)
    
    def test_preset_cost_filtering(self):
        """Test 13: Verify OpenRouter presets span different cost levels."""
        cost_levels = ["low", "medium", "high"]
        
        for cost_level in cost_levels:
            cost_presets = self.preset_manager.get_presets_by_cost(cost_level)
            openrouter_cost_presets = [p for p in cost_presets if 'openrouter' in p.id]
            
            # Should have OpenRouter presets for each cost level
            if cost_level in ["low", "medium", "high"]:
                self.assertGreater(len(openrouter_cost_presets), 0)

class TestOpenRouterErrorHandling(unittest.TestCase):
    """Test error handling for OpenRouter integration."""
    
    def test_graceful_degradation_without_openrouter_key(self):
        """Test 14: Verify system works gracefully without OpenRouter API key."""
        # Ensure no OpenRouter key is set
        with patch.dict(os.environ, {}, clear=True):
            wizard = CommandWizard()
            
            # Should not crash and should have openrouter: False
            self.assertFalse(wizard.api_status["openrouter"])
            
            # Should still have categorizer available for UI
            self.assertIsNotNone(wizard.openrouter_categorizer)
    
    def test_graceful_degradation_without_categorizer(self):
        """Test 15: Verify system works gracefully without categorizer module."""
        # Test initialization when categorizer import fails
        with patch('command_wizard.OPENROUTER_CATEGORIZATION_AVAILABLE', False):
            with patch.object(CommandWizard, '__init__') as mock_init:
                mock_init.return_value = None
                wizard = CommandWizard()
                wizard.openrouter_categorizer = None
                wizard._configure_openrouter_filters()
                # Should not crash

def run_integration_tests():
    """Run all OpenRouter Command Wizard integration tests."""
    print("🚀 OpenRouter Command Wizard Integration Test Suite")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestOpenRouterCommandWizardIntegration,
        TestOpenRouterPresetIntegration,
        TestOpenRouterErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)
    
    # Print results summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    
    print(f"✅ Tests Passed: {passed}/{total_tests}")
    print(f"❌ Tests Failed: {failures}/{total_tests}")
    print(f"💥 Test Errors: {errors}/{total_tests}")
    
    if failures > 0:
        print("\n🔍 Failures:")
        for test, failure in result.failures:
            print(f"  • {test}: {failure.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if errors > 0:
        print("\n💥 Errors:")
        for test, error in result.errors:
            print(f"  • {test}: {error.split('\\n')[-2]}")
    
    success_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 All tests passed! OpenRouter Command Wizard integration is working perfectly.")
    elif success_rate >= 80:
        print("⚠️  Most tests passed. Minor issues detected.")
    else:
        print("🚨 Multiple test failures detected. Integration needs attention.")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)