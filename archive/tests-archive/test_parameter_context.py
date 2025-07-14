#!/usr/bin/env python3
"""
Test script for parameter context module

This script tests the enhanced parameter context functionality implemented
as part of the Command Wizard UX Enhancement Roadmap - Step 1.2.
"""

import unittest
from parameter_context import ParameterContext

class TestParameterContext(unittest.TestCase):
    """Test cases for the parameter context functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.param_context = ParameterContext()
    
    def test_get_parameter_context(self):
        """Test retrieving parameter context information."""
        # Test getting context for a valid parameter
        models_context = self.param_context.get_parameter_context("models")
        self.assertIsNotNone(models_context)
        self.assertIn("short", models_context)
        self.assertIn("long", models_context)
        self.assertIn("impact", models_context)
        self.assertIn("examples", models_context)
        
        # Test getting context for an invalid parameter
        invalid_context = self.param_context.get_parameter_context("nonexistent_param")
        self.assertEqual(invalid_context, {})
    
    def test_get_parameter_examples(self):
        """Test retrieving parameter examples."""
        # Test getting examples for a parameter with examples
        models_examples = self.param_context.get_parameter_examples("models")
        self.assertIsInstance(models_examples, list)
        self.assertTrue(len(models_examples) > 0)
        
        # Test getting examples for a parameter without examples (should return empty list)
        nonexistent_examples = self.param_context.get_parameter_examples("nonexistent_param")
        self.assertEqual(nonexistent_examples, [])
    
    def test_get_detailed_example(self):
        """Test retrieving detailed examples."""
        # Test getting a detailed example for a parameter with detailed examples
        models_example = self.param_context.get_detailed_example("models")
        self.assertIsInstance(models_example, dict)
        self.assertIn("value", models_example)
        self.assertIn("explanation", models_example)
        
        # Test getting a detailed example for a parameter without detailed examples
        nonexistent_example = self.param_context.get_detailed_example("nonexistent_param")
        self.assertEqual(nonexistent_example, {})
        
        # Test getting a detailed example with a specific index
        if len(self.param_context.get_parameter_context("models").get("detailed_examples", [])) > 1:
            second_example = self.param_context.get_detailed_example("models", 1)
            self.assertIsInstance(second_example, dict)
            self.assertIn("value", second_example)
            self.assertIn("explanation", second_example)
    
    def test_get_cross_parameter_impacts(self):
        """Test retrieving cross-parameter impacts."""
        # Test getting cross-parameter impacts for a parameter with impacts
        models_impacts = self.param_context.get_cross_parameter_impacts("models")
        self.assertIsInstance(models_impacts, list)
        if models_impacts:  # If there are impacts
            self.assertIn("parameter", models_impacts[0])
            self.assertIn("impact", models_impacts[0])
        
        # Test getting cross-parameter impacts for a parameter without impacts
        nonexistent_impacts = self.param_context.get_cross_parameter_impacts("nonexistent_param")
        self.assertEqual(nonexistent_impacts, [])
    
    def test_get_related_parameters(self):
        """Test retrieving related parameters."""
        # Test getting related parameters for a parameter with relations
        models_related = self.param_context.get_related_parameters("models")
        self.assertIsInstance(models_related, list)
        self.assertTrue(len(models_related) > 0)
        
        # Test getting related parameters for a parameter without relations
        nonexistent_related = self.param_context.get_related_parameters("nonexistent_param")
        self.assertEqual(nonexistent_related, [])
    
    def test_get_parameter_warning(self):
        """Test retrieving parameter warnings."""
        # Test getting warning for a parameter with a warning threshold
        # Find a parameter with a warning threshold
        param_with_warning = None
        for param, context in self.param_context.context_db.items():
            if "warning_threshold" in context:
                param_with_warning = param
                threshold = context["warning_threshold"]
                break
        
        if param_with_warning:
            # Test with a value that should trigger a warning
            if isinstance(threshold, bool):
                warning = self.param_context.get_parameter_warning(param_with_warning, True)
            else:
                warning = self.param_context.get_parameter_warning(param_with_warning, threshold + 1)
            
            self.assertIsNotNone(warning)
            
            # Test with a value that should not trigger a warning
            if isinstance(threshold, bool):
                no_warning = self.param_context.get_parameter_warning(param_with_warning, False)
            else:
                no_warning = self.param_context.get_parameter_warning(param_with_warning, threshold - 1)
            
            self.assertIsNone(no_warning)
    
    def test_check_parameter_dependencies(self):
        """Test checking parameter dependencies."""
        # Test dependencies for analyze_results which depends on generate_reports
        if "analyze_results" in self.param_context.context_db:
            # Test with dependency satisfied
            all_params = {"analyze_results": True, "generate_reports": True}
            warnings = self.param_context.check_parameter_dependencies("analyze_results", all_params)
            self.assertEqual(warnings, [])
            
            # Test with dependency not satisfied
            all_params = {"analyze_results": True, "generate_reports": False}
            warnings = self.param_context.check_parameter_dependencies("analyze_results", all_params)
            self.assertTrue(len(warnings) > 0)
    
    def test_get_all_parameter_names(self):
        """Test retrieving all parameter names."""
        param_names = self.param_context.get_all_parameter_names()
        self.assertIsInstance(param_names, list)
        self.assertTrue(len(param_names) > 0)
        self.assertIn("query", param_names)
        self.assertIn("models", param_names)
    
    def test_get_parameters_by_category(self):
        """Test retrieving parameters by category."""
        # Test getting parameters for a valid category
        basic_params = self.param_context.get_parameters_by_category("basic")
        self.assertIsInstance(basic_params, list)
        self.assertTrue(len(basic_params) > 0)
        self.assertIn("query", basic_params)
        
        # Test getting parameters for an invalid category
        invalid_params = self.param_context.get_parameters_by_category("nonexistent_category")
        self.assertEqual(invalid_params, [])
    
    def test_get_all_categories(self):
        """Test retrieving all categories."""
        categories = self.param_context.get_all_categories()
        self.assertIsInstance(categories, list)
        self.assertTrue(len(categories) > 0)
        self.assertIn("id", categories[0])
        self.assertIn("name", categories[0])
        self.assertIn("description", categories[0])
        self.assertIn("parameters", categories[0])
    
    def test_calculate_combinations(self):
        """Test calculating total combinations."""
        # Test with basic parameters
        params = {
            "models": 2,
            "instructions": 3,
            "variations": 2
        }
        combinations = self.param_context.calculate_combinations(params)
        self.assertEqual(combinations, 12)
        
        # Test with max_combinations specified
        params = {
            "models": 2,
            "instructions": 3,
            "variations": 2,
            "max_combinations": 6
        }
        combinations = self.param_context.calculate_combinations(params)
        self.assertEqual(combinations, 6)
        
        # Test with full mode
        params = {
            "models": 2,
            "instructions": 3,
            "variations": 2,
            "max_combinations": 6,
            "full": True
        }
        combinations = self.param_context.calculate_combinations(params)
        self.assertEqual(combinations, 12)  # Should ignore max_combinations
        
        # Test with quick mode
        params = {
            "models": 10,
            "instructions": 10,
            "variations": 10,
            "quick": True
        }
        combinations = self.param_context.calculate_combinations(params)
        self.assertEqual(combinations, 36)  # Should be limited to 36
    
    def test_get_combination_impact(self):
        """Test getting combination impact description."""
        # Test with a small number of combinations
        params = {
            "models": 2,
            "instructions": 2,
            "variations": 1
        }
        impact = self.param_context.get_combination_impact(params)
        self.assertIn("4 combinations", impact)
        
        # Test with a large number of combinations
        params = {
            "models": 5,
            "instructions": 10,
            "variations": 5
        }
        impact = self.param_context.get_combination_impact(params)
        self.assertIn("250 combinations", impact)

if __name__ == "__main__":
    unittest.main()