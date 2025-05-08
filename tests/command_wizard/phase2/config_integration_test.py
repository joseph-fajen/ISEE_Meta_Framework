#!/usr/bin/env python3
"""
ISEE Command Wizard Configuration Integration Tests

Tests for the configuration file handling functionality of the ISEE Command Construction Wizard.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import json
from typing import Dict, Any, List

# Add parent directory to path to import harness
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from tests.command_wizard.test_harness import BaseMockTest, CommandWizardTestHarness

class TestConfigIntegration(BaseMockTest):
    """Tests for configuration file handling functionality."""
    
    def test_config_file_selection(self):
        """Test selecting custom configuration files."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Create a mock configuration wizard object
        self.harness.mock_command_wizard()
        
        # Create mock config files
        mock_config_files = [
            "unified_config.json",
            "sample_config.json",
            "gemini_test_config.json",
            "ollama_config.json",
            "custom_config.json"
        ]
        
        # Mock os.path.exists to detect these files
        with patch('os.path.exists', lambda path: path in mock_config_files):
            # Mock os.listdir to return all config files
            with patch('os.listdir', return_value=mock_config_files):
                # Call the mock method to select config
                config_file = self.harness.wizard._select_config_file()
                
                # Verify config selection occurred and returned a value
                self.assertIsNotNone(config_file)
                self.assertIn(config_file, mock_config_files)
    
    def test_config_file_existence_check(self):
        """Test checking for unified_config.json by default."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Create a mock configuration wizard object
        self.harness.mock_command_wizard()
        
        # Test when unified_config.json exists
        with patch('os.path.exists', lambda path: path == "unified_config.json"):
            command = self.harness.wizard.generate_command()
            self.assertIn("--config unified_config.json", command)
            self.assertTrue(self.harness.wizard.using_unified_config)
        
        # Test when unified_config.json doesn't exist
        with patch('os.path.exists', lambda path: path != "unified_config.json"):
            command = self.harness.wizard.generate_command()
            self.assertNotIn("--config", command)
            self.assertFalse(self.harness.wizard.using_unified_config)
    
    def test_config_file_validation(self):
        """Test validating configuration files."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Create a mock configuration wizard object
        self.harness.mock_command_wizard()
        
        # Create a valid config file
        valid_config = {
            "models": [
                {"id": "claude-3-opus", "name": "Claude 3 Opus"},
                {"id": "gpt-4-turbo", "name": "GPT-4 Turbo"}
            ]
        }
        
        # Create an invalid config file
        invalid_config = {"foo": "bar"}  # Missing models
        
        # Test valid config validation
        with patch('builtins.open', mock_open(read_data=json.dumps(valid_config))):
            result = self.harness.wizard._validate_config_file("valid_config.json")
            self.assertTrue(result)
        
        # Test invalid config validation
        with patch('builtins.open', mock_open(read_data=json.dumps(invalid_config))):
            result = self.harness.wizard._validate_config_file("invalid_config.json")
            self.assertFalse(result)
        
        # Test malformed JSON
        with patch('builtins.open', mock_open(read_data="{")):
            result = self.harness.wizard._validate_config_file("malformed_config.json")
            self.assertFalse(result)
    
    def test_config_explanation(self):
        """Test explanation of configuration file usage."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Create a mock configuration wizard object
        self.harness.mock_command_wizard()
        
        # Mock stdout capture
        captured_output = []
        def mock_print(*args, **kwargs):
            captured_output.append(" ".join(str(arg) for arg in args))
        
        # Test with unified_config.json
        with patch('os.path.exists', lambda path: path == "unified_config.json"):
            with patch('builtins.print', mock_print):
                # Mock preview_command to capture output
                command = self.harness.wizard.generate_command()
                self.harness.wizard.preview_command(command)
                
                # Check that the explanation mentions unified_config.json
                explanation_found = False
                for line in captured_output:
                    if "unified_config.json" in line and "model" in line:
                        explanation_found = True
                        break
                
                self.assertTrue(explanation_found)


if __name__ == "__main__":
    unittest.main()