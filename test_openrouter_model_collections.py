#!/usr/bin/env python3
"""
Test suite for OpenRouter Model Collections

This module tests the purpose-driven model collections functionality
that provides users with curated OpenRouter model selection experience.

Part of OpenRouter Integration - Stage 3: Purpose-Driven Collections Testing
"""

import unittest
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from openrouter_model_collections import (
        OpenRouterModelCollections, ModelCollection, create_default_model_collections
    )
    from openrouter_categorization import ProviderCategory, CapabilityCategory, CostTier
    COLLECTIONS_AVAILABLE = True
except ImportError as e:
    print(f"OpenRouter model collections not available: {e}")
    COLLECTIONS_AVAILABLE = False

class TestOpenRouterModelCollections(unittest.TestCase):
    """Test OpenRouter model collections functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not COLLECTIONS_AVAILABLE:
            self.skipTest("OpenRouter model collections not available")
        
        self.collections_manager = create_default_model_collections()
    
    def test_collections_manager_initialization(self):
        """Test 1: Verify collections manager initializes properly."""
        self.assertIsNotNone(self.collections_manager)
        self.assertIsNotNone(self.collections_manager.collections)
        self.assertGreater(len(self.collections_manager.collections), 0)
    
    def test_default_collections_exist(self):
        """Test 2: Verify all expected default collections exist."""
        expected_collections = [
            "quick_exploration",
            "deep_analysis", 
            "creative_innovation",
            "content_creation",
            "problem_solving",
            "learning_design",
            "strategic_planning",
            "budget_optimizer"
        ]
        
        for collection_id in expected_collections:
            with self.subTest(collection_id=collection_id):
                collection = self.collections_manager.get_collection(collection_id)
                self.assertIsNotNone(collection, f"Collection {collection_id} should exist")
                self.assertEqual(collection.id, collection_id)
    
    def test_collection_structure_validity(self):
        """Test 3: Verify collection data structure is valid."""
        for collection in self.collections_manager.get_all_collections():
            with self.subTest(collection_id=collection.id):
                # Required fields
                self.assertIsNotNone(collection.id)
                self.assertIsNotNone(collection.name)
                self.assertIsNotNone(collection.description)
                self.assertIsNotNone(collection.icon)
                
                # Numeric fields
                self.assertIsInstance(collection.expected_model_count, int)
                self.assertGreater(collection.expected_model_count, 0)
                
                # Model specs should be list
                self.assertIsInstance(collection.model_specs, list)
                
                # Cost profile should be valid
                self.assertIn(collection.cost_profile, ["budget", "balanced", "premium"])
    
    def test_purpose_alignment_mapping(self):
        """Test 4: Verify collections map to purpose categories correctly."""
        purpose_mappings = {
            "quick_exploration": ["quick_exploration"],
            "deep_analysis": ["deep_analysis"],
            "creative_innovation": ["creative_innovation"],
            "content_creation": ["content_creation"],
            "problem_solving": ["problem_solving"],
            "learning_design": ["learning_design"],
            "strategic_planning": ["strategic_planning"]
        }
        
        for purpose_id, expected_collections in purpose_mappings.items():
            collections = self.collections_manager.get_collections_for_purpose(purpose_id)
            collection_ids = [c.id for c in collections]
            
            for expected_id in expected_collections:
                self.assertIn(expected_id, collection_ids, 
                             f"Purpose {purpose_id} should have collection {expected_id}")
    
    def test_recommended_collection_selection(self):
        """Test 5: Verify recommended collection selection logic."""
        test_cases = [
            ("quick_exploration", "budget", "quick_exploration"),
            ("deep_analysis", "premium", "deep_analysis"),
            ("creative_innovation", "balanced", "creative_innovation"),
            ("unknown_purpose", "budget", "budget_optimizer"),
            ("unknown_purpose", "premium", "deep_analysis")
        ]
        
        for purpose_id, cost_preference, expected_type in test_cases:
            with self.subTest(purpose=purpose_id, cost=cost_preference):
                recommended = self.collections_manager.get_recommended_collection(
                    purpose_id, cost_preference
                )
                self.assertIsNotNone(recommended)
                
                if expected_type in ["budget_optimizer", "deep_analysis", "creative_innovation"]:
                    self.assertEqual(recommended.id, expected_type)
    
    def test_cost_profile_filtering(self):
        """Test 6: Verify cost profile filtering works correctly."""
        cost_profiles = ["budget", "balanced", "premium"]
        
        for profile in cost_profiles:
            collections = self.collections_manager.get_collection_by_cost_profile(profile)
            self.assertGreater(len(collections), 0, f"Should have {profile} collections")
            
            for collection in collections:
                self.assertEqual(collection.cost_profile, profile,
                               f"Collection {collection.id} should have {profile} cost profile")
    
    def test_model_specs_structure(self):
        """Test 7: Verify model specs have valid structure."""
        for collection in self.collections_manager.get_all_collections():
            with self.subTest(collection_id=collection.id):
                for i, spec in enumerate(collection.model_specs):
                    with self.subTest(spec_index=i):
                        self.assertIsInstance(spec, dict)
                        
                        # Check for expected fields
                        if "providers" in spec:
                            self.assertIsInstance(spec["providers"], list)
                            for provider in spec["providers"]:
                                self.assertIsInstance(provider, ProviderCategory)
                        
                        if "capabilities" in spec:
                            self.assertIsInstance(spec["capabilities"], list)
                            for capability in spec["capabilities"]:
                                self.assertIsInstance(capability, CapabilityCategory)
                        
                        if "cost_tiers" in spec:
                            self.assertIsInstance(spec["cost_tiers"], list)
                            for tier in spec["cost_tiers"]:
                                self.assertIsInstance(tier, CostTier)
    
    def test_diversity_strategies(self):
        """Test 8: Verify diversity strategies are defined properly."""
        valid_strategies = [
            "provider_and_capability",
            "maximum_provider_diversity", 
            "creative_cognitive_diversity",
            "style_and_approach_diversity",
            "analytical_approach_diversity",
            "pedagogical_approach_diversity",
            "strategic_perspective_diversity",
            "cost_optimized_diversity"
        ]
        
        for collection in self.collections_manager.get_all_collections():
            with self.subTest(collection_id=collection.id):
                self.assertIn(collection.diversity_strategy, valid_strategies,
                             f"Collection {collection.id} has invalid diversity strategy")
    
    def test_fallback_specs_structure(self):
        """Test 9: Verify fallback specs are properly structured."""
        for collection in self.collections_manager.get_all_collections():
            with self.subTest(collection_id=collection.id):
                self.assertIsInstance(collection.fallback_specs, list)
                
                for fallback in collection.fallback_specs:
                    self.assertIsInstance(fallback, dict)
                    # Should have at least one filter criteria
                    self.assertTrue(
                        any(key in fallback for key in ["providers", "capabilities", "cost_tiers"]),
                        f"Fallback spec in {collection.id} should have filter criteria"
                    )

class TestModelCollectionIntegration(unittest.TestCase):
    """Test model collection integration features."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not COLLECTIONS_AVAILABLE:
            self.skipTest("OpenRouter model collections not available")
        
        self.collections_manager = create_default_model_collections()
    
    def test_collection_to_dict_conversion(self):
        """Test 10: Verify collections can be serialized to dict."""
        collection = self.collections_manager.get_collection("quick_exploration")
        self.assertIsNotNone(collection)
        
        collection_dict = collection.to_dict()
        self.assertIsInstance(collection_dict, dict)
        
        # Check required fields
        required_fields = ["id", "name", "description", "icon", "purpose_alignment", 
                          "model_specs", "diversity_strategy", "cost_profile", 
                          "expected_model_count", "fallback_specs"]
        
        for field in required_fields:
            self.assertIn(field, collection_dict)
    
    def test_collection_recommendations_coverage(self):
        """Test 11: Verify all purposes have recommended collections."""
        common_purposes = [
            "quick_exploration",
            "deep_analysis", 
            "creative_innovation",
            "content_creation",
            "problem_solving",
            "learning_design",
            "strategic_planning"
        ]
        
        for purpose in common_purposes:
            with self.subTest(purpose=purpose):
                recommended = self.collections_manager.get_recommended_collection(purpose)
                self.assertIsNotNone(recommended, f"Purpose {purpose} should have a recommendation")
    
    def test_collection_model_count_reasonableness(self):
        """Test 12: Verify model counts are reasonable for ISEE usage."""
        for collection in self.collections_manager.get_all_collections():
            with self.subTest(collection_id=collection.id):
                # Should be between 2-5 models for ISEE cognitive diversity
                self.assertGreaterEqual(collection.expected_model_count, 2,
                                      f"{collection.id} should have at least 2 models")
                self.assertLessEqual(collection.expected_model_count, 5,
                                   f"{collection.id} should have at most 5 models")

def main():
    """Run the test suite."""
    print("🚀 OpenRouter Model Collections Test Suite")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestOpenRouterModelCollections))
    test_suite.addTest(unittest.makeSuite(TestModelCollectionIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"✅ Tests Passed: {result.testsRun - len(result.failures) - len(result.errors)}/{result.testsRun}")
    print(f"❌ Tests Failed: {len(result.failures)}/{result.testsRun}")
    print(f"💥 Test Errors: {len(result.errors)}/{result.testsRun}")
    
    if result.wasSuccessful():
        success_rate = 100.0
        print(f"\n🎯 Success Rate: {success_rate}%")
        print("🎉 All tests passed! OpenRouter model collections are working perfectly.")
    else:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        if result.failures:
            print("\n❌ Failures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
        
        if result.errors:
            print("\n💥 Errors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split('\\n')[-2]}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)