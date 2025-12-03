"""
Provider Manager for ISEE Framework

This module manages the Globant Enterprise AI provider for the ISEE framework.
Simplified from dual-provider architecture to single-provider (Globant).
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional, Tuple

from model_api_integration import ModelAPIFactory, ModelAPIClient, APIIntegrationError


class ProviderHealth:
    """Track provider health and performance metrics."""

    def __init__(self, provider_name: str = "globant"):
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

    def reset(self):
        """Reset health metrics."""
        self.__init__(self.provider_name)


class ProviderManager:
    """Manages the Globant Enterprise AI provider for ISEE.

    This is a simplified manager that uses Globant as the sole provider.
    The dual-provider architecture with OpenRouter has been removed for simplicity.
    """

    def __init__(self, default_mode: str = "globant", fallback_enabled: bool = False):
        """Initialize the ProviderManager.

        Args:
            default_mode: Provider mode (always "globant" in simplified version)
            fallback_enabled: Ignored in simplified version (no fallback provider)
        """
        self.logger = logging.getLogger(f"{__name__}.ProviderManager")

        # Single provider: Globant Enterprise AI
        self.provider = "globant"
        self.provider_health = ProviderHealth("globant")

        # Cache for API client
        self._client = None

        self.logger.info(f"ProviderManager initialized with Globant Enterprise AI as primary provider")

    def get_client(self, provider: Optional[str] = None, force_provider: bool = False) -> Tuple[ModelAPIClient, str]:
        """Get the Globant API client.

        Args:
            provider: Ignored (always uses Globant)
            force_provider: Ignored (no fallback)

        Returns:
            Tuple of (API client instance, "globant")
        """
        try:
            if self._client is None:
                self._client = ModelAPIFactory.create_client("globant")

            return self._client, "globant"

        except Exception as e:
            self.logger.error(f"Failed to create Globant client: {str(e)}")
            raise APIIntegrationError(f"Could not create Globant client: {str(e)}")

    def make_api_call_with_fallback(self,
                                    prompt: str,
                                    parameters: Dict[str, Any],
                                    preferred_provider: Optional[str] = None) -> Tuple[str, str, float]:
        """Make an API call to Globant Enterprise AI.

        Args:
            prompt: The prompt to send to the API
            parameters: API call parameters including model ID
            preferred_provider: Ignored (always uses Globant)

        Returns:
            Tuple of (response text, "globant", response time)
        """
        start_time = time.time()

        try:
            client, provider = self.get_client()

            # Make the API call
            response = client.generate(prompt, parameters)
            response_time = time.time() - start_time

            # Record success
            self.provider_health.record_success(response_time)

            return response, provider, response_time

        except Exception as e:
            response_time = time.time() - start_time
            self.provider_health.record_failure()
            raise APIIntegrationError(f"Globant API call failed after {response_time:.2f}s: {str(e)}")

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get the current status of the Globant provider.

        Returns:
            Dictionary containing health metrics
        """
        return {
            "globant": {
                "healthy": self.provider_health.is_healthy,
                "success_rate": self.provider_health.get_success_rate(),
                "total_requests": self.provider_health.total_requests,
                "consecutive_failures": self.provider_health.consecutive_failures,
                "average_response_time": self.provider_health.average_response_time,
                "last_success_time": self.provider_health.last_success_time,
                "last_failure_time": self.provider_health.last_failure_time
            }
        }

    def reset_provider_health(self, provider: Optional[str] = None):
        """Reset health metrics for Globant provider.

        Args:
            provider: Ignored (only Globant supported)
        """
        self.provider_health.reset()
        self.logger.info("Reset health metrics for Globant provider")

    def set_provider_mode(self, mode: str):
        """Set provider mode (always Globant in simplified version).

        Args:
            mode: Ignored - always uses Globant
        """
        self.logger.info(f"Provider mode request '{mode}' - using Globant (single provider architecture)")

    def get_available_models(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available models from Globant Enterprise AI.

        Args:
            provider: Ignored (always uses Globant)

        Returns:
            List of available model dictionaries
        """
        try:
            client, _ = self.get_client()

            if hasattr(client, 'get_available_models'):
                return client.get_available_models()
            else:
                return []

        except Exception as e:
            self.logger.error(f"Failed to get available models from Globant: {str(e)}")
            return []

    # Backward compatibility methods (no-ops in simplified version)
    def translate_model_id(self, model_id: str, from_provider: str = None, to_provider: str = None) -> str:
        """Model ID translation (no-op in single provider mode)."""
        return model_id

    @property
    def default_mode(self):
        """Return default mode for backward compatibility."""
        class _Mode:
            value = "globant"
        return _Mode()

    @property
    def fallback_enabled(self):
        """Fallback disabled in single provider mode."""
        return False
