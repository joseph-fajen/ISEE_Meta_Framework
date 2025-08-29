#!/usr/bin/env python3
"""
Globant Enterprise AI Client Class
==================================

A production-ready, reusable client class for Globant Enterprise AI API.
Based on the proven GlobantEnterpriseClient from ISEE Meta Framework.

Features:
- Environment variable support
- Comprehensive error handling
- Model caching and validation
- Async support capability
- Logging integration
- Rate limiting awareness

Usage:
    from globant_client_class import GlobantClient
    
    client = GlobantClient()  # Uses environment variables
    response = client.generate("Your prompt here", model="anthropic/claude-3-5-haiku-20241022")
"""

import os
import json
import time
import logging
import requests
from typing import Dict, Any, Optional, List
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GlobantAPIError(Exception):
    """Base exception for Globant API errors."""
    pass


class GlobantRateLimitError(GlobantAPIError):
    """Exception for rate limit exceeded."""
    pass


class GlobantAuthError(GlobantAPIError):
    """Exception for authentication/authorization errors."""
    pass


class GlobantClient:
    """
    Production-ready client for Globant Enterprise AI API.
    
    This client handles authentication, request formatting, error handling,
    and response parsing for Globant's Enterprise AI platform.
    """
    
    def __init__(self, api_key: Optional[str] = None, org_id: Optional[str] = None, 
                 base_url: Optional[str] = None, timeout: int = 120):
        """
        Initialize the Globant client.
        
        Args:
            api_key: Globant API key (defaults to GLOBANT_API_KEY env var)
            org_id: Organization ID (defaults to GLOBANT_ORG_ID env var)  
            base_url: Base API URL (defaults to GLOBANT_BASE_URL env var)
            timeout: Request timeout in seconds
            
        Raises:
            GlobantAPIError: If required credentials are missing
        """
        # Load credentials from environment if not provided
        self.api_key = api_key or os.getenv("GLOBANT_API_KEY")
        self.org_id = org_id or os.getenv("GLOBANT_ORG_ID")
        self.base_url = base_url or os.getenv("GLOBANT_BASE_URL", "https://api.saia.ai")
        self.timeout = timeout
        
        # Validate required credentials
        if not self.api_key:
            raise GlobantAPIError(
                "Globant API key not provided. Set GLOBANT_API_KEY environment variable "
                "or pass api_key parameter."
            )
        if not self.org_id:
            raise GlobantAPIError(
                "Globant organization ID not provided. Set GLOBANT_ORG_ID environment variable "
                "or pass org_id parameter."
            )
        
        # API endpoints (confirmed working from ISEE implementation)
        self.chat_url = f"{self.base_url}/chat/completions"
        self.models_url = f"{self.base_url}/v1/models"
        
        # Model caching
        self._models_cache = None
        self._models_cache_time = 0
        self._cache_duration = 300  # 5 minutes
        
        # Rate limiting tracking
        self._last_request_time = 0
        self._min_request_interval = 0.1  # 100ms between requests
        
        logger.info(f"GlobantClient initialized with base_url: {self.base_url}")
    
    def generate(self, prompt: str, model: str, **kwargs) -> str:
        """
        Generate a response using a Globant-hosted model.
        
        Args:
            prompt: Input prompt text
            model: Model identifier in provider/model format 
                   (e.g., "anthropic/claude-3-5-haiku-20241022")
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Generated response text
            
        Raises:
            GlobantAPIError: If the API call fails
            GlobantRateLimitError: If rate limited
            GlobantAuthError: If authentication fails
            
        Examples:
            >>> client = GlobantClient()
            >>> # Standard model
            >>> response = client.generate("Hello!", "anthropic/claude-3-5-haiku-20241022")
            >>> print(response)
            
            >>> # Reasoning model with effort control
            >>> response = client.generate(
            ...     "Solve this logic puzzle step by step...",
            ...     "openai/o1",
            ...     reasoning_effort="high",
            ...     max_completion_tokens=500
            ... )
            >>> print(response)
        """
        # Validate model format
        if "/" not in model:
            raise GlobantAPIError(
                f"Invalid model format: '{model}'. "
                "Models must be in 'provider/model' format (e.g., 'anthropic/claude-3-5-haiku-20241022')"
            )
        
        # Rate limiting
        self._enforce_rate_limit()
        
        # Prepare request headers (CRITICAL: both Authorization and X-Organization-ID required)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Organization-ID": self.org_id
        }
        
        # Prepare request payload (OpenAI-compatible format)
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", 1024),
            "temperature": kwargs.get("temperature", 0.7)
        }
        
        # Add optional parameters
        optional_params = ["top_p", "presence_penalty", "frequency_penalty", "stop", "stream", "n"]
        for param in optional_params:
            if param in kwargs:
                payload[param] = kwargs[param]
        
        # Special handling for reasoning models (o1, o3, o4 series)
        is_reasoning_model = any(series in model.lower() for series in ["o1", "o3", "o4"])
        
        if is_reasoning_model:
            # Reasoning models use different parameters
            payload.pop("temperature", None)  # Reasoning models don't support temperature
            
            # Set reasoning_effort parameter (new discovery from Globant docs)
            if "reasoning_effort" in kwargs:
                payload["reasoning_effort"] = kwargs["reasoning_effort"]
            else:
                payload["reasoning_effort"] = "medium"  # Default to medium effort
            
            # Use max_completion_tokens for reasoning models
            if "max_completion_tokens" in kwargs:
                payload["max_completion_tokens"] = kwargs["max_completion_tokens"]
                payload.pop("max_tokens", None)
            else:
                # Convert max_tokens to max_completion_tokens
                payload["max_completion_tokens"] = payload.pop("max_tokens", 1024)
        
        try:
            logger.debug(f"Making API call to {self.chat_url} with model {model}")
            
            # Make the API request
            response = requests.post(
                self.chat_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            # Update rate limiting tracking
            self._last_request_time = time.time()
            
            # Handle HTTP errors
            if response.status_code == 401:
                raise GlobantAuthError("Invalid API key or authentication failed")
            elif response.status_code == 403:
                raise GlobantAuthError("Access denied. Check organization permissions.")
            elif response.status_code == 429:
                raise GlobantRateLimitError("Rate limit exceeded. Please retry later.")
            elif response.status_code != 200:
                self._handle_error_response(response)
            
            # Parse response
            response_data = response.json()
            
            # Check for API-level errors
            if "error" in response_data:
                error_info = response_data["error"]
                error_message = error_info.get("message", "Unknown error")
                error_code = error_info.get("code", "Unknown")
                
                # Specific error handling
                if "organization" in error_message.lower():
                    raise GlobantAuthError(f"Organization error: {error_message}")
                elif "model" in error_message.lower() and "invalid" in error_message.lower():
                    raise GlobantAPIError(f"Model error: {error_message}")
                else:
                    raise GlobantAPIError(f"Globant API error {error_code}: {error_message}")
            
            # Extract and return the response
            return response_data["choices"][0]["message"]["content"]
            
        except requests.RequestException as e:
            logger.error(f"Network error during API call: {str(e)}")
            raise GlobantAPIError(f"Network error: {str(e)}")
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse API response: {str(e)}")
            raise GlobantAPIError(f"Response parsing error: {str(e)}")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models from Globant API.
        
        Returns:
            List of model dictionaries with metadata
            
        Note:
            Results are cached for 5 minutes to reduce API calls
        """
        current_time = time.time()
        
        # Return cached models if cache is valid
        if (self._models_cache is not None and 
            current_time - self._models_cache_time < self._cache_duration):
            return self._models_cache
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "X-Organization-ID": self.org_id
            }
            
            response = requests.get(self.models_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                
                # Cache results
                self._models_cache = models
                self._models_cache_time = current_time
                
                logger.info(f"Retrieved {len(models)} models from API")
                return models
            else:
                logger.warning(f"Failed to fetch models: HTTP {response.status_code}")
                return self._get_fallback_models()
                
        except requests.RequestException as e:
            logger.warning(f"Network error fetching models: {e}")
            return self._get_fallback_models()
    
    def list_model_names(self) -> List[str]:
        """
        Get a simple list of available model names.
        
        Returns:
            List of model identifier strings
        """
        try:
            models = self.get_available_models()
            return [model.get("id", "") for model in models if model.get("id")]
        except Exception as e:
            logger.warning(f"Failed to fetch model names: {e}")
            return [
                "anthropic/claude-sonnet-4-20250514",
                "anthropic/claude-3-5-haiku-20241022", 
                "openai/gpt-4o-mini",
                "azure/gpt-4.1",
                "vertex_ai/gemini-2.5-pro"
            ]
    
    def validate_model(self, model: str) -> bool:
        """
        Validate if a model is available and properly formatted.
        
        Args:
            model: Model identifier to validate
            
        Returns:
            True if model is valid and available
        """
        if "/" not in model:
            return False
        
        available_models = self.list_model_names()
        return model in available_models
    
    def _enforce_rate_limit(self):
        """Enforce minimum interval between requests."""
        if self._last_request_time > 0:
            elapsed = time.time() - self._last_request_time
            if elapsed < self._min_request_interval:
                sleep_time = self._min_request_interval - elapsed
                time.sleep(sleep_time)
    
    def _handle_error_response(self, response: requests.Response):
        """Handle non-200 HTTP responses."""
        try:
            error_data = response.json()
            if "error" in error_data:
                error_message = error_data["error"].get("message", "Unknown error")
            else:
                error_message = f"HTTP {response.status_code}"
        except:
            error_message = f"HTTP {response.status_code}"
        
        raise GlobantAPIError(f"API request failed: {error_message}")
    
    def _get_fallback_models(self) -> List[Dict[str, Any]]:
        """Provide fallback model list based on ISEE's working configuration."""
        return [
            {
                "id": "anthropic/claude-sonnet-4-20250514",
                "name": "Claude Sonnet 4",
                "provider": "anthropic",
                "capabilities": ["frontier_reasoning", "highest_quality"],
                "cost_tier": "premium_plus"
            },
            {
                "id": "openai/gpt-4o-mini", 
                "name": "GPT-4o Mini",
                "provider": "openai",
                "capabilities": ["fast", "cost_efficient"],
                "cost_tier": "standard"
            },
            {
                "id": "anthropic/claude-3-5-haiku-20241022",
                "name": "Claude 3.5 Haiku",
                "provider": "anthropic", 
                "capabilities": ["fastest", "cost_efficient"],
                "cost_tier": "standard"
            },
            {
                "id": "vertex_ai/gemini-2.5-pro",
                "name": "Gemini 2.5 Pro",
                "provider": "google",
                "capabilities": ["multimodal", "verification"],
                "cost_tier": "premium"
            },
            {
                "id": "azure/gpt-4.1",
                "name": "GPT-4 Turbo (Azure)",
                "provider": "microsoft",
                "capabilities": ["reliable", "reasoning"],
                "cost_tier": "premium"
            }
        ]


def main():
    """Example usage of the GlobantClient class."""
    print("Globant Enterprise AI Client - Class Example")
    print("=" * 45)
    
    try:
        # Initialize client (uses environment variables)
        client = GlobantClient()
        print("✅ Client initialized successfully")
        
        # List available models
        print("\n📋 Available Models:")
        models = client.list_model_names()
        for i, model in enumerate(models[:5], 1):  # Show first 5
            print(f"   {i}. {model}")
        if len(models) > 5:
            print(f"   ... and {len(models) - 5} more")
        
        # Test model validation
        test_model = "anthropic/claude-3-5-haiku-20241022"
        is_valid = client.validate_model(test_model)
        print(f"\n🔍 Model validation for '{test_model}': {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        # Generate response with standard model
        print(f"\n💭 Generating response with {test_model}...")
        response = client.generate(
            prompt="Explain what Globant Enterprise AI is in one sentence.",
            model=test_model,
            max_tokens=100,
            temperature=0.7
        )
        print(f"✅ Response: {response}")
        
        # Test reasoning model if available
        reasoning_model = "openai/o1"
        print(f"\n🧠 Testing reasoning model: {reasoning_model}")
        try:
            response = client.generate(
                prompt="If I have 8 apples and give away 3, then buy 5 more, how many do I have? Show your reasoning.",
                model=reasoning_model,
                reasoning_effort="medium",  # Use new reasoning_effort parameter
                max_completion_tokens=150
            )
            print(f"✅ Reasoning response: {response}")
        except Exception as e:
            print(f"⚠️  Reasoning model test failed (may not be available): {e}")
        
    except GlobantAuthError as e:
        print(f"❌ Authentication Error: {e}")
        print("   Check your GLOBANT_API_KEY and GLOBANT_ORG_ID")
    except GlobantAPIError as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")


if __name__ == "__main__":
    main()