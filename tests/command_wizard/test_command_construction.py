#!/usr/bin/env python3
"""
ISEE Command Wizard Command Construction Tests

Tests for the command construction functionality of the ISEE Command Construction Wizard.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from typing import Dict, Any, List

# Add parent directory to path to import harness
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from tests.command_wizard.test_harness import BaseMockTest, CommandWizardTestHarness, generate_command_construction_test_cases

class TestCommandConstruction(BaseMockTest):
    """Tests for command construction functionality."""
    
    def test_simple_query(self):
        """Test constructing a command with a simple query."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Mock the command wizard
        self.harness.mock_command_wizard()
        
        # Set the parameters directly
        self.harness.wizard.params = {
            "query": "How might we improve urban transportation",
            "domain": "mobility",
            "models": 2,
            "instructions": 3,
            "variations": 2,
            "max_combinations": None,
            "sampling_method": "exhaustive",
            "use_ollama": False,
            "balanced_models": False,
            "output_format": "markdown",
            "output_file": None,
            "simulate": False,
            "dry_run": False,
            "generate_reports": False,
            "analyze_results": False,
            "save_state": None,
            "load_state": None,
            "synthesize_method": "cluster_based",
        }
        
        # Generate the command
        command = self.harness.wizard.generate_command()
        
        # Verify expected command parts
        self.assertIn('python main.py', command)
        self.assertIn('--query "How might we improve urban transportation"', command)
        self.assertIn('--domain "mobility"', command)
        self.assertIn('--models 2', command)
        self.assertIn('--instructions 3', command)
        self.assertIn('--variations 2', command)
        
        # Verify optional parameters are not included
        self.assertNotIn('--max-combinations', command)
        self.assertNotIn('--use-ollama', command)
        self.assertNotIn('--balanced-models', command)
        self.assertNotIn('--output-file', command)
        self.assertNotIn('--simulate', command)
        self.assertNotIn('--dry-run', command)
        self.assertNotIn('--save-state', command)
        
        # Verify included parameters
        self.assertIn('--output-format markdown', command)
        
        # Default parameters should not be repeated if they are defaults
        self.assertNotIn('--synthesize-method cluster_based', command)
    
    def test_complex_query_with_special_chars(self):
        """Test constructing a command with special characters in the query."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Mock the command wizard
        self.harness.mock_command_wizard()
        
        # Set the parameters with a complex query containing special characters
        self.harness.wizard.params = {
            "query": 'How might we improve user\'s experience with "smart home" devices?',
            "domain": None,
            "models": 3,
            "instructions": 4,
            "variations": 2,
            "max_combinations": None,
            "sampling_method": "exhaustive",
            "use_ollama": False,
            "balanced_models": False,
            "output_format": "markdown",
            "output_file": None,
            "simulate": False,
            "dry_run": False,
            "generate_reports": False,
            "analyze_results": False,
            "save_state": None,
            "load_state": None,
            "synthesize_method": "cluster_based",
        }
        
        # Generate the command
        command = self.harness.wizard.generate_command()
        
        # Verify the query is properly escaped
        self.assertIn('--query "How might we improve user\'s experience with \\"smart home\\" devices?"', command)
        
        # Verify domain is not included (since it's None)
        self.assertNotIn('--domain', command)
        
        # Verify other parameters
        self.assertIn('--models 3', command)
        self.assertIn('--instructions 4', command)
        self.assertIn('--variations 2', command)
    
    def test_all_parameters(self):
        """Test constructing a command with all available parameters."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Mock the command wizard
        self.harness.mock_command_wizard()
        
        # Set all parameters
        self.harness.wizard.params = {
            "query": "How might we reduce plastic waste?",
            "domain": "sustainability",
            "models": 2,
            "use_ollama": True,
            "balanced_models": True,
            "instructions": 3,
            "variations": 2,
            "max_combinations": 24,
            "sampling_method": "stratified",
            "synthesize_method": "cross_pollination",
            "output_format": "json",
            "output_file": "results.json",
            "generate_reports": True,
            "analyze_results": True,
            "simulate": True,
            "dry_run": True,
            "save_state": "test_state.json",
            "load_state": None,
        }
        
        # Generate the command
        command = self.harness.wizard.generate_command()
        
        # Verify all parameters are included
        self.assertIn('python main.py', command)
        self.assertIn('--query "How might we reduce plastic waste?"', command)
        self.assertIn('--domain "sustainability"', command)
        self.assertIn('--models 2', command)
        self.assertIn('--use-ollama', command)
        self.assertIn('--balanced-models', command)
        self.assertIn('--instructions 3', command)
        self.assertIn('--variations 2', command)
        self.assertIn('--max-combinations 24', command)
        self.assertIn('--sampling-method stratified', command)
        self.assertIn('--synthesize-method cross_pollination', command)
        self.assertIn('--output-format json', command)
        self.assertIn('--output-file "results.json"', command)
        self.assertIn('--generate-reports', command)
        self.assertIn('--analyze-results', command)
        self.assertIn('--simulate', command)
        self.assertIn('--dry-run', command)
        self.assertIn('--save-state "test_state.json"', command)
    
    def test_unified_config_inclusion(self):
        """Test automatic inclusion of unified config if available."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Mock the command wizard
        self.harness.mock_command_wizard()
        
        # Set basic parameters
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
            "simulate": False,
            "dry_run": False,
            "generate_reports": False,
            "analyze_results": False,
            "save_state": None,
            "load_state": None,
            "synthesize_method": "cluster_based",
        }
        
        # Mock os.path.exists to return True for unified_config.json
        with patch('os.path.exists', lambda path: path == "unified_config.json"):
            # Generate the command
            command = self.harness.wizard.generate_command()
            
            # Verify config is included
            self.assertIn('--config unified_config.json', command)
            self.assertTrue(hasattr(self.harness.wizard, 'using_unified_config'))
            self.assertTrue(self.harness.wizard.using_unified_config)
    
    def test_special_template_comment(self):
        """Test the special template comment is added when specific templates are selected."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Mock the command wizard
        self.harness.mock_command_wizard()
        
        # Set parameters with specific templates
        self.harness.wizard.params = {
            "query": "How might we improve urban transportation?",
            "domain": None,
            "models": 2,
            "instructions": 3,
            "variations": 2,
            "specific_templates": ["framework_thinking", "critical_analysis", "contrarian_thinking"],
            "max_combinations": None,
            "sampling_method": "exhaustive",
            "use_ollama": False,
            "balanced_models": False,
            "output_format": "markdown",
            "output_file": None,
            "simulate": False,
            "dry_run": False,
            "generate_reports": False,
            "analyze_results": False,
            "save_state": None,
            "load_state": None,
            "synthesize_method": "cluster_based",
        }
        
        # Generate the command
        command = self.harness.wizard.generate_command()
        
        # Verify the specific_templates_comment attribute is set
        self.assertTrue(hasattr(self.harness.wizard, 'specific_templates_comment'))
        self.assertIsNotNone(self.harness.wizard.specific_templates_comment)
        
        # Verify the comment contains the specified templates
        comment = self.harness.wizard.specific_templates_comment
        self.assertIn("Selected templates:", comment)
        for template_id in self.harness.wizard.params["specific_templates"]:
            self.assertIn(template_id, comment)


if __name__ == "__main__":
    unittest.main()