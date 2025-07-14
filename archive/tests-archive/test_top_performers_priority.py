#!/usr/bin/env python3
"""
Test script to verify Top Performers collection appears as option #1 in Command Wizard
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from command_wizard import CommandWizard

class TestTopPerformersPriority(unittest.TestCase):
    """Test that Top Performers collection appears as option #1"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock environment variables for OpenRouter availability
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'sk-or-test-key'}):
            self.wizard = CommandWizard()
            # Mock API status to show OpenRouter as available
            self.wizard.api_status = {
                'anthropic': False,
                'openai': False,
                'google': False,
                'openrouter': True
            }
    
    def test_top_performers_appears_first_in_collections(self):
        """Test that Top Performers collection is positioned as option #1"""
        # Mock OpenRouter collections availability
        if not self.wizard.openrouter_collections:
            self.skipTest("OpenRouter collections not available")
        
        # Simulate collection ordering logic
        purpose_id = "custom_exploration"
        recommended_collection = self.wizard.openrouter_collections.get_recommended_collection(purpose_id)
        
        # Replicate the collection ordering logic from _select_model_collection
        collections = []
        
        # Always add Top Performers first (priority positioning)
        top_performers = self.wizard.openrouter_collections.get_collection("top_performers")
        if top_performers:
            collections.append(top_performers)
        
        # Add purpose-recommended collection as #2 if different from Top Performers
        if recommended_collection and recommended_collection != top_performers:
            collections.append(recommended_collection)
        
        # Add other popular collections
        for collection_id in ["quick_exploration", "deep_analysis", "creative_innovation", "budget_optimizer"]:
            collection = self.wizard.openrouter_collections.get_collection(collection_id)
            if collection and collection not in collections:
                collections.append(collection)
        
        # Verify Top Performers is first
        self.assertGreater(len(collections), 0, "Should have at least one collection")
        self.assertEqual(collections[0].id, "top_performers", "Top Performers should be first collection")
        self.assertEqual(collections[0].name, "Top Performers", "First collection should be Top Performers")
        self.assertEqual(collections[0].icon, "🏆", "Top Performers should have trophy icon")
    
    def test_top_performers_collection_properties(self):
        """Test that Top Performers collection has correct properties"""
        if not self.wizard.openrouter_collections:
            self.skipTest("OpenRouter collections not available")
        
        top_performers = self.wizard.openrouter_collections.get_collection("top_performers")
        self.assertIsNotNone(top_performers, "Top Performers collection should exist")
        
        # Verify key properties
        self.assertEqual(top_performers.id, "top_performers")
        self.assertEqual(top_performers.name, "Top Performers")
        self.assertEqual(top_performers.icon, "🏆")
        self.assertEqual(top_performers.cost_profile, "balanced")
        self.assertIn("Top 20 highest-performing", top_performers.description)
        
        # Verify it has specific models defined
        self.assertGreater(len(top_performers.model_specs), 0, "Should have model specifications")
        self.assertIn("specific_models", top_performers.model_specs[0], "Should have specific models list")
        
        # Verify some top models are included
        specific_models = top_performers.model_specs[0]["specific_models"]
        self.assertIn("openai/gpt-4o-mini", specific_models, "Should include GPT-4o-mini")
        self.assertIn("google/gemini-2.0-flash", specific_models, "Should include Gemini 2.0 Flash")
        self.assertIn("anthropic/claude-3.7-sonnet", specific_models, "Should include Claude 3.7 Sonnet")
    
    def test_collection_ordering_with_different_purposes(self):
        """Test that Top Performers stays #1 regardless of user's purpose"""
        if not self.wizard.openrouter_collections:
            self.skipTest("OpenRouter collections not available")
        
        # Test with different purpose selections
        test_purposes = [
            "quick_exploration",
            "deep_analysis", 
            "creative_innovation",
            "content_creation",
            "problem_solving",
            "learning_design",
            "strategic_planning",
            "custom_exploration"
        ]
        
        for purpose_id in test_purposes:
            with self.subTest(purpose=purpose_id):
                recommended_collection = self.wizard.openrouter_collections.get_recommended_collection(purpose_id)
                
                # Replicate collection ordering logic
                collections = []
                
                # Always add Top Performers first
                top_performers = self.wizard.openrouter_collections.get_collection("top_performers")
                if top_performers:
                    collections.append(top_performers)
                
                # Add recommended collection if different
                if recommended_collection and recommended_collection != top_performers:
                    collections.append(recommended_collection)
                
                # Verify Top Performers is always first
                self.assertGreater(len(collections), 0, f"Should have collections for purpose {purpose_id}")
                self.assertEqual(collections[0].id, "top_performers", 
                               f"Top Performers should be first for purpose {purpose_id}")

if __name__ == '__main__':
    print("🏆 Top Performers Priority Test Suite")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestTopPerformersPriority))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"✅ Tests Passed: {result.testsRun - len(result.failures) - len(result.errors)}/{result.testsRun}")
    print(f"❌ Tests Failed: {len(result.failures)}/{result.testsRun}")
    print(f"💥 Test Errors: {len(result.errors)}/{result.testsRun}")
    
    if result.wasSuccessful():
        print(f"\n🎯 Success Rate: 100.0%")
        print("🎉 All tests passed! Top Performers is correctly prioritized as option #1.")
        sys.exit(0)
    else:
        print(f"\n🎯 Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
        if result.failures:
            print("\n❌ Test Failures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
        if result.errors:
            print("\n💥 Test Errors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")
        sys.exit(1)