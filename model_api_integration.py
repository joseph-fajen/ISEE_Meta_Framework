"""
Model API Integration Module for ISEE Framework

This module provides integration with various AI model APIs, handling authentication,
request formatting, error handling, and response parsing.
"""

import os
import json
import time
import requests
import subprocess
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
try:
    from dotenv import load_dotenv
    # Attempt to load .env file from the project root
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # dotenv is not installed, just continue without it
    pass

# Try to import Google's Generative AI library
try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False

class APIIntegrationError(Exception):
    """Base exception for API integration errors."""
    pass

class RateLimitError(APIIntegrationError):
    """Exception for rate limit exceeded errors."""
    pass

class APITimeoutError(APIIntegrationError):
    """Exception for API timeout errors."""
    pass

class ModelAPIClient:
    """Base class for model API clients with async/sync support."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the API client.
        
        Args:
            api_key: API key for authentication. If None, will attempt to load from environment.
        """
        self.api_key = api_key
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._thread_pool = None  # Lazy initialization for async support
    
    def generate(self, prompt: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response from the model.
        
        Args:
            prompt: The input prompt to send to the model.
            parameters: Optional parameters to control generation.
            
        Returns:
            The generated text response.
        """
        raise NotImplementedError("Subclasses must implement generate()")
    
    async def generate_async(self, prompt: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Async wrapper for generate method.
        
        Args:
            prompt: The input prompt to send to the model.
            parameters: Optional parameters to control generation.
            
        Returns:
            The generated text response.
        """
        if self._thread_pool is None:
            self._thread_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix=f"{self.__class__.__name__}")
        
        try:
            # Run the synchronous generate method in a thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self._thread_pool,
                self.generate,
                prompt,
                parameters
            )
            return result
        except Exception as e:
            self.logger.error(f"Async generation failed: {str(e)}")
            raise APIIntegrationError(f"Async API call failed: {str(e)}")
    
    def _handle_error(self, response: requests.Response) -> None:
        """Handle error responses from the API.
        
        Args:
            response: The HTTP response object.
            
        Raises:
            RateLimitError: If the API returns a rate limit error.
            APITimeoutError: If the API returns a timeout error.
            APIIntegrationError: For other API errors.
        """
        try:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Unknown API error")
        except (ValueError, KeyError):
            error_message = f"API error: {response.status_code} - {response.text[:100]}"
        
        # Classify error types
        if response.status_code == 429:
            # Rate limit exceeded
            raise RateLimitError(f"Rate limit exceeded: {error_message}")
        elif response.status_code in [408, 504, 524]:
            # Timeout errors
            raise APITimeoutError(f"API timeout: {error_message}")
        elif "rate limit" in error_message.lower():
            # Rate limit in message body
            raise RateLimitError(f"Rate limit exceeded: {error_message}")
        elif "timeout" in error_message.lower():
            # Timeout in message body
            raise APITimeoutError(f"API timeout: {error_message}")
        else:
            # General API error
            raise APIIntegrationError(error_message)


class AnthropicClient(ModelAPIClient):
    """Client for the Anthropic Claude API."""
    
    def __init__(self, api_key: Optional[str] = None, api_version: str = "2023-06-01"):
        """Initialize the Anthropic Claude API client.
        
        Args:
            api_key: Anthropic API key. If None, will load from ANTHROPIC_API_KEY environment variable.
            api_version: API version to use.
        """
        super().__init__(api_key)
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise APIIntegrationError("Anthropic API key not provided and not found in environment")
        
        self.api_version = api_version
        self.base_url = "https://api.anthropic.com/v1/messages"
    
    def generate(self, prompt: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response from Claude.
        
        Args:
            prompt: The input prompt to send to Claude.
            parameters: Optional parameters like temperature, max_tokens, etc.
            
        Returns:
            The generated text response.
        """
        params = parameters or {}
        
        # Set default parameters if not provided
        if "max_tokens" not in params:
            params["max_tokens"] = 1024
        if "temperature" not in params:
            params["temperature"] = 0.7
        
        # Prepare the API request
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.api_version,
            "content-type": "application/json"
        }
        
        # Format the request payload according to Anthropic's API
        payload = {
            "model": params.get("model", "claude-3-sonnet-20240229"),
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": params["max_tokens"],
            "temperature": params["temperature"]
        }
        
        # Include other parameters if provided
        for key in ["top_p", "top_k", "stop_sequences"]:
            if key in params:
                payload[key] = params[key]
        
        # Send the request
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            
            if response.status_code != 200:
                self._handle_error(response)
            
            response_data = response.json()
            return response_data["content"][0]["text"]
        
        except requests.RequestException as e:
            raise APIIntegrationError(f"Request to Anthropic API failed: {str(e)}")
        except (KeyError, IndexError, ValueError) as e:
            raise APIIntegrationError(f"Failed to parse Anthropic API response: {str(e)}")


class OpenAIClient(ModelAPIClient):
    """Client for the OpenAI API."""
    
    def __init__(self, api_key: Optional[str] = None, organization: Optional[str] = None):
        """Initialize the OpenAI API client.
        
        Args:
            api_key: OpenAI API key. If None, will load from OPENAI_API_KEY environment variable.
            organization: Optional organization ID for OpenAI API.
        """
        super().__init__(api_key)
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise APIIntegrationError("OpenAI API key not provided and not found in environment")
        
        self.organization = organization or os.environ.get("OPENAI_ORGANIZATION")
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    def generate(self, prompt: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response from OpenAI.
        
        Args:
            prompt: The input prompt to send to OpenAI.
            parameters: Optional parameters like temperature, max_tokens, etc.
            
        Returns:
            The generated text response.
        """
        params = parameters or {}
        
        # Set default parameters if not provided
        if "max_tokens" not in params:
            params["max_tokens"] = 1024
        if "temperature" not in params:
            params["temperature"] = 0.7
        
        # Prepare the API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.organization:
            headers["OpenAI-Organization"] = self.organization
        
        # Format the request payload according to OpenAI's API
        payload = {
            "model": params.get("model", "gpt-4-turbo"),
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": params["max_tokens"],
            "temperature": params["temperature"]
        }
        
        # Include other parameters if provided
        for key in ["top_p", "presence_penalty", "frequency_penalty", "stop"]:
            if key in params:
                payload[key] = params[key]
        
        # Send the request
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            
            if response.status_code != 200:
                self._handle_error(response)
            
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]
        
        except requests.RequestException as e:
            raise APIIntegrationError(f"Request to OpenAI API failed: {str(e)}")
        except (KeyError, IndexError, ValueError) as e:
            raise APIIntegrationError(f"Failed to parse OpenAI API response: {str(e)}")


class GeminiClient(ModelAPIClient):
    """Client for the Google Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Google Gemini API client.
        
        Args:
            api_key: Google Gemini API key. If None, will load from GOOGLE_API_KEY environment variable.
        """
        super().__init__(api_key)
        
        if not GOOGLE_AI_AVAILABLE:
            raise ImportError("Google Generative AI library not installed. Please install with: pip install google-generativeai")
            
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise APIIntegrationError("Google API key not provided and not found in environment")
        
        # Configure the Google API client
        genai.configure(api_key=self.api_key)
    
    def generate(self, prompt: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response from Google Gemini.
        
        Args:
            prompt: The input prompt to send to Gemini.
            parameters: Optional parameters like temperature, max_tokens, etc.
            
        Returns:
            The generated text response.
        """
        params = parameters or {}
        
        # Set default parameters if not provided
        max_tokens = params.get("max_tokens", 1024)
        temperature = params.get("temperature", 0.7)
        top_p = params.get("top_p", 1.0)
        top_k = params.get("top_k", 32)
        
        model_name = params.get("model", "models/gemini-2.5-pro-exp-03-25")
        
        # Prepare the model
        try:
            # Get the specified model
            model = genai.GenerativeModel(model_name=model_name)
            
            # Configure the generation parameters
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                max_output_tokens=max_tokens,
                stop_sequences=params.get("stop_sequences", None)
            )
            
            # Generate the content
            response = model.generate_content(
                contents=prompt,
                generation_config=generation_config,
                safety_settings=params.get("safety_settings", None)
            )
            
            # Return the text from the response
            if response.text:
                return response.text
            else:
                # Handle the case where no text is generated
                raise APIIntegrationError("No text was generated from the Gemini API")
            
        except Exception as e:
            raise APIIntegrationError(f"Request to Google Gemini API failed: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get a list of available Google Gemini models.
        
        Returns:
            List of model names.
        """
        try:
            models = genai.list_models()
            # Filter for Gemini models only
            gemini_models = [model.name for model in models if "gemini" in model.name.lower()]
            return gemini_models
        except Exception as e:
            print(f"Failed to retrieve Gemini models: {str(e)}")
            return []

class OllamaClient(ModelAPIClient):
    """Client for the Ollama API."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "http://localhost:11434"):
        """Initialize the Ollama API client.
        
        Args:
            api_key: Not used for Ollama but kept for compatibility.
            base_url: Base URL for the Ollama API.
        """
        super().__init__(api_key)
        self.base_url = base_url
        self.session = requests.Session()
    
    def generate(self, prompt: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response from Ollama.
        
        Args:
            prompt: The input prompt to send to Ollama.
            parameters: Optional parameters like model, temperature, etc.
            
        Returns:
            The generated text response.
        """
        params = parameters or {}
        
        # Get the model name from parameters
        model = params.get("model", "llama3:8b")
        
        # Determine if we should use chat or completion API
        use_chat = params.get("use_chat", False)
        
        # Extract messages if provided, otherwise create from prompt
        messages = params.get("messages", [{"role": "user", "content": prompt}])
        
        # Create API request
        if use_chat and len(messages) > 1:
            url = f"{self.base_url}/api/chat"
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": params.get("temperature", 0.7),
                    "num_predict": params.get("max_tokens", 1024)
                }
            }
        else:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": params.get("temperature", 0.7),
                    "num_predict": params.get("max_tokens", 1024)
                }
            }
        
        # Send the request
        try:
            response = self.session.post(url, json=payload, timeout=params.get("timeout", 600))
            
            if response.status_code != 200:
                self._handle_error(response)
            
            response_json = response.json()
            
            # Extract response text according to API endpoint used
            if use_chat and len(messages) > 1:
                return response_json.get("message", {}).get("content", "")
            else:
                return response_json.get("response", "")
        
        except requests.RequestException as e:
            raise APIIntegrationError(f"Request to Ollama API failed: {str(e)}")
        except (KeyError, IndexError, ValueError) as e:
            raise APIIntegrationError(f"Failed to parse Ollama API response: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get a list of available Ollama models.
        
        Returns:
            List of model names.
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = self.session.get(url)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            # Filter out embedding models which cannot generate text
            models = [model["name"] for model in data.get("models", []) 
                     if "embed" not in model["name"].lower()]
            return models
        except Exception:
            # If API call fails, try command line as fallback
            try:
                result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
                lines = result.stdout.strip().split('\n')
                
                # Skip the header line
                if len(lines) > 1:
                    models = []
                    for line in lines[1:]:  # Skip header row
                        parts = line.split()
                        if len(parts) >= 1:
                            model_name = parts[0]
                            # Skip embedding models
                            if "embed" not in model_name.lower():
                                models.append(model_name)
                    return models
            except:
                pass
            return []


class GlobantEnterpriseClient(ModelAPIClient):
    """Client for Globant Enterprise AI API."""
    
    def __init__(self, api_key: Optional[str] = None, org_id: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize the Globant Enterprise AI API client.
        
        Args:
            api_key: Globant API key. If None, will load from GLOBANT_API_KEY environment variable.
            org_id: Globant organization ID. If None, will load from GLOBANT_ORG_ID environment variable.
            base_url: Base URL for Globant API. If None, will load from GLOBANT_BASE_URL environment variable.
        """
        super().__init__(api_key)
        self.api_key = api_key or os.environ.get("GLOBANT_API_KEY")
        self.org_id = org_id or os.environ.get("GLOBANT_ORG_ID")
        self.base_url = base_url or os.environ.get("GLOBANT_BASE_URL", "https://api.saia.ai")
        
        if not self.api_key:
            raise APIIntegrationError("Globant API key not provided and not found in environment")
        if not self.org_id:
            raise APIIntegrationError("Globant organization ID not provided and not found in environment")
        
        # Globant API endpoints (confirmed working endpoints)
        self.chat_url = f"{self.base_url}/chat/completions"
        self.models_url = f"{self.base_url}/models"
        
        # Cache for available models
        self._models_cache = None
        self._models_cache_time = 0
        self._cache_duration = 300  # 5 minutes
    
    def _is_reasoning_model(self, model: str) -> bool:
        """Check if the model is a reasoning model that requires special parameter handling.
        
        Args:
            model: The model identifier (e.g., "openai/o1", "openai/o3-mini")
            
        Returns:
            True if this is a reasoning model, False otherwise.
        """
        reasoning_model_patterns = [
            "o1", "o3", "o4"  # OpenAI reasoning model series
        ]
        model_lower = model.lower()
        return any(pattern in model_lower for pattern in reasoning_model_patterns)
    
    def generate(self, prompt: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response using Globant Enterprise AI.
        
        Args:
            prompt: The input prompt to send to the model.
            parameters: Optional parameters like model, temperature, max_tokens, etc.
            
        Returns:
            The generated text response.
        """
        params = parameters or {}
        model = params.get("model", "gpt-4-turbo")
        
        # Prepare the API request headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Organization-ID": self.org_id
        }
        
        # Format the request payload (OpenAI-compatible format)
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        # Check if this is a reasoning model and handle parameters accordingly
        is_reasoning = self._is_reasoning_model(model)
        
        if is_reasoning:
            # Reasoning models (o1, o3, o4 series) have different parameter requirements
            
            # Use max_completion_tokens instead of max_tokens
            if "max_completion_tokens" in params:
                payload["max_completion_tokens"] = params["max_completion_tokens"]
            elif "max_tokens" in params:
                payload["max_completion_tokens"] = params["max_tokens"]
            else:
                payload["max_completion_tokens"] = 1024
            
            # Add reasoning_effort parameter if provided, otherwise use default
            if "reasoning_effort" in params:
                valid_efforts = ["low", "medium", "high"]
                if params["reasoning_effort"] in valid_efforts:
                    payload["reasoning_effort"] = params["reasoning_effort"]
                else:
                    payload["reasoning_effort"] = "medium"  # Safe default
            else:
                payload["reasoning_effort"] = "medium"  # Default reasoning level
            
            # Reasoning models don't support temperature parameter
            # Do not include temperature, top_p, presence_penalty, frequency_penalty
            
        else:
            # Standard models use regular parameters
            if "max_tokens" in params:
                payload["max_tokens"] = params["max_tokens"]
            else:
                payload["max_tokens"] = 1024
            
            if "temperature" in params:
                payload["temperature"] = params["temperature"]
            else:
                payload["temperature"] = 0.7
            
            # Include other standard parameters if provided
            for key in ["top_p", "presence_penalty", "frequency_penalty", "stop"]:
                if key in params:
                    payload[key] = params[key]
        
        # Add common parameters that work for both model types
        for key in ["stream", "user", "n"]:
            if key in params:
                payload[key] = params[key]
        
        # Send the request
        try:
            response = requests.post(self.chat_url, headers=headers, json=payload, timeout=120)
            
            if response.status_code != 200:
                self._handle_error(response)
            
            response_data = response.json()
            
            # Check for Globant-specific errors in the response
            if "error" in response_data:
                error_info = response_data["error"]
                error_message = error_info.get("message", "Unknown error")
                error_code = error_info.get("code", "Unknown")
                
                raise APIIntegrationError(f"Globant Enterprise AI error {error_code}: {error_message}")
            
            # Standard OpenAI-compatible response parsing
            return response_data["choices"][0]["message"]["content"]
        
        except requests.RequestException as e:
            raise APIIntegrationError(f"Request to Globant Enterprise AI API failed: {str(e)}")
        except (KeyError, IndexError, ValueError) as e:
            raise APIIntegrationError(f"Failed to parse Globant Enterprise AI API response: {str(e)}")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get a list of available models from Globant Enterprise AI.
        
        Returns:
            A list of model dictionaries with id, name, and other metadata.
        """
        current_time = time.time()
        
        # Return cached models if cache is still valid
        if (self._models_cache is not None and 
            current_time - self._models_cache_time < self._cache_duration):
            return self._models_cache
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "X-Organization-ID": self.org_id
            }
            
            response = requests.get(self.models_url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                raise APIIntegrationError(f"Failed to fetch models: {response.status_code}")
            
            data = response.json()
            models = data.get("data", [])
            
            # Cache the results
            self._models_cache = models
            self._models_cache_time = current_time
            
            return models
        
        except requests.RequestException as e:
            # Fallback to common models if API call fails
            return self._get_fallback_models()
        except (KeyError, ValueError) as e:
            return self._get_fallback_models()
    
    def _get_fallback_models(self) -> List[Dict[str, Any]]:
        """Provide fallback models based on current enterprise AI offerings with correct 2025 model names."""
        return [
            {
                "id": "claude-sonnet-4-20250514",
                "name": "Claude Sonnet 4",
                "provider": "globant",
                "capabilities": ["frontier_reasoning", "highest_quality", "complex_reasoning"],
                "cost_tier": "premium_plus"
            },
            {
                "id": "claude-3-5-haiku-20241022",
                "name": "Claude 3.5 Haiku",
                "provider": "globant",
                "capabilities": ["fastest", "cost_efficient", "high_quality"],
                "cost_tier": "standard"
            },
            {
                "id": "gpt-4o-mini",
                "name": "GPT-4o Mini",
                "provider": "globant",
                "capabilities": ["fastest", "cost_efficient", "reasoning"],
                "cost_tier": "standard"
            },
            {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "provider": "globant",
                "capabilities": ["fast", "reasoning", "coding"],
                "cost_tier": "premium"
            },
            {
                "id": "gemini-2.5-pro",
                "name": "Gemini 2.5 Pro",
                "provider": "globant",
                "capabilities": ["efficiency_leader", "multimodal", "fast"],
                "cost_tier": "premium"
            }
        ]
    
    def get_model_names(self) -> List[str]:
        """Get a simple list of available model names.
        
        Returns:
            A list of model ID strings.
        """
        try:
            models = self.get_available_models()
            return [model.get("id", "") for model in models if model.get("id")]
        except Exception:
            # Return fallback model names with correct 2025 identifiers
            return [
                "claude-sonnet-4-20250514",
                "claude-3-5-haiku-20241022",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gemini-2.5-pro"
            ]


class ModelAPIFactory:
    """Factory for creating model API clients."""

    @staticmethod
    def create_client(provider: str, **kwargs) -> ModelAPIClient:
        """Create a model API client for the specified provider.

        Args:
            provider: The provider name ("globant", "anthropic", "openai", "ollama", "gemini")
            **kwargs: Additional arguments to pass to the client constructor.

        Returns:
            A model API client instance.

        Raises:
            ValueError: If the provider is not supported.

        Note:
            Globant Enterprise AI is the primary provider for ISEE.
            "openrouter" is redirected to "globant" for backward compatibility.
        """
        provider = provider.lower()

        # Primary provider: Globant Enterprise AI
        if provider in ("globant", "openrouter"):
            # openrouter redirected to globant for backward compatibility
            return GlobantEnterpriseClient(**kwargs)
        elif provider == "anthropic":
            return AnthropicClient(**kwargs)
        elif provider == "openai":
            return OpenAIClient(**kwargs)
        elif provider == "ollama":
            return OllamaClient(**kwargs)
        elif provider == "gemini":
            return GeminiClient(**kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}. Use 'globant' (primary) or direct providers.")


# Example usage:
def test_api_integration():
    """Test the API integration with a simple prompt."""
    # Load API keys from environment variables
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    google_key = os.environ.get("GOOGLE_API_KEY")
    
    # Test prompt
    prompt = "Explain the concept of combinatorial innovation in one paragraph."
    
    # Test with available APIs
    results = []
    
    if anthropic_key:
        try:
            print("Testing Anthropic API...")
            client = ModelAPIFactory.create_client("anthropic")
            result = client.generate(prompt)
            print(f"Response: {result[:100]}...")
            results.append(("Anthropic", True))
        except Exception as e:
            print(f"Anthropic API test failed: {str(e)}")
            results.append(("Anthropic", False))
    
    if openai_key:
        try:
            print("Testing OpenAI API...")
            client = ModelAPIFactory.create_client("openai")
            result = client.generate(prompt)
            print(f"Response: {result[:100]}...")
            results.append(("OpenAI", True))
        except Exception as e:
            print(f"OpenAI API test failed: {str(e)}")
            results.append(("OpenAI", False))
    
    if google_key and GOOGLE_AI_AVAILABLE:
        try:
            print("Testing Google Gemini API...")
            client = ModelAPIFactory.create_client("gemini")
            
            # List available Gemini models
            if hasattr(client, 'get_available_models'):
                print("Available Gemini models:")
                models = client.get_available_models()
                for model in models[:5]:  # Show first 5 models
                    print(f"  - {model}")
                if len(models) > 5:
                    print(f"  - ... and {len(models) - 5} more")
            
            result = client.generate(prompt)
            print(f"Response: {result[:100]}...")
            results.append(("Gemini", True))
        except Exception as e:
            print(f"Google Gemini API test failed: {str(e)}")
            results.append(("Gemini", False))
    elif google_key and not GOOGLE_AI_AVAILABLE:
        print("Google AI library not installed. Install with: pip install google-generativeai")
        results.append(("Gemini", False))
    
    # Test Ollama if available (no key needed)
    try:
        # First check if Ollama is running
        client = ModelAPIFactory.create_client("ollama")
        models = client.get_available_models()
        
        if models:
            print(f"Testing Ollama API with model: {models[0]}...")
            # Use first available model
            parameters = {"model": models[0]}
            result = client.generate(prompt, parameters)
            print(f"Response: {result[:100]}...")
            results.append(("Ollama", True))
        else:
            print("No Ollama models found. Is Ollama installed and running?")
            results.append(("Ollama", False))
    except Exception as e:
        print(f"Ollama API test failed: {str(e)}")
        results.append(("Ollama", False))
    
    # Print summary
    print("\nAPI Integration Test Results:")
    for provider, success in results:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{provider}: {status}")
    
    # If no tests were run
    if not results:
        print("No API providers available for testing. Make sure at least one of these is set up:")
        print("- Anthropic API key in environment variable ANTHROPIC_API_KEY")
        print("- OpenAI API key in environment variable OPENAI_API_KEY")
        print("- Google API key in environment variable GOOGLE_API_KEY")
        print("- Ollama running locally (http://localhost:11434)")


if __name__ == "__main__":
    test_api_integration()
