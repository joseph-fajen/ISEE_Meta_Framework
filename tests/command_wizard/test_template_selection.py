#!/usr/bin/env python3
"""
ISEE Command Wizard Template Selection Tests

Tests for the template selection functionality of the ISEE Command Construction Wizard.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from typing import Dict, Any, List

# Add parent directory to path to import harness
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from tests.command_wizard.test_harness import BaseMockTest, CommandWizardTestHarness, generate_template_test_cases
from instruction_templates import InstructionTemplate, TemplateLibrary

class TestTemplateSelection(BaseMockTest):
    """Tests for template selection functionality."""
    
    def test_all_templates(self):
        """Test selecting all available templates."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Mock the command wizard
        self.harness.mock_command_wizard()
        
        # Get the template library to determine number of templates
        template_count = len(self.harness.wizard.template_library.list_templates())
        
        # Simulate user inputs for a flow where all templates are selected
        self.harness.simulate_user_inputs([
            "",  # Accept default query
            "0",  # No specific domain
            "2",  # 2 models
            "n",  # Don't select specific templates
            str(template_count),  # Select all templates
            "2",  # 2 variations
            "",  # No max combinations
            "1",  # Exhaustive sampling
            "1",  # Cluster-based synthesis
            "1",  # Markdown output
            "n",  # No custom output file
            "y",  # Generate reports
            "y",  # Analyze results
            "n",  # No simulation
            "n",  # No dry run
            "n",  # No save state
            "n",  # Don't execute the command
        ])
        
        # Run the simulation
        results = self.harness.run_simulation()
        
        # Verify all templates are selected
        self.assertEqual(results["params"]["instructions"], template_count)
        self.assertIsNone(results["params"]["specific_templates"])
        
        # Verify the command includes the correct instruction count
        command = self.harness.get_generated_command()
        self.assertIn(f"--instructions {template_count}", command)
    
    def test_specific_templates(self):
        """Test selecting specific templates."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Mock the command wizard
        self.harness.mock_command_wizard()
        
        # Simulate user inputs for a flow where specific templates are selected
        self.harness.simulate_user_inputs([
            "",  # Accept default query
            "0",  # No specific domain
            "2",  # 2 models
            "y",  # Select specific templates
            "1,3,5",  # Select templates 1, 3, and 5
            "2",  # 2 variations
            "",  # No max combinations
            "1",  # Exhaustive sampling
            "1",  # Cluster-based synthesis
            "1",  # Markdown output
            "n",  # No custom output file
            "y",  # Generate reports
            "y",  # Analyze results
            "n",  # No simulation
            "n",  # No dry run
            "n",  # No save state
            "n",  # Don't execute the command
        ])
        
        # Run the simulation
        results = self.harness.run_simulation()
        
        # Verify specific templates are selected
        self.assertEqual(results["params"]["instructions"], 3)  # 3 templates selected
        self.assertIsNotNone(results["params"]["specific_templates"])
        self.assertEqual(len(results["params"]["specific_templates"]), 3)
        
        # Get the template IDs from the library to verify selection
        templates = self.harness.wizard.template_library.list_templates()
        template_ids = [template.id for template in templates]
        
        # Extract the expected template IDs from positions 1, 3, 5 (zero-indexed)
        expected_template_ids = [template_ids[pos-1] for pos in [1, 3, 5] if pos-1 < len(template_ids)]
        
        # Verify the selected template IDs match
        for template_id in expected_template_ids:
            self.assertIn(template_id, results["params"]["specific_templates"])
        
        # Verify the command includes the comment with specific templates
        command = self.harness.get_generated_command()
        
        # Check if the wizard stored the specific templates comment
        if hasattr(self.harness.wizard, 'specific_templates_comment'):
            self.assertIsNotNone(self.harness.wizard.specific_templates_comment)
            self.assertIn("Selected templates:", self.harness.wizard.specific_templates_comment)
    
    def test_template_count_affects_combinations(self):
        """Test that template count affects the number of combinations."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Mock the command wizard
        self.harness.mock_command_wizard()
        
        # Simulate user inputs for a flow with 4 templates
        self.harness.simulate_user_inputs([
            "",  # Accept default query
            "0",  # No specific domain
            "2",  # 2 models
            "n",  # Don't select specific templates
            "4",  # Select 4 templates
            "2",  # 2 variations
            "",  # No max combinations
            "1",  # Exhaustive sampling
            "1",  # Cluster-based synthesis
            "1",  # Markdown output
            "n",  # No custom output file
            "y",  # Generate reports
            "y",  # Analyze results
            "n",  # No simulation
            "n",  # No dry run
            "n",  # No save state
            "n",  # Don't execute the command
        ])
        
        # Run the simulation
        results = self.harness.run_simulation()
        
        # Store the command and parameters
        command1 = self.harness.get_generated_command()
        params1 = results["params"]
        total_combinations1 = params1["models"] * params1["instructions"] * params1["variations"]
        
        # Now run again with 2 templates to compare
        self.setUp()  # Reset the test harness
        
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Mock the command wizard
        self.harness.mock_command_wizard()
        
        # Simulate user inputs for a flow with 2 templates
        self.harness.simulate_user_inputs([
            "",  # Accept default query
            "0",  # No specific domain
            "2",  # 2 models
            "n",  # Don't select specific templates
            "2",  # Select 2 templates
            "2",  # 2 variations
            "",  # No max combinations
            "1",  # Exhaustive sampling
            "1",  # Cluster-based synthesis
            "1",  # Markdown output
            "n",  # No custom output file
            "y",  # Generate reports
            "y",  # Analyze results
            "n",  # No simulation
            "n",  # No dry run
            "n",  # No save state
            "n",  # Don't execute the command
        ])
        
        # Run the simulation
        results = self.harness.run_simulation()
        
        # Store the command and parameters
        command2 = self.harness.get_generated_command()
        params2 = results["params"]
        total_combinations2 = params2["models"] * params2["instructions"] * params2["variations"]
        
        # Verify changing template count affects combinations
        self.assertEqual(params1["models"], params2["models"])
        self.assertEqual(params1["variations"], params2["variations"])
        self.assertNotEqual(params1["instructions"], params2["instructions"])
        self.assertNotEqual(total_combinations1, total_combinations2)
        
        # Verify both commands reflect the different template counts
        self.assertIn("--instructions 4", command1)
        self.assertIn("--instructions 2", command2)


if __name__ == "__main__":
    unittest.main()