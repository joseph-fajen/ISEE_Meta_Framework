#!/usr/bin/env python3
"""
ISEE Command Wizard Model Selection Implementation

Implementation of improved model selection logic for the ISEE Command Construction Wizard.
This file will be used to update the command_wizard.py with aligned model selection logic.
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional, Tuple

# Add path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

def get_provider_diverse_models(api_status: Dict[str, Any], model_count: int) -> List[str]:
    """Select models ensuring diversity across providers.
    
    Args:
        api_status: Dictionary with API availability information.
        model_count: Number of models to select.
        
    Returns:
        List of model IDs ensuring provider diversity.
    """
    # Create simulated model configs based on available APIs
    model_configs = {}
    
    # Add Anthropic models if available
    if api_status["anthropic"]:
        model_configs["claude-3-opus"] = {
            "id": "claude-3-opus",
            "name": "Claude 3 Opus",
            "provider": "anthropic"
        }
        model_configs["claude-3-sonnet"] = {
            "id": "claude-3-sonnet",
            "name": "Claude 3 Sonnet",
            "provider": "anthropic"
        }
        model_configs["claude-3-haiku"] = {
            "id": "claude-3-haiku",
            "name": "Claude 3 Haiku",
            "provider": "anthropic"
        }
    
    # Add OpenAI models if available
    if api_status["openai"]:
        model_configs["gpt-4-turbo"] = {
            "id": "gpt-4-turbo",
            "name": "GPT-4 Turbo",
            "provider": "openai"
        }
        model_configs["gpt-3.5-turbo"] = {
            "id": "gpt-3.5-turbo",
            "name": "GPT-3.5 Turbo",
            "provider": "openai"
        }
    
    # Add Google models if available
    if api_status["google"]:
        model_configs["gemini-2.5-pro"] = {
            "id": "gemini-2.5-pro",
            "name": "Gemini 2.5 Pro",
            "provider": "google"
        }
    
    # Add Ollama models if available
    if api_status["ollama"] and "ollama_models" in api_status:
        for model_name in api_status["ollama_models"]:
            model_configs[model_name] = {
                "id": model_name,
                "name": model_name,
                "provider": "ollama"
            }
    
    # If no API providers are available, use placeholder models
    if not model_configs:
        return [f"model_{i}" for i in range(1, model_count + 1)]
    
    # Apply the selection logic from main.py
    models = list(model_configs.keys())
    if model_count >= len(models):
        return models  # Return all available models
    
    # Group by provider
    provider_models = {}
    for model_id in models:
        model_config = model_configs[model_id]
        provider = model_config.get("provider", "")
        provider_models.setdefault(provider, []).append(model_id)
    
    # Select models to ensure diversity across providers
    selected_models = []
    
    # First, select one model from each provider
    for provider in provider_models:
        if provider_models[provider] and len(selected_models) < model_count:
            selected_models.append(provider_models[provider][0])
    
    # If we still need more models, add additional ones
    providers_cycle = list(provider_models.keys())
    idx = 0
    while len(selected_models) < model_count and idx < 100:  # avoid infinite loop
        provider = providers_cycle[idx % len(providers_cycle)]
        provider_list = provider_models[provider]
        if len(provider_list) > 1:  # If there are more models from this provider
            for model in provider_list[1:]:
                if model not in selected_models and len(selected_models) < model_count:
                    selected_models.append(model)
        idx += 1
    
    return selected_models


def get_model_display_names(selected_models: List[str]) -> List[str]:
    """Get readable names for the models.
    
    Args:
        selected_models: List of model IDs.
        
    Returns:
        List of readable model names.
    """
    selected_model_names = []
    
    for model_id in selected_models:
        if "claude" in model_id:
            selected_model_names.append(f"Anthropic: {model_id}")
        elif "gpt" in model_id:
            selected_model_names.append(f"OpenAI: {model_id}")
        elif "gemini" in model_id:
            selected_model_names.append(f"Google: {model_id}")
        else:
            selected_model_names.append(f"Ollama: {model_id}")
    
    return selected_model_names


def get_balanced_distribution_explanation(rich_available: bool) -> str:
    """Get explanation text for balanced model distribution.
    
    Args:
        rich_available: Whether Rich formatting is available.
        
    Returns:
        Explanation text.
    """
    if rich_available:
        return (
            "[dim]Balanced model distribution:[/dim]\n"
            "[dim]- Interleaves models across combinations, ensuring each model gets similar template/query varieties[/dim]\n"
            "[dim]- Without balancing, combinations are grouped by model type[/dim]"
        )
    else:
        return (
            "Balanced model distribution:\n"
            "- Interleaves models across combinations, ensuring each model gets similar template/query varieties\n"
            "- Without balancing, combinations are grouped by model type"
        )


def update_command_wizard_with_model_selection_improvements():
    """Update CommandWizard with model selection improvements.
    
    This function lists all the changes needed in command_wizard.py to 
    implement the improved model selection logic.
    """
    changes = [
        {
            "method": "CommandWizard._get_provider_diverse_models",
            "implementation": get_provider_diverse_models,
            "description": "Add method to select models with provider diversity"
        },
        {
            "method": "CommandWizard.configure_models",
            "change": "Add provider-diverse model selection",
            "description": "Update model selection to use provider-diverse logic"
        },
        {
            "method": "CommandWizard.preview_command",
            "change": "Enhance model explanation",
            "description": "Add better explanation of model selection and balanced distribution"
        }
    ]
    
    return changes


if __name__ == "__main__":
    # Example usage to test the implementation
    api_status = {
        "anthropic": True,
        "openai": True,
        "google": True,
        "ollama": True,
        "ollama_models": ["llama2", "mistral", "codellama"]
    }
    
    model_count = 3
    selected_models = get_provider_diverse_models(api_status, model_count)
    print(f"Selected models: {selected_models}")
    
    model_names = get_model_display_names(selected_models)
    print(f"Model names: {model_names}")
    
    explanation = get_balanced_distribution_explanation(False)
    print(f"\nExplanation:\n{explanation}")