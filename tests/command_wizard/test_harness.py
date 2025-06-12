#!/usr/bin/env python3
"""
ISEE Command Wizard Test Harness

A framework for testing the ISEE Command Construction Wizard.
"""

import sys
import os
import unittest
import json
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List, Optional, Tuple
import io

# Add parent directory to path to import command_wizard
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from command_wizard import CommandWizard

class CommandWizardTestHarness:
    """Test harness for CommandWizard."""
    
    def __init__(self):
        """Initialize the test harness."""
        self.wizard = None
        self.simulated_inputs = []
        self.captured_outputs = []
        self.api_status = {}
        self.captured_command = None
        
    def setup_mock_environment(
        self, 
        anthropic_api_key: bool = False,
        openai_api_key: bool = False,
        google_api_key: bool = False,
        openrouter_api_key: bool = False,
        ollama_available: bool = False,
        ollama_models: List[str] = None
    ) -> None:
        """Set up a mock environment with specific API availability.
        
        Args:
            anthropic_api_key: Whether the Anthropic API key is available.
            openai_api_key: Whether the OpenAI API key is available.
            google_api_key: Whether the Google API key is available.
            openrouter_api_key: Whether the OpenRouter API key is available.
            ollama_available: Whether Ollama is available.
            ollama_models: List of available Ollama models.
        """
        self.api_status = {
            "anthropic": anthropic_api_key,
            "openai": openai_api_key,
            "google": google_api_key,
            "openrouter": openrouter_api_key,
            "ollama": ollama_available,
            "any_api": anthropic_api_key or openai_api_key or google_api_key or openrouter_api_key,
        }
        
        if ollama_available and ollama_models:
            self.api_status["ollama_models"] = ollama_models
    
    def mock_command_wizard(self) -> None:
        """Create a CommandWizard instance with mocked dependencies."""
        # Start patching environment variables
        self.env_patcher = patch.dict('os.environ', {
            'ANTHROPIC_API_KEY': 'test_key' if self.api_status.get('anthropic', False) else '',
            'OPENAI_API_KEY': 'test_key' if self.api_status.get('openai', False) else '',
            'GOOGLE_API_KEY': 'test_key' if self.api_status.get('google', False) else '',
        })
        self.env_patcher.start()
        
        # Mock _detect_apis method to return our configured status
        with patch('command_wizard.CommandWizard._detect_apis', return_value=self.api_status):
            self.wizard = CommandWizard()
            
            # Mock specific methods for testing
            self.wizard._load_domain_configs = MagicMock()
            
            # Store original method references for selective mocking later
            self.original_methods = {
                'copy_to_clipboard': self.wizard.copy_to_clipboard,
                'execute_command': self.wizard.execute_command,
            }
            
            # Mock clipboard and execution by default
            self.wizard.copy_to_clipboard = MagicMock(return_value=True)
            self.wizard.execute_command = MagicMock(side_effect=self._capture_command)
    
    def _capture_command(self, command: str) -> bool:
        """Capture the generated command without executing it.
        
        Args:
            command: The command string.
            
        Returns:
            True to simulate successful command execution.
        """
        self.captured_command = command
        return True
            
    def teardown_mock_environment(self) -> None:
        """Clean up the mock environment."""
        if hasattr(self, 'env_patcher'):
            self.env_patcher.stop()
        
        # Restore original methods if needed
        if self.wizard and hasattr(self, 'original_methods'):
            for method_name, method in self.original_methods.items():
                setattr(self.wizard, method_name, method)
    
    def simulate_user_inputs(self, inputs: List[str]) -> None:
        """Set up a list of simulated user inputs.
        
        Args:
            inputs: List of input strings to simulate.
        """
        self.simulated_inputs = inputs
    
    def run_simulation(self) -> Dict[str, Any]:
        """Run the command wizard with simulated inputs.
        
        Returns:
            Dictionary with test results.
        """
        if not self.wizard:
            raise ValueError("Mock environment not set up. Call mock_command_wizard() first.")
        
        # Replace stdin with our simulated inputs
        with patch('builtins.input', side_effect=self.simulated_inputs):
            # Capture stdout
            captured_output = io.StringIO()
            with patch('sys.stdout', new=captured_output):
                # Run the wizard
                self.wizard.run_wizard()
                
                # Store captured output
                self.captured_outputs = captured_output.getvalue()
        
        # Return results
        return {
            "params": self.wizard.params,
            "command": self.captured_command,
            "output": self.captured_outputs
        }
    
    def get_generated_command(self) -> Optional[str]:
        """Get the generated command string.
        
        Returns:
            The generated command string or None if no command was generated.
        """
        return self.captured_command


class BaseMockTest(unittest.TestCase):
    """Base class for all command wizard tests."""
    
    def setUp(self):
        """Set up the test environment."""
        self.harness = CommandWizardTestHarness()
        
    def tearDown(self):
        """Clean up after the test."""
        self.harness.teardown_mock_environment()


# Helper functions for test case generation
def generate_api_test_cases() -> List[Dict[str, Any]]:
    """Generate test cases for API detection tests.
    
    Returns:
        List of test case configurations.
    """
    return [
        {
            "name": "no_apis",
            "description": "No API keys available",
            "config": {
                "anthropic_api_key": False,
                "openai_api_key": False,
                "google_api_key": False,
                "ollama_available": False,
            },
            "expected": {
                "simulate": True,
            }
        },
        {
            "name": "anthropic_only",
            "description": "Only Anthropic API key available",
            "config": {
                "anthropic_api_key": True,
                "openai_api_key": False,
                "google_api_key": False,
                "ollama_available": False,
            },
            "expected": {
                "simulate": False,
            }
        },
        {
            "name": "all_apis",
            "description": "All API keys available",
            "config": {
                "anthropic_api_key": True,
                "openai_api_key": True,
                "google_api_key": True,
                "ollama_available": False,
            },
            "expected": {
                "simulate": False,
            }
        },
        {
            "name": "ollama_only",
            "description": "Only Ollama available",
            "config": {
                "anthropic_api_key": False,
                "openai_api_key": False,
                "google_api_key": False,
                "ollama_available": True,
                "ollama_models": ["llama2", "mistral", "codellama"],
            },
            "expected": {
                "simulate": False,
                "use_ollama": True,
            }
        },
    ]


def generate_domain_test_cases() -> List[Dict[str, Any]]:
    """Generate test cases for domain loading tests.
    
    Returns:
        List of test case configurations.
    """
    return [
        {
            "name": "default_domains",
            "description": "Load default domains",
            "mock_files": {},
            "expected": {
                "domain_count": 5,  # Expected default domain count
            }
        },
        {
            "name": "tech_writing_domains",
            "description": "Load tech_writing_domains.json",
            "mock_files": {
                "tech_writing_domains.json": {
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
            },
            "expected": {
                "domain_count": 7,  # 5 default + 2 custom
            }
        },
        {
            "name": "malformed_domain_file",
            "description": "Handle malformed domain file",
            "mock_files": {
                "tech_writing_domains.json": "This is not valid JSON"
            },
            "expected": {
                "domain_count": 5,  # Should fall back to defaults
                "warning": True
            }
        },
    ]


def generate_template_test_cases() -> List[Dict[str, Any]]:
    """Generate test cases for template selection tests.
    
    Returns:
        List of test case configurations.
    """
    return [
        {
            "name": "all_templates",
            "description": "Select all available templates",
            "inputs": {
                "specific_templates": False,
                "instruction_count": 6,  # Select all templates (assuming 6 default templates)
            },
            "expected": {
                "specific_templates": None,
                "instructions": 6,
            }
        },
        {
            "name": "specific_templates",
            "description": "Select specific templates",
            "inputs": {
                "specific_templates": True,
                "template_selections": "1,3,5",  # Select templates 1, 3, and 5
            },
            "expected": {
                "specific_templates": ["framework_thinking", "critical_analysis", "contrarian_thinking"],
                "instructions": 3,
            }
        },
    ]


def generate_command_construction_test_cases() -> List[Dict[str, Any]]:
    """Generate test cases for command construction tests.
    
    Returns:
        List of test case configurations.
    """
    return [
        {
            "name": "simple_query",
            "description": "Simple query with no special characters",
            "params": {
                "query": "How might we improve urban transportation",
                "domain": "mobility",
                "models": 2,
                "instructions": 3,
                "variations": 2,
            },
            "expected": {
                "cmd_parts": [
                    "python main.py",
                    "--query \"How might we improve urban transportation\"",
                    "--domain \"mobility\"",
                    "--models 2",
                    "--instructions 3",
                    "--variations 2",
                ]
            }
        },
        {
            "name": "complex_query",
            "description": "Query with special characters",
            "params": {
                "query": "How might we improve user's experience with \"smart home\" devices?",
                "domain": None,
                "models": 3,
                "instructions": 4,
                "variations": 2,
            },
            "expected": {
                "cmd_parts": [
                    "python main.py",
                    "--query \"How might we improve user's experience with \\\"smart home\\\" devices?\"",
                    "--models 3",
                    "--instructions 4",
                    "--variations 2",
                ]
            }
        },
        {
            "name": "all_parameters",
            "description": "Command with all available parameters",
            "params": {
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
            },
            "expected": {
                "cmd_parts": [
                    "python main.py",
                    "--query \"How might we reduce plastic waste?\"",
                    "--domain \"sustainability\"",
                    "--models 2",
                    "--use-ollama",
                    "--balanced-models",
                    "--instructions 3",
                    "--variations 2",
                    "--max-combinations 24",
                    "--sampling-method stratified",
                    "--synthesize-method cross_pollination",
                    "--output-format json",
                    "--output-file \"results.json\"",
                    "--generate-reports",
                    "--analyze-results",
                    "--simulate",
                    "--dry-run",
                    "--save-state \"test_state.json\"",
                ]
            }
        },
    ]


# Main test suite factory
def create_test_suite() -> unittest.TestSuite:
    """Create a test suite containing all command wizard tests.
    
    Returns:
        A unittest.TestSuite containing all tests.
    """
    suite = unittest.TestSuite()
    
    # Add API detection tests
    # Add domain loading tests
    # Add template selection tests
    # Add command construction tests
    
    return suite


if __name__ == "__main__":
    # Run all tests when executed directly
    unittest.main()