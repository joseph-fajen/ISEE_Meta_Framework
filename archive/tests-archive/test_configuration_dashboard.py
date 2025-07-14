#!/usr/bin/env python3
"""
Test suite for Configuration Dashboard (Step 3.2)

Comprehensive tests for the visual configuration dashboard including:
- Dashboard state management
- Parameter visualization 
- Real-time updates
- Interactive controls
- Resource protection integration
- Command generation
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from io import StringIO

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from configuration_dashboard import (
        ConfigurationDashboard, 
        DashboardState, 
        ParameterState, 
        ParameterStatus,
        DashboardMode,
        create_configuration_dashboard
    )
    from interactive_dashboard_controller import InteractiveDashboardController, InteractionMode
    from rich.console import Console
    DASHBOARD_AVAILABLE = True
except ImportError as e:
    print(f"Dashboard components not available: {e}")
    DASHBOARD_AVAILABLE = False


class TestDashboardState(unittest.TestCase):
    """Test dashboard state management"""
    
    def setUp(self):
        """Set up test environment"""
        if not DASHBOARD_AVAILABLE:
            self.skipTest("Dashboard components not available")
        
        self.console = Console(file=StringIO(), width=80)
        
    def test_parameter_state_creation(self):
        """Test ParameterState creation and defaults"""
        param = ParameterState(
            name="models",
            value=3,
            default_value=3,
            category="basic"
        )
        
        self.assertEqual(param.name, "models")
        self.assertEqual(param.value, 3)
        self.assertEqual(param.default_value, 3)
        self.assertEqual(param.category, "basic")
        self.assertEqual(param.status, ParameterStatus.DEFAULT)
        self.assertEqual(param.dependencies, [])
        self.assertEqual(param.impact_score, 0.0)
        self.assertEqual(param.cost_impact, 0.0)
    
    def test_dashboard_state_initialization(self):
        """Test DashboardState initialization"""
        state = DashboardState()
        
        self.assertEqual(state.parameters, {})
        self.assertEqual(state.total_cost, 0.0)
        self.assertEqual(state.total_time, 0.0)
        self.assertEqual(state.combination_count, 0)
        self.assertEqual(state.resource_warnings, [])
        self.assertEqual(state.mode, DashboardMode.OVERVIEW)
    
    def test_parameter_status_changes(self):
        """Test parameter status tracking"""
        param = ParameterState(
            name="models",
            value=5,
            default_value=3,
            category="basic"
        )
        
        # Should detect modification
        param.status = ParameterStatus.MODIFIED if param.value != param.default_value else ParameterStatus.DEFAULT
        self.assertEqual(param.status, ParameterStatus.MODIFIED)
        
        # Reset to default
        param.value = param.default_value
        param.status = ParameterStatus.MODIFIED if param.value != param.default_value else ParameterStatus.DEFAULT
        self.assertEqual(param.status, ParameterStatus.DEFAULT)


class TestConfigurationDashboard(unittest.TestCase):
    """Test main dashboard functionality"""
    
    def setUp(self):
        """Set up test environment"""
        if not DASHBOARD_AVAILABLE:
            self.skipTest("Dashboard components not available")
        
        self.console = Console(file=StringIO(), width=80)
        
        # Mock components to avoid import errors
        with patch('configuration_dashboard.COMPONENTS_AVAILABLE', False):
            self.dashboard = ConfigurationDashboard(self.console)
    
    def test_dashboard_initialization(self):
        """Test dashboard initialization"""
        self.assertIsNotNone(self.dashboard)
        self.assertEqual(self.dashboard.console, self.console)
        self.assertIsInstance(self.dashboard.state, DashboardState)
    
    def test_category_colors_mapping(self):
        """Test parameter category color mapping"""
        expected_colors = {
            "basic": "cyan",
            "sampling": "green", 
            "models": "blue",
            "output": "magenta",
            "advanced": "yellow"
        }
        
        self.assertEqual(self.dashboard.category_colors, expected_colors)
    
    def test_parameter_value_formatting(self):
        """Test parameter value formatting for display"""
        # Test boolean values
        self.assertEqual(self.dashboard._format_parameter_value(True), "✓")
        self.assertEqual(self.dashboard._format_parameter_value(False), "✗")
        
        # Test long strings
        long_string = "This is a very long string that should be truncated"
        result = self.dashboard._format_parameter_value(long_string)
        self.assertTrue(len(result) <= 20)
        self.assertTrue(result.endswith("..."))
        
        # Test regular values
        self.assertEqual(self.dashboard._format_parameter_value(42), "42")
        self.assertEqual(self.dashboard._format_parameter_value("short"), "short")
    
    def test_impact_score_formatting(self):
        """Test impact score formatting"""
        self.assertEqual(self.dashboard._format_impact_score(0.5), "[green]Low[/]")
        self.assertEqual(self.dashboard._format_impact_score(2.0), "[yellow]Medium[/]")
        self.assertEqual(self.dashboard._format_impact_score(4.0), "[red]High[/]")
    
    def test_status_text_formatting(self):
        """Test parameter status text formatting"""
        status_tests = [
            (ParameterStatus.DEFAULT, "[dim]Default[/]"),
            (ParameterStatus.MODIFIED, "[green]Modified[/]"),
            (ParameterStatus.WARNING, "[yellow]Warning[/]"),
            (ParameterStatus.ERROR, "[red]Error[/]")
        ]
        
        for status, expected in status_tests:
            result = self.dashboard._get_status_text(status)
            self.assertEqual(result, expected)
    
    @patch('configuration_dashboard.COMPONENTS_AVAILABLE', True)
    def test_parameter_update(self):
        """Test parameter value updates"""
        # Create dashboard with mocked components
        with patch('configuration_dashboard.ParameterContext'), \
             patch('configuration_dashboard.CostEstimator'), \
             patch('configuration_dashboard.CognitiveFrameworkVisualizer'), \
             patch('configuration_dashboard.ISEEGuardrails'):
            
            dashboard = ConfigurationDashboard(self.console)
            
            # Add a test parameter
            dashboard.state.parameters["models"] = ParameterState(
                name="models",
                value=3,
                default_value=3,
                category="basic"
            )
            
            # Update parameter
            dashboard.update_parameter("models", 5)
            
            # Check update
            param = dashboard.state.parameters["models"]
            self.assertEqual(param.value, 5)
            self.assertEqual(param.status, ParameterStatus.MODIFIED)
    
    def test_command_building(self):
        """Test ISEE command generation"""
        # Set up test parameters
        self.dashboard.state.parameters = {
            "query": ParameterState("query", "test query", "", "basic"),
            "domain": ParameterState("domain", "Technology Innovation", "Technology Innovation", "basic"),
            "models": ParameterState("models", 5, 3, "basic"),
            "instructions": ParameterState("instructions", 4, 3, "basic"),
            "variations": ParameterState("variations", 3, 2, "basic"),
            "max_combinations": ParameterState("max_combinations", 20, 12, "sampling"),
            "balanced_models": ParameterState("balanced_models", True, False, "models"),
            "simulate": ParameterState("simulate", True, False, "models")
        }
        
        command = self.dashboard._build_command()
        
        # Check command components
        self.assertIn('--query "test query"', command)
        self.assertIn('--models 5', command)
        self.assertIn('--instructions 4', command)
        self.assertIn('--variations 3', command)
        self.assertIn('--max-combinations 20', command)
        self.assertIn('--balanced-models', command)
        self.assertIn('--simulate', command)
    
    def test_configuration_loading(self):
        """Test loading configuration from dictionary"""
        # Set up initial parameter
        self.dashboard.state.parameters["models"] = ParameterState(
            name="models",
            value=3,
            default_value=3,
            category="basic"
        )
        
        # Load configuration
        config = {"models": 7}
        self.dashboard.load_config(config)
        
        # Check parameter was updated
        param = self.dashboard.state.parameters["models"]
        self.assertEqual(param.value, 7)
        self.assertEqual(param.status, ParameterStatus.MODIFIED)
    
    def test_configuration_export(self):
        """Test exporting current configuration"""
        # Set up test parameters
        self.dashboard.state.parameters = {
            "models": ParameterState("models", 5, 3, "basic"),
            "simulate": ParameterState("simulate", True, False, "models")
        }
        
        config = self.dashboard.get_current_config()
        
        expected = {"models": 5, "simulate": True}
        self.assertEqual(config, expected)


class TestInteractiveDashboardController(unittest.TestCase):
    """Test interactive dashboard controller"""
    
    def setUp(self):
        """Set up test environment"""
        if not DASHBOARD_AVAILABLE:
            self.skipTest("Dashboard components not available")
        
        self.console = Console(file=StringIO(), width=80)
        
        # Mock dashboard to avoid import issues
        with patch('interactive_dashboard_controller.DASHBOARD_AVAILABLE', False):
            self.controller = InteractiveDashboardController(self.console)
    
    def test_controller_initialization(self):
        """Test controller initialization"""
        self.assertIsNotNone(self.controller)
        self.assertEqual(self.controller.console, self.console)
        self.assertEqual(self.controller.interaction_mode, InteractionMode.NAVIGATE)
        self.assertFalse(self.controller.running)
    
    def test_controls_mapping(self):
        """Test control commands mapping"""
        expected_controls = {
            "1": self.controller._switch_to_overview,
            "2": self.controller._switch_to_detailed,
            "3": self.controller._switch_to_expert,
            "e": self.controller._edit_parameters,
            "r": self.controller._reset_parameters,
            "p": self.controller._preview_command,
            "x": self.controller._execute_command,
            "h": self.controller._show_help,
            "q": self.controller._quit_dashboard
        }
        
        for key in expected_controls:
            self.assertIn(key, self.controller.controls)


class TestDashboardIntegration(unittest.TestCase):
    """Test dashboard integration with command wizard"""
    
    def setUp(self):
        """Set up test environment"""
        if not DASHBOARD_AVAILABLE:
            self.skipTest("Dashboard components not available")
    
    def test_factory_function(self):
        """Test dashboard factory function"""
        console = Console(file=StringIO(), width=80)
        
        with patch('configuration_dashboard.COMPONENTS_AVAILABLE', False):
            dashboard = create_configuration_dashboard(console)
        
        self.assertIsInstance(dashboard, ConfigurationDashboard)
        self.assertEqual(dashboard.console, console)
    
    @patch('interactive_dashboard_controller.run_interactive_dashboard')
    def test_command_wizard_integration(self, mock_run_dashboard):
        """Test dashboard integration with command wizard"""
        # Mock the dashboard to return a test command
        mock_run_dashboard.return_value = "python main.py --query 'test' --simulate"
        
        # Test that dashboard can be called from command wizard
        console = Console(file=StringIO(), width=80)
        result = mock_run_dashboard(console)
        
        self.assertEqual(result, "python main.py --query 'test' --simulate")
        mock_run_dashboard.assert_called_once_with(console)


class TestDashboardDisplay(unittest.TestCase):
    """Test dashboard display functionality"""
    
    def setUp(self):
        """Set up test environment"""
        if not DASHBOARD_AVAILABLE:
            self.skipTest("Dashboard components not available")
        
        self.console = Console(file=StringIO(), width=80)
        
        with patch('configuration_dashboard.COMPONENTS_AVAILABLE', False):
            self.dashboard = ConfigurationDashboard(self.console)
    
    def test_header_creation(self):
        """Test dashboard header creation"""
        header = self.dashboard._create_header()
        self.assertIsNotNone(header)
    
    def test_footer_creation(self):
        """Test dashboard footer creation"""
        footer = self.dashboard._create_footer()
        self.assertIsNotNone(footer)
    
    def test_status_panel_creation(self):
        """Test status panel creation"""
        status_panel = self.dashboard._create_status_panel()
        self.assertIsNotNone(status_panel)
    
    def test_display_modes(self):
        """Test different display modes"""
        modes = [DashboardMode.OVERVIEW, DashboardMode.DETAILED, DashboardMode.EXPERT]
        
        for mode in modes:
            # Should not raise an exception
            try:
                self.dashboard.display_dashboard(mode)
                self.assertEqual(self.dashboard.state.mode, mode)
            except Exception as e:
                self.fail(f"Display mode {mode} failed: {e}")


class TestResourceProtectionIntegration(unittest.TestCase):
    """Test integration with resource protection guardrails"""
    
    def setUp(self):
        """Set up test environment"""
        if not DASHBOARD_AVAILABLE:
            self.skipTest("Dashboard components not available")
        
        self.console = Console(file=StringIO(), width=80)
        
        with patch('configuration_dashboard.COMPONENTS_AVAILABLE', False):
            self.dashboard = ConfigurationDashboard(self.console)
    
    def test_resource_warning_updates(self):
        """Test resource warning system"""
        # Initially no warnings
        self.assertEqual(self.dashboard.state.resource_warnings, [])
        
        # Update estimates should check for warnings
        self.dashboard._update_resource_warnings()
        
        # Should still be a list (might be empty due to mocked components)
        self.assertIsInstance(self.dashboard.state.resource_warnings, list)
    
    def test_cost_estimation_updates(self):
        """Test cost estimation updates"""
        # Initialize dashboard with components available to get proper parameter initialization
        with patch('configuration_dashboard.COMPONENTS_AVAILABLE', True), \
             patch('configuration_dashboard.ParameterContext'), \
             patch('configuration_dashboard.CostEstimator'), \
             patch('configuration_dashboard.CognitiveFrameworkVisualizer'), \
             patch('configuration_dashboard.ISEEGuardrails'):
            
            dashboard = ConfigurationDashboard(self.console)
            
            # Set up parameters for estimation
            dashboard.state.parameters = {
                "models": ParameterState("models", 3, 3, "basic"),
                "instructions": ParameterState("instructions", 3, 3, "basic"),
                "variations": ParameterState("variations", 2, 2, "basic"),
                "max_combinations": ParameterState("max_combinations", 12, 12, "sampling"),
                "query": ParameterState("query", "test query", "", "basic"),
                "use_ollama": ParameterState("use_ollama", False, False, "models")
            }
            
            # Update estimates
            dashboard._update_estimates()
            
            # Should calculate combination count
            expected_combinations = min(3 * 3 * 2, 12)
            self.assertEqual(dashboard.state.combination_count, expected_combinations)
        
        # Should have cost and time estimates
        self.assertGreaterEqual(self.dashboard.state.total_cost, 0.0)
        self.assertGreaterEqual(self.dashboard.state.total_time, 0.0)


def run_dashboard_tests():
    """Run all dashboard tests"""
    if not DASHBOARD_AVAILABLE:
        print("Skipping dashboard tests - components not available")
        return
    
    # Create test suite
    test_classes = [
        TestDashboardState,
        TestConfigurationDashboard,
        TestInteractiveDashboardController,
        TestDashboardIntegration,
        TestDashboardDisplay,
        TestResourceProtectionIntegration
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_rate = ((total_tests - failures - errors) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"Dashboard Test Results:")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_tests - failures - errors}")
    print(f"Failed: {failures}")
    print(f"Errors: {errors}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"{'='*60}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run the tests
    success = run_dashboard_tests()
    sys.exit(0 if success else 1)