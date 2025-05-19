"""
Cost and Time Estimation Module for ISEE Framework

This module provides functionality to estimate API costs and execution time
based on parameter selections in the ISEE Command Wizard.

Part of the UX Enhancement Roadmap - Step 1.1: Cost and Time Estimation
"""

from typing import Dict, Any, List, Optional, Tuple, Union
import math
import json
import os
from pathlib import Path

# Token counting
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

# Constants for cost estimation
# Based on publicly available pricing as of May 2024, adjust as needed
MODEL_COSTS = {
    # Anthropic Claude models (per 1M input tokens / 1M output tokens in USD)
    "claude-3-opus-20240229": {"input": 15, "output": 75},
    "claude-3-sonnet-20240229": {"input": 3, "output": 15},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    
    # OpenAI GPT models (per 1M tokens in USD)
    "gpt-4-turbo": {"input": 10, "output": 30},
    "gpt-4": {"input": 30, "output": 60},
    "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
    
    # Google Gemini models (per 1M tokens in USD)
    "models/gemini-1.5-pro": {"input": 3.5, "output": 10.5},
    "models/gemini-1.0-pro": {"input": 3.5, "output": 10.5},
    
    # Default rates for unknown models
    "default-large": {"input": 10, "output": 30},
    "default-medium": {"input": 3, "output": 15},
    "default-small": {"input": 0.5, "output": 1.5},
    
    # Ollama models have no direct cost (they run locally)
    "ollama": {"input": 0, "output": 0}
}

# Map from model aliases to actual model costs
MODEL_ALIASES = {
    # Anthropic models
    "claude-3-opus": "claude-3-opus-20240229",
    "claude-3-sonnet": "claude-3-sonnet-20240229", 
    "claude-3-haiku": "claude-3-haiku-20240307",
    
    # OpenAI models
    "gpt-4-0125-preview": "gpt-4-turbo",
    "gpt-4-1106-preview": "gpt-4-turbo",
    "gpt-3.5-turbo-0125": "gpt-3.5-turbo",
    
    # Google models
    "gemini-pro": "models/gemini-1.0-pro",
    
    # Ollama models (all zero cost)
    "llama2": "ollama",
    "llama3": "ollama",
    "mistral": "ollama",
    "mixtral": "ollama",
    "phi3": "ollama",
    "codellama": "ollama"
}

# Approximate token sizes for prompt components
PROMPT_TOKEN_SIZES = {
    "short_query": 25,       # ~25 tokens for a short query
    "medium_query": 50,      # ~50 tokens for a medium query
    "long_query": 100,       # ~100 tokens for a long query
    "instruction": 150,      # ~150 tokens for an instruction template
    "domain_context": 50,    # ~50 tokens for domain context
    "system_overhead": 100,  # ~100 tokens for system overhead
}

# Average tokens per minute for model processing
MODEL_PROCESSING_SPEEDS = {
    "claude-3-opus-20240229": 3000,  # Tokens per minute
    "claude-3-sonnet-20240229": 4000,
    "claude-3-haiku-20240307": 5000,
    "gpt-4-turbo": 4000,
    "gpt-4": 3000,
    "gpt-3.5-turbo": 6000,
    "models/gemini-1.5-pro": 4000,
    "models/gemini-1.0-pro": 4000,
    
    # Ollama processing speeds vary by hardware
    "llama3:8b": 4000,      # Estimated on consumer hardware
    "mistral:7b": 4000,
    "mixtral:8x7b": 2000,   # Slower due to model size
    "phi3:mini": 5000,      # Faster due to smaller size
    
    # Defaults for model categories
    "default-large": 3000,
    "default-medium": 4000,
    "default-small": 5000
}

# Cost warnings thresholds (in USD)
COST_WARNING_THRESHOLDS = {
    "notice": 0.5,     # $0.50 - Just a notice
    "warning": 2.0,    # $2.00 - Warning level
    "high": 10.0,      # $10.00 - High cost warning
    "very_high": 50.0  # $50.00 - Very high cost warning
}

# Time warnings thresholds (in minutes)
TIME_WARNING_THRESHOLDS = {
    "notice": 2,      # 2 minutes - Just a notice
    "warning": 5,     # 5 minutes - Warning level
    "high": 15,       # 15 minutes - High time warning
    "very_high": 60   # 60 minutes - Very high time warning
}


class CostEstimator:
    """Estimates API costs and execution time for ISEE commands."""
    
    def __init__(self):
        """Initialize the cost estimator."""
        self.models_info = self._load_models_info()
    
    def _load_models_info(self) -> Dict[str, Dict[str, Any]]:
        """Load models information from configuration files.
        
        Returns:
            Dictionary mapping model IDs to model information.
        """
        models_info = {}
        
        # Look for configuration files
        config_files = []
        try:
            for file in os.listdir():
                if file.endswith('.json') and ('config' in file.lower()):
                    config_files.append(file)
        except Exception:
            # If directory listing fails, use fallback model info
            return self._get_fallback_models_info()
        
        # Try to load models from configuration files
        for config_file in config_files:
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Process models in the config file
                if "models" in config:
                    # Check if models is a dictionary with sections or a flat list
                    if isinstance(config["models"], dict):
                        if "api_models" in config["models"]:
                            for model in config["models"]["api_models"]:
                                models_info[model.get("id")] = model
                        
                        if "ollama_models" in config["models"]:
                            for model in config["models"]["ollama_models"]:
                                models_info[model.get("id")] = model
                    else:
                        # Handle flat list of models
                        for model in config["models"]:
                            models_info[model.get("id")] = model
            except Exception:
                # Skip files with errors
                continue
        
        # If no models were found, use fallback model info
        if not models_info:
            return self._get_fallback_models_info()
        
        return models_info
    
    def _get_fallback_models_info(self) -> Dict[str, Dict[str, Any]]:
        """Provide fallback model information when config files are not available.
        
        Returns:
            Dictionary mapping model IDs to model information.
        """
        return {
            "anthropic_claude": {
                "id": "anthropic_claude",
                "name": "Claude 3 Sonnet",
                "provider": "anthropic",
                "parameters": {"model": "claude-3-sonnet-20240229"}
            },
            "openai_gpt4": {
                "id": "openai_gpt4",
                "name": "GPT-4 Turbo",
                "provider": "openai",
                "parameters": {"model": "gpt-4-turbo"}
            },
            "openai_gpt35": {
                "id": "openai_gpt35",
                "name": "GPT-3.5 Turbo",
                "provider": "openai",
                "parameters": {"model": "gpt-3.5-turbo"}
            },
            "google_gemini": {
                "id": "google_gemini",
                "name": "Gemini 1.5 Pro",
                "provider": "google",
                "parameters": {"model": "models/gemini-1.5-pro"}
            },
            "ollama_llama3": {
                "id": "ollama_llama3",
                "name": "Llama 3 (8B)",
                "provider": "ollama",
                "parameters": {"model": "llama3:8b"}
            }
        }
    
    def _get_model_cost_rate(self, model_info: Dict[str, Any]) -> Dict[str, float]:
        """Get the cost rate for a model.
        
        Args:
            model_info: Model information dictionary.
            
        Returns:
            Dictionary with input and output token costs per 1M tokens.
        """
        # Extract model name from parameters
        model_params = model_info.get("parameters", {})
        model_name = model_params.get("model", "")
        
        # Check if we have exact match for the model
        if model_name in MODEL_COSTS:
            return MODEL_COSTS[model_name]
        
        # Check if we have an alias for the model
        for alias, target in MODEL_ALIASES.items():
            if alias in model_name.lower():
                return MODEL_COSTS[target]
        
        # Use provider-based fallback
        provider = model_info.get("provider", "").lower()
        if provider == "anthropic":
            return MODEL_COSTS["default-medium"]  # Medium cost model
        elif provider == "openai":
            if "gpt-4" in model_name.lower():
                return MODEL_COSTS["default-large"]  # Large cost model
            else:
                return MODEL_COSTS["default-small"]  # Small cost model
        elif provider == "google":
            return MODEL_COSTS["default-medium"]  # Medium cost model
        elif provider == "ollama":
            return MODEL_COSTS["ollama"]  # Zero cost
        
        # Default fallback
        return MODEL_COSTS["default-medium"]
    
    def _get_model_processing_speed(self, model_info: Dict[str, Any]) -> int:
        """Get the processing speed for a model (tokens per minute).
        
        Args:
            model_info: Model information dictionary.
            
        Returns:
            Processing speed in tokens per minute.
        """
        # Extract model name from parameters
        model_params = model_info.get("parameters", {})
        model_name = model_params.get("model", "")
        
        # Check if we have exact match for the model
        if model_name in MODEL_PROCESSING_SPEEDS:
            return MODEL_PROCESSING_SPEEDS[model_name]
        
        # Use provider-based fallback
        provider = model_info.get("provider", "").lower()
        if provider == "anthropic":
            return MODEL_PROCESSING_SPEEDS["default-medium"]
        elif provider == "openai":
            if "gpt-4" in model_name.lower():
                return MODEL_PROCESSING_SPEEDS["default-large"]
            else:
                return MODEL_PROCESSING_SPEEDS["default-small"]
        elif provider == "google":
            return MODEL_PROCESSING_SPEEDS["default-medium"]
        elif provider == "ollama":
            # Ollama speeds depend on model size and hardware
            if "llama3" in model_name.lower() or "mistral" in model_name.lower():
                return MODEL_PROCESSING_SPEEDS["llama3:8b"]
            elif "mixtral" in model_name.lower():
                return MODEL_PROCESSING_SPEEDS["mixtral:8x7b"]
            elif "phi3" in model_name.lower():
                return MODEL_PROCESSING_SPEEDS["phi3:mini"]
            return MODEL_PROCESSING_SPEEDS["default-medium"]
        
        # Default fallback
        return MODEL_PROCESSING_SPEEDS["default-medium"]
    
    def _estimate_tokens_for_query(self, query: str) -> int:
        """Estimate the number of tokens in a query.
        
        Args:
            query: The query string.
            
        Returns:
            Estimated number of tokens.
        """
        if not query:
            return 0
        
        if TIKTOKEN_AVAILABLE:
            # Use tiktoken for more accurate token counting
            try:
                encoder = tiktoken.get_encoding("cl100k_base")  # Use Claude's encoding
                return len(encoder.encode(query))
            except Exception:
                # Fallback to rough estimation if tiktoken fails
                pass
        
        # Rough estimation: ~1.33 tokens per word
        words = query.split()
        return math.ceil(len(words) * 1.33)
    
    def _estimate_prompt_tokens(self, params: Dict[str, Any]) -> int:
        """Estimate the number of tokens in a prompt.
        
        Args:
            params: Dictionary of command parameters.
            
        Returns:
            Estimated number of tokens.
        """
        query = params.get("query", "")
        
        # Use tiktoken if available
        if query and TIKTOKEN_AVAILABLE:
            query_tokens = self._estimate_tokens_for_query(query)
        else:
            # Rough estimation based on query length
            if not query:
                query_tokens = 0
            elif len(query) < 100:
                query_tokens = PROMPT_TOKEN_SIZES["short_query"]
            elif len(query) < 300:
                query_tokens = PROMPT_TOKEN_SIZES["medium_query"]
            else:
                query_tokens = PROMPT_TOKEN_SIZES["long_query"]
        
        # Add tokens for instruction template and domain context
        instruction_tokens = PROMPT_TOKEN_SIZES["instruction"]
        domain_tokens = PROMPT_TOKEN_SIZES["domain_context"] if params.get("domain") else 0
        system_tokens = PROMPT_TOKEN_SIZES["system_overhead"]
        
        return query_tokens + instruction_tokens + domain_tokens + system_tokens
    
    def _estimate_response_tokens(self, params: Dict[str, Any]) -> int:
        """Estimate the number of tokens in a response.
        
        Args:
            params: Dictionary of command parameters.
            
        Returns:
            Estimated number of tokens.
        """
        # Default response size based on model parameters
        model_params = params.get("parameters", {})
        max_tokens = model_params.get("max_tokens", 1024)
        
        # Responses rarely use full max_tokens
        # Use 85% of max_tokens as a reasonable estimate for average case
        return int(max_tokens * 0.85)
    
    def _get_available_models_for_params(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get the list of available models that would be used based on parameters.
        
        Args:
            params: Dictionary of command parameters.
            
        Returns:
            List of model information dictionaries.
        """
        models_to_use = []
        
        # Check how many models should be used
        models_count = params.get("models", 2)
        
        # Check if we should use Ollama models
        use_ollama = params.get("use_ollama", False)
        
        # Sort models by provider (cloud API vs Ollama)
        cloud_models = []
        ollama_models = []
        
        for model_id, model_info in self.models_info.items():
            provider = model_info.get("provider", "").lower()
            if provider == "ollama":
                ollama_models.append(model_info)
            else:
                cloud_models.append(model_info)
        
        # Select models based on params
        selected_models = []
        
        # Use a balanced approach if balanced_models is set
        if params.get("balanced_models", False):
            # Ensure diversity across providers
            providers_seen = set()
            
            # First, select one model from each provider
            for model in cloud_models + ollama_models:
                provider = model.get("provider", "").lower()
                
                # Only include Ollama models if use_ollama is True
                if provider == "ollama" and not use_ollama:
                    continue
                
                if provider not in providers_seen and len(selected_models) < models_count:
                    selected_models.append(model)
                    providers_seen.add(provider)
            
            # If we need more models, add additional ones
            remaining_slots = models_count - len(selected_models)
            if remaining_slots > 0:
                remaining_models = [m for m in cloud_models + ollama_models if m not in selected_models]
                
                # Only include Ollama models if use_ollama is True
                if not use_ollama:
                    remaining_models = [m for m in remaining_models if m.get("provider", "").lower() != "ollama"]
                
                # Add remaining models up to the requested count
                selected_models.extend(remaining_models[:remaining_slots])
        else:
            # Simple selection: use the first models up to the requested count
            all_models = cloud_models
            
            # Add Ollama models if requested
            if use_ollama:
                all_models.extend(ollama_models)
            
            selected_models = all_models[:models_count]
        
        return selected_models
    
    def estimate_cost(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate the cost and execution time for a command.
        
        Args:
            params: Dictionary of command parameters.
            
        Returns:
            Dictionary with cost and time estimates and warnings.
        """
        # If simulate is enabled, zero cost
        if params.get("simulate", False):
            return {
                "total_cost": 0.0,
                "time_estimate_min": 0.5,
                "time_estimate_max": 1.0,
                "cost_warning_level": None,
                "time_warning_level": None,
                "cost_breakdown": {},
                "time_breakdown": {},
                "token_estimate": 0,
                "combinations_estimate": 0,
                "is_simulation": True
            }
        
        # If dry run is enabled, zero cost
        if params.get("dry_run", False):
            return {
                "total_cost": 0.0,
                "time_estimate_min": 0.1,
                "time_estimate_max": 0.2,
                "cost_warning_level": None,
                "time_warning_level": None,
                "cost_breakdown": {},
                "time_breakdown": {},
                "token_estimate": 0,
                "combinations_estimate": 0,
                "is_dry_run": True
            }
        
        # Get the number of combinations
        combinations = self._estimate_combinations(params)
        
        # Get the available models
        selected_models = self._get_available_models_for_params(params)
        
        # Check if models were found
        if not selected_models:
            # No valid models found, use fallbacks
            selected_models = list(self._get_fallback_models_info().values())
        
        # Calculate token estimates per prompt
        prompt_tokens = self._estimate_prompt_tokens(params)
        response_tokens = self._estimate_response_tokens(params)
        
        # Calculate total tokens and costs per model
        total_cost = 0.0
        total_time_min = 0.0
        total_time_max = 0.0
        cost_breakdown = {}
        time_breakdown = {}
        total_tokens = 0
        
        # Split combinations evenly among models
        combinations_per_model = [combinations // len(selected_models)] * len(selected_models)
        for i in range(combinations % len(selected_models)):
            combinations_per_model[i] += 1
        
        # Calculate cost and time for each model
        for i, model_info in enumerate(selected_models):
            model_id = model_info.get("id", f"model_{i+1}")
            model_name = model_info.get("name", model_id)
            
            # Get cost rate for this model
            cost_rate = self._get_model_cost_rate(model_info)
            
            # Calculate tokens for this model's share of combinations
            model_combinations = combinations_per_model[i]
            
            model_prompt_tokens = prompt_tokens * model_combinations
            model_response_tokens = response_tokens * model_combinations
            model_total_tokens = model_prompt_tokens + model_response_tokens
            
            # Calculate cost in USD
            model_input_cost = (model_prompt_tokens / 1000000) * cost_rate["input"]
            model_output_cost = (model_response_tokens / 1000000) * cost_rate["output"]
            model_cost = model_input_cost + model_output_cost
            
            # Add to total cost
            total_cost += model_cost
            
            # Calculate estimated processing time
            processing_speed = self._get_model_processing_speed(model_info)
            
            # Calculate time for sequential processing (slower bound)
            sequential_time = (model_total_tokens / processing_speed)
            
            # Add overhead for API latency and system processing
            overhead_min = 0.1  # Minimum 6 seconds overhead per combination
            overhead_max = 0.2  # Maximum 12 seconds overhead per combination
            
            model_time_min = sequential_time + (overhead_min * model_combinations)
            model_time_max = sequential_time + (overhead_max * model_combinations)
            
            # Update total time estimates
            total_time_min += model_time_min
            total_time_max += model_time_max
            
            # Add to breakdowns
            cost_breakdown[model_name] = {
                "cost": model_cost,
                "prompt_tokens": model_prompt_tokens,
                "response_tokens": model_response_tokens,
                "total_tokens": model_total_tokens,
                "combinations": model_combinations
            }
            
            time_breakdown[model_name] = {
                "time_min": model_time_min,
                "time_max": model_time_max,
                "tokens_per_minute": processing_speed,
                "combinations": model_combinations
            }
            
            total_tokens += model_total_tokens
        
        # Determine warning levels
        cost_warning_level = None
        for level, threshold in sorted(COST_WARNING_THRESHOLDS.items(), key=lambda x: x[1]):
            if total_cost >= threshold:
                cost_warning_level = level
        
        # Use the max time for warning level determination
        time_warning_level = None
        for level, threshold in sorted(TIME_WARNING_THRESHOLDS.items(), key=lambda x: x[1]):
            if total_time_max >= threshold:
                time_warning_level = level
        
        return {
            "total_cost": round(total_cost, 2),
            "time_estimate_min": round(total_time_min, 2),
            "time_estimate_max": round(total_time_max, 2),
            "cost_warning_level": cost_warning_level,
            "time_warning_level": time_warning_level,
            "cost_breakdown": cost_breakdown,
            "time_breakdown": time_breakdown,
            "token_estimate": total_tokens,
            "combinations_estimate": combinations
        }
    
    def _estimate_combinations(self, params: Dict[str, Any]) -> int:
        """Estimate the number of combinations based on parameters.
        
        Args:
            params: Dictionary of command parameters.
            
        Returns:
            Estimated number of combinations.
        """
        # Extract key parameters
        models_count = params.get("models", 2)
        instructions_count = params.get("instructions", 3)
        variations_count = params.get("variations", 2)
        max_combinations = params.get("max_combinations")
        
        # Calculate the total possible combinations
        total_combinations = models_count * instructions_count * variations_count
        
        # If max_combinations is set, use that as the limit
        if max_combinations is not None and max_combinations > 0:
            return min(total_combinations, max_combinations)
        
        return total_combinations
    
    def get_warning_message(self, estimate: Dict[str, Any]) -> Optional[str]:
        """Get a warning message based on cost and time estimates.
        
        Args:
            estimate: Dictionary with cost and time estimates.
            
        Returns:
            Warning message or None if no warning is needed.
        """
        # Simulation or dry run has no warnings
        if estimate.get("is_simulation") or estimate.get("is_dry_run"):
            return None
        
        cost_warning = estimate.get("cost_warning_level")
        time_warning = estimate.get("time_warning_level")
        total_cost = estimate.get("total_cost", 0)
        time_max = estimate.get("time_estimate_max", 0)
        combinations = estimate.get("combinations_estimate", 0)
        
        warnings = []
        
        # Cost warnings
        if cost_warning == "very_high":
            warnings.append(f"VERY HIGH COST: This operation will cost approximately ${total_cost:.2f} in API calls")
        elif cost_warning == "high":
            warnings.append(f"HIGH COST: This operation will cost approximately ${total_cost:.2f} in API calls")
        elif cost_warning == "warning":
            warnings.append(f"COST WARNING: This operation will cost approximately ${total_cost:.2f} in API calls")
        elif cost_warning == "notice":
            warnings.append(f"COST NOTICE: This operation will cost approximately ${total_cost:.2f} in API calls")
        
        # Time warnings
        if time_warning == "very_high":
            warnings.append(f"VERY LONG EXECUTION: This operation may take up to {math.ceil(time_max)} minutes to complete")
        elif time_warning == "high":
            warnings.append(f"LONG EXECUTION: This operation may take up to {math.ceil(time_max)} minutes to complete")
        elif time_warning == "warning":
            warnings.append(f"TIME WARNING: This operation may take up to {math.ceil(time_max)} minutes to complete")
        elif time_warning == "notice":
            warnings.append(f"TIME NOTICE: This operation may take several minutes to complete")
        
        # Suggestion for reducing cost/time if we have high warnings
        if cost_warning in ["high", "very_high"] or time_warning in ["high", "very_high"]:
            suggestions = []
            
            # If we have many combinations, suggest reducing them
            if combinations > 10:
                suggestions.append(f"Reducing combinations from {combinations} to {combinations // 2} would approximately halve the cost and time")
            
            # Suggest simulation mode for testing
            suggestions.append("Use --simulate flag for testing without incurring API costs")
            
            # Add suggestions to warning
            if suggestions:
                warnings.append("Suggestions:")
                warnings.extend([f"  - {s}" for s in suggestions])
        
        if warnings:
            return "\n".join(warnings)
        
        return None
    
    def get_cost_indicator(self, estimate: Dict[str, Any]) -> str:
        """Get a visual indicator of cost level.
        
        Args:
            estimate: Dictionary with cost and time estimates.
            
        Returns:
            String with a visual indicator of cost level.
        """
        if estimate.get("is_simulation") or estimate.get("is_dry_run"):
            return "🔄 (No API cost - simulation mode)"
        
        cost_warning = estimate.get("cost_warning_level")
        total_cost = estimate.get("total_cost", 0)
        
        if cost_warning == "very_high":
            return f"💰💰💰💰 (${total_cost:.2f})"
        elif cost_warning == "high":
            return f"💰💰💰 (${total_cost:.2f})"
        elif cost_warning == "warning":
            return f"💰💰 (${total_cost:.2f})"
        elif cost_warning == "notice":
            return f"💰 (${total_cost:.2f})"
        else:
            return f"$ (${total_cost:.2f})"
    
    def get_time_indicator(self, estimate: Dict[str, Any]) -> str:
        """Get a visual indicator of time level.
        
        Args:
            estimate: Dictionary with cost and time estimates.
            
        Returns:
            String with a visual indicator of time level.
        """
        if estimate.get("is_simulation") or estimate.get("is_dry_run"):
            return "⏱️ (Quick - simulation mode)"
        
        time_warning = estimate.get("time_warning_level")
        time_min = estimate.get("time_estimate_min", 0)
        time_max = estimate.get("time_estimate_max", 0)
        
        # Format time range
        time_range = f"{math.ceil(time_min)}-{math.ceil(time_max)} min" if time_min != time_max else f"{math.ceil(time_max)} min"
        
        if time_warning == "very_high":
            return f"⏱️⏱️⏱️⏱️ ({time_range})"
        elif time_warning == "high":
            return f"⏱️⏱️⏱️ ({time_range})"
        elif time_warning == "warning":
            return f"⏱️⏱️ ({time_range})"
        elif time_warning == "notice":
            return f"⏱️ ({time_range})"
        else:
            return f"⏱️ (< 2 min)"
