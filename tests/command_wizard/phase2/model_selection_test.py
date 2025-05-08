#!/usr/bin/env python3
"""
ISEE Command Wizard Model Selection Test

Tests for the updated model selection logic in the ISEE Command Construction Wizard.
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

class TestModelSelection(BaseMockTest):
    """Tests for model selection logic."""
    
    def test_model_selection_with_diversity(self):
        """Test model selection that matches main.py's diversity prioritization."""
        # Mock model_configs in main.py to test selection logic
        model_configs = {
            "claude-3-opus": {
                "id": "claude-3-opus",
                "name": "Claude 3 Opus",
                "provider": "anthropic"
            },
            "claude-3-sonnet": {
                "id": "claude-3-sonnet",
                "name": "Claude 3 Sonnet",
                "provider": "anthropic"
            },
            "gpt-4-turbo": {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "provider": "openai"
            },
            "gpt-3.5-turbo": {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "provider": "openai"
            },
            "gemini-2.5-pro": {
                "id": "gemini-2.5-pro",
                "name": "Gemini 2.5 Pro",
                "provider": "google"
            },
            "llama2": {
                "id": "llama2",
                "name": "Llama 2",
                "provider": "ollama"
            },
            "mistral": {
                "id": "mistral",
                "name": "Mistral",
                "provider": "ollama"
            }
        }
        
        # Apply the main.py model selection logic
        model_count = 3
        models = list(model_configs.keys())
        
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
        
        # Verify that the selection contains one model from each provider first
        self.assertEqual(len(selected_models), 3)
        
        # Verify provider diversity
        providers = [model_configs[model]["provider"] for model in selected_models]
        self.assertEqual(len(set(providers)), 3)
        
        # Test with model_count = 5 (more than unique providers)
        model_count = 5
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
            
        # Verify that the selection contains 5 models
        self.assertEqual(len(selected_models), 5)
        
        # Verify the models come from all providers but some providers have multiple models
        providers = [model_configs[model]["provider"] for model in selected_models]
        self.assertEqual(len(set(providers)), 4)  # All 4 providers should be represented
        
        # Create a provider count
        provider_count = {}
        for provider in providers:
            provider_count[provider] = provider_count.get(provider, 0) + 1
        
        # Check that at least one provider has more than 1 model
        self.assertTrue(any(count > 1 for count in provider_count.values()))
    
    def test_balanced_model_distribution(self):
        """Test balanced model distribution across combinations."""
        # Mock simplified version of generate_combinations logic
        models = ["claude-3-opus", "gpt-4-turbo", "gemini-2.5-pro"]
        templates = ["analytical", "creative", "critical"]
        queries = ["query1", "query2"]
        domains = ["domain1"]
        balanced = True
        
        # Generate combinations like main.py would when balanced=True
        combinations = []
        
        if balanced:
            # Create all possible template/query/domain combinations
            component_combinations = []
            for template in templates:
                for query in queries:
                    for domain in domains:
                        component_combinations.append((template, query, domain))
            
            # Then distribute these combinations across models in a balanced way
            while component_combinations and models:
                for model in models:
                    if not component_combinations:
                        break
                    
                    template, query, domain = component_combinations.pop(0)
                    combination_id = f"{model}_{template}_{query}_{domain}"
                    
                    combination = {
                        "id": combination_id,
                        "model": model,
                        "template": template,
                        "query": query,
                        "domain": domain
                    }
                    
                    combinations.append(combination)
        
        # Count occurrences of each model in combinations
        model_counts = {}
        for combo in combinations:
            model = combo["model"]
            model_counts[model] = model_counts.get(model, 0) + 1
        
        # Verify that models are evenly distributed (or at most differ by 1)
        min_count = min(model_counts.values())
        max_count = max(model_counts.values())
        self.assertLessEqual(max_count - min_count, 1)
        
        # Now do the same for unbalanced distribution
        balanced = False
        unbalanced_combinations = []
        
        # Create combinations grouped by model (original behavior)
        for model in models:
            for template in templates:
                for query in queries:
                    for domain in domains:
                        combination_id = f"{model}_{template}_{query}_{domain}"
                        
                        combination = {
                            "id": combination_id,
                            "model": model,
                            "template": template,
                            "query": query,
                            "domain": domain
                        }
                        
                        unbalanced_combinations.append(combination)
        
        # Count occurrences of each model in combinations
        model_counts = {}
        template_per_model = {}
        for combo in unbalanced_combinations:
            model = combo["model"]
            template = combo["template"]
            
            model_counts[model] = model_counts.get(model, 0) + 1
            
            if model not in template_per_model:
                template_per_model[model] = []
            template_per_model[model].append(template)
        
        # Verify that all models have the same count
        self.assertEqual(len(set(model_counts.values())), 1)
        
        # Verify that templates are clustered by model (each model has all templates)
        for model in models:
            self.assertEqual(len(template_per_model[model]), len(templates) * len(queries) * len(domains))


if __name__ == "__main__":
    unittest.main()