"""
Main Application for ISEE Framework

This module provides a simple command-line interface to interact with the
Idea Synthesis and Extraction Engine framework.
"""

import os
import json
import argparse
import sys
from typing import Dict, Any, List, Optional, Tuple
import time
import random
from datetime import datetime
import platform
import psutil
from pathlib import Path
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
import logging

# Import modules
from model_api_integration import ModelAPIFactory, ModelAPIClient
from api_error_detector import APIErrorDetector
from provider_manager import ProviderManager
from instruction_templates import TemplateLibrary, create_default_library, InstructionTemplate
from query_generator import QueryGenerator, create_default_queries, Query
from domain_manager import DomainManager, create_default_domains, Domain
from evaluation_scoring import ScoringFramework, create_default_framework
from reporting import generate_reports
from query_export import auto_export_queries
from analysis import analyze_results

def get_week_of_month(date_str: str) -> int:
    """Convert YYYYMMDD to week number within month (1-5)"""
    year = int(date_str[:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])

    date_obj = datetime(year, month, day)
    first_day = datetime(year, month, 1)

    # Calculate week number (1-based)
    days_from_start = (date_obj - first_day).days
    week_num = (days_from_start // 7) + 1

    return min(week_num, 5)  # Cap at week 5 for end-of-month runs


def normalize_framework_name(template_name_or_id: str) -> str:
    """
    Normalize framework names to short display format for UI consistency.

    Converts:
    - "Analytical Framework" → "Analytical"
    - "ins_analytical" → "Analytical"
    - "Future-Oriented Framework" → "Futurist"
    """
    # Mapping from template IDs to short display names
    id_to_short = {
        "ins_analytical": "Analytical",
        "ins_creative": "Creative",
        "ins_critical": "Critical",
        "ins_integrative": "Integrative",
        "ins_pragmatic": "Pragmatic",
        "ins_first_principles": "First Principles",
        "ins_systems": "Systems",
        "ins_contrarian": "Contrarian",
        "ins_historical": "Historical",
        "ins_futurist": "Futurist",
        "ins_disruption": "Disruption",
    }

    # Check if it's a template ID
    if template_name_or_id in id_to_short:
        return id_to_short[template_name_or_id]

    # Handle full framework names like "Analytical Framework"
    name = template_name_or_id

    # Special case for Future-Oriented
    if "Future-Oriented" in name or "Future Oriented" in name:
        return "Futurist"

    # Remove " Framework" suffix if present
    if name.endswith(" Framework"):
        return name[:-10]  # Remove " Framework"

    return name


def normalize_model_display_name(model_name: str, model_configs: dict = None) -> str:
    """
    Normalize model names for consistent UI display.

    Handles Globant provider-prefixed names like:
    - "vertex_ai/gemini-2.5-pro" → "Gemini 2.5 Pro"
    - "anthropic/claude-sonnet-4-20250514" → "Claude Sonnet 4"
    """
    # First check if we have a configured display name
    if model_configs and model_name in model_configs:
        return model_configs[model_name].get("name", model_name)

    # Handle provider-prefixed names (Globant format)
    if "/" in model_name:
        # Extract model part after provider prefix
        parts = model_name.split("/")
        model_part = parts[-1]  # Get the model name after provider

        # Clean up the model name for display
        # Remove version suffixes like -20250514
        import re
        model_part = re.sub(r'-\d{8}$', '', model_part)

        # Convert to title case and clean up
        model_part = model_part.replace("-", " ").replace("_", " ")

        # Capitalize properly
        words = model_part.split()
        capitalized = []
        for word in words:
            # Keep version numbers as-is, capitalize others
            if word.replace(".", "").isdigit() or word in ["v1", "v2", "v3"]:
                capitalized.append(word)
            else:
                capitalized.append(word.capitalize())

        return " ".join(capitalized)

    return model_name


class ParallelExecutionEngine:
    """Async execution engine for parallel API calls with intelligent rate limiting."""
    
    # Provider rate limits (requests per second)
    PROVIDER_LIMITS = {
        "openrouter": 10,    # Generous unified limit
        "anthropic": 5,      # Conservative for direct API
        "openai": 8,         # Based on tier limits  
        "google": 6          # Gemini limits
    }
    
    def __init__(self, isee_app, max_workers: int = 8, json_progress: bool = False):
        """Initialize the parallel execution engine.
        
        Args:
            isee_app: Reference to main ISEEApplication instance
            max_workers: Maximum concurrent API calls
            json_progress: Whether to output structured progress JSON
        """
        self.isee_app = isee_app
        self.max_workers = max_workers
        self.json_progress = json_progress
        self.logger = logging.getLogger(f"{__name__}.ParallelExecutionEngine")
        
        # Create semaphores for rate limiting per provider
        self.provider_semaphores = {
            provider: asyncio.Semaphore(limit) 
            for provider, limit in self.PROVIDER_LIMITS.items()
        }
        
        # Progress tracking
        self.completed_count = 0
        self.failed_count = 0
        self.total_combinations = 0
        
    def get_provider_for_model(self, model_id: str) -> str:
        """Determine the API provider for a given model ID."""
        if model_id in self.isee_app.model_configs:
            provider = self.isee_app.model_configs[model_id].get("provider", "unknown")
            # Map provider names to our rate limit keys
            if provider == "openrouter":
                return "openrouter"
            elif provider in ["anthropic", "claude"]:
                return "anthropic"
            elif provider in ["openai", "gpt"]:
                return "openai"
            elif provider in ["google", "gemini"]:
                return "google"
        
        # Default fallback based on model name patterns
        if "openrouter" in model_id or "/" in model_id:
            return "openrouter"
        elif "claude" in model_id.lower():
            return "anthropic"
        elif "gpt" in model_id.lower():
            return "openai"
        elif "gemini" in model_id.lower():
            return "google"
        
        return "openrouter"  # Safe default
    
    async def execute_combinations_parallel(
        self,
        combinations: List[Dict[str, Any]],
        max_to_execute: Optional[int] = None,
        use_real_models: bool = True
    ) -> Dict[str, Any]:
        """Execute combinations in parallel with intelligent rate limiting.
        
        Args:
            combinations: List of combinations to execute
            max_to_execute: Optional limit on number of combinations
            use_real_models: Whether to use real API calls vs simulation
            
        Returns:
            Dictionary mapping combination IDs to results
        """
        # Apply execution limit if specified
        if max_to_execute and len(combinations) > max_to_execute:
            self.logger.info(f"Limiting execution to {max_to_execute} out of {len(combinations)} combinations")
            combinations = combinations[:max_to_execute]
        
        self.total_combinations = len(combinations)
        self.completed_count = 0
        self.failed_count = 0
        
        # Output initial progress
        if self.json_progress:
            progress_info = {
                "type": "parallel_execution_start",
                "total_combinations": self.total_combinations,
                "max_workers": self.max_workers,
                "timestamp": datetime.now().isoformat()
            }
            print(f"PROGRESS_JSON:{json.dumps(progress_info)}")
            sys.stdout.flush()
        
        # Shuffle for diverse execution order
        random.seed(int(time.time()))
        random.shuffle(combinations)
        
        # Create and execute tasks with semaphore-based rate limiting
        tasks = [
            self.execute_single_combination(combo, use_real_models) 
            for combo in combinations
        ]
        
        # Execute with controlled concurrency
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = {}
        for i, (combo, result) in enumerate(zip(combinations, results)):
            combo_id = combo["id"]
            
            if isinstance(result, Exception):
                self.logger.error(f"Combination {combo_id} failed with exception: {result}")
                processed_results[combo_id] = {
                    "error": str(result),
                    "combination_id": combo_id,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                processed_results[combo_id] = result
        
        # Output final progress
        if self.json_progress:
            progress_info = {
                "type": "parallel_execution_complete",
                "total_combinations": self.total_combinations,
                "completed": self.completed_count,
                "failed": self.failed_count,
                "success_rate": self.completed_count / self.total_combinations if self.total_combinations > 0 else 0,
                "timestamp": datetime.now().isoformat()
            }
            print(f"PROGRESS_JSON:{json.dumps(progress_info)}")
            sys.stdout.flush()
        
        return processed_results
    
    async def execute_single_combination(
        self,
        combination: Dict[str, Any],
        use_real_models: bool = True
    ) -> Dict[str, Any]:
        """Execute a single combination with retry logic and rate limiting.
        
        Args:
            combination: Combination dictionary to execute
            use_real_models: Whether to use real API calls vs simulation
            
        Returns:
            Result dictionary
        """
        combo_id = combination["id"]
        provider = self.get_provider_for_model(combination["model"])
        
        # Get semaphore for this provider
        semaphore = self.provider_semaphores.get(provider, self.provider_semaphores["openrouter"])
        
        # Output combination start progress
        if self.json_progress:
            template = self.isee_app.template_library.get_template(combination["template"])
            
            # Handle dynamic domains
            if combination["domain"].startswith('dynamic:'):
                domain_name = combination["domain"].replace('dynamic:', '')
            else:
                domain = self.isee_app.domain_manager.get_domain(combination["domain"])
                domain_name = domain.name if domain else combination["domain"]
            
            # Normalize model name for consistent UI display
            model_display_name = normalize_model_display_name(
                combination["model"],
                self.isee_app.model_configs
            )

            # Normalize framework name for consistent UI display
            framework_display_name = normalize_framework_name(
                template.name if template else combination["template"]
            )

            progress_info = {
                "type": "combination_start_parallel",
                "combination_id": combo_id,
                "model": model_display_name,
                "framework": framework_display_name,
                "domain": domain_name,
                "provider": provider,
                "progress_percent": int((self.completed_count + self.failed_count + 1) / self.total_combinations * 100),
                "timestamp": datetime.now().isoformat()
            }
            print(f"PROGRESS_JSON:{json.dumps(progress_info)}")
            sys.stdout.flush()
        
        # Execute with provider rate limiting and retry logic
        async with semaphore:
            for attempt in range(3):  # Three-tier retry
                try:
                    if use_real_models:
                        # Call the synchronous method in a thread pool
                        loop = asyncio.get_event_loop()
                        with ThreadPoolExecutor(max_workers=1) as executor:
                            future = loop.run_in_executor(
                                executor,
                                self._execute_combination_sync,
                                combination
                            )
                            result = await future
                    else:
                        # Use simulation - run in thread pool for consistency
                        loop = asyncio.get_event_loop()
                        with ThreadPoolExecutor(max_workers=1) as executor:
                            future = loop.run_in_executor(
                                executor,
                                self._execute_combination_simulation,
                                combination
                            )
                            result = await future
                    
                    # Success - update counters and return
                    self.completed_count += 1
                    
                    if self.json_progress:
                        success = result.get("response") is not None and not result.get("error")
                        progress_info = {
                            "type": "combination_complete_parallel",
                            "combination_id": combo_id,
                            "model": model_display_name,
                            "framework": framework_display_name,
                            "domain": domain_name,
                            "success": success,
                            "attempt": attempt + 1,
                            "response_length": len(result.get("response", "")) if success else 0,
                            "timestamp": datetime.now().isoformat()
                        }
                        print(f"PROGRESS_JSON:{json.dumps(progress_info)}")
                        sys.stdout.flush()
                    
                    return result
                    
                except Exception as e:
                    if attempt < 2:  # Not the final attempt
                        # Exponential backoff
                        wait_time = 2 ** attempt
                        self.logger.warning(f"Attempt {attempt + 1} failed for {combo_id}, retrying in {wait_time}s: {str(e)}")
                        await asyncio.sleep(wait_time)
                    else:
                        # Final attempt failed
                        self.failed_count += 1
                        self.logger.error(f"All 3 attempts failed for combination {combo_id}: {str(e)}")
                        
                        error_result = {
                            "error": f"All retries failed: {str(e)}",
                            "combination_id": combo_id,
                            "timestamp": datetime.now().isoformat(),
                            "attempts": 3
                        }
                        
                        if self.json_progress:
                            progress_info = {
                                "type": "combination_failed_parallel",
                                "combination_id": combo_id,
                                "model": model_display_name,
                                "framework": framework_display_name,
                                "domain": domain_name,
                                "error": str(e),
                                "attempts": 3,
                                "timestamp": datetime.now().isoformat()
                            }
                            print(f"PROGRESS_JSON:{json.dumps(progress_info)}")
                            sys.stdout.flush()
                        
                        return error_result
    
    def _execute_combination_sync(self, combination: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single combination synchronously (to be called from thread pool)."""
        template = self.isee_app.template_library.get_template(combination["template"])
        query_obj = self.isee_app.query_generator.get_query_by_id(combination["query"])
        
        # Handle both static and dynamic domains
        if combination["domain"].startswith('dynamic:'):
            dynamic_name = combination["domain"].replace('dynamic:', '')
            from collections import namedtuple
            DynamicDomain = namedtuple('DynamicDomain', ['id', 'name', 'description', 'keywords'])
            domain = DynamicDomain(
                id=combination["domain"],
                name=dynamic_name,
                description=f"the Domain of {dynamic_name}",
                keywords=f"{dynamic_name.lower()}, dynamic domain"
            )
        else:
            domain = self.isee_app.domain_manager.get_domain(combination["domain"])
        
        # Use existing synchronous method from ISEEApplication
        result = self.isee_app._generate_model_response(combination, template, query_obj, domain)
        
        # Save raw response using existing method
        self.isee_app.save_raw_response(result, combination)
        
        return result
    
    def _execute_combination_simulation(self, combination: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single combination in simulation mode (to be called from thread pool)."""
        template = self.isee_app.template_library.get_template(combination["template"])
        query_obj = self.isee_app.query_generator.get_query_by_id(combination["query"])
        
        # Handle both static and dynamic domains
        if combination["domain"].startswith('dynamic:'):
            dynamic_name = combination["domain"].replace('dynamic:', '')
            from collections import namedtuple
            DynamicDomain = namedtuple('DynamicDomain', ['id', 'name', 'description', 'keywords'])
            domain = DynamicDomain(
                id=combination["domain"],
                name=dynamic_name,
                description=f"the Domain of {dynamic_name}",
                keywords=f"{dynamic_name.lower()}, dynamic domain"
            )
        else:
            domain = self.isee_app.domain_manager.get_domain(combination["domain"])
        
        # Use existing simulation method from ISEEApplication
        return self.isee_app._simulate_model_response(combination, template, query_obj, domain)


class ISEEApplication:
    """Main application class for the ISEE framework."""
    
    def __init__(self, config_path: Optional[str] = None, output_directory: Optional[str] = None):
        """Initialize the ISEE application.
        
        Args:
            config_path: Optional path to a configuration file.
            output_directory: Optional custom output directory (overrides auto-generated timestamp).
        """
        # Initialize components
        self.template_library = create_default_library()
        self.query_generator = QueryGenerator(use_dynamic_variations=True)  # Enable dynamic context-sensitive variations
        self.domain_manager = DomainManager()
        self.scoring_framework = create_default_framework()
        
        # Add default data
        for query in create_default_queries():
            self.query_generator.add_base_query(query)
        
        for domain in create_default_domains():
            self.domain_manager.add_domain(domain)
        
        # Storage for results
        self.combinations = []
        self.results = {}
        self.evaluations = {}
        self.synthesized_ideas = {}
        self.query_export_paths = {}  # Store paths to exported query details
        
        # Model configuration and clients
        self.model_configs = {}
        self.model_clients = {}
        self.error_detector = APIErrorDetector()  # Error detection system
        
        # Provider management - initialized with default settings, can be updated later
        self.provider_manager = ProviderManager(default_mode="openrouter", fallback_enabled=True)
        
        # Default execution settings
        self.execution_settings = {
            "max_combinations": None
        }
        
        # Create timestamped directory for this run (or use provided directory)
        if output_directory:
            self.run_output_dir = output_directory
            self.output_directory = output_directory  # Store for auto-export compatibility
            self.timestamp = os.path.basename(output_directory).replace("run_", "")
        else:
            self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Calculate organized path: data/output/YYYY-MM/weekX/run_TIMESTAMP  
            year_month = self.timestamp[:6]  # YYYYMM
            week_num = get_week_of_month(self.timestamp[:8])  # YYYYMMDD -> week number
            organized_path = f"data/output/20{year_month[2:4]}-{year_month[4:6]}/week{week_num}"
            
            self.run_output_dir = os.path.join(organized_path, f"run_{self.timestamp}")
            self.output_directory = self.run_output_dir  # Store for auto-export compatibility
        
        # Ensure base directories exist
        os.makedirs("data", exist_ok=True)
        os.makedirs("data/output", exist_ok=True)
        os.makedirs("data/state", exist_ok=True)
        os.makedirs(self.run_output_dir, exist_ok=True)
        
        # Load configuration if provided
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Process configuration
        print(f"Loading configuration from {config_path}...")
        
        # Note: Directories for data are already created in __init__
        
        # Load execution settings if present
        if "execution_settings" in config:
            print("Loading execution settings from config...")
            self.execution_settings = config["execution_settings"]
            
        # Load model configurations
        if "models" in config:
            # Check if models is a dictionary with sections or a flat list
            if isinstance(config["models"], dict):
                # Handle structured models with sections
                all_models = []
                if "api_models" in config["models"]:
                    all_models.extend(config["models"]["api_models"])
                if "ollama_models" in config["models"]:
                    all_models.extend(config["models"]["ollama_models"])
                
                # Process all collected models
                for model_config in all_models:
                    model_id = model_config.get("id")
                    if model_id:
                        # Skip disabled models
                        if model_config.get("disabled", False):
                            disabled_reason = model_config.get("disabled_reason", "Disabled in configuration")
                            print(f"Skipping disabled model: {model_id} ({disabled_reason})")
                            continue
                        
                        self.model_configs[model_id] = model_config
                        print(f"Loaded configuration for model: {model_id}")
            else:
                # Handle flat list of models (backwards compatibility)
                for model_config in config["models"]:
                    model_id = model_config.get("id")
                    if model_id:
                        # Skip disabled models
                        if model_config.get("disabled", False):
                            disabled_reason = model_config.get("disabled_reason", "Disabled in configuration")
                            print(f"Skipping disabled model: {model_id} ({disabled_reason})")
                            continue
                        
                        self.model_configs[model_id] = model_config
                        print(f"Loaded configuration for model: {model_id}")
        
        # Load instruction templates if provided
        if "instructions" in config:
            self.template_library = TemplateLibrary()
            for template_data in config["instructions"]:
                template = InstructionTemplate.from_dict(template_data)
                self.template_library.add_template(template)
            print(f"Loaded {len(config['instructions'])} instruction templates")
        
        # Load domains if provided
        if "domains" in config:
            self.domain_manager = DomainManager()
            for domain_data in config["domains"]:
                domain = Domain.from_dict(domain_data)
                self.domain_manager.add_domain(domain)
            print(f"Loaded {len(config['domains'])} domains")
        
        # Load queries if provided
        if "queries" in config:
            for query_data in config["queries"]:
                query = Query.from_dict(query_data)
                self.query_generator.add_base_query(query)
            print(f"Loaded {len(config['queries'])} queries")
    
    def save_state(self, state_path: str) -> None:
        """Save the current state to a file.
        
        Args:
            state_path: Path to save the state to. If no directory is specified,
                        it will be saved to data/state/.
        """
        # Ensure we're using the data/state directory for files without a path
        if not os.path.dirname(state_path):
            state_path = os.path.join("data", "state", state_path)
            
        # Make sure the directory exists
        os.makedirs(os.path.dirname(state_path), exist_ok=True)
        
        state = {
            "combinations": self.combinations,
            "results": self.results,
            "evaluations": self.evaluations,
            "synthesized_ideas": self.synthesized_ideas
        }
        
        with open(state_path, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"State saved to {state_path}")
    
    def load_state(self, state_path: str) -> None:
        """Load state from a file.
        
        Args:
            state_path: Path to the state file. If no directory is specified,
                        it will look in data/state/.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        # If no directory is specified, try the data/state directory
        if not os.path.dirname(state_path):
            state_path_to_try = os.path.join("data", "state", state_path)
            if os.path.exists(state_path_to_try):
                state_path = state_path_to_try
        
        with open(state_path, 'r') as f:
            state = json.load(f)
        
        self.combinations = state.get("combinations", [])
        self.results = state.get("results", {})
        self.evaluations = state.get("evaluations", {})
        self.synthesized_ideas = state.get("synthesized_ideas", {})
        
        print(f"State loaded from {state_path}")
    
    def _select_innovation_weighted_templates(self, all_templates, instruction_count):
        """Select templates with enhanced weighting for innovation-focused frameworks.
        
        Innovation frameworks (creative, contrarian, first_principles, disruption) get 
        higher allocation to boost novelty scoring.
        
        Args:
            all_templates: List of all available templates
            instruction_count: Total number of templates to select
            
        Returns:
            List of selected templates with innovation bias
        """
        import random as random_module
        
        # Define innovation-focused frameworks
        innovation_frameworks = {
            "ins_creative", "ins_contrarian", "ins_first_principles", "ins_disruption"
        }
        
        # Separate innovation and traditional frameworks
        innovation_templates = [t for t in all_templates if t.id in innovation_frameworks]
        traditional_templates = [t for t in all_templates if t.id not in innovation_frameworks]
        
        # Calculate allocation: 60% for innovation frameworks, 40% for traditional
        innovation_count = max(1, int(instruction_count * 0.6))
        traditional_count = instruction_count - innovation_count
        
        selected_templates = []
        
        # Select innovation frameworks (prioritized)
        if len(innovation_templates) > innovation_count:
            selected_templates.extend(random_module.sample(innovation_templates, innovation_count))
        else:
            selected_templates.extend(innovation_templates)
            # If we don't have enough innovation templates, fill with traditional
            remaining_needed = innovation_count - len(innovation_templates)
            traditional_count += remaining_needed
        
        # Select traditional frameworks
        if len(traditional_templates) > traditional_count:
            selected_templates.extend(random_module.sample(traditional_templates, traditional_count))
        else:
            selected_templates.extend(traditional_templates)
            # If we don't have enough total templates, use what we have
            if len(selected_templates) < instruction_count:
                # Fill remaining slots with any available templates
                remaining_templates = [t for t in all_templates if t not in selected_templates]
                needed = instruction_count - len(selected_templates)
                if remaining_templates and needed > 0:
                    selected_templates.extend(random_module.sample(
                        remaining_templates, min(needed, len(remaining_templates))
                    ))
        
        print(f"Selected {len(selected_templates)} templates with innovation weighting:")
        innovation_selected = [t.name for t in selected_templates if t.id in innovation_frameworks]
        traditional_selected = [t.name for t in selected_templates if t.id not in innovation_frameworks]
        print(f"  Innovation frameworks ({len(innovation_selected)}): {', '.join(innovation_selected)}")
        print(f"  Traditional frameworks ({len(traditional_selected)}): {', '.join(traditional_selected)}")
        
        return selected_templates
    
    def generate_combinations(
        self,
        query_id: str,
        domain_ids: Optional[List[str]] = None,
        model_count: int = 2,
        instruction_count: int = 3,
        query_variations: int = 2,
        # balanced models is now always enabled for maximum diversity
        max_combinations: Optional[int] = None,
        selected_models: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Generate combinations of models, instructions, queries, and domains.
        
        Args:
            query_id: ID of the base query.
            domain_ids: Optional list of domain IDs. If None, all domains are used.
            model_count: Number of models to use.
            instruction_count: Number of instructions to use.
            query_variations: Number of query variations to generate.
            Balanced model representation is now always enabled for maximum diversity.
            max_combinations: Maximum number of combinations to generate (only used with sampling methods).
            selected_models: Optional list of specific model IDs to use (overrides model_count).
            
        Returns:
            List of combination dictionaries.
            
        Raises:
            KeyError: If the query ID does not exist.
        """
        # Get the base query
        base_query = self.query_generator.get_query_by_id(query_id)
        if not base_query:
            raise KeyError(f"No query with ID '{query_id}' exists")
        
        # Generate query variations
        variations = self.query_generator.generate_variations(query_id, count=query_variations)
        all_queries = [base_query] + variations
        
        # Get domains - handle both static and dynamic domains
        if domain_ids:
            domains = []
            for domain_id in domain_ids:
                if domain_id.startswith('dynamic:'):
                    # Create a pseudo-domain object for dynamic domains
                    dynamic_name = domain_id.replace('dynamic:', '')
                    from collections import namedtuple
                    DynamicDomain = namedtuple('DynamicDomain', ['id', 'name', 'description', 'keywords'])
                    dynamic_domain = DynamicDomain(
                        id=domain_id,
                        name=dynamic_name,
                        description=f"the Domain of {dynamic_name}",
                        keywords=f"{dynamic_name.lower()}, dynamic domain"
                    )
                    domains.append(dynamic_domain)
                else:
                    # Regular static domain
                    domains.append(self.domain_manager.get_domain(domain_id))
        else:
            domains = self.domain_manager.list_domains()
        
        # Use model IDs from config, or create placeholder IDs if not available
        if selected_models:
            # Use specifically selected models (overrides model_count)
            models = []
            available_models = list(self.model_configs.keys()) if self.model_configs else []
            for model_id in selected_models:
                if not self.model_configs or model_id in available_models:
                    models.append(model_id)
                else:
                    # Check if this is a dynamic OpenRouter model parameter
                    if "/" in model_id:
                        print(f"Creating dynamic config for OpenRouter model: {model_id}")
                        # Create a minimal config for this OpenRouter model
                        provider, model_name = model_id.split("/", 1)
                        dynamic_config = {
                            "id": model_id,
                            "name": f"{provider.title()} {model_name}",
                            "provider": "openrouter",
                            "parameters": {
                                "model": model_id,
                                "max_tokens": 4096,
                                "temperature": 0.7,
                                "top_p": 0.95
                            },
                            "features": ["dynamic"],
                            "cost_tier": "unknown"
                        }
                        # Add this dynamic config to our model configs
                        self.model_configs[model_id] = dynamic_config
                        models.append(model_id)
                        print(f"Dynamic config created and added: {model_id}")
                    # Check if this is a dynamic Ollama model
                    elif not model_id.startswith("ollama_") and (":" in model_id or model_id.startswith("llama") or model_id.startswith("qwen") or model_id.startswith("phi") or model_id.startswith("mixtral") or model_id.startswith("codellama")):
                        print(f"Creating dynamic config for Ollama model: {model_id}")
                        # Create a minimal config for this Ollama model
                        dynamic_config = {
                            "id": model_id,
                            "name": f"Ollama {model_id}",
                            "provider": "ollama",
                            "parameters": {
                                "model": model_id,
                                "max_tokens": 2048,
                                "temperature": 0.7
                            },
                            "features": ["dynamic", "local"],
                            "cost_tier": "free"
                        }
                        # Add this dynamic config to our model configs
                        self.model_configs[model_id] = dynamic_config
                        models.append(model_id)
                        print(f"Dynamic Ollama config created and added: {model_id}")
                    else:
                        print(f"Warning: Selected model '{model_id}' not found in config, skipping.")
            
            if not models:
                print("No valid models found among selected models. Falling back to default selection.")
                # Fall back to normal model selection logic
                selected_models = None
        
        if not selected_models:
            # Normal model selection logic
            if self.model_configs:
                models = list(self.model_configs.keys())
                if model_count == len(models):
                    # Use all available models
                    pass
                elif model_count < len(models):
                    # If we need fewer models than available, prioritize diversity
                    # Instead of random sampling, we'll ensure we get a mix of different providers
                    provider_models = {}
                    for model_id in models:
                        if model_id in self.model_configs:
                            model_config = self.model_configs[model_id]
                            model_name = model_config.get("name", "")
                            # Determine provider
                            provider = model_config.get("provider", "")
                            if not provider:
                                if "claude" in model_name.lower():
                                    provider = "anthropic"
                                elif "gpt" in model_name.lower():
                                    provider = "openai"
                                elif any(keyword in model_name.lower() for keyword in 
                                         ["llama", "mixtral", "codellama", "phi3"]):
                                    provider = "ollama"
                                else:
                                    provider = "unknown"
                            # Group by provider
                            provider_models.setdefault(provider, []).append(model_id)
                    
                    # Select models to ensure diversity across providers
                    selected_models_list = []
                    # First, select one model from each provider
                    for provider in provider_models:
                        if provider_models[provider] and len(selected_models_list) < model_count:
                            selected_models_list.append(provider_models[provider][0])
                    
                    # If we still need more models, add additional ones
                    providers_cycle = list(provider_models.keys())
                    idx = 0
                    while len(selected_models_list) < model_count and idx < 100:  # avoid infinite loop
                        provider = providers_cycle[idx % len(providers_cycle)]
                        provider_list = provider_models[provider]
                        if len(provider_list) > 1:  # If there are more models from this provider
                            for model in provider_list[1:]:
                                if model not in selected_models_list and len(selected_models_list) < model_count:
                                    selected_models_list.append(model)
                        idx += 1
                    
                    models = selected_models_list
            else:
                # Fall back to placeholder IDs
                models = [f"model_{i}" for i in range(1, model_count + 1)]
        
        # Get instructions
        all_templates = self.template_library.list_templates()
        
        # Import random module explicitly to avoid shadowing issues
        import random as random_module
        
        # Check if specific template IDs were provided
        specific_template_ids = getattr(self, 'specific_template_ids', None)
        if specific_template_ids:
            # Find the templates with matching IDs
            templates = []
            for template_id in specific_template_ids:
                try:
                    template = self.template_library.get_template(template_id)
                    templates.append(template)
                    print(f"✓ Loaded specific template: {template_id}")
                except KeyError:
                    print(f"Warning: Template with ID '{template_id}' not found, skipping.")
            
            if not templates:
                print("No valid templates found among the specified IDs. Falling back to innovation-weighted selection.")
                templates = self._select_innovation_weighted_templates(all_templates, instruction_count)
            else:
                print(f"Using {len(templates)} specific templates (including ins_disruption: {'ins_disruption' in [t.id for t in templates]})")
        else:
            # Use innovation-weighted selection for enhanced novelty
            templates = self._select_innovation_weighted_templates(all_templates, instruction_count)
        
        # Generate combinations using exhaustive sampling
        combinations = []
        
        # Create all possible combinations
        all_combinations = []
        for template in templates:
            for domain in domains:
                for query in all_queries:
                    for model in models:
                        combination_id = f"{model}_{template.id}_{query.id}_{domain.id}"
                        
                        combination = {
                            "id": combination_id,
                            "model": model,
                            "template": template.id,
                            "query": query.id,
                            "domain": domain.id
                        }
                        
                        all_combinations.append(combination)
        
        # Apply max_combinations limit with fair distribution across all dimensions
        if max_combinations and len(all_combinations) > max_combinations:
            # Calculate distribution to ensure all models, templates, and domains are represented
            import random
            import time
            random.seed(int(time.time()))  # Random execution order for diversity
            
            # Stratified sampling to ensure representation across all dimensions
            selected_combinations = []
            
            # Group by template to ensure each framework is represented
            template_groups = {}
            for combo in all_combinations:
                template_id = combo['template']
                if template_id not in template_groups:
                    template_groups[template_id] = []
                template_groups[template_id].append(combo)
            
            # Calculate how many combinations per template
            combinations_per_template = max_combinations // len(templates)
            remainder = max_combinations % len(templates)
            
            for i, (template_id, template_combos) in enumerate(template_groups.items()):
                # Give some templates one extra combination if there's a remainder
                template_limit = combinations_per_template + (1 if i < remainder else 0)
                
                if len(template_combos) <= template_limit:
                    selected_combinations.extend(template_combos)
                else:
                    # Randomly sample from this template's combinations to ensure model diversity
                    sampled = random_module.sample(template_combos, template_limit)
                    selected_combinations.extend(sampled)
            
            combinations = selected_combinations
        else:
            combinations = all_combinations
        
        # Store the combinations
        self.combinations = combinations
        
        print(f"Generated {len(combinations)} combinations")
        return combinations
        
    # Stratified sampling removed - ISEE now uses exhaustive + balanced for maximum diversity
    
    def _get_or_create_model_client(self, model_id: str) -> Optional[ModelAPIClient]:
        """Get or create a model API client.
        
        Args:
            model_id: ID of the model.
            
        Returns:
            ModelAPIClient instance or None if model configuration is not available.
        """
        # Return existing client if already created
        if model_id in self.model_clients:
            return self.model_clients[model_id]
        
        # Check if we have configuration for this model
        if model_id not in self.model_configs:
            # Check if this is a dynamic OpenRouter model parameter (e.g., "anthropic/claude-3-5-sonnet")
            if "/" in model_id:
                print(f"Creating dynamic config for OpenRouter model: {model_id}")
                # Create a minimal config for this OpenRouter model
                provider, model_name = model_id.split("/", 1)
                dynamic_config = {
                    "id": model_id,
                    "name": f"{provider.title()} {model_name}",
                    "provider": "openrouter",
                    "parameters": {
                        "model": model_id,
                        "max_tokens": 4096,
                        "temperature": 0.7,
                        "top_p": 0.95
                    },
                    "features": ["dynamic"],
                    "cost_tier": "unknown"
                }
                # Add this dynamic config to our model configs
                self.model_configs[model_id] = dynamic_config
                print(f"Dynamic config created for {model_id}")
            else:
                print(f"Warning: No configuration found for model {model_id}")
                return None
        
        # Create a new client
        model_config = self.model_configs[model_id]
        model_name = model_config.get("name", "")
        
        try:
            # Determine provider from model name or explicit provider field
            provider = model_config.get("provider", "")
            if not provider:
                if "claude" in model_name.lower():
                    provider = "anthropic"
                elif "gpt" in model_name.lower():
                    provider = "openai"
                elif any(keyword in model_name.lower() for keyword in 
                        ["llama", "mixtral", "codellama", "phi3"]):
                    provider = "ollama"
                else:
                    print(f"Warning: Could not determine provider for model {model_id}")
                    return None
            
            print(f"Creating client for model {model_id} using provider: {provider}")
            
            # For Ollama models, check if Ollama is running and if the model is available
            if provider == "ollama":
                try:
                    # Create temporary client to check for model availability
                    temp_client = ModelAPIFactory.create_client("ollama")
                    available_models = temp_client.get_available_models()
                    model_param = model_config.get("parameters", {}).get("model")
                    
                    if not available_models:
                        print(f"Warning: No Ollama models found. Is Ollama running?")
                        print(f"Please ensure Ollama is installed and running on http://localhost:11434")
                        return None
                    
                    if model_param and model_param not in available_models:
                        print(f"Warning: Model {model_param} not found in Ollama. Available models: {', '.join(available_models)}")
                        print(f"Consider running 'ollama pull {model_param}' to download the model.")
                        return None
                except Exception as e:
                    print(f"Warning: Error checking Ollama availability: {str(e)}")
                    print("Please ensure Ollama is installed and running on http://localhost:11434")
            
            # Create the client
            client = ModelAPIFactory.create_client(provider)
            self.model_clients[model_id] = client
            return client
        
        except Exception as e:
            print(f"Error creating client for model {model_id}: {str(e)}")
            return None
    

    def set_provider_mode(self, provider_mode: str) -> None:
        """Set the API provider mode for this application instance.
        
        Args:
            provider_mode: Provider mode ("openrouter", "globant", "hybrid")
        """
        try:
            self.provider_manager.set_provider_mode(provider_mode)
            print(f"Provider mode set to: {provider_mode}")
        except ValueError as e:
            print(f"Error setting provider mode: {e}")
            raise
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get current provider health status.
        
        Returns:
            Dictionary containing provider status information
        """
        return self.provider_manager.get_provider_status()
    
    def save_raw_response(self, result: Dict[str, Any], combination: Dict[str, Any]) -> None:
        """Save raw response text to individual files."""
        try:
            # Create responses directory
            responses_dir = Path(self.output_directory) / "raw_responses"
            responses_dir.mkdir(exist_ok=True)
            
            # Generate filename
            combo_id = result.get("combination_id", "unknown")
            model_name = combination.get("model", "unknown").replace("/", "_")
            template_id = combination.get("template", "unknown")
            
            filename = f"{combo_id}_{model_name}_{template_id}.md"
            filepath = responses_dir / filename
            
            # Save response with metadata
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Raw Response Data\n\n")
                f.write(f"**Combination ID:** {combo_id}\n")
                f.write(f"**Model:** {combination.get('model', 'Unknown')}\n")
                f.write(f"**Template:** {combination.get('template', 'Unknown')}\n")
                f.write(f"**Domain:** {combination.get('domain', 'Unknown')}\n")
                f.write(f"**Query:** {combination.get('query', 'Unknown')}\n")
                f.write(f"**Timestamp:** {result.get('metadata', {}).get('timestamp', 'Unknown')}\n")
                f.write(f"**Duration:** {result.get('metadata', {}).get('duration', 'Unknown')}s\n\n")
                f.write(f"## Prompt Sent to Model\n\n")
                f.write(f"```\n{result.get('prompt', 'Prompt not available')}\n```\n\n")
                f.write(f"## Raw Response\n\n")
                f.write(result.get("response", "Response not available"))
                
        except Exception as e:
            print(f"Warning: Failed to save raw response for {combo_id}: {e}")

    def execute_combinations(
        self,
        combinations: Optional[List[Dict[str, Any]]] = None,
        max_to_execute: Optional[int] = None,
        dry_run: bool = False,
        use_real_models: bool = True,
        verbose_queries: bool = False,
        show_all_queries: bool = False,
        json_progress: bool = False,
        parallel: bool = True,
        max_workers: int = 8
    ) -> Dict[str, Any]:
        """Execute the generated combinations.
        
        Args:
            combinations: Optional list of combinations to execute. If None, uses stored combinations.
            max_to_execute: Optional maximum number of combinations to execute.
            dry_run: If True, just print what would be executed without actually executing.
            use_real_models: If True, uses real model API calls. If False, uses simulation.
            verbose_queries: If True, show sample complete queries being sent to LLMs.
            show_all_queries: If True, show complete query for every combination (very verbose).
            json_progress: If True, output structured JSON progress for Web UI.
            parallel: If True, use parallel execution engine for faster processing.
            max_workers: Maximum concurrent workers for parallel execution.
            
        Returns:
            Dictionary mapping combination IDs to results.
        """
        combinations = combinations or self.combinations
        
        if max_to_execute and len(combinations) > max_to_execute:
            print(f"Limiting execution to {max_to_execute} out of {len(combinations)} combinations")
            combinations = combinations[:max_to_execute]
        
        if dry_run:
            print(f"Would execute {len(combinations)} combinations")
            for i, combo in enumerate(combinations[:5], 1):
                print(f"{i}. Combination: {combo['id']}")
                if i == 5 and len(combinations) > 5:
                    print(f"... and {len(combinations) - 5} more")
            return {}
        
        results = {}
        
        # Show initial query sample if verbose_queries is enabled
        if verbose_queries and not show_all_queries:
            print(f"\n🔍 QUERY SAMPLE: Showing 3 representative complete queries from {len(combinations)} combinations")
            sample_combos = combinations[:3] if len(combinations) >= 3 else combinations
            for j, sample_combo in enumerate(sample_combos, 1):
                template = self.template_library.get_template(sample_combo["template"])
                query_obj = self.query_generator.get_query_by_id(sample_combo["query"])
                domain = self.domain_manager.get_domain(sample_combo["domain"])
                
                formatted_instruction = template.format({
                    "domain": domain.description,
                    **query_obj.variables
                })
                complete_prompt = f"{formatted_instruction}\n\n{query_obj.text}"
                
                print(f"\n📋 Sample {j} - {sample_combo['id']}:")
                print(f"  Model: {sample_combo['model']} | Template: {template.name} | Domain: {domain.name}")
                print(f"  Complete Query ({len(complete_prompt)} chars):")
                print(f"  ┌─────────────────────────────────────────")
                if len(complete_prompt) > 300:
                    print(f"  │ {complete_prompt[:250]}...")
                    print(f"  │ ...{complete_prompt[-47:]}")
                else:
                    for line in complete_prompt.split('\n'):
                        print(f"  │ {line}")
                print(f"  └─────────────────────────────────────────")
            print(f"\n⚡ Starting execution of all {len(combinations)} combinations...\n")
        
        # Output initial progress information
        if json_progress:
            progress_info = {
                "type": "execution_start",
                "total_combinations": len(combinations),
                "timestamp": datetime.now().isoformat()
            }
            print(f"PROGRESS_JSON:{json.dumps(progress_info)}")
            sys.stdout.flush()  # Force immediate output for Web UI monitoring
        
        # Shuffle combinations for diverse execution order
        import random
        import time
        random.seed(int(time.time()))
        random.shuffle(combinations)
        
        # Choose execution mode: parallel vs sequential
        if parallel and len(combinations) > 1:
            print(f"🚀 Using parallel execution with {max_workers} workers for {len(combinations)} combinations")
            
            # Create and configure parallel execution engine
            parallel_engine = ParallelExecutionEngine(
                isee_app=self,
                max_workers=max_workers,
                json_progress=json_progress
            )
            
            # Execute in parallel using asyncio
            try:
                # Create event loop if running in thread
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If event loop is already running (e.g., in Jupyter), create new thread
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(
                                asyncio.run,
                                parallel_engine.execute_combinations_parallel(
                                    combinations, max_to_execute, use_real_models
                                )
                            )
                            results = future.result()
                    else:
                        results = loop.run_until_complete(
                            parallel_engine.execute_combinations_parallel(
                                combinations, max_to_execute, use_real_models
                            )
                        )
                except RuntimeError:
                    # No event loop exists, create one
                    results = asyncio.run(
                        parallel_engine.execute_combinations_parallel(
                            combinations, max_to_execute, use_real_models
                        )
                    )
                
                # Store results in instance
                self.results.update(results)
                
                print(f"🏁 Parallel execution completed: {len(results)} combinations processed")
                
            except Exception as e:
                print(f"⚠️  Parallel execution failed ({str(e)}), falling back to sequential mode")
                parallel = False  # Fall back to sequential execution
        
        if not parallel or len(combinations) <= 1:
            print(f"⚡ Using sequential execution for {len(combinations)} combinations")
            results = {}
            
            for i, combo in enumerate(combinations, 1):
                # Get the components first for model name
                template = self.template_library.get_template(combo["template"])
                query_obj = self.query_generator.get_query_by_id(combo["query"])
                
                # Handle both static and dynamic domains
                if combo["domain"].startswith('dynamic:'):
                    # Create a pseudo-domain object for dynamic domains
                    dynamic_name = combo["domain"].replace('dynamic:', '')
                    from collections import namedtuple
                    DynamicDomain = namedtuple('DynamicDomain', ['id', 'name', 'description', 'keywords'])
                    domain = DynamicDomain(
                        id=combo["domain"],
                        name=dynamic_name,
                        description=f"the Domain of {dynamic_name}",
                        keywords=f"{dynamic_name.lower()}, dynamic domain"
                    )
                else:
                    domain = self.domain_manager.get_domain(combo["domain"])
                
                # Get normalized display names for UI
                model_display_name = normalize_model_display_name(combo["model"], self.model_configs)
                framework_display_name = normalize_framework_name(
                    template.name if template else combo["template"]
                )
                domain_display_name = domain.name if domain else combo["domain"]

                # Output structured progress for Web UI
                if json_progress:
                    progress_info = {
                        "type": "combination_start",
                        "combination_index": i,
                        "total_combinations": len(combinations),
                        "combination_id": combo["id"],
                        "model": model_display_name,
                        "framework": framework_display_name,
                        "domain": domain_display_name,
                        "progress_percent": int((i / len(combinations)) * 100),
                        "timestamp": datetime.now().isoformat()
                    }
                    print(f"PROGRESS_JSON:{json.dumps(progress_info)}")
                    sys.stdout.flush()  # Force immediate output for Web UI monitoring
                
                # Enhanced execution line with query details if requested
                if show_all_queries:
                    print(f"Executing combination {i}/{len(combinations)}: {combo['id']}")
                    
                    # Show complete query for this combination
                    formatted_instruction = template.format({
                        "domain": domain.description,
                        **query_obj.variables
                    })
                    complete_prompt = f"{formatted_instruction}\n\n{query_obj.text}"
                    
                    print(f"  ┌─ Model: {model_display_name} | Template: {template.name} | Domain: {domain.name}")
                    print(f"  ├─ Complete Query ({len(complete_prompt)} chars):")
                    if len(complete_prompt) > 150:
                        print(f"  │   {complete_prompt[:100]}...")
                        print(f"  │   ...{complete_prompt[-47:]}")
                    else:
                        print(f"  │   {complete_prompt}")
                    print(f"  └─")
                elif not json_progress:  # Only show regular output if not in JSON mode
                    print(f"Executing combination {i}/{len(combinations)}: {combo['id']}")
                
                # Determine whether to use real API or simulation
                use_api = use_real_models and self.model_configs
                
                if use_api:
                    # Use real model API
                    result = self._generate_model_response(combo, template, query_obj, domain)
                else:
                    # Use simulation
                    result = self._simulate_model_response(combo, template, query_obj, domain)
                
                # Store the result
                results[combo["id"]] = result
                self.results[combo["id"]] = result
                
                # Save raw response to disk
                self.save_raw_response(result, combo)
                
                # Output completion progress for Web UI
                if json_progress:
                    success = result.get("response") is not None and not result.get("error")
                    progress_info = {
                        "type": "combination_complete",
                        "combination_index": i,
                        "total_combinations": len(combinations),
                        "combination_id": combo["id"],
                        "model": model_display_name,
                        "framework": framework_display_name,
                        "domain": domain_display_name,
                        "success": success,
                        "error": result.get("error") if not success else None,
                        "response_length": len(result.get("response", "")) if success else 0,
                        "progress_percent": int((i / len(combinations)) * 100),
                        "timestamp": datetime.now().isoformat()
                    }
                    print(f"PROGRESS_JSON:{json.dumps(progress_info)}")
                    sys.stdout.flush()  # Force immediate output for Web UI monitoring
                
                # Add a small delay between requests to avoid rate limits
                time.sleep(0.2)
        
        print(f"Executed {len(results)} combinations")
        
        # Auto-export query details for analysis and debugging
        if combinations and self.output_directory:
            try:
                export_metadata = {
                    'execution_timestamp': datetime.now().isoformat(),
                    'total_executed': len(results),
                    'total_combinations': len(combinations),
                    'dry_run': dry_run,
                    'use_real_models': use_real_models
                }
                
                export_paths = auto_export_queries(combinations, self.output_directory, export_metadata, self)
                print(f"Query details exported:")
                print(f"  📋 CSV: {os.path.basename(export_paths['csv'])}")
                print(f"  📊 Summary: {os.path.basename(export_paths['json'])}")
                
                # Store export paths for later access
                self.query_export_paths = export_paths
                
            except Exception as e:
                print(f"Warning: Failed to export query details: {e}")
        
        return results
    
    def _generate_model_response(
        self,
        combination: Dict[str, Any],
        template: Any,
        query: Query,
        domain: Domain
    ) -> Dict[str, Any]:
        """Generate a response using the actual model API.
        
        Args:
            combination: Combination dictionary.
            template: Instruction template.
            query: Query object.
            domain: Domain object.
            
        Returns:
            Result dictionary with API response.
        """
        # Format the instruction template
        formatted_instruction = template.format({
            "domain": domain.description,
            **query.variables
        })
        
        # Combine the instruction and query
        prompt = f"{formatted_instruction}\n\n{query.text}"
        
        # Get the model ID and client
        model_id = combination["model"]
        client = self._get_or_create_model_client(model_id)
        template_style = template.metadata.get("cognitive_style", "default")
        
        # Get model parameters from config
        model_params = {}
        if model_id in self.model_configs:
            model_config = self.model_configs[model_id]
            if "parameters" in model_config:
                model_params = model_config["parameters"].copy()
        
        response_text = ""
        start_time = time.time()
        
        try:
            if client:
                # Use the real API client
                print(f"Making real API call to {model_id}...")
                response_text = client.generate(prompt, model_params)
                print(f"Received response from {model_id} (length: {len(response_text)} chars)")
                
                # Check if response is actually an error
                is_error, error_reason = self.error_detector.is_api_error(response_text)
                if is_error:
                    print(f"⚠️  API Error detected for {model_id}: {error_reason}")
                    print(f"   Response preview: {response_text[:100]}...")
                    # Return simulation instead of the error
                    print(f"   Falling back to simulation for {model_id}")
                    return self._simulate_model_response(combination, template, query, domain)
                
            else:
                # Fall back to simulation if client creation failed
                print(f"Warning: Using simulated response for {model_id} due to missing client")
                return self._simulate_model_response(combination, template, query, domain)
        
        except Exception as e:
            # Handle API errors gracefully
            error_message = str(e)
            print(f"Error calling API for {model_id}: {error_message}")
            print(f"Falling back to simulation for {model_id}")
            return self._simulate_model_response(combination, template, query, domain)
        
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            "combination_id": combination["id"],
            "prompt": prompt,
            "response": response_text,
            "metadata": {
                "model": model_id,
                "template_style": template_style,
                "timestamp": time.time(),
                "duration": duration
            }
        }
    
    def _simulate_model_response(
        self,
        combination: Dict[str, Any],
        template: Any,
        query: Query,
        domain: Domain
    ) -> Dict[str, Any]:
        """Simulate a model response for prototype purposes.
        
        Args:
            combination: Combination dictionary.
            template: Instruction template.
            query: Query object.
            domain: Domain object.
            
        Returns:
            Simulated result dictionary.
        """
        # Format the instruction template
        formatted_instruction = template.format({
            "domain": domain.description,
            **query.variables
        })
        
        # Combine the instruction and query
        prompt = f"{formatted_instruction}\n\n{query.text}"
        
        # For simulation purposes, generate a placeholder response
        model_name = combination["model"]
        template_style = template.metadata.get("cognitive_style", "default")
        
        # Generate a placeholder response based on the components
        response_parts = [
            f"This is a simulated response from {model_name} using the {template_style} approach.",
            f"Domain: {domain.name}",
            f"The query was: {query.text}",
            "Here are some ideas that address this challenge:",
        ]
        
        # Add some random "ideas" based on the domain keywords
        ideas = []
        for i in range(3):
            if domain.keywords:
                keyword = random.choice(domain.keywords)
                ideas.append(f"Idea {i+1}: A solution involving {keyword} that addresses the core challenge.")
            else:
                ideas.append(f"Idea {i+1}: A novel approach to solving this problem.")
        
        response_parts.extend(ideas)
        
        # Create a simulation of a conclusion
        response_parts.append(f"These ideas represent a {template_style} approach to the problem within the {domain.name} domain.")
        
        # Join the parts
        response_text = "\n\n".join(response_parts)
        
        return {
            "combination_id": combination["id"],
            "prompt": prompt,
            "response": response_text,
            "metadata": {
                "model": model_name,
                "template_style": template_style,
                "timestamp": time.time(),
                "simulated": True
            }
        }
    
    def evaluate_results(
        self, 
        results: Optional[Dict[str, Any]] = None,
        criteria: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, float]]:
        """Evaluate the results against the scoring criteria.
        
        Args:
            results: Optional dictionary of results to evaluate. If None, uses stored results.
            criteria: Optional list of criteria to evaluate against. If None, uses all criteria.
            
        Returns:
            Dictionary mapping combination IDs to evaluation scores.
        """
        results = results or self.results
        
        if not results:
            print("No results to evaluate")
            return {}
        
        evaluations = {}
        
        for combo_id, result in results.items():
            text = result["response"]
            
            # Score the text
            scores = self.scoring_framework.score_text(text)
            
            if criteria:
                # Filter to only the requested criteria
                scores = {k: v for k, v in scores.items() if k in criteria}
            
            # Calculate the overall score
            overall = self.scoring_framework.calculate_weighted_score(scores)
            scores["overall"] = overall
            
            # Store the scores
            evaluations[combo_id] = scores
            self.evaluations[combo_id] = scores
        
        print(f"Evaluated {len(evaluations)} results")
        return evaluations
    
    def get_top_results(
        self, 
        criterion: str = "overall", 
        n: int = 10
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Get the top N results based on a specific criterion.
        
        Args:
            criterion: The criterion to sort by.
            n: Number of top results to return.
            
        Returns:
            List of (result, score) tuples sorted by the criterion in descending order.
        """
        if not self.evaluations or not self.results:
            print("No evaluated results to rank")
            return []
        
        # Pair results with their scores
        scored_results = []
        for combo_id, evaluation in self.evaluations.items():
            if criterion in evaluation and combo_id in self.results:
                score = evaluation[criterion]
                result = self.results[combo_id]
                scored_results.append((result, score))
        
        # Sort by score in descending order
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        # Return the top N
        return scored_results[:n]
    
    def rename_files_by_rank(self, criterion: str = "overall") -> None:
        """Rename raw response files to include their rank based on evaluation scores.
        
        This method renames files from:
          combo_id_model_template.md
        To:
          01_combo_id_model_template.md (for rank #1)
          02_combo_id_model_template.md (for rank #2)
          etc.
          
        Args:
            criterion: The scoring criterion to rank by (default: "overall")
        """
        if not self.evaluations or not self.results:
            print("No evaluations available for ranking files")
            return
        
        # Get ranked results based on the specified criterion
        ranked_results = self.get_top_results(criterion=criterion, n=len(self.evaluations))
        
        if not ranked_results:
            print("No ranked results available")
            return
        
        responses_dir = Path(self.output_directory) / "raw_responses"
        if not responses_dir.exists():
            print(f"Raw responses directory not found: {responses_dir}")
            return
        
        renamed_count = 0
        errors = []
        
        print(f"🏆 Renaming {len(ranked_results)} raw response files by rank ({criterion} score)...")
        
        for rank, (result, score) in enumerate(ranked_results, 1):
            try:
                combo_id = result.get("combination_id")
                if not combo_id:
                    continue
                
                # Find existing file for this combination
                # First try original pattern, then try pattern with rank prefix
                existing_files = list(responses_dir.glob(f"{combo_id}_*.md"))
                if not existing_files:
                    # Look for already renamed files (with rank prefix)
                    existing_files = list(responses_dir.glob(f"*_{combo_id}_*.md"))
                
                if not existing_files:
                    errors.append(f"Rank {rank}: No file found for combination {combo_id}")
                    continue
                
                old_file = existing_files[0]
                
                # Check if file is already renamed (starts with digits and has correct rank)
                if old_file.name[:2].isdigit() and old_file.name[2] == '_':
                    expected_prefix = f"{rank:02d}_"
                    if old_file.name.startswith(expected_prefix):
                        continue  # Skip files that already have the correct rank
                    else:
                        # File has wrong rank prefix, need to rename it
                        # Strip the old rank prefix first
                        original_name = old_file.name[3:]  # Remove "XX_" prefix
                        new_filename = f"{rank:02d}_{original_name}"
                        new_file = responses_dir / new_filename
                        old_file.rename(new_file)
                        renamed_count += 1
                        if rank <= 10:
                            print(f"  Rank #{rank:2d} (score: {score:.3f}): {old_file.name} → {new_filename}")
                        continue
                
                # Create new filename with rank prefix
                rank_prefix = f"{rank:02d}_"
                new_filename = rank_prefix + old_file.name
                new_file = responses_dir / new_filename
                
                # Rename the file
                old_file.rename(new_file)
                renamed_count += 1
                
                # Show progress for top 10
                if rank <= 10:
                    print(f"  Rank #{rank:2d} (score: {score:.3f}): {old_file.name} → {new_filename}")
                
            except Exception as e:
                errors.append(f"Rank {rank}: Error renaming file - {str(e)}")
        
        # Summary
        print(f"✅ Successfully renamed {renamed_count} files with rank prefixes")
        
        if errors:
            print(f"⚠️  {len(errors)} files had issues:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"     {error}")
            if len(errors) > 5:
                print(f"     ... and {len(errors) - 5} more")
    
    def synthesize_ideas(
        self, 
        top_results: Optional[List[Tuple[Dict[str, Any], float]]] = None,
        method: str = "cluster_based"
    ) -> Dict[str, Any]:
        """Synthesize ideas from the top results.
        
        Args:
            top_results: Optional list of (result, score) tuples. If None, gets top results automatically.
            method: Method to use for synthesis (cluster_based, cross_pollination, etc.).
            
        Returns:
            Dictionary of synthesized ideas.
        """
        if top_results is None:
            top_results = self.get_top_results(n=10)
        
        if not top_results:
            print("No results to synthesize")
            return {}
        
        print(f"Synthesizing ideas from {len(top_results)} top results using {method} method")
        
        # In a real implementation, this would use sophisticated NLP techniques
        # For prototype purposes, we'll just create placeholder synthesized ideas
        synthesized = {}
        
        if method == "cluster_based":
            # Simulate clustering into 3 groups
            clusters = [
                top_results[:len(top_results)//3],
                top_results[len(top_results)//3:2*len(top_results)//3],
                top_results[2*len(top_results)//3:]
            ]
            
            for i, cluster in enumerate(clusters, 1):
                if not cluster:
                    continue
                
                # Create a synthesized idea from this cluster
                idea_id = f"synthesized_idea_{i}"
                
                # Extract information from the results in this cluster
                result_texts = [result["response"] for result, _ in cluster]
                combined_text = "\n\n".join(result_texts)
                
                # Group source combinations by model
                model_contributions = {}
                for result, _ in cluster:
                    model_id = result["metadata"]["model"]
                    model_contributions.setdefault(model_id, 0)
                    model_contributions[model_id] += 1
                
                # Calculate percentage contributions from each model
                total_contributions = sum(model_contributions.values())
                model_percentages = {model: (count / total_contributions) * 100 
                                     for model, count in model_contributions.items()}
                
                # In a real implementation, this would analyze and synthesize the texts
                # For prototype purposes, we'll just create a placeholder
                response_texts = [result["response"] for result, _ in cluster]
                
                # Use the first response's text if available, or create a summary
                if response_texts and len(response_texts[0]) > 0:
                    # Extract a title from the first response
                    lines = response_texts[0].split('\n')
                    title_candidate = next((line for line in lines if len(line) > 5 and len(line) < 80), f"Synthesized Idea {i}")
                    
                    synthesized_idea = {
                        "id": idea_id,
                        "title": title_candidate[:80],  # Use a portion of the first meaningful line as title
                        "description": f"This idea represents a synthesis of {len(cluster)} top-ranked responses.",
                        "source_combinations": [result["combination_id"] for result, _ in cluster],
                        "text": response_texts[0],  # Use the actual response text
                        "metadata": {
                            "method": method,
                            "cluster_id": i,
                            "cluster_size": len(cluster),
                            "average_score": sum(score for _, score in cluster) / len(cluster),
                            "model_contributions": model_contributions,
                            "model_percentages": model_percentages
                        }
                    }
                else:
                    # Fallback to placeholder if no response text is available
                    synthesized_idea = {
                        "id": idea_id,
                        "title": f"Synthesized Idea {i}",
                        "description": f"This idea represents a synthesis of {len(cluster)} top-ranked responses.",
                        "source_combinations": [result["combination_id"] for result, _ in cluster],
                        "text": f"Synthesized text would extract the common themes and innovative elements from cluster {i}.",
                        "metadata": {
                            "method": method,
                            "cluster_id": i,
                            "cluster_size": len(cluster),
                            "average_score": sum(score for _, score in cluster) / len(cluster),
                            "model_contributions": model_contributions,
                            "model_percentages": model_percentages
                        }
                    }
                
                synthesized[idea_id] = synthesized_idea
        
        elif method == "cross_pollination":
            # Simulate cross-pollination by combining elements from top results
            idea_id = "synthesized_idea_crossover"
            
            synthesized_idea = {
                "id": idea_id,
                "title": "Cross-Pollinated Innovation",
                "description": f"This idea combines elements from {len(top_results)} diverse top-ranked responses.",
                "source_combinations": [result["combination_id"] for result, _ in top_results],
                "text": "Cross-pollinated text would extract complementary elements from different responses and combine them in novel ways.",
                "metadata": {
                    "method": method,
                    "sources_count": len(top_results),
                    "average_score": sum(score for _, score in top_results) / len(top_results)
                }
            }
            
            synthesized[idea_id] = synthesized_idea
        
        else:
            print(f"Unknown synthesis method: {method}")
        
        # Store the synthesized ideas
        self.synthesized_ideas.update(synthesized)
        
        print(f"Synthesized {len(synthesized)} ideas")
        return synthesized
    
    def _clean_markdown_content(self, content: str) -> str:
        """Clean markdown content to avoid conflicts with our template structure"""
        if not content:
            return content
            
        # Split into lines for processing
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove leading/trailing whitespace
            line = line.strip()
            
            # Fix multiple header conflicts (## ### patterns)
            if line.startswith('## ### '):
                # Remove the conflicting ## prefix, keep the ###
                line = line[3:]  # Remove "## "
            elif line.startswith('### **') and line.endswith('**'):
                # Convert standalone headers to bold text instead of headers
                line = f"**{line[6:-2]}**"
            elif line.startswith('## **') and line.endswith('**'):
                # Convert h2 headers to h4 to avoid conflicts
                line = f"#### {line[5:-2]}"
            elif line.startswith('# **') and line.endswith('**'):
                # Convert h1 headers to h3 to avoid conflicts  
                line = f"### {line[4:-2]}"
            
            # Fix numbered list issues
            import re
            
            # Convert checkbox-style numbered items to proper checkboxes
            if re.match(r'^\d+\.\s*\[\s*\]', line):
                # Extract the content after the checkbox
                content_match = re.search(r'^\d+\.\s*\[\s*\]\s*(.+)', line)
                if content_match:
                    line = f"- [ ] {content_match.group(1)}"
            
            # Clean up numbered lists that should be bullet points in synthesized content
            elif re.match(r'^\d+\.\s+[A-Z]', line) and not re.match(r'^\d+\.\s+\d', line):
                # Convert numbered items to bullet points (unless they look like sub-numbering)
                content_match = re.search(r'^\d+\.\s+(.+)', line)
                if content_match:
                    line = f"- {content_match.group(1)}"
            
            # Standardize bullet points to use - instead of *
            if line.startswith('* '):
                line = f"- {line[2:]}"
            elif line.startswith('*\t'):
                line = f"- {line[2:]}"
            
            # Clean up bold formatting in headers
            if line.startswith('####') and '**' in line:
                # Remove bold formatting from h4 headers (redundant)
                line = line.replace('**', '')
                
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _clean_title(self, title: str) -> str:
        """Clean and format titles to remove markdown conflicts and improve readability"""
        if not title:
            return "Untitled Finding"
        
        # Remove any leading/trailing whitespace
        title = title.strip()
        
        # Remove markdown formatting from titles
        title = title.replace('**', '').replace('*', '').replace('`', '')
        
        # Remove leading # symbols if present (they don't belong in titles)
        while title.startswith('#'):
            title = title[1:].strip()
        
        # Remove common redundant prefixes
        redundant_prefixes = [
            "Synthesized Idea:",
            "Finding:",
            "Result:",
            "Analysis:",
            "The Documentation Paradox:",
            "# ",
            "## "
        ]
        
        for prefix in redundant_prefixes:
            if title.startswith(prefix):
                title = title[len(prefix):].strip()
        
        # Ensure title doesn't end with a colon unless it's a meaningful subtitle
        if title.endswith(':') and not any(word in title.lower() for word in ['analysis', 'framework', 'approach']):
            title = title[:-1]
        
        # Capitalize first letter if not already
        if title and title[0].islower():
            title = title[0].upper() + title[1:]
        
        return title or "Untitled Finding"
    
    def format_output(
        self, 
        ideas: Optional[Dict[str, Any]] = None, 
        format_type: str = "markdown"
    ) -> str:
        """Format the synthesized ideas for output using improved Option C structure.
        
        Args:
            ideas: Optional dictionary of ideas to format. If None, uses stored synthesized ideas.
            format_type: Output format type (markdown, json, etc.).
            
        Returns:
            Formatted output string with clear 4-part structure.
        """
        ideas = ideas or self.synthesized_ideas
        
        if not ideas:
            return "No synthesized ideas to format"
        
        if format_type == "markdown":
            # Use improved Option C structure: Analysis Setup + Finding 1, 2, 3
            output = "---\n\n"  # Start with separator for clean separation from metadata
            
            for idea_index, (idea_id, idea) in enumerate(ideas.items(), 1):
                # Clean and extract the idea title, removing any markdown formatting quirks
                title = self._clean_title(idea.get('title', f'Finding {idea_index}'))
                
                # Add clear section separator (except for first finding)
                if idea_index > 1:
                    output += "\n---\n\n"
                
                # Use clean Finding numbering (Finding 1, Finding 2, Finding 3)
                output += f"# Finding {idea_index}: {title}\n\n"
                
                # Add description if available
                if idea.get('description'):
                    output += f"{idea['description']}\n\n"
                
                # Add the main content with proper formatting
                if idea.get('text'):
                    cleaned_text = self._clean_markdown_content(idea['text'])
                    output += f"{cleaned_text}\n\n"
                
                # Add metadata in a clean, optional section
                if "metadata" in idea and idea["metadata"]:
                    output += "### Analysis Details\n\n"
                    
                    # Special handling for model contributions with cleaner formatting
                    if "model_contributions" in idea["metadata"]:
                        model_contributions = idea["metadata"]["model_contributions"]
                        
                        # Sort contributions by count (highest first)
                        sorted_contributions = sorted(
                            model_contributions.items(), 
                            key=lambda x: x[1], 
                            reverse=True
                        )
                        
                        # Only show top contributors to avoid clutter
                        output += "**Primary Contributors:** "
                        top_contributors = []
                        for model_id, count in sorted_contributions[:3]:  # Top 3 only
                            model_name = "Unknown"
                            if model_id in self.model_configs:
                                model_name = self.model_configs[model_id].get("name", model_id)
                            
                            percentage = idea["metadata"]["model_percentages"][model_id]
                            top_contributors.append(f"{model_name} ({percentage:.1f}%)")
                        
                        output += ", ".join(top_contributors) + "\n\n"
                    
                    # Display key metadata only
                    metadata_display = idea["metadata"]
                    if "average_score" in metadata_display:
                        output += f"**Average Score:** {metadata_display['average_score']:.3f}\n\n"
            
            return output
        
        elif format_type == "json":
            return json.dumps(ideas, indent=2)
        
        else:
            print(f"Unknown format type: {format_type}")
            return json.dumps(ideas, indent=2)
    
    def show_query_preview(
        self,
        combinations: Optional[List[Dict[str, Any]]] = None,
        sample_count: int = 5,
        show_breakdown: bool = True
    ) -> None:
        """Show preview of complete queries that would be sent to LLMs.
        
        Args:
            combinations: List of combinations to preview. If None, uses stored combinations.
            sample_count: Number of sample queries to show.
            show_breakdown: If True, shows detailed breakdown of query construction.
        """
        combinations = combinations or self.combinations
        
        if not combinations:
            print("No combinations available for preview")
            return
        
        # Sample combinations to show diverse examples
        import random
        sample_combinations = random.sample(combinations, min(sample_count, len(combinations)))
        
        print(f"\n{'='*80}")
        print(f"QUERY PREVIEW: Showing {len(sample_combinations)} representative queries from {len(combinations)} total combinations")
        print(f"{'='*80}")
        
        for i, combo in enumerate(sample_combinations, 1):
            print(f"\n🔍 SAMPLE QUERY {i}/{len(sample_combinations)}")
            print(f"{'─'*60}")
            
            # Get the components
            template = self.template_library.get_template(combo["template"])
            query_obj = self.query_generator.get_query_by_id(combo["query"])
            domain = self.domain_manager.get_domain(combo["domain"])
            
            # Show component breakdown if requested
            if show_breakdown:
                print(f"📋 QUERY COMPONENTS:")
                print(f"  • Combination ID: {combo['id']}")
                print(f"  • Model: {combo['model']}")
                print(f"  • Template: {template.name} ({template.id})")
                print(f"  • Query: {query_obj.text[:100]}{'...' if len(query_obj.text) > 100 else ''}")
                print(f"  • Domain: {domain.name}")
                print(f"  • Template Style: {template.metadata.get('cognitive_style', 'default')}")
                print()
            
            # Format the instruction template
            formatted_instruction = template.format({
                "domain": domain.description,
                **query_obj.variables
            })
            
            # Combine the instruction and query to create the complete prompt
            complete_prompt = f"{formatted_instruction}\n\n{query_obj.text}"
            
            print(f"🤖 COMPLETE QUERY SENT TO LLM:")
            print(f"{'─'*40}")
            print(complete_prompt)
            print(f"{'─'*40}")
            print(f"📊 Query Stats: {len(complete_prompt)} characters, {len(complete_prompt.split())} words")
            
            if i < len(sample_combinations):
                print()
    
    def show_verbose_execution(
        self,
        combinations: Optional[List[Dict[str, Any]]] = None,
        show_every_nth: int = 10
    ) -> None:
        """Show verbose execution with query details for selected combinations.
        
        Args:
            combinations: List of combinations to show. If None, uses stored combinations.
            show_every_nth: Show query details for every nth combination.
        """
        combinations = combinations or self.combinations
        
        if not combinations:
            print("No combinations available for verbose execution")
            return
        
        print(f"\n🔍 VERBOSE EXECUTION MODE: Showing query details for every {show_every_nth} combinations")
        print(f"Total combinations: {len(combinations)}")
        
        for i, combo in enumerate(combinations, 1):
            # Always show the execution line
            print(f"Executing combination {i}/{len(combinations)}: {combo['id']}")
            
            # Show query details for selected combinations
            if i % show_every_nth == 1 or i <= 3 or i >= len(combinations) - 2:
                # Get the components
                template = self.template_library.get_template(combo["template"])
                query_obj = self.query_generator.get_query_by_id(combo["query"])
                domain = self.domain_manager.get_domain(combo["domain"])
                
                # Format the complete prompt
                formatted_instruction = template.format({
                    "domain": domain.description,
                    **query_obj.variables
                })
                complete_prompt = f"{formatted_instruction}\n\n{query_obj.text}"
                
                print(f"  ┌─ Model: {combo['model']}")
                print(f"  ├─ Template: {template.name} ({template.metadata.get('cognitive_style', 'default')})")
                print(f"  ├─ Domain: {domain.name}")
                print(f"  └─ Complete Query ({len(complete_prompt)} chars):")
                
                # Show abbreviated query for space
                if len(complete_prompt) > 200:
                    print(f"     {complete_prompt[:150]}...")
                    print(f"     ...{complete_prompt[-47:]}")
                else:
                    print(f"     {complete_prompt}")
                print()
    
    def run_complete_pipeline(
        self,
        query_text: str,
        domain_names: Optional[List[str]] = None,
        dynamic_domain_names: Optional[List[str]] = None,
        model_count: int = 2,
        instruction_count: int = 3,
        query_variations: int = 2,
        max_combinations: Optional[int] = 10,
        output_format: str = "markdown",
        use_real_models: bool = True,
        # balanced models is now always enabled for maximum diversity
        specific_template_ids: Optional[List[str]] = None,
        verbose_queries: bool = False,
        show_all_queries: bool = False,
        selected_models: Optional[List[str]] = None,
        json_progress: bool = False,
        parallel: bool = True,
        max_workers: int = 8
    ) -> str:
        """Run the complete ISEE pipeline from query to synthesized ideas.
        
        Args:
            query_text: The input query text.
            domain_name: Optional domain name to focus on.
            model_count: Number of models to use.
            instruction_count: Number of instructions to use.
            query_variations: Number of query variations to generate.
            max_combinations: Maximum number of combinations to execute.
            output_format: Output format type.
            use_real_models: If True, uses real model API calls. If False, uses simulation.
            Balanced model representation is now always enabled for maximum diversity.
            
        Returns:
            Formatted output of synthesized ideas.
        """
        print(f"Running complete pipeline for query: {query_text}")
        
        # 1. Create a new query
        from uuid import uuid4
        query_id = f"query_{str(uuid4())[:8]}"
        query = Query(id=query_id, text=query_text)
        self.query_generator.add_base_query(query)
        
        # If specific templates were provided, override the class attribute
        if specific_template_ids:
            self.specific_template_ids = specific_template_ids
            print(f"Using specific instruction templates: {', '.join(specific_template_ids)}")
        
        # 2. Determine domains - support both static and dynamic domains
        domain_ids = None
        
        # Process static domains (with validation)
        if domain_names:
            domain_ids = []
            for domain_name in domain_names:
                # Direct domain ID validation
                if domain_name.startswith('domain_'):
                    # Direct domain ID provided
                    if domain_name in self.domain_manager.domains:
                        domain_ids.append(domain_name)
                        print(f"Using domain ID: {domain_name}")
                    else:
                        print(f"Error: Invalid domain ID '{domain_name}'")
                        print(f"Tip: Use --list-domains to see all available domain IDs.")
                        return
                else:
                    # Domain name provided - find exact match
                    all_domains = self.domain_manager.list_domains()
                    exact_matches = [d for d in all_domains if d.name.lower() == domain_name.lower()]
                    if exact_matches:
                        domain_ids.append(exact_matches[0].id)
                        print(f"Found exact match for '{domain_name}' -> {exact_matches[0].id}")
                    else:
                        print(f"Error: No exact match found for domain '{domain_name}'")
                        print(f"Tip: Use --list-domains to see all available domain names.")
                        return
        
        # Process dynamic domains (no validation - used as contextual guidance)
        if dynamic_domain_names:
            if not domain_ids:
                domain_ids = []
            for dynamic_domain in dynamic_domain_names:
                # Use dynamic domain name directly as context
                domain_ids.append(f"dynamic:{dynamic_domain}")
                print(f"Using dynamic domain: {dynamic_domain}")
        
        # 3. Generate combinations
        combinations = self.generate_combinations(
            query_id=query_id,
            domain_ids=domain_ids,
            model_count=model_count,
            instruction_count=instruction_count,
            query_variations=query_variations,
            # balanced models is now always enabled
            max_combinations=max_combinations,
            selected_models=selected_models
        )
        
        # 4. Execute combinations
        results = self.execute_combinations(
            combinations=combinations,
            max_to_execute=max_combinations,
            use_real_models=use_real_models,
            verbose_queries=verbose_queries,
            show_all_queries=show_all_queries,
            json_progress=json_progress,
            parallel=parallel,
            max_workers=max_workers
        )
        
        # 5. Evaluate results
        evaluations = self.evaluate_results(results=results)
        
        # 5.5. Rename raw response files by rank for easy sharing
        # Skip renaming if --no-rank-files flag is set
        if not getattr(self, 'skip_rank_files', False):
            self.rename_files_by_rank(criterion="overall")
        
        # 6. Get top results
        top_results = self.get_top_results(n=min(10, len(evaluations)))
        
        # 7. Synthesize ideas
        synthesized = self.synthesize_ideas(top_results=top_results)
        
        # 8. Format output
        output = self.format_output(ideas=synthesized, format_type=output_format)
        
        print("Pipeline execution complete")
        return output


class ISEEGuardrails:
    """Guardrail system to prevent excessive resource consumption."""
    
    # Hardware-specific limits
    DEVICE_LIMITS = {
        "laptop": {
            "max_combinations": 100,
            "max_estimated_cost": 15.0,
            "max_estimated_time_minutes": 30,
            "warning_combinations": 50,
            "warning_cost": 8.0,
            "warning_time_minutes": 15
        },
        "workstation": {
            "max_combinations": 500,
            "max_estimated_cost": 50.0,
            "max_estimated_time_minutes": 120,
            "warning_combinations": 200,
            "warning_cost": 25.0,
            "warning_time_minutes": 60
        }
    }
    
    @staticmethod
    def detect_device_type():
        """Detect if running on laptop or workstation based on system specs."""
        try:
            # Get system info
            memory_gb = psutil.virtual_memory().total / (1024**3)
            cpu_count = psutil.cpu_count()
            system = platform.system()
            
            # Simple heuristic for device classification
            if system == "Darwin" and "MacBook" in platform.platform():
                return "laptop"
            elif memory_gb < 16 or cpu_count < 8:
                return "laptop"
            else:
                return "workstation"
        except:
            # Default to laptop for safety
            return "laptop"
    
    @staticmethod
    def estimate_combinations(models, templates, variations, domains=5):
        """Estimate total combinations based on parameters."""
        # Handle string input (comma-separated template IDs)
        if isinstance(templates, str):
            template_count = len([t.strip() for t in templates.split(',') if t.strip()])
        else:
            template_count = templates
            
        return models * template_count * variations * domains
    
    @staticmethod
    def estimate_cost(combinations, has_api_key=True):
        """Estimate API cost based on combination count."""
        if not has_api_key:
            return 0.0
        
        # Conservative cost estimate: $0.05-0.15 per combination
        # Varies based on model and query complexity
        avg_cost_per_combination = 0.08
        return combinations * avg_cost_per_combination
    
    @staticmethod
    def estimate_time_minutes(combinations, simulate=False):
        """Estimate execution time based on combination count."""
        if simulate:
            # Simulation is very fast
            return max(1, combinations * 0.01)  # ~0.6 seconds per 100 combinations
        else:
            # Real API calls: ~2-10 seconds per combination depending on model
            avg_seconds_per_combination = 4
            return (combinations * avg_seconds_per_combination) / 60
    
    @classmethod
    def validate_command_limits(cls, args):
        """Validate command parameters against device limits and return warnings/errors."""
        device_type = cls.detect_device_type()
        limits = cls.DEVICE_LIMITS[device_type]
        
        # Calculate estimated metrics
        template_count = args.instructions
        if args.instruction_templates:
            template_count = len([t.strip() for t in args.instruction_templates.split(',') if t.strip()])
        
        estimated_combinations = cls.estimate_combinations(
            models=args.models,
            templates=template_count,
            variations=args.variations
        )
        
        # Apply max_combinations limit if set
        if args.max_combinations:
            estimated_combinations = min(estimated_combinations, args.max_combinations)
        
        # Check for API keys
        has_api_key = bool(
            os.getenv('ANTHROPIC_API_KEY') or 
            os.getenv('OPENAI_API_KEY') or 
            os.getenv('OPENROUTER_API_KEY')
        )
        
        estimated_cost = cls.estimate_cost(estimated_combinations, has_api_key and not args.simulate)
        estimated_time = cls.estimate_time_minutes(estimated_combinations, args.simulate)
        
        # Check hard limits (BLOCKING)
        errors = []
        if estimated_combinations > limits["max_combinations"]:
            errors.append(f"🚫 COMBINATION LIMIT EXCEEDED: {estimated_combinations:,} combinations")
            errors.append(f"   Maximum allowed for {device_type}: {limits['max_combinations']:,}")
            
        if estimated_cost > limits["max_estimated_cost"]:
            errors.append(f"🚫 COST LIMIT EXCEEDED: ~${estimated_cost:.2f}")
            errors.append(f"   Maximum allowed for {device_type}: ${limits['max_estimated_cost']:.2f}")
            
        if estimated_time > limits["max_estimated_time_minutes"]:
            errors.append(f"🚫 TIME LIMIT EXCEEDED: ~{estimated_time:.1f} minutes")
            errors.append(f"   Maximum allowed for {device_type}: {limits['max_estimated_time_minutes']} minutes")
        
        # Check warning thresholds (INFORMATIONAL)
        warnings = []
        if (estimated_combinations > limits["warning_combinations"] and 
            estimated_combinations <= limits["max_combinations"]):
            warnings.append(f"⚠️  HIGH COMBINATION COUNT: {estimated_combinations:,} combinations")
            
        if (estimated_cost > limits["warning_cost"] and 
            estimated_cost <= limits["max_estimated_cost"]):
            warnings.append(f"⚠️  HIGH ESTIMATED COST: ~${estimated_cost:.2f}")
            
        if (estimated_time > limits["warning_time_minutes"] and 
            estimated_time <= limits["max_estimated_time_minutes"]):
            warnings.append(f"⚠️  LONG EXECUTION TIME: ~{estimated_time:.1f} minutes")
        
        return {
            "device_type": device_type,
            "estimated_combinations": estimated_combinations,
            "estimated_cost": estimated_cost,
            "estimated_time_minutes": estimated_time,
            "errors": errors,
            "warnings": warnings,
            "limits": limits
        }
    
    @classmethod
    def print_optimization_suggestions(cls, validation_result, args):
        """Print helpful optimization suggestions."""
        print("\n💡 OPTIMIZATION SUGGESTIONS:")
        
        if validation_result["estimated_combinations"] > 100:
            print("   • Reduce --models (currently: {}) to 3-5".format(args.models))
            print("   • Use --max-combinations 50 to limit execution")
            print("   • Try --sampling-method stratified for intelligent selection")
        
        if validation_result["estimated_cost"] > 5:
            print("   • Add --simulate for free testing")
            print("   • Use --quick mode for faster runs")
            
        if validation_result["estimated_time_minutes"] > 15:
            print("   • Add --max-combinations to limit execution time")
            print("   • Consider breaking into multiple smaller runs")
        
        print("   • Start with --dry-run to preview without executing")
        print()


def generate_metadata_header(args, app, execution_start_time, execution_end_time=None, combinations=None):
    """Generate comprehensive metadata header for result files."""
    from datetime import datetime
    
    # Determine query display based on whether enhancement was used
    if hasattr(args, 'original_query') and hasattr(args, 'enhancement_type'):
        # Enhancement was used
        header_lines = [
            "# Query Information",
            "",
            f"**Enhanced Query** ({args.enhancement_type}):",
            args.query if args.query else "No query specified",
            "",
            "**Original Query:**",
            args.original_query,
            "",
            f"**Enhancement Rationale:** {args.enhancement_rationale}",
            "",
            "# Parameters",
        ]
    else:
        # No enhancement used
        header_lines = [
            "# Query Information", 
            "",
            args.query if args.query else "No query specified",
            "",
            "# Parameters",
        ]
    
    # Continue with common header elements
    header_lines.extend([
        "",
        "## Cognitive Frameworks",
        ""
    ])
    
    # Extract selected frameworks from args
    if hasattr(args, 'instruction_templates') and args.instruction_templates:
        template_ids = [t.strip() for t in args.instruction_templates.split(',')]
        framework_names = []
        framework_mapping = {
            "ins_analytical": "Analytical",
            "ins_creative": "Creative", 
            "ins_critical": "Critical",
            "ins_integrative": "Integrative",
            "ins_pragmatic": "Pragmatic",
            "ins_first_principles": "First Principles",
            "ins_systems": "Systems",
            "ins_contrarian": "Contrarian",
            "ins_historical": "Historical",
            "ins_futurist": "Future-Oriented"
        }
        for template_id in template_ids:
            framework_names.append(f"- {framework_mapping.get(template_id, template_id)}")
        header_lines.append("\n".join(framework_names))
    else:
        header_lines.append(f"Count: {args.instructions if args.instructions else 'Default'}")
    
    header_lines.extend([
        "",
        "## LLMs",
        ""
    ])
    
    # Extract selected models
    if hasattr(args, 'selected_models') and args.selected_models:
        selected_models = [m.strip() for m in args.selected_models.split(',')]
        model_names = []
        for model_id in selected_models:
            if model_id in app.model_configs:
                model_name = app.model_configs[model_id].get("name", model_id)
                model_names.append(f"- {model_name}")
            else:
                model_names.append(f"- {model_id}")
        header_lines.append("\n".join(model_names))
    else:
        header_lines.append(f"Count: {args.models if args.models else 'Default'}")
    
    header_lines.extend([
        "",
        "## Knowledge Domains",
        ""
    ])
    
    # Extract domains (both static and dynamic)
    domain_names = []
    
    # Add static domains from args.domain
    if hasattr(args, 'domain') and args.domain:
        for domain_id in args.domain:
            if domain_id.startswith('dynamic:'):
                # Handle dynamic domains that might be in the static domain list
                dynamic_name = domain_id.replace('dynamic:', '')
                domain_names.append(f"- {dynamic_name} (Dynamic)")
            elif domain_id.startswith('domain_'):
                # Convert static domain ID to readable name with better formatting
                name = domain_id.replace('domain_', '').replace('_', ' ')
                # Handle special cases and proper capitalization
                name_parts = name.split()
                formatted_parts = []
                for part in name_parts:
                    if part.lower() in ['ai', 'ml', 'it', 'ux', 'ui', 'api', 'iot']:
                        formatted_parts.append(part.upper())
                    elif part.lower() in ['and', 'or', 'of', 'in', 'on', 'at', 'to', 'for']:
                        formatted_parts.append(part.lower())
                    else:
                        formatted_parts.append(part.capitalize())
                name = ' '.join(formatted_parts)
                domain_names.append(f"- {name}")
            else:
                domain_names.append(f"- {domain_id}")
    
    # Add dynamic domains from args.dynamic_domain
    if hasattr(args, 'dynamic_domain') and args.dynamic_domain:
        for dynamic_domain in args.dynamic_domain:
            domain_names.append(f"- {dynamic_domain} (Dynamic)")
    
    # Output the domain list
    if domain_names:
        header_lines.append("\n".join(domain_names))
    else:
        header_lines.append("Default domain selection")
    
    # Format execution settings with better structure
    # Use actual number of combinations executed instead of misleading variations parameter
    if combinations:
        actual_combinations = len(combinations)
    elif hasattr(app, 'results') and app.results:
        actual_combinations = len(app.results)
    else:
        actual_combinations = 0
    max_combinations = args.max_combinations if args.max_combinations else 'Unlimited'
    output_format = args.output_format.title() if args.output_format else 'Markdown'
    
    # Determine analysis depth based on actual combinations executed
    if actual_combinations <= 20:
        depth_label = "Quick Exploration"
    elif actual_combinations <= 45:
        depth_label = "Balanced Analysis"
    else:
        depth_label = "Deep Analysis"
    
    # Determine combination scope
    if isinstance(max_combinations, int):
        if max_combinations <= 30:
            scope_label = "Quick"
        elif max_combinations <= 60:
            scope_label = "Balanced"
        else:
            scope_label = "Comprehensive"
    else:
        scope_label = "Unlimited"
    
    header_lines.extend([
        "",
        "## Execution Settings",
        "",
        f"- **Analysis Depth**: {actual_combinations} LLM calls ({depth_label})",
        f"- **Output Format**: {output_format}",
        ""
    ])
    
    # Add execution status
    if execution_end_time:
        duration = int((execution_end_time - execution_start_time).total_seconds())
        status_line = f"**Execution completed successfully!**  \nDuration: {duration} seconds"
        if hasattr(args, 'output_file') and args.output_file:
            result_filename = os.path.basename(args.output_file)
            status_line += f"  \nResults file: {result_filename}"
    else:
        status_line = "**Execution in progress...**"
    
    header_lines.extend([
        status_line,
        ""
    ])
    
    # Add separator
    header_lines.extend([
        "---",
        "",
        ""
    ])
    
    return "\n".join(header_lines)


def update_latest_symlink(run_output_dir: str) -> None:
    """Update the 'latest' symlink to point to the most recent run directory.
    
    Args:
        run_output_dir: Path to the completed run directory
    """
    try:
        # Get the output base directory
        output_base = os.path.join("data", "output")
        latest_link = os.path.join(output_base, "latest")
        
        # Convert run_output_dir to relative path from output directory
        if run_output_dir.startswith(output_base):
            # Handle both organized (monthly/weekly) and flat structures
            relative_path = os.path.relpath(run_output_dir, output_base)
        else:
            # Fallback: use just the run folder name
            relative_path = os.path.basename(run_output_dir)
        
        # Remove existing symlink if it exists
        if os.path.islink(latest_link):
            os.unlink(latest_link)
        elif os.path.exists(latest_link):
            # Handle case where 'latest' is a regular directory/file
            if os.path.isdir(latest_link):
                os.rmdir(latest_link)
            else:
                os.remove(latest_link)
        
        # Create new symlink
        os.symlink(relative_path, latest_link)
        print(f"Updated 'latest' symlink to point to: {relative_path}")
        
    except Exception as e:
        print(f"Warning: Could not update 'latest' symlink: {e}")
        # Don't fail the whole run if symlink update fails


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Idea Synthesis and Extraction Engine")
    
    # Main commands
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--save-state", help="Save application state to file")
    parser.add_argument("--load-state", help="Load application state from file")
    parser.add_argument("--domain-config", help="Path to a domain-specific configuration file")
    
    # Pipeline parameters
    parser.add_argument("--query", help="Input query text")
    parser.add_argument("--domain", action="append", help="Domain to focus on (can be used multiple times)")
    parser.add_argument("--dynamic-domain", action="append", help="Dynamic domain name (bypasses validation, can be used multiple times)")
    parser.add_argument("--models", type=int, default=2, help="Number of models to use (set to a higher number to include more models)")
    parser.add_argument("--selected-models", type=str, help="Comma-separated list of specific model IDs to use (overrides --models count)")
    parser.add_argument("--use-ollama", action="store_true", help="Include Ollama models in the model selection (automatic when using unified_config.json)")
    parser.add_argument("--instructions", type=int, default=3, help="Number of instructions to use")
    parser.add_argument("--instruction-templates", help="Comma-separated list of specific template IDs to use (overrides --instructions count)")
    parser.add_argument("--variations", type=int, default=2, help="Number of query variations to generate")
    parser.add_argument("--max-combinations", type=int, help="Maximum number of combinations to execute")
    # Sampling method removed - ISEE now uses exhaustive sampling with balanced models for maximum diversity
    parser.add_argument("--output-format", choices=["markdown", "json"], default="markdown", help="Output format")
    parser.add_argument("--output-file", help="Path to save the output to")
    parser.add_argument("--output-directory", help="Directory to save reports to")
    parser.add_argument("--simulate", action="store_true", help="Use simulated responses instead of real model APIs")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be executed without actually running")
    # Balanced models is now enabled by default for maximum diversity - no longer needs to be specified
    parser.add_argument("--synthesize-method", choices=["cluster_based", "cross_pollination"], default="cluster_based", 
                        help="Method to use for synthesizing ideas (cluster_based or cross_pollination)")
    parser.add_argument("--generate-reports", action="store_true", help="Generate detailed reports")
    parser.add_argument("--report-format", choices=["markdown", "json"], default="markdown", help="Format for generated reports")
    parser.add_argument("--export-csv", action="store_true", help="Export data as CSV files for analysis")
    parser.add_argument("--no-rank-files", action="store_true", help="Skip renaming raw response files with rank prefixes (useful for programmatic processing)")
    parser.add_argument("--analyze-results", action="store_true", help="Perform analysis of results with visualizations")
    parser.add_argument("--no-visualizations", action="store_true", help="Skip generating visualization charts during analysis")
    # Add simple preset flag options
    parser.add_argument("--quick", action="store_true", help="Run in quick mode (exhaustive sampling with 36 combinations limit)")
    parser.add_argument("--full", action="store_true", help="Run in full mode (exhaustive combinations)")
    parser.add_argument("--list-domains", action="store_true", help="List all available domains and exit")
    parser.add_argument("--expert-mode", action="store_true", help="Bypass guardrail limits (use with caution)")
    parser.add_argument("--force", action="store_true", help="Force execution despite guardrail warnings")
    parser.add_argument("--verbose-queries", action="store_true", help="Show sample complete queries being sent to LLMs")
    parser.add_argument("--show-all-queries", action="store_true", help="Show complete query for every combination (very verbose)")
    parser.add_argument("--query-preview-only", action="store_true", help="Show representative queries without executing")
    parser.add_argument("--enhance-query", action="store_true", help="Show enhanced versions of the input query based on proven patterns")
    parser.add_argument("--json-progress", action="store_true", help="Output structured JSON progress information for Web UI parsing")
    parser.add_argument("--parallel", action="store_true", help="Use parallel execution for faster processing")
    parser.add_argument("--max-workers", type=int, default=8, help="Maximum concurrent workers for parallel execution")
    parser.add_argument("--provider", choices=["openrouter", "globant", "hybrid"], default="openrouter", 
                        help="API provider to use (openrouter, globant, or hybrid for intelligent switching)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check for enhancement information from Web UI (passed via environment variables)
    if os.getenv('ISEE_ORIGINAL_QUERY') and os.getenv('ISEE_ENHANCEMENT_TYPE'):
        args.original_query = os.getenv('ISEE_ORIGINAL_QUERY')
        args.enhancement_type = os.getenv('ISEE_ENHANCEMENT_TYPE') 
        args.enhancement_rationale = os.getenv('ISEE_ENHANCEMENT_RATIONALE', '')
    
    # Check if we should list domains and exit
    if args.list_domains:
        # We need to initialize the application first to load domains
        app = ISEEApplication(config_path=args.config, output_directory=args.output_directory)
        
        # Load domain-specific config if provided
        if args.domain_config and os.path.exists(args.domain_config):
            try:
                with open(args.domain_config, 'r') as f:
                    domain_data = json.load(f)
                    if "domains" in domain_data:
                        # Create a new domain manager to replace the existing one
                        app.domain_manager = DomainManager()
                        for domain_info in domain_data["domains"]:
                            domain = Domain.from_dict(domain_info)
                            app.domain_manager.add_domain(domain)
            except Exception as e:
                print(f"Error loading domain config: {str(e)}")
        
        # Print all domains
        print("\nAvailable Domains:")
        print("=================")
        for domain in app.domain_manager.list_domains():
            print(f"ID: {domain.id}")
            print(f"Name: {domain.name}")
            print(f"Description: {domain.description}")
            print(f"Keywords: {', '.join(domain.keywords)}")
            print()
        
        # Exit after listing domains
        sys.exit(0)
    
    # Check if API keys are available
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    
    # Check API and Ollama availability
    ollama_available = False
    ollama_models = []
    try:
        from model_api_integration import ModelAPIFactory
        ollama_client = ModelAPIFactory.create_client("ollama")
        ollama_models = ollama_client.get_available_models()
        if ollama_models:
            ollama_available = True
    except Exception:
        # Silently fail if Ollama check fails
        pass
    
    # Show API status
    api_status = []
    if anthropic_key:
        api_status.append("Anthropic API key found")
    if openai_key:
        api_status.append("OpenAI API key found")
    if openrouter_key:
        api_status.append("OpenRouter API key found (300+ models available)")
    if ollama_available:
        api_status.append(f"Ollama available with {len(ollama_models)} models")
    
    if api_status:
        print(f"API Status: {', '.join(api_status)}")
        print("Real model API calls can be used. Use --simulate to use simulation instead.")
        
        # Show Ollama models if available
        if ollama_available:
            print(f"\nAvailable Ollama models: {', '.join(ollama_models)}")
            
        # Check for unified_config.json and suggest it if available
        if os.path.exists("unified_config.json") and not args.config:
            print("\nUNIFIED CONFIG DETECTED: For best results with your available models, consider using:")
            print("python main.py --config unified_config.json --query \"Your query here\"")
            if ollama_available and not (anthropic_key or openai_key or openrouter_key):
                print("This configuration will automatically use only Ollama models since no API keys are present.")
            
    else:
        print("API Status: No API providers found.")
        print("Options:")
        print("1. Create a .env file with ANTHROPIC_API_KEY, OPENAI_API_KEY, and/or OPENROUTER_API_KEY")
        print("2. Install Ollama (https://ollama.com) and run 'ollama serve'")
        print("3. Use --simulate to run with simulation mode")
        print("4. Run 'python command_wizard.py' for interactive OpenRouter setup")
    print()
    
    # Initialize the application
    app = ISEEApplication(config_path=args.config, output_directory=args.output_directory)
    
    # Set provider mode from CLI argument
    app.set_provider_mode(args.provider)
    
    # Set rank files flag
    app.skip_rank_files = args.no_rank_files
    
    # Process specific template IDs if provided
    if args.instruction_templates:
        # Split comma-separated string into list of template IDs
        app.specific_template_ids = [template_id.strip() for template_id in args.instruction_templates.split(',')]
        print(f"Using specific instruction templates: {', '.join(app.specific_template_ids)}")
    
    # Process specific model IDs if provided
    selected_models = None
    if args.selected_models:
        # Split comma-separated string into list of model IDs
        selected_models = [model_id.strip() for model_id in args.selected_models.split(',')]
        print(f"Using specific models: {', '.join(selected_models)}")
    
    # Load domain-specific config if provided
    if args.domain_config and os.path.exists(args.domain_config):
        try:
            with open(args.domain_config, 'r') as f:
                domain_data = json.load(f)
                if "domains" in domain_data:
                    # Create a new domain manager to replace the existing one
                    app.domain_manager = DomainManager()
                    for domain_info in domain_data["domains"]:
                        domain = Domain.from_dict(domain_info)
                        app.domain_manager.add_domain(domain)
                    print(f"Loaded {len(domain_data['domains'])} domains from {args.domain_config}")
        except Exception as e:
            print(f"Error loading domain config: {str(e)}")
    
    # Load state if requested
    if args.load_state:
        app.load_state(args.load_state)
        
        # If synthesize-method is provided without a query, just synthesize from loaded state
        if args.synthesize_method and not args.query:
            top_results = app.get_top_results(n=10)
            if top_results:
                synthesized = app.synthesize_ideas(top_results=top_results, method=args.synthesize_method)
                output = app.format_output(ideas=synthesized, format_type=args.output_format)
                
                # Determine output path - either user-specified or auto-generated in run-specific directory
                output_path = args.output_file
                if not output_path:
                    # Use .md extension instead of .markdown for better compatibility
                    extension = "md" if args.output_format == "markdown" else args.output_format
                    filename = f"isee_result.{extension}"
                    # Use the run-specific output directory
                    output_path = os.path.join(app.run_output_dir, filename)
                
                # If user specified a filename without a path, put it in the run directory
                elif not os.path.dirname(output_path):
                    output_path = os.path.join(app.run_output_dir, output_path)
                    
                # Write the output
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w') as f:
                    f.write(output)
                print(f"Output saved to {output_path}")
                
                # Also print a preview if not redirected
                if not args.output_file:
                    preview_lines = output.split('\n')[:20]  # First 20 lines as preview
                    print("\nOutput Preview:")
                    print("=" * 80)
                    print('\n'.join(preview_lines))
                    if len(output.split('\n')) > 20:
                        print("...")
                        print(f"Full output available in {output_path}")
                    
                # Save state if requested
                if args.save_state:
                    app.save_state(args.save_state)
                    
                # Exit after synthesis
                return
    
    # Determine if we should use simulation mode
    use_simulation = args.simulate
    if not use_simulation and not (anthropic_key or openai_key or openrouter_key or ollama_available):
        print("No API keys available. Forcing simulation mode.")
        use_simulation = True
    
    # Apply quick and full presets
    if args.quick:
        if not args.max_combinations:
            args.max_combinations = 36
    # Full mode now just removes max_combinations limit
        
    # Get config settings if available
    max_combinations = args.max_combinations
    
    # Command line args override config settings
    if hasattr(app, 'execution_settings'):
        # Use config settings if command line args not provided
        if not args.max_combinations and 'max_combinations' in app.execution_settings:
            max_combinations = app.execution_settings['max_combinations']
            print(f"Using max combinations from config: {max_combinations}")
    
    # Handle query enhancement if requested
    if args.enhance_query and args.query:
        from query_enhancement import get_enhancement_service
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich import box
        
        console = Console()
        
        console.print("\n[bold blue]✨ Query Enhancement System[/bold blue]")
        console.print(f"[dim]Original query:[/dim] {args.query}")
        
        try:
            enhancement_service = get_enhancement_service()
            result = enhancement_service.enhance_query(args.query)
            
            # Display analysis
            console.print(f"\n[green]Enhancement Analysis (processed in {result.processing_time_ms:.1f}ms):[/green]")
            console.print(Panel(result.enhancement_analysis, box=box.ROUNDED))
            
            # Create table for enhanced versions
            table = Table(title="Enhanced Query Versions", box=box.ROUNDED)
            table.add_column("Type", style="cyan", width=20)
            table.add_column("Expected Improvement", style="green", width=18)
            table.add_column("Confidence", style="yellow", width=12)
            table.add_column("Enhanced Query", style="white", width=80)
            
            for i, enhancement in enumerate(result.enhanced_versions):
                table.add_row(
                    enhancement.type.value,
                    enhancement.expected_quality_improvement,
                    f"{enhancement.confidence_score:.0%}",
                    enhancement.query[:300] + ("..." if len(enhancement.query) > 300 else "")
                )
            
            console.print("\n")
            console.print(table)
            
            # Show detailed versions
            for i, enhancement in enumerate(result.enhanced_versions):
                console.print(f"\n[bold cyan]Option {i+1}: {enhancement.type.value}[/bold cyan]")
                console.print(f"[green]{enhancement.expected_quality_improvement}[/green] | [yellow]{enhancement.confidence_score:.0%} confidence[/yellow]")
                console.print(Panel(enhancement.query, title="Enhanced Query", box=box.MINIMAL))
                console.print(f"[dim]Rationale: {enhancement.rationale}[/dim]")
            
            # Ask user to select an enhancement
            console.print(f"\n[bold]Would you like to use one of these enhanced versions?[/bold]")
            console.print("[dim]Enter the option number (1-{}) to use that enhancement, or press Enter to keep original:[/dim]".format(len(result.enhanced_versions)))
            
            choice = input().strip()
            
            if choice.isdigit():
                choice_num = int(choice) - 1
                if 0 <= choice_num < len(result.enhanced_versions):
                    selected_enhancement = result.enhanced_versions[choice_num]
                    args.query = selected_enhancement.query
                    console.print(f"[green]✅ Using {selected_enhancement.type.value} enhancement[/green]")
                    console.print(f"[dim]Updated query:[/dim] {args.query[:100]}{'...' if len(args.query) > 100 else ''}")
                else:
                    console.print("[yellow]Invalid selection. Using original query.[/yellow]")
            else:
                console.print("[blue]Using original query.[/blue]")
            
            # Update analytics
            analytics = enhancement_service.get_analytics()
            console.print(f"\n[dim]Enhancement Analytics: {analytics['total_enhancements']} queries enhanced, avg processing time: {analytics['average_processing_time']:.1f}ms[/dim]")
            
            # Store enhancement information for reporting
            if choice.isdigit() and 0 <= int(choice) - 1 < len(result.enhanced_versions):
                selected_enhancement = result.enhanced_versions[int(choice) - 1]
                args.original_query = result.original  # Store original for reporting
                args.enhancement_type = selected_enhancement.type.value
                args.enhancement_rationale = selected_enhancement.rationale
            
        except Exception as e:
            console.print(f"[red]Enhancement failed: {e}[/red]")
            console.print("[yellow]Continuing with original query...[/yellow]")
        
        console.print("\n" + "="*80 + "\n")
    
    # Run pipeline if query is provided
    if args.query:
        # GUARDRAIL VALIDATION - Check limits before execution
        if not args.expert_mode:
            validation_result = ISEEGuardrails.validate_command_limits(args)
            
            # Print device info and estimates
            print(f"\n🖥️  Device Type: {validation_result['device_type'].title()}")
            print(f"📊 Estimated: {validation_result['estimated_combinations']:,} combinations, "
                  f"${validation_result['estimated_cost']:.2f} cost, "
                  f"{validation_result['estimated_time_minutes']:.1f} min")
            
            # Handle HARD LIMITS (blocking errors)
            if validation_result['errors']:
                print("\n🚫 COMMAND REJECTED - Exceeds safety limits:")
                for error in validation_result['errors']:
                    print(f"   {error}")
                
                ISEEGuardrails.print_optimization_suggestions(validation_result, args)
                
                print("🔧 To bypass these limits, add --expert-mode (use with caution)")
                print("   Example: python main.py --expert-mode [your command]")
                sys.exit(1)
            
            # Handle WARNINGS (informational)
            if validation_result['warnings']:
                print("\n⚠️  PERFORMANCE WARNINGS:")
                for warning in validation_result['warnings']:
                    print(f"   {warning}")
                
                if not args.force:
                    ISEEGuardrails.print_optimization_suggestions(validation_result, args)
                    print("🚀 To proceed anyway, add --force")
                    print("   Example: python main.py --force [your command]")
                    sys.exit(1)
            
            print("✅ Command within safety limits\n")
        else:
            print("🔥 EXPERT MODE: Guardrails bypassed\n")
        
        # If dry run is specified, just print what would be executed
        if args.dry_run:
            # Handle multiple domains for dry run using direct mapping
            domain_ids = None
            if args.domain:
                domain_ids = []
                for domain_name in args.domain:
                    # Direct domain ID validation
                    if domain_name.startswith('domain_'):
                        if domain_name in app.domain_manager.domains:
                            domain_ids.append(domain_name)
                            print(f"Using domain ID: {domain_name}")
                        else:
                            print(f"Error: Invalid domain ID '{domain_name}'")
                            sys.exit(1)
                    else:
                        # Domain name provided - find exact match
                        all_domains = app.domain_manager.list_domains()
                        exact_matches = [d for d in all_domains if d.name.lower() == domain_name.lower()]
                        if exact_matches:
                            domain_ids.append(exact_matches[0].id)
                            print(f"Found exact match for '{domain_name}' -> {exact_matches[0].id}")
                        else:
                            print(f"Error: No exact match found for domain '{domain_name}'")
                            sys.exit(1)
            
            combinations = app.generate_combinations(
                query_id=app.query_generator.list_base_queries()[0].id,
                domain_ids=domain_ids,
                model_count=args.models,
                instruction_count=args.instructions,
                query_variations=args.variations,
                # exhaustive + balanced is now the default
                max_combinations=max_combinations,
                selected_models=selected_models
            )
            app.execute_combinations(
                combinations=combinations,
                max_to_execute=max_combinations,
                dry_run=True
            )
        else:
            # Handle query preview mode
            if args.query_preview_only:
                print("🔍 QUERY PREVIEW MODE: Generating combinations and showing representative queries")
                
                # Handle multiple domains for query preview using direct mapping
                domain_ids = None
                if args.domain:
                    domain_ids = []
                    for domain_name in args.domain:
                        # Direct domain ID validation
                        if domain_name.startswith('domain_'):
                            if domain_name in app.domain_manager.domains:
                                domain_ids.append(domain_name)
                                print(f"Using domain ID: {domain_name}")
                            else:
                                print(f"Error: Invalid domain ID '{domain_name}'")
                                sys.exit(1)
                        else:
                            # Domain name provided - find exact match
                            all_domains = app.domain_manager.list_domains()
                            exact_matches = [d for d in all_domains if d.name.lower() == domain_name.lower()]
                            if exact_matches:
                                domain_ids.append(exact_matches[0].id)
                                print(f"Found exact match for '{domain_name}' -> {exact_matches[0].id}")
                            else:
                                print(f"Error: No exact match found for domain '{domain_name}'")
                                sys.exit(1)
                
                # Generate combinations without executing
                combinations = app.generate_combinations(
                    query_id=app.query_generator.list_base_queries()[0].id,
                    domain_ids=domain_ids,
                    model_count=args.models,
                    instruction_count=args.instructions,
                    query_variations=args.variations,
                    max_combinations=max_combinations,
                    selected_models=selected_models
                )
                
                # Show query preview
                app.show_query_preview(combinations=combinations, sample_count=8, show_breakdown=True)
                return
            
            # Process instruction templates parameter if provided
            specific_templates = None
            if args.instruction_templates:
                specific_templates = [template_id.strip() for template_id in args.instruction_templates.split(',')]
            
            # Track execution timing for metadata
            execution_start_time = datetime.now()
            
            output = app.run_complete_pipeline(
                query_text=args.query,
                domain_names=args.domain,
                dynamic_domain_names=args.dynamic_domain,
                model_count=args.models,
                instruction_count=args.instructions,
                query_variations=args.variations,
                max_combinations=max_combinations,
                output_format=args.output_format,
                use_real_models=not use_simulation,
                # exhaustive + balanced models is now the default
                specific_template_ids=specific_templates,
                verbose_queries=args.verbose_queries,
                show_all_queries=args.show_all_queries,
                selected_models=selected_models,
                json_progress=args.json_progress,
                parallel=args.parallel,
                max_workers=args.max_workers
            )
            
            execution_end_time = datetime.now()
            
            # Apply custom synthesis method if specified
            if args.synthesize_method and args.synthesize_method != "cluster_based":
                print(f"Applying {args.synthesize_method} synthesis method...")
                top_results = app.get_top_results(n=10)
                if top_results:
                    synthesized = app.synthesize_ideas(top_results=top_results, method=args.synthesize_method)
                    output = app.format_output(ideas=synthesized, format_type=args.output_format)
        
        # Print or save the output if not a dry run
        if not args.dry_run:
            # Determine output path - either user-specified or auto-generated in run-specific directory
            output_path = args.output_file
            if not output_path:
                # Use .md extension instead of .markdown for better compatibility
                extension = "md" if args.output_format == "markdown" else args.output_format
                filename = f"isee_result.{extension}"
                # Use the run-specific output directory
                output_path = os.path.join(app.run_output_dir, filename)
            
            # If user specified a filename without a path, put it in the run directory
            elif not os.path.dirname(output_path):
                output_path = os.path.join(app.run_output_dir, output_path)
                
            # Generate metadata header and combine with output
            metadata_header = generate_metadata_header(args, app, execution_start_time, execution_end_time)
            combined_output = metadata_header + output
            
            # Write the output with metadata header
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(combined_output)
            print(f"Output saved to {output_path}")
            
            # Also print a preview if not redirected
            if not args.output_file:
                preview_lines = combined_output.split('\n')[:20]  # First 20 lines as preview
                print("\nOutput Preview:")
                print("=" * 80)
                print('\n'.join(preview_lines))
                if len(combined_output.split('\n')) > 20:
                    print("...")
                    print(f"Full output available in {output_path}")
            
            # Generate additional reports if requested
            if args.generate_reports:
                print("\nGenerating detailed reports...")
                report_files = generate_reports(
                    app=app,
                    args=args,
                    query=args.query,
                    combinations=app.combinations,
                    results=app.results,
                    evaluations=app.evaluations,
                    synthesized_ideas=app.synthesized_ideas,
                    run_output_dir=app.run_output_dir
                )
                
                print("Reports generated:")
                for report_name, file_path in report_files.items():
                    print(f"- {report_name.capitalize()} report: {file_path}")
                
                # Perform analysis if requested
                if args.analyze_results:
                    print("\nAnalyzing results...")
                    # Prefer app's run directory if available
                    output_directory = app.run_output_dir if hasattr(app, 'run_output_dir') else (args.output_directory if args.output_directory else "data/output")
                    generate_visualizations = not args.no_visualizations
                    
                    # CSV files are now directly in the run directory, no timestamp needed
                    analysis_report, visualization_files = analyze_results(
                        data_directory=output_directory,
                        output_directory=output_directory,
                        output_format=args.report_format,
                        run_timestamp=None,  # Not needed with new directory structure
                        generate_visualizations=generate_visualizations
                    )
                    
                    # Save analysis report with simple name in run directory
                    # Always use .md extension for markdown files for consistency
                    extension = "md" if args.report_format == "markdown" else args.report_format
                    analysis_filename = f"analysis.{extension}"
                    analysis_path = os.path.join(output_directory, analysis_filename)
                    
                    with open(analysis_path, 'w') as f:
                        f.write(analysis_report)
                    
                    print(f"Analysis report saved to: {analysis_path}")
                    
                    if visualization_files:
                        print("Visualizations generated:")
                        for viz_file in visualization_files:
                            print(f"- {viz_file}")
    
    # Save state if requested
    if args.save_state:
        app.save_state(args.save_state)
    
    # Update 'latest' symlink to point to this run
    if hasattr(app, 'run_output_dir') and app.run_output_dir:
        update_latest_symlink(app.run_output_dir)


if __name__ == "__main__":
    main()