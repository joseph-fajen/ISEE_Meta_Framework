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

class APIIntegrationError(Exception):
    """Base exception for API integration errors."""
    pass

class ModelAPIClient:
    """Base class for model API clients."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the API client.
        
        Args:
            api_key: API key for authentication. If None, will attempt to load from environment.
        """
        self.api_key = api_key
    
    def generate(self, prompt: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response from the model.
        
        Args:
            prompt: The input prompt to send to the model.
            parameters: Optional parameters to control generation.
            
        Returns:
            The generated text response.
        """
        raise NotImplementedError("Subclasses must implement generate()")
    
    def _handle_error(self, response: requests.Response) -> None:
        """Handle error responses from the API.
        
        Args:
            response: The HTTP response object.
            
        Raises:
            APIIntegrationError: If the API returns an error.
        """
        try:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Unknown API error")
        except (ValueError, KeyError):
            error_message = f"API error: {response.status_code} - {response.text[:100]}"
        
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


class ModelAPIFactory:
    """Factory for creating model API clients."""
    
    @staticmethod
    def create_client(provider: str, **kwargs) -> ModelAPIClient:
        """Create a model API client for the specified provider.
        
        Args:
            provider: The provider name ("anthropic", "openai", "ollama", etc.)
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
        else:
            raise ValueError(f"Unsupported provider: {provider}")


# Example usage:
def test_api_integration():
    """Test the API integration with a simple prompt."""
    # Load API keys from environment variables
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
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
        print("- Anthropic API key in environment variable")
        print("- OpenAI API key in environment variable")
        print("- Ollama running locally (http://localhost:11434)")


if __name__ == "__main__":
    test_api_integration()
