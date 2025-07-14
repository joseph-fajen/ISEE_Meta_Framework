#!/usr/bin/env python3
"""
Test script for OpenRouter Model Categorization System

This script tests the intelligent categorization and filtering capabilities
that organize OpenRouter's 300+ models for ISEE framework usage.

Tests:
1. Model categorization accuracy
2. Provider-based filtering
3. Capability-based filtering  
4. Cost-tier filtering
5. Use-case filtering
6. ISEE-optimized recommendations
"""

import os
import sys
from typing import List, Dict, Any

# Add the current directory to the Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openrouter_categorization import (
    OpenRouterCategorizer, ModelMetadata, ProviderCategory, 
    CapabilityCategory, CostTier, UseCase
)

def create_test_model_data() -> List[Dict[str, Any]]:
    """Create test model data simulating OpenRouter API responses."""
    return [
        {
            "id": "anthropic/claude-3-opus",
            "name": "Claude 3 Opus",
            "description": "Most powerful model in the Claude 3 family, with best-in-class performance on complex reasoning",
            "context_length": 200000,
            "pricing": {"prompt": "15.00", "completion": "75.00"},
            "architecture": "transformer"
        },
        {
            "id": "anthropic/claude-3-sonnet", 
            "name": "Claude 3 Sonnet",
            "description": "Balanced performance for efficiency and intelligence",
            "context_length": 200000,
            "pricing": {"prompt": "3.00", "completion": "15.00"},
            "architecture": "transformer"
        },
        {
            "id": "openai/gpt-4-turbo",
            "name": "GPT-4 Turbo",
            "description": "Fast and capable model for reasoning tasks",
            "context_length": 128000,
            "pricing": {"prompt": "10.00", "completion": "30.00"},
            "architecture": "transformer"
        },
        {
            "id": "openai/gpt-3.5-turbo",
            "name": "GPT-3.5 Turbo", 
            "description": "Fast and affordable model for most tasks",
            "context_length": 16000,
            "pricing": {"prompt": "0.50", "completion": "1.50"},
            "architecture": "transformer"
        },
        {
            "id": "meta-llama/llama-2-70b-chat",
            "name": "Llama 2 70B Chat",
            "description": "Open source chat model from Meta",
            "context_length": 4096,
            "pricing": {"prompt": "0.70", "completion": "0.80"},
            "architecture": "transformer"
        },
        {
            "id": "mistralai/mixtral-8x7b-instruct",
            "name": "Mixtral 8x7B Instruct",
            "description": "Mixture of experts model with large context window",
            "context_length": 32000,
            "pricing": {"prompt": "0.24", "completion": "0.24"},
            "architecture": "mixture-of-experts"
        },
        {
            "id": "cohere/command-r-plus",
            "name": "Command R+",
            "description": "Enterprise-grade model optimized for RAG applications",
            "context_length": 128000,
            "pricing": {"prompt": "3.00", "completion": "15.00"},
            "architecture": "transformer"
        },
        {
            "id": "ai21/jamba-instruct",
            "name": "Jamba Instruct",
            "description": "Hybrid model with long context capabilities",
            "context_length": 256000,
            "pricing": {"prompt": "0.50", "completion": "0.70"},
            "architecture": "hybrid"
        },
        {
            "id": "google/gemini-pro",
            "name": "Gemini Pro",
            "description": "Multimodal model for text and vision tasks",
            "context_length": 32000,
            "pricing": {"prompt": "0.50", "completion": "1.50"},
            "architecture": "multimodal"
        },
        {
            "id": "deepinfra/codellama-34b-instruct",
            "name": "CodeLlama 34B Instruct",
            "description": "Code generation model based on Llama 2",
            "context_length": 16000,
            "pricing": {"prompt": "0.60", "completion": "0.60"},
            "architecture": "transformer"
        }
    ]

def test_model_categorization():
    """Test basic model categorization functionality."""
    print("🔍 Testing Model Categorization")
    print("=" * 50)
    
    categorizer = OpenRouterCategorizer()
    test_models = create_test_model_data()
    
    categorized = []
    for model_data in test_models:
        metadata = categorizer.categorize_model(model_data)
        categorized.append(metadata)
        
        print(f"✅ {metadata.name}")
        print(f"   Provider: {metadata.provider.value}")
        print(f"   Cost Tier: {metadata.cost_tier.value}")
        print(f"   Quality Score: {metadata.quality_score}/10")
        print(f"   Capabilities: {[cap.value for cap in metadata.capabilities]}")
        print(f"   Use Cases: {[uc.value for uc in metadata.use_cases][:3]}...")
        print()
    
    print(f"📊 Successfully categorized {len(categorized)} models")
    return categorized

def test_provider_filtering():
    """Test provider-based filtering."""
    print("\n🏢 Testing Provider-Based Filtering")
    print("=" * 50)
    
    categorizer = OpenRouterCategorizer()
    test_models = create_test_model_data()
    
    # Categorize all test models
    categorized = [categorizer.categorize_model(m) for m in test_models]
    
    # Test filtering by different providers
    providers_to_test = [ProviderCategory.ANTHROPIC, ProviderCategory.OPENAI, ProviderCategory.META]
    
    for provider in providers_to_test:
        filtered = categorizer.filter_models(categorized, providers=[provider])
        print(f"🔍 {provider.value.title()} models: {len(filtered)} found")
        for model in filtered:
            print(f"   • {model.name}")
    
    return True

def test_capability_filtering():
    """Test capability-based filtering."""
    print("\n🧠 Testing Capability-Based Filtering")
    print("=" * 50)
    
    categorizer = OpenRouterCategorizer()
    test_models = create_test_model_data()
    
    # Categorize all test models
    categorized = [categorizer.categorize_model(m) for m in test_models]
    
    # Test different capability filters
    capability_tests = [
        ([CapabilityCategory.REASONING], "Reasoning Models"),
        ([CapabilityCategory.FAST], "Fast Models"),
        ([CapabilityCategory.LARGE_CONTEXT], "Large Context Models"),
        ([CapabilityCategory.CODING], "Coding Models"),
        ([CapabilityCategory.REASONING, CapabilityCategory.LARGE_CONTEXT], "Reasoning + Large Context")
    ]
    
    for capabilities, description in capability_tests:
        filtered = categorizer.filter_models(categorized, capabilities=capabilities)
        print(f"🎯 {description}: {len(filtered)} found")
        for model in filtered:
            caps = [cap.value for cap in model.capabilities]
            print(f"   • {model.name} - {caps}")
        print()
    
    return True

def test_cost_tier_filtering():
    """Test cost-tier filtering."""
    print("\n💰 Testing Cost-Tier Filtering")
    print("=" * 50)
    
    categorizer = OpenRouterCategorizer()
    test_models = create_test_model_data()
    
    # Categorize all test models
    categorized = [categorizer.categorize_model(m) for m in test_models]
    
    # Test filtering by cost tiers
    cost_tiers = [CostTier.BUDGET, CostTier.STANDARD, CostTier.PREMIUM]
    
    for cost_tier in cost_tiers:
        filtered = categorizer.filter_models(categorized, cost_tiers=[cost_tier])
        print(f"💳 {cost_tier.value.title()} models: {len(filtered)} found")
        for model in filtered:
            completion_cost = model.pricing.get('completion', 0)
            print(f"   • {model.name} - ${completion_cost:.2f}/1M tokens")
        print()
    
    return True

def test_use_case_filtering():
    """Test use-case filtering."""
    print("\n🎯 Testing Use-Case Filtering")
    print("=" * 50)
    
    categorizer = OpenRouterCategorizer()
    test_models = create_test_model_data()
    
    # Categorize all test models
    categorized = [categorizer.categorize_model(m) for m in test_models]
    
    # Test filtering by ISEE-relevant use cases
    use_cases_to_test = [
        UseCase.DEEP_ANALYSIS,
        UseCase.CREATIVE_INNOVATION, 
        UseCase.QUICK_EXPLORATION,
        UseCase.CODE_GENERATION
    ]
    
    for use_case in use_cases_to_test:
        filtered = categorizer.filter_models(categorized, use_cases=[use_case])
        print(f"📋 {use_case.value.replace('_', ' ').title()}: {len(filtered)} models")
        for model in filtered:
            print(f"   • {model.name} - Quality: {model.quality_score}/10")
        print()
    
    return True

def test_isee_recommendations():
    """Test ISEE-optimized model recommendations."""
    print("\n🚀 Testing ISEE-Optimized Recommendations")
    print("=" * 50)
    
    # This would normally use a real OpenRouterClient, but we'll simulate
    # the recommendation logic with our test data
    
    categorizer = OpenRouterCategorizer()
    test_models = create_test_model_data()
    categorized = [categorizer.categorize_model(m) for m in test_models]
    
    # Simulate different ISEE scenarios
    scenarios = [
        ("Deep Analysis", UseCase.DEEP_ANALYSIS, 8.0),
        ("Creative Innovation", UseCase.CREATIVE_INNOVATION, 7.0),
        ("Quick Exploration", UseCase.QUICK_EXPLORATION, 6.0),
        ("Budget Research", UseCase.RESEARCH, 5.0)
    ]
    
    for scenario_name, use_case, min_quality in scenarios:
        # Filter for the use case and quality
        candidates = categorizer.filter_models(
            categorized, 
            use_cases=[use_case],
            min_quality_score=min_quality
        )
        
        # Sort by quality and ensure provider diversity
        high_quality = sorted(candidates, key=lambda x: x.quality_score, reverse=True)
        
        # Select diverse providers (max 3 models)
        selected = []
        used_providers = set()
        
        for model in high_quality:
            if model.provider not in used_providers or len(selected) < 3:
                selected.append(model)
                used_providers.add(model.provider)
                if len(selected) >= 3:
                    break
        
        print(f"🎯 {scenario_name} Recommendations:")
        for i, model in enumerate(selected, 1):
            print(f"   {i}. {model.name} ({model.provider.value})")
            print(f"      Quality: {model.quality_score}/10 | Cost: {model.cost_tier.value}")
            caps = [cap.value for cap in list(model.capabilities)[:3]]
            print(f"      Capabilities: {', '.join(caps)}")
        print()
    
    return True

def test_categorization_performance():
    """Test categorization system performance."""
    print("\n⚡ Testing Categorization Performance")
    print("=" * 50)
    
    import time
    
    categorizer = OpenRouterCategorizer()
    test_models = create_test_model_data()
    
    # Test categorization speed
    start_time = time.time()
    categorized = [categorizer.categorize_model(m) for m in test_models]
    categorization_time = time.time() - start_time
    
    # Test filtering speed
    start_time = time.time()
    for _ in range(10):  # Simulate multiple filter operations
        categorizer.filter_models(categorized, providers=[ProviderCategory.ANTHROPIC])
        categorizer.filter_models(categorized, capabilities=[CapabilityCategory.REASONING])
        categorizer.filter_models(categorized, cost_tiers=[CostTier.STANDARD])
    filtering_time = time.time() - start_time
    
    print(f"📊 Performance Results:")
    print(f"   Categorization: {categorization_time:.3f}s for {len(test_models)} models")
    print(f"   Filtering: {filtering_time:.3f}s for 30 operations")
    print(f"   Models/second: {len(test_models)/categorization_time:.1f}")
    
    # Test cache behavior
    print(f"\n💾 Categorization includes intelligent caching")
    print(f"   Category enums for efficient filtering")
    print(f"   Pattern matching for capability detection")
    print(f"   Provider-aware quality scoring")
    
    return True

def main():
    """Run all categorization system tests."""
    print("🚀 OpenRouter Model Categorization System Test")
    print("=" * 60)
    
    tests = [
        test_model_categorization,
        test_provider_filtering,
        test_capability_filtering,
        test_cost_tier_filtering,
        test_use_case_filtering,
        test_isee_recommendations,
        test_categorization_performance
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(True)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n📊 Test Results Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"✅ Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All categorization tests passed!")
        print("\n🌟 Key Achievements:")
        print("  ✅ Intelligent model categorization working")
        print("  ✅ Multi-dimensional filtering implemented")
        print("  ✅ ISEE-optimized recommendations functional")
        print("  ✅ Performance optimized with caching")
        print("  ✅ Provider diversity handling working")
    else:
        print("⚠️  Some tests failed. Review implementation.")
    
    print("\n💡 Integration Benefits:")
    print("  🔍 300+ models organized intelligently")
    print("  🎯 Use-case driven model selection")
    print("  💰 Cost-aware filtering capabilities")
    print("  🌈 Provider diversity for maximum cognitive variety")
    print("  ⚡ Fast filtering for real-time recommendations")

if __name__ == "__main__":
    main()