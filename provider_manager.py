"""
Provider Manager for ISEE Framework

This module manages switching between different API providers (OpenRouter, Globant Enterprise AI)
and provides fallback mechanisms for improved reliability.
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from enum import Enum
from pathlib import Path

from model_api_integration import ModelAPIFactory, ModelAPIClient, APIIntegrationError


class ProviderMode(Enum):
    """Enumeration of supported provider modes."""
    OPENROUTER = "openrouter"
    GLOBANT = "globant"
    HYBRID = "hybrid"  # Intelligent switching between providers


class ProviderHealth:
    """Track provider health and performance metrics."""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.last_success_time = 0
        self.last_failure_time = 0
        self.consecutive_failures = 0
        self.total_requests = 0
        self.successful_requests = 0
        self.average_response_time = 0
        self.is_healthy = True
    
    def record_success(self, response_time: float):
        """Record a successful API call."""
        self.last_success_time = time.time()
        self.consecutive_failures = 0
        self.total_requests += 1
        self.successful_requests += 1
        
        # Update rolling average response time
        if self.average_response_time == 0:
            self.average_response_time = response_time
        else:
            # Simple weighted average (70% old, 30% new)
            self.average_response_time = (0.7 * self.average_response_time + 0.3 * response_time)
        
        self.is_healthy = True
    
    def record_failure(self):
        """Record a failed API call."""
        self.last_failure_time = time.time()
        self.consecutive_failures += 1
        self.total_requests += 1
        
        # Mark as unhealthy after 3 consecutive failures
        if self.consecutive_failures >= 3:
            self.is_healthy = False
    
    def get_success_rate(self) -> float:
        """Get the success rate as a percentage."""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100
    
    def should_retry(self) -> bool:
        """Determine if this provider should be retried."""
        # Don't retry if marked unhealthy
        if not self.is_healthy:
            return False
        
        # Allow retry if last failure was more than 5 minutes ago
        if time.time() - self.last_failure_time > 300:
            return True
            
        return self.consecutive_failures < 2


class ProviderManager:
    """Manages API provider selection, switching, and fallback mechanisms."""
    
    def __init__(self, default_mode: str = "openrouter", fallback_enabled: bool = True):
        """Initialize the ProviderManager.
        
        Args:
            default_mode: Default provider mode (openrouter|globant|hybrid)
            fallback_enabled: Whether to enable automatic fallback between providers
        """
        self.logger = logging.getLogger(f"{__name__}.ProviderManager")
        
        # Load configuration from environment
        self.default_mode = ProviderMode(os.environ.get("ISEE_PROVIDER_MODE", default_mode))
        self.fallback_enabled = os.environ.get("ISEE_FALLBACK_ENABLED", str(fallback_enabled)).lower() == "true"
        
        # Provider health tracking
        self.provider_health = {
            "openrouter": ProviderHealth("openrouter"),
            "globant": ProviderHealth("globant")
        }
        
        # Model mappings between providers
        self.model_mappings = self._load_model_mappings()
        
        # Cache for API clients
        self._client_cache = {}
        
        self.logger.info(f"ProviderManager initialized with mode: {self.default_mode.value}, fallback: {self.fallback_enabled}")
    
    def _load_model_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load model mappings between OpenRouter and Globant providers."""
        return {
            # OpenRouter model ID -> Globant model ID
            "openrouter_to_globant": {
                "anthropic/claude-sonnet-4": "claude-sonnet-4-20250514",
                "anthropic/claude-3.5-haiku": "claude-3-5-haiku-20241022", 
                "openai/gpt-4o-mini": "gpt-4o-mini",
                "openai/gpt-4-turbo": "gpt-4-turbo",
                "google/gemini-2.5-pro": "gemini-2.5-pro",
                "anthropic/claude-3-sonnet": "claude-3-sonnet-20240229",
                "openai/gpt-4": "gpt-4",
                "openai/gpt-3.5-turbo": "gpt-3.5-turbo"
            },
            # Globant model ID -> OpenRouter model ID  
            "globant_to_openrouter": {
                "claude-sonnet-4-20250514": "anthropic/claude-sonnet-4",
                "claude-3-5-haiku-20241022": "anthropic/claude-3.5-haiku",
                "gpt-4o-mini": "openai/gpt-4o-mini", 
                "gpt-4-turbo": "openai/gpt-4-turbo",
                "gemini-2.5-pro": "google/gemini-2.5-pro",
                "claude-3-sonnet-20240229": "anthropic/claude-3-sonnet",
                "gpt-4": "openai/gpt-4",
                "gpt-3.5-turbo": "openai/gpt-3.5-turbo"
            }
        }
    
    def get_client(self, provider: Optional[str] = None, force_provider: bool = False) -> Tuple[ModelAPIClient, str]:
        """Get an API client for the specified or optimal provider.
        
        Args:
            provider: Specific provider to use (None = use intelligent selection)
            force_provider: If True, don't fallback even if provider fails
            
        Returns:
            Tuple of (API client instance, actual provider used)
        """
        # Determine which provider to use
        if provider:
            target_provider = provider
        elif self.default_mode == ProviderMode.HYBRID:
            target_provider = self._select_optimal_provider()
        else:
            target_provider = self.default_mode.value
        
        # Try to get client for target provider
        try:
            if target_provider not in self._client_cache:
                self._client_cache[target_provider] = ModelAPIFactory.create_client(target_provider)
            
            client = self._client_cache[target_provider]
            self.logger.debug(f"Using provider: {target_provider}")
            return client, target_provider
            
        except Exception as e:
            self.logger.warning(f"Failed to create client for {target_provider}: {str(e)}")
            
            # Try fallback if enabled and not forced
            if self.fallback_enabled and not force_provider:
                fallback_provider = self._get_fallback_provider(target_provider)
                if fallback_provider and fallback_provider != target_provider:
                    try:
                        if fallback_provider not in self._client_cache:
                            self._client_cache[fallback_provider] = ModelAPIFactory.create_client(fallback_provider)
                        
                        client = self._client_cache[fallback_provider]
                        self.logger.info(f"Falling back to provider: {fallback_provider}")
                        return client, fallback_provider
                        
                    except Exception as fallback_error:
                        self.logger.error(f"Fallback to {fallback_provider} also failed: {str(fallback_error)}")
            
            # Re-raise the original exception if no fallback worked
            raise APIIntegrationError(f"Could not create client for any provider. Last error: {str(e)}")
    
    def _select_optimal_provider(self) -> str:
        """Select the optimal provider based on health metrics."""
        openrouter_health = self.provider_health["openrouter"]
        globant_health = self.provider_health["globant"]
        
        # If one provider is unhealthy, use the other
        if not openrouter_health.is_healthy and globant_health.is_healthy:
            return "globant"
        elif not globant_health.is_healthy and openrouter_health.is_healthy:
            return "openrouter"
        
        # If both healthy, choose based on performance
        if openrouter_health.get_success_rate() > globant_health.get_success_rate():
            return "openrouter"
        elif globant_health.get_success_rate() > openrouter_health.get_success_rate():
            return "globant"
        
        # If similar success rates, choose based on response time
        if openrouter_health.average_response_time < globant_health.average_response_time:
            return "openrouter"
        else:
            return "globant"
    
    def _get_fallback_provider(self, failed_provider: str) -> Optional[str]:
        """Get the fallback provider when the primary fails."""
        fallback_map = {
            "openrouter": "globant",
            "globant": "openrouter"
        }
        
        fallback = fallback_map.get(failed_provider)
        
        # Only return fallback if it's healthy
        if fallback and self.provider_health[fallback].should_retry():
            return fallback
            
        return None
    
    def translate_model_id(self, model_id: str, from_provider: str, to_provider: str) -> str:
        """Translate a model ID from one provider to another.
        
        Args:
            model_id: The model ID to translate
            from_provider: Source provider name
            to_provider: Target provider name
            
        Returns:
            Translated model ID for the target provider
        """
        mapping_key = f"{from_provider}_to_{to_provider}"
        
        if mapping_key in self.model_mappings:
            return self.model_mappings[mapping_key].get(model_id, model_id)
        
        # If no mapping exists, return original ID
        return model_id
    
    def make_api_call_with_fallback(self, 
                                  prompt: str, 
                                  parameters: Dict[str, Any],
                                  preferred_provider: Optional[str] = None) -> Tuple[str, str, float]:
        """Make an API call with intelligent provider selection and fallback.
        
        Args:
            prompt: The prompt to send to the API
            parameters: API call parameters including model ID
            preferred_provider: Preferred provider to try first
            
        Returns:
            Tuple of (response text, provider used, response time)
        """
        start_time = time.time()
        
        try:
            # Get the optimal client
            client, provider = self.get_client(preferred_provider)
            
            # Translate model ID if needed
            original_model = parameters.get("model", "")
            if preferred_provider and provider != preferred_provider:
                # We fell back to a different provider, translate the model ID
                translated_model = self.translate_model_id(original_model, preferred_provider, provider)
                parameters = dict(parameters)  # Make a copy
                parameters["model"] = translated_model
                self.logger.debug(f"Translated model {original_model} -> {translated_model} for provider {provider}")
            
            # Make the API call
            response = client.generate(prompt, parameters)
            response_time = time.time() - start_time
            
            # Record success
            self.provider_health[provider].record_success(response_time)
            
            return response, provider, response_time
            
        except Exception as e:
            response_time = time.time() - start_time
            
            # Record failure for the attempted provider
            attempted_provider = preferred_provider or self.default_mode.value
            if attempted_provider in self.provider_health:
                self.provider_health[attempted_provider].record_failure()
            
            # Re-raise the exception
            raise APIIntegrationError(f"API call failed after {response_time:.2f}s: {str(e)}")
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get the current status of all providers.
        
        Returns:
            Dictionary containing health metrics for each provider
        """
        status = {}
        
        for provider_name, health in self.provider_health.items():
            status[provider_name] = {
                "healthy": health.is_healthy,
                "success_rate": health.get_success_rate(),
                "total_requests": health.total_requests,
                "consecutive_failures": health.consecutive_failures,
                "average_response_time": health.average_response_time,
                "last_success_time": health.last_success_time,
                "last_failure_time": health.last_failure_time
            }
        
        return status
    
    def reset_provider_health(self, provider: Optional[str] = None):
        """Reset health metrics for a specific provider or all providers.
        
        Args:
            provider: Provider name to reset, or None to reset all
        """
        if provider:
            if provider in self.provider_health:
                self.provider_health[provider] = ProviderHealth(provider)
                self.logger.info(f"Reset health metrics for provider: {provider}")
        else:
            for provider_name in self.provider_health:
                self.provider_health[provider_name] = ProviderHealth(provider_name)
            self.logger.info("Reset health metrics for all providers")
    
    def set_provider_mode(self, mode: str):
        """Change the provider mode at runtime.
        
        Args:
            mode: New provider mode (openrouter|globant|hybrid)
        """
        try:
            self.default_mode = ProviderMode(mode)
            self.logger.info(f"Provider mode changed to: {mode}")
        except ValueError:
            raise ValueError(f"Invalid provider mode: {mode}. Must be one of: openrouter, globant, hybrid")
    
    def get_available_models(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available models from the specified provider.
        
        Args:
            provider: Provider name, or None to use default
            
        Returns:
            List of available model dictionaries
        """
        try:
            client, actual_provider = self.get_client(provider)
            
            if hasattr(client, 'get_available_models'):
                return client.get_available_models()
            else:
                # Fallback for clients without this method
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to get available models from {provider}: {str(e)}")
            return []