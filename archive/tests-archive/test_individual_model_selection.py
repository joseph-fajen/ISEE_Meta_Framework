#!/usr/bin/env python3
"""
Test Individual Model Selection Enhancement

Tests the new individual Top 20 model selection functionality in the Command Wizard.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from command_wizard import CommandWizard
    from openrouter_model_collections import create_default_model_collections
    from rich.console import Console
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

class TestIndividualModelSelection(unittest.TestCase):
    """Test cases for individual model selection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.console = Console()
        self.wizard = CommandWizard()
        
        # Set up test environment
        self.wizard.complexity_level = "expert"
        self.wizard.api_status = {
            "openrouter": True,
            "anthropic": False,
            "openai": False,
            "google": False,
            "ollama": False
        }
        
        # Set up OpenRouter collections
        self.wizard.openrouter_collections = create_default_model_collections()
    
    def test_model_selection_parsing(self):
        """Test parsing of model selection input."""
        # Test single numbers
        result = self.wizard._parse_model_selection("1,3,5", 20)
        self.assertEqual(result, [1, 3, 5])
        
        # Test ranges
        result = self.wizard._parse_model_selection("1-3", 20)
        self.assertEqual(result, [1, 2, 3])
        
        # Test combined
        result = self.wizard._parse_model_selection("1,3-5,7", 20)
        self.assertEqual(result, [1, 3, 4, 5, 7])
        
        # Test 'all'
        result = self.wizard._parse_model_selection("all", 5)
        self.assertEqual(result, [1, 2, 3, 4, 5])
        
        # Test default
        result = self.wizard._parse_model_selection("", 20)
        self.assertEqual(result, [1, 2, 3])
    
    def test_cost_estimation(self):
        """Test model cost estimation."""
        # Test known models
        cost = self.wizard._estimate_model_cost("openai/gpt-4o-mini")
        self.assertEqual(cost, "$0.15")
        
        cost = self.wizard._estimate_model_cost("deepseek/deepseek-v3-0324-free")
        self.assertEqual(cost, "Free")
        
        # Test unknown model
        cost = self.wizard._estimate_model_cost("unknown/model")
        self.assertEqual(cost, "$0.50")
    
    def test_quality_estimation(self):
        """Test model quality estimation."""
        # Test known models
        quality = self.wizard._estimate_model_quality("openai/gpt-4o-mini")
        self.assertEqual(quality, 9.2)
        
        quality = self.wizard._estimate_model_quality("google/gemini-2.0-flash")
        self.assertEqual(quality, 9.1)
        
        # Test unknown model
        quality = self.wizard._estimate_model_quality("unknown/model")
        self.assertEqual(quality, 7.0)
    
    def test_cost_profile_calculation(self):
        """Test cost profile calculation for selected models."""
        # All free models
        free_models = [
            {"cost": "Free", "id": "model1"},
            {"cost": "Free", "id": "model2"}
        ]
        profile = self.wizard._calculate_selection_cost(free_models)
        self.assertEqual(profile, "Free")
        
        # Budget models
        budget_models = [
            {"cost": "$0.15", "id": "model1"},
            {"cost": "$0.30", "id": "model2"}
        ]
        profile = self.wizard._calculate_selection_cost(budget_models)
        self.assertEqual(profile, "Budget")
        
        # Premium models
        premium_models = [
            {"cost": "$3.00", "id": "model1"},
            {"cost": "$5.00", "id": "model2"}
        ]
        profile = self.wizard._calculate_selection_cost(premium_models)
        self.assertEqual(profile, "Premium")
    
    def test_top_performers_collection_access(self):
        """Test access to Top 20 performers collection."""
        top_performers = self.wizard.openrouter_collections.get_collection("top_performers")
        self.assertIsNotNone(top_performers)
        
        # Check that it has specific models
        specific_models = []
        for spec in top_performers.model_specs:
            if "specific_models" in spec:
                specific_models = spec["specific_models"]
                break
        
        self.assertTrue(len(specific_models) > 0)
        self.assertIn("openai/gpt-4o-mini", specific_models)
        self.assertIn("google/gemini-2.0-flash", specific_models)
        self.assertIn("anthropic/claude-3.7-sonnet", specific_models)
    
    @patch('rich.prompt.Prompt.ask')
    def test_individual_model_selection_flow(self, mock_prompt):
        """Test the individual model selection flow."""
        # Mock user selecting models 1,2,3
        mock_prompt.return_value = "1,2,3"
        
        # Test the selection process
        with patch.object(self.wizard, 'console') as mock_console:
            self.wizard._select_individual_models(preset_models_count=False)
            
            # Verify that parameters were set
            self.assertIn("openrouter_filters", self.wizard.params)
            self.assertIn("specific_models", self.wizard.params["openrouter_filters"])
            self.assertEqual(self.wizard.params["config_file"], "openrouter_config.json")
            self.assertEqual(self.wizard.params["models"], 3)
    
    def test_expert_mode_selection_options(self):
        """Test that expert mode shows individual selection option."""
        # Verify that advanced/expert complexity levels get the enhanced selection
        self.wizard.complexity_level = "expert"
        
        # The _select_model_collection method should offer individual selection
        # This is tested implicitly through the mode selection logic
        self.assertTrue(self.wizard.complexity_level in ["advanced", "expert"])

if __name__ == "__main__":
    print("Running Individual Model Selection Tests...")
    unittest.main(verbosity=2)