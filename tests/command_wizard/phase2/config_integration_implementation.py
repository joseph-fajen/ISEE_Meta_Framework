#!/usr/bin/env python3
"""
ISEE Command Wizard Configuration Integration Implementation

Implementation of improved configuration file handling for the ISEE Command Wizard.
This file will be used to update the command_wizard.py with better config file integration.
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional, Tuple

# Add path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

def select_config_file() -> Optional[str]:
    """Allow the user to select a configuration file.
    
    Returns:
        Selected configuration file or None if no file is selected.
    """
    # Find all JSON files that might be configuration files
    potential_configs = []
    try:
        for f in os.listdir():
            if f.endswith('.json') and 'config' in f.lower():
                potential_configs.append(f)
    except Exception:
        # Handle errors gracefully
        return None
    
    if not potential_configs:
        return None
    
    # Sort config files with unified_config.json first
    if "unified_config.json" in potential_configs:
        potential_configs.remove("unified_config.json")
        potential_configs.insert(0, "unified_config.json")
    
    # In a real implementation, this would ask the user to select a file
    # For this simulation, return the first config file if available
    if potential_configs:
        return potential_configs[0]
    
    return None


def validate_config_file(config_path: str) -> bool:
    """Validate that a configuration file is compatible with the ISEE framework.
    
    Args:
        config_path: Path to the configuration file.
        
    Returns:
        True if the configuration file is valid, False otherwise.
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check if the config file has the expected structure
        if not isinstance(config, dict):
            return False
        
        # Check for models configuration
        if "models" not in config:
            return False
        
        # Ensure models is either a list or a dict with sections
        models = config["models"]
        if not (isinstance(models, list) or isinstance(models, dict)):
            return False
        
        # If it's a dict, check for expected sections
        if isinstance(models, dict):
            if not any(section in models for section in ["api_models", "ollama_models"]):
                return False
        
        return True
    except (json.JSONDecodeError, IOError):
        return False


def get_config_description(config_path: str) -> str:
    """Get a description for a configuration file.
    
    Args:
        config_path: Path to the configuration file.
        
    Returns:
        Description of the configuration file.
    """
    # Check for known configuration files
    if config_path == "unified_config.json":
        return "Unified configuration with models mapped to API providers"
    elif config_path == "sample_config.json":
        return "Sample configuration for demonstration purposes"
    elif config_path == "gemini_test_config.json":
        return "Configuration for testing Google Gemini models"
    elif config_path == "ollama_config.json":
        return "Configuration for Ollama models"
    
    # Try to read the file and determine its purpose
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if "models" in config:
            models = config["models"]
            model_count = 0
            
            if isinstance(models, list):
                model_count = len(models)
            elif isinstance(models, dict):
                # Count models in each section
                api_models = models.get("api_models", [])
                ollama_models = models.get("ollama_models", [])
                model_count = len(api_models) + len(ollama_models)
            
            return f"Configuration with {model_count} model mappings"
    except (json.JSONDecodeError, IOError):
        pass
    
    return "Unknown configuration file"


def get_config_explanation(config_file: str, rich_available: bool) -> str:
    """Get explanation text for a configuration file.
    
    Args:
        config_file: Name of the configuration file.
        rich_available: Whether Rich formatting is available.
        
    Returns:
        Explanation text.
    """
    explanation = (
        f"Using {config_file} for model configuration\n\n"
        "The configuration file maps model IDs to actual API providers and includes:\n"
        "- Model names and versions\n"
        "- API provider information\n"
        "- Model-specific parameters\n\n"
        "This ensures the correct models are used for each API provider."
    )
    
    if rich_available:
        # Add rich formatting
        explanation = (
            f"[green]Using {config_file} for model configuration[/green]\n\n"
            "The configuration file maps model IDs to actual API providers and includes:\n"
            "- Model names and versions\n"
            "- API provider information\n"
            "- Model-specific parameters\n\n"
            "This ensures the correct models are used for each API provider."
        )
    
    return explanation


def generate_command_with_config(params: Dict[str, Any]) -> str:
    """Generate command with configuration file.
    
    Args:
        params: Wizard parameters.
        
    Returns:
        Command with configuration file.
    """
    cmd_parts = ["python main.py"]
    
    # Add config parameter if a configuration file was selected
    if params.get("config_file"):
        cmd_parts.append(f'--config "{params["config_file"]}"')
    # Otherwise, use unified_config.json if it exists as a fallback
    elif os.path.exists("unified_config.json"):
        cmd_parts.append('--config unified_config.json')
        
    # Add other parameters
    if params.get("query"):
        cmd_parts.append(f'--query "{params["query"]}"')
    
    # Return the command
    return " ".join(cmd_parts)


def update_command_wizard_with_config_improvements():
    """Update CommandWizard with configuration improvements.
    
    This function lists all the changes needed in command_wizard.py to
    implement the improved configuration handling.
    """
    changes = [
        {
            "method": "CommandWizard._select_config_file",
            "implementation": select_config_file,
            "description": "Add method to select configuration file"
        },
        {
            "method": "CommandWizard._validate_config_file",
            "implementation": validate_config_file,
            "description": "Add method to validate configuration file"
        },
        {
            "method": "CommandWizard._get_config_description",
            "implementation": get_config_description,
            "description": "Add method to get configuration file description"
        },
        {
            "method": "CommandWizard.generate_command",
            "change": "Update to handle configuration files",
            "description": "Update to handle selected configuration file"
        },
        {
            "method": "CommandWizard.preview_command",
            "change": "Enhance configuration explanation",
            "description": "Add better explanation of configuration file purpose"
        },
        {
            "method": "CommandWizard.run_wizard",
            "change": "Add configuration selection step",
            "description": "Add step to select configuration file"
        }
    ]
    
    return changes


if __name__ == "__main__":
    # Example usage to test the implementation
    config_file = select_config_file()
    print(f"Selected config file: {config_file}")
    
    if config_file:
        is_valid = validate_config_file(config_file)
        print(f"Config file is valid: {is_valid}")
        
        description = get_config_description(config_file)
        print(f"Config description: {description}")
        
        explanation = get_config_explanation(config_file, False)
        print(f"\nExplanation:\n{explanation}")
        
        # Test command generation
        params = {
            "config_file": config_file,
            "query": "How might we improve urban transportation?",
        }
        
        command = generate_command_with_config(params)
        print(f"\nGenerated command:\n{command}")