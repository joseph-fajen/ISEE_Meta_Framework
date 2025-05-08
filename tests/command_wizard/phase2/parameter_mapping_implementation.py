#!/usr/bin/env python3
"""
ISEE Command Wizard Parameter Mapping Implementation

Implementation of improved parameter mapping and validation for the ISEE Command Wizard.
This file will be used to update the command_wizard.py to better align with main.py.
"""

import os
import sys
import json
import re
import subprocess
from typing import Dict, Any, List, Optional, Tuple

# Add path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

def extract_main_parameters() -> Dict[str, Dict[str, Any]]:
    """Extract parameters from main.py using the help command.
    
    Returns:
        Dictionary mapping parameter names to their details.
    """
    try:
        # Run main.py --help to get parameter information
        result = subprocess.run(["python", "main.py", "--help"], 
                                capture_output=True, text=True)
        help_text = result.stdout
        
        # Extract parameters using regex
        param_pattern = r"(?:--([a-zA-Z0-9_-]+))(?: ((?:\{[^}]+\})|(?:[A-Z_]+)))?"
        params = {}
        choice_pattern = r"\{([^}]+)\}"
        
        # Find parameters and their types
        for line in help_text.split("\n"):
            for match in re.finditer(param_pattern, line):
                param_name = match.group(1)
                param_type = "flag"  # Default type is flag (boolean)
                choices = None
                
                # If there's a type indicator
                if match.group(2):
                    type_indicator = match.group(2)
                    
                    # Check if it's a choice type
                    choice_match = re.search(choice_pattern, type_indicator)
                    if choice_match:
                        param_type = "choice"
                        choices = [choice.strip() for choice in choice_match.group(1).split(",")]
                    else:
                        # Otherwise it's a value type
                        param_type = "text"
                
                # Store parameter details
                params[param_name] = {
                    "type": param_type,
                    "required": False,  # Assume not required by default
                }
                
                # Add choices if available
                if choices:
                    params[param_name]["choices"] = choices
        
        return params
    except Exception as e:
        print(f"Warning: Could not extract parameters from main.py: {str(e)}")
        
        # Return an empty dict if extraction fails
        return {}


def validate_parameters(params: Dict[str, Any], main_params: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Validate wizard parameters against main.py parameters.
    
    Args:
        params: Wizard parameters.
        main_params: Parameters from main.py.
        
    Returns:
        Dictionary with validation results.
    """
    # Initialize validation result
    validation = {
        "valid": True,
        "issues": []
    }
    
    # Check each wizard parameter against main.py parameters
    for param_name, param_value in params.items():
        # Skip None/empty values
        if param_value is None or (isinstance(param_value, str) and not param_value):
            continue
        
        # Convert wizard parameter name to main.py parameter name
        main_param_name = param_name.replace("_", "-")
        
        # Check if the parameter exists in main.py
        if main_param_name not in main_params:
            # Some parameters are handled specially
            if param_name in ["specific_templates", "load_state", "config_file"]:
                continue
            
            validation["valid"] = False
            validation["issues"].append(f"Parameter '{param_name}' does not exist in main.py")
            continue
        
        # Get main.py parameter details
        main_param = main_params[main_param_name]
        
        # Validate based on parameter type
        if main_param["type"] == "choice" and param_value not in main_param.get("choices", []):
            validation["valid"] = False
            validation["issues"].append(
                f"Invalid value '{param_value}' for parameter '{param_name}'. "
                f"Valid choices: {', '.join(main_param.get('choices', []))}"
            )
    
    # Validate parameter dependencies
    if params.get("analyze_results") and not params.get("generate_reports"):
        validation["valid"] = False
        validation["issues"].append("'analyze_results' requires 'generate_reports' to be enabled")
    
    return validation


def show_help_options(rich_available: bool) -> str:
    """Show help information about available command-line options.
    
    Args:
        rich_available: Whether Rich formatting is available.
        
    Returns:
        Help text.
    """
    help_info = [
        {
            "name": "--help",
            "description": "Show the help message and exit",
            "usage": "python main.py --help"
        },
        {
            "name": "--list-domains",
            "description": "List all available domains and exit",
            "usage": "python main.py --list-domains"
        },
        {
            "name": "--quick",
            "description": "Run in quick mode (stratified sampling with 36 combinations)",
            "usage": "python main.py --quick --query \"Your query here\""
        },
        {
            "name": "--full",
            "description": "Run in full mode (exhaustive combinations)",
            "usage": "python main.py --full --query \"Your query here\""
        }
    ]
    
    if rich_available:
        help_text = "\n[bold cyan]Additional Command-Line Options[/bold cyan]\n\n"
        
        for option in help_info:
            help_text += f"[green]{option['name']}[/green]: {option['description']}\n"
            help_text += f"  Example: [yellow]{option['usage']}[/yellow]\n\n"
    else:
        help_text = "\nAdditional Command-Line Options:\n\n"
        for option in help_info:
            help_text += f"{option['name']}: {option['description']}\n"
            help_text += f"  Example: {option['usage']}\n\n"
    
    return help_text


def configure_advanced_options(params: Dict[str, Any], rich_available: bool) -> Dict[str, Any]:
    """Configure advanced options not covered by other steps.
    
    Args:
        params: Current wizard parameters.
        rich_available: Whether Rich formatting is available.
        
    Returns:
        Updated parameters.
    """
    # Simulate user selection for testing purposes
    output_params = params.copy()
    
    # Add domain config (simulated choice)
    output_params["domain_config"] = "learning_design_domains.json"
    
    # Add report format if reports are enabled
    if output_params.get("generate_reports"):
        output_params["report_format"] = "markdown"
    
    # Add export CSV if reports are enabled
    if output_params.get("generate_reports"):
        output_params["export_csv"] = True
    
    # Add no visualizations if analysis is enabled
    if output_params.get("analyze_results"):
        output_params["no_visualizations"] = False
    
    # Add preset mode
    output_params["quick"] = True
    
    return output_params


def update_command_wizard_with_parameter_improvements():
    """Update CommandWizard with parameter mapping improvements.
    
    This function lists all the changes needed in command_wizard.py to 
    implement the improved parameter mapping and validation.
    """
    changes = [
        {
            "method": "CommandWizard._extract_main_parameters",
            "implementation": extract_main_parameters,
            "description": "Add method to extract parameters from main.py"
        },
        {
            "method": "CommandWizard._validate_parameters",
            "implementation": validate_parameters,
            "description": "Add method to validate parameters against main.py"
        },
        {
            "method": "CommandWizard._show_help_options",
            "implementation": show_help_options,
            "description": "Add method to show help for command-line options"
        },
        {
            "method": "CommandWizard.configure_advanced_options",
            "implementation": configure_advanced_options,
            "description": "Add method to configure advanced options"
        },
        {
            "method": "CommandWizard.generate_command",
            "change": "Update to validate parameters",
            "description": "Update to validate parameters before generating command"
        },
        {
            "method": "CommandWizard.run_wizard",
            "change": "Update to add advanced options and validation",
            "description": "Update to add advanced options and validation steps"
        }
    ]
    
    return changes


if __name__ == "__main__":
    # Example usage to test the implementation
    main_params = extract_main_parameters()
    print(f"Extracted {len(main_params)} parameters from main.py")
    
    # Test parameter validation
    test_params = {
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
    
    validation = validate_parameters(test_params, main_params)
    print(f"Validation result: {validation['valid']}")
    if not validation['valid']:
        print("Issues:")
        for issue in validation['issues']:
            print(f"- {issue}")
    
    help_text = show_help_options(False)
    print(f"\nHelp text sample:\n{help_text[:200]}...")