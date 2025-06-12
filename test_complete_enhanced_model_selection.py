#!/usr/bin/env python3
"""
Complete Integration Test: Enhanced Model Selection

Tests the complete enhanced model selection flow including the new individual
Top 20 model selection alongside existing collection-based selection.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from command_wizard import CommandWizard
    from openrouter_model_collections import create_default_model_collections
    from rich.console import Console
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

class TestCompleteEnhancedModelSelection(unittest.TestCase):
    """Complete integration tests for enhanced model selection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wizard = CommandWizard()
        
        # Set up test environment
        self.wizard.api_status = {
            "openrouter": True,
            "anthropic": False,
            "openai": False,
            "google": False,
            "ollama": False
        }
        
        # Set up OpenRouter collections
        self.wizard.openrouter_collections = create_default_model_collections()
        
        # Reset params
        self.wizard.params = {}
    
    def test_basic_mode_uses_collections(self):
        """Test that basic complexity mode uses collections (not individual selection)."""
        self.wizard.complexity_level = "basic"
        
        # Mock the collection selection
        with patch.object(self.wizard, '_apply_model_collection') as mock_apply:
            with patch('rich.prompt.IntPrompt.ask', return_value=1):  # Select Top Performers
                with patch.object(self.wizard, 'console'):
                    self.wizard._select_model_collection(4)
                    
                    # Should have called apply_model_collection (not individual selection)
                    self.assertTrue(mock_apply.called)
    
    def test_expert_mode_offers_individual_selection(self):
        """Test that expert mode offers individual model selection option."""
        self.wizard.complexity_level = "expert"
        
        # Mock user selecting individual models (option 1)
        with patch('rich.prompt.IntPrompt.ask', return_value=1):
            with patch.object(self.wizard, '_select_individual_models') as mock_individual:
                with patch.object(self.wizard, 'console'):
                    self.wizard._select_model_collection(4)
                    
                    # Should have called individual selection
                    self.assertTrue(mock_individual.called)
    
    def test_expert_mode_collections_fallback(self):
        """Test that expert mode can still use collections (option 2)."""
        self.wizard.complexity_level = "expert"
        
        # Mock user selecting collections (option 2)  
        with patch('rich.prompt.IntPrompt.ask', return_value=2):
            with patch.object(self.wizard, '_apply_model_collection') as mock_apply:
                with patch('rich.prompt.Prompt.ask', return_value="1"):  # Select first collection
                    with patch.object(self.wizard, 'console'):
                        self.wizard._select_model_collection(4)
                        
                        # Should have called collection application
                        self.assertTrue(mock_apply.called)
    
    def test_expert_mode_legacy_fallback(self):
        """Test that expert mode can use legacy selection (option 3)."""
        self.wizard.complexity_level = "expert"
        
        # Mock user selecting legacy (option 3)
        with patch('rich.prompt.IntPrompt.ask', return_value=3):
            with patch.object(self.wizard, '_legacy_model_selection') as mock_legacy:
                with patch.object(self.wizard, 'console'):
                    self.wizard._select_model_collection(4)
                    
                    # Should have called legacy selection
                    self.assertTrue(mock_legacy.called)
    
    @patch('rich.prompt.Prompt.ask')
    def test_individual_selection_sets_correct_params(self, mock_prompt):
        """Test that individual selection sets the correct parameters."""
        # Mock user selecting models 1,5,10
        mock_prompt.return_value = "1,5,10"
        
        with patch.object(self.wizard, 'console'):
            self.wizard._select_individual_models()
            
            # Check that correct parameters were set
            self.assertIn("openrouter_filters", self.wizard.params)
            self.assertIn("specific_models", self.wizard.params["openrouter_filters"])
            self.assertEqual(len(self.wizard.params["openrouter_filters"]["specific_models"]), 3)
            self.assertEqual(self.wizard.params["config_file"], "openrouter_config.json")
            self.assertEqual(self.wizard.params["models"], 3)
            self.assertTrue(self.wizard.params.get("balanced_models", False))
    
    @patch('rich.prompt.Prompt.ask')
    def test_individual_selection_handles_all_selection(self, mock_prompt):
        """Test that 'all' selection works correctly."""
        # Mock user selecting 'all'
        mock_prompt.return_value = "all"
        
        with patch.object(self.wizard, 'console'):
            self.wizard._select_individual_models()
            
            # Should select all 20 models
            self.assertEqual(len(self.wizard.params["openrouter_filters"]["specific_models"]), 20)
            self.assertEqual(self.wizard.params["models"], 20)
    
    @patch('rich.prompt.Prompt.ask')
    def test_individual_selection_handles_default(self, mock_prompt):
        """Test that default selection (empty input) works correctly."""
        # Mock user pressing enter (empty input)
        mock_prompt.return_value = ""
        
        with patch.object(self.wizard, 'console'):
            self.wizard._select_individual_models()
            
            # Should select top 3 models by default
            self.assertEqual(len(self.wizard.params["openrouter_filters"]["specific_models"]), 3)
            self.assertEqual(self.wizard.params["models"], 3)
    
    def test_collection_priority_order(self):
        """Test that Top Performers appears as #1 in collections."""
        self.wizard.complexity_level = "basic"  # Use collections mode
        self.wizard.selected_purpose = Mock()
        self.wizard.selected_purpose.id = "deep_analysis"
        
        # Get collections in the order they would be presented
        purpose_id = self.wizard.selected_purpose.id
        recommended_collection = self.wizard.openrouter_collections.get_recommended_collection(purpose_id)
        
        collections = []
        
        # Always add Top Performers first (priority positioning)
        top_performers = self.wizard.openrouter_collections.get_collection("top_performers")
        if top_performers:
            collections.append(top_performers)
        
        # Add purpose-recommended collection as #2 if different from Top Performers
        if recommended_collection and recommended_collection != top_performers:
            collections.append(recommended_collection)
        
        # Verify Top Performers is first
        self.assertEqual(collections[0].id, "top_performers")
        self.assertEqual(collections[0].name, "Top Performers")
    
    def test_no_openrouter_fallback(self):
        """Test fallback when OpenRouter is not available."""
        # Disable OpenRouter
        self.wizard.api_status["openrouter"] = False
        self.wizard.openrouter_collections = None
        
        with patch.object(self.wizard, '_legacy_model_selection') as mock_legacy:
            with patch.object(self.wizard, 'console'):
                self.wizard._select_model_collection(4)
                
                # Should fallback to legacy selection
                self.assertTrue(mock_legacy.called)
    
    def test_invalid_selection_handling(self):
        """Test handling of invalid model selections."""
        # Test invalid range
        result = self.wizard._parse_model_selection("1-", 20)
        self.assertEqual(result, [])  # Should return empty for invalid range
        
        # Test invalid number
        result = self.wizard._parse_model_selection("abc", 20)
        self.assertEqual(result, [])  # Should return empty for invalid input
        
        # Test out of bounds
        result = self.wizard._parse_model_selection("25", 20)
        self.assertEqual(result, [])  # Should return empty for out of bounds

if __name__ == "__main__":
    print("Running Complete Enhanced Model Selection Integration Tests...")
    unittest.main(verbosity=2)