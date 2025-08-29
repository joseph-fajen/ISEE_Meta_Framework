#!/usr/bin/env python3
"""
Globant Enterprise AI Error Handling Examples
==============================================

Comprehensive error handling patterns for Globant's Enterprise AI API.
Based on real-world issues encountered during ISEE Meta Framework development.

This module demonstrates:
- Common error scenarios and their solutions
- Robust error handling patterns
- Retry strategies and fallback mechanisms
- Debugging tools and techniques

Usage:
    python globant_error_handling.py
"""

import os
import json
import time
import requests
import logging
from typing import Dict, Any, Optional, Tuple
from enum import Enum

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GlobantErrorType(Enum):
    """Classification of Globant API errors."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    MODEL_FORMAT = "model_format"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    SERVER_ERROR = "server_error"
    NETWORK = "network"
    ORGANIZATION = "organization"
    QUOTA = "quota"
    UNKNOWN = "unknown"


class GlobantErrorHandler:
    """
    Comprehensive error handling for Globant Enterprise AI API.
    
    Provides classification, retry logic, and recovery strategies
    based on the specific type of error encountered.
    """
    
    def __init__(self, api_key: str, org_id: str, max_retries: int = 3):
        self.api_key = api_key
        self.org_id = org_id
        self.max_retries = max_retries
        self.base_url = "https://api.saia.ai"
        self.retry_delays = [1, 2, 4]  # Exponential backoff
    
    def call_with_error_handling(self, prompt: str, model: str, **kwargs) -> Tuple[Optional[str], Optional[str]]:
        """
        Make an API call with comprehensive error handling.
        
        Args:
            prompt: Input prompt
            model: Model identifier
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (response_text, error_message)
            If successful: (response, None)
            If failed: (None, error_description)
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = self._make_api_call(prompt, model, **kwargs)
                logger.info(f"API call succeeded on attempt {attempt + 1}")
                return response, None
                
            except Exception as e:
                last_error = e
                error_type = self._classify_error(e)
                
                logger.warning(f"Attempt {attempt + 1} failed: {error_type.value} - {str(e)}")
                
                # Determine if we should retry
                if not self._should_retry(error_type, attempt):
                    break
                
                # Apply retry delay
                if attempt < self.max_retries - 1:
                    delay = self._get_retry_delay(error_type, attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
        
        # All retries failed
        error_message = self._format_error_message(last_error)
        logger.error(f"All retries failed. Final error: {error_message}")
        return None, error_message
    
    def _make_api_call(self, prompt: str, model: str, **kwargs) -> str:
        """Make a single API call with proper error detection."""
        
        # Validate model format first
        if "/" not in model:
            raise ValueError(f"Invalid model format: '{model}'. Must use 'provider/model' format")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Organization-ID": self.org_id
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", 1024),
            "temperature": kwargs.get("temperature", 0.7)
        }
        
        # Special handling for reasoning models (o1, o3, o4 series)
        is_reasoning_model = any(series in model.lower() for series in ["o1", "o3", "o4"])
        
        if is_reasoning_model:
            # Reasoning models use different parameters
            payload.pop("temperature", None)  # Not supported by reasoning models
            
            # Set reasoning_effort parameter (controls internal reasoning depth)
            if "reasoning_effort" in kwargs:
                valid_efforts = ["low", "medium", "high"]
                if kwargs["reasoning_effort"] not in valid_efforts:
                    raise ValueError(f"reasoning_effort must be one of {valid_efforts}")
                payload["reasoning_effort"] = kwargs["reasoning_effort"]
            else:
                payload["reasoning_effort"] = "medium"  # Default reasoning level
            
            # Use max_completion_tokens instead of max_tokens
            if "max_completion_tokens" in kwargs:
                payload["max_completion_tokens"] = kwargs["max_completion_tokens"]
                payload.pop("max_tokens", None)
            else:
                # Convert max_tokens to max_completion_tokens
                payload["max_completion_tokens"] = payload.pop("max_tokens", 1024)
        
        # Make the request
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=kwargs.get("timeout", 120)
        )
        
        # Handle different response scenarios
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                # API-level error in 200 response
                raise Exception(f"API Error: {data['error'].get('message', 'Unknown error')}")
            return data["choices"][0]["message"]["content"]
        
        else:
            # HTTP error
            self._handle_http_error(response)
    
    def _classify_error(self, error: Exception) -> GlobantErrorType:
        """Classify error type for appropriate handling strategy."""
        
        error_str = str(error).lower()
        
        # Authentication errors
        if any(phrase in error_str for phrase in ["unauthorized", "invalid api key", "authentication failed"]):
            return GlobantErrorType.AUTHENTICATION
        
        # Authorization errors  
        if any(phrase in error_str for phrase in ["forbidden", "access denied", "permission"]):
            return GlobantErrorType.AUTHORIZATION
        
        # Model format errors
        if any(phrase in error_str for phrase in ["invalid model", "model name", "provider/model"]):
            return GlobantErrorType.MODEL_FORMAT
        
        # Rate limiting
        if any(phrase in error_str for phrase in ["rate limit", "too many requests", "429"]):
            return GlobantErrorType.RATE_LIMIT
        
        # Timeout errors
        if any(phrase in error_str for phrase in ["timeout", "timed out", "connection timeout"]):
            return GlobantErrorType.TIMEOUT
        
        # Organization/billing errors
        if any(phrase in error_str for phrase in ["organization", "quota", "billing", "credits"]):
            return GlobantErrorType.ORGANIZATION
        
        # Server errors
        if any(phrase in error_str for phrase in ["500", "502", "503", "504", "server error"]):
            return GlobantErrorType.SERVER_ERROR
        
        # Network errors
        if isinstance(error, requests.RequestException):
            return GlobantErrorType.NETWORK
        
        return GlobantErrorType.UNKNOWN
    
    def _should_retry(self, error_type: GlobantErrorType, attempt: int) -> bool:
        """Determine if error is retryable and we haven't exceeded max attempts."""
        
        if attempt >= self.max_retries - 1:
            return False
        
        # Never retry these error types
        non_retryable = {
            GlobantErrorType.AUTHENTICATION,
            GlobantErrorType.AUTHORIZATION, 
            GlobantErrorType.MODEL_FORMAT,
            GlobantErrorType.ORGANIZATION
        }
        
        return error_type not in non_retryable
    
    def _get_retry_delay(self, error_type: GlobantErrorType, attempt: int) -> float:
        """Get appropriate retry delay based on error type."""
        
        base_delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
        
        # Longer delays for rate limiting
        if error_type == GlobantErrorType.RATE_LIMIT:
            return base_delay * 3
        
        # Shorter delays for network issues
        if error_type == GlobantErrorType.NETWORK:
            return base_delay * 0.5
        
        return base_delay
    
    def _handle_http_error(self, response: requests.Response):
        """Handle specific HTTP error responses."""
        
        status_code = response.status_code
        
        try:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", f"HTTP {status_code}")
        except:
            error_message = f"HTTP {status_code}"
        
        if status_code == 400:
            if "invalid" in error_message.lower() and "model" in error_message.lower():
                raise ValueError(f"Model format error: {error_message}")
            else:
                raise ValueError(f"Bad request: {error_message}")
        
        elif status_code == 401:
            raise PermissionError(f"Authentication failed: {error_message}")
        
        elif status_code == 403:
            raise PermissionError(f"Access denied: {error_message}")
        
        elif status_code == 429:
            raise Exception(f"Rate limit exceeded: {error_message}")
        
        elif status_code >= 500:
            raise Exception(f"Server error: {error_message}")
        
        else:
            raise Exception(f"HTTP {status_code}: {error_message}")
    
    def _format_error_message(self, error: Exception) -> str:
        """Format error message with helpful troubleshooting info."""
        
        error_type = self._classify_error(error)
        base_message = str(error)
        
        troubleshooting = {
            GlobantErrorType.AUTHENTICATION: "Check your GLOBANT_API_KEY environment variable",
            GlobantErrorType.AUTHORIZATION: "Verify your GLOBANT_ORG_ID and account permissions", 
            GlobantErrorType.MODEL_FORMAT: "Use format: 'provider/model' (e.g., 'anthropic/claude-3-5-haiku-20241022')",
            GlobantErrorType.RATE_LIMIT: "Reduce request frequency or upgrade your plan",
            GlobantErrorType.TIMEOUT: "Check network connection or increase timeout value",
            GlobantErrorType.ORGANIZATION: "Contact Globant about billing/quota issues",
            GlobantErrorType.SERVER_ERROR: "Globant server issue - try again later",
            GlobantErrorType.NETWORK: "Check internet connection and firewall settings"
        }
        
        if error_type in troubleshooting:
            return f"{base_message}\n💡 Suggestion: {troubleshooting[error_type]}"
        
        return base_message


def demonstrate_error_scenarios():
    """Demonstrate various error scenarios and their handling."""
    
    print("Globant Error Handling Demonstration")
    print("=" * 40)
    
    # Get credentials
    api_key = os.getenv("GLOBANT_API_KEY", "fake_key_for_demo")
    org_id = os.getenv("GLOBANT_ORG_ID", "fake_org_for_demo")
    
    handler = GlobantErrorHandler(api_key, org_id)
    
    error_scenarios = [
        {
            "name": "Invalid Model Format",
            "model": "claude-3-5-haiku",  # Missing provider prefix
            "prompt": "Test",
            "expected": "Should fail with model format error"
        },
        {
            "name": "Invalid Authentication", 
            "model": "anthropic/claude-3-5-haiku-20241022",
            "prompt": "Test",
            "expected": "Should fail with auth error (unless you have real creds)"
        },
        {
            "name": "Valid Model with Real Credentials",
            "model": "anthropic/claude-3-5-haiku-20241022", 
            "prompt": "Say hello!",
            "expected": "Should succeed if you have valid credentials"
        }
    ]
    
    for scenario in error_scenarios:
        print(f"\n🧪 Testing: {scenario['name']}")
        print(f"Expected: {scenario['expected']}")
        
        response, error = handler.call_with_error_handling(
            scenario["prompt"], 
            scenario["model"],
            max_tokens=50
        )
        
        if response:
            print(f"✅ Success: {response[:100]}...")
        else:
            print(f"❌ Failed: {error}")


def validate_setup():
    """Validate Globant setup and provide specific guidance."""
    
    print("Globant Setup Validation")
    print("=" * 25)
    
    # Check environment variables
    api_key = os.getenv("GLOBANT_API_KEY")
    org_id = os.getenv("GLOBANT_ORG_ID")
    base_url = os.getenv("GLOBANT_BASE_URL", "https://api.saia.ai")
    
    issues = []
    
    if not api_key:
        issues.append("❌ GLOBANT_API_KEY not set")
    else:
        print("✅ GLOBANT_API_KEY found")
    
    if not org_id:
        issues.append("❌ GLOBANT_ORG_ID not set")
    else:
        print("✅ GLOBANT_ORG_ID found")
    
    if base_url != "https://api.saia.ai":
        issues.append(f"⚠️  GLOBANT_BASE_URL is '{base_url}', should be 'https://api.saia.ai'")
    else:
        print("✅ GLOBANT_BASE_URL correct")
    
    if issues:
        print("\n🔧 Setup Issues Found:")
        for issue in issues:
            print(f"   {issue}")
        print("\n📋 To fix:")
        print("   1. Set missing environment variables")
        print("   2. Use correct base URL: https://api.saia.ai")
        print("   3. Ensure model format: provider/model")
    else:
        print("\n✅ Setup looks good!")
    
    return len(issues) == 0


def test_specific_models():
    """Test specific models with proper error handling."""
    
    api_key = os.getenv("GLOBANT_API_KEY")
    org_id = os.getenv("GLOBANT_ORG_ID") 
    
    if not api_key or not org_id:
        print("❌ Missing credentials for model testing")
        return
    
    handler = GlobantErrorHandler(api_key, org_id)
    
    test_models = [
        "anthropic/claude-3-5-haiku-20241022",
        "openai/gpt-4o-mini",
        "vertex_ai/gemini-2.5-pro",
        "openai/o1",  # Reasoning model test
        "invalid-model-format",  # Should fail
        "openai/nonexistent-model"  # Should fail
    ]
    
    print("\nModel Testing with Error Handling")
    print("-" * 35)
    
    for model in test_models:
        print(f"\n🧪 Testing: {model}")
        
        # Use appropriate parameters for reasoning models
        if any(series in model for series in ["o1", "o3", "o4"]):
            kwargs = {
                "reasoning_effort": "medium",
                "max_completion_tokens": 50,
                "timeout": 60  # Reasoning models may take longer
            }
            test_prompt = "What is 2+2? Show your reasoning."
        else:
            kwargs = {
                "max_tokens": 50,
                "timeout": 30,
                "temperature": 0.7
            }
            test_prompt = "Hello! This is a test."
        
        response, error = handler.call_with_error_handling(
            test_prompt,
            model,
            **kwargs
        )
        
        if response:
            print(f"✅ Success: {response[:80]}...")
        else:
            print(f"❌ Error: {error}")


def main():
    """Main demonstration function."""
    
    print("🔧 Globant Enterprise AI - Error Handling Guide")
    print("=" * 50)
    
    # Validate setup first
    if not validate_setup():
        print("\n⚠️  Please fix setup issues before proceeding")
        return
    
    # Run demonstrations
    demonstrate_error_scenarios()
    
    # Test specific models if credentials available
    if os.getenv("GLOBANT_API_KEY") and os.getenv("GLOBANT_ORG_ID"):
        test_specific_models()
    else:
        print("\n📝 To test actual API calls, set:")
        print("   export GLOBANT_API_KEY=your_key")  
        print("   export GLOBANT_ORG_ID=your_org_id")
    
    print("\n📚 Error Handling Tips:")
    print("   • Always validate model format: 'provider/model'")
    print("   • Include both Authorization and X-Organization-ID headers")
    print("   • Use exponential backoff for retries")
    print("   • Don't retry authentication/authorization errors")
    print("   • Log errors for debugging")
    print("   • Check Globant documentation for model availability")


if __name__ == "__main__":
    main()