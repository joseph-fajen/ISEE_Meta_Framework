#!/usr/bin/env python3
"""
ISEE Command Wizard API Detection Tests

Tests for the API detection functionality of the ISEE Command Construction Wizard.
"""

import unittest
from unittest.mock import patch
import sys
import os
from typing import Dict, Any, List

# Add parent directory to path to import harness
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from tests.command_wizard.test_harness import BaseMockTest, CommandWizardTestHarness, generate_api_test_cases

class TestAPIDetection(BaseMockTest):
    """Tests for API detection functionality."""
    
    def test_no_apis_available(self):
        """Test behavior when no API keys are available."""
        # Set up the test harness with no API keys
        self.harness.setup_mock_environment(
            anthropic_api_key=False,
            openai_api_key=False,
            google_api_key=False,
            ollama_available=False
        )
        
        # Mock the command wizard
        self.harness.mock_command_wizard()
        
        # Simulate user inputs for a basic flow
        self.harness.simulate_user_inputs([
            "",  # Accept default query
            "0",  # No specific domain
            "2",  # 2 models
            "3",  # 3 instructions
            "2",  # 2 variations
            "",  # No max combinations
            "1",  # Exhaustive sampling
            "1",  # Cluster-based synthesis
            "1",  # Markdown output
            "n",  # No custom output file
            "y",  # Generate reports
            "y",  # Analyze results
            "",  # No need to specify simulation (should be forced)
            "n",  # No dry run
            "n",  # No save state
            "n",  # Don't execute the command
        ])
        
        # Run the simulation
        results = self.harness.run_simulation()
        
        # Verify the command has simulation mode enabled
        command = self.harness.get_generated_command()
        self.assertIn("--simulate", command)
        
        # Verify the params object has simulate=True
        self.assertTrue(results["params"]["simulate"])
        
        # Check for warning message in the output
        self.assertIn("No API providers detected", results["output"])
    
    def test_anthropic_only(self):
        """Test behavior when only Anthropic API key is available."""
        # Set up the test harness with only Anthropic API
        self.harness.setup_mock_environment(
            anthropic_api_key=True,
            openai_api_key=False,
            google_api_key=False,
            ollama_available=False
        )
        
        # Mock the command wizard
        self.harness.mock_command_wizard()
        
        # Simulate user inputs for a basic flow
        self.harness.simulate_user_inputs([
            "",  # Accept default query
            "0",  # No specific domain
            "1",  # Select Top Performers collection (option 1)
            "3",  # 3 instructions
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
        
        # Verify the command does not have simulation mode enabled
        command = self.harness.get_generated_command()
        self.assertNotIn("--simulate", command)
        
        # Verify the params object has simulate=False
        self.assertFalse(results["params"]["simulate"])
        
        # Check for Anthropic available message in the output
        self.assertIn("Anthropic API: Available", results["output"])
    
    def test_all_apis(self):
        """Test behavior when all API keys are available."""
        # Set up the test harness with all APIs
        self.harness.setup_mock_environment(
            anthropic_api_key=True,
            openai_api_key=True,
            google_api_key=True,
            openrouter_api_key=True,
            ollama_available=False
        )
        
        # Mock the command wizard
        self.harness.mock_command_wizard()
        
        # Simulate user inputs for a basic flow
        self.harness.simulate_user_inputs([
            "",  # Accept default query
            "0",  # No specific domain
            "1",  # Select Top Performers collection (option 1)
            "3",  # 3 instructions
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
        
        # Verify the command does not have simulation mode enabled
        command = self.harness.get_generated_command()
        self.assertNotIn("--simulate", command)
        
        # Verify the params object has simulate=False
        self.assertFalse(results["params"]["simulate"])
        
        # Check for all API available messages in the output
        self.assertIn("Anthropic API: Available", results["output"])
        self.assertIn("OpenAI API: Available", results["output"])
        self.assertIn("Google API: Available", results["output"])
    
    def test_ollama_only(self):
        """Test behavior when only Ollama is available."""
        # Set up the test harness with only Ollama
        self.harness.setup_mock_environment(
            anthropic_api_key=False,
            openai_api_key=False,
            google_api_key=False,
            ollama_available=True,
            ollama_models=["llama2", "mistral", "codellama"]
        )
        
        # Mock the command wizard
        self.harness.mock_command_wizard()
        
        # Simulate user inputs for a basic flow
        self.harness.simulate_user_inputs([
            "",  # Accept default query
            "0",  # No specific domain
            "2",  # 2 models
            "y",  # Include Ollama models
            "y",  # Balanced representation
            "3",  # 3 instructions
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
        
        # Verify the command has use-ollama flag
        command = self.harness.get_generated_command()
        self.assertIn("--use-ollama", command)
        
        # Verify the params object has use_ollama=True
        self.assertTrue(results["params"]["use_ollama"])
        
        # Check for Ollama available message in the output
        self.assertIn("Ollama: Available", results["output"])
        
        # Check that models are listed
        self.assertIn("llama2", results["output"])
        self.assertIn("mistral", results["output"])
        self.assertIn("codellama", results["output"])


if __name__ == "__main__":
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add all tests
    for name in dir(TestAPIDetection):
        if name.startswith('test_'):
            suite.addTest(TestAPIDetection(name))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)