#!/usr/bin/env python3
"""
ISEE Command Wizard Reporting Integration Tests

Tests for the reporting integration in the ISEE Command Construction Wizard.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from typing import Dict, Any, List

# Add parent directory to path to import harness
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from tests.command_wizard.test_harness import BaseMockTest, CommandWizardTestHarness

class TestReportingIntegration(BaseMockTest):
    """Tests for reporting integration functionality."""
    
    def test_reporting_parameters(self):
        """Test the reporting parameter handling."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Create a mock command wizard
        self.harness.mock_command_wizard()
        
        # Set wizard parameters with reporting enabled
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
            "generate_reports": True,
            "analyze_results": True,
            "report_format": "markdown",
            "export_csv": True,
            "no_visualizations": False,
            "simulate": False,
            "dry_run": False,
            "save_state": None,
            "synthesize_method": "cluster_based",
            "output_directory": "custom/output/dir",
        }
        
        # Generate the command
        command = self.harness.wizard.generate_command()
        
        # Verify reporting parameters are included in the command
        self.assertIn("--generate-reports", command)
        self.assertIn("--analyze-results", command)
        self.assertIn("--report-format markdown", command)
        self.assertIn("--export-csv", command)
        self.assertIn("--output-directory \"custom/output/dir\"", command)
        
        # No visualizations should be excluded since it's false
        self.assertNotIn("--no-visualizations", command)
        
        # Update parameter to include no-visualizations
        self.harness.wizard.params["no_visualizations"] = True
        
        # Generate the command again
        command = self.harness.wizard.generate_command()
        
        # Verify no-visualizations is now included
        self.assertIn("--no-visualizations", command)
    
    def test_output_directory_handling(self):
        """Test handling of the output directory parameter."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Create a mock command wizard
        self.harness.mock_command_wizard()
        
        # Mock the datetime to get a predictable timestamp
        with patch('datetime.datetime') as mock_datetime:
            # Set a fixed datetime for testing
            mock_datetime.now.return_value = mock_datetime
            mock_datetime.strftime.return_value = "20230101_120000"
            
            # Call the method to get the output directory
            output_dir = self.harness.wizard._get_timestamped_output_dir()
            
            # Verify the output directory format
            self.assertEqual(output_dir, "data/output/run_20230101_120000")
    
    def test_custom_output_directory(self):
        """Test setting a custom output directory."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Create a mock command wizard
        self.harness.mock_command_wizard()
        
        # Mock directory path validation
        def mock_exists(path):
            # Return True for 'custom_dir' to simulate it exists
            return 'custom_dir' in path or path == "data/output"
        
        with patch('os.path.exists', side_effect=mock_exists):
            with patch('os.path.isdir', return_value=True):
                # Call the method to choose an output directory
                with patch('builtins.input', return_value="custom_dir"):
                    output_dir = self.harness.wizard._choose_output_directory()
                    
                    # Verify the custom directory was returned
                    self.assertEqual(output_dir, "custom_dir")
    
    def test_reporting_explanation(self):
        """Test the explanation of reporting features."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Create a mock command wizard
        self.harness.mock_command_wizard()
        
        # Set wizard parameters with reporting enabled
        self.harness.wizard.params = {
            "query": "How might we improve urban transportation?",
            "generate_reports": True,
            "analyze_results": True,
        }
        
        # Generate the command
        command = self.harness.wizard.generate_command()
        
        # Capture the console output during preview
        captured_output = []
        def mock_print(*args, **kwargs):
            captured_output.append(" ".join(str(arg) for arg in args))
        
        # Call preview_command to generate the explanation
        with patch('builtins.print', mock_print):
            self.harness.wizard.preview_command(command)
            
            # Check for reporting explanation
            reporting_explanation = False
            visualization_explanation = False
            for line in captured_output:
                if "generate detailed reports" in line.lower():
                    reporting_explanation = True
                if "perform analysis with visualizations" in line.lower():
                    visualization_explanation = True
            
            self.assertTrue(reporting_explanation)
            self.assertTrue(visualization_explanation)
    
    def test_report_format_selection(self):
        """Test selecting the report format."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Create a mock command wizard
        self.harness.mock_command_wizard()
        
        # Call the method to select report format with a mock for input
        with patch('builtins.input', return_value="2"):  # Select JSON format
            report_format = self.harness.wizard._select_report_format()
            
            # Verify JSON format was selected
            self.assertEqual(report_format, "json")
            
        # Try with default (markdown)
        with patch('builtins.input', return_value=""):  # Default selection
            report_format = self.harness.wizard._select_report_format()
            
            # Verify markdown format was selected by default
            self.assertEqual(report_format, "markdown")


if __name__ == "__main__":
    unittest.main()