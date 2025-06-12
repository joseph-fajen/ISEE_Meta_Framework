"""
OpenRouter Rankings Service for ISEE Framework

This service provides dynamic top 20 LLM rankings updates from OpenRouter.ai
with smart caching, user control, and graceful fallback mechanisms.

Features:
- Smart caching with 24-hour refresh cycle
- OpenRouter Models API integration
- User-prompted updates when cache is stale
- Graceful fallback to hardcoded top performers
- Cache status reporting for UI integration
"""

import json
import time
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class RankingsCache:
    """Data structure for rankings cache metadata."""
    models: List[Dict[str, Any]]
    timestamp: float
    source: str  # "openrouter_api", "fallback", "manual"
    api_success: bool
    error_message: Optional[str] = None

class OpenRouterRankingsService:
    """Service for managing OpenRouter model rankings with smart caching."""
    
    def __init__(self, cache_file: str = "data/rankings_cache.json"):
        """Initialize the rankings service.
        
        Args:
            cache_file: Path to the cache file for storing rankings data
        """
        self.cache_file = Path(cache_file)
        self.cache_duration = 24 * 3600  # 24 hours in seconds
        self.stale_threshold = 6 * 3600  # 6 hours - when to show update prompt
        self.logger = logging.getLogger(f"{__name__}.OpenRouterRankingsService")
        
        # Ensure cache directory exists
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Fallback top 20 models (current as of June 2025)
        self.fallback_models = [
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "provider": "OpenAI", "model_param": "openai/gpt-4o-mini", "cost_tier": "budget", "features": ["reasoning", "fast", "cost_effective"], "description": "OpenAI's cost-effective flagship model"},
            {"id": "gemini-2-0-flash", "name": "Gemini 2.0 Flash", "provider": "Google", "model_param": "google/gemini-2.0-flash", "cost_tier": "balanced", "features": ["fast", "multimodal", "reasoning"], "description": "Google's latest fast multimodal model"},
            {"id": "claude-3-7-sonnet", "name": "Claude 3.7 Sonnet", "provider": "Anthropic", "model_param": "anthropic/claude-3.7-sonnet", "cost_tier": "premium", "features": ["reasoning", "analysis", "writing"], "description": "Anthropic's enhanced reasoning model"},
            {"id": "gemini-2-5-pro-preview", "name": "Gemini 2.5 Pro Preview", "provider": "Google", "model_param": "google/gemini-2.5-pro-preview", "cost_tier": "premium", "features": ["reasoning", "multimodal", "large_context"], "description": "Google's next-generation flagship model"},
            {"id": "claude-sonnet-4", "name": "Claude Sonnet 4", "provider": "Anthropic", "model_param": "anthropic/claude-sonnet-4", "cost_tier": "premium", "features": ["reasoning", "analysis", "coding"], "description": "Anthropic's latest generation model"},
            {"id": "deepseek-v3-free", "name": "DeepSeek V3 Free", "provider": "DeepSeek", "model_param": "deepseek/deepseek-v3-0324-free", "cost_tier": "free", "features": ["reasoning", "coding", "free"], "description": "DeepSeek's powerful free reasoning model"},
            {"id": "deepseek-v3", "name": "DeepSeek V3", "provider": "DeepSeek", "model_param": "deepseek/deepseek-v3-0324", "cost_tier": "budget", "features": ["reasoning", "coding", "cost_effective"], "description": "DeepSeek's latest reasoning model"},
            {"id": "gpt-4-1", "name": "GPT-4.1", "provider": "OpenAI", "model_param": "openai/gpt-4.1", "cost_tier": "premium", "features": ["reasoning", "analysis", "latest"], "description": "OpenAI's enhanced GPT-4 model"},
            {"id": "deepseek-r1-free", "name": "DeepSeek R1 Free", "provider": "DeepSeek", "model_param": "deepseek/r1-free", "cost_tier": "free", "features": ["reasoning", "thinking", "free"], "description": "DeepSeek's reasoning model with thinking process"},
            {"id": "llama-3-3-70b", "name": "Llama 3.3 70B", "provider": "Meta", "model_param": "meta-llama/llama-3.3-70b-instruct", "cost_tier": "balanced", "features": ["reasoning", "open_source", "large_context"], "description": "Meta's latest open-source flagship model"},
            {"id": "mistral-nemo", "name": "Mistral Nemo", "provider": "Mistral", "model_param": "mistralai/mistral-nemo", "cost_tier": "budget", "features": ["efficient", "multilingual", "coding"], "description": "Mistral's efficient latest model"},
            {"id": "gemini-2-0-flash-lite", "name": "Gemini 2.0 Flash Lite", "provider": "Google", "model_param": "google/gemini-2.0-flash-lite", "cost_tier": "budget", "features": ["fast", "cost_effective", "multimodal"], "description": "Google's lightweight flash model"},
            {"id": "gemini-1-5-flash-8b", "name": "Gemini 1.5 Flash 8B", "provider": "Google", "model_param": "google/gemini-1.5-flash-8b", "cost_tier": "budget", "features": ["fast", "efficient", "cost_effective"], "description": "Google's efficient 8B parameter model"},
            {"id": "gpt-4-1-mini", "name": "GPT-4.1 Mini", "provider": "OpenAI", "model_param": "openai/gpt-4.1-mini", "cost_tier": "budget", "features": ["reasoning", "cost_effective", "latest"], "description": "OpenAI's cost-effective GPT-4.1 variant"},
            {"id": "claude-3-5-sonnet", "name": "Claude 3.5 Sonnet", "provider": "Anthropic", "model_param": "anthropic/claude-3.5-sonnet", "cost_tier": "premium", "features": ["reasoning", "coding", "analysis"], "description": "Anthropic's proven capable model"},
            {"id": "gemini-1-5-flash", "name": "Gemini 1.5 Flash", "provider": "Google", "model_param": "google/gemini-1.5-flash", "cost_tier": "balanced", "features": ["fast", "reliable", "multimodal"], "description": "Google's reliable flash model"},
            {"id": "gpt-4o", "name": "GPT-4o", "provider": "OpenAI", "model_param": "openai/gpt-4o", "cost_tier": "premium", "features": ["reasoning", "multimodal", "analysis"], "description": "OpenAI's multimodal flagship model"},
            {"id": "claude-3-opus", "name": "Claude 3 Opus", "provider": "Anthropic", "model_param": "anthropic/claude-3-opus", "cost_tier": "premium", "features": ["reasoning", "analysis"], "description": "Anthropic's most capable model"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "provider": "OpenAI", "model_param": "openai/gpt-4-turbo", "cost_tier": "premium", "features": ["reasoning", "large_context"], "description": "OpenAI's turbo model"},
            {"id": "claude-3-haiku", "name": "Claude 3 Haiku", "provider": "Anthropic", "model_param": "anthropic/claude-3-haiku", "cost_tier": "budget", "features": ["fast", "cost_effective"], "description": "Anthropic's fast model"}
        ]
        
        self.logger.info("OpenRouterRankingsService initialized")
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get current cache status and update recommendations.
        
        Returns:
            Dictionary with cache status information
        """
        try:
            cache_data = self._load_cache()
            if not cache_data:
                return {
                    "cache_exists": False,
                    "cache_age_hours": None,
                    "needs_update": True,
                    "is_stale": True,
                    "last_updated": None,
                    "source": "none",
                    "recommendation": "initial_update"
                }
            
            current_time = time.time()
            cache_age_seconds = current_time - cache_data.timestamp
            cache_age_hours = cache_age_seconds / 3600
            
            needs_update = cache_age_seconds > self.cache_duration
            is_stale = cache_age_seconds > self.stale_threshold
            
            # Determine recommendation
            if needs_update:
                recommendation = "auto_update"
            elif is_stale:
                recommendation = "suggest_update"
            else:
                recommendation = "no_update"
            
            return {
                "cache_exists": True,
                "cache_age_hours": round(cache_age_hours, 1),
                "needs_update": needs_update,
                "is_stale": is_stale,
                "last_updated": datetime.fromtimestamp(cache_data.timestamp).isoformat(),
                "source": cache_data.source,
                "api_success": cache_data.api_success,
                "error_message": cache_data.error_message,
                "model_count": len(cache_data.models),
                "recommendation": recommendation
            }
            
        except Exception as e:
            self.logger.error(f"Error getting cache status: {e}")
            return {
                "cache_exists": False,
                "cache_age_hours": None,
                "needs_update": True,
                "is_stale": True,
                "last_updated": None,
                "source": "error",
                "recommendation": "fallback_update",
                "error_message": str(e)
            }
    
    async def get_top_models(self, force_update: bool = False) -> List[Dict[str, Any]]:
        """Get top 20 models with smart caching.
        
        Args:
            force_update: Force update even if cache is fresh
            
        Returns:
            List of top 20 model dictionaries
        """
        try:
            cache_status = self.get_cache_status()
            
            if cache_status["needs_update"] or force_update:
                self.logger.info(f"Updating rankings cache (force_update={force_update})")
                await self._update_rankings()
            
            # Load from cache (either existing or newly updated)
            cache_data = self._load_cache()
            if cache_data and cache_data.models:
                self.logger.info(f"Returning {len(cache_data.models)} models from cache ({cache_data.source})")
                return cache_data.models
            
            # Final fallback
            self.logger.warning("Using fallback models due to cache failure")
            return self.fallback_models
            
        except Exception as e:
            self.logger.error(f"Error getting top models: {e}")
            return self.fallback_models
    
    async def _update_rankings(self) -> bool:
        """Update rankings from OpenRouter API with fallback.
        
        Returns:
            True if successful, False if failed
        """
        try:
            # Try to fetch from OpenRouter API
            models = await self._fetch_from_openrouter()
            
            if models:
                # Success - save to cache
                cache_data = RankingsCache(
                    models=models,
                    timestamp=time.time(),
                    source="openrouter_api",
                    api_success=True
                )
                self._save_cache(cache_data)
                self.logger.info(f"Successfully updated rankings with {len(models)} models from OpenRouter API")
                return True
            else:
                # API failed - use fallback but mark as such
                cache_data = RankingsCache(
                    models=self.fallback_models,
                    timestamp=time.time(),
                    source="fallback",
                    api_success=False,
                    error_message="OpenRouter API returned no models"
                )
                self._save_cache(cache_data)
                self.logger.warning("API failed, updated cache with fallback models")
                return False
                
        except Exception as e:
            # Complete failure - use fallback and log error
            error_msg = f"Failed to update rankings: {str(e)}"
            self.logger.error(error_msg)
            
            cache_data = RankingsCache(
                models=self.fallback_models,
                timestamp=time.time(),
                source="fallback",
                api_success=False,
                error_message=error_msg
            )
            self._save_cache(cache_data)
            return False
    
    async def _fetch_from_openrouter(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch top models from OpenRouter API.
        
        Returns:
            List of model dictionaries or None if failed
        """
        try:
            timeout = aiohttp.ClientTimeout(total=10)  # 10 second timeout
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Try to get models sorted by popularity/usage
                url = "https://openrouter.ai/api/v1/models"
                headers = {
                    "User-Agent": "ISEE-Framework/1.0",
                    "Accept": "application/json"
                }
                
                self.logger.debug(f"Fetching models from OpenRouter API: {url}")
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "data" in data and isinstance(data["data"], list):
                            raw_models = data["data"]
                            
                            # Convert to our format and take top 20
                            converted_models = []
                            for model in raw_models[:20]:  # Take first 20 (hopefully sorted by popularity)
                                converted_model = self._convert_openrouter_model(model)
                                if converted_model:
                                    converted_models.append(converted_model)
                            
                            if converted_models:
                                self.logger.info(f"Successfully fetched {len(converted_models)} models from OpenRouter")
                                return converted_models
                            else:
                                self.logger.warning("No valid models found in OpenRouter response")
                                return None
                        else:
                            self.logger.warning("Invalid response format from OpenRouter API")
                            return None
                    else:
                        self.logger.warning(f"OpenRouter API returned status {response.status}")
                        return None
                        
        except asyncio.TimeoutError:
            self.logger.warning("Timeout fetching from OpenRouter API")
            return None
        except Exception as e:
            self.logger.error(f"Error fetching from OpenRouter API: {e}")
            return None
    
    def _convert_openrouter_model(self, model: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert OpenRouter API model format to our internal format.
        
        Args:
            model: Raw model data from OpenRouter API
            
        Returns:
            Converted model dictionary or None if invalid
        """
        try:
            model_id = model.get("id", "")
            if not model_id:
                return None
            
            # Extract provider from model ID (e.g., "anthropic/claude-3-5-sonnet" -> "Anthropic")
            provider = "Unknown"
            if "/" in model_id:
                provider_key = model_id.split("/")[0]
                provider_map = {
                    "anthropic": "Anthropic",
                    "openai": "OpenAI", 
                    "google": "Google",
                    "meta-llama": "Meta",
                    "mistralai": "Mistral",
                    "deepseek": "DeepSeek",
                    "cohere": "Cohere",
                    "amazon": "Amazon",
                    "microsoft": "Microsoft",
                    "ai21": "AI21",
                    "qwen": "Qwen"
                }
                provider = provider_map.get(provider_key, provider_key.title())
            
            # Determine cost tier from pricing
            cost_tier = "balanced"
            if "pricing" in model and model["pricing"]:
                pricing = model["pricing"]
                prompt_cost = float(pricing.get("prompt", "0"))
                
                if prompt_cost == 0:
                    cost_tier = "free"
                elif prompt_cost < 0.000005:  # Very cheap
                    cost_tier = "budget"
                elif prompt_cost > 0.00005:  # Expensive
                    cost_tier = "premium"
                else:
                    cost_tier = "balanced"
            
            # Extract features from model name and description
            features = []
            model_name = model.get("name", "").lower()
            model_desc = model.get("description", "").lower()
            text_to_search = f"{model_name} {model_desc}"
            
            feature_keywords = {
                "reasoning": ["reasoning", "analysis", "logic"],
                "coding": ["code", "coding", "programming"],
                "multimodal": ["multimodal", "vision", "image"],
                "fast": ["fast", "flash", "quick", "lite"],
                "large_context": ["large context", "long context", "100k", "128k"],
                "creative": ["creative", "writing", "story"],
                "free": ["free"],
                "thinking": ["thinking", "reasoning"]
            }
            
            for feature, keywords in feature_keywords.items():
                if any(keyword in text_to_search for keyword in keywords):
                    features.append(feature)
            
            # Clean up model name
            clean_name = model.get("name", model_id)
            if ":" in clean_name:
                clean_name = clean_name.split(":", 1)[1].strip()
            
            # Generate clean ID for UI
            clean_id = model_id.replace("/", "-").replace(":", "-")
            
            return {
                "id": clean_id,
                "name": clean_name,
                "provider": provider,
                "model_param": model_id,  # Keep original for API calls
                "cost_tier": cost_tier,
                "features": features,
                "description": model.get("description", f"{provider} model"),
                "context_length": model.get("context_length"),
                "max_completion_tokens": model.get("max_completion_tokens"),
                "pricing": model.get("pricing")
            }
            
        except Exception as e:
            self.logger.error(f"Error converting model {model.get('id', 'unknown')}: {e}")
            return None
    
    def _load_cache(self) -> Optional[RankingsCache]:
        """Load rankings from cache file.
        
        Returns:
            RankingsCache object or None if not found/invalid
        """
        try:
            if not self.cache_file.exists():
                return None
            
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
            
            return RankingsCache(
                models=data["models"],
                timestamp=data["timestamp"],
                source=data["source"],
                api_success=data["api_success"],
                error_message=data.get("error_message")
            )
            
        except Exception as e:
            self.logger.error(f"Error loading cache: {e}")
            return None
    
    def _save_cache(self, cache_data: RankingsCache) -> bool:
        """Save rankings to cache file.
        
        Args:
            cache_data: RankingsCache object to save
            
        Returns:
            True if successful, False if failed
        """
        try:
            data = {
                "models": cache_data.models,
                "timestamp": cache_data.timestamp,
                "source": cache_data.source,
                "api_success": cache_data.api_success,
                "error_message": cache_data.error_message
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.debug(f"Cache saved successfully to {self.cache_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving cache: {e}")
            return False