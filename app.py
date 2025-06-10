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

app = Flask(__name__)
app.secret_key = os.urandom(24)

class ISEEWebDemo:
    """Web demo controller that leverages existing ISEE backend logic"""
    
    def __init__(self):
        self.cost_estimator = CostEstimator()
        self.framework_visualizer = CognitiveFrameworkVisualizer()
        self.model_collections = OpenRouterModelCollections()
        self.dashboard = ConfigurationDashboard()
        self.parameter_context = ParameterContext()
        self.guardrails = ISEEGuardrails()
        self.execution_status = {}
        
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
    
    def get_individual_models(self) -> List[Dict[str, Any]]:
        """Get individual LLM models for manual selection"""
        # Load models from OpenRouter config
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
            
            # Add some common models if config is limited
            if len(models) < 10:
                additional_models = [
                    {
                        "id": "gpt-4o",
                        "name": "GPT-4o",
                        "provider": "OpenAI",
                        "model_param": "openai/gpt-4o",
                        "cost_tier": "premium",
                        "features": ["reasoning", "analysis"],
                        "description": "OpenAI's latest multimodal model"
                    },
                    {
                        "id": "claude-3-5-sonnet",
                        "name": "Claude 3.5 Sonnet",
                        "provider": "Anthropic",
                        "model_param": "anthropic/claude-3-5-sonnet",
                        "cost_tier": "premium",
                        "features": ["reasoning", "coding", "analysis"],
                        "description": "Anthropic's most capable model"
                    },
                    {
                        "id": "gemini-2-flash-exp",
                        "name": "Gemini 2.0 Flash",
                        "provider": "Google",
                        "model_param": "google/gemini-2.0-flash-exp",
                        "cost_tier": "balanced",
                        "features": ["fast", "multimodal"],
                        "description": "Google's fast multimodal model"
                    },
                    {
                        "id": "llama-3-2-90b",
                        "name": "Llama 3.2 90B",
                        "provider": "Meta",
                        "model_param": "meta-llama/llama-3.2-90b-instruct",
                        "cost_tier": "balanced",
                        "features": ["reasoning", "large_context"],
                        "description": "Meta's open-source flagship model"
                    },
                    {
                        "id": "qwen-2-5-72b",
                        "name": "Qwen 2.5 72B",
                        "provider": "Alibaba",
                        "model_param": "qwen/qwen-2.5-72b-instruct",
                        "cost_tier": "budget",
                        "features": ["coding", "multilingual"],
                        "description": "Alibaba's coding-optimized model"
                    },
                    {
                        "id": "deepseek-v3",
                        "name": "DeepSeek V3",
                        "provider": "DeepSeek",
                        "model_param": "deepseek-ai/deepseek-v3",
                        "cost_tier": "budget",
                        "features": ["reasoning", "coding"],
                        "description": "DeepSeek's latest reasoning model"
                    },
                    {
                        "id": "grok-beta",
                        "name": "Grok Beta",
                        "provider": "xAI",
                        "model_param": "x-ai/grok-beta",
                        "cost_tier": "premium",
                        "features": ["reasoning", "real_time"],
                        "description": "xAI's Grok model with real-time data"
                    },
                    {
                        "id": "mistral-large-2",
                        "name": "Mistral Large 2",
                        "provider": "Mistral",
                        "model_param": "mistralai/mistral-large-2",
                        "cost_tier": "balanced",
                        "features": ["reasoning", "multilingual"],
                        "description": "Mistral's flagship model"
                    },
                    {
                        "id": "command-r-plus",
                        "name": "Command R+",
                        "provider": "Cohere",
                        "model_param": "cohere/command-r-plus",
                        "cost_tier": "balanced",
                        "features": ["reasoning", "retrieval"],
                        "description": "Cohere's enterprise model"
                    },
                    {
                        "id": "nova-pro",
                        "name": "Nova Pro",
                        "provider": "Amazon",
                        "model_param": "amazon/nova-pro",
                        "cost_tier": "balanced",
                        "features": ["multimodal", "fast"],
                        "description": "Amazon's multimodal model"
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
            # Fallback to basic model list
            return [
                {
                    "id": "gpt-4o",
                    "name": "GPT-4o",
                    "provider": "OpenAI",
                    "model_param": "openai/gpt-4o",
                    "cost_tier": "premium",
                    "features": ["reasoning"],
                    "description": "OpenAI's latest model"
                },
                {
                    "id": "claude-3-5-sonnet",
                    "name": "Claude 3.5 Sonnet",
                    "provider": "Anthropic",
                    "model_param": "anthropic/claude-3-5-sonnet",
                    "cost_tier": "premium",
                    "features": ["reasoning"],
                    "description": "Anthropic's flagship model"
                },
                {
                    "id": "gemini-2-flash",
                    "name": "Gemini 2.0 Flash",
                    "provider": "Google",
                    "model_param": "google/gemini-2.0-flash-exp",
                    "cost_tier": "balanced",
                    "features": ["fast"],
                    "description": "Google's fast model"
                }
            ]
    
    def get_knowledge_domains(self) -> Dict[str, List[str]]:
        """Get knowledge domains organized by category"""
        # This would normally come from domain_manager.py, but we'll create a simplified version
        return {
            "Technology & Innovation": [
                "Artificial Intelligence & Machine Learning",
                "Software Development & Engineering",
                "Data Science & Analytics",
                "Cybersecurity & Privacy",
                "Blockchain & Cryptocurrency",
                "Internet of Things (IoT)",
                "Quantum Computing",
                "Robotics & Automation"
            ],
            "Business & Strategy": [
                "Strategic Planning & Management",
                "Digital Transformation",
                "Product Management",
                "Marketing & Brand Strategy",
                "Financial Analysis & Investment",
                "Operations & Supply Chain",
                "Human Resources & Organizational Development",
                "Entrepreneurship & Startups"
            ],
            "Science & Research": [
                "Biology & Life Sciences",
                "Chemistry & Materials Science",
                "Physics & Engineering",
                "Environmental Science & Sustainability",
                "Medical & Healthcare Research",
                "Psychology & Cognitive Science",
                "Mathematics & Statistics",
                "Space & Astronomy"
            ],
            "Creative & Content": [
                "Creative Writing & Storytelling",
                "Visual Design & User Experience",
                "Film & Video Production",
                "Music & Audio Production",
                "Game Design & Development",
                "Marketing Content & Copywriting",
                "Educational Content Development",
                "Social Media & Digital Marketing"
            ],
            "Education & Learning": [
                "Curriculum Design & Development",
                "Educational Technology",
                "Adult Learning & Professional Development",
                "K-12 Education",
                "Higher Education & Research",
                "Language Learning & Linguistics",
                "Training & Skills Development",
                "Assessment & Evaluation"
            ],
            "Social & Cultural": [
                "Social Impact & Nonprofit",
                "Cultural Studies & Anthropology",
                "Political Science & Policy",
                "History & Historical Analysis",
                "Philosophy & Ethics",
                "Sociology & Community Development",
                "International Relations & Geopolitics",
                "Law & Legal Studies"
            ],
            "Health & Wellness": [
                "Mental Health & Psychology",
                "Nutrition & Wellness",
                "Healthcare & Medical Practice",
                "Public Health & Epidemiology",
                "Fitness & Physical Performance",
                "Alternative & Holistic Medicine",
                "Healthcare Technology",
                "Medical Research & Clinical Trials"
            ],
            "Custom": [
                "Custom Domain (specify in query)"
            ]
        }
    
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
            # Determine config based on model types
            has_ollama = any(model in selected_models for model in self._detect_apis().get("ollama_models", []))
            has_openrouter = any(not model in self._detect_apis().get("ollama_models", []) for model in selected_models)
            
            if has_ollama and not has_openrouter:
                # Pure Ollama models - use ollama config
                cmd_parts.extend(["--config", "ollama_config.json"])
            elif has_openrouter and not has_ollama:
                # Pure OpenRouter models - use openrouter config
                cmd_parts.extend(["--config", "openrouter_config.json"])
            else:
                # Mixed models - use unified config that supports both
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
    
    def execute_isee_command(self, parameters: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
        """Execute ISEE command and track progress"""
        try:
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
            
            # Add query (properly handled)
            if parameters.get("query"):
                cmd.extend(["--query", parameters["query"]])
            
            # Add selected domains
            selected_domains = parameters.get("selected_domains", [])
            if selected_domains:
                cmd.extend(["--domain", selected_domains[0]])
            
            # Add cognitive frameworks
            frameworks = parameters.get("cognitive_frameworks", [])
            if frameworks:
                framework_list = ",".join(frameworks)
                cmd.extend(["--instruction-templates", framework_list])
            
            # Add model configuration
            selected_models = parameters.get("selected_models", [])
            if selected_models:
                # Determine config based on model types
                has_ollama = any(model in selected_models for model in self._detect_apis().get("ollama_models", []))
                has_openrouter = any(not model in self._detect_apis().get("ollama_models", []) for model in selected_models)
                
                if has_ollama and not has_openrouter:
                    # Pure Ollama models - use ollama config
                    cmd.extend(["--config", "ollama_config.json"])
                elif has_openrouter and not has_ollama:
                    # Pure OpenRouter models - use openrouter config
                    cmd.extend(["--config", "openrouter_config.json"])
                else:
                    # Mixed models - use unified config that supports both
                    cmd.extend(["--config", "unified_config.json"])
                
                cmd.extend(["--models", str(len(selected_models))])
            
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
            
            # Check if we should use real execution or simulation
            # Use real execution if we have API keys available
            current_api_status = self._detect_apis()
            if not current_api_status.get("any_api", False):
                cmd.append("--simulate")  # Use simulation if no API keys
            
            # Add output file with execution ID
            output_dir = Path("data/output")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"demo_results_{execution_id}.json"
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
            if 'openrouter_api_key' in session:
                env['OPENROUTER_API_KEY'] = session['openrouter_api_key']
            
            # Execute command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=Path(__file__).parent,
                env=env
            )
            
            # Monitor progress (simplified - in reality this would parse actual output)
            for progress in range(20, 90, 10):
                time.sleep(2)  # Simulate processing time
                if execution_id in self.execution_status:
                    self.execution_status[execution_id].update({
                        "progress": progress,
                        "message": f"Processing combinations... {progress}%"
                    })
            
            # Wait for completion
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
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
                self.execution_status[execution_id].update({
                    "status": "error",
                    "progress": 0,
                    "message": f"Execution failed: {stderr}",
                    "end_time": datetime.now().isoformat(),
                    "error": stderr
                })
        
        except Exception as e:
            self.execution_status[execution_id].update({
                "status": "error",
                "progress": 0,
                "message": f"Execution error: {str(e)}",
                "end_time": datetime.now().isoformat(),
                "error": str(e)
            })
        
        return self.execution_status[execution_id]
    
    def _convert_web_params_to_isee(self, web_params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert web UI parameters to format expected by ISEE backend"""
        converted = {}
        
        # Map web parameters to ISEE parameter names
        param_mapping = {
            "query": "query",
            "variations": "variations",
            "max_combinations": "max_combinations",
            "sampling_method": "sampling_method"
        }
        
        for web_key, isee_key in param_mapping.items():
            if web_key in web_params and web_params[web_key]:
                converted[isee_key] = web_params[web_key]
        
        # Handle frameworks
        if web_params.get("cognitive_frameworks"):
            converted["instructions"] = len(web_params["cognitive_frameworks"])
            converted["instruction_templates"] = web_params["cognitive_frameworks"]
        
        # Handle models
        if web_params.get("selected_models"):
            converted["models"] = len(web_params["selected_models"])
            converted["selected_models"] = web_params["selected_models"]
        
        return converted
    
    def _detect_apis(self) -> Dict[str, Any]:
        """Detect available API providers and Ollama models (adapted from command wizard)"""
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
        if 'openrouter_api_key' in session:
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
    
    # Start execution in background thread
    thread = threading.Thread(
        target=demo.execute_isee_command,
        args=(parameters, execution_id)
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
    """Download results file"""
    status = demo.execution_status.get(execution_id, {})
    results_file = status.get("results_file")
    
    if results_file and Path(results_file).exists():
        return send_file(results_file, as_attachment=True)
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

if __name__ == '__main__':
    # Ensure output directory exists
    Path("data/output").mkdir(parents=True, exist_ok=True)
    
    # Run development server on port 5001 to avoid macOS AirPlay conflict
    print("🚀 Starting ISEE Web Demo...")
    print("📱 Open your browser to: http://localhost:5001")
    print("💡 For investor demo, press F11 for full screen mode")
    app.run(debug=True, host='0.0.0.0', port=5001)