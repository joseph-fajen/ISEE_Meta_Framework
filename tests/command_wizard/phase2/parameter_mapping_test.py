#!/usr/bin/env python3
"""
ISEE Command Wizard Parameter Mapping Tests

Tests for the parameter mapping in the ISEE Command Construction Wizard.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
import re
from typing import Dict, Any, List

# Add parent directory to path to import harness
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from tests.command_wizard.test_harness import BaseMockTest, CommandWizardTestHarness

class TestParameterMapping(BaseMockTest):
    """Tests for parameter mapping functionality."""
    
    def test_extract_main_parameters(self):
        """Test extracting parameters from main.py."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Create a mock command wizard
        self.harness.mock_command_wizard()
        
        # Mock subprocess.run to return help text
        help_text = """
        usage: main.py [-h] [--config CONFIG] [--save-state SAVE_STATE]
               [--load-state LOAD_STATE] [--domain-config DOMAIN_CONFIG]
               [--query QUERY] [--domain DOMAIN] [--models MODELS]
               [--use-ollama] [--instructions INSTRUCTIONS]
               [--variations VARIATIONS] [--max-combinations MAX_COMBINATIONS]
               [--sampling-method {exhaustive,stratified,adaptive}]
               [--output-format {markdown,json}] [--output-file OUTPUT_FILE]
               [--output-directory OUTPUT_DIRECTORY] [--simulate] [--dry-run]
               [--balanced-models] [--synthesize-method {cluster_based,cross_pollination}]
               [--generate-reports] [--report-format {markdown,json}]
               [--export-csv] [--analyze-results] [--no-visualizations]
               [--quick] [--full] [--list-domains]
        """
        
        with patch('subprocess.run', return_value=MagicMock(stdout=help_text, returncode=0)):
            # Call the method to extract parameters
            main_params = self.harness.wizard._extract_main_parameters()
            
            # Verify that key parameters are extracted
            self.assertIn("config", main_params)
            self.assertIn("query", main_params)
            self.assertIn("domain", main_params)
            self.assertIn("models", main_params)
            self.assertIn("instructions", main_params)
            self.assertIn("variations", main_params)
            self.assertIn("max_combinations", main_params)
            self.assertIn("sampling_method", main_params)
            self.assertIn("output_format", main_params)
            self.assertIn("output_file", main_params)
            self.assertIn("simulate", main_params)
            self.assertIn("dry_run", main_params)
            self.assertIn("balanced_models", main_params)
            self.assertIn("synthesize_method", main_params)
            self.assertIn("generate_reports", main_params)
            self.assertIn("analyze_results", main_params)
            
            # Verify parameter types
            self.assertEqual(main_params["query"]["type"], "text")
            self.assertEqual(main_params["models"]["type"], "text")
            self.assertEqual(main_params["use_ollama"]["type"], "flag")
            self.assertEqual(main_params["sampling_method"]["type"], "choice")
            
            # Verify choices for choice parameters
            self.assertIn("exhaustive", main_params["sampling_method"]["choices"])
            self.assertIn("stratified", main_params["sampling_method"]["choices"])
            self.assertIn("adaptive", main_params["sampling_method"]["choices"])
    
    def test_parameter_mapping(self):
        """Test mapping wizard parameters to main.py parameters."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Create a mock command wizard
        self.harness.mock_command_wizard()
        
        # Set wizard parameters
        wizard_params = {
            "query": "How might we improve urban transportation?",
            "domain": "mobility",
            "models": 2,
            "instructions": 3,
            "variations": 2,
            "max_combinations": 36,
            "sampling_method": "stratified",
            "use_ollama": True,
            "balanced_models": True,
            "output_format": "markdown",
            "output_file": "results.md",
            "generate_reports": True,
            "analyze_results": True,
            "simulate": False,
            "dry_run": False,
            "save_state": "state.json",
            "synthesize_method": "cluster_based",
        }
        
        # Mock the main.py parameters
        main_params = {
            "query": {"type": "text", "required": True},
            "domain": {"type": "text", "required": False},
            "models": {"type": "text", "required": False},
            "instructions": {"type": "text", "required": False},
            "variations": {"type": "text", "required": False},
            "max_combinations": {"type": "text", "required": False},
            "sampling_method": {"type": "choice", "required": False, "choices": ["exhaustive", "stratified", "adaptive"]},
            "use_ollama": {"type": "flag", "required": False},
            "balanced_models": {"type": "flag", "required": False},
            "output_format": {"type": "choice", "required": False, "choices": ["markdown", "json"]},
            "output_file": {"type": "text", "required": False},
            "generate_reports": {"type": "flag", "required": False},
            "analyze_results": {"type": "flag", "required": False},
            "simulate": {"type": "flag", "required": False},
            "dry_run": {"type": "flag", "required": False},
            "save_state": {"type": "text", "required": False},
            "synthesize_method": {"type": "choice", "required": False, "choices": ["cluster_based", "cross_pollination"]},
        }
        
        # Mock the _extract_main_parameters method
        with patch.object(self.harness.wizard, '_extract_main_parameters', return_value=main_params):
            # Patch the wizard params
            self.harness.wizard.params = wizard_params
            
            # Call parameter validation
            validation_result = self.harness.wizard._validate_parameters()
            
            # Verify validation passed
            self.assertTrue(validation_result.get("valid", False))
            self.assertEqual(len(validation_result.get("issues", [])), 0)
            
            # Test with an invalid parameter value
            self.harness.wizard.params["sampling_method"] = "invalid_method"
            validation_result = self.harness.wizard._validate_parameters()
            
            # Verify validation failed
            self.assertFalse(validation_result.get("valid", True))
            self.assertGreater(len(validation_result.get("issues", [])), 0)
            
            # Reset to valid value
            self.harness.wizard.params["sampling_method"] = "stratified"
            
            # Generate command
            command = self.harness.wizard.generate_command()
            
            # Verify all parameters are correctly added to the command
            self.assertIn('--query "How might we improve urban transportation?"', command)
            self.assertIn('--domain "mobility"', command)
            self.assertIn('--models 2', command)
            self.assertIn('--instructions 3', command)
            self.assertIn('--variations 2', command)
            self.assertIn('--max-combinations 36', command)
            self.assertIn('--sampling-method stratified', command)
            self.assertIn('--use-ollama', command)
            self.assertIn('--balanced-models', command)
            self.assertIn('--output-format markdown', command)
            self.assertIn('--output-file "results.md"', command)
            self.assertIn('--generate-reports', command)
            self.assertIn('--analyze-results', command)
            self.assertIn('--save-state "state.json"', command)
    
    def test_help_option_integration(self):
        """Test integration of help option into command preview."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Create a mock command wizard
        self.harness.mock_command_wizard()
        
        # Set wizard parameters
        self.harness.wizard.params = {
            "query": "How might we improve urban transportation?",
            "domain": None,
            "models": 2,
            "instructions": 3,
            "variations": 2,
            "max_combinations": None,
            "sampling_method": "exhaustive",
            "use_ollama": False,
            "balanced_models": False,
            "output_format": "markdown",
            "output_file": None,
            "generate_reports": False,
            "analyze_results": False,
            "simulate": False,
            "dry_run": False,
            "save_state": None,
            "synthesize_method": "cluster_based",
        }
        
        # Mock stdout capture
        captured_output = []
        def mock_print(*args, **kwargs):
            captured_output.append(" ".join(str(arg) for arg in args))
        
        # Generate the command
        command = self.harness.wizard.generate_command()
        
        # Mock showing help options
        with patch('builtins.print', mock_print):
            self.harness.wizard._show_help_options()
            
            # Verify the help options were displayed
            help_found = False
            for line in captured_output:
                if "--help" in line:
                    help_found = True
                    break
            
            self.assertTrue(help_found)


if __name__ == "__main__":
    unittest.main()