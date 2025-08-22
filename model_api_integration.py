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


class OpenRouterClient(ModelAPIClient):
    """Client for the OpenRouter unified API providing access to 300+ models."""
    
    def __init__(self, api_key: Optional[str] = None, site_url: Optional[str] = None, app_name: Optional[str] = None):
        """Initialize the OpenRouter API client.
        
        Args:
            api_key: OpenRouter API key. If None, will load from OPENROUTER_API_KEY environment variable.
            site_url: Optional site URL for referrer tracking and rankings.
            app_name: Optional app name for identification in OpenRouter dashboard.
        """
        super().__init__(api_key)
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise APIIntegrationError("OpenRouter API key not provided and not found in environment")
        
        self.site_url = site_url or os.environ.get("OPENROUTER_SITE_URL")
        self.app_name = app_name or os.environ.get("OPENROUTER_APP_NAME", "ISEE Meta Framework")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.models_url = "https://openrouter.ai/api/v1/models"
        
        # Cache for available models to reduce API calls
        self._models_cache = None
        self._models_cache_time = 0
        self._cache_duration = 300  # 5 minutes
        
        # Cache for categorized models
        self._categorized_models_cache = None
        self._categorized_models_cache_time = 0
        
        # Initialize categorization system
        try:
            from openrouter_categorization import OpenRouterCategorizer
            self.categorizer = OpenRouterCategorizer()
            self._categorization_available = True
        except ImportError:
            self.categorizer = None
            self._categorization_available = False
    
    def generate(self, prompt: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response using OpenRouter.
        
        Args:
            prompt: The input prompt to send to the model.
            parameters: Optional parameters like model, temperature, max_tokens, etc.
            
        Returns:
            The generated text response.
        """
        params = parameters or {}
        
        # Set default parameters if not provided
        if "max_tokens" not in params:
            params["max_tokens"] = 1024
        if "temperature" not in params:
            params["temperature"] = 0.7
        
        # Prepare the API request headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Add optional headers for tracking and rankings
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        if self.app_name:
            headers["X-Title"] = self.app_name
        
        # Format the request payload (OpenAI-compatible format)
        payload = {
            "model": params.get("model", "anthropic/claude-3-sonnet"),
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": params["max_tokens"],
            "temperature": params["temperature"]
        }
        
        # Include other parameters if provided
        for key in ["top_p", "presence_penalty", "frequency_penalty", "stop"]:
            if key in params:
                payload[key] = params[key]
        
        # Add OpenRouter-specific parameters if provided
        for key in ["transforms", "models", "route"]:
            if key in params:
                payload[key] = params[key]
        
        # Send the request
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=120)
            
            if response.status_code != 200:
                self._handle_error(response)
            
            response_data = response.json()
            
            # Check for provider errors in the response
            if "error" in response_data:
                error_info = response_data["error"]
                provider_name = error_info.get("metadata", {}).get("provider_name", "Unknown")
                error_message = error_info.get("message", "Unknown error")
                error_code = error_info.get("code", "Unknown")
                
                raise APIIntegrationError(f"Provider {provider_name} error {error_code}: {error_message}")
            
            # Standard OpenAI-compatible response parsing
            return response_data["choices"][0]["message"]["content"]
        
        except requests.RequestException as e:
            raise APIIntegrationError(f"Request to OpenRouter API failed: {str(e)}")
        except (KeyError, IndexError, ValueError) as e:
            raise APIIntegrationError(f"Failed to parse OpenRouter API response: {str(e)}")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get a list of available models from OpenRouter with detailed information.
        
        Returns:
            A list of model dictionaries with id, name, pricing, and other metadata.
        """
        current_time = time.time()
        
        # Return cached models if cache is still valid
        if (self._models_cache is not None and 
            current_time - self._models_cache_time < self._cache_duration):
            return self._models_cache
        
        try:
            response = requests.get(self.models_url, timeout=30)
            
            if response.status_code != 200:
                raise APIIntegrationError(f"Failed to fetch models: {response.status_code}")
            
            data = response.json()
            models = data.get("data", [])
            
            # Cache the results
            self._models_cache = models
            self._models_cache_time = current_time
            
            return models
        
        except requests.RequestException as e:
            raise APIIntegrationError(f"Request to OpenRouter models API failed: {str(e)}")
        except (KeyError, ValueError) as e:
            raise APIIntegrationError(f"Failed to parse OpenRouter models response: {str(e)}")
    
    def get_model_names(self) -> List[str]:
        """Get a simple list of available model names.
        
        Returns:
            A list of model ID strings.
        """
        try:
            models = self.get_available_models()
            return [model.get("id", "") for model in models if model.get("id")]
        except Exception:
            # Return a fallback list of popular models if API call fails
            return [
                "anthropic/claude-3-sonnet",
                "anthropic/claude-3-opus", 
                "openai/gpt-4-turbo",
                "openai/gpt-4",
                "openai/gpt-3.5-turbo",
                "google/gemini-pro",
                "meta-llama/llama-2-70b-chat",
                "mistralai/mixtral-8x7b-instruct"
            ]
    
    def get_models_by_provider(self, provider: str) -> List[Dict[str, Any]]:
        """Get models filtered by provider.
        
        Args:
            provider: Provider name (e.g., "anthropic", "openai", "google", "meta-llama")
            
        Returns:
            A list of model dictionaries from the specified provider.
        """
        try:
            all_models = self.get_available_models()
            return [model for model in all_models 
                   if model.get("id", "").startswith(f"{provider}/")]
        except Exception:
            return []
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific model.
        
        Args:
            model_id: The model ID to get information for.
            
        Returns:
            Model information dictionary or None if not found.
        """
        try:
            all_models = self.get_available_models()
            for model in all_models:
                if model.get("id") == model_id:
                    return model
            return None
        except Exception:
            return None
    
    def get_categorized_models(self) -> List[Dict[str, Any]]:
        """Get models with rich categorization metadata.
        
        Returns:
            List of models with categorization information added.
        """
        if not self._categorization_available:
            # Fallback to basic model list if categorization unavailable
            return self.get_available_models()
        
        current_time = time.time()
        
        # Return cached categorized models if cache is still valid
        if (self._categorized_models_cache is not None and 
            current_time - self._categorized_models_cache_time < self._cache_duration):
            return self._categorized_models_cache
        
        try:
            # Get raw model data
            raw_models = self.get_available_models()
            
            # Categorize each model
            categorized_models = []
            for model_data in raw_models:
                try:
                    model_metadata = self.categorizer.categorize_model(model_data)
                    
                    # Convert to enriched dictionary format
                    enriched_model = dict(model_data)  # Start with original data
                    enriched_model.update({
                        'provider_category': model_metadata.provider.value,
                        'capabilities': [cap.value for cap in model_metadata.capabilities],
                        'cost_tier': model_metadata.cost_tier.value,
                        'use_cases': [uc.value for uc in model_metadata.use_cases],
                        'quality_score': model_metadata.quality_score,
                        'speed_tier': model_metadata.speed_tier,
                        'categorization_metadata': model_metadata
                    })
                    categorized_models.append(enriched_model)
                    
                except Exception as e:
                    # If categorization fails for a model, include it without enrichment
                    categorized_models.append(model_data)
            
            # Cache the results
            self._categorized_models_cache = categorized_models
            self._categorized_models_cache_time = current_time
            
            return categorized_models
            
        except Exception:
            # Fallback to basic models if categorization fails completely
            return self.get_available_models()
    
    def filter_models_by_provider(self, provider: str) -> List[Dict[str, Any]]:
        """Get models filtered by provider.
        
        Args:
            provider: Provider name (e.g., "anthropic", "openai", "google")
            
        Returns:
            List of models from the specified provider.
        """
        try:
            categorized_models = self.get_categorized_models()
            return [model for model in categorized_models 
                   if model.get('provider_category') == provider or
                   model.get('id', '').startswith(f'{provider}/')]
        except Exception:
            # Fallback to basic filtering
            return self.get_models_by_provider(provider)
    
    def filter_models_by_capabilities(self, required_capabilities: List[str]) -> List[Dict[str, Any]]:
        """Filter models by required capabilities.
        
        Args:
            required_capabilities: List of capability names (e.g., ["reasoning", "fast"])
            
        Returns:
            List of models that have all required capabilities.
        """
        try:
            categorized_models = self.get_categorized_models()
            filtered_models = []
            
            for model in categorized_models:
                model_capabilities = model.get('capabilities', [])
                if all(cap in model_capabilities for cap in required_capabilities):
                    filtered_models.append(model)
                    
            return filtered_models
        except Exception:
            return []
    
    def filter_models_by_cost_tier(self, cost_tiers: List[str]) -> List[Dict[str, Any]]:
        """Filter models by cost tiers.
        
        Args:
            cost_tiers: List of cost tier names (e.g., ["budget", "standard"])
            
        Returns:
            List of models in the specified cost tiers.
        """
        try:
            categorized_models = self.get_categorized_models()
            return [model for model in categorized_models 
                   if model.get('cost_tier') in cost_tiers]
        except Exception:
            return []
    
    def filter_models_by_use_case(self, use_cases: List[str]) -> List[Dict[str, Any]]:
        """Filter models by use cases.
        
        Args:
            use_cases: List of use case names (e.g., ["deep_analysis", "creative_innovation"])
            
        Returns:
            List of models suitable for the specified use cases.
        """
        try:
            categorized_models = self.get_categorized_models()
            filtered_models = []
            
            for model in categorized_models:
                model_use_cases = model.get('use_cases', [])
                if any(uc in model_use_cases for uc in use_cases):
                    filtered_models.append(model)
                    
            return filtered_models
        except Exception:
            return []
    
    def get_recommended_models_for_isee(self, 
                                       use_case: str = "deep_analysis",
                                       max_models: int = 5,
                                       diversity_providers: bool = True,
                                       min_quality: float = 7.0) -> List[Dict[str, Any]]:
        """Get recommended models optimized for ISEE framework usage.
        
        Args:
            use_case: Target use case (e.g., "deep_analysis", "creative_innovation")
            max_models: Maximum number of models to return
            diversity_providers: Whether to ensure provider diversity
            min_quality: Minimum quality score threshold
            
        Returns:
            List of recommended models sorted by suitability.
        """
        try:
            # Filter by use case and quality
            candidates = self.filter_models_by_use_case([use_case])
            high_quality = [m for m in candidates if m.get('quality_score', 0) >= min_quality]
            
            if diversity_providers:
                # Ensure provider diversity
                selected_models = []
                used_providers = set()
                
                # Sort by quality score (descending)
                sorted_candidates = sorted(high_quality, 
                                         key=lambda x: x.get('quality_score', 0), reverse=True)
                
                for model in sorted_candidates:
                    provider = model.get('provider_category')
                    if provider not in used_providers or len(selected_models) < max_models:
                        selected_models.append(model)
                        used_providers.add(provider)
                        if len(selected_models) >= max_models:
                            break
                
                return selected_models
            else:
                # Just return top models by quality
                sorted_models = sorted(high_quality, 
                                     key=lambda x: x.get('quality_score', 0), reverse=True)
                return sorted_models[:max_models]
                
        except Exception:
            # Fallback to basic model list
            basic_models = self.get_model_names()
            return [{"id": model_id, "name": model_id} for model_id in basic_models[:max_models]]


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
        self.base_url = base_url or os.environ.get("GLOBANT_BASE_URL", "https://console.saia.ai/tokens")
        
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
    
    def generate(self, prompt: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response using Globant Enterprise AI.
        
        Args:
            prompt: The input prompt to send to the model.
            parameters: Optional parameters like model, temperature, max_tokens, etc.
            
        Returns:
            The generated text response.
        """
        params = parameters or {}
        
        # Set default parameters if not provided
        if "max_tokens" not in params:
            params["max_tokens"] = 1024
        if "temperature" not in params:
            params["temperature"] = 0.7
        
        # Prepare the API request headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Organization-ID": self.org_id
        }
        
        # Format the request payload (assuming OpenAI-compatible format)
        payload = {
            "model": params.get("model", "gpt-4-turbo"),  # Default to GPT-4 Turbo
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": params["max_tokens"],
            "temperature": params["temperature"]
        }
        
        # Include other parameters if provided
        for key in ["top_p", "presence_penalty", "frequency_penalty", "stop"]:
            if key in params:
                payload[key] = params[key]
        
        # Add Globant-specific parameters if provided
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
            provider: The provider name ("anthropic", "openai", "ollama", "gemini", "openrouter", etc.)
            **kwargs: Additional arguments to pass to the client constructor.
            
        Returns:
            A model API client instance.
            
        Raises:
            ValueError: If the provider is not supported.
        """
        provider = provider.lower()
        
        if provider == "anthropic":
            return AnthropicClient(**kwargs)
        elif provider == "openai":
            return OpenAIClient(**kwargs)
        elif provider == "ollama":
            return OllamaClient(**kwargs)
        elif provider == "gemini":
            return GeminiClient(**kwargs)
        elif provider == "openrouter":
            return OpenRouterClient(**kwargs)
        elif provider == "globant":
            return GlobantEnterpriseClient(**kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")


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
