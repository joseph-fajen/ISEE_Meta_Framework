#!/usr/bin/env python3
"""
Simple Globant Enterprise AI API Example
========================================

This script demonstrates the basic usage of Globant's Enterprise AI API
for making single LLM calls. Based on the proven ISEE implementation.

Requirements:
- Valid Globant API key and Organization ID
- Python 3.7+ with requests library

Setup:
1. Get your API credentials from Globant
2. Set environment variables or update the script with your credentials
3. Run: python globant_simple_example.py

Documentation Sources:
- Official Wiki: https://wiki.genexus.com/enterprise-ai/wiki?20
- GitHub Repo: https://github.com/genexuslabs/saia-ingest  
- Supported Models: https://wiki.genexus.com/enterprise-ai/wiki?200,Supported+Chat+Models
- Reasoning Models: https://docs.globant.ai/en/wiki?1168,LLMs+with+Reasoning+Capabilities
"""

import os
import json
import requests
from typing import Dict, Any, Optional

class GlobantSimpleClient:
    """
    Simple client for Globant Enterprise AI API calls.
    
    Based on the working implementation from ISEE Meta Framework.
    """
    
    def __init__(self, api_key: str, org_id: str):
        """
        Initialize the Globant client.
        
        Args:
            api_key: Your Globant API key
            org_id: Your Globant organization ID
        """
        self.api_key = api_key
        self.org_id = org_id
        
        # CRITICAL: Use the correct base URL and endpoint
        # This was discovered through debugging - the console URL won't work!
        self.base_url = "https://api.saia.ai"
        self.chat_endpoint = "/chat/completions"  # NOT /v1/chat/completions
        self.chat_url = f"{self.base_url}{self.chat_endpoint}"
    
    def call_model(self, prompt: str, model: str, **kwargs) -> str:
        """
        Make a single call to a Globant-hosted LLM.
        
        Args:
            prompt: Your text prompt/question
            model: Model in provider/model format (e.g., "anthropic/claude-3-5-haiku-20241022")
            **kwargs: Additional parameters (temperature, max_tokens, reasoning_effort, etc.)
            
        Returns:
            The model's response text
            
        Raises:
            Exception: If the API call fails
            
        Note:
            For reasoning models (o1, o3, o4 series), use reasoning_effort instead of temperature:
            - reasoning_effort: "low" (fastest), "medium" (balanced), "high" (thorough)
        """
        # CRITICAL: Headers must include both Authorization and X-Organization-ID
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json", 
            "X-Organization-ID": self.org_id
        }
        
        # Prepare the request payload (OpenAI-compatible format)
        payload = {
            "model": model,  # MUST be in provider/model format!
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", 1024),
            "temperature": kwargs.get("temperature", 0.7)
        }
        
        # Special handling for reasoning models (o1, o3, o4 series)
        is_reasoning_model = any(series in model.lower() for series in ["o1", "o3", "o4"])
        
        if is_reasoning_model:
            # Reasoning models use different parameters
            payload.pop("temperature", None)  # Remove temperature - not supported
            if "reasoning_effort" in kwargs:
                payload["reasoning_effort"] = kwargs["reasoning_effort"]
            else:
                payload["reasoning_effort"] = "medium"  # Default reasoning effort
            # Use max_completion_tokens instead of max_tokens for some reasoning models
            if "max_completion_tokens" in kwargs:
                payload["max_completion_tokens"] = kwargs["max_completion_tokens"]
                payload.pop("max_tokens", None)
        else:
            # Standard models - add optional parameters
            for param in ["top_p", "presence_penalty", "frequency_penalty", "stop"]:
                if param in kwargs:
                    payload[param] = kwargs[param]
        
        # Always allow reasoning_effort for any model (backward compatibility)
        if "reasoning_effort" in kwargs and not is_reasoning_model:
            payload["reasoning_effort"] = kwargs["reasoning_effort"]
        
        try:
            # Make the API call
            response = requests.post(
                self.chat_url, 
                headers=headers, 
                json=payload, 
                timeout=120
            )
            
            # Check for HTTP errors
            if response.status_code != 200:
                error_detail = ""
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_detail = f": {error_data['error'].get('message', 'Unknown error')}"
                except:
                    pass
                
                raise Exception(f"API call failed with status {response.status_code}{error_detail}")
            
            # Parse the response
            response_data = response.json()
            
            # Check for API-level errors
            if "error" in response_data:
                error_info = response_data["error"]
                error_message = error_info.get("message", "Unknown error")
                error_code = error_info.get("code", "Unknown")
                raise Exception(f"Globant API error {error_code}: {error_message}")
            
            # Extract the response text
            return response_data["choices"][0]["message"]["content"]
            
        except requests.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to parse API response: {str(e)}")


def main():
    """
    Example usage of the Globant client.
    """
    print("Globant Enterprise AI - Simple Example")
    print("=" * 40)
    
    # Get credentials from environment variables
    api_key = os.getenv("GLOBANT_API_KEY")
    org_id = os.getenv("GLOBANT_ORG_ID")
    
    if not api_key or not org_id:
        print("❌ Missing required environment variables:")
        print("   - GLOBANT_API_KEY: Your Globant API key")
        print("   - GLOBANT_ORG_ID: Your Globant organization ID")
        print("\nSet these in your environment or .env file")
        return
    
    # Initialize the client
    client = GlobantSimpleClient(api_key, org_id)
    
    # Example 1: Simple question with Claude 3.5 Haiku
    print("\n🔍 Example 1: Simple question with Claude 3.5 Haiku")
    try:
        response = client.call_model(
            prompt="What are the key benefits of using enterprise AI platforms?",
            model="anthropic/claude-3-5-haiku-20241022",  # Note the provider/model format!
            max_tokens=200,
            temperature=0.7
        )
        print(f"✅ Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 2: Technical question with GPT-4o Mini
    print("\n🔍 Example 2: Technical question with GPT-4o Mini")
    try:
        response = client.call_model(
            prompt="Explain the difference between API authentication and authorization in 2 sentences.",
            model="openai/gpt-4o-mini",
            max_tokens=150,
            temperature=0.5
        )
        print(f"✅ Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 3: Creative task with higher temperature
    print("\n🔍 Example 3: Creative task with Gemini 2.5 Pro")
    try:
        response = client.call_model(
            prompt="Write a haiku about cloud computing.",
            model="vertex_ai/gemini-2.5-pro",
            max_tokens=100,
            temperature=1.0  # Higher temperature for creativity
        )
        print(f"✅ Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 4: Reasoning model with reasoning_effort parameter
    print("\n🔍 Example 4: Complex reasoning with OpenAI o1")
    try:
        response = client.call_model(
            prompt="If you have 3 boxes and 12 balls, and you want to distribute them as evenly as possible, how would you do it and why?",
            model="openai/o1",
            reasoning_effort="high",  # Use high reasoning effort for complex problems
            max_completion_tokens=200  # Use max_completion_tokens for reasoning models
        )
        print(f"✅ Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 5: Another reasoning model with medium effort
    print("\n🔍 Example 5: Analysis task with OpenAI o3-mini") 
    try:
        response = client.call_model(
            prompt="What are the pros and cons of microservices architecture vs monolithic architecture?",
            model="openai/o3-mini",
            reasoning_effort="medium",  # Balanced reasoning effort
            max_completion_tokens=150
        )
        print(f"✅ Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n✅ Examples completed!")
    print("\n📚 Helpful Resources:")
    print("   - Official Wiki: https://wiki.genexus.com/enterprise-ai/wiki?20")
    print("   - GitHub Repo: https://github.com/genexuslabs/saia-ingest")
    print("   - Supported Models: https://wiki.genexus.com/enterprise-ai/wiki?200,Supported+Chat+Models")
    print("   - 🆕 Reasoning Models: https://docs.globant.ai/en/wiki?1168,LLMs+with+Reasoning+Capabilities")


if __name__ == "__main__":
    main()