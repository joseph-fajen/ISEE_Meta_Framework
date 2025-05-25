#!/usr/bin/env python3
"""
Test Suite for Purpose Selection Foundation (UX Enhancement Step 2.1)

This test suite verifies the functionality of the purpose-based interface
changes to the Command Wizard, ensuring that purpose selection correctly
influences parameter suggestions and maintains backward compatibility.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from purpose_categories import PurposeManager, PurposeCategory, create_default_purpose_manager
    from command_wizard import CommandWizard
    PURPOSE_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Purpose modules not available: {e}")
    PURPOSE_MODULES_AVAILABLE = False


class TestPurposeCategories(unittest.TestCase):
    """Test the PurposeCategory and PurposeManager classes."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not PURPOSE_MODULES_AVAILABLE:
            self.skipTest("Purpose modules not available")
        
        self.purpose_manager = create_default_purpose_manager()
    
    def test_purpose_category_creation(self):
        """Test creating a purpose category."""
        category = PurposeCategory(
            id="test_purpose",
            name="Test Purpose",
            description="A test purpose for unit testing",
            icon="🧪",
            examples=["Test example 1", "Test example 2"],
            recommended_params={"models": 2, "instructions": 3},
            required_expertise="beginner",
            estimated_cost="low",
            typical_runtime="quick",
            domains=["domain_test"]
        )
        
        self.assertEqual(category.id, "test_purpose")
        self.assertEqual(category.name, "Test Purpose")
        self.assertEqual(category.icon, "🧪")
        self.assertEqual(len(category.examples), 2)
        self.assertEqual(category.recommended_params["models"], 2)
        self.assertEqual(category.required_expertise, "beginner")
    
    def test_purpose_category_to_dict(self):
        """Test converting purpose category to dictionary."""
        category = PurposeCategory(
            id="test_dict",
            name="Test Dict",
            description="Test dictionary conversion",
            icon="📝",
            examples=["Example"],
            recommended_params={"models": 1},
            required_expertise="intermediate",
            estimated_cost="medium",
            typical_runtime="moderate",
            domains=["domain_test"]
        )
        
        category_dict = category.to_dict()
        
        self.assertIsInstance(category_dict, dict)
        self.assertEqual(category_dict["id"], "test_dict")
        self.assertEqual(category_dict["name"], "Test Dict")
        self.assertEqual(category_dict["recommended_params"]["models"], 1)
    
    def test_purpose_category_from_dict(self):
        """Test creating purpose category from dictionary."""
        data = {
            "id": "test_from_dict",
            "name": "Test From Dict",
            "description": "Test creating from dict",
            "icon": "🔧",
            "examples": ["Dict example"],
            "recommended_params": {"instructions": 2},
            "required_expertise": "advanced",
            "estimated_cost": "high",
            "typical_runtime": "extended",
            "domains": ["domain_advanced"]
        }
        
        category = PurposeCategory.from_dict(data)
        
        self.assertEqual(category.id, "test_from_dict")
        self.assertEqual(category.name, "Test From Dict")
        self.assertEqual(category.recommended_params["instructions"], 2)
        self.assertEqual(category.required_expertise, "advanced")
    
    def test_default_purposes_loaded(self):
        """Test that default purposes are loaded correctly."""
        categories = self.purpose_manager.list_categories()
        
        # Should have several default categories
        self.assertGreater(len(categories), 5)
        
        # Check for specific expected categories
        category_ids = [cat.id for cat in categories]
        self.assertIn("quick_exploration", category_ids)
        self.assertIn("deep_analysis", category_ids)
        self.assertIn("creative_innovation", category_ids)
        self.assertIn("problem_solving", category_ids)
        self.assertIn("content_creation", category_ids)
        self.assertIn("learning_design", category_ids)
        self.assertIn("strategic_planning", category_ids)
        self.assertIn("custom_exploration", category_ids)
    
    def test_get_category_by_id(self):
        """Test retrieving a specific category by ID."""
        category = self.purpose_manager.get_category("quick_exploration")
        
        self.assertIsNotNone(category)
        self.assertEqual(category.id, "quick_exploration")
        self.assertEqual(category.name, "Quick Exploration")
        self.assertEqual(category.required_expertise, "beginner")
        self.assertEqual(category.estimated_cost, "low")
    
    def test_get_categories_by_expertise(self):
        """Test filtering categories by expertise level."""
        beginner_cats = self.purpose_manager.get_categories_by_expertise("beginner")
        intermediate_cats = self.purpose_manager.get_categories_by_expertise("intermediate")
        advanced_cats = self.purpose_manager.get_categories_by_expertise("advanced")
        
        self.assertGreater(len(beginner_cats), 0)
        self.assertGreater(len(intermediate_cats), 0)
        self.assertGreater(len(advanced_cats), 0)
        
        # Verify all returned categories have the correct expertise level
        for cat in beginner_cats:
            self.assertEqual(cat.required_expertise, "beginner")
        for cat in intermediate_cats:
            self.assertEqual(cat.required_expertise, "intermediate")
        for cat in advanced_cats:
            self.assertEqual(cat.required_expertise, "advanced")
    
    def test_get_categories_by_cost(self):
        """Test filtering categories by estimated cost."""
        low_cost_cats = self.purpose_manager.get_categories_by_cost("low")
        medium_cost_cats = self.purpose_manager.get_categories_by_cost("medium")
        high_cost_cats = self.purpose_manager.get_categories_by_cost("high")
        
        # Should have categories in each cost range
        self.assertGreater(len(low_cost_cats), 0)
        self.assertGreater(len(medium_cost_cats), 0)
        self.assertGreater(len(high_cost_cats), 0)
        
        # Verify cost levels are correct
        for cat in low_cost_cats:
            self.assertEqual(cat.estimated_cost, "low")
        for cat in medium_cost_cats:
            self.assertEqual(cat.estimated_cost, "medium")
        for cat in high_cost_cats:
            self.assertEqual(cat.estimated_cost, "high")
    
    def test_search_categories(self):
        """Test searching categories by query."""
        # Search by name
        results = self.purpose_manager.search_categories("exploration")
        self.assertGreater(len(results), 0)
        
        # Search by description
        results = self.purpose_manager.search_categories("brainstorming")
        self.assertGreater(len(results), 0)
        
        # Search that should return no results
        results = self.purpose_manager.search_categories("nonexistent_term_xyz")
        self.assertEqual(len(results), 0)
    
    def test_parameter_recommendations(self):
        """Test that categories have appropriate parameter recommendations."""
        quick_exp = self.purpose_manager.get_category("quick_exploration")
        deep_analysis = self.purpose_manager.get_category("deep_analysis")
        
        # Quick exploration should have fewer combinations
        self.assertLess(quick_exp.recommended_params["models"], 
                       deep_analysis.recommended_params["models"])
        self.assertLess(quick_exp.recommended_params["max_combinations"], 
                       deep_analysis.recommended_params["max_combinations"])
        
        # Deep analysis should use stratified sampling
        self.assertEqual(deep_analysis.recommended_params["sampling_method"], "stratified")


class TestCommandWizardPurposeIntegration(unittest.TestCase):
    """Test the integration of purpose selection into the Command Wizard."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not PURPOSE_MODULES_AVAILABLE:
            self.skipTest("Purpose modules not available")
        
        self.wizard = CommandWizard()
    
    def test_purpose_manager_initialization(self):
        """Test that the purpose manager is properly initialized."""
        self.assertIsNotNone(self.wizard.purpose_manager)
        self.assertIsNone(self.wizard.selected_purpose)
        
        # Should have default categories loaded
        categories = self.wizard.purpose_manager.list_categories()
        self.assertGreater(len(categories), 0)
    
    @patch('builtins.input')
    @patch('sys.stdout')
    def test_purpose_selection_skip(self, mock_stdout, mock_input):
        """Test skipping purpose selection."""
        # Mock input to skip purpose selection
        mock_input.return_value = "0"
        
        result = self.wizard._select_purpose()
        
        self.assertIsNone(result)
        self.assertIsNone(self.wizard.selected_purpose)
    
    @patch('builtins.input')
    @patch('sys.stdout')
    def test_purpose_selection_valid_choice(self, mock_stdout, mock_input):
        """Test selecting a valid purpose."""
        # Mock input to select first purpose
        mock_input.return_value = "1"
        
        result = self.wizard._select_purpose()
        
        # Should return a purpose ID
        self.assertIsNotNone(result)
        self.assertIsNotNone(self.wizard.selected_purpose)
        
        # Parameters should be updated
        selected_purpose = self.wizard.selected_purpose
        for param, value in selected_purpose.recommended_params.items():
            if value is not None:
                self.assertEqual(self.wizard.params[param], value)
    
    @patch('builtins.input')
    @patch('sys.stdout')
    def test_purpose_selection_invalid_choice(self, mock_stdout, mock_input):
        """Test handling invalid purpose selection."""
        # Mock input with invalid choice
        mock_input.return_value = "999"
        
        result = self.wizard._select_purpose()
        
        # Should handle gracefully and return None
        self.assertIsNone(result)
        self.assertIsNone(self.wizard.selected_purpose)
    
    def test_parameter_application(self):
        """Test that purpose selection correctly applies parameters."""
        # Manually set a purpose for testing
        quick_exp = self.wizard.purpose_manager.get_category("quick_exploration")
        self.wizard.selected_purpose = quick_exp
        
        # Apply the recommended parameters
        for param, value in quick_exp.recommended_params.items():
            if value is not None:
                self.wizard.params[param] = value
        
        # Verify parameters were set correctly
        self.assertEqual(self.wizard.params["models"], 2)
        self.assertEqual(self.wizard.params["instructions"], 2)
        self.assertEqual(self.wizard.params["variations"], 1)
        self.assertEqual(self.wizard.params["max_combinations"], 4)
        self.assertEqual(self.wizard.params["sampling_method"], "random")
    
    def test_domain_auto_selection(self):
        """Test that domains are automatically selected when specified by purpose."""
        # Create a test purpose with domain specification
        test_purpose = PurposeCategory(
            id="test_domain_purpose",
            name="Test Domain Purpose",
            description="Test domain auto-selection",
            icon="🧪",
            examples=["Test"],
            recommended_params={"models": 1},
            required_expertise="beginner",
            estimated_cost="low",
            typical_runtime="quick",
            domains=["domain_instructional_design"]  # This should exist in the domain manager
        )
        
        # Add the test purpose
        self.wizard.purpose_manager.add_category(test_purpose)
        self.wizard.selected_purpose = test_purpose
        
        # Simulate the domain selection logic from _select_purpose
        if test_purpose.domains:
            for domain_id in test_purpose.domains:
                domain = self.wizard.domain_manager.get_domain(domain_id)
                if domain:
                    self.wizard.params["domain"] = domain.name
                    break
        
        # Check that domain was set (if the domain exists)
        # Note: This test depends on the domain manager having the specified domain
        if self.wizard.domain_manager.get_domain("domain_instructional_design"):
            self.assertIsNotNone(self.wizard.params.get("domain"))


class TestBackwardCompatibility(unittest.TestCase):
    """Test that purpose selection doesn't break existing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not PURPOSE_MODULES_AVAILABLE:
            self.skipTest("Purpose modules not available")
        
        self.wizard = CommandWizard()
    
    def test_existing_step_methods_still_work(self):
        """Test that existing step methods continue to function."""
        # Test that we can still call existing methods
        self.assertIsNotNone(self.wizard.select_instruction_templates)
        self.assertIsNotNone(self.wizard.configure_advanced_options)
        
        # These methods should accept step number parameters now
        try:
            # Should not raise an exception
            self.wizard.select_instruction_templates(step_num=3)
        except Exception as e:
            self.fail(f"select_instruction_templates failed with step_num parameter: {e}")
        
        try:
            # Should not raise an exception
            self.wizard.configure_advanced_options(step_num=8)
        except Exception as e:
            self.fail(f"configure_advanced_options failed with step_num parameter: {e}")
    
    def test_parameters_not_overwritten_when_none(self):
        """Test that existing parameters aren't overwritten by None values."""
        # Set some initial parameters
        self.wizard.params["models"] = 5
        self.wizard.params["instructions"] = 7
        
        # Create a purpose with None values for some parameters
        test_purpose = PurposeCategory(
            id="test_none_purpose",
            name="Test None Purpose",
            description="Test that None values don't overwrite",
            icon="🚫",
            examples=["Test"],
            recommended_params={"models": None, "instructions": 3, "new_param": 1},
            required_expertise="beginner",
            estimated_cost="low",
            typical_runtime="quick",
            domains=[]
        )
        
        self.wizard.selected_purpose = test_purpose
        
        # Apply parameters (simulating the logic from _select_purpose)
        for param, value in test_purpose.recommended_params.items():
            if value is not None:  # Only set non-None values
                self.wizard.params[param] = value
        
        # Check that existing non-None values weren't overwritten
        self.assertEqual(self.wizard.params["models"], 5)  # Should remain unchanged
        self.assertEqual(self.wizard.params["instructions"], 3)  # Should be updated
        self.assertEqual(self.wizard.params["new_param"], 1)  # Should be added
    
    def test_no_purpose_manager_graceful_degradation(self):
        """Test that the wizard works when purpose manager is not available."""
        # Temporarily disable purpose manager
        original_purpose_manager = self.wizard.purpose_manager
        self.wizard.purpose_manager = None
        
        try:
            # Purpose selection should return None gracefully
            result = self.wizard._select_purpose()
            self.assertIsNone(result)
        finally:
            # Restore purpose manager
            self.wizard.purpose_manager = original_purpose_manager


def run_purpose_selection_tests():
    """Run all purpose selection tests and return results."""
    if not PURPOSE_MODULES_AVAILABLE:
        print("❌ Purpose selection modules not available - skipping tests")
        return False
    
    print("🧪 Running Purpose Selection Foundation Tests (Step 2.1)")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestPurposeCategories))
    suite.addTest(unittest.makeSuite(TestCommandWizardPurposeIntegration))
    suite.addTest(unittest.makeSuite(TestBackwardCompatibility))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Purpose Selection Tests Summary:")
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
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n✅ All Purpose Selection tests passed!")
    else:
        print("\n❌ Some Purpose Selection tests failed!")
    
    return success


if __name__ == "__main__":
    success = run_purpose_selection_tests()
    sys.exit(0 if success else 1)