#!/usr/bin/env python3
"""
ISEE Meta Framework - Web Demo Application
Minimalist web UI for investor demonstrations showcasing the ISEE configuration capabilities.
"""

import os
import json
import threading
import time
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import markdown

# Import existing ISEE components
from cost_estimation import CostEstimator
from cognitive_framework_visualizer import CognitiveFrameworkVisualizer
from openrouter_model_collections import OpenRouterModelCollections
# Import from isee_engine for direct execution (Phase 4 refactoring)
from isee_engine import ISEEApplication, ISEEGuardrails, ExecutionParams
from domain_manager import DomainManager, create_default_domains
from openrouter_rankings_service import OpenRouterRankingsService
# Removed: HTML report generation - using markdown display only

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.urandom(24)

# Configure logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('isee-ui.log'),
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
        # Legacy components removed - dashboard and parameter_context archived
        self.guardrails = ISEEGuardrails()
        self.execution_status = {}
        # Removed: HTML report generator - using markdown display only
        
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
            "ins_futurist": "🚀",
            "ins_disruption": "⚡"
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
            "ins_futurist": "Futurist - Explore future possibilities",
            "ins_disruption": "Disruption - Challenge all existing assumptions"
        }
        
        for framework_id, _ in frameworks:
            framework_data.append({
                "id": framework_id,
                "icon": framework_icons.get(framework_id, "🔍"),
                "name": framework_descriptions.get(framework_id, framework_id),
                "description": framework_descriptions.get(framework_id, framework_id)
            })
        
        return framework_data
    
    def get_individual_models(self, use_cached: bool = True, strategic_only: bool = False) -> List[Dict[str, Any]]:
        """Get individual LLM models for manual selection.
        
        Args:
            use_cached: Whether to use cached rankings (True) or force update (False)
            strategic_only: Whether to return only strategically curated models (True) or all models (False)
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
                        
                        # Apply strategic filtering if requested
                        if strategic_only:
                            models = self._filter_strategic_models(models)
                            self.logger.info(f"Filtered to {len(models)} strategic models")
                        
                        return models
            
            # Fallback to config-based models + hardcoded fallback
            self.logger.info("Using fallback model loading approach")
            fallback_models = self._get_fallback_models()
            
            # Apply strategic filtering if requested
            if strategic_only:
                fallback_models = self._filter_strategic_models(fallback_models)
                self.logger.info(f"Filtered fallback to {len(fallback_models)} strategic models")
            
            return fallback_models
            
        except Exception as e:
            self.logger.error(f"Error in get_individual_models: {e}")
            fallback_models = self._get_fallback_models()
            
            # Apply strategic filtering if requested
            if strategic_only:
                fallback_models = self._filter_strategic_models(fallback_models)
                self.logger.info(f"Filtered error fallback to {len(fallback_models)} strategic models")
            
            return fallback_models
    
    def _filter_strategic_models(self, models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter models to return only strategically curated ones based on config metadata."""
        try:
            # Load globant_enterprise_config.json for strategic model metadata
            with open('globant_enterprise_config.json', 'r') as f:
                config = json.load(f)
            
            # Create lookup of strategic models by ID and model_param
            strategic_ids = set()
            strategic_params = set()
            
            for model in config.get('models', {}).get('api_models', []):
                # Skip disabled models
                if model.get('disabled', False):
                    continue
                    
                if model.get('ui_priority') == 'strategic':
                    strategic_ids.add(model.get('id'))
                    model_param = model.get('parameters', {}).get('model', '')
                    if model_param:
                        strategic_params.add(model_param)
            
            # Filter input models to only strategic ones and remove duplicates
            strategic_models = []
            seen_model_params = set()  # Track model_params to prevent duplicates
            
            for model in models:
                model_id = model.get('id', '')
                model_param = model.get('model_param', '')
                
                # Check if this model is marked as strategic
                if ((model_id in strategic_ids or model_param in strategic_params) 
                    and model_param not in seen_model_params):
                    strategic_models.append(model)
                    seen_model_params.add(model_param)
                elif model_param in seen_model_params:
                    self.logger.debug(f"Skipping duplicate strategic model: {model.get('name', '')} ({model_param})")
            
            self.logger.debug(f"Strategic filtering: {len(strategic_models)} out of {len(models)} models (duplicates removed)")
            return strategic_models
            
        except Exception as e:
            self.logger.error(f"Error filtering strategic models: {e}")
            # Return first 12 models as fallback
            return models[:12]
    
    def _get_fallback_models(self) -> List[Dict[str, Any]]:
        """Get models from Globant config file and hardcoded fallback list."""
        try:
            with open('globant_enterprise_config.json', 'r') as f:
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
                    "description": f"{provider.title()} model",
                    "ui_priority": model.get('ui_priority'),
                    "curation_tags": model.get('curation_tags', []),
                    "willison_tier": model.get('willison_tier')
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
            combinations = parameters.get("max_combinations", 30)
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
            # Use Globant Enterprise config (primary provider)
            cmd_parts.extend(["--config", "globant_enterprise_config.json"])
            
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
        """Execute ISEE command using direct imports (Phase 4 refactoring).

        This method uses ISEEApplication directly instead of spawning a subprocess,
        providing cleaner integration and real-time progress updates via callbacks.
        """
        self.logger.info(f"Starting execution {execution_id} with parameters: {parameters}")

        # Store execution parameters for performance tracking
        if not hasattr(self, 'execution_parameters'):
            self.execution_parameters = {}
        stored_params = parameters.copy()
        stored_params['session_api_key'] = session_api_key
        if 'generate_report' not in stored_params:
            stored_params['generate_report'] = True
        self.execution_parameters[execution_id] = stored_params

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
                "results_file": None,
                "current_calls": [],
                "active_parallel_calls": []
            }

            # Convert Web UI parameters to format expected by ISEE backend
            converted_params = self._convert_web_params_to_isee(parameters)
            self.logger.debug(f"Converted parameters: {converted_params}")

            # Create timestamped run directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            run_dir = Path("data/output") / f"run_{timestamp}"
            run_dir.mkdir(parents=True, exist_ok=True)

            # Determine output format
            output_format = converted_params.get("output_format", "markdown")
            extension = "md" if output_format == "markdown" else "json"
            output_file = run_dir / f"isee_result.{extension}"

            # Store run directory
            self.execution_status[execution_id]["run_directory"] = str(run_dir)

            # Check if we should use real execution or simulation
            current_api_status = self._detect_apis_with_session_key(session_api_key)
            use_real_models = current_api_status.get("any_api", False)

            # Process domains - handle both static and dynamic
            domain_names = None
            dynamic_domain_names = None
            selected_domains = converted_params.get("domains", [])
            use_dynamic_domains = converted_params.get("strategic_models", False)

            if selected_domains:
                if use_dynamic_domains:
                    dynamic_domain_names = [d.replace('dynamic:', '') if d.startswith('dynamic:') else d
                                           for d in selected_domains]
                else:
                    domain_names = selected_domains
            elif converted_params.get("domain"):
                if use_dynamic_domains:
                    dynamic_domain_names = [converted_params["domain"]]
                else:
                    domain_names = [converted_params["domain"]]

            # Process framework templates
            specific_template_ids = None
            if converted_params.get("instruction_templates"):
                specific_template_ids = [t.strip() for t in converted_params["instruction_templates"].split(",")]

            # Get selected models
            selected_models = converted_params.get("selected_models", [])
            if selected_models:
                selected_models = self._process_model_params(selected_models)

            # Create progress callback to update execution status
            def progress_callback(progress_info: Dict[str, Any]) -> None:
                """Handle progress updates from ISEEEngine."""
                try:
                    progress_type = progress_info.get("type", "")

                    if progress_type == "execution_start":
                        total_combinations = progress_info.get("total_combinations", 0)
                        self.execution_status[execution_id].update({
                            "status": "running",
                            "progress": 10,
                            "message": f"Starting execution of {total_combinations} LLM calls...",
                            "total_combinations": total_combinations,
                            "completed_combinations": 0
                        })

                    elif progress_type == "parallel_execution_start":
                        total = progress_info.get("total_combinations", 0)
                        workers = progress_info.get("max_workers", 8)
                        self.execution_status[execution_id].update({
                            "status": "running",
                            "progress": 10,
                            "message": f"Starting parallel execution ({workers} workers) for {total} LLM calls...",
                            "total_combinations": total
                        })

                    elif progress_type in ["combination_start", "combination_start_parallel"]:
                        current_calls = self.execution_status[execution_id].get("current_calls", [])
                        combination_call = {
                            "combination_id": progress_info.get("combination_id", ""),
                            "model": progress_info.get("model", "Unknown"),
                            "framework": progress_info.get("framework", "Unknown"),
                            "domain": progress_info.get("domain", "Unknown"),
                            "provider": progress_info.get("provider", "Unknown"),
                            "status": "processing",
                            "start_time": datetime.now().isoformat(),
                            "is_parallel": progress_type == "combination_start_parallel"
                        }
                        current_calls.append(combination_call)

                        # Keep recent calls for display
                        max_visible = 8 if progress_type == "combination_start_parallel" else 5

                        progress_pct = progress_info.get("progress_percent", 10)
                        self.execution_status[execution_id].update({
                            "progress": 10 + int(progress_pct * 0.8),
                            "message": f"Processing {progress_info.get('model', 'Unknown')} with {progress_info.get('framework', 'Unknown')}",
                            "current_calls": current_calls[-max_visible:],
                            "active_parallel_calls": [c for c in current_calls if c["status"] == "processing"][-max_visible:]
                        })

                    elif progress_type in ["combination_complete", "combination_complete_parallel"]:
                        current_calls = self.execution_status[execution_id].get("current_calls", [])
                        combo_id = progress_info.get("combination_id", "")
                        success = progress_info.get("success", True)

                        # Update the matching call status
                        for call in current_calls:
                            if call.get("combination_id") == combo_id:
                                call["status"] = "completed" if success else "error"
                                call["end_time"] = datetime.now().isoformat()
                                if not success:
                                    call["error"] = progress_info.get("error", "Unknown error")
                                break

                        completed = self.execution_status[execution_id].get("completed_combinations", 0) + 1
                        total = self.execution_status[execution_id].get("total_combinations", 1)

                        self.execution_status[execution_id].update({
                            "completed_combinations": completed,
                            "progress": 10 + int((completed / total) * 80),
                            "message": f"Completed {completed}/{total} LLM calls ({int(completed/total*100)}%)",
                            "current_calls": current_calls,
                            "active_parallel_calls": [c for c in current_calls if c["status"] == "processing"]
                        })

                    elif progress_type in ["combination_failed_parallel"]:
                        self.logger.warning(f"Combination failed: {progress_info.get('error', 'Unknown')}")

                    elif progress_type == "parallel_execution_complete":
                        completed = progress_info.get("completed", 0)
                        failed = progress_info.get("failed", 0)
                        self.execution_status[execution_id].update({
                            "progress": 90,
                            "message": f"Parallel execution complete: {completed} succeeded, {failed} failed. Generating reports..."
                        })

                except Exception as e:
                    self.logger.error(f"Error in progress callback: {e}")

            # Update status to running
            self.execution_status[execution_id].update({
                "status": "running",
                "progress": 5,
                "message": "Initializing ISEE engine..."
            })

            # Create ExecutionParams for direct execution
            exec_params = ExecutionParams(
                query=converted_params.get("query", ""),
                config_path="globant_enterprise_config.json",
                output_directory=str(run_dir),
                domain_names=domain_names,
                dynamic_domain_names=dynamic_domain_names,
                model_count=len(selected_models) if selected_models else converted_params.get("models", 3),
                selected_models=selected_models if selected_models else None,
                instruction_count=converted_params.get("instructions", 3),
                specific_template_ids=specific_template_ids,
                query_variations=converted_params.get("variations", 0),
                max_combinations=converted_params.get("max_combinations", 100),
                use_real_models=use_real_models,
                parallel=True,
                max_workers=8,
                output_format=output_format,
                json_progress=False,  # Using callback instead
                generate_reports=True,
                analyze_results=True,
                provider="globant",
                progress_callback=progress_callback
            )

            # Execute using ISEEApplication directly
            self.logger.info(f"Starting direct ISEE execution for {execution_id}")
            isee = ISEEApplication()
            isee.load_config(exec_params.config_path)
            isee.set_output_directory(str(run_dir))

            # Run the pipeline
            result_output = isee.run_from_params(exec_params)

            # Write output file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result_output)

            self.logger.info(f"Execution {execution_id} completed successfully")

            # Auto-ingest performance data
            run_directory = str(run_dir)
            try:
                from performance_tracker import PerformanceTracker
                tracker = PerformanceTracker()

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

                success = tracker.ingest_test_run(run_directory, collection_name)
                if success:
                    self.logger.info(f"Performance data automatically captured for {collection_name}")

            except Exception as e:
                self.logger.error(f"Error auto-ingesting performance data: {e}")

            # Enhanced completion message
            completion_message = "Execution completed successfully! Results saved to timestamped directory:"
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
                "end_time": datetime.now().isoformat()
            })

        except Exception as e:
            self.logger.exception(f"Unexpected error during execution {execution_id}: {e}")
            self.execution_status[execution_id].update({
                "status": "error",
                "progress": 0,
                "message": f"Execution error: {str(e)}",
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
            
        # Validate model selections - accept strategic models, individual models, or collections
        selected_models = parameters.get("selected_models", [])
        selected_collection = parameters.get("selected_collection")
        use_strategic_models = parameters.get("use_strategic_models", False)
        
        if not selected_models and not selected_collection and not use_strategic_models:
            errors.append("At least one model, collection, or strategic models must be selected")
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
        if frameworks and len(frameworks) > 11:
            errors.append("Maximum 11 cognitive frameworks can be selected")
            
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
            "no_visualizations": "no_visualizations",
            "enhancement_info": "enhancement_info",
            "provider": "provider"
        }
        
        for web_key, isee_key in param_mapping.items():
            if web_key in web_params and web_params[web_key] is not None:
                converted[isee_key] = web_params[web_key]
        
        # Handle domain selection - support dynamic domains and traditional mapping
        domain_ids = []
        if web_params.get("selected_domains"):
            # Process selected domains from Web UI
            for domain_identifier in web_params["selected_domains"]:
                # Check if it's a dynamic domain (generated by Smart Auto-Pilot)
                if domain_identifier.startswith('dynamic_domain_') or not domain_identifier.startswith('domain_'):
                    # For dynamic domains or plain text domains, use the name directly
                    # The backend can handle descriptive domain names
                    domain_ids.append(domain_identifier)
                    self.logger.debug(f"Using dynamic/descriptive domain: '{domain_identifier}'")
                else:
                    # Traditional domain ID mapping
                    if domain_identifier in self.domain_manager.domains:
                        domain_ids.append(domain_identifier)
                        self.logger.debug(f"Direct ID mapping for '{domain_identifier}'")
                    else:
                        # Try name-to-ID mapping for backward compatibility
                        all_domains = self.domain_manager.list_domains()
                        exact_matches = [d for d in all_domains if d.name.lower() == domain_identifier.lower()]
                        
                        if exact_matches:
                            domain_ids.extend([d.id for d in exact_matches])
                            self.logger.debug(f"Exact name match for '{domain_identifier}' to ID: {exact_matches[0].id}")
                        else:
                            # Try fuzzy matching for dynamic domains
                            matched_domain = self._find_best_domain_match(domain_identifier)
                            if matched_domain:
                                domain_ids.append(matched_domain)
                                self.logger.debug(f"Fuzzy matched '{domain_identifier}' to '{matched_domain}'")
                            else:
                                # Use the domain name as-is as last resort
                                domain_ids.append(domain_identifier)
                                self.logger.debug(f"Using domain name as-is: '{domain_identifier}'")
            
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
            # Use a simple, safe domain placeholder when none specified
            converted["domain"] = "Technology"
            self.logger.debug("No domains specified, using safe domain placeholder")
        
        # Handle cognitive frameworks
        if web_params.get("cognitive_frameworks"):
            converted["instructions"] = len(web_params["cognitive_frameworks"])
            # Convert Web UI framework names to backend template IDs
            framework_mapping = {
                "Analytical": "ins_analytical",
                "Creative": "ins_creative", 
                "Critical": "ins_critical",
                "Integrative": "ins_integrative",
                "Pragmatic": "ins_pragmatic",
                "First Principles": "ins_first_principles",
                "Systems": "ins_systems",
                "Contrarian": "ins_contrarian",
                "Historical": "ins_historical",
                "Futurist": "ins_futurist",
                "Disruption": "ins_disruption",
                # Legacy support for full names
                "Analytical Framework": "ins_analytical",
                "Creative Framework": "ins_creative", 
                "Critical Framework": "ins_critical",
                "Integrative Framework": "ins_integrative",
                "Pragmatic Framework": "ins_pragmatic",
                "First Principles Framework": "ins_first_principles",
                "Systems Thinking Framework": "ins_systems",
                "Contrarian Framework": "ins_contrarian",
                "Historical Framework": "ins_historical",
                "Future-Oriented Framework": "ins_futurist",
                "Disruption Framework": "ins_disruption"
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
        
        # Handle models - support strategic models, collections, or individual selection
        if web_params.get("use_strategic_models"):
            # Smart Auto-Pilot: Use strategic models
            strategic_models = self.get_individual_models(strategic_only=True)
            strategic_model_ids = [model['model_param'] for model in strategic_models]
            converted["models"] = len(strategic_model_ids)
            converted["selected_models"] = strategic_model_ids
            converted["strategic_models"] = True
            self.logger.info(f"Using strategic models: {len(strategic_model_ids)} models")
        elif web_params.get("selected_collection"):
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
            converted["max_combinations"] = 30
        
        # Add defaults for cost estimator parameters
        converted.setdefault("simulate", False)
        converted.setdefault("dry_run", False)
        converted.setdefault("use_ollama", False)
        converted.setdefault("balanced_models", False)
        
        return converted

    # NOTE: _monitor_subprocess_progress and _analyze_execution_error methods removed
    # as part of Phase 4 refactoring - subprocess pattern eliminated in favor of direct imports

    def _process_model_params(self, selected_models):
        """Process model parameters to ensure they work with the ISEE backend"""
        processed_models = []
        
        # Load Globant config to check existing models
        try:
            with open('globant_enterprise_config.json', 'r') as f:
                config = json.load(f)
                config_models = {model.get('id'): model for model in config.get('models', {}).get('api_models', [])}
                # Also create a reverse lookup by model parameter
                param_to_config = {model.get('parameters', {}).get('model', ''): model.get('id')
                                 for model in config.get('models', {}).get('api_models', [])
                                 if model.get('parameters', {}).get('model')}
        except Exception as e:
            self.logger.warning(f"Could not load Globant config for model processing: {e}")
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
            "globant": bool(os.environ.get("GLOBANT_API_KEY")),
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
            api_status["globant"],
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
    
    def _generate_dynamic_domains(self, query: str) -> List[Dict[str, str]]:
        """Generate domain areas dynamically based on query using lightweight LLM"""
        try:
            # Import OpenRouter client
            import requests
            
            # Use a fast, cost-effective model for domain analysis
            api_key = session.get('openrouter_api_key') or os.environ.get('OPENROUTER_API_KEY')
            if not api_key:
                self.logger.warning("No OpenRouter API key available for domain suggestion")
                return self._get_fallback_domains()
            
            # Construct domain analysis prompt
            prompt = f"""Analyze this query and suggest 2-3 relevant domain areas that would provide the most valuable perspectives:

Query: "{query}"

Respond with ONLY a JSON array of 2-3 domain objects, each with:
- "name": A concise domain name (2-4 words)
- "description": Brief explanation of why this domain is relevant (1 sentence)

Example format:
[
  {{"name": "Behavioral Psychology", "description": "Understanding human decision-making patterns and cognitive biases relevant to the query."}},
  {{"name": "Technology Innovation", "description": "Exploring technological solutions and digital transformation opportunities."}}
]

Return only the JSON array, no other text."""

            # Make API call to lightweight model
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "anthropic/claude-3-haiku",  # Fast, cost-effective
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.1
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                
                # Parse JSON response
                import json
                domains = json.loads(content)
                
                # Validate and format domains
                formatted_domains = []
                for i, domain in enumerate(domains[:3]):  # Max 3 domains
                    if isinstance(domain, dict) and "name" in domain and "description" in domain:
                        formatted_domains.append({
                            "id": f"dynamic_domain_{i+1}",
                            "name": domain["name"],
                            "description": domain["description"]
                        })
                
                if formatted_domains:
                    self.logger.info(f"Generated {len(formatted_domains)} dynamic domains for query: {query[:50]}...")
                    return formatted_domains
                    
            self.logger.warning("Failed to parse domain suggestions, using fallback")
            return self._get_fallback_domains()
            
        except Exception as e:
            self.logger.error(f"Dynamic domain generation failed: {str(e)}")
            return self._get_fallback_domains()
    
    def _get_fallback_domains(self) -> List[Dict[str, str]]:
        """Provide fallback domains when dynamic generation fails"""
        return [
            {
                "id": "fallback_domain_1",
                "name": "Cross-Disciplinary Analysis", 
                "description": "Integrating insights from multiple fields to provide comprehensive understanding."
            },
            {
                "id": "fallback_domain_2",
                "name": "Practical Implementation",
                "description": "Focusing on actionable solutions and real-world application strategies."
            },
            {
                "id": "fallback_domain_3", 
                "name": "Strategic Planning",
                "description": "Examining long-term implications and systematic approaches to the challenge."
            }
        ]
    
    def _find_best_domain_match(self, domain_name: str) -> Optional[str]:
        """Find the best matching domain ID for a dynamic domain name"""
        # Define mapping of common dynamic domain terms to existing domains
        domain_mappings = {
            # Technical documentation related
            "technical communication": "domain_technical_writing",
            "technical documentation": "domain_technical_writing", 
            "documentation": "domain_technical_writing",
            "content management": "domain_content_strategy",
            "content strategy": "domain_content_strategy",
            
            # UX/Design related
            "user experience": "domain_technology",
            "ux design": "domain_technology",
            "user experience design": "domain_technology",
            "interface design": "domain_technology",
            
            # Technology related
            "technology": "domain_technology",
            "innovation": "domain_technology",
            "digital": "domain_technology",
            "ai": "domain_ai_writing",
            "artificial intelligence": "domain_ai_writing",
            
            # Education related
            "education": "domain_education",
            "learning": "domain_education", 
            "teaching": "domain_education",
            "instructional": "domain_instructional_design",
            
            # Development related
            "development": "domain_developer_docs",
            "programming": "domain_developer_docs",
            "software": "domain_developer_docs",
            
            # Management related
            "knowledge management": "domain_knowledge_management",
            "information": "domain_knowledge_management",
            
            # General fallbacks
            "communication": "domain_technical_writing",
            "systems": "domain_technology",
            "management": "domain_knowledge_management"
        }
        
        domain_lower = domain_name.lower().strip()
        
        # Direct mapping first
        if domain_lower in domain_mappings:
            return domain_mappings[domain_lower]
        
        # Partial matching - check if any mapping key is contained in the domain name
        for key, domain_id in domain_mappings.items():
            if key in domain_lower or domain_lower in key:
                return domain_id
        
        # No match found
        return None

# Initialize demo controller
demo = ISEEWebDemo()

@app.route('/')
def index():
    """Main demo page"""
    # Generate session ID for user behavior analytics if not exists
    if 'session_id' not in session:
        import uuid
        session['session_id'] = str(uuid.uuid4())[:8]  # Short session ID
        
        # Track new session start
        demo.logger.info(f"USER_ANALYTICS: event_type=session_started user_session={session['session_id']} "
                        f"timestamp={datetime.now().isoformat()}")
    
    return render_template('demo.html')

@app.route('/isee-ui')
def isee_ui():
    """Serve the hybrid UI interface with dynamic model loading"""
    return send_file('isee-ui.html')

@app.route('/api/frameworks')
def api_frameworks():
    """Get cognitive frameworks data"""
    complexity = request.args.get('complexity', 'all')
    frameworks = demo.get_cognitive_frameworks(complexity)
    return jsonify(frameworks)

@app.route('/api/models')
def api_models():
    """Get individual model data with optional strategic filtering"""
    strategic_only = request.args.get('strategic_only', 'false').lower() == 'true'
    models = demo.get_individual_models(strategic_only=strategic_only)
    return jsonify(models)

@app.route('/api/domains')
def api_domains():
    """Get knowledge domains data"""
    domains = demo.get_knowledge_domains()
    return jsonify(domains)

@app.route('/api/collections')
def api_collections():
    """Get LLM collections data"""
    # User Behavior Analytics - Track collections viewing
    user_session = session.get('session_id', 'anonymous')
    demo.logger.info(f"USER_ANALYTICS: event_type=collections_viewed user_session={user_session} "
                    f"timestamp={datetime.now().isoformat()}")
    
    collections = demo.get_llm_collections()
    return jsonify(collections)

@app.route('/api/estimate', methods=['POST'])
def api_estimate():
    """Get cost and resource estimates"""
    parameters = request.json
    
    # User Behavior Analytics - Track cost estimation usage
    user_session = session.get('session_id', 'anonymous')
    collection_name = parameters.get('collection_name', 'individual_models')
    estimated_models = len(parameters.get('selected_models', []))
    
    demo.logger.info(f"USER_ANALYTICS: event_type=cost_estimated user_session={user_session} "
                    f"collection_name={collection_name} estimated_models={estimated_models} "
                    f"timestamp={datetime.now().isoformat()}")
    
    estimate = demo.estimate_execution_cost(parameters)
    
    # Track the estimated cost value
    estimated_cost = estimate.get('estimated_cost', 0)
    demo.logger.info(f"USER_ANALYTICS: event_type=cost_calculated user_session={user_session} "
                    f"estimated_cost_usd={estimated_cost} collection_name={collection_name} "
                    f"timestamp={datetime.now().isoformat()}")
    
    return jsonify(estimate)

@app.route('/api/preview', methods=['POST'])
def api_preview():
    """Generate command preview"""
    parameters = request.json
    
    # User Behavior Analytics - Track command preview usage
    user_session = session.get('session_id', 'anonymous')
    collection_name = parameters.get('collection_name', 'individual_models')
    demo.logger.info(f"USER_ANALYTICS: event_type=command_previewed user_session={user_session} "
                    f"collection_name={collection_name} timestamp={datetime.now().isoformat()}")
    
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
        from isee_engine import ISEEApplication
        from query_generator import Query
        isee = ISEEApplication()
        
        # Load Globant Enterprise configuration
        config_file = converted_params.get('config', 'globant_enterprise_config.json')
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
            domain_ids = ['general problem-solving']
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
    
    # User Behavior Analytics - Track execution start
    user_session = session.get('session_id', 'anonymous')
    collection_name = parameters.get('collection_name', 'individual_models')
    query_length = len(parameters.get('query', ''))
    frameworks_count = len(parameters.get('selected_frameworks', []))
    domains_count = len(parameters.get('selected_domains', []))
    
    demo.logger.info(f"USER_ANALYTICS: event_type=execution_started user_session={user_session} "
                    f"execution_id={execution_id} collection_name={collection_name} "
                    f"query_length={query_length} frameworks_count={frameworks_count} "
                    f"domains_count={domains_count} timestamp={datetime.now().isoformat()}")
    
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

@app.route('/api/analyze-test', methods=['POST'])
def api_analyze_test():
    """Execute ISEE test analysis with reduced parameters for testing report generation"""
    parameters = request.json
    execution_id = f"test_{int(time.time())}"
    
    # Log test execution
    user_session = session.get('session_id', 'anonymous')
    demo.logger.info(f"USER_ANALYTICS: event_type=test_execution_started user_session={user_session} "
                    f"execution_id={execution_id} max_combinations={parameters.get('max_combinations', 10)} "
                    f"timestamp={datetime.now().isoformat()}")
    
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
    
    # User Behavior Analytics - Track result download
    user_session = session.get('session_id', 'anonymous')
    execution_duration = None
    if status.get("start_time") and status.get("status") == "completed":
        start_time = datetime.fromisoformat(status["start_time"].replace('Z', '+00:00'))
        execution_duration = (datetime.now() - start_time).total_seconds()
    
    demo.logger.info(f"USER_ANALYTICS: event_type=result_downloaded user_session={user_session} "
                    f"execution_id={execution_id} file_available={bool(results_file and Path(results_file).exists())} "
                    f"execution_duration_seconds={execution_duration} timestamp={datetime.now().isoformat()}")
    
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

@app.route('/api/download-zip/<execution_id>')
def api_download_zip(execution_id):
    """Download entire run directory as ZIP archive"""
    import zipfile
    import tempfile
    import os
    
    status = demo.execution_status.get(execution_id, {})
    results_file = status.get("results_file")
    
    # User Behavior Analytics - Track ZIP download
    user_session = session.get('session_id', 'anonymous')
    execution_duration = None
    if status.get("start_time") and status.get("status") == "completed":
        start_time = datetime.fromisoformat(status["start_time"].replace('Z', '+00:00'))
        execution_duration = (datetime.now() - start_time).total_seconds()
    
    demo.logger.info(f"USER_ANALYTICS: event_type=zip_downloaded user_session={user_session} "
                    f"execution_id={execution_id} timestamp={datetime.now().isoformat()}")
    
    # Find the run directory
    run_directory = None
    
    if results_file and Path(results_file).exists():
        # If we have the results file, use its parent directory
        run_directory = Path(results_file).parent
    else:
        # Search for recent run directories that might contain the results
        output_dir = Path("data/output")
        if output_dir.exists():
            # Get all run directories sorted by modification time (newest first)
            run_dirs = [d for d in output_dir.iterdir() if d.is_dir() and d.name.startswith('run_')]
            run_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Look for directories with content in the most recent run directories
            for run_dir in run_dirs[:10]:  # Check last 10 runs
                if any(run_dir.iterdir()):  # Directory has files
                    run_directory = run_dir
                    demo.logger.info(f"Found run directory for execution {execution_id} in {run_dir}")
                    break
    
    if not run_directory or not run_directory.exists():
        return jsonify({"error": "Run directory not found"}), 404
    
    # Create temporary ZIP file
    try:
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        temp_zip.close()
        
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files from the run directory
            for file_path in run_directory.rglob('*'):
                if file_path.is_file():
                    # Create archive path relative to run directory
                    arcname = file_path.relative_to(run_directory)
                    zipf.write(file_path, arcname)
        
        # Determine download filename
        timestamp = run_directory.name.replace('run_', '')
        download_name = f"isee_results_{timestamp}_{execution_id}.zip"
        
        def remove_temp_file():
            try:
                os.unlink(temp_zip.name)
            except:
                pass
        
        # Schedule cleanup after response
        from flask import after_this_request
        @after_this_request
        def cleanup(response):
            remove_temp_file()
            return response
        
        return send_file(
            temp_zip.name,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/zip'
        )
        
    except Exception as e:
        demo.logger.error(f"Error creating ZIP for execution {execution_id}: {e}")
        # Cleanup temp file if it exists
        try:
            os.unlink(temp_zip.name)
        except:
            pass
        return jsonify({"error": f"Error creating ZIP archive: {str(e)}"}), 500

# HTML report endpoint removed - using markdown display only

@app.route('/api/markdown/<execution_id>')
def api_view_markdown(execution_id):
    """Serve the raw markdown content for client-side rendering"""
    status = demo.execution_status.get(execution_id, {})
    results_file = status.get("results_file")
    
    # If not in execution status, try to find the file directly
    if not results_file:
        # First try the direct execution_id path (for backward compatibility)
        potential_path = Path(f"data/output/{execution_id}/isee_result.md")
        if potential_path.exists():
            results_file = str(potential_path)
        else:
            # Search for recent run directories that might contain the results
            # Since execution_id format is exec_{timestamp} but directories are run_{formatted_timestamp}
            output_dir = Path("data/output")
            if output_dir.exists():
                # Get all run directories sorted by modification time (newest first)
                run_dirs = [d for d in output_dir.iterdir() if d.is_dir() and d.name.startswith('run_')]
                run_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                # Look for markdown files in the most recent run directories
                for run_dir in run_dirs[:10]:  # Check last 10 runs
                    potential_md = run_dir / "isee_result.md"
                    if potential_md.exists():
                        results_file = str(potential_md)
                        demo.logger.info(f"Found results file for execution {execution_id} in {run_dir}")
                        break
    
    # User Behavior Analytics - Track markdown viewing
    user_session = session.get('session_id', 'anonymous')
    demo.logger.info(f"USER_ANALYTICS: event_type=markdown_viewed user_session={user_session} "
                    f"execution_id={execution_id} results_available={bool(results_file and Path(results_file).exists())} "
                    f"timestamp={datetime.now().isoformat()}")
    
    if results_file and Path(results_file).exists() and str(results_file).endswith('.md'):
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            return jsonify({
                "success": True,
                "markdown": markdown_content,
                "filename": Path(results_file).name,
                "execution_id": execution_id
            })
        except Exception as e:
            demo.logger.error(f"Error reading markdown file {results_file}: {e}")
            return jsonify({"error": f"Error reading results file: {str(e)}"}), 500
    else:
        return jsonify({"error": "Markdown results file not available"}), 404

@app.route('/api/query-details/<execution_id>')
def api_query_details(execution_id):
    """Serve query details CSV for a specific execution"""
    try:
        # Find the output directory for this execution
        output_dir = Path(f"data/output")
        
        # Look for query details CSV files in the execution directory or output directory
        possible_patterns = [
            f"data/output/{execution_id}/queries_detailed_*.csv",
            f"data/output/run_*/queries_detailed_*.csv",  # Search in run directories
            f"data/output/queries_detailed_*{execution_id}*.csv",
            f"data/output/queries_detailed_*.csv"  # Fallback to any recent file
        ]
        
        csv_file = None
        for pattern in possible_patterns:
            matches = list(Path().glob(pattern))
            if matches:
                # Get the most recent file
                csv_file = max(matches, key=lambda p: p.stat().st_mtime)
                break
        
        if not csv_file or not csv_file.exists():
            return jsonify({"error": "Query details not available for this execution"}), 404
        
        # Read CSV content
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_content = f.read()
        
        return jsonify({
            "success": True,
            "csv_content": csv_content,
            "csv_path": str(csv_file),
            "filename": csv_file.name,
            "execution_id": execution_id
        })
        
    except Exception as e:
        demo.logger.error(f"Error serving query details for {execution_id}: {e}")
        return jsonify({"error": f"Error loading query details: {str(e)}"}), 500

@app.route('/api/download-file')
def api_download_file():
    """Download a file by path (security restricted to output directory)"""
    file_path = request.args.get('path')
    
    if not file_path:
        return jsonify({"error": "File path is required"}), 400
    
    # Security: Ensure file is within the output directory
    try:
        file_path = Path(file_path).resolve()
        output_dir = Path("data/output").resolve()
        
        if not str(file_path).startswith(str(output_dir)):
            return jsonify({"error": "Access denied: File outside allowed directory"}), 403
        
        if not file_path.exists():
            return jsonify({"error": "File not found"}), 404
        
        return send_file(file_path, as_attachment=True, download_name=file_path.name)
        
    except Exception as e:
        demo.logger.error(f"Error downloading file {file_path}: {e}")
        return jsonify({"error": f"Error downloading file: {str(e)}"}), 500

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

@app.route('/api/enhance-query', methods=['POST'])
def api_enhance_query():
    """Generate enhanced versions of user query using validated patterns"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Import enhancement system
        from query_enhancement import get_enhancement_service
        from enhancement_tracking import get_enhancement_tracker
        
        # Generate enhancements
        enhancement_service = get_enhancement_service()
        result = enhancement_service.enhance_query(query)
        
        # Track enhancement generation
        tracker = get_enhancement_tracker()
        enhancement_ids = tracker.track_enhancement_generation(result)
        
        # Convert to JSON-serializable format
        response_data = {
            "original": result.original,
            "enhanced_versions": [
                {
                    "type": enhancement.type.value,
                    "query": enhancement.query,
                    "rationale": enhancement.rationale,
                    "expected_quality_improvement": enhancement.expected_quality_improvement,
                    "confidence_score": enhancement.confidence_score,
                    "enhancement_id": enhancement_ids[i] if i < len(enhancement_ids) else None
                }
                for i, enhancement in enumerate(result.enhanced_versions)
            ],
            "enhancement_analysis": result.enhancement_analysis,
            "processing_time_ms": result.processing_time_ms,
            "analytics": enhancement_service.get_analytics(),
            "tracking_enabled": True
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        demo.logger.error(f"Query enhancement failed: {str(e)}")
        return jsonify({
            "error": "Failed to enhance query",
            "original": data.get('query', '') if data else ''
        }), 500

@app.route('/api/track-enhancement-selection', methods=['POST'])
def api_track_enhancement_selection():
    """Track when user selects an enhancement"""
    try:
        data = request.get_json()
        enhancement_id = data.get('enhancement_id')
        selected = data.get('selected', True)
        
        if not enhancement_id:
            return jsonify({"error": "Enhancement ID is required"}), 400
        
        from enhancement_tracking import get_enhancement_tracker
        tracker = get_enhancement_tracker()
        tracker.track_enhancement_selection(enhancement_id, selected)
        
        return jsonify({
            "success": True,
            "enhancement_id": enhancement_id,
            "selected": selected
        })
        
    except Exception as e:
        demo.logger.error(f"Enhancement tracking failed: {str(e)}")
        return jsonify({
            "error": "Failed to track enhancement selection",
            "enhancement_id": data.get('enhancement_id', '') if data else ''
        }), 500

@app.route('/api/enhancement-analytics')
def api_enhancement_analytics():
    """Get enhancement effectiveness analytics"""
    try:
        from enhancement_tracking import get_enhancement_tracker
        tracker = get_enhancement_tracker()
        
        # Get effectiveness metrics
        effectiveness = tracker.get_enhancement_effectiveness()
        validation_report = tracker.get_validation_report()
        
        return jsonify({
            "effectiveness": effectiveness,
            "validation_report": validation_report,
            "generated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        demo.logger.error(f"Enhancement analytics failed: {str(e)}")
        return jsonify({
            "error": "Failed to retrieve enhancement analytics"
        }), 500

@app.route('/api/suggest-domains', methods=['POST'])
def api_suggest_domains():
    """Generate relevant domains based on user query using lightweight LLM"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Use a lightweight model to analyze query and suggest domains
        suggested_domains = demo._generate_dynamic_domains(query)
        
        return jsonify({
            "query": query,
            "suggested_domains": suggested_domains,
            "domain_count": len(suggested_domains)
        })
        
    except Exception as e:
        demo.logger.error(f"Domain suggestion failed: {str(e)}")
        return jsonify({
            "error": "Failed to generate domain suggestions",
            "fallback_domains": demo._get_fallback_domains()
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

@app.route('/docs')
@app.route('/docs/')
@app.route('/docs/<path:doc_path>')
def documentation(doc_path=''):
    """Documentation pages with hierarchical navigation"""
    try:
        # Build documentation structure from docs/ directory
        docs_structure = _build_docs_structure()
        
        # Handle root docs page - show index/overview
        if not doc_path:
            doc_path = 'index'
        
        # If requesting a category (getting-started, advanced, etc.), show category index
        if doc_path in ['getting-started', 'configuration', 'advanced', 'development', 'specs']:
            content, breadcrumbs = _load_category_index(doc_path, docs_structure)
        else:
            # Load specific document
            content, breadcrumbs = _load_documentation_file(doc_path, docs_structure)
        
        return render_template('documentation.html', 
                             content=content, 
                             docs_structure=docs_structure,
                             breadcrumbs=breadcrumbs,
                             current_path=doc_path,
                             is_markdown=isinstance(content, dict))
    except Exception as e:
        logger.error(f"Error loading documentation: {e}")
        return render_template('documentation.html', 
                             content="<p>Error loading documentation.</p>",
                             docs_structure={},
                             breadcrumbs=[],
                             current_path=doc_path)

def _build_docs_structure():
    """Build hierarchical structure of all documentation files"""
    docs_base = Path('docs')
    structure = {
        'getting-started': {
            'title': 'Getting Started',
            'description': 'Quick start guides and introduction to ISEE',
            'files': []
        },
        'configuration': {
            'title': 'Configuration',
            'description': 'Setup and configuration guides',
            'files': []
        },
        'advanced': {
            'title': 'Advanced Features',
            'description': 'In-depth features and capabilities',
            'files': []
        },
        'development': {
            'title': 'Development',
            'description': 'Technical architecture and development guides',
            'files': []
        }
    }
    
    # Add specs if it exists
    specs_path = Path('specs')
    if specs_path.exists():
        structure['specs'] = {
            'title': 'Specifications',
            'description': 'Technical specifications and implementation details',
            'files': []
        }
    
    # Scan docs directory
    if docs_base.exists():
        for category in structure.keys():
            category_path = docs_base / category
            if category_path.exists():
                for md_file in category_path.glob('*.md'):
                    if md_file.name != 'README.md':  # Skip READMEs for now
                        file_info = {
                            'name': md_file.stem,
                            'title': _get_title_from_file(md_file),
                            'path': f"{category}/{md_file.stem}",
                            'file_path': md_file
                        }
                        structure[category]['files'].append(file_info)
    
    # Add specs files
    if specs_path.exists():
        for md_file in specs_path.glob('*.md'):
            file_info = {
                'name': md_file.stem,
                'title': _get_title_from_file(md_file),
                'path': f"specs/{md_file.stem}",
                'file_path': md_file
            }
            structure['specs']['files'].append(file_info)
    
    return structure

def _get_title_from_file(file_path):
    """Extract title from markdown file (first # heading or filename)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('# '):
                    return line[2:].strip()
                elif line.startswith('## '):
                    return line[3:].strip()
        # Fallback to filename with formatting
        return file_path.stem.replace('_', ' ').replace('-', ' ').title()
    except:
        return file_path.stem.replace('_', ' ').replace('-', ' ').title()

def _load_category_index(category, docs_structure):
    """Generate index page for a documentation category"""
    if category not in docs_structure:
        return "<p>Category not found.</p>", [("Documentation", "/docs")]
    
    cat_info = docs_structure[category]
    content = f"<h1>{cat_info['title']}</h1>\n"
    content += f"<p class='category-description'>{cat_info['description']}</p>\n\n"
    
    if cat_info['files']:
        content += "<div class='file-list'>\n"
        for file_info in cat_info['files']:
            content += f"<div class='file-item'>\n"
            content += f"  <h3><a href='/docs/{file_info['path']}'>{file_info['title']}</a></h3>\n"
            content += f"</div>\n"
        content += "</div>\n"
    else:
        content += "<p>No documentation files found in this category.</p>"
    
    breadcrumbs = [
        ("Documentation", "/docs"),
        (cat_info['title'], f"/docs/{category}")
    ]
    
    return content, breadcrumbs

def _load_documentation_file(doc_path, docs_structure):
    """Load specific documentation file"""
    # Handle special case for index
    if doc_path == 'index':
        return _load_docs_index(docs_structure), [("Documentation", "/docs")]
    
    # Find the file in structure
    file_path = None
    category = None
    title = "Documentation"
    
    # Check if it's a category/file pattern
    if '/' in doc_path:
        cat, filename = doc_path.split('/', 1)
        if cat in docs_structure:
            for file_info in docs_structure[cat]['files']:
                if file_info['name'] == filename:
                    file_path = file_info['file_path']
                    category = cat
                    title = file_info['title']
                    break
    
    if not file_path:
        return "<p>Documentation file not found.</p>", [("Documentation", "/docs")]
    
    # Load raw markdown for client-side rendering
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Build breadcrumbs
        breadcrumbs = [("Documentation", "/docs")]
        if category:
            breadcrumbs.append((docs_structure[category]['title'], f"/docs/{category}"))
        breadcrumbs.append((title, f"/docs/{doc_path}"))
        
        # Return raw markdown with metadata for client-side rendering
        return {
            'markdown': markdown_content,
            'title': title,
            'type': 'markdown'
        }, breadcrumbs
    except Exception as e:
        logger.error(f"Error reading documentation file {file_path}: {e}")
        return "<p>Error loading documentation file.</p>", [("Documentation", "/docs")]

def _load_docs_index(docs_structure):
    """Generate main documentation index page"""
    content = "<h1>ISEE Meta Framework Documentation</h1>\n"
    content += "<p class='docs-intro'>Comprehensive guides and documentation for the ISEE Meta Framework system.</p>\n\n"
    
    for category, cat_info in docs_structure.items():
        if cat_info['files']:  # Only show categories with files
            content += f"<div class='category-section'>\n"
            content += f"  <h2><a href='/docs/{category}'>{cat_info['title']}</a></h2>\n"
            content += f"  <p class='category-description'>{cat_info['description']}</p>\n"
            content += f"  <div class='file-preview'>\n"
            
            # Show first few files as preview
            for file_info in cat_info['files'][:3]:
                content += f"    <div class='file-preview-item'>\n"
                content += f"      <a href='/docs/{file_info['path']}'>{file_info['title']}</a>\n"
                content += f"    </div>\n"
            
            if len(cat_info['files']) > 3:
                content += f"    <div class='file-preview-more'>\n"
                content += f"      <a href='/docs/{category}'>View all {len(cat_info['files'])} files →</a>\n"
                content += f"    </div>\n"
            
            content += f"  </div>\n"
            content += f"</div>\n\n"
    
    return content

@app.route('/api/extract_cognitive_diversity', methods=['POST'])
def extract_cognitive_diversity():
    """Extract cognitive diversity metadata for a given execution"""
    try:
        data = request.json
        execution_id = data.get('execution_id')
        
        if not execution_id:
            return jsonify({'success': False, 'error': 'No execution ID provided'})
        
        # Get run directory from execution status (handles exec_* -> run_* mapping)
        execution_status = demo.execution_status.get(execution_id, {})
        run_directory = execution_status.get('run_directory')
        
        if not run_directory:
            # Fallback: try direct execution_id if it's already in run_* format
            if execution_id.startswith('run_'):
                run_directory = f"data/output/{execution_id}"
            else:
                return jsonify({'success': False, 'error': f'Run directory not found for execution: {execution_id}'})
        
        if not os.path.exists(run_directory):
            # Additional fallback: look for similar run directories with close timestamps
            if execution_id.startswith('run_'):
                # Extract date prefix (run_YYYYMMDD_) and look for runs within a few minutes
                import glob
                date_prefix = execution_id[:13]  # run_YYYYMMDD_
                time_part = execution_id[13:]    # HHMMSS
                
                if len(time_part) == 6:  # HHMMSS format
                    pattern = f"data/output/{date_prefix}*"
                    matching_dirs = glob.glob(pattern)
                    
                    # Find the closest timestamp
                    if matching_dirs:
                        target_time = int(time_part)
                        closest_dir = None
                        min_diff = float('inf')
                        
                        for dir_path in matching_dirs:
                            dir_name = os.path.basename(dir_path)
                            if len(dir_name) >= 19:  # run_YYYYMMDD_HHMMSS
                                dir_time_str = dir_name[13:19]
                                try:
                                    dir_time = int(dir_time_str)
                                    time_diff = abs(dir_time - target_time)
                                    if time_diff < min_diff and time_diff <= 300:  # Within 5 minutes
                                        min_diff = time_diff
                                        closest_dir = dir_path
                                except ValueError:
                                    continue
                        
                        if closest_dir:
                            run_directory = closest_dir
                            demo.logger.info(f"Found close timestamp match: {execution_id} -> {os.path.basename(closest_dir)}")
            
            if not os.path.exists(run_directory):
                return jsonify({'success': False, 'error': f'Run directory does not exist: {run_directory}'})
        
        # Extract run_id from directory path for the response
        run_id = os.path.basename(run_directory)
        
        # Extract cognitive diversity metadata
        # Use absolute paths and explicit Python to handle remote deployment
        import sys
        script_path = os.path.join(os.getcwd(), 'cognitive_diversity_extractor.py')
        
        # Enhanced subprocess call with better error handling
        try:
            result = subprocess.run([
                sys.executable, script_path, run_directory
            ], capture_output=True, text=True, cwd=os.getcwd(), timeout=300)
            
            if result.returncode == 0:
                return jsonify({'success': True, 'run_id': run_id})
            else:
                # Log detailed error for debugging
                detailed_error = f'Extraction failed. Return code: {result.returncode}'
                if result.stderr:
                    detailed_error += f', STDERR: {result.stderr}'
                if result.stdout:
                    detailed_error += f', STDOUT: {result.stdout}'
                demo.logger.error(f"Cognitive diversity extraction failed: {detailed_error}")
                
                # Return user-friendly error message
                user_error = 'Cognitive diversity extraction failed'
                if 'FileNotFoundError' in str(result.stderr):
                    user_error += ': Required files not found'
                elif 'ModuleNotFoundError' in str(result.stderr):
                    user_error += ': Missing Python dependencies'
                elif 'PermissionError' in str(result.stderr):
                    user_error += ': File permission denied'
                else:
                    user_error += f': {result.stderr[:200] if result.stderr else "Unknown error"}'
                    
                return jsonify({'success': False, 'error': user_error})
                
        except subprocess.TimeoutExpired:
            error_msg = 'Extraction timed out after 5 minutes'
            demo.logger.error(error_msg)
            return jsonify({'success': False, 'error': error_msg})
        except FileNotFoundError as e:
            error_msg = f'Script not found: {script_path}. Error: {str(e)}'
            demo.logger.error(error_msg)
            return jsonify({'success': False, 'error': error_msg})
        except Exception as e:
            error_msg = f'Subprocess error: {str(e)}'
            demo.logger.error(error_msg)
            return jsonify({'success': False, 'error': error_msg})
            
    except Exception as e:
        demo.logger.error(f"Error extracting cognitive diversity: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/cognitive_diversity_explorer/<run_id>')
def cognitive_diversity_explorer(run_id):
    """Serve the cognitive diversity explorer for a specific run"""
    run_directory = f"data/output/{run_id}"
    index_file = f"{run_directory}/cognitive_diversity_index.json"
    
    if not os.path.exists(index_file):
        return "Cognitive diversity data not found. Please extract metadata first.", 404
    
    # Serve the cognitive diversity explorer HTML
    explorer_html = f"{run_directory}/cognitive_diversity_explorer.html"
    
    if not os.path.exists(explorer_html):
        # Create the explorer HTML if it doesn't exist
        try:
            from launch_cognitive_explorer import create_enhanced_web_interface
            create_enhanced_web_interface(index_file, explorer_html)
        except Exception as e:
            demo.logger.error(f"Error creating cognitive diversity explorer: {e}")
            return f"Error creating explorer interface: {str(e)}", 500
    
    # Update the HTML to use the correct API endpoint with run_id
    try:
        with open(explorer_html, 'r') as f:
            html_content = f.read()
        
        # Replace the generic API endpoint with the run-specific one
        updated_html = html_content.replace(
            "const response = await fetch('/api/cognitive_diversity_data');",
            f"const response = await fetch('/api/cognitive_diversity_data/{run_id}');"
        )
        
        # Also update the raw response file API endpoint
        updated_html = updated_html.replace(
            "const response = await fetch(`/api/raw-response?file=${encodeURIComponent(file_path)}`);",
            f"const response = await fetch(`/api/raw-response/{run_id}?file=${{encodeURIComponent(file_path)}}`);"
        )
        
        # Alternative pattern that might be used
        updated_html = updated_html.replace(
            "/api/raw-response?file=",
            f"/api/raw-response/{run_id}?file="
        )
        
        # Write the updated HTML back
        with open(explorer_html, 'w') as f:
            f.write(updated_html)
            
    except Exception as e:
        demo.logger.error(f"Error updating explorer HTML: {e}")
        # Continue serving the original file
    
    return send_file(explorer_html)

@app.route('/api/cognitive_diversity_data/<run_id>')
def cognitive_diversity_data(run_id):
    """Serve cognitive diversity data as JSON API"""
    index_file = f"data/output/{run_id}/cognitive_diversity_index.json"
    
    if not os.path.exists(index_file):
        return jsonify({'error': 'Cognitive diversity data not found'}), 404
    
    try:
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        return jsonify(data)
    except Exception as e:
        demo.logger.error(f"Error loading cognitive diversity data: {e}")
        return jsonify({'error': f'Error loading data: {str(e)}'}), 500

@app.route('/api/raw-response/<run_id>')
def serve_raw_response(run_id):
    """Serve raw response files for cognitive diversity explorer"""
    try:
        # Get the file parameter from query string
        file_path = request.args.get('file')
        
        if not file_path:
            return jsonify({'error': 'Missing file parameter'}), 400
        
        # Security: ensure the file path is within the expected directory structure
        # and doesn't contain path traversal attempts
        if '..' in file_path or file_path.startswith('/'):
            return jsonify({'error': 'Invalid file path'}), 403
        
        # Construct full path to the raw response file
        run_directory = f"data/output/{run_id}"
        full_file_path = os.path.join(run_directory, file_path)
        
        if not os.path.exists(full_file_path):
            return jsonify({'error': f'File not found: {file_path}'}), 404
        
        # Read and serve the file content
        with open(full_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        
    except Exception as e:
        demo.logger.error(f"Error serving raw response file: {e}")
        return jsonify({'error': f'Error reading file: {str(e)}'}), 500

@app.route('/about')
def about():
    """About page with editable content from markdown file"""
    try:
        content_path = Path('content/about.md')
        if content_path.exists():
            with open(content_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            html_content = markdown.markdown(
            markdown_content,
            extensions=['codehilite', 'fenced_code', 'tables', 'toc'],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': False  # We'll use Prism.js instead
                }
            }
        )
            return render_template('about.html', content=html_content)
        else:
            return render_template('about.html', content="<p>About content not found.</p>")
    except Exception as e:
        logger.error(f"Error loading about page: {e}")
        return render_template('about.html', content="<p>Error loading about content.</p>")

if __name__ == '__main__':
    import os
    
    # Ensure output directory exists
    Path("data/output").mkdir(parents=True, exist_ok=True)
    
    # Get port from environment (Railway sets PORT) or default to 5001
    port = int(os.environ.get('PORT', 5001))
    
    # Run development server on specified port
    print("🚀 Starting ISEE Meta Framework...")
    print(f"📱 Open your browser to: http://localhost:{port}/isee-ui")
    print("💡 For full screen mode, press F11")
    
    # Use debug=False in production (when PORT env var is set)
    debug_mode = os.environ.get('PORT') is None
    app.run(debug=debug_mode, host='0.0.0.0', port=port)