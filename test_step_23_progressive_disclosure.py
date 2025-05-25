#!/usr/bin/env python3
"""
Test suite for Step 2.3: Progressive Disclosure Pattern implementation
Tests the tier system, collapsible sections, and configuration paths.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock, call
from io import StringIO

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from command_wizard import CommandWizard
    COMMAND_WIZARD_AVAILABLE = True
except ImportError:
    COMMAND_WIZARD_AVAILABLE = False
    print("Warning: command_wizard not available for testing")

class TestProgressiveDisclosurePattern(unittest.TestCase):
    """Test suite for Step 2.3 Progressive Disclosure Pattern functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not COMMAND_WIZARD_AVAILABLE:
            self.skipTest("CommandWizard not available")
            
        self.wizard = CommandWizard()
        
    def test_initialization_defaults(self):
        """Test that progressive disclosure settings are properly initialized."""
        self.assertEqual(self.wizard.complexity_level, "basic")
        self.assertFalse(self.wizard.show_advanced_options)
        self.assertEqual(self.wizard.configuration_path, "quick")
        
    def test_parameter_categorization(self):
        """Test that parameters are correctly categorized by complexity."""
        categories = self.wizard._categorize_parameters()
        
        # Verify structure
        self.assertIn("basic", categories)
        self.assertIn("intermediate", categories)
        self.assertIn("advanced", categories)
        self.assertIn("expert", categories)
        
        # Verify basic parameters
        basic_params = categories["basic"]
        self.assertIn("query", basic_params)
        self.assertIn("domain", basic_params)
        self.assertIn("models", basic_params)
        self.assertIn("instructions", basic_params)
        
        # Verify intermediate parameters
        intermediate_params = categories["intermediate"]
        self.assertIn("variations", intermediate_params)
        self.assertIn("sampling_method", intermediate_params)
        self.assertIn("balanced_models", intermediate_params)
        
        # Verify advanced parameters
        advanced_params = categories["advanced"]
        self.assertIn("generate_reports", advanced_params)
        self.assertIn("analyze_results", advanced_params)
        self.assertIn("synthesize_method", advanced_params)
        
        # Verify expert parameters
        expert_params = categories["expert"]
        self.assertIn("save_state", expert_params)
        self.assertIn("load_state", expert_params)
        self.assertIn("domain_config", expert_params)
        
    def test_should_show_parameter_basic_level(self):
        """Test parameter visibility for basic complexity level."""
        self.wizard.complexity_level = "basic"
        self.wizard.show_advanced_options = False
        
        # Basic parameters should always show
        self.assertTrue(self.wizard._should_show_parameter("query"))
        self.assertTrue(self.wizard._should_show_parameter("domain"))
        self.assertTrue(self.wizard._should_show_parameter("models"))
        
        # Intermediate parameters should not show
        self.assertFalse(self.wizard._should_show_parameter("variations"))
        self.assertFalse(self.wizard._should_show_parameter("sampling_method"))
        
        # Advanced parameters should not show
        self.assertFalse(self.wizard._should_show_parameter("generate_reports"))
        self.assertFalse(self.wizard._should_show_parameter("analyze_results"))
        
        # Expert parameters should not show
        self.assertFalse(self.wizard._should_show_parameter("save_state"))
        self.assertFalse(self.wizard._should_show_parameter("domain_config"))
        
    def test_should_show_parameter_advanced_level(self):
        """Test parameter visibility for advanced complexity level."""
        self.wizard.complexity_level = "advanced"
        self.wizard.show_advanced_options = True
        
        # Basic parameters should always show
        self.assertTrue(self.wizard._should_show_parameter("query"))
        self.assertTrue(self.wizard._should_show_parameter("domain"))
        
        # Intermediate parameters should show
        self.assertTrue(self.wizard._should_show_parameter("variations"))
        self.assertTrue(self.wizard._should_show_parameter("sampling_method"))
        
        # Advanced parameters should show when advanced options enabled
        self.assertTrue(self.wizard._should_show_parameter("generate_reports"))
        self.assertTrue(self.wizard._should_show_parameter("analyze_results"))
        
        # Expert parameters should not show
        self.assertFalse(self.wizard._should_show_parameter("save_state"))
        self.assertFalse(self.wizard._should_show_parameter("domain_config"))
        
    def test_should_show_parameter_expert_level(self):
        """Test parameter visibility for expert complexity level."""
        self.wizard.complexity_level = "expert"
        self.wizard.show_advanced_options = True
        
        # All parameters should show in expert level
        self.assertTrue(self.wizard._should_show_parameter("query"))
        self.assertTrue(self.wizard._should_show_parameter("variations"))
        self.assertTrue(self.wizard._should_show_parameter("generate_reports"))
        self.assertTrue(self.wizard._should_show_parameter("save_state"))
        self.assertTrue(self.wizard._should_show_parameter("domain_config"))
        
    def test_advanced_options_toggle_functionality(self):
        """Test the advanced options toggle functionality."""
        self.wizard.complexity_level = "advanced"
        self.wizard.show_advanced_options = False
        
        with patch('rich.prompt.Confirm.ask', return_value=True):
            with patch.object(self.wizard.console, 'print') as mock_print:
                self.wizard._show_advanced_options_toggle()
                
                # Should enable advanced options
                self.assertTrue(self.wizard.show_advanced_options)
                
                # Should print appropriate messages
                mock_print.assert_any_call("\n[dim]💡 Advanced options are available for this configuration level[/dim]")
                mock_print.assert_any_call("[green]✓ Advanced options enabled[/green]")
                
    def test_advanced_options_toggle_declined(self):
        """Test declining advanced options toggle."""
        self.wizard.complexity_level = "advanced"
        self.wizard.show_advanced_options = False
        
        with patch('rich.prompt.Confirm.ask', return_value=False):
            with patch.object(self.wizard.console, 'print') as mock_print:
                self.wizard._show_advanced_options_toggle()
                
                # Should keep advanced options disabled
                self.assertFalse(self.wizard.show_advanced_options)
                
                # Should print decline message
                mock_print.assert_any_call("[dim]Advanced options remain hidden (you can enable them later)[/dim]")
                
    def test_configuration_path_selection_quick(self):
        """Test selecting quick configuration path."""
        with patch('rich.prompt.Prompt.ask', return_value="1"):
            with patch.object(self.wizard.console, 'print') as mock_print:
                self.wizard._select_configuration_path()
                
                # Should set quick configuration
                self.assertEqual(self.wizard.configuration_path, "quick")
                self.assertEqual(self.wizard.complexity_level, "basic")
                self.assertFalse(self.wizard.show_advanced_options)
                
                # Should print success message
                mock_print.assert_any_call("[green]✓ Selected: 🚀 Quick Configuration[/green]")
                
    def test_configuration_path_selection_detailed(self):
        """Test selecting detailed configuration path."""
        with patch('rich.prompt.Prompt.ask', return_value="2"):
            with patch.object(self.wizard.console, 'print') as mock_print:
                self.wizard._select_configuration_path()
                
                # Should set detailed configuration
                self.assertEqual(self.wizard.configuration_path, "detailed")
                self.assertEqual(self.wizard.complexity_level, "advanced")
                self.assertTrue(self.wizard.show_advanced_options)
                
                # Should print success and advanced options messages
                mock_print.assert_any_call("[green]✓ Selected: ⚙️ Detailed Configuration[/green]")
                mock_print.assert_any_call("[dim]Advanced options will be available throughout the wizard[/dim]")
                
    def test_configuration_path_selection_expert(self):
        """Test selecting expert configuration path."""
        with patch('rich.prompt.Prompt.ask', return_value="3"):
            with patch.object(self.wizard.console, 'print') as mock_print:
                self.wizard._select_configuration_path()
                
                # Should set expert configuration
                self.assertEqual(self.wizard.configuration_path, "detailed")
                self.assertEqual(self.wizard.complexity_level, "expert")
                self.assertTrue(self.wizard.show_advanced_options)
                
                # Should print success and advanced options messages
                mock_print.assert_any_call("[green]✓ Selected: 🔧 Expert Configuration[/green]")
                mock_print.assert_any_call("[dim]Advanced options will be available throughout the wizard[/dim]")
                
    def test_configuration_path_selection_defaults(self):
        """Test using defaults (option 0)."""
        with patch('rich.prompt.Prompt.ask', return_value="0"):
            with patch.object(self.wizard.console, 'print') as mock_print:
                self.wizard._select_configuration_path()
                
                # Should use defaults
                self.assertEqual(self.wizard.configuration_path, "quick")
                self.assertEqual(self.wizard.complexity_level, "basic")
                self.assertFalse(self.wizard.show_advanced_options)
                
                # Should print default message
                mock_print.assert_any_call("[green]Using Quick Configuration with smart defaults[/green]")
                
    def test_configuration_path_invalid_then_valid(self):
        """Test handling invalid input then valid input."""
        with patch('rich.prompt.Prompt.ask', side_effect=["invalid", "1"]):
            with patch.object(self.wizard.console, 'print') as mock_print:
                self.wizard._select_configuration_path()
                
                # Should eventually set quick configuration
                self.assertEqual(self.wizard.configuration_path, "quick")
                self.assertEqual(self.wizard.complexity_level, "basic")
                
                # Should print error message for invalid input
                mock_print.assert_any_call("[red]Please enter 1, 2, 3, or 0[/red]")
                
    def test_parameter_filtering_in_workflow(self):
        """Test that parameters are filtered based on complexity level during workflow."""
        # Set basic level
        self.wizard.complexity_level = "basic"
        self.wizard.show_advanced_options = False
        
        # Mock the parameter context to avoid import issues
        self.wizard.param_context = None
        
        # Test that advanced parameters are not shown
        self.assertFalse(self.wizard._should_show_parameter("variations"))
        self.assertFalse(self.wizard._should_show_parameter("sampling_method"))
        self.assertFalse(self.wizard._should_show_parameter("generate_reports"))
        
        # Set advanced level
        self.wizard.complexity_level = "advanced"
        self.wizard.show_advanced_options = True
        
        # Test that intermediate and advanced parameters are shown
        self.assertTrue(self.wizard._should_show_parameter("variations"))
        self.assertTrue(self.wizard._should_show_parameter("sampling_method"))
        self.assertTrue(self.wizard._should_show_parameter("generate_reports"))
        
        # But expert parameters still hidden
        self.assertFalse(self.wizard._should_show_parameter("domain_config"))
        
    def test_complexity_level_affects_headers(self):
        """Test that complexity level affects section headers in advanced options."""
        # Mock all the prompts to avoid interactive input
        with patch('rich.prompt.Confirm.ask', return_value=False):
            with patch.object(self.wizard.console, 'print') as mock_print:
                # Test expert level header
                self.wizard.complexity_level = "expert"
                result = self.wizard.configure_advanced_options(8)
                
                # Should show expert configuration header
                mock_print.assert_any_call("\n[bold cyan]Step 8: Expert Configuration[/bold cyan]")
                
        with patch('rich.prompt.Confirm.ask', return_value=False):
            with patch.object(self.wizard.console, 'print') as mock_print:
                # Test advanced level header
                self.wizard.complexity_level = "advanced"
                result = self.wizard.configure_advanced_options(8)
                
                # Should show advanced options header
                mock_print.assert_any_call("\n[bold cyan]Step 8: Advanced Options[/bold cyan]")
            
    def test_integration_with_existing_features(self):
        """Test that progressive disclosure integrates well with existing features."""
        # Test that purpose selection still works
        self.wizard.complexity_level = "basic"
        self.assertIsNotNone(self.wizard.purpose_manager)
        
        # Test that preset selection still works
        self.assertIsNotNone(self.wizard.preset_manager)
        
        # Test that cost estimation still works
        self.assertIsNotNone(self.wizard.cost_estimator)
        
        # Test that parameter context still works
        self.assertIsNotNone(self.wizard.param_context)

def run_progressive_disclosure_tests():
    """Run all progressive disclosure tests and return results."""
    if not COMMAND_WIZARD_AVAILABLE:
        print("❌ CommandWizard not available - skipping progressive disclosure tests")
        return False
        
    print("🧪 Running Step 2.3 Progressive Disclosure Pattern Tests...")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestProgressiveDisclosurePattern)
    
    # Run tests with detailed output
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    
    # Print results
    output = stream.getvalue()
    print(output)
    
    # Summary
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    
    print(f"\n📊 Test Results Summary:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {total_tests - failures - errors - skipped}")
    print(f"   Failed: {failures}")
    print(f"   Errors: {errors}")
    print(f"   Skipped: {skipped}")
    
    if failures > 0:
        print(f"\n❌ Failures:")
        for test, failure in result.failures:
            print(f"   {test}: {failure}")
            
    if errors > 0:
        print(f"\n💥 Errors:")
        for test, error in result.errors:
            print(f"   {test}: {error}")
    
    success = failures == 0 and errors == 0
    status = "✅ All tests passed!" if success else "❌ Some tests failed!"
    print(f"\n{status}")
    
    return success

if __name__ == "__main__":
    success = run_progressive_disclosure_tests()
    sys.exit(0 if success else 1)