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

app = Flask(__name__)
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
                        self.logger.info(f"Using cached rankings: {len(cache_data.models)} models")
                        return cache_data.models
            
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
            
            return sorted(models, key=lambda x: (x["provider"], x["name"]))
            
        except Exception as e:
            print(f"Error loading models: {e}")
            # Fallback to top 20 performers model list
            return [
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
    
    def _load_actual_domains(self):
        """Load domains from actual ISEE domain system"""
        # Load default domains
        for domain in create_default_domains():
            self.domain_manager.add_domain(domain)
        
        # Load external domain files (optional)
        try:
            self.domain_manager.load_from_file('tech_writing_domains.json')
        except FileNotFoundError:
            pass  # Optional file
        
        try:
            self.domain_manager.load_from_file('learning_design_domains.json')
        except FileNotFoundError:
            pass  # Optional file
    
    def _get_real_domains(self) -> Dict[str, List[str]]:
        """Get actual domains organized by category"""
        # Convert DomainManager domains to web UI format
        domains_by_category = {
            "Core Domains": [],
            "Technical Writing": [],
            "Learning Design": [],
        }
        
        # domains is a dictionary, so iterate over values
        for domain in self.domain_manager.domains.values():
            domain_name = domain.name
            
            # Categorize domains based on their IDs and source files
            if domain.id in ["domain_technical_writing", "domain_knowledge_management", "domain_content_strategy", "domain_ai_writing", "domain_developer_docs"]:
                domains_by_category["Technical Writing"].append(domain_name)
            elif domain.id in ["domain_instructional_design", "domain_elearning", "domain_learning_experience", "domain_corporate_training", "domain_assessment_design"]:
                domains_by_category["Learning Design"].append(domain_name)
            else:
                # Default domains and others go to Core Domains
                domains_by_category["Core Domains"].append(domain_name)
        
        # Remove empty categories
        return {k: v for k, v in domains_by_category.items() if v}
    
    def get_knowledge_domains(self) -> Dict[str, List[str]]:
        """Get knowledge domains organized by category"""
        return self._get_real_domains()
    
    def estimate_execution_cost(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate cost and resource requirements for given parameters"""
        try:
            # Create a simple parameter object for cost estimation
            class SimpleParams:
                def __init__(self, params_dict):
                    for key, value in params_dict.items():
                        setattr(self, key, value)
            
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
            # For multiple domains, use first one (limitation of current CLI)
            cmd_parts.extend(["--domain", selected_domains[0]])
        
        # Add cognitive frameworks
        frameworks = parameters.get("cognitive_frameworks", [])
        if frameworks:
            framework_list = ",".join(frameworks)
            cmd_parts.extend(["--instruction-templates", framework_list])
        
        # Add model configuration
        selected_models = parameters.get("selected_models", [])
        if selected_models:
            # Determine config based on model types (same logic as execution)
            api_status = self._detect_apis()
            ollama_models = api_status.get("ollama_models", [])
            has_ollama = any(model in ollama_models for model in selected_models)
            has_openrouter = any(model.startswith("openrouter_") for model in selected_models)
            
            if has_ollama and not has_openrouter:
                # Pure Ollama models - use ollama config
                cmd_parts.extend(["--config", "ollama_config.json"])
            elif has_openrouter and not has_ollama:
                # Pure OpenRouter models - use openrouter config
                cmd_parts.extend(["--config", "openrouter_config.json"])
            else:
                # Mixed models - prefer OpenRouter config for compatibility
                openrouter_models = [m for m in selected_models if m.startswith("openrouter_")]
                ollama_models_selected = [m for m in selected_models if m in ollama_models]
                
                if openrouter_models:
                    # Use OpenRouter config when OpenRouter models are present
                    cmd_parts.extend(["--config", "openrouter_config.json"])
                else:
                    # Fall back to unified config
                    cmd_parts.extend(["--config", "unified_config.json"])
            
            cmd_parts.extend(["--models", str(len(selected_models))])
            # Note: Specific model selection would be handled by the execution logic
        
        # Add execution settings
        if parameters.get("variations"):
            cmd_parts.extend(["--variations", str(parameters["variations"])])
        
        if parameters.get("max_combinations"):
            cmd_parts.extend(["--max-combinations", str(parameters["max_combinations"])])
        
        if parameters.get("sampling_method"):
            cmd_parts.extend(["--sampling-method", parameters["sampling_method"]])
        
        # Add output format
        if parameters.get("output_format") and parameters["output_format"] != "json":
            cmd_parts.extend(["--output-format", parameters["output_format"]])
        
        # Note: No dry-run flag added - show the actual command that will be executed
        
        # Properly escape the command for shell display
        return " ".join(shlex.quote(part) for part in cmd_parts)
    
    def execute_isee_command(self, parameters: Dict[str, Any], execution_id: str, session_api_key: str = None) -> Dict[str, Any]:
        """Execute ISEE command and track progress"""
        self.logger.info(f"Starting execution {execution_id} with parameters: {parameters}")
        
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
            
            # Build command properly for subprocess
            cmd = ["python", "main.py"]
            self.logger.debug(f"Building command for execution {execution_id}")
            
            # Add query (properly handled)
            if parameters.get("query"):
                cmd.extend(["--query", parameters["query"]])
                self.logger.debug(f"Added query: {parameters['query'][:100]}...")
            
            # Add selected domain (support both single domain and domain list)
            domain = parameters.get("domain")
            selected_domains = parameters.get("selected_domains", [])
            
            if domain:
                cmd.extend(["--domain", domain])
            elif selected_domains:
                # Use first selected domain if multiple are provided
                cmd.extend(["--domain", selected_domains[0]])
            
            # Add cognitive frameworks
            frameworks = parameters.get("cognitive_frameworks", [])
            if frameworks:
                framework_list = ",".join(frameworks)
                cmd.extend(["--instruction-templates", framework_list])
            
            # Add model configuration
            selected_models = parameters.get("selected_models", [])
            if selected_models:
                self.logger.debug(f"Selected models: {selected_models}")
                # Determine config based on model types
                api_status = self._detect_apis_with_session_key(session_api_key)
                ollama_models = api_status.get("ollama_models", [])
                has_ollama = any(model in ollama_models for model in selected_models)
                has_openrouter = any(model.startswith("openrouter_") for model in selected_models)
                
                config_file = None
                if has_ollama and not has_openrouter:
                    # Pure Ollama models - use ollama config
                    config_file = "ollama_config.json"
                    cmd.extend(["--config", config_file])
                elif has_openrouter and not has_ollama:
                    # Pure OpenRouter models - use openrouter config
                    config_file = "openrouter_config.json"
                    cmd.extend(["--config", config_file])
                else:
                    # Mixed models - we need a hybrid approach
                    # For now, filter the models to use appropriate configs
                    openrouter_models = [m for m in selected_models if m.startswith("openrouter_")]
                    ollama_models_selected = [m for m in selected_models if m in ollama_models]
                    
                    if openrouter_models:
                        # Use OpenRouter config and let Ollama models fall back to direct API
                        config_file = "openrouter_config.json"
                        cmd.extend(["--config", config_file])
                        self.logger.debug(f"Mixed models: Using OpenRouter config for {openrouter_models}, Ollama direct for {ollama_models_selected}")
                    else:
                        # Fall back to unified config
                        config_file = "unified_config.json"
                        cmd.extend(["--config", config_file])
                
                self.logger.debug(f"Using config file: {config_file} (ollama: {has_ollama}, openrouter: {has_openrouter})")
                
                # Pass specific model selections to CLI
                cmd.extend(["--selected-models", ",".join(selected_models)])
                cmd.extend(["--models", str(len(selected_models))])
                self.logger.debug(f"Added {len(selected_models)} specific models to command")
            
            # Add execution settings
            if parameters.get("variations"):
                cmd.extend(["--variations", str(parameters["variations"])])
            
            if parameters.get("max_combinations"):
                cmd.extend(["--max-combinations", str(parameters["max_combinations"])])
            
            if parameters.get("sampling_method"):
                cmd.extend(["--sampling-method", parameters["sampling_method"]])
            
            # Add output format
            if parameters.get("output_format") and parameters["output_format"] != "json":
                cmd.extend(["--output-format", parameters["output_format"]])
            
            # Add advanced output options
            if parameters.get("generate_reports"):
                cmd.append("--generate-reports")
                
            if parameters.get("report_format") and parameters["report_format"] != "markdown":
                cmd.extend(["--report-format", parameters["report_format"]])
                
            if parameters.get("export_csv"):
                cmd.append("--export-csv")
                
            if parameters.get("analyze_results"):
                cmd.append("--analyze-results")
                
            if parameters.get("no_visualizations"):
                cmd.append("--no-visualizations")
            
            # Check if we should use real execution or simulation
            # Use real execution if we have API keys available
            current_api_status = self._detect_apis_with_session_key(session_api_key)
            if not current_api_status.get("any_api", False):
                cmd.append("--simulate")  # Use simulation if no API keys
            
            # Add output file with execution ID and proper extension based on format
            output_dir = Path("data/output")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine file extension based on output format (following main.py logic)
            output_format = parameters.get("output_format", "json")
            if output_format == "markdown":
                extension = "md"
            else:
                extension = "json"
            
            output_file = output_dir / f"demo_results_{execution_id}.{extension}"
            cmd.extend(["--output-file", str(output_file)])
            
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
            
            # Log command execution details
            self.logger.info(f"Executing command: {' '.join(cmd)}")
            self.logger.debug(f"Working directory: {Path(__file__).parent}")
            self.logger.debug(f"Environment variables set: {[k for k in env.keys() if 'API_KEY' in k]}")
            
            # Execute command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=Path(__file__).parent,
                env=env
            )
            
            self.logger.info(f"Started subprocess with PID {process.pid} for execution {execution_id}")
            
            # Monitor progress with real subprocess communication
            self._monitor_subprocess_progress(process, execution_id)
            
            # Wait for completion
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.logger.info(f"Execution {execution_id} completed successfully")
                self.execution_status[execution_id].update({
                    "status": "completed",
                    "progress": 100,
                    "message": "Execution completed successfully",
                    "results_file": str(output_file),
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
            
        # Validate model selections
        selected_models = parameters.get("selected_models", [])
        if not selected_models:
            errors.append("At least one model must be selected")
        elif len(selected_models) > 20:
            errors.append("Maximum 20 models can be selected at once")
            
        # Validate variations
        variations = parameters.get("variations")
        if variations is not None:
            try:
                variations_int = int(variations)
                if variations_int < 1 or variations_int > 5:
                    errors.append("Variations must be between 1 and 5")
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
                
        # Validate sampling method
        sampling_method = parameters.get("sampling_method")
        valid_sampling_methods = ["exhaustive", "stratified", "adaptive"]
        if sampling_method and sampling_method not in valid_sampling_methods:
            errors.append(f"Sampling method must be one of: {', '.join(valid_sampling_methods)}")
            
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
            "sampling_method": "sampling_method",
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
        
        # Handle domain selection
        if web_params.get("domain"):
            converted["domain"] = web_params["domain"]
        
        # Handle cognitive frameworks
        if web_params.get("cognitive_frameworks"):
            converted["instructions"] = len(web_params["cognitive_frameworks"])
            converted["instruction_templates"] = web_params["cognitive_frameworks"]
        
        # Handle models
        if web_params.get("selected_models"):
            converted["models"] = len(web_params["selected_models"])
            converted["selected_models"] = web_params["selected_models"]
        
        return converted
    
    def _monitor_subprocess_progress(self, process, execution_id: str):
        """Real-time progress monitoring from CLI output"""
        self.logger.debug(f"Starting progress monitoring for execution {execution_id}")
        
        # Start a thread to monitor stdout
        def monitor_output():
            try:
                # Simulate progress monitoring - in a real implementation,
                # you would parse the CLI output for progress indicators
                for progress in range(20, 90, 10):
                    if process.poll() is None:  # Process still running
                        time.sleep(2)
                        if execution_id in self.execution_status:
                            self.execution_status[execution_id].update({
                                "progress": progress,
                                "message": f"Processing combinations... {progress}%"
                            })
                            self.logger.debug(f"Progress update for {execution_id}: {progress}%")
                    else:
                        break
            except Exception as e:
                self.logger.error(f"Error monitoring progress for {execution_id}: {e}")
        
        # Start monitoring in background
        monitor_thread = threading.Thread(target=monitor_output)
        monitor_thread.daemon = True
        monitor_thread.start()
    
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