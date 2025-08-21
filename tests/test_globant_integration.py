"""
Comprehensive Test Suite for Globant Enterprise AI Integration

This module contains tests for the dual API provider system, focusing on:
- GlobantEnterpriseClient functionality
- ProviderManager logic
- Model mapping and translation
- Cost estimation with dual providers
- Error handling and fallback mechanisms
"""

import os
import json
import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from model_api_integration import (
    GlobantEnterpriseClient, 
    ModelAPIFactory, 
    APIIntegrationError
)
from provider_manager import (
    ProviderManager, 
    ProviderMode, 
    ProviderHealth
)
from cost_estimation import CostEstimator
from api_error_detector import APIErrorDetector


class TestGlobantEnterpriseClient(unittest.TestCase):
    """Test the GlobantEnterpriseClient implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_api_key = "test_globant_api_key"
        self.test_org_id = "test_org_id_123"
        self.test_base_url = "https://test.globant.ai/tokens"
        
    def test_client_initialization(self):
        """Test client initialization with various parameters."""
        # Test with explicit parameters
        client = GlobantEnterpriseClient(
            api_key=self.test_api_key,
            org_id=self.test_org_id,
            base_url=self.test_base_url
        )
        
        self.assertEqual(client.api_key, self.test_api_key)
        self.assertEqual(client.org_id, self.test_org_id)
        self.assertEqual(client.base_url, self.test_base_url)
    
    def test_client_initialization_missing_api_key(self):
        """Test client initialization fails without API key."""
        with self.assertRaises(APIIntegrationError) as context:
            GlobantEnterpriseClient(org_id=self.test_org_id)
        
        self.assertIn("API key not provided", str(context.exception))
    
    def test_client_initialization_missing_org_id(self):
        """Test client initialization fails without organization ID."""
        with self.assertRaises(APIIntegrationError) as context:
            GlobantEnterpriseClient(api_key=self.test_api_key)
        
        self.assertIn("organization ID not provided", str(context.exception))
    
    @patch.dict(os.environ, {
        'GLOBANT_API_KEY': 'env_api_key',
        'GLOBANT_ORG_ID': 'env_org_id',
        'GLOBANT_BASE_URL': 'https://env.globant.ai'
    })
    def test_client_initialization_from_env(self):
        """Test client initialization from environment variables."""
        client = GlobantEnterpriseClient()
        
        self.assertEqual(client.api_key, 'env_api_key')
        self.assertEqual(client.org_id, 'env_org_id')
        self.assertEqual(client.base_url, 'https://env.globant.ai')
    
    @patch('requests.post')
    def test_generate_success(self, mock_post):
        """Test successful API call generation."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response from Globant"}}]
        }
        mock_post.return_value = mock_response
        
        client = GlobantEnterpriseClient(
            api_key=self.test_api_key,
            org_id=self.test_org_id
        )
        
        response = client.generate("Test prompt")
        
        self.assertEqual(response, "Test response from Globant")
        mock_post.assert_called_once()
        
        # Verify request headers
        call_args = mock_post.call_args
        headers = call_args[1]['headers']
        self.assertEqual(headers['Authorization'], f'Bearer {self.test_api_key}')
        self.assertEqual(headers['X-Organization-ID'], self.test_org_id)
    
    @patch('requests.post')
    def test_generate_api_error(self, mock_post):
        """Test API error handling."""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {
                "message": "Invalid organization credentials",
                "code": "ORG_INVALID"
            }
        }
        mock_post.return_value = mock_response
        
        client = GlobantEnterpriseClient(
            api_key=self.test_api_key,
            org_id=self.test_org_id
        )
        
        with self.assertRaises(APIIntegrationError) as context:
            client.generate("Test prompt")
        
        self.assertIn("Globant Enterprise AI error", str(context.exception))
        self.assertIn("Invalid organization credentials", str(context.exception))
    
    def test_get_fallback_models(self):
        """Test fallback model retrieval."""
        client = GlobantEnterpriseClient(
            api_key=self.test_api_key,
            org_id=self.test_org_id
        )
        
        models = client._get_fallback_models()
        
        # Verify expected models are present
        model_ids = [model['id'] for model in models]
        self.assertIn('claude-sonnet-4-20250514', model_ids)
        self.assertIn('claude-3-5-haiku-20241022', model_ids)
        self.assertIn('gpt-4o-mini', model_ids)


class TestProviderManager(unittest.TestCase):
    """Test the ProviderManager implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = ProviderManager(default_mode="openrouter", fallback_enabled=True)
    
    def test_provider_mode_enum(self):
        """Test ProviderMode enum values."""
        self.assertEqual(ProviderMode.OPENROUTER.value, "openrouter")
        self.assertEqual(ProviderMode.GLOBANT.value, "globant")
        self.assertEqual(ProviderMode.HYBRID.value, "hybrid")
    
    def test_provider_health_initialization(self):
        """Test ProviderHealth initialization."""
        health = ProviderHealth("test_provider")
        
        self.assertEqual(health.provider_name, "test_provider")
        self.assertEqual(health.consecutive_failures, 0)
        self.assertEqual(health.total_requests, 0)
        self.assertTrue(health.is_healthy)
    
    def test_provider_health_record_success(self):
        """Test recording successful API calls."""
        health = ProviderHealth("test_provider")
        
        health.record_success(1.5)  # 1.5 second response time
        
        self.assertEqual(health.consecutive_failures, 0)
        self.assertEqual(health.successful_requests, 1)
        self.assertEqual(health.total_requests, 1)
        self.assertEqual(health.average_response_time, 1.5)
        self.assertTrue(health.is_healthy)
    
    def test_provider_health_record_failure(self):
        """Test recording failed API calls."""
        health = ProviderHealth("test_provider")
        
        # Record multiple failures
        for i in range(3):
            health.record_failure()
        
        self.assertEqual(health.consecutive_failures, 3)
        self.assertEqual(health.total_requests, 3)
        self.assertEqual(health.successful_requests, 0)
        self.assertFalse(health.is_healthy)  # Should be unhealthy after 3 failures
    
    def test_model_translation(self):
        """Test model ID translation between providers."""
        # Test OpenRouter to Globant translation
        openrouter_model = "anthropic/claude-sonnet-4"
        globant_model = self.manager.translate_model_id(
            openrouter_model, "openrouter", "globant"
        )
        
        self.assertEqual(globant_model, "claude-sonnet-4-20250514")
        
        # Test Globant to OpenRouter translation
        reverse_model = self.manager.translate_model_id(
            globant_model, "globant", "openrouter"
        )
        
        self.assertEqual(reverse_model, "anthropic/claude-sonnet-4")
    
    @patch('model_api_integration.ModelAPIFactory.create_client')
    def test_get_client_success(self, mock_create_client):
        """Test successful client retrieval."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        client, provider = self.manager.get_client("openrouter")
        
        self.assertEqual(client, mock_client)
        self.assertEqual(provider, "openrouter")
        mock_create_client.assert_called_once_with("openrouter")
    
    @patch('model_api_integration.ModelAPIFactory.create_client')
    def test_get_client_fallback(self, mock_create_client):
        """Test client fallback mechanism."""
        # First call fails, second succeeds
        mock_globant_client = Mock()
        mock_create_client.side_effect = [
            APIIntegrationError("OpenRouter failed"),
            mock_globant_client
        ]
        
        client, provider = self.manager.get_client("openrouter")
        
        self.assertEqual(client, mock_globant_client)
        self.assertEqual(provider, "globant")
        self.assertEqual(mock_create_client.call_count, 2)
    
    def test_set_provider_mode(self):
        """Test changing provider mode at runtime."""
        self.manager.set_provider_mode("globant")
        self.assertEqual(self.manager.default_mode, ProviderMode.GLOBANT)
        
        with self.assertRaises(ValueError):
            self.manager.set_provider_mode("invalid_mode")
    
    def test_get_provider_status(self):
        """Test getting provider health status."""
        status = self.manager.get_provider_status()
        
        self.assertIn("openrouter", status)
        self.assertIn("globant", status)
        self.assertIn("healthy", status["openrouter"])
        self.assertIn("success_rate", status["openrouter"])
    
    def test_reset_provider_health(self):
        """Test resetting provider health metrics."""
        # Artificially damage health
        self.manager.provider_health["openrouter"].record_failure()
        self.manager.provider_health["openrouter"].record_failure()
        
        # Reset health
        self.manager.reset_provider_health("openrouter")
        
        health = self.manager.provider_health["openrouter"]
        self.assertEqual(health.consecutive_failures, 0)
        self.assertEqual(health.total_requests, 0)
        self.assertTrue(health.is_healthy)


class TestCostEstimationDualProvider(unittest.TestCase):
    """Test cost estimation with dual provider support."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.estimator = CostEstimator()
    
    def test_provider_model_cost_key_generation(self):
        """Test generation of provider-specific cost keys."""
        # Test Globant provider
        key = self.estimator.get_provider_model_cost_key(
            "claude-sonnet-4-20250514", "globant"
        )
        self.assertEqual(key, "globant:claude-sonnet-4-20250514")
        
        # Test OpenRouter provider
        key = self.estimator.get_provider_model_cost_key(
            "anthropic/claude-sonnet-4", "openrouter"
        )
        self.assertEqual(key, "openrouter:anthropic/claude-sonnet-4")
        
        # Test direct provider (should return unchanged)
        key = self.estimator.get_provider_model_cost_key(
            "claude-sonnet-4-20250514", "anthropic"
        )
        self.assertEqual(key, "claude-sonnet-4-20250514")
    
    def test_cost_comparison_across_providers(self):
        """Test cost comparison between providers for the same model."""
        costs = self.estimator.get_cost_comparison("claude-sonnet-4-20250514")
        
        # Should include both providers if both are configured
        if "globant:claude-sonnet-4-20250514" in self.estimator.MODEL_COSTS:
            self.assertIn("globant", costs)
        
        if "openrouter:anthropic/claude-sonnet-4" in self.estimator.MODEL_COSTS:
            self.assertIn("openrouter", costs)
    
    def test_provider_specific_cost_retrieval(self):
        """Test retrieving provider-specific costs."""
        # Mock model info for Globant
        globant_model_info = {
            "provider": "globant",
            "parameters": {"model": "claude-sonnet-4-20250514"}
        }
        
        cost = self.estimator._get_model_cost_rate(globant_model_info)
        
        # Should either find Globant-specific pricing or apply enterprise markup
        self.assertIn("input", cost)
        self.assertIn("output", cost)
        self.assertGreater(cost["input"], 0)
        self.assertGreater(cost["output"], 0)


class TestAPIErrorDetectorGlobant(unittest.TestCase):
    """Test API error detection with Globant-specific patterns."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = APIErrorDetector()
    
    def test_globant_error_pattern_detection(self):
        """Test detection of Globant-specific error patterns."""
        error_messages = [
            "Globant Enterprise AI error: Invalid credentials",
            "Organization ID not found in system",
            "Enterprise API access denied for user",
            "Organization quota exceeded for month"
        ]
        
        for error_msg in error_messages:
            is_error, reason = self.detector.is_api_error(error_msg)
            self.assertTrue(is_error, f"Failed to detect error in: {error_msg}")
            self.assertIsInstance(reason, str)
    
    def test_globant_specific_error_indicators(self):
        """Test Globant-specific error indicators."""
        error_text = "Your organization does not have access to this enterprise model"
        
        is_error, reason = self.detector.is_api_error(error_text)
        
        self.assertTrue(is_error)
        self.assertIn("organization", reason.lower() or error_text.lower())
    
    def test_legitimate_globant_response(self):
        """Test that legitimate responses are not flagged as errors."""
        legitimate_response = """
        Based on the enterprise analysis requirements, here are the key recommendations:
        1. Implement comprehensive security protocols
        2. Establish clear organizational governance
        3. Deploy enterprise-grade monitoring solutions
        
        This approach ensures scalable implementation while maintaining compliance standards.
        """
        
        is_error, reason = self.detector.is_api_error(legitimate_response)
        
        self.assertFalse(is_error, f"Legitimate response flagged as error: {reason}")


class TestModelAPIFactoryExtension(unittest.TestCase):
    """Test ModelAPIFactory extension for Globant support."""
    
    def test_factory_supports_globant_provider(self):
        """Test that the factory can create Globant clients."""
        with patch('model_api_integration.GlobantEnterpriseClient') as mock_client:
            ModelAPIFactory.create_client("globant")
            mock_client.assert_called_once()
    
    def test_factory_unsupported_provider(self):
        """Test factory behavior with unsupported provider."""
        with self.assertRaises(ValueError) as context:
            ModelAPIFactory.create_client("unsupported_provider")
        
        self.assertIn("Unsupported provider", str(context.exception))


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios and edge cases."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.provider_manager = ProviderManager(
            default_mode="hybrid", 
            fallback_enabled=True
        )
    
    @patch('model_api_integration.ModelAPIFactory.create_client')
    def test_hybrid_mode_provider_selection(self, mock_create_client):
        """Test intelligent provider selection in hybrid mode."""
        # Mock both clients
        mock_openrouter_client = Mock()
        mock_globant_client = Mock()
        
        def create_client_side_effect(provider):
            if provider == "openrouter":
                return mock_openrouter_client
            elif provider == "globant":
                return mock_globant_client
            
        mock_create_client.side_effect = create_client_side_effect
        
        # Simulate OpenRouter being healthier
        self.provider_manager.provider_health["openrouter"].record_success(1.0)
        self.provider_manager.provider_health["globant"].record_success(2.0)
        
        client, provider = self.provider_manager.get_client()
        
        # Should select OpenRouter due to better performance
        self.assertEqual(provider, "openrouter")
        self.assertEqual(client, mock_openrouter_client)
    
    def test_model_mapping_roundtrip(self):
        """Test that model mapping works correctly in both directions."""
        original_model = "anthropic/claude-3.5-haiku"
        
        # OpenRouter -> Globant
        globant_model = self.provider_manager.translate_model_id(
            original_model, "openrouter", "globant"
        )
        
        # Globant -> OpenRouter
        back_to_openrouter = self.provider_manager.translate_model_id(
            globant_model, "globant", "openrouter"
        )
        
        self.assertEqual(original_model, back_to_openrouter)
    
    @patch.dict(os.environ, {
        'ISEE_PROVIDER_MODE': 'globant',
        'ISEE_FALLBACK_ENABLED': 'false'
    })
    def test_environment_configuration(self):
        """Test configuration loading from environment variables."""
        manager = ProviderManager()
        
        self.assertEqual(manager.default_mode, ProviderMode.GLOBANT)
        self.assertFalse(manager.fallback_enabled)


if __name__ == "__main__":
    # Set up test environment
    os.environ['GLOBANT_API_KEY'] = 'test_key'
    os.environ['GLOBANT_ORG_ID'] = 'test_org'
    
    # Run tests
    unittest.main(verbosity=2)