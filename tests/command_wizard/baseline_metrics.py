#!/usr/bin/env python3
"""
ISEE Command Wizard Baseline Metrics

Establishes baseline functionality metrics for the ISEE Command Construction Wizard.
"""

import sys
import os
import json
from typing import Dict, Any, List, Tuple
import subprocess
import re

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from command_wizard import CommandWizard
from tests.command_wizard.test_harness import CommandWizardTestHarness

class BaselineMetricsGenerator:
    """Generates baseline metrics for the Command Wizard."""
    
    def __init__(self, output_dir: str = "tests/command_wizard/baseline"):
        """Initialize the metrics generator.
        
        Args:
            output_dir: Directory to save baseline metrics.
        """
        self.output_dir = output_dir
        self.harness = CommandWizardTestHarness()
        self.metrics = {
            "api_detection": {},
            "domain_loading": {},
            "template_selection": {},
            "command_construction": {},
            "command_validation": {},
            "parameter_mapping": {},
            "compatibility": {},
        }
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_all_metrics(self) -> None:
        """Generate all baseline metrics."""
        self.generate_api_detection_metrics()
        self.generate_domain_metrics()
        self.generate_template_metrics()
        self.generate_command_construction_metrics()
        self.generate_command_validation_metrics()
        self.generate_parameter_mapping_metrics()
        self.generate_compatibility_metrics()
        
        # Save the metrics
        self.save_metrics()
    
    def generate_api_detection_metrics(self) -> None:
        """Generate metrics for API detection."""
        print("Generating API detection metrics...")
        
        # Test API detection configurations
        api_configs = [
            {
                "name": "no_apis",
                "anthropic": False,
                "openai": False,
                "google": False,
                "ollama": False,
                "ollama_models": None,
            },
            {
                "name": "anthropic_only",
                "anthropic": True,
                "openai": False,
                "google": False,
                "ollama": False,
                "ollama_models": None,
            },
            {
                "name": "all_apis",
                "anthropic": True,
                "openai": True,
                "google": True,
                "ollama": False,
                "ollama_models": None,
            },
            {
                "name": "ollama_only",
                "anthropic": False,
                "openai": False,
                "google": False,
                "ollama": True,
                "ollama_models": ["llama2", "mistral", "codellama"],
            },
        ]
        
        for config in api_configs:
            # Reset test harness
            self.harness = CommandWizardTestHarness()
            
            # Set up API environment
            self.harness.setup_mock_environment(
                anthropic_api_key=config["anthropic"],
                openai_api_key=config["openai"],
                google_api_key=config["google"],
                ollama_available=config["ollama"],
                ollama_models=config["ollama_models"],
            )
            
            # Mock the command wizard
            self.harness.mock_command_wizard()
            
            # Check API status
            api_status = self.harness.wizard.api_status
            
            # Store metrics
            self.metrics["api_detection"][config["name"]] = {
                "config": config,
                "detected_status": api_status,
                "any_api_detected": api_status.get("any_api", False),
                "simulation_forced": not api_status.get("any_api", False) and not api_status.get("ollama", False),
            }
    
    def generate_domain_metrics(self) -> None:
        """Generate metrics for domain loading."""
        print("Generating domain loading metrics...")
        
        # Reset test harness
        self.harness = CommandWizardTestHarness()
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Mock the command wizard with real domain loading
        with patch.object(CommandWizardTestHarness, 'mock_command_wizard') as mock_method:
            # Override to allow real domain loading
            def modified_mock():
                self.harness.env_patcher = patch.dict('os.environ', {
                    'ANTHROPIC_API_KEY': 'test_key',
                    'OPENAI_API_KEY': '',
                    'GOOGLE_API_KEY': '',
                })
                self.harness.env_patcher.start()
                
                # Create wizard without mocking _load_domain_configs
                with patch('command_wizard.CommandWizard._detect_apis', 
                        return_value=self.harness.api_status):
                    self.harness.wizard = CommandWizard()
                    
                    # Mock clipboard and execution
                    self.harness.wizard.copy_to_clipboard = MagicMock(return_value=True)
                    self.harness.wizard.execute_command = MagicMock(
                        side_effect=self.harness._capture_command)
            
            # Use modified mock
            mock_method.side_effect = modified_mock
            self.harness.mock_command_wizard()
        
        # Get domains
        domain_manager = self.harness.wizard.domain_manager
        domains = domain_manager.list_domains()
        
        # Store metrics
        self.metrics["domain_loading"]["default"] = {
            "domain_count": len(domains),
            "domain_names": [domain.name for domain in domains],
            "domain_ids": [domain.id for domain in domains],
        }
    
    def generate_template_metrics(self) -> None:
        """Generate metrics for template selection."""
        print("Generating template metrics...")
        
        # Reset test harness
        self.harness = CommandWizardTestHarness()
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Mock the command wizard
        self.harness.mock_command_wizard()
        
        # Get templates
        template_library = self.harness.wizard.template_library
        templates = template_library.list_templates()
        
        # Store metrics
        self.metrics["template_selection"]["default"] = {
            "template_count": len(templates),
            "template_names": [template.name for template in templates],
            "template_ids": [template.id for template in templates],
            "specific_template_support": False,  # Will be updated in validation
        }
    
    def generate_command_construction_metrics(self) -> None:
        """Generate metrics for command construction."""
        print("Generating command construction metrics...")
        
        # Reset test harness
        self.harness = CommandWizardTestHarness()
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Mock the command wizard
        self.harness.mock_command_wizard()
        
        # Test various parameter combinations
        command_tests = [
            {
                "name": "minimal",
                "params": {
                    "query": "How might we improve urban transportation?",
                    "domain": None,
                    "models": 2,
                    "instructions": 3,
                    "variations": 2,
                },
            },
            {
                "name": "complex",
                "params": {
                    "query": "How might we improve user's experience with \"smart home\" devices?",
                    "domain": "technology",
                    "models": 3,
                    "use_ollama": True,
                    "balanced_models": True,
                    "instructions": 4,
                    "variations": 3,
                    "max_combinations": 36,
                    "sampling_method": "stratified",
                    "synthesize_method": "cross_pollination",
                    "output_format": "json",
                    "output_file": "results.json",
                    "generate_reports": True,
                    "analyze_results": True,
                    "simulate": True,
                    "dry_run": False,
                    "save_state": "test_state.json",
                },
            },
        ]
        
        for test in command_tests:
            # Set parameters
            self.harness.wizard.params = {
                # Default parameters
                "query": None,
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
                # Override with test parameters
                **test["params"],
            }
            
            # Generate command
            command = self.harness.wizard.generate_command()
            
            # Store metrics
            self.metrics["command_construction"][test["name"]] = {
                "params": test["params"],
                "command": command,
                "command_parts": command.split(),
                "param_count": len(command.split()) - 2,  # Subtract "python main.py"
            }
    
    def generate_command_validation_metrics(self) -> None:
        """Generate metrics for command validation."""
        print("Generating command validation metrics...")
        
        # Reset test harness
        self.harness = CommandWizardTestHarness()
        self.harness.setup_mock_environment(anthropic_api_key=True)
        
        # Mock the command wizard
        self.harness.mock_command_wizard()
        
        # Test command validation by checking if the command is executable
        command_tests = [
            {
                "name": "default",
                "params": {
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
                    "simulate": True,  # Use simulation mode to avoid API calls
                    "dry_run": True,   # Use dry run to avoid actual execution
                    "generate_reports": False,
                    "analyze_results": False,
                    "save_state": None,
                    "load_state": None,
                    "synthesize_method": "cluster_based",
                },
            },
        ]
        
        for test in command_tests:
            # Set parameters
            self.harness.wizard.params = test["params"]
            
            # Generate command
            command = self.harness.wizard.generate_command()
            
            # Check if command is valid by running it with --help to see if it parses
            try:
                # Extract just the Python command part (not the arguments)
                cmd_parts = command.split()
                cmd_base = cmd_parts[0:2]  # python main.py
                cmd_base.append("--help")
                
                # Run the help command to check if main.py exists and is executable
                result = subprocess.run(cmd_base, capture_output=True, text=True)
                valid = result.returncode == 0
                validation_message = "Command is valid" if valid else "Command is invalid"
                validation_details = result.stdout if valid else result.stderr
            except Exception as e:
                valid = False
                validation_message = f"Error validating command: {str(e)}"
                validation_details = str(e)
            
            # Store metrics
            self.metrics["command_validation"][test["name"]] = {
                "command": command,
                "valid": valid,
                "validation_message": validation_message,
                "validation_details": validation_details[:200] + "..." if len(validation_details) > 200 else validation_details,
            }
    
    def generate_parameter_mapping_metrics(self) -> None:
        """Generate metrics for parameter mapping between wizard and main.py."""
        print("Generating parameter mapping metrics...")
        
        # Get parameters from the wizard
        wizard_params = {
            "query": "text",
            "domain": "text",
            "models": "integer",
            "use_ollama": "boolean",
            "balanced_models": "boolean",
            "instructions": "integer",
            "variations": "integer",
            "max_combinations": "integer",
            "sampling_method": "choice",
            "synthesize_method": "choice",
            "output_format": "choice",
            "output_file": "text",
            "generate_reports": "boolean",
            "analyze_results": "boolean",
            "simulate": "boolean",
            "dry_run": "boolean",
            "save_state": "text",
            "load_state": "text",
        }
        
        # Extract parameters from main.py using --help
        try:
            result = subprocess.run(["python", "main.py", "--help"], capture_output=True, text=True)
            help_text = result.stdout
            
            # Extract parameters using regex
            param_pattern = r"(--[a-zA-Z0-9-]+)(?:\s+([A-Z_]+))?"
            main_params = {}
            
            for line in help_text.split("\n"):
                matches = re.finditer(param_pattern, line)
                for match in matches:
                    param_name = match.group(1)
                    param_type = match.group(2) if match.group(2) else "boolean"
                    
                    # Convert parameter name to wizard format
                    wizard_name = param_name[2:].replace("-", "_")
                    
                    # Determine parameter type
                    if param_type:
                        if "INT" in param_type:
                            param_type = "integer"
                        elif "CHOICES" in param_type:
                            param_type = "choice"
                        elif "FILE" in param_type or "DIR" in param_type:
                            param_type = "text"
                        else:
                            param_type = "text"
                    
                    main_params[wizard_name] = param_type
            
            # Compare parameters
            matching_params = {}
            missing_in_main = {}
            missing_in_wizard = {}
            type_mismatches = {}
            
            for param, type_ in wizard_params.items():
                if param in main_params:
                    if main_params[param] == type_ or (main_params[param] == "boolean" and type_ == "boolean"):
                        matching_params[param] = type_
                    else:
                        type_mismatches[param] = {
                            "wizard_type": type_,
                            "main_type": main_params[param],
                        }
                else:
                    missing_in_main[param] = type_
            
            for param, type_ in main_params.items():
                if param not in wizard_params:
                    missing_in_wizard[param] = type_
            
            # Store metrics
            self.metrics["parameter_mapping"] = {
                "matching_params": matching_params,
                "type_mismatches": type_mismatches,
                "missing_in_main": missing_in_main,
                "missing_in_wizard": missing_in_wizard,
                "total_wizard_params": len(wizard_params),
                "total_main_params": len(main_params),
                "match_percentage": len(matching_params) / len(wizard_params) * 100,
            }
        except Exception as e:
            self.metrics["parameter_mapping"] = {
                "error": f"Error extracting parameters: {str(e)}",
            }
    
    def generate_compatibility_metrics(self) -> None:
        """Generate metrics for compatibility between wizard and main.py."""
        print("Generating compatibility metrics...")
        
        # Generate a command and check if it is accepted by main.py
        self.harness = CommandWizardTestHarness()
        self.harness.setup_mock_environment(anthropic_api_key=True)
        self.harness.mock_command_wizard()
        
        # Create a minimal command with simulation and dry run
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
            "simulate": True,  # Use simulation mode to avoid API calls
            "dry_run": True,   # Use dry run to avoid actual execution
            "generate_reports": False,
            "analyze_results": False,
            "save_state": None,
            "load_state": None,
            "synthesize_method": "cluster_based",
        }
        
        # Generate the command
        command = self.harness.wizard.generate_command()
        
        # Try to execute the command
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            valid = result.returncode == 0
            validation_message = "Command is valid" if valid else "Command is invalid"
            
            # Store metrics
            self.metrics["compatibility"] = {
                "command": command,
                "valid": valid,
                "validation_message": validation_message,
                "stdout": result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout,
                "stderr": result.stderr[:200] + "..." if len(result.stderr) > 200 else result.stderr,
            }
        except Exception as e:
            self.metrics["compatibility"] = {
                "command": command,
                "valid": False,
                "validation_message": f"Error executing command: {str(e)}",
                "error": str(e),
            }
    
    def save_metrics(self) -> None:
        """Save metrics to file."""
        metrics_file = os.path.join(self.output_dir, "baseline_metrics.json")
        with open(metrics_file, "w") as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"Baseline metrics saved to {metrics_file}")
        
        # Also save a summary in markdown format
        summary_file = os.path.join(self.output_dir, "baseline_summary.md")
        with open(summary_file, "w") as f:
            f.write("# Command Wizard Baseline Metrics Summary\n\n")
            
            # API Detection
            f.write("## API Detection\n\n")
            for name, data in self.metrics["api_detection"].items():
                f.write(f"### {name}\n\n")
                f.write(f"- Any API detected: {data['any_api_detected']}\n")
                f.write(f"- Simulation forced: {data['simulation_forced']}\n\n")
            
            # Domain Loading
            f.write("## Domain Loading\n\n")
            domain_data = self.metrics["domain_loading"]["default"]
            f.write(f"- Total domains: {domain_data['domain_count']}\n")
            f.write(f"- Domain names: {', '.join(domain_data['domain_names'])}\n\n")
            
            # Template Selection
            f.write("## Template Selection\n\n")
            template_data = self.metrics["template_selection"]["default"]
            f.write(f"- Total templates: {template_data['template_count']}\n")
            f.write(f"- Template names: {', '.join(template_data['template_names'])}\n")
            f.write(f"- Specific template support: {template_data['specific_template_support']}\n\n")
            
            # Command Construction
            f.write("## Command Construction\n\n")
            for name, data in self.metrics["command_construction"].items():
                f.write(f"### {name}\n\n")
                f.write(f"- Command: `{data['command']}`\n")
                f.write(f"- Parameter count: {data['param_count']}\n\n")
            
            # Command Validation
            f.write("## Command Validation\n\n")
            for name, data in self.metrics["command_validation"].items():
                f.write(f"### {name}\n\n")
                f.write(f"- Valid: {data['valid']}\n")
                f.write(f"- Message: {data['validation_message']}\n\n")
            
            # Parameter Mapping
            f.write("## Parameter Mapping\n\n")
            if "error" in self.metrics["parameter_mapping"]:
                f.write(f"Error: {self.metrics['parameter_mapping']['error']}\n\n")
            else:
                f.write(f"- Total wizard parameters: {self.metrics['parameter_mapping']['total_wizard_params']}\n")
                f.write(f"- Total main.py parameters: {self.metrics['parameter_mapping']['total_main_params']}\n")
                f.write(f"- Match percentage: {self.metrics['parameter_mapping']['match_percentage']:.1f}%\n")
                
                f.write("\n### Missing in main.py\n\n")
                for param, type_ in self.metrics["parameter_mapping"]["missing_in_main"].items():
                    f.write(f"- {param} ({type_})\n")
                
                f.write("\n### Missing in wizard\n\n")
                for param, type_ in self.metrics["parameter_mapping"]["missing_in_wizard"].items():
                    f.write(f"- {param} ({type_})\n")
                
                f.write("\n### Type mismatches\n\n")
                for param, data in self.metrics["parameter_mapping"]["type_mismatches"].items():
                    f.write(f"- {param}: Wizard {data['wizard_type']} vs Main {data['main_type']}\n")
            
            # Compatibility
            f.write("\n## Compatibility\n\n")
            compat_data = self.metrics["compatibility"]
            f.write(f"- Command: `{compat_data['command']}`\n")
            f.write(f"- Valid: {compat_data['valid']}\n")
            f.write(f"- Message: {compat_data['validation_message']}\n")
        
        print(f"Baseline summary saved to {summary_file}")


if __name__ == "__main__":
    # Fix for import errors
    from unittest.mock import patch, MagicMock
    
    # Generate baseline metrics
    generator = BaselineMetricsGenerator()
    generator.generate_all_metrics()