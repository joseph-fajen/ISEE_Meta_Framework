#!/usr/bin/env python3
"""
ISEE Command Wizard Domain Loading Tests

Tests for the domain loading functionality of the ISEE Command Construction Wizard.
"""

import unittest
from unittest.mock import patch, mock_open
import sys
import os
import json
import tempfile
from typing import Dict, Any, List

# Add parent directory to path to import harness
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from tests.command_wizard.test_harness import BaseMockTest, CommandWizardTestHarness, generate_domain_test_cases
from domain_manager import Domain

class TestDomainLoading(BaseMockTest):
    """Tests for domain loading functionality."""
    
    def test_default_domains(self):
        """Test loading of default domains."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Create a patch for os.path.exists to return False for any domain files
        with patch('os.path.exists', return_value=False):
            # Mock the command wizard but allow it to load default domains
            self.harness.mock_command_wizard()
            
            # Get the domain manager instance
            domain_manager = self.harness.wizard.domain_manager
            
            # Verify default domains are loaded
            domains = domain_manager.list_domains()
            
            # Check how many domains we have (depends on create_default_domains implementation)
            self.assertTrue(len(domains) > 0, "Default domains should be loaded")
            
            # Verify some expected default domains are present
            domain_names = [domain.name for domain in domains]
            
            # Expect at least these domains, but there could be more
            expected_domains = ["General", "Technology", "Business"]
            for domain in expected_domains:
                self.assertIn(domain, domain_names, f"Default domain '{domain}' should be loaded")
    
    def test_tech_writing_domains(self):
        """Test loading domains from tech_writing_domains.json."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Create a mock tech_writing_domains.json file
        tech_writing_domains = {
            "domains": [
                {
                    "id": "technical_writing",
                    "name": "Technical Writing",
                    "description": "Creating clear technical documentation",
                    "keywords": ["documentation", "technical", "clarity"]
                },
                {
                    "id": "api_docs",
                    "name": "API Documentation",
                    "description": "Creating clear API reference documentation",
                    "keywords": ["api", "reference", "endpoints"]
                }
            ]
        }
        
        # Create patchers
        exists_patcher = patch('os.path.exists', lambda path: path == "tech_writing_domains.json")
        open_patcher = patch('builtins.open', mock_open(read_data=json.dumps(tech_writing_domains)))
        
        # Start patchers
        exists_patcher.start()
        open_patcher.start()
        
        try:
            # Mock the command wizard with standard _load_domain_configs method
            with patch.object(CommandWizardTestHarness, 'mock_command_wizard') as mock_method:
                # Override the method to allow real domain loading
                def modified_mock():
                    self.harness.env_patcher = patch.dict('os.environ', {
                        'ANTHROPIC_API_KEY': 'test_key' if self.harness.api_status.get('anthropic', False) else '',
                        'OPENAI_API_KEY': 'test_key' if self.harness.api_status.get('openai', False) else '',
                        'GOOGLE_API_KEY': 'test_key' if self.harness.api_status.get('google', False) else '',
                    })
                    self.harness.env_patcher.start()
                    
                    # Create wizard without mocking _load_domain_configs
                    with patch('command_wizard.CommandWizard._detect_apis', return_value=self.harness.api_status):
                        self.harness.wizard = self.harness.wizard = CommandWizard()
                        
                        # Mock clipboard and execution
                        self.harness.wizard.copy_to_clipboard = unittest.mock.MagicMock(return_value=True)
                        self.harness.wizard.execute_command = unittest.mock.MagicMock(side_effect=self.harness._capture_command)
                
                # Use our modified mock
                mock_method.side_effect = modified_mock
                
                # Call mock_command_wizard with our override
                self.harness.mock_command_wizard()
                
                # Get the domain manager instance
                domain_manager = self.harness.wizard.domain_manager
                
                # Verify domains are loaded
                domains = domain_manager.list_domains()
                domain_names = [domain.name for domain in domains]
                
                # Verify the tech writing domains are present
                self.assertIn("Technical Writing", domain_names)
                self.assertIn("API Documentation", domain_names)
                
                # Get a specific domain to verify its properties
                tech_writing_domain = domain_manager.get_domain("technical_writing")
                self.assertIsNotNone(tech_writing_domain)
                self.assertEqual(tech_writing_domain.name, "Technical Writing")
                self.assertEqual(tech_writing_domain.description, "Creating clear technical documentation")
                self.assertIn("documentation", tech_writing_domain.keywords)
        finally:
            # Stop patchers
            exists_patcher.stop()
            open_patcher.stop()
    
    def test_malformed_domain_file(self):
        """Test handling of malformed domain files."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Create patchers for a malformed JSON file
        exists_patcher = patch('os.path.exists', lambda path: path == "tech_writing_domains.json")
        open_patcher = patch('builtins.open', mock_open(read_data="This is not valid JSON"))
        
        # Capture console output
        console_output = []
        
        def mock_print(*args, **kwargs):
            console_output.append(" ".join(str(arg) for arg in args))
        
        print_patcher = patch('builtins.print', mock_print)
        
        # Start patchers
        exists_patcher.start()
        open_patcher.start()
        print_patcher.start()
        
        try:
            # Mock the command wizard with standard _load_domain_configs method
            with patch.object(CommandWizardTestHarness, 'mock_command_wizard') as mock_method:
                # Override the method to allow real domain loading
                def modified_mock():
                    self.harness.env_patcher = patch.dict('os.environ', {
                        'ANTHROPIC_API_KEY': 'test_key' if self.harness.api_status.get('anthropic', False) else '',
                        'OPENAI_API_KEY': 'test_key' if self.harness.api_status.get('openai', False) else '',
                        'GOOGLE_API_KEY': 'test_key' if self.harness.api_status.get('google', False) else '',
                    })
                    self.harness.env_patcher.start()
                    
                    # Create wizard without mocking _load_domain_configs
                    with patch('command_wizard.CommandWizard._detect_apis', return_value=self.harness.api_status):
                        self.harness.wizard = self.harness.wizard = CommandWizard()
                        
                        # Mock clipboard and execution
                        self.harness.wizard.copy_to_clipboard = unittest.mock.MagicMock(return_value=True)
                        self.harness.wizard.execute_command = unittest.mock.MagicMock(side_effect=self.harness._capture_command)
                
                # Use our modified mock
                mock_method.side_effect = modified_mock
                
                # Call mock_command_wizard with our override
                self.harness.mock_command_wizard()
                
                # Verify default domains are still loaded
                domains = self.harness.wizard.domain_manager.list_domains()
                self.assertTrue(len(domains) > 0, "Default domains should be loaded despite file error")
                
                # Verify warning message was printed
                warning_found = False
                for line in console_output:
                    if "Warning:" in line and "tech_writing_domains.json" in line:
                        warning_found = True
                        break
                
                self.assertTrue(warning_found, "Warning message about malformed file should be printed")
        finally:
            # Stop patchers
            exists_patcher.stop()
            open_patcher.stop()
            print_patcher.stop()
    
    def test_load_learning_design_domains(self):
        """Test loading domains from learning_design_domains.json."""
        # Set up the test harness
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Create a mock learning_design_domains.json file
        learning_domains = {
            "domains": [
                {
                    "id": "instructional_design",
                    "name": "Instructional Design",
                    "description": "Creating effective learning experiences",
                    "keywords": ["learning", "education", "pedagogy"]
                },
                {
                    "id": "e_learning",
                    "name": "E-Learning",
                    "description": "Digital learning platforms and content",
                    "keywords": ["online", "digital", "remote learning"]
                }
            ]
        }
        
        # Define which files exist
        def mock_exists(path):
            return path in ["learning_design_domains.json"]
        
        # Mock file opening based on path
        def mock_open_function(file, *args, **kwargs):
            if file == "learning_design_domains.json":
                return mock_open(read_data=json.dumps(learning_domains))(file, *args, **kwargs)
            return mock_open()(file, *args, **kwargs)
        
        # Create patchers
        exists_patcher = patch('os.path.exists', mock_exists)
        open_patcher = patch('builtins.open', mock_open_function)
        
        # Start patchers
        exists_patcher.start()
        open_patcher.start()
        
        try:
            # Mock the command wizard with standard _load_domain_configs method
            with patch.object(CommandWizardTestHarness, 'mock_command_wizard') as mock_method:
                # Override the method to allow real domain loading
                def modified_mock():
                    self.harness.env_patcher = patch.dict('os.environ', {
                        'ANTHROPIC_API_KEY': 'test_key' if self.harness.api_status.get('anthropic', False) else '',
                        'OPENAI_API_KEY': 'test_key' if self.harness.api_status.get('openai', False) else '',
                        'GOOGLE_API_KEY': 'test_key' if self.harness.api_status.get('google', False) else '',
                    })
                    self.harness.env_patcher.start()
                    
                    # Create wizard without mocking _load_domain_configs
                    with patch('command_wizard.CommandWizard._detect_apis', return_value=self.harness.api_status):
                        self.harness.wizard = self.harness.wizard = CommandWizard()
                        
                        # Mock clipboard and execution
                        self.harness.wizard.copy_to_clipboard = unittest.mock.MagicMock(return_value=True)
                        self.harness.wizard.execute_command = unittest.mock.MagicMock(side_effect=self.harness._capture_command)
                
                # Use our modified mock
                mock_method.side_effect = modified_mock
                
                # Call mock_command_wizard with our override
                self.harness.mock_command_wizard()
                
                # Get the domain manager instance
                domain_manager = self.harness.wizard.domain_manager
                
                # Verify domains are loaded
                domains = domain_manager.list_domains()
                domain_names = [domain.name for domain in domains]
                
                # Verify the learning design domains are present
                self.assertIn("Instructional Design", domain_names)
                self.assertIn("E-Learning", domain_names)
                
                # Get a specific domain to verify its properties
                elearning_domain = domain_manager.get_domain("e_learning")
                self.assertIsNotNone(elearning_domain)
                self.assertEqual(elearning_domain.name, "E-Learning")
                self.assertEqual(elearning_domain.description, "Digital learning platforms and content")
                self.assertIn("online", elearning_domain.keywords)
        finally:
            # Stop patchers
            exists_patcher.stop()
            open_patcher.stop()


if __name__ == "__main__":
    unittest.main()