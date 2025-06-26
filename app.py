#!/usr/bin/env python3
"""
ISEE Meta Framework - Web Demo Application
Minimalist web UI for investor demonstrations showcasing the ISEE configuration capabilities.
"""

import os
import json
import subprocess
import threading
import time
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename

# Import existing ISEE components
from cost_estimation import CostEstimator
from cognitive_framework_visualizer import CognitiveFrameworkVisualizer
from openrouter_model_collections import OpenRouterModelCollections
from configuration_dashboard import ConfigurationDashboard, DashboardState
from parameter_context import ParameterContext
from main import ISEEGuardrails
from domain_manager import DomainManager, create_default_domains
from openrouter_rankings_service import OpenRouterRankingsService

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.urandom(24)

# Configure logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('isee_web_demo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ISEEWebDemo:
    """Web demo controller that leverages existing ISEE backend logic"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ISEEWebDemo")
        self.cost_estimator = CostEstimator()
        self.framework_visualizer = CognitiveFrameworkVisualizer()
        self.model_collections = OpenRouterModelCollections()
        self.dashboard = ConfigurationDashboard()
        self.parameter_context = ParameterContext()
        self.guardrails = ISEEGuardrails()
        self.execution_status = {}
        
        # Initialize rankings service
        self.rankings_service = OpenRouterRankingsService()
        
        # Initialize domain manager with real domains
        self.domain_manager = DomainManager()
        self._load_actual_domains()
        
        # Initialize LLM collections
        self.llm_collections = {}
        self._load_llm_collections()
        
        self.logger.info("ISEEWebDemo initialized successfully")
        
    def get_cognitive_frameworks(self, complexity_level: str = "all") -> List[Dict[str, Any]]:
        """Get cognitive frameworks with icons and descriptions"""
        # Handle "all" complexity level by getting all frameworks
        if complexity_level == "all":
            all_frameworks = []
            for level in ["basic", "advanced", "expert"]:
                all_frameworks.extend(self.framework_visualizer.get_frameworks_for_complexity(level))
            frameworks = all_frameworks
        else:
            frameworks = self.framework_visualizer.get_frameworks_for_complexity(complexity_level)
        framework_data = []
        
        framework_icons = {
            "ins_analytical": "🔍",
            "ins_creative": "💡", 
            "ins_critical": "⚖️",
            "ins_integrative": "🔗",
            "ins_pragmatic": "🔧",
            "ins_first_principles": "🧱",
            "ins_systems": "🌐",
            "ins_contrarian": "🔄",
            "ins_historical": "📚",
            "ins_futurist": "🚀"
        }
        
        framework_descriptions = {
            "ins_analytical": "Analytical - Break down problems systematically",
            "ins_creative": "Creative - Generate novel solutions and ideas",
            "ins_critical": "Critical - Evaluate assumptions and evidence",
            "ins_integrative": "Integrative - Synthesize multiple perspectives",
            "ins_pragmatic": "Pragmatic - Focus on practical implementations",
            "ins_first_principles": "First Principles - Reason from fundamental truths",
            "ins_systems": "Systems - Consider holistic relationships",
            "ins_contrarian": "Contrarian - Challenge conventional wisdom",
            "ins_historical": "Historical - Learn from past patterns",
            "ins_futurist": "Futurist - Explore future possibilities"
        }
        
        for framework_id, _ in frameworks:
            framework_data.append({
                "id": framework_id,
                "icon": framework_icons.get(framework_id, "🔍"),
                "name": framework_descriptions.get(framework_id, framework_id),
                "description": framework_descriptions.get(framework_id, framework_id)
            })
        
        return framework_data
    
    def get_individual_models(self, use_cached: bool = True) -> List[Dict[str, Any]]:
        """Get individual LLM models for manual selection.
        
        Args:
            use_cached: Whether to use cached rankings (True) or force update (False)
        """
        try:
            # First, try to get models from the rankings service
            if use_cached:
                # Get models synchronously from cache (fast)
                cache_status = self.rankings_service.get_cache_status()
                if cache_status["cache_exists"] and not cache_status["needs_update"]:
                    cache_data = self.rankings_service._load_cache()
                    if cache_data and cache_data.models:
                        models = cache_data.models.copy()
                        
                        # Add ranking positions to cached models (OpenRouter rankings)
                        for i, model in enumerate(models):
                            model["ranking_position"] = i + 1
                            model["is_top_performer"] = i < 10  # Top 10 get special highlighting
                        
                        # Add dynamic Ollama models to cached rankings
                        try:
                            api_status = self._detect_apis()
                            ollama_models = api_status.get("ollama_models", [])
                            if ollama_models:
                                existing_ids = {m["id"] for m in models}
                                ollama_count = len(models)  # Start Ollama numbering after ranked models
                                for ollama_model in ollama_models:
                                    model_id = ollama_model
                                    if model_id not in existing_ids:
                                        models.append({
                                            "id": model_id,
                                            "name": f"Ollama {model_id}",
                                            "provider": "Ollama",
                                            "model_param": model_id,
                                            "cost_tier": "free",
                                            "features": ["local", "free", "dynamic"],
                                            "description": f"Local Ollama model: {model_id}",
                                            "ranking_position": None,  # Ollama models not ranked
                                            "is_top_performer": False
                                        })
                                        self.logger.debug(f"Added dynamic Ollama model to cached list: {model_id}")
                        except Exception as e:
                            self.logger.error(f"Error adding Ollama models to cached rankings: {e}")
                        
                        self.logger.info(f"Using cached rankings (performance-based order) with Ollama integration: {len(models)} models")
                        return models
            
            # Fallback to config-based models + hardcoded fallback
            self.logger.info("Using fallback model loading approach")
            return self._get_fallback_models()
            
        except Exception as e:
            self.logger.error(f"Error in get_individual_models: {e}")
            return self._get_fallback_models()
    
    def _get_fallback_models(self) -> List[Dict[str, Any]]:
        """Get models from config file and hardcoded fallback list."""
        try:
            with open('openrouter_config.json', 'r') as f:
                config = json.load(f)
            
            models = []
            for model in config.get('models', {}).get('api_models', []):
                # Extract provider from model parameter
                model_param = model.get('parameters', {}).get('model', '')
                provider = model_param.split('/')[0] if '/' in model_param else 'unknown'
                
                # Determine cost tier from features
                cost_tier = model.get('cost_tier', 'medium')
                if cost_tier == 'premium_plus':
                    cost_tier = 'premium'
                
                models.append({
                    "id": model.get('id'),
                    "name": model.get('name'),
                    "provider": provider.title(),
                    "model_param": model_param,
                    "cost_tier": cost_tier,
                    "features": model.get('features', []),
                    "description": f"{provider.title()} model"
                })
            
            # Add top performers to reach 20 models minimum  
            if len(models) < 20:
                # Top 20 performers based on OpenRouter rankings (updated for current performance)
                additional_models = [
                    {
                        "id": "gpt-4o-mini",
                        "name": "GPT-4o Mini",
                        "provider": "OpenAI",
                        "model_param": "openai/gpt-4o-mini",
                        "cost_tier": "budget",
                        "features": ["reasoning", "fast", "cost_effective"],
                        "description": "OpenAI's cost-effective flagship model"
                    },
                    {
                        "id": "gemini-2-0-flash",
                        "name": "Gemini 2.0 Flash",
                        "provider": "Google",
                        "model_param": "google/gemini-2.0-flash",
                        "cost_tier": "balanced",
                        "features": ["fast", "multimodal", "reasoning"],
                        "description": "Google's latest fast multimodal model"
                    },
                    {
                        "id": "claude-3-7-sonnet",
                        "name": "Claude 3.7 Sonnet",
                        "provider": "Anthropic",
                        "model_param": "anthropic/claude-3.7-sonnet",
                        "cost_tier": "premium",
                        "features": ["reasoning", "analysis", "writing"],
                        "description": "Anthropic's enhanced reasoning model"
                    },
                    {
                        "id": "gemini-2-5-pro-preview",
                        "name": "Gemini 2.5 Pro Preview",
                        "provider": "Google",
                        "model_param": "google/gemini-2.5-pro-preview",
                        "cost_tier": "premium",
                        "features": ["reasoning", "multimodal", "large_context"],
                        "description": "Google's next-generation flagship model"
                    },
                    {
                        "id": "claude-sonnet-4",
                        "name": "Claude Sonnet 4",
                        "provider": "Anthropic",
                        "model_param": "anthropic/claude-sonnet-4",
                        "cost_tier": "premium",
                        "features": ["reasoning", "analysis", "coding"],
                        "description": "Anthropic's latest generation model"
                    },
                    {
                        "id": "deepseek-v3-free",
                        "name": "DeepSeek V3 Free",
                        "provider": "DeepSeek",
                        "model_param": "deepseek/deepseek-v3-0324-free",
                        "cost_tier": "free",
                        "features": ["reasoning", "coding", "free"],
                        "description": "DeepSeek's powerful free reasoning model"
                    },
                    {
                        "id": "gemini-2-5-flash-preview",
                        "name": "Gemini 2.5 Flash Preview",
                        "provider": "Google",
                        "model_param": "google/gemini-2.5-flash-preview-04-17",
                        "cost_tier": "balanced",
                        "features": ["fast", "reasoning", "multimodal"],
                        "description": "Google's enhanced flash model preview"
                    },
                    {
                        "id": "deepseek-v3",
                        "name": "DeepSeek V3",
                        "provider": "DeepSeek",
                        "model_param": "deepseek/deepseek-v3-0324",
                        "cost_tier": "budget",
                        "features": ["reasoning", "coding", "cost_effective"],
                        "description": "DeepSeek's latest reasoning model"
                    },
                    {
                        "id": "gpt-4-1",
                        "name": "GPT-4.1",
                        "provider": "OpenAI",
                        "model_param": "openai/gpt-4.1",
                        "cost_tier": "premium",
                        "features": ["reasoning", "analysis", "latest"],
                        "description": "OpenAI's enhanced GPT-4 model"
                    },
                    {
                        "id": "deepseek-r1-free",
                        "name": "DeepSeek R1 Free",
                        "provider": "DeepSeek",
                        "model_param": "deepseek/r1-free",
                        "cost_tier": "free",
                        "features": ["reasoning", "thinking", "free"],
                        "description": "DeepSeek's reasoning model with thinking process"
                    },
                    {
                        "id": "llama-3-3-70b",
                        "name": "Llama 3.3 70B",
                        "provider": "Meta",
                        "model_param": "meta-llama/llama-3.3-70b-instruct",
                        "cost_tier": "balanced",
                        "features": ["reasoning", "open_source", "large_context"],
                        "description": "Meta's latest open-source flagship model"
                    },
                    {
                        "id": "mistral-nemo",
                        "name": "Mistral Nemo",
                        "provider": "Mistral",
                        "model_param": "mistralai/mistral-nemo",
                        "cost_tier": "budget",
                        "features": ["efficient", "multilingual", "coding"],
                        "description": "Mistral's efficient latest model"
                    },
                    {
                        "id": "gemini-2-0-flash-lite",
                        "name": "Gemini 2.0 Flash Lite",
                        "provider": "Google",
                        "model_param": "google/gemini-2.0-flash-lite",
                        "cost_tier": "budget",
                        "features": ["fast", "cost_effective", "multimodal"],
                        "description": "Google's lightweight flash model"
                    },
                    {
                        "id": "gemini-1-5-flash-8b",
                        "name": "Gemini 1.5 Flash 8B",
                        "provider": "Google",
                        "model_param": "google/gemini-1.5-flash-8b",
                        "cost_tier": "budget",
                        "features": ["fast", "efficient", "cost_effective"],
                        "description": "Google's efficient 8B parameter model"
                    },
                    {
                        "id": "gpt-4-1-mini",
                        "name": "GPT-4.1 Mini",
                        "provider": "OpenAI",
                        "model_param": "openai/gpt-4.1-mini",
                        "cost_tier": "budget",
                        "features": ["reasoning", "cost_effective", "latest"],
                        "description": "OpenAI's cost-effective GPT-4.1 variant"
                    },
                    {
                        "id": "gemini-2-5-flash-thinking",
                        "name": "Gemini 2.5 Flash Thinking",
                        "provider": "Google",
                        "model_param": "google/gemini-2.5-flash-preview-05-20-thinking",
                        "cost_tier": "balanced",
                        "features": ["reasoning", "thinking", "analysis"],
                        "description": "Google's thinking-enabled flash model"
                    },
                    {
                        "id": "claude-3-5-sonnet",
                        "name": "Claude 3.5 Sonnet",
                        "provider": "Anthropic",
                        "model_param": "anthropic/claude-3.5-sonnet",
                        "cost_tier": "premium",
                        "features": ["reasoning", "coding", "analysis"],
                        "description": "Anthropic's proven capable model"
                    },
                    {
                        "id": "gemini-1-5-flash",
                        "name": "Gemini 1.5 Flash",
                        "provider": "Google",
                        "model_param": "google/gemini-1.5-flash",
                        "cost_tier": "balanced",
                        "features": ["fast", "reliable", "multimodal"],
                        "description": "Google's reliable flash model"
                    },
                    {
                        "id": "claude-3-7-sonnet-thinking",
                        "name": "Claude 3.7 Sonnet Thinking",
                        "provider": "Anthropic",
                        "model_param": "anthropic/claude-3.7-sonnet-thinking",
                        "cost_tier": "premium",
                        "features": ["reasoning", "thinking", "analysis"],
                        "description": "Anthropic's thinking-enabled reasoning model"
                    },
                    {
                        "id": "gpt-4o",
                        "name": "GPT-4o",
                        "provider": "OpenAI",
                        "model_param": "openai/gpt-4o",
                        "cost_tier": "premium",
                        "features": ["reasoning", "multimodal", "analysis"],
                        "description": "OpenAI's multimodal flagship model"
                    }
                ]
                
                # Add models that aren't already in the config
                existing_ids = {m["id"] for m in models}
                for model in additional_models:
                    if model["id"] not in existing_ids:
                        models.append(model)
            
            # Add dynamic Ollama models if available
            try:
                api_status = self._detect_apis()
                ollama_models = api_status.get("ollama_models", [])
                if ollama_models:
                    existing_ids = {m["id"] for m in models}
                    for ollama_model in ollama_models:
                        # Use the model name directly as the ID (this matches what users select)
                        model_id = ollama_model
                        if model_id not in existing_ids:
                            models.append({
                                "id": model_id,
                                "name": f"Ollama {model_id}",
                                "provider": "Ollama",
                                "model_param": model_id,
                                "cost_tier": "free",
                                "features": ["local", "free", "dynamic"],
                                "description": f"Local Ollama model: {model_id}"
                            })
                            self.logger.debug(f"Added dynamic Ollama model to list: {model_id}")
            except Exception as e:
                self.logger.error(f"Error adding Ollama models: {e}")
            
            # Don't sort - preserve the order from config file which follows top performers list
            # Add fallback ranking metadata for consistency with rankings service
            for i, model in enumerate(models):
                model["ranking_position"] = None  # Config models don't have rankings
                model["is_top_performer"] = i < 10  # First 10 from config get highlighting
            
            return models
            
        except Exception as e:
            print(f"Error loading models: {e}")
            # Fallback to top 20 performers model list with ranking metadata
            fallback_models = [
                {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "provider": "OpenAI", "model_param": "openai/gpt-4o-mini", "cost_tier": "budget", "features": ["reasoning", "fast"], "description": "OpenAI's cost-effective flagship"},
                {"id": "gemini-2-0-flash", "name": "Gemini 2.0 Flash", "provider": "Google", "model_param": "google/gemini-2.0-flash", "cost_tier": "balanced", "features": ["fast", "multimodal"], "description": "Google's latest flash model"},
                {"id": "claude-3-7-sonnet", "name": "Claude 3.7 Sonnet", "provider": "Anthropic", "model_param": "anthropic/claude-3.7-sonnet", "cost_tier": "premium", "features": ["reasoning", "analysis"], "description": "Anthropic's enhanced model"},
                {"id": "gemini-2-5-pro-preview", "name": "Gemini 2.5 Pro Preview", "provider": "Google", "model_param": "google/gemini-2.5-pro-preview", "cost_tier": "premium", "features": ["reasoning", "large_context"], "description": "Google's next-gen flagship"},
                {"id": "claude-sonnet-4", "name": "Claude Sonnet 4", "provider": "Anthropic", "model_param": "anthropic/claude-sonnet-4", "cost_tier": "premium", "features": ["reasoning", "coding"], "description": "Anthropic's latest generation"},
                {"id": "deepseek-v3-free", "name": "DeepSeek V3 Free", "provider": "DeepSeek", "model_param": "deepseek/deepseek-v3-0324-free", "cost_tier": "free", "features": ["reasoning", "free"], "description": "Free powerful reasoning model"},
                {"id": "deepseek-v3", "name": "DeepSeek V3", "provider": "DeepSeek", "model_param": "deepseek/deepseek-v3-0324", "cost_tier": "budget", "features": ["reasoning", "coding"], "description": "DeepSeek's latest model"},
                {"id": "gpt-4-1", "name": "GPT-4.1", "provider": "OpenAI", "model_param": "openai/gpt-4.1", "cost_tier": "premium", "features": ["reasoning", "latest"], "description": "OpenAI's enhanced GPT-4"},
                {"id": "deepseek-r1-free", "name": "DeepSeek R1 Free", "provider": "DeepSeek", "model_param": "deepseek/r1-free", "cost_tier": "free", "features": ["reasoning", "thinking"], "description": "Free reasoning with thinking"},
                {"id": "llama-3-3-70b", "name": "Llama 3.3 70B", "provider": "Meta", "model_param": "meta-llama/llama-3.3-70b-instruct", "cost_tier": "balanced", "features": ["reasoning", "open_source"], "description": "Meta's open-source flagship"},
                {"id": "mistral-nemo", "name": "Mistral Nemo", "provider": "Mistral", "model_param": "mistralai/mistral-nemo", "cost_tier": "budget", "features": ["efficient", "multilingual"], "description": "Mistral's efficient model"},
                {"id": "gemini-2-0-flash-lite", "name": "Gemini 2.0 Flash Lite", "provider": "Google", "model_param": "google/gemini-2.0-flash-lite", "cost_tier": "budget", "features": ["fast", "cost_effective"], "description": "Google's lightweight model"},
                {"id": "gemini-1-5-flash-8b", "name": "Gemini 1.5 Flash 8B", "provider": "Google", "model_param": "google/gemini-1.5-flash-8b", "cost_tier": "budget", "features": ["efficient", "fast"], "description": "Google's 8B parameter model"},
                {"id": "gpt-4-1-mini", "name": "GPT-4.1 Mini", "provider": "OpenAI", "model_param": "openai/gpt-4.1-mini", "cost_tier": "budget", "features": ["reasoning", "cost_effective"], "description": "OpenAI's cost-effective variant"},
                {"id": "claude-3-5-sonnet", "name": "Claude 3.5 Sonnet", "provider": "Anthropic", "model_param": "anthropic/claude-3.5-sonnet", "cost_tier": "premium", "features": ["reasoning", "coding"], "description": "Anthropic's proven model"},
                {"id": "gemini-1-5-flash", "name": "Gemini 1.5 Flash", "provider": "Google", "model_param": "google/gemini-1.5-flash", "cost_tier": "balanced", "features": ["fast", "reliable"], "description": "Google's reliable flash model"},
                {"id": "gpt-4o", "name": "GPT-4o", "provider": "OpenAI", "model_param": "openai/gpt-4o", "cost_tier": "premium", "features": ["reasoning", "multimodal"], "description": "OpenAI's multimodal flagship"},
                {"id": "claude-3-opus", "name": "Claude 3 Opus", "provider": "Anthropic", "model_param": "anthropic/claude-3-opus", "cost_tier": "premium", "features": ["reasoning", "analysis"], "description": "Anthropic's most capable model"},
                {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "provider": "OpenAI", "model_param": "openai/gpt-4-turbo", "cost_tier": "premium", "features": ["reasoning", "large_context"], "description": "OpenAI's turbo model"},
                {"id": "claude-3-haiku", "name": "Claude 3 Haiku", "provider": "Anthropic", "model_param": "anthropic/claude-3-haiku", "cost_tier": "budget", "features": ["fast", "cost_effective"], "description": "Anthropic's fast model"}
            ]
            
            # Add fallback ranking metadata 
            for i, model in enumerate(fallback_models):
                model["ranking_position"] = i + 1  # Fallback models get estimated rankings
                model["is_top_performer"] = i < 10  # Top 10 get highlighting
            
            return fallback_models
    
    def _load_actual_domains(self):
        """Load domains from actual ISEE domain system"""
        # Load default domains (now includes all 15 domains: Core, Technical Writing, and Learning Design)
        for domain in create_default_domains():
            self.domain_manager.add_domain(domain)
    
    def _get_real_domains(self) -> Dict[str, List[Dict[str, str]]]:
        """Get actual domains organized by category with IDs and names"""
        # Convert DomainManager domains to web UI format with IDs
        domains_by_category = {
            "Core Domains": [],
            "Technical Writing": [],
            "Learning Design": [],
        }
        
        # domains is a dictionary, so iterate over values
        for domain in self.domain_manager.domains.values():
            domain_info = {
                "id": domain.id,
                "name": domain.name,
                "description": domain.description
            }
            
            # Categorize domains based on their IDs and source files
            if domain.id in ["domain_technical_writing", "domain_knowledge_management", "domain_content_strategy", "domain_ai_writing", "domain_developer_docs"]:
                domains_by_category["Technical Writing"].append(domain_info)
            elif domain.id in ["domain_instructional_design", "domain_elearning", "domain_learning_experience", "domain_corporate_training", "domain_assessment_design"]:
                domains_by_category["Learning Design"].append(domain_info)
            else:
                # Default domains and others go to Core Domains
                domains_by_category["Core Domains"].append(domain_info)
        
        # Remove empty categories
        return {k: v for k, v in domains_by_category.items() if v}
    
    def get_knowledge_domains(self) -> Dict[str, List[Dict[str, str]]]:
        """Get knowledge domains organized by category with IDs and names"""
        return self._get_real_domains()
    
    def _load_llm_collections(self):
        """Load LLM collections from JSON configuration"""
        try:
            collections_file = Path("llm_collections.json")
            if collections_file.exists():
                with open(collections_file, 'r') as f:
                    collections_data = json.load(f)
                self.llm_collections = collections_data.get("collections", {})
                self.logger.info(f"Loaded {len(self.llm_collections)} LLM collections")
            else:
                self.logger.warning("llm_collections.json not found, using empty collections")
                self.llm_collections = {}
        except Exception as e:
            self.logger.error(f"Error loading LLM collections: {e}")
            self.llm_collections = {}
    
    def get_llm_collections(self) -> Dict[str, Any]:
        """Get LLM collections for the web UI"""
        return self.llm_collections
    
    def resolve_collection_models(self, collection_id: str) -> List[str]:
        """Resolve a collection ID to a list of model IDs"""
        if collection_id not in self.llm_collections:
            self.logger.error(f"Collection '{collection_id}' not found")
            return []
        
        collection = self.llm_collections[collection_id]
        model_ids = []
        
        # Extract model IDs from collection - use model_param for OpenRouter models
        for model in collection.get("models", []):
            # Use model_param (actual OpenRouter ID) for models with "rankings" source
            # Use id (internal config ID) for models with "config" source
            if model.get("source") == "rankings":
                model_ids.append(model["model_param"])
            else:
                model_ids.append(model["id"])
        
        self.logger.info(f"Resolved collection '{collection_id}' to {len(model_ids)} models: {model_ids}")
        return model_ids
    
    def estimate_execution_cost(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate cost and resource requirements for given parameters"""
        try:
            # Create a simple parameter object for cost estimation
            class SimpleParams:
                def __init__(self, params_dict):
                    self._params = params_dict
                    for key, value in params_dict.items():
                        setattr(self, key, value)
                
                def get(self, key, default=None):
                    """Dictionary-like get method for compatibility with cost estimator"""
                    return self._params.get(key, default)
            
            # Convert web parameters to format expected by cost estimator
            converted_params = self._convert_web_params_to_isee(parameters)
            param_obj = SimpleParams(converted_params)
            
            # Get cost estimate using existing logic
            estimate = self.cost_estimator.estimate_cost(param_obj)
            
            # Add resource guardrails check
            limits_check = self.guardrails.validate_command_limits(param_obj)
            
            return {
                **estimate,
                "guardrails": limits_check,
                "resource_warnings": limits_check.get("warnings", []),
                "within_limits": limits_check.get("within_limits", True)
            }
        except Exception as e:
            # Log the actual error for debugging
            self.logger.error(f"Cost estimation failed, falling back to simplified calculation: {str(e)}")
            self.logger.debug(f"Parameters that caused error: {parameters}")
            
            # Fallback calculation for demo
            combinations = parameters.get("max_combinations", 24)
            cost_per_combination = 0.08
            return {
                "total_cost": combinations * cost_per_combination,
                "time_estimate_min": combinations * 0.5,
                "time_estimate_max": combinations * 1.2,
                "combinations_estimate": combinations,
                "cost_warning_level": "notice" if combinations <= 50 else "warning",
                "resource_warnings": ["Demo mode: Using simplified cost calculation"],
                "within_limits": combinations <= 100
            }
    
    def generate_command_preview(self, parameters: Dict[str, Any]) -> str:
        """Generate the terminal command that would be executed"""
        import shlex
        
        cmd_parts = ["python", "main.py"]
        
        # Add query (properly escaped)
        if parameters.get("query"):
            cmd_parts.extend(["--query", parameters["query"]])
        
        # Add selected domains (properly escaped)
        selected_domains = parameters.get("selected_domains", [])
        if selected_domains:
            # Add multiple --domain flags for accurate command preview
            for domain in selected_domains:
                cmd_parts.extend(["--domain", domain])
        
        # Add cognitive frameworks
        frameworks = parameters.get("cognitive_frameworks", [])
        if frameworks:
            framework_list = ",".join(frameworks)
            cmd_parts.extend(["--instruction-templates", framework_list])
        
        # Add model configuration - handle both collections and individual selection
        selected_models = parameters.get("selected_models", [])
        
        # Check for collection selection first (same logic as execution)
        if parameters.get("selected_collection"):
            collection_id = parameters["selected_collection"]
            collection_models = self.resolve_collection_models(collection_id)
            if collection_models:
                selected_models = collection_models
                self.logger.debug(f"Preview: Using collection '{collection_id}' with {len(collection_models)} models")
            else:
                self.logger.warning(f"Preview: Collection '{collection_id}' resolution failed")
        
        if selected_models:
            # Process model parameters (same as execution)
            processed_models = self._process_model_params(selected_models)
            
            # Determine config based on model types (same logic as execution)
            api_status = self._detect_apis()
            ollama_models = api_status.get("ollama_models", [])
            # Use consolidated OpenRouter config for all model combinations (per June 2025 config consolidation)
            cmd_parts.extend(["--config", "openrouter_config.json"])
            
            cmd_parts.extend(["--models", str(len(processed_models))])
            # Add processed models to preview
            cmd_parts.extend(["--selected-models", ",".join(processed_models)])
        
        # Add execution settings
        if parameters.get("variations"):
            cmd_parts.extend(["--variations", str(parameters["variations"])])
        
        if parameters.get("max_combinations"):
            cmd_parts.extend(["--max-combinations", str(parameters["max_combinations"])])
        
        # Sampling method removed - now uses optimal default (exhaustive + balanced-models)
        
        # Add output format
        if parameters.get("output_format") and parameters["output_format"] != "json":
            cmd_parts.extend(["--output-format", parameters["output_format"]])
        
        # Note: No dry-run flag added - show the actual command that will be executed
        
        # Properly escape the command for shell display
        return " ".join(shlex.quote(part) for part in cmd_parts)
    
    def execute_isee_command(self, parameters: Dict[str, Any], execution_id: str, session_api_key: str = None) -> Dict[str, Any]:
        """Execute ISEE command and track progress"""
        self.logger.info(f"Starting execution {execution_id} with parameters: {parameters}")
        
        # Store execution parameters for performance tracking
        if not hasattr(self, 'execution_parameters'):
            self.execution_parameters = {}
        self.execution_parameters[execution_id] = parameters.copy()
        
        try:
            # Validate parameters before execution
            validation_errors = self._validate_parameters(parameters)
            if validation_errors:
                error_message = "Parameter validation failed: " + "; ".join(validation_errors)
                self.logger.error(f"Validation failed for execution {execution_id}: {validation_errors}")
                self.execution_status[execution_id] = {
                    "status": "error",
                    "progress": 0,
                    "message": error_message,
                    "start_time": datetime.now().isoformat(),
                    "results_file": None,
                    "validation_errors": validation_errors
                }
                return self.execution_status[execution_id]
            
            # Update status
            self.execution_status[execution_id] = {
                "status": "starting",
                "progress": 0,
                "message": "Preparing execution...",
                "start_time": datetime.now().isoformat(),
                "results_file": None
            }
            
            # Convert Web UI parameters to format expected by ISEE backend
            converted_params = self._convert_web_params_to_isee(parameters)
            self.logger.debug(f"Converted parameters: {converted_params}")
            
            # Build command properly for subprocess using converted parameters
            cmd = ["python", "main.py"]
            self.logger.debug(f"Building command for execution {execution_id}")
            
            # Add query (properly handled)
            if converted_params.get("query"):
                cmd.extend(["--query", converted_params["query"]])
                self.logger.debug(f"Added query: {converted_params['query'][:100]}...")
            
            # Add selected domains (support both single domain and multiple domains)
            domain = converted_params.get("domain")
            selected_domains = converted_params.get("domains", [])
            
            if selected_domains:
                # Add multiple domain flags for execution
                for domain_id in selected_domains:
                    cmd.extend(["--domain", domain_id])
            elif domain:
                cmd.extend(["--domain", domain])
            
            # Add cognitive frameworks - use converted framework IDs instead of Web UI names
            if converted_params.get("instruction_templates"):
                cmd.extend(["--instruction-templates", converted_params["instruction_templates"]])
                self.logger.debug(f"Added framework templates: {converted_params['instruction_templates']}")
            
            # Add model configuration - Always use openrouter_config.json (consolidated config)
            selected_models = converted_params.get("selected_models", [])
            if selected_models:
                self.logger.debug(f"Selected models: {selected_models}")
                
                # Process model parameters (now receiving OpenRouter model params directly)
                processed_models = self._process_model_params(selected_models)
                self.logger.debug(f"Processed models: {processed_models}")
                
                # Use consolidated OpenRouter config for all model combinations
                config_file = "openrouter_config.json"
                cmd.extend(["--config", config_file])
                self.logger.debug(f"Using consolidated config file: {config_file}")
                
                # Pass specific model selections to CLI using processed model params
                cmd.extend(["--selected-models", ",".join(processed_models)])
                cmd.extend(["--models", str(len(processed_models))])
                self.logger.debug(f"Added {len(processed_models)} specific models to command")
            
            # Add execution settings using converted parameters
            if converted_params.get("variations"):
                cmd.extend(["--variations", str(converted_params["variations"])])
            
            if converted_params.get("max_combinations"):
                cmd.extend(["--max-combinations", str(converted_params["max_combinations"])])
            
            # Sampling method removed - now uses optimal default (exhaustive + balanced-models)
            
            # Add output format
            if converted_params.get("output_format") and converted_params["output_format"] != "json":
                cmd.extend(["--output-format", converted_params["output_format"]])
            
            # Always generate comprehensive result package for Web UI
            cmd.append("--generate-reports")
            cmd.append("--export-csv") 
            cmd.append("--analyze-results")
            cmd.append("--json-progress")  # Enable structured progress output
            
            # Add report format if specified
            if converted_params.get("report_format") and converted_params["report_format"] != "markdown":
                cmd.extend(["--report-format", converted_params["report_format"]])
                
            # Only add no-visualizations if explicitly requested
            if converted_params.get("no_visualizations"):
                cmd.append("--no-visualizations")
            
            # Check if we should use real execution or simulation
            # Use real execution if we have API keys available
            current_api_status = self._detect_apis_with_session_key(session_api_key)
            if not current_api_status.get("any_api", False):
                cmd.append("--simulate")  # Use simulation if no API keys
            
            # Create timestamped run directory (matching CLI behavior)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            run_dir = Path("data/output") / f"run_{timestamp}"
            run_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine file extension based on output format (following main.py logic)
            output_format = converted_params.get("output_format", "json")
            if output_format == "markdown":
                extension = "md"
            else:
                extension = "json"
            
            # Use standard filename in run directory
            output_file = run_dir / f"isee_result.{extension}"
            cmd.extend(["--output-file", str(output_file)])
            
            # Force CLI to use the same output directory for all reports
            cmd.extend(["--output-directory", str(run_dir)])
            
            # Store run directory for generating additional reports
            self.execution_status[execution_id]["run_directory"] = str(run_dir)
            
            # Update status
            self.execution_status[execution_id].update({
                "status": "running",
                "progress": 10,
                "message": "Executing ISEE framework...",
                "command": " ".join(cmd)
            })
            
            # Prepare environment with session API keys
            env = os.environ.copy()
            
            # Add session-stored OpenRouter API key if available
            if session_api_key:
                env['OPENROUTER_API_KEY'] = session_api_key
                self.logger.debug("Added OpenRouter API key from session to environment")
            
            # Force Python to be unbuffered for real-time progress monitoring
            env['PYTHONUNBUFFERED'] = '1'
            
            # Log command execution details
            self.logger.info(f"Executing command: {' '.join(cmd)}")
            self.logger.debug(f"Working directory: {Path(__file__).parent}")
            self.logger.debug(f"Environment variables set: {[k for k in env.keys() if 'API_KEY' in k]}")
            
            # Execute command with unbuffered output for real-time monitoring
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True,
                cwd=Path(__file__).parent,
                env=env
            )
            
            self.logger.info(f"Started subprocess with PID {process.pid} for execution {execution_id}")
            
            # Monitor progress and wait for completion
            stdout, stderr = self._monitor_subprocess_progress(process, execution_id)
            
            if process.returncode == 0:
                self.logger.info(f"Execution {execution_id} completed successfully")
                
                # Auto-ingest performance data into database
                run_directory = self.execution_status[execution_id].get("run_directory", "")
                if run_directory:
                    try:
                        from performance_tracker import PerformanceTracker
                        tracker = PerformanceTracker()
                        
                        # Get collection name from parameters
                        collection_name = "Unknown Collection"
                        if hasattr(self, 'execution_parameters') and execution_id in self.execution_parameters:
                            params = self.execution_parameters[execution_id]
                            if params.get("selected_collection"):
                                collection_id = params["selected_collection"]
                                collection_names = {
                                    "premium": "Premium Diversity",
                                    "reliable": "Reliable Exploration", 
                                    "experimental": "Experimental Innovation",
                                    "free": "Free Cognitive Diversity"
                                }
                                collection_name = collection_names.get(collection_id, collection_id.title())
                        
                        # Ingest performance data
                        success = tracker.ingest_test_run(run_directory, collection_name)
                        if success:
                            self.logger.info(f"Performance data automatically captured for {collection_name}")
                        else:
                            self.logger.warning(f"Failed to capture performance data for {execution_id}")
                            
                    except Exception as e:
                        self.logger.error(f"Error auto-ingesting performance data: {e}")
                
                # Enhanced completion message with file location details
                completion_message = "Execution completed successfully! Results saved to timestamped directory:"
                if run_directory:
                    completion_message += f"\n📁 Directory: {run_directory}"
                    completion_message += f"\n📄 Main Results: {os.path.basename(str(output_file))}"
                    completion_message += f"\n📊 Additional Files: run_summary.md, analysis.md, CSV exports, visualizations"
                    completion_message += f"\n🗄️ Performance data automatically captured in database"
                
                self.execution_status[execution_id].update({
                    "status": "completed",
                    "progress": 100,
                    "message": completion_message,
                    "results_file": str(output_file),
                    "run_directory": run_directory,
                    "end_time": datetime.now().isoformat(),
                    "stdout": stdout,
                    "stderr": stderr
                })
            else:
                # Use enhanced error analysis
                error_message = self._analyze_execution_error(stderr, process.returncode, execution_id)
                self.logger.error(f"Execution {execution_id} failed with return code {process.returncode}")
                self.execution_status[execution_id].update({
                    "status": "error",
                    "progress": 0,
                    "message": error_message,
                    "end_time": datetime.now().isoformat(),
                    "error": stderr,
                    "return_code": process.returncode
                })
        
        except Exception as e:
            self.logger.exception(f"Unexpected error during execution {execution_id}: {e}")
            self.execution_status[execution_id].update({
                "status": "error",
                "progress": 0,
                "message": f"Unexpected execution error: {str(e)}",
                "end_time": datetime.now().isoformat(),
                "error": str(e),
                "exception": str(e)
            })
        
        return self.execution_status[execution_id]
    
    def _validate_parameters(self, parameters: Dict[str, Any]) -> List[str]:
        """Validate web UI parameters before execution"""
        errors = []
        
        # Validate required parameters
        if not parameters.get("query") or not parameters.get("query").strip():
            errors.append("Query is required and cannot be empty")
            
        # Validate model selections - accept either individual models or collections
        selected_models = parameters.get("selected_models", [])
        selected_collection = parameters.get("selected_collection")
        
        if not selected_models and not selected_collection:
            errors.append("At least one model or collection must be selected")
        elif selected_collection and selected_collection not in self.llm_collections:
            errors.append(f"Invalid collection '{selected_collection}' - must be one of: {list(self.llm_collections.keys())}")
        elif selected_models and len(selected_models) > 20:
            errors.append("Maximum 20 models can be selected at once")
            
        # Validate variations
        variations = parameters.get("variations")
        if variations is not None:
            try:
                variations_int = int(variations)
                if variations_int < 0 or variations_int > 5:
                    errors.append("Variations must be between 0 and 5")
            except (ValueError, TypeError):
                errors.append("Variations must be a valid number")
                
        # Validate max combinations
        max_combinations = parameters.get("max_combinations")
        if max_combinations is not None:
            try:
                max_combinations_int = int(max_combinations)
                if max_combinations_int < 1 or max_combinations_int > 1000:
                    errors.append("Max combinations must be between 1 and 1000")
            except (ValueError, TypeError):
                errors.append("Max combinations must be a valid number")
                
        # Sampling method validation removed - now uses optimal default configuration
            
        # Validate output format
        output_format = parameters.get("output_format")
        valid_output_formats = ["markdown", "json"]
        if output_format and output_format not in valid_output_formats:
            errors.append(f"Output format must be one of: {', '.join(valid_output_formats)}")
            
        # Validate report format
        report_format = parameters.get("report_format")
        valid_report_formats = ["markdown", "json"]
        if report_format and report_format not in valid_report_formats:
            errors.append(f"Report format must be one of: {', '.join(valid_report_formats)}")
            
        # Validate cognitive frameworks
        frameworks = parameters.get("cognitive_frameworks", [])
        if frameworks and len(frameworks) > 10:
            errors.append("Maximum 10 cognitive frameworks can be selected")
            
        return errors

    def _convert_web_params_to_isee(self, web_params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert web UI parameters to format expected by ISEE backend"""
        converted = {}
        
        # Core parameter mapping
        param_mapping = {
            "query": "query",
            "variations": "variations", 
            "max_combinations": "max_combinations",
            # "sampling_method": removed - simplified to optimal default
            "output_format": "output_format",
            "generate_reports": "generate_reports",
            "report_format": "report_format", 
            "export_csv": "export_csv",
            "analyze_results": "analyze_results",
            "no_visualizations": "no_visualizations"
        }
        
        for web_key, isee_key in param_mapping.items():
            if web_key in web_params and web_params[web_key] is not None:
                converted[isee_key] = web_params[web_key]
        
        # Handle domain selection - BULLETPROOF direct mapping only (no fuzzy search)
        domain_ids = []
        if web_params.get("selected_domains"):
            # Process selected domains from Web UI using direct mapping
            for domain_identifier in web_params["selected_domains"]:
                # Check if it's already a domain ID (starts with 'domain_')
                if domain_identifier.startswith('domain_'):
                    # Direct domain ID mapping (bulletproof)
                    if domain_identifier in self.domain_manager.domains:
                        domain_ids.append(domain_identifier)
                        self.logger.debug(f"Direct ID mapping for '{domain_identifier}'")
                    else:
                        self.logger.error(f"Invalid domain ID '{domain_identifier}' - domain not found")
                else:
                    # Legacy name-to-ID mapping for backward compatibility
                    all_domains = self.domain_manager.list_domains()
                    exact_matches = [d for d in all_domains if d.name.lower() == domain_identifier.lower()]
                    
                    if exact_matches:
                        # Use exact match only (no fuzzy search fallback)
                        domain_ids.extend([d.id for d in exact_matches])
                        self.logger.debug(f"Exact name match for '{domain_identifier}' to ID: {exact_matches[0].id}")
                    else:
                        self.logger.error(f"No exact match found for domain '{domain_identifier}' - rejecting (no fuzzy fallback)")
            
            if domain_ids:
                # Remove duplicates while preserving order
                unique_domain_ids = list(dict.fromkeys(domain_ids))
                converted["domains"] = unique_domain_ids
                converted["domain"] = unique_domain_ids[0]  # Keep single domain for backward compatibility
        elif web_params.get("domain"):
            # Handle single domain selection
            domain_name = web_params["domain"]
            matching_domains = self.domain_manager.search_domains(domain_name)
            if matching_domains:
                domain_ids = [matching_domains[0].id]
                converted["domain"] = domain_ids[0]
                self.logger.debug(f"Resolved single domain '{domain_name}' to ID: {domain_ids[0]}")
            else:
                self.logger.warning(f"No matching domain found for '{domain_name}', using as-is")
                converted["domain"] = domain_name
        
        # Fallback if no domains were resolved
        if not domain_ids and not web_params.get("domain"):
            # Default to Education domain
            converted["domain"] = "domain_education"
            self.logger.debug("No domains specified, defaulting to Education")
        
        # Handle cognitive frameworks
        if web_params.get("cognitive_frameworks"):
            converted["instructions"] = len(web_params["cognitive_frameworks"])
            # Convert Web UI framework names to backend template IDs
            framework_mapping = {
                "Analytical Framework": "ins_analytical",
                "Creative Framework": "ins_creative", 
                "Critical Framework": "ins_critical",
                "Integrative Framework": "ins_integrative",
                "Pragmatic Framework": "ins_pragmatic",
                "First Principles Framework": "ins_first_principles",
                "Systems Thinking Framework": "ins_systems",
                "Contrarian Framework": "ins_contrarian",
                "Historical Framework": "ins_historical",
                "Future-Oriented Framework": "ins_futurist"
            }
            
            # Map Web UI framework names to backend IDs
            mapped_frameworks = []
            for framework in web_params["cognitive_frameworks"]:
                if framework in framework_mapping:
                    mapped_frameworks.append(framework_mapping[framework])
                else:
                    self.logger.warning(f"Unknown framework: {framework}")
                    # Keep original name as fallback
                    mapped_frameworks.append(framework)
            
            # Convert list to comma-separated string as expected by guardrails
            converted["instruction_templates"] = ",".join(mapped_frameworks)
        else:
            # Default to 3 instructions if not specified
            converted["instructions"] = 3
            converted["instruction_templates"] = None
        
        # Handle models - either from collection or individual selection
        if web_params.get("selected_collection"):
            # Collection-based model selection
            collection_id = web_params["selected_collection"]
            collection_models = self.resolve_collection_models(collection_id)
            if collection_models:
                converted["models"] = len(collection_models)
                converted["selected_models"] = collection_models
                converted["collection_id"] = collection_id
                self.logger.info(f"Using collection '{collection_id}' with {len(collection_models)} models")
            else:
                # Fallback to default if collection resolution fails
                self.logger.warning(f"Collection '{collection_id}' resolution failed, using default")
                converted["models"] = 3
        elif web_params.get("selected_models"):
            # Individual model selection (legacy support)
            converted["models"] = len(web_params["selected_models"])
            converted["selected_models"] = web_params["selected_models"]
            self.logger.info(f"Using individual model selection: {len(web_params['selected_models'])} models")
        else:
            # Default to 3 models if not specified
            converted["models"] = 3
            self.logger.debug("No models or collection specified, defaulting to 3 models")
        
        # Add defaults for other required parameters
        if "variations" not in converted:
            # Default to 0 variations to preserve only the original user query
            # Users can explicitly set higher values if they want query exploration
            converted["variations"] = 0
        if "max_combinations" not in converted:
            converted["max_combinations"] = 24
        
        # Add defaults for cost estimator parameters
        converted.setdefault("simulate", False)
        converted.setdefault("dry_run", False)
        converted.setdefault("use_ollama", False)
        converted.setdefault("balanced_models", False)
        
        return converted
    
    def _monitor_subprocess_progress(self, process, execution_id: str):
        """Real-time progress monitoring from CLI JSON output and wait for completion"""
        self.logger.debug(f"Starting JSON progress monitoring for execution {execution_id}")
        
        # Initialize progress tracking
        total_combinations = 0
        completed_combinations = 0
        stdout_lines = []
        stderr_lines = []
        
        # Enhanced error recovery tracking
        last_progress_time = datetime.now()
        consecutive_errors = 0
        max_consecutive_errors = 10
        
        try:
            # Read output line by line in real-time with error recovery
            while True:
                # Check if process has finished
                if process.poll() is not None:
                    break
                
                # Check for stalled progress (no updates for too long)
                current_time = datetime.now()
                time_since_progress = (current_time - last_progress_time).total_seconds()
                
                if time_since_progress > 60:  # No progress for 60 seconds
                    self.logger.warning(f"Execution {execution_id}: No progress updates for {int(time_since_progress)} seconds")
                    if execution_id in self.execution_status:
                        current_msg = self.execution_status[execution_id].get("message", "Processing...")
                        self.execution_status[execution_id].update({
                            "message": f"{current_msg} (Working on complex task...)",
                            "last_activity": current_time.isoformat()
                        })
                    last_progress_time = current_time  # Reset timer
                    
                try:
                    # Use a simpler approach - try to read a line with a short timeout
                    try:
                        line = process.stdout.readline()
                        if line:
                            line = line.strip()
                            stdout_lines.append(line)
                            self.logger.debug(f"CLI output: {line}")
                            
                            # Check for JSON progress messages
                            if line.startswith("PROGRESS_JSON:"):
                                try:
                                    json_str = line[14:]  # Remove "PROGRESS_JSON:" prefix
                                    progress_data = json.loads(json_str)
                                    
                                    if progress_data["type"] == "execution_start":
                                        total_combinations = progress_data["total_combinations"]
                                        self.execution_status[execution_id].update({
                                            "progress": 10,
                                            "message": f"Starting execution of {total_combinations} LLM calls...",
                                            "total_combinations": total_combinations,
                                            "completed_combinations": 0,
                                            "current_calls": []
                                        })
                                        
                                    elif progress_data["type"] == "combination_start":
                                        # Update with current combination being processed
                                        progress_percentage = int((progress_data['combination_index'] / total_combinations) * 100)
                                        
                                        # Calculate estimated time remaining
                                        current_time = datetime.now()
                                        start_time = datetime.fromisoformat(self.execution_status[execution_id]["start_time"])
                                        elapsed_minutes = (current_time - start_time).total_seconds() / 60
                                        
                                        if progress_data['combination_index'] > 1:
                                            # Calculate velocity (combinations per minute)
                                            velocity = (progress_data['combination_index'] - 1) / max(elapsed_minutes, 0.1)
                                            remaining_combinations = total_combinations - progress_data['combination_index']
                                            estimated_remaining_minutes = remaining_combinations / max(velocity, 0.01)
                                            
                                            if estimated_remaining_minutes < 1:
                                                time_remaining = "< 1 min"
                                            elif estimated_remaining_minutes < 60:
                                                time_remaining = f"{int(estimated_remaining_minutes)} min"
                                            else:
                                                hours = int(estimated_remaining_minutes // 60)
                                                minutes = int(estimated_remaining_minutes % 60)
                                                time_remaining = f"{hours}h {minutes}m"
                                        else:
                                            time_remaining = "calculating..."
                                        
                                        current_message = f"Processing {progress_data['model']} with {progress_data['framework']} framework ({progress_data['combination_index']}/{total_combinations} - {progress_percentage}%) • ETA: {time_remaining}"
                                        
                                        # Track current calls
                                        current_calls = self.execution_status[execution_id].get("current_calls", [])
                                        current_calls.append({
                                            "model": progress_data["model"],
                                            "framework": progress_data["framework"],
                                            "domain": progress_data["domain"],
                                            "status": "processing",
                                            "start_time": current_time.isoformat()
                                        })
                                        
                                        self.execution_status[execution_id].update({
                                            "progress": 10 + int((progress_data["combination_index"] / total_combinations) * 80),
                                            "message": current_message,
                                            "current_calls": current_calls[-5:]  # Keep last 5 for display
                                        })
                                        
                                    elif progress_data["type"] == "combination_complete":
                                        completed_combinations += 1
                                        
                                        # Update the last call status
                                        current_calls = self.execution_status[execution_id].get("current_calls", [])
                                        if current_calls:
                                            current_calls[-1]["status"] = "completed" if progress_data["success"] else "error"
                                            if not progress_data["success"]:
                                                current_calls[-1]["error"] = progress_data.get("error", "Unknown error")
                                        
                                        completion_percentage = int((completed_combinations / total_combinations) * 100)
                                        
                                        # Calculate elapsed time for this combination
                                        current_time = datetime.now()
                                        start_time = datetime.fromisoformat(self.execution_status[execution_id]["start_time"])
                                        elapsed_minutes = (current_time - start_time).total_seconds() / 60
                                        
                                        if elapsed_minutes < 1:
                                            elapsed_time = f"{int(elapsed_minutes * 60)}s"
                                        elif elapsed_minutes < 60:
                                            elapsed_time = f"{int(elapsed_minutes)}m"
                                        else:
                                            hours = int(elapsed_minutes // 60)
                                            minutes = int(elapsed_minutes % 60)
                                            elapsed_time = f"{hours}h {minutes}m"
                                        
                                        completion_message = f"Completed {completed_combinations}/{total_combinations} LLM calls ({completion_percentage}%) • Elapsed: {elapsed_time}"
                                        if not progress_data["success"]:
                                            completion_message += f" (Last call failed: {progress_data.get('error', 'Unknown error')})"
                                        
                                        self.execution_status[execution_id].update({
                                            "progress": 10 + int((completed_combinations / total_combinations) * 80),
                                            "message": completion_message,
                                            "completed_combinations": completed_combinations,
                                            "current_calls": current_calls
                                        })
                                        
                                except json.JSONDecodeError as e:
                                    self.logger.warning(f"Failed to parse JSON progress: {e}")
                                    consecutive_errors += 1
                        else:
                            # No output available, short sleep
                            time.sleep(0.1)
                    except Exception as read_error:
                        self.logger.debug(f"Read timeout or error: {read_error}")
                        consecutive_errors += 1
                        time.sleep(0.1)
                        
                except Exception as e:
                    self.logger.debug(f"Non-critical error reading output: {e}")
                    consecutive_errors += 1
                    time.sleep(0.1)  # Small delay to prevent busy waiting
                
                # Check for too many consecutive errors
                if consecutive_errors > max_consecutive_errors:
                    self.logger.warning(f"Execution {execution_id}: {consecutive_errors} consecutive errors, attempting recovery")
                    if execution_id in self.execution_status:
                        current_msg = self.execution_status[execution_id].get("message", "Processing...")
                        self.execution_status[execution_id].update({
                            "message": f"{current_msg} (Recovering from communication issues...)",
                            "recovery_attempts": self.execution_status[execution_id].get("recovery_attempts", 0) + 1
                        })
                    consecutive_errors = 0  # Reset counter
                    time.sleep(1)  # Longer delay for recovery
                elif consecutive_errors == 0:
                    # Reset progress timer on successful reads
                    last_progress_time = datetime.now()
            
            # Read any remaining output
            remaining_stdout, remaining_stderr = process.communicate()
            if remaining_stdout:
                stdout_lines.extend(remaining_stdout.strip().split('\n'))
            if remaining_stderr:
                stderr_lines.extend(remaining_stderr.strip().split('\n'))
                
            # When process completes, update to synthesis phase
            if execution_id in self.execution_status and self.execution_status[execution_id]["status"] == "running":
                self.execution_status[execution_id].update({
                    "progress": 90,
                    "message": "Generating reports and analysis..."
                })
                    
        except Exception as e:
            self.logger.error(f"Error monitoring progress for {execution_id}: {e}")
            # Fallback to communicate() if monitoring fails
            remaining_stdout, remaining_stderr = process.communicate()
            if remaining_stdout:
                stdout_lines.append(remaining_stdout)
            if remaining_stderr:
                stderr_lines.append(remaining_stderr)
        
        # Return combined output
        return '\n'.join(stdout_lines), '\n'.join(stderr_lines)
    
    def _analyze_execution_error(self, stderr: str, returncode: int, execution_id: str) -> str:
        """Analyze subprocess errors and provide specific guidance"""
        self.logger.error(f"Analyzing execution error for {execution_id}: return code {returncode}")
        self.logger.error(f"STDERR content: {stderr}")
        
        # Analyze common error patterns
        if "No module named" in stderr:
            missing_module = stderr.split("No module named '")[1].split("'")[0] if "No module named '" in stderr else "unknown"
            self.logger.error(f"Missing Python module: {missing_module}")
            return f"Missing Python dependencies ({missing_module}). Run: pip install -r requirements.txt"
            
        elif "API key" in stderr.lower() or "authentication" in stderr.lower():
            self.logger.error("API key or authentication issue detected")
            return "API key issue. Check your OpenRouter or other API key configuration in the session."
            
        elif "FileNotFoundError" in stderr:
            if "config" in stderr.lower():
                self.logger.error("Configuration file not found")
                return "Configuration file missing. Verify the selected config file exists."
            else:
                self.logger.error("General file not found error")
                return "Required file missing. Check file paths and permissions."
                
        elif "Permission denied" in stderr:
            self.logger.error("Permission denied error")
            return "Permission denied. Check file permissions and disk space."
            
        elif "Connection" in stderr and ("refused" in stderr or "timeout" in stderr):
            self.logger.error("Network connection issue")
            return "Network connection issue. Check internet connectivity and API endpoints."
            
        elif returncode == 1 and "Usage:" in stderr:
            self.logger.error("Command line argument error")
            return "Invalid command line arguments. Check parameter formatting."
            
        elif returncode == 130:  # Ctrl+C
            self.logger.warning("Process interrupted by user")
            return "Process was interrupted. This may be normal if you stopped the execution."
            
        else:
            self.logger.error(f"Unhandled error pattern: {stderr[:200]}...")
            return f"Execution failed with code {returncode}: {stderr[:200]}{'...' if len(stderr) > 200 else ''}"
    
    def _process_model_params(self, selected_models):
        """Process model parameters to ensure they work with the ISEE backend"""
        processed_models = []
        
        # Load config to check existing models
        try:
            with open('openrouter_config.json', 'r') as f:
                config = json.load(f)
                config_models = {model.get('id'): model for model in config.get('models', {}).get('api_models', [])}
                # Also create a reverse lookup by model parameter
                param_to_config = {model.get('parameters', {}).get('model', ''): model.get('id') 
                                 for model in config.get('models', {}).get('api_models', [])
                                 if model.get('parameters', {}).get('model')}
        except Exception as e:
            self.logger.warning(f"Could not load config for model processing: {e}")
            config_models = {}
            param_to_config = {}
        
        for model_param in selected_models:
            # Check if this is already a model parameter (e.g., "anthropic/claude-3-5-sonnet")
            if '/' in model_param:
                # This looks like an OpenRouter model parameter
                if model_param in param_to_config:
                    # Use the existing config ID
                    config_id = param_to_config[model_param]
                    processed_models.append(config_id)
                    self.logger.info(f"Found existing config for {model_param} -> {config_id}")
                else:
                    # Generate a dynamic config ID for this model parameter
                    dynamic_id = f"openrouter_{model_param.replace('/', '_').replace('-', '_')}"
                    processed_models.append(model_param)  # Pass the model param directly
                    self.logger.info(f"Using dynamic model parameter: {model_param}")
            else:
                # This might be a legacy ID, check if it exists in config
                if model_param in config_models:
                    processed_models.append(model_param)
                    self.logger.debug(f"Using existing config ID: {model_param}")
                else:
                    # Treat as a model parameter and pass through
                    processed_models.append(model_param)
                    self.logger.warning(f"Unknown model identifier, passing through: {model_param}")
        
        return processed_models
    
    def _detect_apis(self) -> Dict[str, Any]:
        """Detect available API providers and Ollama models (adapted from command wizard)"""
        # Get session API key if available (only within request context)
        session_api_key = None
        try:
            if 'openrouter_api_key' in session:
                session_api_key = session['openrouter_api_key']
        except RuntimeError:
            # Outside request context - no session access
            pass
        
        return self._detect_apis_with_session_key(session_api_key)
    
    def _detect_apis_with_session_key(self, session_api_key: str = None) -> Dict[str, Any]:
        """Detect available API providers and Ollama models with optional session key"""
        api_status = {
            "anthropic": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "openai": bool(os.environ.get("OPENAI_API_KEY")),
            "google": bool(os.environ.get("GOOGLE_API_KEY")),
            "openrouter": bool(os.environ.get("OPENROUTER_API_KEY")),
            "ollama": False,
            "ollama_models": [],
            "any_api": False
        }
        
        # Check session-stored keys
        if session_api_key:
            api_status["openrouter"] = True
        
        # Check Ollama availability
        try:
            from model_api_integration import ModelAPIFactory
            ollama_client = ModelAPIFactory.create_client("ollama")
            ollama_models = ollama_client.get_available_models()
            if ollama_models:
                api_status["ollama"] = True
                api_status["ollama_models"] = ollama_models
        except Exception:
            # Silently fail if Ollama check fails
            pass
            
        api_status["any_api"] = any([
            api_status["anthropic"],
            api_status["openai"], 
            api_status["google"],
            api_status["openrouter"],
            api_status["ollama"]
        ])
        
        return api_status
    
    def validate_openrouter_api_key(self, api_key: str) -> bool:
        """Validate an OpenRouter API key by making a test request"""
        try:
            from model_api_integration import OpenRouterClient
            
            # Create a temporary client with the provided key
            temp_client = OpenRouterClient(api_key=api_key)
            
            # Try to get the models list as a validation
            models = temp_client.get_available_models()
            
            # If we get here without exception, the key works
            return len(models) > 0
            
        except Exception as e:
            print(f"API key validation failed: {str(e)}")
            return False
    
    def setup_openrouter_api_key(self, api_key: str, storage_method: str = "session") -> Dict[str, Any]:
        """Set up OpenRouter API key with specified storage method"""
        result = {
            "success": False,
            "message": "",
            "api_status": {}
        }
        
        # Validate API key format
        if not api_key.startswith("sk-or-"):
            result["message"] = "OpenRouter API keys should start with 'sk-or-'"
            return result
        
        # Optional validation
        if not self.validate_openrouter_api_key(api_key):
            result["message"] = "API key validation failed. Please check your key."
            return result
        
        # Store the key based on storage method
        if storage_method == "session":
            session['openrouter_api_key'] = api_key
            result["message"] = "OpenRouter API key set for this session!"
        elif storage_method == "environment":
            os.environ["OPENROUTER_API_KEY"] = api_key
            result["message"] = "OpenRouter API key set for this application session!"
        
        # Update API status
        updated_api_status = self._detect_apis()
        result["success"] = True
        result["api_status"] = updated_api_status
        
        return result

# Initialize demo controller
demo = ISEEWebDemo()

@app.route('/')
def index():
    """Main demo page"""
    return render_template('demo.html')

@app.route('/api/frameworks')
def api_frameworks():
    """Get cognitive frameworks data"""
    complexity = request.args.get('complexity', 'all')
    frameworks = demo.get_cognitive_frameworks(complexity)
    return jsonify(frameworks)

@app.route('/api/models')
def api_models():
    """Get individual model data"""
    models = demo.get_individual_models()
    return jsonify(models)

@app.route('/api/domains')
def api_domains():
    """Get knowledge domains data"""
    domains = demo.get_knowledge_domains()
    return jsonify(domains)

@app.route('/api/collections')
def api_collections():
    """Get LLM collections data"""
    collections = demo.get_llm_collections()
    return jsonify(collections)

@app.route('/api/estimate', methods=['POST'])
def api_estimate():
    """Get cost and resource estimates"""
    parameters = request.json
    estimate = demo.estimate_execution_cost(parameters)
    return jsonify(estimate)

@app.route('/api/preview', methods=['POST'])
def api_preview():
    """Generate command preview"""
    parameters = request.json
    command = demo.generate_command_preview(parameters)
    return jsonify({"command": command})

@app.route('/api/preview-queries', methods=['POST'])
def api_preview_queries():
    """Preview the assembled queries that would be sent to LLMs"""
    try:
        parameters = request.json
        
        if not parameters:
            return jsonify({"error": "No parameters provided"}), 400
        
        # Validate required parameters
        if not parameters.get('query'):
            return jsonify({"error": "Query text is required"}), 400
        
        # Convert web parameters to ISEE format
        converted_params = demo._convert_web_params_to_isee(parameters)
        
        # Create ISEE instance for preview
        from main import ISEEApplication, Query
        isee = ISEEApplication()
        
        # Load configuration
        config_file = converted_params.get('config', 'openrouter_config.json')
        if not os.path.exists(config_file):
            return jsonify({"error": f"Configuration file {config_file} not found"}), 400
        
        isee.load_config(config_file)
        
        # Generate combinations for preview
        query_text = converted_params['query']
        
        # Use domain IDs that were already resolved in parameter conversion
        domain_ids = []
        if converted_params.get('domains'):
            # Use already-resolved domain IDs from parameter conversion
            domain_ids = converted_params['domains']
        elif converted_params.get('domain'):
            # Use single resolved domain ID
            domain_ids = [converted_params['domain']]
        
        # Final fallback if no domains found
        if not domain_ids:
            domain_ids = ['domain_education']
        model_count = converted_params.get('models', 3)
        instruction_count = converted_params.get('instructions', 3)
        query_variations = converted_params.get('variations', 0)
        max_combinations = converted_params.get('max_combinations', 100)  # No limit for preview - enables full analysis
        selected_models = converted_params.get('selected_models', [])
        # Create query and generate combinations
        from uuid import uuid4
        query_id = f"query_{str(uuid4())[:8]}"
        query = Query(id=query_id, text=query_text)
        isee.query_generator.add_base_query(query)
        
        # Set specific framework templates if provided by Web UI
        if converted_params.get('instruction_templates'):
            framework_ids = converted_params['instruction_templates'].split(',')
            isee.specific_template_ids = [fid.strip() for fid in framework_ids if fid.strip()]
        
        # Generate combinations
        combinations = isee.generate_combinations(
            query_id=query_id,
            domain_ids=domain_ids,
            model_count=model_count,
            instruction_count=instruction_count,
            query_variations=query_variations,
            max_combinations=max_combinations,
            selected_models=selected_models
        )
        
        if not combinations:
            return jsonify({"error": "No valid combinations generated"}), 400
        
        # Build preview data
        preview_data = []
        for combo in combinations:
            try:
                # Get components
                template = isee.template_library.get_template(combo["template"])
                query_obj = isee.query_generator.get_query_by_id(combo["query"])
                domain = isee.domain_manager.get_domain(combo["domain"])
                
                # Format the instruction template
                formatted_instruction = template.format({
                    "domain": domain.description,
                    **query_obj.variables
                })
                
                # Create complete prompt
                complete_prompt = f"{formatted_instruction}\n\n{query_obj.text}"
                
                preview_data.append({
                    "combination_id": combo["id"],
                    "model": combo["model"],
                    "template_name": template.name,
                    "template_id": template.id,
                    "cognitive_style": template.metadata.get('cognitive_style', 'default'),
                    "domain_name": domain.name,
                    "query_text": query_obj.text,
                    "formatted_instruction": formatted_instruction,
                    "complete_prompt": complete_prompt,
                    "character_count": len(complete_prompt),
                    "word_count": len(complete_prompt.split())
                })
                
            except Exception as e:
                # Skip invalid combinations
                continue
        
        return jsonify({
            "success": True,
            "total_combinations": len(combinations),
            "preview_count": len(preview_data),
            "queries": preview_data
        })
        
    except Exception as e:
        return jsonify({"error": f"Preview generation failed: {str(e)}"}), 500

@app.route('/api/execute', methods=['POST'])
def api_execute():
    """Execute ISEE command"""
    parameters = request.json
    execution_id = f"exec_{int(time.time())}"
    
    # Get session API key if available
    session_api_key = session.get('openrouter_api_key', None)
    
    # Start execution in background thread
    thread = threading.Thread(
        target=demo.execute_isee_command,
        args=(parameters, execution_id, session_api_key)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({"execution_id": execution_id})

@app.route('/api/status/<execution_id>')
def api_status(execution_id):
    """Get execution status"""
    status = demo.execution_status.get(execution_id, {"status": "not_found"})
    return jsonify(status)

@app.route('/api/download/<execution_id>')
def api_download(execution_id):
    """Download results file with proper content type and filename"""
    status = demo.execution_status.get(execution_id, {})
    results_file = status.get("results_file")
    
    if results_file and Path(results_file).exists():
        file_path = Path(results_file)
        
        # Determine content type and download filename based on file extension
        if file_path.suffix == '.md':
            mimetype = 'text/markdown'
            download_name = f"isee_results_{execution_id}.md"
        elif file_path.suffix == '.json':
            mimetype = 'application/json'
            download_name = f"isee_results_{execution_id}.json"
        else:
            # Fallback for other formats
            mimetype = 'application/octet-stream'
            download_name = f"isee_results_{execution_id}{file_path.suffix}"
        
        return send_file(
            results_file, 
            as_attachment=True,
            download_name=download_name,
            mimetype=mimetype
        )
    else:
        return jsonify({"error": "Results file not found"}), 404

@app.route('/api/api-status')
def api_api_status():
    """Get current API provider status"""
    api_status = demo._detect_apis()  # Get current status
    return jsonify(api_status)

@app.route('/api/setup-openrouter', methods=['POST'])
def api_setup_openrouter():
    """Set up OpenRouter API key"""
    data = request.get_json()
    api_key = data.get('api_key', '').strip()
    storage_method = data.get('storage_method', 'session')
    
    if not api_key:
        return jsonify({"success": False, "message": "API key is required"}), 400
    
    result = demo.setup_openrouter_api_key(api_key, storage_method)
    return jsonify(result)

@app.route('/api/validate-openrouter', methods=['POST'])
def api_validate_openrouter():
    """Validate OpenRouter API key without storing it"""
    data = request.get_json()
    api_key = data.get('api_key', '').strip()
    
    if not api_key:
        return jsonify({"valid": False, "message": "API key is required"}), 400
    
    if not api_key.startswith("sk-or-"):
        return jsonify({"valid": False, "message": "OpenRouter API keys should start with 'sk-or-'"})
    
    is_valid = demo.validate_openrouter_api_key(api_key)
    return jsonify({
        "valid": is_valid,
        "message": "API key is valid!" if is_valid else "API key validation failed"
    })

@app.route('/api/ollama-models')
def api_ollama_models():
    """Get available Ollama models"""
    api_status = demo._detect_apis()
    return jsonify({
        "available": api_status.get("ollama", False),
        "models": api_status.get("ollama_models", []),
        "count": len(api_status.get("ollama_models", []))
    })

@app.route('/api/rankings-status')
def api_rankings_status():
    """Get current rankings cache status"""
    try:
        status = demo.rankings_service.get_cache_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "cache_exists": False,
            "needs_update": True,
            "recommendation": "error"
        }), 500

@app.route('/api/update-rankings', methods=['POST'])
def api_update_rankings():
    """Update model rankings from OpenRouter API"""
    try:
        # Run the async update in a thread
        def run_update():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(demo.rankings_service._update_rankings())
                return success
            finally:
                loop.close()
        
        # Execute in background thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_update)
            success = future.result(timeout=30)  # 30 second timeout
        
        # Get updated status
        status = demo.rankings_service.get_cache_status()
        
        return jsonify({
            "success": success,
            "status": status,
            "message": "Rankings updated successfully" if success else "Update failed, using fallback data"
        })
        
    except concurrent.futures.TimeoutError:
        return jsonify({
            "success": False,
            "error": "Update timeout after 30 seconds",
            "message": "Rankings update timed out"
        }), 408
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": f"Update failed: {str(e)}"
        }), 500

@app.route('/api/models-fresh')
def api_models_fresh():
    """Get fresh model data (bypassing cache)"""
    try:
        # Run async model fetch in thread
        def run_fetch():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                models = loop.run_until_complete(demo.rankings_service.get_top_models(force_update=True))
                return models
            finally:
                loop.close()
        
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_fetch)
            models = future.result(timeout=30)
        
        return jsonify(models)
        
    except concurrent.futures.TimeoutError:
        return jsonify({"error": "Request timeout"}), 408
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Ensure output directory exists
    Path("data/output").mkdir(parents=True, exist_ok=True)
    
    # Run development server on port 5001 to avoid macOS AirPlay conflict
    print("🚀 Starting ISEE Web Demo...")
    print("📱 Open your browser to: http://localhost:5001")
    print("💡 For investor demo, press F11 for full screen mode")
    app.run(debug=True, host='0.0.0.0', port=5001)