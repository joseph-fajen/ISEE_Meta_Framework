#!/usr/bin/env python3
"""
ISEE Command Construction Wizard

A terminal-based interactive wizard that helps users construct valid ISEE commands
with proper parameters and options.
"""

import os
import re
import sys
import json
import argparse
import subprocess
import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# Import cost estimation module (from UX Enhancement Roadmap - Step 1.1)
try:
    from cost_estimation import CostEstimator
    COST_ESTIMATION_AVAILABLE = True
except ImportError:
    COST_ESTIMATION_AVAILABLE = False
    
# Import parameter context module (from UX Enhancement Roadmap - Step 1.2)
try:
    from parameter_context import ParameterContext
    PARAMETER_CONTEXT_AVAILABLE = True
except ImportError:
    PARAMETER_CONTEXT_AVAILABLE = False

# Import purpose categories module (from UX Enhancement Roadmap - Step 2.1)
try:
    from purpose_categories import PurposeManager, create_default_purpose_manager
    PURPOSE_SELECTION_AVAILABLE = True
except ImportError:
    PURPOSE_SELECTION_AVAILABLE = False

# Import preset manager module (from UX Enhancement Roadmap - Step 2.2)
try:
    from preset_manager import PresetManager, create_default_preset_manager
    PRESET_MANAGER_AVAILABLE = True
except ImportError:
    PRESET_MANAGER_AVAILABLE = False

# Import cognitive framework visualizer (from UX Enhancement Roadmap - Step 3.1)
try:
    from cognitive_framework_visualizer import CognitiveFrameworkVisualizer, create_framework_visualizer
    FRAMEWORK_VISUALIZER_AVAILABLE = True
except ImportError:
    FRAMEWORK_VISUALIZER_AVAILABLE = False

# Rich is required - fail fast with clear error message
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.table import Table
    from rich import print as rprint
except ImportError:
    print("ERROR: This application requires the 'rich' library.")
    print("Install with: pip install rich")
    print("Or install all requirements: pip install -r requirements.txt")
    sys.exit(1)

# Import components from the ISEE framework
try:
    from domain_manager import DomainManager, Domain, create_default_domains
    from instruction_templates import TemplateLibrary, create_default_library
    from model_api_integration import ModelAPIFactory
except ImportError as e:
    print(f"Error importing ISEE components: {str(e)}")
    print("Make sure you're running this script from the ISEE framework directory.")
    sys.exit(1)

# Import OpenRouter categorization (OpenRouter Integration Stage 2)
try:
    from openrouter_categorization import OpenRouterCategorizer
    OPENROUTER_CATEGORIZATION_AVAILABLE = True
except ImportError:
    OPENROUTER_CATEGORIZATION_AVAILABLE = False

# Import OpenRouter model collections (OpenRouter Integration Stage 3)
try:
    from openrouter_model_collections import OpenRouterModelCollections, create_default_model_collections
    OPENROUTER_COLLECTIONS_AVAILABLE = True
except ImportError:
    OPENROUTER_COLLECTIONS_AVAILABLE = False

# Error classification system
class CommandError:
    """Base class for all command execution errors."""
    def __init__(self, error_code, message, details=None, suggestions=None):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.suggestions = suggestions or []
        
class ValidationError(CommandError):
    """Error that occurs during command validation."""
    pass
    
class EnvironmentError(CommandError):
    """Error that occurs due to environment configuration issues."""
    pass
    
class ExecutionError(CommandError):
    """Error that occurs during command execution."""
    pass
    
class ResourceError(CommandError):
    """Error that occurs due to resource constraints."""
    pass

# Error code registry
ERROR_CODES = {
    # Validation errors (100-199)
    "VAL-001": "Missing required parameter",
    "VAL-002": "Invalid parameter value",
    "VAL-003": "Parameter combination conflict",
    "VAL-004": "Invalid configuration file",
    "VAL-005": "Invalid template ID",
    
    # Environment errors (200-299)
    "ENV-001": "Missing required API key",
    "ENV-002": "Missing Python dependency",
    "ENV-003": "Ollama not running or available",
    "ENV-004": "Required executable not found",
    "ENV-005": "Invalid environment configuration",
    
    # Execution errors (300-399)
    "EXEC-001": "Command execution failed",
    "EXEC-002": "API call failed",
    "EXEC-003": "Output creation failed",
    "EXEC-004": "State management failed",
    "EXEC-005": "Syntax error in command",
    
    # Resource errors (400-499)
    "RES-001": "API rate limit exceeded",
    "RES-002": "Insufficient memory",
    "RES-003": "Execution timed out",
    "RES-004": "Disk space insufficient",
    "RES-005": "Network connectivity issue",
}

# Parameter descriptions database
PARAMETER_DESCRIPTIONS = {
    "query": {
        "short": "The text query to send to models",
        "long": "This is the primary input text that will be sent to all selected models. It should clearly describe the problem or request for which you want to evaluate model responses.",
        "impact": "The quality and specificity of your query directly affects the relevance of model responses.",
        "examples": ["How to improve urban mobility?", "Design an eco-friendly packaging solution", "Explain quantum computing to a 10-year-old"],
        "related": ["domain"]
    },
    "domain": {
        "short": "Problem domain to focus models on",
        "long": "Specifies the knowledge domain that models should consider when responding. This helps direct model responses toward a specific field or context.",
        "impact": "Choosing the right domain improves response relevance by providing appropriate context. Models can leverage domain-specific knowledge to generate better responses.",
        "examples": ["Technology", "Education", "Healthcare"],
        "related": ["query"]
    },
    "models": {
        "short": "Number of different models to use",
        "long": "Determines how many different AI models will process your query. Using multiple models allows you to compare responses across different architectures and capabilities.",
        "impact": "More models provide greater diversity of responses but increase API costs and execution time. Each model adds a multiplier to your total combinations.",
        "examples": ["2", "3", "5"],
        "related": ["balanced_models", "use_ollama", "simulate"]
    },
    "instructions": {
        "short": "Number of different instruction prompts to use",
        "long": "Determines how many different instruction templates will be used to frame your query. Different instruction templates encourage different response styles and perspectives.",
        "impact": "More instruction templates lead to greater cognitive diversity in responses but increase the total number of combinations and execution time.",
        "examples": ["3", "5", "10"],
        "related": ["instruction_templates", "variations"]
    },
    "variations": {
        "short": "Number of query variations to generate",
        "long": "Creates multiple variations of your base query to test how slight wording changes affect model responses. Helps identify response sensitivity to query phrasing.",
        "impact": "More variations increase the robustness of your evaluation but multiply the total number of combinations, increasing costs and execution time.",
        "examples": ["2", "3", "5"],
        "related": ["instructions", "models"]
    },
    "max_combinations": {
        "short": "Maximum number of combinations to execute",
        "long": "Limits the total number of query-model-instruction combinations that will be executed. Helps control execution time and API costs.",
        "impact": "Lower values reduce cost and time but might not provide a representative sample of all possible combinations.",
        "examples": ["36", "50", "100"],
        "related": ["sampling_method", "quick", "full"]
    },
    "sampling_method": {
        "short": "Method for sampling combinations",
        "long": "Determines how combinations are selected when not running exhaustively. Options are 'exhaustive' (all combinations), 'stratified' (balanced representation), or 'random' (random selection).",
        "impact": "Stratified sampling provides good coverage with fewer combinations. Random sampling is faster but less systematic.",
        "examples": ["exhaustive", "stratified", "random"],
        "related": ["max_combinations", "quick", "full"]
    },
    "use_ollama": {
        "short": "Include Ollama local models",
        "long": "When enabled, includes locally-running Ollama models in the evaluation. Requires Ollama to be installed and running on your system.",
        "impact": "Allows comparison between cloud API models and open-source models running locally, but requires Ollama setup.",
        "examples": ["True", "False"],
        "related": ["models", "balanced_models"]
    },
    "balanced_models": {
        "short": "Balance models across providers",
        "long": "Ensures that model combinations are evenly distributed across different providers (OpenAI, Anthropic, etc.). Helps prevent bias toward any single provider.",
        "impact": "Provides more balanced results but may limit flexibility in model selection.",
        "examples": ["True", "False"],
        "related": ["models", "use_ollama"]
    },
    "output_format": {
        "short": "Format for result output",
        "long": "Determines the format of the output files generated by the ISEE framework. Markdown is human-readable, while JSON is better for programmatic processing.",
        "impact": "Choose markdown for readability or JSON for further automated processing.",
        "examples": ["markdown", "json", "text"],
        "related": ["output_file", "generate_reports"]
    },
    "output_file": {
        "short": "Path to save output results",
        "long": "Specifies where the output file will be saved. If not provided, a default path in the data/output directory will be used.",
        "impact": "Allows organizing outputs in specific locations for easier management.",
        "examples": ["results.md", "output/my_evaluation.json"],
        "related": ["output_format"]
    },
    "simulate": {
        "short": "Simulate responses without API calls",
        "long": "Runs the evaluation with simulated model responses instead of making actual API calls. Useful for testing workflow or when API keys are not available.",
        "impact": "Eliminates API costs but provides only placeholder responses for testing purposes.",
        "examples": ["True", "False"],
        "related": ["dry_run"]
    },
    "dry_run": {
        "short": "Show what would run without executing",
        "long": "Shows which combinations would be executed without actually running them. Useful for validating your configuration before committing to a full run.",
        "impact": "Allows validation of settings without spending time or API credits.",
        "examples": ["True", "False"],
        "related": ["simulate"]
    },
    "generate_reports": {
        "short": "Generate summary reports",
        "long": "Creates detailed summary reports of the evaluation results, including model comparisons, statistical analyses, and key findings.",
        "impact": "Provides valuable insights but adds processing time at the end of execution.",
        "examples": ["True", "False"],
        "related": ["analyze_results", "report_format", "export_csv"]
    },
    "analyze_results": {
        "short": "Analyze results with visualizations",
        "long": "Performs in-depth analysis of results and generates visualizations like charts and graphs. Requires generate_reports to be enabled.",
        "impact": "Helps identify patterns and insights but adds significant processing time.",
        "examples": ["True", "False"],
        "related": ["generate_reports", "no_visualizations"]
    },
    "save_state": {
        "short": "Save state to a file",
        "long": "Saves the current state of the evaluation to a file that can be loaded later. Useful for long-running evaluations that might need to be paused.",
        "impact": "Enables resuming interrupted runs but adds overhead for state management.",
        "examples": ["my_evaluation_state.json"],
        "related": ["load_state"]
    },
    "load_state": {
        "short": "Load state from a file",
        "long": "Loads a previously saved state to continue an evaluation. Useful for resuming interrupted runs or building upon previous results.",
        "impact": "Allows continuing previous runs without starting over.",
        "examples": ["my_evaluation_state.json"],
        "related": ["save_state"]
    },
    "synthesize_method": {
        "short": "Method for synthesizing results",
        "long": "Determines how model responses are combined and synthesized into final insights. 'cluster_based' groups similar responses, while 'cross_pollination' combines elements from different responses.",
        "impact": "Different methods produce different types of synthesized insights.",
        "examples": ["cluster_based", "cross_pollination"],
        "related": ["analyze_results", "generate_reports"]
    },
    "quick": {
        "short": "Run in quick mode with stratified sampling",
        "long": "Preset that runs with stratified sampling and 36 combinations for a quicker evaluation. Good balance between thoroughness and speed.",
        "impact": "Significantly reduces execution time while maintaining reasonable coverage.",
        "examples": ["True", "False"],
        "related": ["full", "sampling_method", "max_combinations"]
    },
    "full": {
        "short": "Run in full mode with exhaustive combinations",
        "long": "Preset that runs all possible combinations for the most thorough evaluation. May take significant time and API credits.",
        "impact": "Provides the most comprehensive results but maximizes execution time and costs.",
        "examples": ["True", "False"],
        "related": ["quick", "sampling_method", "max_combinations"]
    },
    "instruction_templates": {
        "short": "Specific instruction templates to use",
        "long": "Instead of randomly selecting templates, this allows specifying exactly which templates to use by their ID. Provides precise control over the instruction diversity.",
        "impact": "Allows targeted evaluation with specific instruction styles.",
        "examples": ["creative_thinking,critical_analysis,empathetic_response"],
        "related": ["instructions"]
    },
    "report_format": {
        "short": "Format for generated reports",
        "long": "Specifies the format for summary reports. Only applies when generate_reports is enabled.",
        "impact": "Choose markdown for human readability or JSON for programmatic analysis.",
        "examples": ["markdown", "json"],
        "related": ["generate_reports", "export_csv"]
    },
    "export_csv": {
        "short": "Export data as CSV for analysis",
        "long": "Exports evaluation data in CSV format for further analysis in spreadsheet software or data analysis tools. Only applies when generate_reports is enabled.",
        "impact": "Facilitates deeper custom analysis in external tools.",
        "examples": ["True", "False"],
        "related": ["generate_reports", "analyze_results"]
    },
    "no_visualizations": {
        "short": "Skip generating visualization charts",
        "long": "Disables the generation of visualization charts during analysis. Only applies when analyze_results is enabled.",
        "impact": "Speeds up analysis but loses visual insights from charts and graphs.",
        "examples": ["True", "False"],
        "related": ["analyze_results"]
    },
    "domain_config": {
        "short": "Domain-specific configuration file",
        "long": "Path to a configuration file containing domain-specific settings for the evaluation.",
        "impact": "Allows tailoring the evaluation to specific domains with specialized settings.",
        "examples": ["tech_writing_domains.json", "learning_design_domains.json"],
        "related": ["domain"]
    },
    "sampling_method": {
        "short": "Method for selecting combinations to run",
        "long": "Controls how combinations of models, instructions, and variations are selected for execution. Exhaustive runs all combinations, random selects a random subset, and stratified ensures representative sampling across parameters.",
        "impact": "Affects both result quality and the number of API calls made. Exhaustive is most thorough but most expensive, while random and stratified can significantly reduce costs.",
        "examples": ["exhaustive", "random", "stratified"],
        "related": ["max_combinations", "quick", "full"]
    },
    "output_format": {
        "short": "Format for result output files",
        "long": "Determines the file format used for storing results. Affects how results are structured, displayed, and can be processed by other tools.",
        "impact": "Markdown is human-readable, JSON is machine-readable, and text is simplest. Choose based on how you plan to use the results.",
        "examples": ["markdown", "json", "text"],
        "related": ["query", "output_dir"]
    },
    "advanced_options": {
        "short": "Additional configuration options",
        "long": "A set of less commonly used configuration options that provide fine-grained control over execution behavior, including domain-specific settings, API parameters, and specialized outputs.",
        "impact": "Can significantly alter command behavior for specific use cases. Only needed for specialized requirements.",
        "examples": ["domain-specific configuration", "custom API parameters", "specialized outputs"],
        "related": ["sampling_method", "output_format"]
    }
}

# Error detection and analysis
def detect_error_type(error, command, env_state=None):
    """
    Analyze an error and classify it by type.
    
    Args:
        error: The original exception
        command: The command string that was executed
        env_state: Optional environment state information
        
    Returns:
        CommandError instance with appropriate classification
    """
    error_str = str(error)
    
    # Check for API key issues
    if any(key in error_str.lower() for key in ["api key", "apikey", "authentication", "unauthorized"]):
        provider = None
        env_var = "required API key"
        
        if "anthropic" in error_str.lower():
            provider = "Anthropic"
            env_var = "ANTHROPIC_API_KEY"
        elif "openai" in error_str.lower():
            provider = "OpenAI"
            env_var = "OPENAI_API_KEY"
        elif "google" in error_str.lower():
            provider = "Google"
            env_var = "GOOGLE_API_KEY"
        elif "openrouter" in error_str.lower():
            provider = "OpenRouter"
            env_var = "OPENROUTER_API_KEY"
        
        return EnvironmentError(
            "ENV-001",
            f"Missing or invalid API key{f' for {provider}' if provider else ''}",
            {"command": command, "provider": provider, "error": error_str},
            [
                f"Check that you have set the {env_var} environment variable",
                "Consider using simulation mode with --simulate for testing without API access",
                "Check that your API key is valid and has not expired"
            ]
        )
    
    # Check for Ollama issues
    if "ollama" in error_str.lower() and any(term in error_str.lower() for term in ["not running", "connection refused", "cannot connect", "not found"]):
        return EnvironmentError(
            "ENV-003",
            "Ollama is not running or accessible",
            {"command": command, "error": error_str},
            [
                "Ensure Ollama is installed and running (https://ollama.com)",
                "Run 'ollama serve' in a separate terminal",
                "Consider using cloud API models instead with --use-ollama=false",
                "Or use simulation mode with --simulate for testing"
            ]
        )
    
    # Check for missing executable
    if "No such file or directory" in error_str and "python" in command:
        return EnvironmentError(
            "ENV-004",
            "Required Python executable not found",
            {"command": command, "error": error_str},
            [
                "Ensure Python is correctly installed and in your PATH",
                "Try running with the full path to Python",
                "Make sure you're in the correct directory containing main.py"
            ]
        )
    
    # Check for parameter issues
    if "argument" in error_str.lower() and any(term in error_str.lower() for term in ["required", "missing", "expected", "invalid"]):
        param_match = re.search(r"(--[a-zA-Z0-9_-]+)", error_str)
        param_name = param_match.group(1) if param_match else "unknown parameter"
        
        return ValidationError(
            "VAL-001",
            f"Missing or invalid parameter: {param_name}",
            {"command": command, "param_name": param_name, "error": error_str},
            [
                f"Provide a valid value for {param_name}",
                "Check the parameter name and format",
                "Try running with --help to see all available parameters"
            ]
        )
    
    # Check for file not found
    if any(term in error_str.lower() for term in ["no such file", "file not found", "cannot find", "not exist"]):
        file_match = re.search(r"['\"]([^'\"]+\.[a-zA-Z0-9]+)['\"]", error_str)
        file_path = file_match.group(1) if file_match else "unknown file"
        
        return ExecutionError(
            "EXEC-003",
            f"File not found: {file_path}",
            {"command": command, "file_path": file_path, "error": error_str},
            [
                "Check that the file path is correct",
                "Ensure the file exists and you have permission to access it",
                "Use absolute paths to avoid directory confusion"
            ]
        )
    
    # Check for resource issues
    if any(term in error_str.lower() for term in ["timeout", "rate limit", "too many requests", "capacity"]):
        return ResourceError(
            "RES-001",
            "API rate limit or timeout occurred",
            {"command": command, "error": error_str},
            [
                "Try again after a brief pause",
                "Reduce the number of combinations or use --max-combinations",
                "Consider using --simulate for testing without API calls"
            ]
        )
    
    # Default to generic execution error
    return ExecutionError(
        "EXEC-001",
        "Command execution failed",
        {"command": command, "error": error_str},
        [
            "Check the command parameters and try again",
            "Verify that required dependencies are installed",
            "Consider using --simulate for testing",
            "Check main.py for any recent changes that might affect your command"
        ]
    )

# Recovery Strategy classes
class RecoveryStrategy:
    """Base class for all recovery strategies."""
    def __init__(self, error):
        self.error = error
        
    def get_user_friendly_message(self):
        """Get a user-friendly error message."""
        return self.error.message
        
    def get_suggestions(self):
        """Get suggestions for resolving the error."""
        return self.error.suggestions
        
    def can_auto_recover(self):
        """Check if automatic recovery is possible."""
        return False
        
    def attempt_recovery(self, command_wizard):
        """Attempt to recover from the error."""
        raise NotImplementedError("Subclasses must implement this method")
        
    def get_next_steps(self):
        """Get next steps for the user."""
        return ["Try again with different parameters", 
                "Check the documentation for more information"]

class ValidationRecoveryStrategy(RecoveryStrategy):
    """Recovery strategy for validation errors."""
    
    def can_auto_recover(self):
        # Some validation errors can be auto-recovered
        return self.error.error_code in ["VAL-002", "VAL-003"]
        
    def attempt_recovery(self, command_wizard):
        if self.error.error_code == "VAL-001":  # Missing required parameter
            # Guide the user to provide the missing parameter
            return self._recover_missing_parameter(command_wizard)
        elif self.error.error_code == "VAL-002":  # Invalid parameter value
            # Suggest valid parameter values
            return self._recover_invalid_parameter(command_wizard)
        else:
            return False
            
    def _recover_missing_parameter(self, command_wizard):
        # Implementation to guide user to input the missing parameter
        param_name = self.error.details.get("param_name")
        if not param_name:
            return False
            
        # Clean up parameter name (remove -- prefix)
        param_name = param_name.replace("--", "").replace("-", "_")
            
        command_wizard.console.print(f"[yellow]The parameter '{param_name}' is required.[/yellow]")
        value = Prompt.ask(f"Please provide a value for {param_name}")
        if value:
            command_wizard.params[param_name] = value
            return True
                
        return False
        
    def _recover_invalid_parameter(self, command_wizard):
        # For now just guide to parameter reconfiguration
        return False

class EnvironmentRecoveryStrategy(RecoveryStrategy):
    """Recovery strategy for environment errors."""
    
    def can_auto_recover(self):
        # Environment errors related to Ollama and API keys can often be auto-recovered
        return self.error.error_code in ["ENV-001", "ENV-003"]
    
    def attempt_recovery(self, command_wizard):
        if self.error.error_code == "ENV-001":  # Missing API key
            return self._recover_missing_api_key(command_wizard)
        elif self.error.error_code == "ENV-003":  # Ollama not running
            return self._recover_ollama_not_running(command_wizard)
        else:
            return False
            
    def _recover_missing_api_key(self, command_wizard):
        provider = self.error.details.get("provider")
            
        message = "An API key is missing or invalid"
        if provider:
            message = f"The API key for {provider} is missing or invalid"
        
        command_wizard.console.print(f"[yellow]{message}.[/yellow]")
        
        # Offer OpenRouter setup if no API keys are working and OpenRouter is available
        if (not command_wizard.api_status.get("any_api", False) and 
            hasattr(command_wizard, 'openrouter_categorizer') and 
            command_wizard.openrouter_categorizer and
            not command_wizard.api_status.get("openrouter", False)):
            
            command_wizard.console.print("\n[cyan]💡 Consider setting up OpenRouter for access to 300+ models![/cyan]")
            setup_openrouter = Confirm.ask("Would you like to set up OpenRouter now?", default=True)
            if setup_openrouter:
                if command_wizard._setup_openrouter_api_key():
                    command_wizard.console.print("[green]✓ OpenRouter setup complete! You can now proceed.[/green]")
                    return True
        
        # Fallback to simulation mode
        use_simulation = Confirm.ask("Would you like to switch to simulation mode instead?", default=True)
        if use_simulation:
            command_wizard.params["simulate"] = True
            return True
                
        return False
        
    def _recover_ollama_not_running(self, command_wizard):
        command_wizard.console.print("[yellow]Ollama is not running or not accessible.[/yellow]")
        options = [
            "Disable Ollama and continue with cloud models only",
            "Switch to simulation mode",
            "Try again after starting Ollama"
        ]
        
        for i, option in enumerate(options, 1):
            command_wizard.console.print(f"{i}. {option}")
            
        choice = IntPrompt.ask(
            "What would you like to do?",
            choices=list(range(1, len(options)+1))
        )
        
        if choice == 1:
            command_wizard.params["use_ollama"] = False
            return True
        elif choice == 2:
            command_wizard.params["simulate"] = True
            return True
                
        return False

class ExecutionRecoveryStrategy(RecoveryStrategy):
    """Recovery strategy for execution errors."""
    
    def can_auto_recover(self):
        # Some execution errors can be auto-recovered
        return self.error.error_code in ["EXEC-001", "EXEC-003"] 
    
    def attempt_recovery(self, command_wizard):
        # Most execution errors require parameter changes
        # Guide user to reconfiguration
        return False

class ResourceRecoveryStrategy(RecoveryStrategy):
    """Recovery strategy for resource errors."""
    
    def can_auto_recover(self):
        # Resource limit errors can often be auto-recovered
        return self.error.error_code in ["RES-001", "RES-003"]
    
    def attempt_recovery(self, command_wizard):
        if self.error.error_code == "RES-001":  # API rate limit
            return self._recover_rate_limit(command_wizard)
        elif self.error.error_code == "RES-003":  # Timeout
            return self._recover_timeout(command_wizard)
        else:
            return False
            
    def _recover_rate_limit(self, command_wizard):
        command_wizard.console.print("[yellow]API rate limit exceeded.[/yellow]")
        options = [
            "Reduce the number of combinations",
            "Switch to simulation mode",
            "Wait and try again"
        ]
            
        for i, option in enumerate(options, 1):
            command_wizard.console.print(f"{i}. {option}")
                
        choice = IntPrompt.ask(
            "What would you like to do?",
            choices=list(range(1, len(options)+1))
        )
            
        if choice == 1:
            # Guide to reduce combinations
            current = command_wizard.params.get("max_combinations")
            if not current:
                # Calculate current potential combinations
                models = command_wizard.params.get("models", 2)
                instructions = command_wizard.params.get("instructions", 3)
                variations = command_wizard.params.get("variations", 2)
                total = models * instructions * variations
                suggested = max(10, total // 2)
                command_wizard.console.print(f"Current potential combinations: {total}")
                command_wizard.console.print(f"Suggested max: {suggested}")
                    
                new_max = IntPrompt.ask(
                    "Set maximum combinations",
                    default=suggested
                )
                command_wizard.params["max_combinations"] = new_max
                return True
            else:
                new_max = IntPrompt.ask(
                    "Set maximum combinations",
                    default=max(10, current // 2)
                )
                command_wizard.params["max_combinations"] = new_max
                return True
        elif choice == 2:
            command_wizard.params["simulate"] = True
            return True
        elif choice == 3:
            command_wizard.console.print("Waiting to retry...")
            time.sleep(5)  # Simple wait and retry
            return True
        return False
    
    def _recover_timeout(self, command_wizard):
        # Similar to rate limit recovery but with focus on timeout issues
        command_wizard.console.print("[yellow]Operation timed out.[/yellow]")
        command_wizard.console.print("This could be due to slow API responses or large combination count.")
            
        # Offer similar options as rate limit recovery
        options = [
            "Reduce the number of combinations",
            "Switch to simulation mode",
            "Try again"
        ]
            
        for i, option in enumerate(options, 1):
            command_wizard.console.print(f"{i}. {option}")
                
        choice = IntPrompt.ask(
            "What would you like to do?",
            choices=list(range(1, len(options)+1))
        )
            
        if choice == 1:
            # Similar implementation as rate limit recovery
            # ...
            return self._recover_rate_limit(command_wizard)  # Reuse implementation
        elif choice == 2:
            command_wizard.params["simulate"] = True
            return True
        elif choice == 3:
            # Just try again
            return True
        return False

def create_recovery_strategy(error):
    """
    Create a recovery strategy based on the error type.
    
    Args:
        error: CommandError instance
        
    Returns:
        RecoveryStrategy instance
    """
    if isinstance(error, ValidationError):
        return ValidationRecoveryStrategy(error)
    elif isinstance(error, EnvironmentError):
        return EnvironmentRecoveryStrategy(error)
    elif isinstance(error, ExecutionError):
        return ExecutionRecoveryStrategy(error)
    elif isinstance(error, ResourceError):
        return ResourceRecoveryStrategy(error)
    else:
        return RecoveryStrategy(error)  # Generic strategy


class CommandWizard:
    """Interactive wizard for constructing ISEE commands."""
    
    def __init__(self):
        """Initialize the command wizard."""
        # Store selected models
        self.selected_models = []
        self.selected_model_names = []
        
        # Initialize console for rich output
        self.console = Console()
        
        # Initialize command parameters
        self.params = {
            "query": None,
            "domain": None,
            "models": 2,
            "instructions": 3,
            "variations": 2,
            "max_combinations": None,
            "sampling_method": "exhaustive",
            "use_ollama": False,
            "balanced_models": False,
            "output_format": "markdown",
            "output_file": None,
            "simulate": False,
            "dry_run": False,
            "generate_reports": False,
            "analyze_results": False,
            "save_state": None,
            "load_state": None,
            "synthesize_method": "cluster_based",
            "instruction_templates": None,  # Add parameter for instruction template IDs
        }
        
        # Initialize cost estimator (UX Enhancement - Step 1.1)
        self.cost_estimator = CostEstimator() if COST_ESTIMATION_AVAILABLE else None
        self.current_cost_estimate = None
        
        # Initialize parameter context (UX Enhancement - Step 1.2)
        self.param_context = ParameterContext() if PARAMETER_CONTEXT_AVAILABLE else None
        
        # Initialize preview tracking (UX Enhancement - Step 1.3)
        self.previous_params = None
        self.preview_detailed_mode = True
        
        # Detect available API keys and models
        self.api_status = self._detect_apis()
        
        # Initialize domain manager and load domains
        self.domain_manager = DomainManager()
        for domain in create_default_domains():
            self.domain_manager.add_domain(domain)
            
        # Try to load domain-specific configurations
        self._load_domain_configs()
        
        # Initialize template library
        self.template_library = create_default_library()
        
        # Initialize purpose manager (UX Enhancement - Step 2.1)
        self.purpose_manager = create_default_purpose_manager() if PURPOSE_SELECTION_AVAILABLE else None
        self.selected_purpose = None
        
        # Initialize preset manager (UX Enhancement - Step 2.2)
        self.preset_manager = create_default_preset_manager() if PRESET_MANAGER_AVAILABLE else None
        self.selected_preset = None
        
        # Initialize OpenRouter categorizer (OpenRouter Integration Stage 2)
        self.openrouter_categorizer = OpenRouterCategorizer() if OPENROUTER_CATEGORIZATION_AVAILABLE else None
        
        # Initialize OpenRouter model collections (OpenRouter Integration Stage 3)
        self.openrouter_collections = create_default_model_collections() if OPENROUTER_COLLECTIONS_AVAILABLE else None
        
        # Initialize progressive disclosure settings (UX Enhancement - Step 2.3)
        self.complexity_level = "basic"  # Options: "basic", "advanced", "expert"
        self.show_advanced_options = False
        self.configuration_path = "quick"  # Options: "quick", "detailed"
        
        # Initialize cognitive framework visualizer (UX Enhancement - Step 3.1)
        self.framework_visualizer = create_framework_visualizer(self.console) if FRAMEWORK_VISUALIZER_AVAILABLE else None
    
    def _show_parameter_examples(self, param_name: str) -> None:
        """
        Show detailed examples for a specific parameter.
        
        Args:
            param_name: The name of the parameter to show examples for.
        """
        # Add a separator line before examples content
        self.console.print("\n[dim]─" + "─" * 50 + "[/dim]\n")
        # Clean up parameter name (replace dashes with underscores)
        clean_param = param_name.replace("-", "_")
        
        # Use enhanced parameter context if available
        if PARAMETER_CONTEXT_AVAILABLE and self.param_context:
            context = self.param_context.get_parameter_context(clean_param)
            detailed_examples = context.get("detailed_examples", [])
            
            if not detailed_examples:
                self.console.print(f"[yellow]No detailed examples available for parameter: {param_name}[/yellow]")
                
                # Add a separator line after content
                self.console.print("\n[dim]─" + "─" * 50 + "[/dim]\n")
                return
            
            # Create a nicely formatted examples panel
            content = [
                f"[bold yellow]{context['short']}[/bold yellow]",
                ""
            ]
                
            # Add all detailed examples
            for i, example in enumerate(detailed_examples):
                content.append(f"[bold]Example {i+1}:[/bold] [cyan]{example['value']}[/cyan]")
                content.append(f"{example['explanation']}")
                if i < len(detailed_examples) - 1:
                    content.append("")  # Add spacing between examples
                
            # Show combination impact if applicable
            if clean_param in ["models", "instructions", "variations"]:
                # Create a temporary params copy to show combination impact
                temp_params = self.params.copy()
                # Try to parse the example value
                try:
                    example_val = detailed_examples[0]["value"]
                    # Convert to int if possible
                    temp_params[clean_param] = int(example_val) if example_val.isdigit() else example_val
                    impact = self.param_context.get_combination_impact(temp_params)
                    content.append("")
                    content.append(f"[bold]Impact on combinations:[/bold] {impact}")
                except (ValueError, KeyError):
                    pass  # Skip if we can't calculate impact
                
            # Display the examples panel
            examples_panel = Panel(
                "\n".join(content),
                title=f"Examples: --{param_name}",
                border_style="cyan",
                expand=False
            )
            self.console.print(examples_panel)
                
            # Add a separator line after examples content
            self.console.print("\n[dim]─" + "─" * 50 + "[/dim]\n")
        else:
            # Fall back when parameter context is not available
            self.console.print(f"[yellow]No detailed examples available for parameter: {param_name}[/yellow]")
    def _show_parameter_help(self, param_name: str) -> None:
        """
        Show detailed help for a specific parameter.
        
        Args:
            param_name: The name of the parameter to show help for.
        """
        # Add a separator line before help content
        self.console.print("\n[dim]─" + "─" * 50 + "[/dim]\n")
        # Clean up parameter name (replace dashes with underscores)
        clean_param = param_name.replace("-", "_")
        
        # Use enhanced parameter context if available
        if PARAMETER_CONTEXT_AVAILABLE and self.param_context:
            context = self.param_context.get_parameter_context(clean_param)
            if not context:
                self.console.print(f"[yellow]No detailed help available for parameter: {param_name}[/yellow]")
                # Add a separator line after help content
                self.console.print("\n[dim]─" + "─" * 50 + "[/dim]\n")
                return
                
            # Get cross-parameter impacts
            cross_impacts = self.param_context.get_cross_parameter_impacts(clean_param)
            
            # Get related parameters
            related_params = self.param_context.get_related_parameters(clean_param)
            
            # Get detailed examples
            detailed_examples = context.get("detailed_examples", [])
            
            # Create a nicely formatted help panel
            content = [
                f"[bold yellow]{context['short']}[/bold yellow]",
                "",
                f"{context['long']}",
                "",
                f"[bold]Impact:[/bold] {context['impact']}"
            ]
                
            # Add examples if available
            if "examples" in context and context["examples"]:
                content.append("")
                content.append("[bold]Examples:[/bold]")
                for example in context["examples"]:
                    content.append(f"  • {example}")
                
            # Add detailed examples if available
            if detailed_examples:
                content.append("")
                content.append("[bold]Detailed Example:[/bold]")
                for i, example in enumerate(detailed_examples[:1]):  # Show only the first detailed example
                    content.append(f"  Value: [cyan]{example['value']}[/cyan]")
                    content.append(f"  {example['explanation']}")
                content.append("  [dim](Type 'example' to see more detailed examples)[/dim]")
                
            # Add cross-parameter impacts if available
            if cross_impacts:
                content.append("")
                content.append("[bold]Parameter Relationships:[/bold]")
                for impact in cross_impacts:
                    related_param = impact.get("parameter", "").replace("_", "-")
                    impact_desc = impact.get("impact", "")
                    content.append(f"  • [cyan]--{related_param}[/cyan]: {impact_desc}")
                
            # Add related parameters
            if related_params:
                content.append("")
                content.append("[bold]Related parameters:[/bold]")
                for related in related_params:
                    related_context = self.param_context.get_parameter_context(related)
                    if related_context:
                        related_display = related.replace("_", "-")
                        content.append(f"  • [cyan]--{related_display}[/cyan]: {related_context['short']}")
                
            # Display the help panel
            help_panel = Panel(
                "\n".join(content),
                title=f"Help: --{param_name}",
                border_style="cyan",
                expand=False
            )
            self.console.print(help_panel)
        else:
            # Fall back to old PARAMETER_DESCRIPTIONS behavior
            if clean_param not in PARAMETER_DESCRIPTIONS:
                self.console.print(f"[yellow]No detailed help available for parameter: {param_name}[/yellow]")
                return
    
            desc = PARAMETER_DESCRIPTIONS[clean_param]
            
            # Create a nicely formatted help panel
            content = [
                f"[bold yellow]{desc['short']}[/bold yellow]",
                "",
                f"{desc['long']}",
                "",
                f"[bold]Impact:[/bold] {desc['impact']}"
            ]
                
            # Add examples if available
            if "examples" in desc and desc["examples"]:
                content.append("")
                content.append("[bold]Examples:[/bold]")
                for example in desc["examples"]:
                    content.append(f"  • {example}")
                
            # Add related parameters
            if "related" in desc and desc["related"]:
                content.append("")
                content.append("[bold]Related parameters:[/bold]")
                for related in desc["related"]:
                    if related in PARAMETER_DESCRIPTIONS:
                        related_display = related.replace("_", "-")
                        content.append(f"  • [cyan]--{related_display}[/cyan]: {PARAMETER_DESCRIPTIONS[related]['short']}")
                
            # Display the help panel
            help_panel = Panel(
                "\n".join(content),
                title=f"Help: --{param_name}",
                border_style="cyan",
                expand=False
            )
            self.console.print(help_panel)
    def _show_parameter_context(self, param_name: str, current_value: Any = None) -> None:
        """
        Show contextual information about a parameter when requesting input.
        
        Args:
            param_name: The name of the parameter
            current_value: The current value of the parameter, if any
        """
        # Use enhanced parameter context if available
        if PARAMETER_CONTEXT_AVAILABLE and self.param_context:
            context = self.param_context.get_parameter_context(param_name)
            if not context:
                return
                
            # Check for parameter warnings based on current value
            warning = None
            if current_value is not None:
                warning = self.param_context.get_parameter_warning(param_name, current_value)
                
            # Check for cross-parameter impacts
            cross_impacts = self.param_context.get_cross_parameter_impacts(param_name)
            
            # Show brief description with option to get more help
            self.console.print(f"[yellow]{context['short']}[/yellow]")
                
            # Show current value if there is one
            if current_value is not None:
                self.console.print(f"Current value: [green]{current_value}[/green]")
                    
            # Show brief impact statement
            self.console.print(f"Impact: {context['impact']}")
                
            # Show warning if applicable
            if warning:
                self.console.print(f"[bold red]Warning:[/bold red] {warning}")
                
            # Show a hint about cross-parameter impacts if they exist
            if cross_impacts:
                most_important = cross_impacts[0]  # Just show the most important one in the context view
                related_param = most_important.get("parameter", "").replace("_", "-")
                impact = most_important.get("impact", "")
                self.console.print(f"[bold]Affects --{related_param}:[/bold] {impact}")
                if len(cross_impacts) > 1:
                    self.console.print(f"[dim](Plus {len(cross_impacts)-1} more relationships)[/dim]")
                
            # Show command hints
            self.console.print("[dim](Type 'help' for more information, 'example' for usage examples)[/dim]")
        else:
            # Fall back to old PARAMETER_DESCRIPTIONS behavior
            if param_name not in PARAMETER_DESCRIPTIONS:
                return
                
            desc = PARAMETER_DESCRIPTIONS[param_name]
            
            # Show brief description with option to get more help
            self.console.print(f"[yellow]{desc['short']}[/yellow]")
                
            # Show current value if there is one
            if current_value is not None:
                self.console.print(f"Current value: [green]{current_value}[/green]")
                    
            # Show brief impact statement
            self.console.print(f"Impact: {desc['impact']}")
                
            # Show a hint about getting more help and examples
            self.console.print("[dim](Type 'help' for more detailed information, 'example' for usage examples)[/dim]")
    def _handle_special_input(self, input_value: str, param_name: str) -> bool:
        """
        Handle special input commands like 'help' and 'example'.
        
        Args:
            input_value: The user input string
            param_name: The parameter name being processed
            
        Returns:
            True if a special command was handled, False otherwise
        """
        input_lower = input_value.lower()
        
        if input_lower == "help":
            self._show_parameter_help(param_name)
            return True
        elif input_lower == "help all":
            self._show_all_parameters_help()
            return True
        elif input_lower == "example" and PARAMETER_CONTEXT_AVAILABLE and self.param_context:
            self._show_parameter_examples(param_name)
            return True
        elif input_lower == "preview":
            # Show preview with current detailed mode
            self.preview_command()
            return True
        elif input_lower == "preview detailed":
            # Show detailed preview and update mode
            self.preview_detailed_mode = True
            self.preview_command(show_detailed=True)
            return True
        elif input_lower == "preview summary":
            # Show summary preview and update mode
            self.preview_detailed_mode = False
            self.preview_command(show_detailed=False)
            return True
        
        return False
        
    def _get_parameter_input(self, param_name: str, prompt_text: str, default_value: str = "") -> str:
        """
        Get user input for a parameter with support for special commands like 'help' and 'example'.
        
        Args:
            param_name: The parameter name being processed
            prompt_text: The text to display when prompting for input
            default_value: The default value to use (for rich UI)
            
        Returns:
            The user input value after handling any special commands
        """
        # Display parameter context first (but only once)
        show_context = True
        
        # Loop until we get a non-special command input
        while True:
            # Only show context on first iteration
            if show_context:
                self._show_parameter_context(param_name, self.params.get(param_name))
                show_context = False
            
            user_input = Prompt.ask(prompt_text, default=default_value)
            
            # Handle special commands
            if self._handle_special_input(user_input, param_name):
                continue
            
            # If we get here, it's a valid input
            return user_input
            
    def _get_boolean_input(self, param_name: str, prompt_text: str, default_value: str = "y") -> bool:
        """
        Get user input for a boolean parameter with support for special commands.
        Handles yes/no conversion to True/False.
        
        Args:
            param_name: The parameter name being processed
            prompt_text: The text to display when prompting for input
            default_value: The default value to use, either "y" or "n"
            
        Returns:
            The boolean value corresponding to the user's input
        """
        # Get string input first using our reusable function
        input_text = self._get_parameter_input(param_name, f"{prompt_text} (y/n)", default_value)
        
        # Convert to boolean - treat "y", "yes", and empty string (with default="y") as True
        return input_text.lower() in ["y", "yes", ""]
        
    def _get_selection_input(self, param_name: str, prompt_text: str, options: list, 
                            descriptions: list = None, default_value: str = "1") -> int:
        """
        Get user input for a selection from a numbered list with support for special commands.
        
        Args:
            param_name: The parameter name being processed
            prompt_text: The text to display when prompting for input
            options: List of options (internal values)
            descriptions: Optional list of descriptions for each option
            default_value: The default selection index (1-based for user display)
            
        Returns:
            The selected index (0-based for internal use)
        """
        # Display options with descriptions if provided
        for i, option in enumerate(options, 1):
            if descriptions and i-1 < len(descriptions):
                self.console.print(f"{i}. {option} - {descriptions[i-1]}")
            else:
                self.console.print(f"{i}. {option}")
        # Get string input using our reusable function
        selection_input = self._get_parameter_input(param_name, prompt_text, default_value)
        
        # Convert to integer and validate
        try:
            selection = int(selection_input) if selection_input.strip() else int(default_value)
            if selection < 1 or selection > len(options):
                self.console.print(f"[red]Invalid selection. Using default ({default_value}).[/red]")
                selection = int(default_value)
        except ValueError:
            self.console.print(f"[red]Invalid input. Using default ({default_value}).[/red]")
            selection = int(default_value)
        
        # Return 0-based index for internal use
        return selection - 1
    
    def _show_all_parameters_help(self) -> None:
        """Show a summary of all available parameters and their descriptions."""
        # Use enhanced parameter context if available
        if PARAMETER_CONTEXT_AVAILABLE and self.param_context:
            self.console.print("\n[bold cyan]All Available Parameters[/bold cyan]")
                
            # Create a table for parameters
            params_table = Table(title="Command Parameters")
            params_table.add_column("Parameter", style="cyan")
            params_table.add_column("Description", style="yellow")
            params_table.add_column("Current Value", style="green")
                
            # Add parameters to table, grouped by category
            if PARAMETER_CONTEXT_AVAILABLE and self.param_context:
                # Use the categories from the parameter context
                categories = {}
                for cat in self.param_context.get_all_categories():
                    categories[cat["name"]] = cat["parameters"]
            else:
                # Fall back to hardcoded categories
                categories = {
                    "Basic": ["query", "domain", "models", "instructions", "variations"],
                    "Sampling": ["sampling_method", "max_combinations", "quick", "full"],
                    "Models": ["balanced_models", "use_ollama", "simulate"],
                    "Output": ["output_format", "output_file", "generate_reports", "analyze_results", "report_format", "export_csv", "no_visualizations"],
                    "Advanced": ["save_state", "load_state", "synthesize_method", "instruction_templates", "domain_config", "dry_run"]
                }
                
            for category, params in categories.items():
                # Add category header
                params_table.add_row(f"[bold]{category}[/bold]", "", "")
                    
                # Add parameters in this category
                for param in params:
                    if PARAMETER_CONTEXT_AVAILABLE and self.param_context:
                        context = self.param_context.get_parameter_context(param)
                        if context:
                            # Parameter description
                            short_desc = context["short"]
                                
                            # Format parameter name with dashes instead of underscores
                            display_name = param.replace("_", "-")
                                
                            # Add to table
                            params_table.add_row(f"--{display_name}", "", short_desc)
                            continue
                    if param in PARAMETER_DESCRIPTIONS:
                        # Parameter description
                        short_desc = PARAMETER_DESCRIPTIONS[param]["short"]
                            
                        # Format parameter name with dashes instead of underscores
                        param_display = f"--{param.replace('_', '-')}"
                            
                        # Get current value if set
                        current_value = self.params.get(param)
                        value_display = str(current_value) if current_value is not None else ""
                            
                        # Add to table
                        params_table.add_row(param_display, short_desc, value_display)
                
            self.console.print(params_table)
            
            # Special highlight for OpenRouter options if available
            if self.api_status["openrouter"] and self.openrouter_categorizer:
                self.console.print("\n[bold green]🌟 OpenRouter Enhanced Options Available![/bold green]")
                self.console.print("[cyan]--openrouter-filters: Configure intelligent model categorization (300+ models!)[/cyan]")
            elif self.openrouter_categorizer:
                self.console.print("\n[bold yellow]💡 OpenRouter Integration Available![/bold yellow]")
                self.console.print("[cyan]Set up OpenRouter to unlock 300+ models with intelligent categorization![/cyan]")
            
            self.console.print("\n[dim]For detailed help on a specific parameter, type its name with 'help' during input prompts.[/dim]")
        else:
            # Plain text version
            print("\nAll Available Parameters")
            print("=" * 50)
            
            # Show parameters grouped by category
            categories = {
                "Basic": ["query", "domain", "models", "instructions", "variations"],
                "Sampling": ["sampling_method", "max_combinations", "quick", "full"],
                "Models": ["balanced_models", "use_ollama", "simulate"],
                "Output": ["output_format", "output_file", "generate_reports", "analyze_results", "report_format", "export_csv", "no_visualizations"],
                "Advanced": ["save_state", "load_state", "synthesize_method", "instruction_templates", "domain_config", "dry_run"]
            }
            
            for category, params in categories.items():
                print(f"\n{category}:")
                print("-" * len(category))
                
                for param in params:
                    if param in PARAMETER_DESCRIPTIONS:
                        # Parameter description
                        short_desc = PARAMETER_DESCRIPTIONS[param]["short"]
                        
                        # Format parameter name with dashes instead of underscores
                        param_display = f"--{param.replace('_', '-')}"
                        
                        # Get current value if set
                        current_value = self.params.get(param)
                        value_display = f" (current: {current_value})" if current_value is not None else ""
                        
                        # Print parameter info
                        print(f"{param_display}: {short_desc}{value_display}")
            
            print("\nFor detailed help on a specific parameter, type its name with 'help' during input prompts.")
    
    def _update_cost_estimate(self) -> Dict[str, Any]:
        """Update the cost and execution time estimate based on current parameters.
        
        Returns:
            Dictionary with cost and time estimates.
        """
        if not COST_ESTIMATION_AVAILABLE or not self.cost_estimator:
            return {}
        
        # Get the current cost estimate
        self.current_cost_estimate = self.cost_estimator.estimate_cost(self.params)
        return self.current_cost_estimate
        
    def _update_param_and_estimate(self, param_name: str, value: Any) -> None:
        """Update a parameter and recalculate the cost estimate.
        
        Args:
            param_name: The name of the parameter to update.
            value: The new value for the parameter.
        """
        # Save current params for change tracking before updating (UX Enhancement - Step 1.3)
        if self.previous_params is None:
            self._save_current_params()
            
        # Update the parameter
        self.params[param_name] = value
        
        # Update cost estimate if available (UX Enhancement - Step 1.1)
        if COST_ESTIMATION_AVAILABLE and self.cost_estimator:
            self._update_cost_estimate()
    
    def _display_cost_estimate(self) -> None:
        """Display the current cost and execution time estimate."""
        if not COST_ESTIMATION_AVAILABLE or not self.cost_estimator or not self.current_cost_estimate:
            return
        
        estimate = self.current_cost_estimate
        
        # Get warning message if any
        warning_message = self.cost_estimator.get_warning_message(estimate)
        
        # Create a table for the estimate
        from rich.table import Table
        from rich.panel import Panel
            
        # Display a summary panel
        cost_indicator = self.cost_estimator.get_cost_indicator(estimate)
        time_indicator = self.cost_estimator.get_time_indicator(estimate)
        combinations = estimate.get("combinations_estimate", 0)
            
        cost_summary = f"Estimated Cost: {cost_indicator}"
        time_summary = f"Estimated Time: {time_indicator}"
        combo_summary = f"Combinations: {combinations}"
            
        summary_panel = Panel(
            f"{cost_summary}\n{time_summary}\n{combo_summary}",
            title="Resource Estimate",
            border_style="cyan"
        )
            
        self.console.print(summary_panel)
            
        # Show warning if needed
        if warning_message:
            # Split warning into lines for better formatting
            warning_lines = warning_message.split("\n")
            warning_title = warning_lines[0].strip() if warning_lines else "Warning"
            warning_content = "\n".join(warning_lines[1:]) if len(warning_lines) > 1 else ""
                
            # Color based on severity
            border_style = "yellow"
            if "HIGH COST" in warning_title or "VERY HIGH COST" in warning_title:
                border_style = "red"
                
            warning_panel = Panel(
                f"{warning_title}\n{warning_content}" if warning_content else warning_title,
                border_style=border_style
            )
                
            self.console.print(warning_panel)
    def _detect_apis(self) -> Dict[str, bool]:
        """Detect available API keys and models.
        
        Returns:
            Dictionary of API availability status.
        """
        status = {
            "anthropic": False,
            "openai": False,
            "google": False,
            "openrouter": False,
            "ollama": False,
            "any_api": False,
        }
        
        # Check for API keys
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")
        google_key = os.environ.get("GOOGLE_API_KEY")
        openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        
        if anthropic_key:
            status["anthropic"] = True
            status["any_api"] = True
        
        if openai_key:
            status["openai"] = True
            status["any_api"] = True
            
        if google_key:
            status["google"] = True
            status["any_api"] = True
            
        if openrouter_key:
            status["openrouter"] = True
            status["any_api"] = True
        
        # Check for Ollama
        try:
            ollama_client = ModelAPIFactory.create_client("ollama")
            ollama_models = ollama_client.get_available_models()
            if ollama_models:
                status["ollama"] = True
                status["ollama_models"] = ollama_models
        except Exception:
            # Silently fail if Ollama check fails
            pass
        
        return status
    
    def _load_domain_configs(self):
        """Try to load domain-specific configuration files."""
        # Look for domain-specific JSON files
        domain_files = []
        for file in os.listdir():
            if file.endswith('.json') and 'domain' in file.lower():
                domain_files.append(file)
        
        # Load each domain file
        for file in domain_files:
            try:
                self.domain_manager.load_from_file(file)
                self.console.print(f"[green]Loaded domains from {file}[/green]")
            except Exception as e:
                self.console.print(f"[yellow]Error loading domains from {file}: {str(e)}[/yellow]")
    
    def _filter_domains_by_category(self, domains: List[Domain], category: str = None) -> List[Domain]:
        """Filter domains by category based on keywords.
        
        Args:
            domains: List of domains to filter
            category: Category to filter by or None for all
            
        Returns:
            Filtered list of domains
        """
        if not category:
            return domains
            
        category = category.lower()
        filtered_domains = []
        
        # Define category keywords mapping
        categories = {
            "education": ["education", "learning", "teaching", "student", "school", "university"],
            "technology": ["technology", "tech", "digital", "software", "programming", "ai"],
            "business": ["business", "corporate", "organization", "management", "workplace"],
            "design": ["design", "ux", "creative", "visual", "interface"],
            "healthcare": ["health", "medical", "patient", "treatment", "care"]
        }
        
        # Check if category exists
        if category not in categories:
            return domains
            
        # Filter domains that match the category
        for domain in domains:
            # Check if any keywords match the category
            domain_keywords = [k.lower() for k in domain.keywords]
            if any(k in domain_keywords for k in categories[category]):
                filtered_domains.append(domain)
                continue
                
            # Check if category name appears in domain name or description
            if category in domain.name.lower() or category in domain.description.lower():
                filtered_domains.append(domain)
                
        return filtered_domains
    
    def _select_domain(self, step_num: int):
        """Handle domain selection with both RICH and fallback interfaces."""
        self.console.print(f"\n[bold cyan]Step {step_num}: Domain Selection[/bold cyan]")
            
        # Display available categories for filtering
        categories = ["education", "technology", "business", "design", "healthcare"]
        categories_table = Table(title="Domain Categories")
        categories_table.add_column("Category", style="cyan")
        categories_table.add_column("Description", style="dim")
            
        for category in categories:
            descriptions = {
                "education": "Educational domains related to teaching, learning, and instruction",
                "technology": "Technology-focused domains including software, digital transformation, and AI", 
                "business": "Business-related domains for corporate, management, and workplace",
                "design": "Design-oriented domains for UX, creative work, and interfaces",
                "healthcare": "Healthcare domains for medical applications, patient care, and wellness"
            }
            categories_table.add_row(category.capitalize(), descriptions.get(category, ""))
            
        self.console.print(categories_table)
            
        # Allow filtering by category
        category_filter = Prompt.ask(
            "Filter by category (or leave empty for all)",
            default=""
        )
            
        # Get all domains first
        all_domains = self.domain_manager.list_domains()
            
        # Filter by category if specified  
        if category_filter:
            filtered_domains = self._filter_domains_by_category(all_domains, category_filter)
            if not filtered_domains:
                self.console.print(f"[yellow]No domains in category '{category_filter}'. Showing all domains.[/yellow]")
                filtered_domains = all_domains
            else:
                self.console.print(f"[green]Found {len(filtered_domains)} domains in category '{category_filter}'.[/green]")
        else:
            filtered_domains = all_domains
            
        # Add search functionality
        search_query = Prompt.ask(
            "Search domains by keyword (or leave empty to see all)",
            default=""
        )
            
        if search_query:
            # If we already filtered by category, search within those results
            if category_filter:
                search_domains = []
                for domain in filtered_domains:
                    # Search in name, description and keywords
                    if (search_query.lower() in domain.name.lower() or 
                        search_query.lower() in domain.description.lower() or
                        any(search_query.lower() in keyword.lower() for keyword in domain.keywords)):
                        search_domains.append(domain)
            else:
                # Otherwise search all domains
                search_domains = self.domain_manager.search_domains(search_query)
                
            if not search_domains:
                self.console.print(f"[yellow]No domains matched your search '{search_query}'. Showing all domains in current filter.[/yellow]")
                domains = filtered_domains
            else:
                self.console.print(f"[green]Found {len(search_domains)} matching domains for '{search_query}'.[/green]")
                domains = search_domains
        else:
            domains = filtered_domains
            
        # Display available domains with keywords
        domains_table = Table(title="Available Domains")
        domains_table.add_column("#", style="green")
        domains_table.add_column("Domain", style="cyan")
        domains_table.add_column("Description")
        domains_table.add_column("Keywords", style="dim")
            
        for i, domain in enumerate(domains, 1):
            description = domain.description[:50] + "..." if len(domain.description) > 50 else domain.description
            keywords = ", ".join(domain.keywords[:3])
            if len(domain.keywords) > 3:
                keywords += "..."
                
            # Highlight search term if present
            if search_query and search_query.lower() in domain.name.lower():
                import re
                domain_name = re.sub(re.escape(search_query), f"[bold yellow]{search_query}[/bold yellow]", domain.name, flags=re.IGNORECASE)
            else:
                domain_name = domain.name
                
            domains_table.add_row(str(i), domain_name, description, keywords)
            
        self.console.print(domains_table)
            
        # Allow selection of domain
        domain_choice = IntPrompt.ask(
            "Select a domain by number (or 0 for default)",
            default=0,
            show_default=True
        )
            
        if domain_choice > 0 and domain_choice <= len(domains):
            selected_domain = domains[domain_choice - 1]
            self.params["domain"] = selected_domain.name
                
            # Show detailed information about selected domain
            self.console.print(f"Selected domain: [green]{selected_domain.name}[/green]")
            self.console.print(f"Description: {selected_domain.description}")
                
            if selected_domain.keywords:
                self.console.print(f"Keywords: [cyan]{', '.join(selected_domain.keywords)}[/cyan]")
                
            # Show related domains if available
            try:
                related_domains = self.domain_manager.get_related_domains(selected_domain.id, min_matches=1)
                if related_domains:
                    self.console.print("\n[italic]Related domains you might consider:[/italic]")
                    for rel_domain in related_domains[:3]:  # Show up to 3 related domains
                        self.console.print(f"- [cyan]{rel_domain.name}[/cyan]")
            except Exception:
                # Silently handle any errors getting related domains
                pass
        else:
            self.console.print("Using default domain.")
    def _get_timestamped_output_dir(self) -> str:
        """Generate a timestamped output directory path.
        
        Returns:
            Path to the timestamped output directory.
        """
        # Match the format used in main.py
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join("data", "output", f"run_{timestamp}")
    
    def _select_config_file(self) -> Optional[str]:
        """Allow the user to select a configuration file.
        
        Returns:
            Selected configuration file or None if no file is selected.
        """
        # Find all JSON files that might be configuration files
        potential_configs = []
        try:
            for f in os.listdir():
                if f.endswith('.json') and 'config' in f.lower():
                    potential_configs.append(f)
        except Exception:
            # Handle errors gracefully
            return None
        
        if not potential_configs:
            return None
        
        # Sort config files with unified_config.json first
        if "unified_config.json" in potential_configs:
            potential_configs.remove("unified_config.json")
            potential_configs.insert(0, "unified_config.json")
        
        self.console.print("\n[bold cyan]Step 2: Configuration File Selection[/bold cyan]")
            
        # Display available configuration files
        configs_table = Table(title="Available Configuration Files")
        configs_table.add_column("#", style="green")
        configs_table.add_column("File", style="cyan")
        configs_table.add_column("Description")
            
        for i, config_file in enumerate(potential_configs, 1):
            description = self._get_config_description(config_file)
            configs_table.add_row(str(i), config_file, description)
            
        self.console.print(configs_table)
            
        # Ask if the user wants to select a configuration file
        use_config = Confirm.ask(
            "Would you like to use a configuration file?",
            default=True if "unified_config.json" in potential_configs else False
        )
            
        if not use_config:
            return None
            
        # Allow selection of configuration file
        while True:
            choice = IntPrompt.ask(
                "Select a configuration file by number (or 0 to skip)",
                default=1 if "unified_config.json" in potential_configs else 0,
                show_default=True
            )
                
            if choice == 0:
                return None
                
            if 1 <= choice <= len(potential_configs):
                selected_config = potential_configs[choice - 1]
                    
                # Validate the config file
                if self._validate_config_file(selected_config):
                    return selected_config
                else:
                    self.console.print(f"[yellow]Warning: {selected_config} does not appear to be a valid ISEE configuration file. It may be missing required model mappings.[/yellow]")
                    use_anyway = Confirm.ask("Use this configuration file anyway?", default=False)
                    if use_anyway:
                        return selected_config
            else:
                self.console.print("[yellow]Invalid selection. Please try again.[/yellow]")
        return None
    
    def _get_default_config_file(self) -> Optional[str]:
        """Automatically select the best available configuration file.
        
        Returns:
            Path to unified_config.json if available, None otherwise.
        """
        # Always prefer unified_config.json as it accommodates all models
        if os.path.exists("unified_config.json"):
            if self._validate_config_file("unified_config.json"):
                self.console.print("[dim]Using unified_config.json (supports all available models)[/dim]")
                return "unified_config.json"
            else:
                self.console.print("[yellow]Warning: unified_config.json found but appears invalid[/yellow]")
        # If unified_config.json is not available, look for other configs
        potential_configs = []
        try:
            for f in os.listdir():
                if f.endswith('.json') and 'config' in f.lower() and f != "unified_config.json":
                    potential_configs.append(f)
        except Exception:
            pass
        
        # Try to find a valid alternative config
        for config_file in potential_configs:
            if self._validate_config_file(config_file):
                self.console.print(f"[dim]Using {config_file} as fallback configuration[/dim]")
                return config_file
        
        # No valid config found
        self.console.print("[yellow]No valid configuration file found. Proceeding without pre-configured models.[/yellow]")
        return None
    
    def _validate_config_file(self, config_path: str) -> bool:
        """Validate that a configuration file is compatible with the ISEE framework.
        
        Args:
            config_path: Path to the configuration file.
            
        Returns:
            True if the configuration file is valid, False otherwise.
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check if the config file has the expected structure
            if not isinstance(config, dict):
                return False
            
            # Check for models configuration
            if "models" not in config:
                return False
            
            # Ensure models is either a list or a dict with sections
            models = config["models"]
            if not (isinstance(models, list) or isinstance(models, dict)):
                return False
            
            # If it's a dict, check for expected sections
            if isinstance(models, dict):
                if not any(section in models for section in ["api_models", "ollama_models"]):
                    return False
            
            return True
        except (json.JSONDecodeError, IOError):
            return False
        
    def _get_config_description(self, config_path: str) -> str:
        """Get a description for a configuration file.
        
        Args:
            config_path: Path to the configuration file.
            
        Returns:
            Description of the configuration file.
        """
        # Check for known configuration files
        if config_path == "unified_config.json":
            return "Unified configuration with models mapped to API providers"
        elif config_path == "sample_config.json":
            return "Sample configuration for demonstration purposes"
        elif config_path == "gemini_test_config.json":
            return "Configuration for testing Google Gemini models"
        elif config_path == "ollama_config.json":
            return "Configuration for Ollama models"
        
        # Try to read the file and determine its purpose
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            if "models" in config:
                models = config["models"]
                model_count = 0
                
                if isinstance(models, list):
                    model_count = len(models)
                elif isinstance(models, dict):
                    # Count models in each section
                    api_models = models.get("api_models", [])
                    ollama_models = models.get("ollama_models", [])
                    model_count = len(api_models) + len(ollama_models)
                
                return f"Configuration with {model_count} model mappings"
        except (json.JSONDecodeError, IOError):
            pass
        
        return "Unknown configuration file"
    
    def _show_help_options(self) -> None:
        """Show help information about available command-line options."""
        help_info = [
            {
                "name": "--help",
                "description": "Show the help message and exit",
                "usage": "python main.py --help"
            },
            {
                "name": "--list-domains",
                "description": "List all available domains and exit",
                "usage": "python main.py --list-domains"
            },
            {
                "name": "--quick",
                "description": "Run in quick mode (stratified sampling with 36 combinations)",
                "usage": "python main.py --quick --query \"Your query here\""
            },
            {
                "name": "--full",
                "description": "Run in full mode (exhaustive combinations)",
                "usage": "python main.py --full --query \"Your query here\""
            }
        ]
        
        self.console.print("\n[bold cyan]Additional Command-Line Options[/bold cyan]")
            
        options_table = Table(title="Helpful Options")
        options_table.add_column("Option", style="green")
        options_table.add_column("Description", style="cyan")
        options_table.add_column("Example", style="yellow")
            
        for option in help_info:
            options_table.add_row(option["name"], option["description"], option["usage"])
            
        self.console.print(options_table)
    def configure_advanced_options(self, step_num: Optional[int] = 8) -> Dict[str, Any]:
        """Configure advanced options not covered by other steps.
        
        Args:
            step_num: The step number to display
            
        Returns:
            Dictionary of advanced options.
        """
        advanced_params = {}
        
        # Show different header based on complexity level
        if self.complexity_level == "expert":
            self.console.print(f"\n[bold cyan]Step {step_num}: Expert Configuration[/bold cyan]")
        else:
            self.console.print(f"\n[bold cyan]Step {step_num}: Advanced Options[/bold cyan]")
            
        # Show collapsible section indicator for intermediate parameters
        if self.complexity_level in ["advanced", "expert"]:
            self.console.print("[dim]🔧 Configuring advanced parameters...[/dim]\n")
            
        # Domain config (expert parameter)
        use_domain_config = False
        if self._should_show_parameter("domain_config"):
            use_domain_config = Confirm.ask(
                "Would you like to use a domain-specific configuration file?",
                default=False
            )
            
        if use_domain_config and self._should_show_parameter("domain_config"):
            domain_config_files = [f for f in os.listdir() if f.endswith('.json') and 'domain' in f.lower()]
            if domain_config_files:
                self.console.print("Available domain configuration files:")
                for i, file in enumerate(domain_config_files, 1):
                    self.console.print(f"{i}. {file}")
                    
                domain_config_choice = IntPrompt.ask(
                    "Select a domain configuration file by number (or 0 to skip)",
                    default=0
                )
                    
                if domain_config_choice > 0 and domain_config_choice <= len(domain_config_files):
                    advanced_params["domain_config"] = domain_config_files[domain_config_choice - 1]
            else:
                self.console.print("[yellow]No domain configuration files found.[/yellow]")
            
        # Report format
        if self.params["generate_reports"]:
            report_format_choices = ["markdown", "json"]
            self.console.print("Report formats:")
            for i, format_name in enumerate(report_format_choices, 1):
                self.console.print(f"{i}. {format_name}")
                
            report_format_index = IntPrompt.ask(
                "Select report format",
                default=1
            )
            if 1 <= report_format_index <= len(report_format_choices):
                advanced_params["report_format"] = report_format_choices[report_format_index - 1]
            
        # Export CSV
        if self.params["generate_reports"]:
            export_csv = Confirm.ask(
                "Export data as CSV files for analysis?",
                default=False
            )
            advanced_params["export_csv"] = export_csv
            
        # No visualizations
        if self.params["analyze_results"]:
            no_visualizations = Confirm.ask(
                "Skip generating visualization charts?",
                default=False
            )
            advanced_params["no_visualizations"] = no_visualizations
            
        # Quick/Full mode
        use_preset = Confirm.ask(
            "Use a preset running mode (quick or full)?",
            default=False
        )
            
        if use_preset:
            preset_choices = ["quick", "full"]
            preset_names = ["Quick mode (stratified sampling with 36 combinations)", 
                           "Full mode (exhaustive combinations)"]
                
            self.console.print("Available presets:")
            for i, (preset, desc) in enumerate(zip(preset_choices, preset_names), 1):
                self.console.print(f"{i}. {desc}")
                
            preset_choice = IntPrompt.ask(
                "Select a preset by number",
                default=1
            )
                
            if 1 <= preset_choice <= len(preset_choices):
                preset = preset_choices[preset_choice - 1]
                advanced_params[preset] = True
                    
                # Update related parameters based on the preset
                if preset == "quick":
                    advanced_params["sampling_method"] = "stratified"
                    advanced_params["max_combinations"] = 36
                elif preset == "full":
                    advanced_params["sampling_method"] = "exhaustive"
                    advanced_params["max_combinations"] = None
        # Update the parameters
        self.params.update(advanced_params)
        
        return advanced_params
    
    def _validate_parameters(self) -> Dict[str, Any]:
        """Validate all parameters before generating the command.
        
        Returns:
            Dictionary with validation results containing:
            - valid: Boolean indicating if parameters are valid
            - errors: List of critical errors that prevent command execution
            - warnings: List of potential issues that won't prevent execution
            - suggestions: List of suggestions to improve the command
        """
        # Initialize validation result
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Check that required parameters are set
        if not self.params["query"]:
            validation["valid"] = False
            validation["errors"].append("Query is required")
        
        # Validate template IDs if specified
        if self.params.get("instruction_templates"):
            template_ids = self.params["instruction_templates"].split(",")
            valid_template_ids = list(self.template_library.templates.keys())
            
            invalid_ids = []
            for template_id in template_ids:
                if template_id not in valid_template_ids:
                    invalid_ids.append(template_id)
            
            if invalid_ids:
                validation["valid"] = False
                validation["errors"].append(f"Invalid template ID(s): {', '.join(invalid_ids)}")
        
        # Validate parameter relationships
        if self.params.get("analyze_results") and not self.params.get("generate_reports"):
            validation["valid"] = False
            validation["errors"].append("analyze_results requires generate_reports to be enabled")
            validation["suggestions"].append("Enable --generate-reports to use --analyze-results")
        
        if self.params.get("export_csv") and not self.params.get("generate_reports"):
            validation["valid"] = False
            validation["errors"].append("export_csv requires generate_reports to be enabled")
            validation["suggestions"].append("Enable --generate-reports to use --export-csv")
        
        if self.params.get("no_visualizations") and not self.params.get("analyze_results"):
            validation["warnings"].append("no_visualizations has no effect without analyze_results")
        
        # Check for mutually exclusive parameters
        if self.params.get("quick") and self.params.get("full"):
            validation["valid"] = False
            validation["errors"].append("quick and full modes are mutually exclusive")
            validation["suggestions"].append("Choose either --quick or --full, not both")
        
        # Validate parameter value ranges
        if self.params.get("models", 0) <= 0:
            validation["valid"] = False
            validation["errors"].append("models must be a positive integer")
        elif self.params.get("models", 0) > 5:
            validation["warnings"].append(f"Using a large number of models ({self.params['models']}) may result in high API costs")
        
        if self.params.get("instructions", 0) <= 0:
            validation["valid"] = False
            validation["errors"].append("instructions must be a positive integer")
        elif self.params.get("instructions", 0) > 10:
            validation["warnings"].append(f"Using a large number of instructions ({self.params['instructions']}) may result in high API costs")
        
        if self.params.get("variations", 0) <= 0:
            validation["valid"] = False
            validation["errors"].append("variations must be a positive integer")
        elif self.params.get("variations", 0) > 5:
            validation["warnings"].append(f"Using a large number of variations ({self.params['variations']}) may result in high API costs")
        
        # Check efficiency and provide warnings/suggestions
        if not self.params.get("quick") and not self.params.get("full"):
            # Calculate total combinations
            models = self.params.get("models", 2)
            instructions = self.params.get("instructions", 3)
            variations = self.params.get("variations", 2)
            total_combinations = models * instructions * variations
            
            # If no max_combinations is set or it's larger than our calculation
            if not self.params.get("max_combinations") or self.params.get("max_combinations", 0) > total_combinations:
                if total_combinations > 100:
                    validation["warnings"].append(f"Large combination count ({total_combinations}) may take a long time to execute")
                    validation["suggestions"].append("Consider using --quick mode to reduce combinations")
                    validation["suggestions"].append("Or set --max-combinations to limit the number of executions")
                
                # Estimate API costs if using real models
                if not self.params.get("simulate") and total_combinations > 36:
                    validation["warnings"].append(f"Running {total_combinations} combinations may result in significant API costs")
                    validation["suggestions"].append("Use --simulate to test without making actual API calls")
        
        # Provide optimization suggestions
        if self.params.get("models", 0) > 1 and not self.params.get("balanced_models"):
            validation["suggestions"].append("Consider using --balanced-models to ensure even representation across providers")
        
        # Check for appropriate sampling method based on combination count
        if not self.params.get("quick") and not self.params.get("full"):
            models = self.params.get("models", 2)
            instructions = self.params.get("instructions", 3) 
            variations = self.params.get("variations", 2)
            total_combinations = models * instructions * variations
            
            if total_combinations > 50 and self.params.get("sampling_method") == "exhaustive":
                validation["suggestions"].append(f"For {total_combinations} combinations, consider using 'stratified' sampling")
            
        # Check instruction templates vs. count
        if self.params.get("instruction_templates") and self.params.get("instructions", 0) != 3:
            validation["warnings"].append("instruction_templates overrides the instructions count parameter")
        
        return validation
        
    def _display_validation_results(self, validation: Dict[str, Any]) -> bool:
        """Display validation results to the user.
        
        Args:
            validation: Validation results dictionary from _validate_parameters
            
        Returns:
            True if the user wants to continue despite warnings, False otherwise
        """
        if validation["valid"] and not validation["warnings"] and not validation["suggestions"]:
            return True
        
        # Display errors
        if validation["errors"]:
            self.console.print("\n[bold red]Command Validation Errors:[/bold red]")
            for error in validation["errors"]:
                self.console.print(f"❌ {error}")
            
        # Display warnings
        if validation["warnings"]:
            self.console.print("\n[bold yellow]Command Validation Warnings:[/bold yellow]")
            for warning in validation["warnings"]:
                self.console.print(f"⚠️ {warning}")
            
        # Display suggestions
        if validation["suggestions"]:
            self.console.print("\n[bold green]Suggestions for Improvement:[/bold green]")
            for suggestion in validation["suggestions"]:
                self.console.print(f"💡 {suggestion}")
                    
        # If there are errors, provide a summary
        if not validation["valid"]:
            self.console.print("\n[bold red]Command cannot be executed due to validation errors.[/bold red]")
            return False
                
        # If there are only warnings, ask the user if they want to continue
        if validation["warnings"]:
            return Confirm.ask("\nContinue despite warnings?", default=True)
            
        return True
    def select_instruction_templates(self, step_num: Optional[int] = 3) -> None:
        """Enhanced instruction template selection with cognitive framework visualization."""
        self.console.print(f"\n[bold cyan]Step {step_num}: Cognitive Frameworks & Instruction Templates[/bold cyan]")
        
        # Show cognitive diversity explanation if visualizer is available
        if FRAMEWORK_VISUALIZER_AVAILABLE and self.framework_visualizer:
            self.framework_visualizer.display_cognitive_diversity_explanation()
            
            # Display frameworks overview based on complexity level
            if self.complexity_level == "basic":
                self.framework_visualizer.display_frameworks_overview("basic")
                self.console.print("[dim]💡 More frameworks available in Advanced/Expert modes[/dim]\n")
            elif self.complexity_level == "advanced":
                self.framework_visualizer.display_frameworks_overview("advanced")
                
                # Show toggle for all frameworks
                show_all = Confirm.ask("Show all frameworks (including expert level)?", default=False)
                if show_all:
                    self.framework_visualizer.display_frameworks_overview("all")
            else:  # expert
                self.framework_visualizer.display_frameworks_overview("all")
        
        # Get user choice for template configuration
        self.console.print("[bold yellow]Choose how to configure instruction templates:[/bold yellow]")
        self.console.print("1. 🎯 Use number of templates (quick)")
        self.console.print("2. 🔧 Select specific frameworks (advanced)")
        self.console.print("3. ℹ️  Learn more about cognitive frameworks")
        
        choice_idx = self._get_selection_input(
            "template_choice",
            "Choose configuration method (1-3)",
            ["1", "2", "3"],
            default_value="1"
        )
        choice = str(choice_idx + 1)  # Convert 0-based index to 1-based choice
        
        if choice == "3":
            # Educational mode - show detailed framework information
            if FRAMEWORK_VISUALIZER_AVAILABLE and self.framework_visualizer:
                self._interactive_framework_exploration()
            else:
                self.console.print("[yellow]Framework visualization not available[/yellow]")
            
            # Ask again after education
            choice_idx = self._get_selection_input(
                "template_choice",
                "Choose configuration method (1-2)",
                ["1", "2"],
                default_value="1"
            )
            choice = str(choice_idx + 1)  # Convert 0-based index to 1-based choice
        
        if choice == "2":
            # Advanced template selection with visualization
            self._select_specific_templates()
        else:
            # Quick template count selection
            self._select_template_count()
    
    def _interactive_framework_exploration(self) -> None:
        """Interactive exploration of cognitive frameworks with visualization."""
        if not (FRAMEWORK_VISUALIZER_AVAILABLE and self.framework_visualizer):
            return
            
        self.console.print("\n[bold green]🧠 Interactive Framework Explorer[/bold green]")
        self.console.print("[cyan]Learn about different AI thinking approaches:[/cyan]\n")
        
        while True:
            self.console.print("[bold yellow]Available commands:[/bold yellow]")
            self.console.print("• [cyan]preview <number>[/cyan] - See detailed framework information")
            self.console.print("• [cyan]compare <num1> <num2>[/cyan] - Compare two frameworks")
            self.console.print("• [cyan]list[/cyan] - Show all frameworks")
            self.console.print("• [cyan]done[/cyan] - Finish exploration")
            
            command = Prompt.ask("Enter command", default="done")
            
            if command.lower() == "done":
                break
            elif command.lower() == "list":
                self.framework_visualizer.display_frameworks_overview("all")
            elif command.lower().startswith("preview "):
                try:
                    parts = command.split()
                    if len(parts) == 2:
                        # Convert number to framework ID
                        framework_num = int(parts[1])
                        templates = self.template_library.list_templates()
                        if 1 <= framework_num <= len(templates):
                            framework_id = templates[framework_num - 1].id
                            self.framework_visualizer.display_framework_detail(framework_id)
                        else:
                            self.console.print(f"[red]Invalid framework number. Use 1-{len(templates)}[/red]")
                    else:
                        self.console.print("[red]Usage: preview <number>[/red]")
                except (ValueError, IndexError):
                    self.console.print("[red]Invalid framework number[/red]")
            elif command.lower().startswith("compare "):
                try:
                    parts = command.split()
                    if len(parts) == 3:
                        # Convert numbers to framework IDs
                        num1, num2 = int(parts[1]), int(parts[2])
                        templates = self.template_library.list_templates()
                        if 1 <= num1 <= len(templates) and 1 <= num2 <= len(templates):
                            framework_id1 = templates[num1 - 1].id
                            framework_id2 = templates[num2 - 1].id
                            self.framework_visualizer.display_framework_comparison(framework_id1, framework_id2)
                        else:
                            self.console.print(f"[red]Invalid framework numbers. Use 1-{len(templates)}[/red]")
                    else:
                        self.console.print("[red]Usage: compare <num1> <num2>[/red]")
                except (ValueError, IndexError):
                    self.console.print("[red]Invalid framework numbers[/red]")
            else:
                self.console.print("[yellow]Unknown command. Type 'done' to finish exploration.[/yellow]")
    
    def _select_specific_templates(self) -> None:
        """Allow user to select specific cognitive frameworks/templates."""
        # Get all available templates
        templates = self.template_library.list_templates()
        
        self.console.print("\n[bold cyan]Select Specific Cognitive Frameworks[/bold cyan]")
        
        # Show numbered list with framework icons
        if FRAMEWORK_VISUALIZER_AVAILABLE and self.framework_visualizer:
            # Use the visualizer's framework overview
            self.framework_visualizer.display_frameworks_overview(self.complexity_level)
        else:
            # Fallback to simple table
            templates_table = Table(title="Available Templates")
            templates_table.add_column("#", style="green", width=3)
            templates_table.add_column("ID", style="cyan")
            templates_table.add_column("Name", style="blue")
            templates_table.add_column("Cognitive Style", style="yellow")
                
            for i, template in enumerate(templates, 1):
                templates_table.add_row(
                    str(i),
                    template.id, 
                    template.name,
                    template.metadata.get("cognitive_style", "Unknown")
                )
                
            self.console.print(templates_table)
        
        # Get template selections from user
        selected_templates = []
        self.console.print("\n[bold yellow]Enter framework numbers to include (e.g., '1,3,5' or '2-4'):[/bold yellow]")
        self.console.print("[dim]Special commands: 'preview <number>', 'compare <num1> <num2>', 'help'[/dim]")
        
        while True:
            user_input = Prompt.ask(
                "Framework selection (or 'done' to finish)",
                default=""
            ).strip()
            
            if not user_input or user_input.lower() == "done":
                break
            
            # Handle special commands
            if user_input.lower().startswith("preview ") and FRAMEWORK_VISUALIZER_AVAILABLE:
                try:
                    num = int(user_input.split()[1])
                    if 1 <= num <= len(templates):
                        self.framework_visualizer.display_framework_detail(templates[num - 1].id)
                    else:
                        self.console.print(f"[red]Invalid number. Use 1-{len(templates)}[/red]")
                except (ValueError, IndexError):
                    self.console.print("[red]Invalid command format. Use 'preview <number>'[/red]")
                continue
            elif user_input.lower().startswith("compare ") and FRAMEWORK_VISUALIZER_AVAILABLE:
                try:
                    parts = user_input.split()
                    num1, num2 = int(parts[1]), int(parts[2])
                    if 1 <= num1 <= len(templates) and 1 <= num2 <= len(templates):
                        self.framework_visualizer.display_framework_comparison(
                            templates[num1 - 1].id, templates[num2 - 1].id
                        )
                    else:
                        self.console.print(f"[red]Invalid numbers. Use 1-{len(templates)}[/red]")
                except (ValueError, IndexError):
                    self.console.print("[red]Invalid command format. Use 'compare <num1> <num2>'[/red]")
                continue
            elif user_input.lower() == "help":
                self.console.print("[cyan]Commands:[/cyan]")
                self.console.print("• Numbers: '1,3,5' or '2-4' to select frameworks")
                self.console.print("• 'preview <number>' to see framework details")
                self.console.print("• 'compare <num1> <num2>' to compare frameworks") 
                self.console.print("• 'done' to finish selection")
                continue
            
            # Parse number selections
            try:
                selected_numbers = self._parse_number_selection(user_input, len(templates))
                if selected_numbers:
                    for num in selected_numbers:
                        template_id = templates[num - 1].id
                        if template_id not in selected_templates:
                            selected_templates.append(template_id)
                            template_name = templates[num - 1].name
                            icon = ""
                            if FRAMEWORK_VISUALIZER_AVAILABLE and self.framework_visualizer:
                                icon = self.framework_visualizer.framework_icons.get(template_id, "🤔")
                            self.console.print(f"✓ Added: [green]{icon} {template_name}[/green]")
                        
                    # Show current selection
                    if selected_templates:
                        self.console.print(f"\n[bold]Selected frameworks ({len(selected_templates)}):[/bold]")
                        for template_id in selected_templates:
                            template = next(t for t in templates if t.id == template_id)
                            icon = ""
                            if FRAMEWORK_VISUALIZER_AVAILABLE and self.framework_visualizer:
                                icon = self.framework_visualizer.framework_icons.get(template_id, "🤔")
                            self.console.print(f"  {icon} {template.name}")
                        self.console.print()
                        
            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")
        
        if selected_templates:
            # Convert the list to a comma-separated string
            self.params["instruction_templates"] = ",".join(selected_templates)
            self.console.print(f"\n[green]✓ Selected {len(selected_templates)} cognitive frameworks[/green]")
        else:
            self.console.print("[yellow]No specific frameworks selected - using count-based selection[/yellow]")
            self._select_template_count()
    
    def _select_template_count(self) -> None:
        """Select number of instruction templates to use."""
        instructions_input = self._get_parameter_input("instructions", "Number of instruction templates to use", "3")
        
        # Convert to integer after handling any special commands
        try:
            instructions_count = int(instructions_input) if instructions_input.strip() else 3
            if instructions_count < 1 or instructions_count > 10:
                self.console.print("[red]Instructions must be between 1 and 10, using default of 3[/red]")
                instructions_count = 3
        except ValueError:
            self.console.print("[red]Invalid number, using default of 3[/red]")
            instructions_count = 3
            
        self.params["instructions"] = instructions_count
        
        if FRAMEWORK_VISUALIZER_AVAILABLE and self.framework_visualizer:
            # Show which frameworks will be automatically selected
            self.console.print(f"\n[dim]💡 ISEE will automatically select {instructions_count} diverse cognitive frameworks for maximum exploration[/dim]")
    
    def _parse_number_selection(self, input_str: str, max_num: int) -> List[int]:
        """Parse user input for number selections (e.g., '1,3,5' or '2-4')."""
        numbers = []
        parts = input_str.replace(" ", "").split(",")
        
        for part in parts:
            if "-" in part:
                # Range selection
                try:
                    start, end = map(int, part.split("-"))
                    if start < 1 or end > max_num or start > end:
                        raise ValueError(f"Invalid range: {part}. Use 1-{max_num}")
                    numbers.extend(range(start, end + 1))
                except ValueError:
                    raise ValueError(f"Invalid range format: {part}")
            else:
                # Single number
                try:
                    num = int(part)
                    if num < 1 or num > max_num:
                        raise ValueError(f"Invalid number: {num}. Use 1-{max_num}")
                    numbers.append(num)
                except ValueError:
                    raise ValueError(f"Invalid number: {part}")
        
        return sorted(list(set(numbers)))  # Remove duplicates and sort
    def generate_command(self) -> str:
        """Generate the command to run based on the selected parameters.
        
        Returns:
            The command string to run the ISEE framework.
        """
        # Validate parameters
        validation = self._validate_parameters()
        if not self._display_validation_results(validation):
            return ""
        
        command_parts = ["python", "main.py"]
        
        # Add query
        if self.params["query"]:
            command_parts.append(f"--query \"{self.params['query']}\"")
        
        # Add domain
        if self.params["domain"]:
            command_parts.append(f"--domain \"{self.params['domain']}\"")
        
        # Add config file
        if "config_file" in self.params and self.params["config_file"]:
            command_parts.append(f"--config \"{self.params['config_file']}\"")
        elif "openrouter_filters" in self.params:
            # Fallback: Auto-add OpenRouter config if filters are detected but no config specified
            command_parts.append("--config \"openrouter_config.json\"")
        
        # Add instruction templates if specified
        if self.params.get("instruction_templates"):
            command_parts.append(f"--instruction-templates \"{self.params['instruction_templates']}\"")
        else:
            # Add instructions count
            if self.params["instructions"]:
                command_parts.append(f"--instructions {self.params['instructions']}")
        
        # Add models count
        if self.params["models"]:
            command_parts.append(f"--models {self.params['models']}")
        
        # Add variations count
        if self.params["variations"]:
            command_parts.append(f"--variations {self.params['variations']}")
        
        # Add sampling method
        if self.params.get("sampling_method"):
            command_parts.append(f"--sampling-method {self.params['sampling_method']}")
        
        # Add max combinations
        if self.params.get("max_combinations"):
            command_parts.append(f"--max-combinations {self.params['max_combinations']}")
        
        # Add use ollama
        if self.params.get("use_ollama"):
            command_parts.append("--use-ollama")
        
        # Add balanced models
        if self.params.get("balanced_models"):
            command_parts.append("--balanced-models")
        
        # Add output format
        if self.params.get("output_format"):
            command_parts.append(f"--output-format {self.params['output_format']}")
        
        # Add output file
        if self.params.get("output_file"):
            command_parts.append(f"--output-file \"{self.params['output_file']}\"")
        
        # Add simulate
        if self.params.get("simulate"):
            command_parts.append("--simulate")
        
        # Add dry run
        if self.params.get("dry_run"):
            command_parts.append("--dry-run")
        
        # Add generate reports
        if self.params.get("generate_reports"):
            command_parts.append("--generate-reports")
            
            # Report format
            if "report_format" in self.params and self.params["report_format"]:
                command_parts.append(f"--report-format {self.params['report_format']}")
            
            # Export CSV
            if "export_csv" in self.params and self.params["export_csv"]:
                command_parts.append("--export-csv")
        
        # Add analyze results
        if self.params["analyze_results"]:
            command_parts.append("--analyze-results")
            
            # No visualizations
            if "no_visualizations" in self.params and self.params["no_visualizations"]:
                command_parts.append("--no-visualizations")
        
        # Add save state
        if self.params.get("save_state"):
            command_parts.append(f"--save-state \"{self.params['save_state']}\"")
        
        # Add load state
        if self.params.get("load_state"):
            command_parts.append(f"--load-state \"{self.params['load_state']}\"")
        
        # Add synthesize method
        if self.params.get("synthesize_method"):
            command_parts.append(f"--synthesize-method {self.params['synthesize_method']}")
        
        # Add domain config
        if "domain_config" in self.params and self.params["domain_config"]:
            command_parts.append(f"--domain-config \"{self.params['domain_config']}\"")
        
        # Add quick/full mode flags
        if "quick" in self.params and self.params["quick"]:
            command_parts.append("--quick")
        elif "full" in self.params and self.params["full"]:
            command_parts.append("--full")
        
        return " ".join(command_parts)
    
    def validate_command(self, command: str) -> Dict[str, Any]:
        """Validate an ISEE command string for potential issues.
        
        Args:
            command: ISEE command string to validate
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        if not command:
            validation["valid"] = False
            validation["errors"].append("Empty command")
            return validation
        
        # Extract parameters from command string
        # Simplified regex to capture parameter names and values
        param_pattern = r'--(\w+)(?:[= ]"([^"]*)"| ([^ "]*)|)'
        params = {}
        
        for match in re.finditer(param_pattern, command):
            param_name = match.group(1)
            # Value could be in group 2 (quoted) or group 3 (unquoted)
            param_value = match.group(2) if match.group(2) else match.group(3)
            
            # If no value was captured, it's a flag parameter
            if param_value is None:
                params[param_name] = True
            else:
                params[param_name] = param_value
        
        # Check for syntax issues
        if not params:
            validation["warnings"].append("Could not parse any parameters from the command")
        
        # Check for common command issues
        if "query" not in params:
            validation["errors"].append("Missing required parameter: --query")
            validation["valid"] = False
        
        # Check for compatibility with sampling method
        if "sampling-method" in params:
            if params["sampling-method"] not in ["exhaustive", "stratified", "random"]:
                validation["warnings"].append(f"Unknown sampling method: {params['sampling-method']}")
        
        # Check for potential cost or performance issues
        if "max-combinations" not in params and "quick" not in params and "full" not in params:
            validation["warnings"].append("No combination limit specified (--max-combinations, --quick, or --full)")
            validation["suggestions"].append("Consider adding --max-combinations or using --quick mode to limit API calls")
        
        # Check for potentially long-running commands
        if "models" in params and "instructions" in params and "variations" in params:
            try:
                models = int(params["models"])
                instructions = int(params["instructions"])
                variations = int(params["variations"])
                total_combinations = models * instructions * variations
                
                if total_combinations > 100 and "max-combinations" not in params and "quick" not in params:
                    validation["warnings"].append(f"Command will generate {total_combinations} combinations without a limit")
                    validation["suggestions"].append("This may take a long time to execute and incur significant API costs")
            except (ValueError, TypeError):
                pass
        
        # Return result
        return validation
        
    def reconfigure_parameters(self) -> None:
        """Allow the user to modify command parameters after an error."""
        self.console.print("\n[bold cyan]Parameter Reconfiguration[/bold cyan]")
            
        # Display current parameters
        params_table = Table(title="Current Parameters")
        params_table.add_column("Parameter", style="cyan")
        params_table.add_column("Value", style="green")
            
        for param, value in self.params.items():
            if value is not None:
                params_table.add_row(param, str(value))
            
        self.console.print(params_table)
            
        # Allow user to modify parameters
        while True:
            modify = Confirm.ask("Would you like to modify a parameter?", default=True)
            if not modify:
                break
                    
            # Let user select parameter to modify
            param_choices = list(self.params.keys())
            param_names = [name.replace("_", "-") for name in param_choices]
                
            for i, name in enumerate(param_names, 1):
                self.console.print(f"{i}. {name}")
                    
            param_idx = IntPrompt.ask(
                "Select a parameter to modify",
                choices=list(range(1, len(param_choices)+1))
            )
                
            param_name = param_choices[param_idx-1]
            current_value = self.params[param_name]
                
            # Get new value
            if isinstance(current_value, bool):
                new_value = Confirm.ask(
                    f"New value for {param_name}",
                    default=current_value
                )
            elif isinstance(current_value, int):
                new_value = IntPrompt.ask(
                    f"New value for {param_name}",
                    default=current_value
                )
            else:
                new_value = Prompt.ask(
                    f"New value for {param_name}",
                    default=str(current_value) if current_value is not None else ""
                )
                    
            # Convert string to appropriate type if needed
            if param_name in ["models", "instructions", "variations", "max_combinations"]:
                try:
                    new_value = int(new_value)
                except ValueError:
                    self.console.print("[yellow]Invalid integer value. Parameter not updated.[/yellow]")
                    continue
                        
            # Update parameter
            self.params[param_name] = new_value
            self.console.print(f"[green]Updated {param_name} to {new_value}[/green]")
    def execute_command(self, command: str) -> Tuple[bool, Any, Optional[str]]:
        """
        Execute a command with error handling and recovery.
        
        Args:
            command: The command string to execute
            
        Returns:
            Tuple of (success, result, error)
        """
        self.console.print(f"[bold green]Running:[/bold green] {command}")
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            self.console.print("[bold green]Command completed successfully.[/bold green]")
            return (True, result, None)
        except subprocess.CalledProcessError as e:
            # Detect and classify the error
            error = detect_error_type(e, command)
            
            # Create recovery strategy
            recovery_strategy = create_recovery_strategy(error)
            
            # Display error information
            self.console.print(f"[bold red]Error:[/bold red] {recovery_strategy.get_user_friendly_message()}")
                
            # Display suggestions
            if recovery_strategy.get_suggestions():
                self.console.print("[bold yellow]Suggestions:[/bold yellow]")
                for suggestion in recovery_strategy.get_suggestions():
                    self.console.print(f"- {suggestion}")
            # Attempt recovery if possible
            if recovery_strategy.can_auto_recover():
                attempt_recovery = Confirm.ask("Would you like to attempt automatic recovery?", default=True)
                if attempt_recovery:
                    recovery_succeeded = recovery_strategy.attempt_recovery(self)
                    if recovery_succeeded:
                        # Re-validate and retry the command
                        updated_command = self.generate_command()
                        if updated_command:
                            return self.execute_command(updated_command)
                        else:
                            # Command generation failed after recovery
                            return (False, None, "command_generation_failed")
                    
            # If we can't auto-recover, offer manual options
            self.console.print("[bold cyan]Options:[/bold cyan]")
            options = [
                "Try again with the same command",
                "Modify command parameters",
                "Switch to simulation mode",
                "Abort execution"
            ]
            for i, option in enumerate(options, 1):
                self.console.print(f"{i}. {option}")
                    
            choice = IntPrompt.ask("What would you like to do?", choices=list(range(1, len(options)+1)))
                
            if choice == 1:
                return self.execute_command(command)
            elif choice == 2:
                # Return to parameter configuration
                return (False, None, "parameters_need_modification")
            elif choice == 3:
                self.params["simulate"] = True
                updated_command = self.generate_command()
                if updated_command:
                    return self.execute_command(updated_command)
                else:
                    return (False, None, "command_generation_failed")
            else:
                return (False, None, "execution_aborted")
        except Exception as e:
            # Handle unexpected errors
            self.console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
            return (False, None, "unexpected_error")

    def copy_to_clipboard(self, text: str) -> bool:
        """
        Copy text to the system clipboard.
        
        Args:
            text: The text to copy to clipboard
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import pyperclip
            pyperclip.copy(text)
            return True
        except ImportError:
            # pyperclip not available, try platform-specific alternatives
            import subprocess
            import platform
            
            system = platform.system()
            try:
                if system == "Darwin":  # macOS
                    subprocess.run(["pbcopy"], input=text, text=True, check=True)
                elif system == "Windows":
                    subprocess.run(["clip"], input=text, text=True, check=True)
                else:  # Linux and others
                    # Try xclip first, then xsel
                    try:
                        subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True, check=True)
                    except FileNotFoundError:
                        subprocess.run(["xsel", "--clipboard", "--input"], input=text, text=True, check=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False
        except Exception:
            return False

    def run_wizard(self):
        """
        Run the command wizard. Alias for main() method for test compatibility.
        """
        return self.main()

    def _display_enhanced_parameter_preview(self, show_detailed: bool = True) -> None:
        """
        Display an enhanced parameter preview with categorization and detailed explanations.
        
        Args:
            show_detailed: Whether to show detailed parameter explanations
        """
            
        # Get parameter categories from parameter context if available
        if PARAMETER_CONTEXT_AVAILABLE and self.param_context:
            from parameter_context import PARAMETER_CATEGORIES
            categories = PARAMETER_CATEGORIES
        else:
            # Fallback categories if parameter context is not available
            categories = {
                "basic": {
                    "name": "Basic Parameters",
                    "description": "Core parameters that define the essential aspects of your ISEE run",
                    "parameters": ["query", "domain", "models", "instructions", "variations"]
                },
                "sampling": {
                    "name": "Sampling Control", 
                    "description": "Parameters that control how combinations are selected",
                    "parameters": ["sampling_method", "max_combinations", "quick", "full"]
                },
                "output": {
                    "name": "Output Options",
                    "description": "Parameters that control what is generated",
                    "parameters": ["output_format", "generate_reports", "analyze_results"]
                },
                "advanced": {
                    "name": "Advanced Options",
                    "description": "Parameters for fine-tuning and specialized use cases",
                    "parameters": ["simulate", "dry_run", "balanced_models", "use_ollama"]
                }
            }
        
        # Calculate combination metrics
        models = self.params.get("models", 2)
        instructions = self.params.get("instructions", 3)
        variations = self.params.get("variations", 2)
        total_combinations = models * instructions * variations
        
        # Create categorized parameter displays
        for category_key, category_info in categories.items():
            category_params = []
            category_name = category_info["name"]
            category_desc = category_info["description"]
            
            # Collect parameters for this category that are actually set
            for param_name in category_info["parameters"]:
                if param_name in self.params:
                    value = self.params[param_name]
                    
                    # Skip None values or empty strings for cleaner display
                    if value is None or value == "" or value == []:
                        continue
                        
                    # Format parameter value for display
                    display_value = self._format_parameter_value(param_name, value)
                    
                    # Get parameter description
                    description = self._get_parameter_description(param_name, show_detailed)
                    
                    category_params.append((param_name, display_value, description))
            
            # Add computed values for basic category
            if category_key == "basic":
                # Add total combinations
                if self.params.get("max_combinations"):
                    max_combinations = min(total_combinations, self.params["max_combinations"])
                    combo_display = f"{total_combinations} (limited to {max_combinations})"
                else:
                    combo_display = str(total_combinations)
                
                combo_desc = "Total number of combinations to be executed"
                category_params.append(("combinations", combo_display, combo_desc))
                
                # Add config file if specified
                if self.params.get("config_file"):
                    category_params.append(("config_file", self.params["config_file"], "Configuration file being used"))
            
            # Only display categories that have parameters
            if category_params:
                self._display_parameter_category(category_name, category_desc, category_params, show_detailed)
        
        # Add impact panel to show how parameters affect execution
        self._display_parameter_impacts(total_combinations, models, instructions, variations)
    
    def _format_parameter_value(self, param_name: str, value: any) -> str:
        """Format a parameter value for display."""
        if isinstance(value, bool):
            return "Yes" if value else "No"
        elif isinstance(value, list):
            return ", ".join(str(v) for v in value)
        elif param_name == "instruction_templates" and isinstance(value, str):
            # Show template details if available
            template_ids = value.split(",")
            if len(template_ids) <= 3:
                return ", ".join(template_ids)
            else:
                return f"{', '.join(template_ids[:3])}... (+{len(template_ids)-3} more)"
        else:
            return str(value)
    
    def _get_parameter_description(self, param_name: str, detailed: bool = False) -> str:
        """Get description for a parameter."""
        # Try parameter context first
        if PARAMETER_CONTEXT_AVAILABLE and self.param_context:
            context = self.param_context.get_parameter_context(param_name)
            if context:
                return context.get("long" if detailed else "short", "")
        
        # Fallback to PARAMETER_DESCRIPTIONS
        if param_name in PARAMETER_DESCRIPTIONS:
            return PARAMETER_DESCRIPTIONS[param_name].get("long" if detailed else "short", "")
        
        # Default descriptions for common parameters
        descriptions = {
            "combinations": "Total number of combinations to be executed",
            "config_file": "Configuration file specifying models and settings"
        }
        
        return descriptions.get(param_name, "")
    
    def _display_parameter_category(self, category_name: str, category_desc: str, 
                                   params: list, show_detailed: bool) -> None:
        """Display a category of parameters in a formatted table."""
        # Create category-specific color scheme
        category_colors = {
            "Basic Parameters": "cyan",
            "Sampling Control": "green", 
            "Model Selection": "blue",
            "Output Options": "magenta",
            "Advanced Options": "yellow"
        }
        
        border_color = category_colors.get(category_name, "white")
        
        # Create table for this category
        table = Table(title=f"{category_name}", title_style=f"bold {border_color}")
        table.add_column("Parameter", style=border_color, width=20)
        table.add_column("Value", style="green", width=25)
        
        if show_detailed:
            table.add_column("Description", style="dim white", width=50)
        
        # Add parameters to table
        for param_name, value, description in params:
            display_name = param_name.replace("_", "-").title()
            
            if show_detailed:
                # Truncate long descriptions for table display
                desc_display = description[:47] + "..." if len(description) > 50 else description
                table.add_row(display_name, value, desc_display)
            else:
                table.add_row(display_name, value)
        
        # Display the table
        self.console.print(table)
        
        # Add category description as a subtle note
        if show_detailed and category_desc:
            self.console.print(f"[dim]{category_desc}[/dim]\n")
        else:
            self.console.print()  # Add spacing
    
    def _display_basic_parameter_preview(self) -> None:
        """Fallback parameter preview for non-rich environments."""
        print("\nCommand Parameters:")
        print(f"Query: {self.params['query'] or ''}")
        print(f"Domain: {self.params['domain'] or 'Default'}")
        print(f"Models: {self.params.get('models', 2)}")
        print(f"Instructions: {self.params.get('instructions', 3)}")
        print(f"Variations: {self.params.get('variations', 2)}")
        
        # Calculate combinations
        total_combinations = (self.params.get('models', 2) * 
                            self.params.get('instructions', 3) * 
                            self.params.get('variations', 2))
        print(f"Total Combinations: {total_combinations}")
        
        # Show enabled flags
        flags = []
        if self.params.get("simulate"): flags.append("simulate")
        if self.params.get("dry_run"): flags.append("dry-run")
        if self.params.get("balanced_models"): flags.append("balanced-models")
        
        if flags:
            print(f"Enabled flags: {', '.join(flags)}")

    def _display_parameter_impacts(self, total_combinations: int, models: int, instructions: int, variations: int) -> None:
        """Display a panel showing how parameters affect execution."""
            
        impact_items = []
        
        # Add specific impact statements based on selected parameters
        if total_combinations > 50:
            impact_items.append(f"⚠️ Running {total_combinations} combinations may result in significant API costs")
        
        if models > 3:
            impact_items.append(f"⚠️ Using {models} models increases API costs proportionally")
        
        if self.params.get("balanced_models"):
            impact_items.append("✓ Balanced model distribution ensures even representation across providers")
        
        if self.params.get("sampling_method") == "stratified" or self.params.get("quick"):
            impact_items.append("✓ Stratified sampling provides good coverage with fewer combinations")
        
        if self.params.get("simulate"):
            impact_items.append("✓ Simulation mode avoids all API costs (but provides placeholder responses)")
        
        # Add quality vs quantity considerations
        if total_combinations < 10:
            impact_items.append("ℹ️ Low combination count may limit result diversity")
        elif total_combinations > 100:
            impact_items.append("ℹ️ High combination count provides comprehensive coverage but increases time/cost")
        
        if impact_items:
            impact_panel = Panel(
                "\n".join(impact_items),
                title="Parameter Impact Analysis",
                border_style="yellow"
            )
            self.console.print(impact_panel)

    def _show_parameter_changes(self) -> None:
        """Show changes from previous parameter state for before/after comparison."""
        if not self.previous_params:
            return
            
        changes = []
        current_params = self.params.copy()
        
        # Compare current params with previous params
        all_param_keys = set(current_params.keys()) | set(self.previous_params.keys())
        
        for key in all_param_keys:
            old_val = self.previous_params.get(key)
            new_val = current_params.get(key)
            
            if old_val != new_val:
                # Format values for display
                old_display = self._format_parameter_value(key, old_val) if old_val is not None else "Not set"
                new_display = self._format_parameter_value(key, new_val) if new_val is not None else "Not set"
                
                changes.append((key, old_display, new_display))
        
        if changes:
            changes_table = Table(title="Parameter Changes", title_style="bold yellow")
            changes_table.add_column("Parameter", style="cyan")
            changes_table.add_column("Previous", style="red")
            changes_table.add_column("Current", style="green")
            
            for param_name, old_val, new_val in changes:
                display_name = param_name.replace("_", "-").title()
                changes_table.add_row(display_name, old_val, new_val)
            
            self.console.print(changes_table)
    
    def _save_current_params(self) -> None:
        """Save current parameters for change tracking."""
        self.previous_params = self.params.copy()

    def preview_command(self, show_detailed: bool = None) -> None:
        """
        Preview the command that will be run with enhanced explanations.
        
        Args:
            show_detailed: Whether to show detailed parameter explanations. If None, uses current mode.
        """
        # Use provided value or fall back to current mode
        if show_detailed is None:
            show_detailed = self.preview_detailed_mode
        command = self.generate_command()
        
        if not command:
            return
            
        # Validate the constructed command
        command_validation = self.validate_command(command)
        
        # Update cost and time estimates (UX Enhancement - Step 1.1)
        if COST_ESTIMATION_AVAILABLE and self.cost_estimator:
            self._update_cost_estimate()
        
        self.console.print("\n[bold cyan]Command Preview[/bold cyan]")
            
        # Create panel for command with appropriate color based on validation
        border_style = "green"
        if not command_validation["valid"]:
            border_style = "red"
        elif command_validation["warnings"]:
            border_style = "yellow"
                
        command_panel = Panel(
            command,
            title="Generated Command",
            border_style=border_style
        )
        self.console.print(command_panel)
            
        # Display cost and time estimates (UX Enhancement - Step 1.1)
        if COST_ESTIMATION_AVAILABLE and self.cost_estimator:
            self._display_cost_estimate()
            
        # Display command validation results if there are issues
        if not command_validation["valid"] or command_validation["warnings"]:
            validation_table = Table(title="Command Validation")
            validation_table.add_column("Type", style="cyan")
            validation_table.add_column("Message", style="white")
                
            for error in command_validation["errors"]:
                validation_table.add_row("Error", f"[red]{error}[/red]")
                
            for warning in command_validation["warnings"]:
                validation_table.add_row("Warning", f"[yellow]{warning}[/yellow]")
                
            for suggestion in command_validation["suggestions"]:
                validation_table.add_row("Suggestion", f"[green]{suggestion}[/green]")
                
            self.console.print(validation_table)
            
        # Show parameter changes if available (before/after comparison)
        self._show_parameter_changes()
            
        # UX Enhancement - Step 1.3: Enhanced Command Preview with categorization
        self._display_enhanced_parameter_preview(show_detailed)
            
        # Add collapsible detail toggle option
        if show_detailed:
            self.console.print("[dim]Showing detailed view. Type 'preview summary' to see summary view.[/dim]")
        else:
            self.console.print("[dim]Showing summary view. Type 'preview detailed' to see detailed view.[/dim]")
            
        # The cost and time estimation is now handled by the _display_cost_estimate method
        # No need for additional time estimates here as they're included in the cost estimation
        # This keeps the estimates consistent throughout the UI
    def _select_purpose(self) -> Optional[str]:
        """
        Purpose selection step (UX Enhancement - Step 2.1)
        
        Returns:
            The selected purpose category ID, or None if skipped/not available
        """
        if not PURPOSE_SELECTION_AVAILABLE or not self.purpose_manager:
            return None
        
        self.console.print("[bold cyan]Step 1: Purpose Selection[/bold cyan]")
        self.console.print("What do you want to accomplish with ISEE? Choose your purpose to get tailored parameter recommendations.\n")
            
        # Group categories by expertise level for better organization
        beginner_cats = self.purpose_manager.get_categories_by_expertise("beginner")
        intermediate_cats = self.purpose_manager.get_categories_by_expertise("intermediate")
        advanced_cats = self.purpose_manager.get_categories_by_expertise("advanced")
            
        # Create purpose selection table
        purpose_table = Table(title="Choose Your Purpose")
        purpose_table.add_column("#", style="green", width=3)
        purpose_table.add_column("Purpose", style="cyan", width=20)
        purpose_table.add_column("Description", width=40)
        purpose_table.add_column("Cost", style="yellow", width=8)
        purpose_table.add_column("Runtime", style="blue", width=10)
            
        all_categories = []
            
        # Add beginner section
        if beginner_cats:
            purpose_table.add_section()
            purpose_table.add_row("", "[bold green]🌱 Beginner-Friendly[/bold green]", "", "", "")
            for cat in beginner_cats:
                all_categories.append(cat)
                purpose_table.add_row(
                    str(len(all_categories)),
                    f"{cat.icon} {cat.name}",
                    cat.description[:50] + "..." if len(cat.description) > 50 else cat.description,
                    cat.estimated_cost.title(),
                    cat.typical_runtime.title()
                )
            
        # Add intermediate section
        if intermediate_cats:
            purpose_table.add_section()
            purpose_table.add_row("", "[bold yellow]⚡ Intermediate[/bold yellow]", "", "", "")
            for cat in intermediate_cats:
                all_categories.append(cat)
                purpose_table.add_row(
                    str(len(all_categories)),
                    f"{cat.icon} {cat.name}",
                    cat.description[:50] + "..." if len(cat.description) > 50 else cat.description,
                    cat.estimated_cost.title(),
                    cat.typical_runtime.title()
                )
            
        # Add advanced section
        if advanced_cats:
            purpose_table.add_section()
            purpose_table.add_row("", "[bold red]🎯 Advanced[/bold red]", "", "", "")
            for cat in advanced_cats:
                all_categories.append(cat)
                purpose_table.add_row(
                    str(len(all_categories)),
                    f"{cat.icon} {cat.name}",
                    cat.description[:50] + "..." if len(cat.description) > 50 else cat.description,
                    cat.estimated_cost.title(),
                    cat.typical_runtime.title()
                )
            
        self.console.print(purpose_table)
            
        # Allow purpose selection
        purpose_choice = IntPrompt.ask(
            "\nSelect your purpose by number (or 0 to skip and configure manually)",
            default=0,
            show_default=True
        )
            
        if purpose_choice > 0 and purpose_choice <= len(all_categories):
            selected_purpose = all_categories[purpose_choice - 1]
            self.selected_purpose = selected_purpose
                
            # Show detailed information about selected purpose
            purpose_panel = Panel(
                f"[bold]{selected_purpose.description}[/bold]\n\n"
                f"[cyan]Example use cases:[/cyan]\n" +
                "\n".join(f"• {example}" for example in selected_purpose.examples) +
                f"\n\n[yellow]Recommended settings will be applied automatically.[/yellow]",
                title=f"{selected_purpose.icon} {selected_purpose.name}",
                border_style="green"
            )
            self.console.print(purpose_panel)
                
            # Apply recommended parameters
            for param, value in selected_purpose.recommended_params.items():
                if value is not None:  # Only set non-None values
                    self.params[param] = value
                
            # Auto-select appropriate domains if specified
            if selected_purpose.domains:
                # Try to find the first matching domain
                for domain_id in selected_purpose.domains:
                    try:
                        domain = self.domain_manager.get_domain(domain_id)
                        if domain:
                            self.params["domain"] = domain.name
                            self.console.print(f"[green]→ Automatically selected domain: {domain.name}[/green]")
                            break
                    except KeyError:
                        # Domain doesn't exist, try the next one
                        continue
                
            return selected_purpose.id
        else:
            self.console.print("[dim]Skipping purpose selection - you can configure parameters manually.[/dim]")
            return None
    
    def _select_preset(self, purpose_category_id: Optional[str] = None) -> Optional[str]:
        """
        Preset selection step (UX Enhancement - Step 2.2)
        
        Args:
            purpose_category_id: The selected purpose category ID to filter presets
            
        Returns:
            The selected preset ID, or None if skipped/not available
        """
        if not PRESET_MANAGER_AVAILABLE or not self.preset_manager:
            return None
        
        # Get available presets for the selected purpose
        if purpose_category_id:
            available_presets = self.preset_manager.get_presets_by_purpose(purpose_category_id)
            if not available_presets:
                self.console.print(f"[yellow]No presets available for purpose '{purpose_category_id}'[/yellow]")
                return None
        else:
            # If no purpose selected, show all presets
            available_presets = self.preset_manager.list_presets()
        
        if not available_presets:
            return None
        
        step_label = "Step 1.5: Preset Selection" if purpose_category_id else "Step 1: Preset Selection"
        self.console.print(f"\n[bold cyan]{step_label}[/bold cyan]")
        
        if purpose_category_id:
            purpose_name = self.selected_purpose.name if self.selected_purpose else purpose_category_id
            self.console.print(f"Choose a preset configuration for '{purpose_name}' to get optimized parameter settings.\n")
        else:
            self.console.print("Choose a preset configuration to get optimized parameter settings.\n")
        
        # Create preset selection table
        preset_table = Table(title="Available Presets")
        preset_table.add_column("#", style="green", width=3)
        preset_table.add_column("Preset", style="cyan", width=25)
        preset_table.add_column("Description", width=35)
        preset_table.add_column("Cost", style="yellow", width=8)
        preset_table.add_column("Time", style="blue", width=10)
        preset_table.add_column("Level", style="magenta", width=12)
        
        # Sort presets by complexity level and cost
        complexity_order = {"beginner": 1, "intermediate": 2, "advanced": 3}
        cost_order = {"low": 1, "medium": 2, "high": 3}
        
        sorted_presets = sorted(available_presets, 
                              key=lambda p: (complexity_order.get(p.complexity_level, 2), 
                                           cost_order.get(p.estimated_cost, 2)))
        
        for i, preset in enumerate(sorted_presets):
            preset_table.add_row(
                str(i + 1),
                f"{preset.icon} {preset.name}",
                preset.description[:40] + "..." if len(preset.description) > 40 else preset.description,
                preset.estimated_cost.title(),
                preset.estimated_time.title(),
                preset.complexity_level.title()
            )
        
        self.console.print(preset_table)
        
        # Show option to skip preset selection and special commands
        self.console.print(f"\n[dim]Select a preset (1-{len(sorted_presets)}) or 0 to use purpose defaults[/dim]")
        self.console.print("[dim]Special commands: 'preview <number>' to preview a preset, 'compare <num1> <num2>' to compare[/dim]")
        
        while True:
            preset_input = Prompt.ask(
                "\nSelect preset by number, special command, or 0 to skip",
                default="0"
            ).strip()
            
            # Handle special commands
            if preset_input.lower().startswith("preview"):
                try:
                    parts = preset_input.split()
                    if len(parts) >= 2:
                        preset_num = int(parts[1])
                        if 1 <= preset_num <= len(sorted_presets):
                            self._show_preset_preview(sorted_presets[preset_num - 1].id)
                        else:
                            self.console.print(f"[red]Invalid preset number. Choose 1-{len(sorted_presets)}[/red]")
                    else:
                        self.console.print("[red]Usage: preview <number>[/red]")
                    continue
                except ValueError:
                    self.console.print("[red]Usage: preview <number>[/red]")
                    continue
            
            elif preset_input.lower().startswith("compare"):
                try:
                    parts = preset_input.split()
                    if len(parts) >= 3:
                        num1, num2 = int(parts[1]), int(parts[2])
                        if (1 <= num1 <= len(sorted_presets) and 1 <= num2 <= len(sorted_presets)):
                            preset_ids = [sorted_presets[num1 - 1].id, sorted_presets[num2 - 1].id]
                            self._compare_presets(preset_ids)
                        else:
                            self.console.print(f"[red]Invalid preset numbers. Choose 1-{len(sorted_presets)}[/red]")
                    else:
                        self.console.print("[red]Usage: compare <number1> <number2>[/red]")
                    continue
                except ValueError:
                    self.console.print("[red]Usage: compare <number1> <number2>[/red]")
                    continue
            
            # Handle regular selection
            try:
                preset_choice = int(preset_input)
                break
            except ValueError:
                self.console.print("[red]Please enter a number or use a special command[/red]")
                continue
        
        if preset_choice > 0 and preset_choice <= len(sorted_presets):
            selected_preset = sorted_presets[preset_choice - 1]
            self.selected_preset = selected_preset
            
            # Show detailed information about selected preset
            preset_panel = Panel(
                f"[bold]{selected_preset.description}[/bold]\n\n"
                f"[cyan]Use cases:[/cyan]\n" +
                "\n".join(f"• {use_case}" for use_case in selected_preset.use_cases) +
                f"\n\n[green]Parameter Configuration:[/green]\n" +
                "\n".join(f"• {param}: {value}" for param, value in selected_preset.parameters.items()) +
                f"\n\n[yellow]These settings will be applied automatically.[/yellow]",
                title=f"{selected_preset.icon} {selected_preset.name}",
                border_style="green"
            )
            self.console.print(preset_panel)
            
            # Apply preset parameters (these override purpose defaults)
            for param, value in selected_preset.parameters.items():
                if value is not None:  # Only set non-None values
                    self.params[param] = value
            
            self.console.print(f"[green]→ Applied preset configuration: {selected_preset.name}[/green]")
            return selected_preset.id
        else:
            if purpose_category_id:
                self.console.print("[dim]Using purpose default configuration.[/dim]")
            else:
                self.console.print("[dim]Skipping preset selection - you can configure parameters manually.[/dim]")
            return None
    
    def _show_preset_preview(self, preset_id: str) -> None:
        """
        Show a detailed preview of a preset configuration.
        
        Args:
            preset_id: The ID of the preset to preview
        """
        if not self.preset_manager:
            return
        
        preset = self.preset_manager.get_preset(preset_id)
        if not preset:
            return
        
        self.console.print(f"\n[bold cyan]Preset Preview: {preset.icon} {preset.name}[/bold cyan]")
        
        # Create parameter preview table
        preview_table = Table(title="Parameter Configuration")
        preview_table.add_column("Parameter", style="cyan", width=20)
        preview_table.add_column("Value", style="green", width=15)
        preview_table.add_column("Description", width=40)
        
        # Add parameter rows with descriptions
        for param, value in preset.parameters.items():
            param_display = param.replace("_", "-")
            
            # Get parameter description from context if available
            description = ""
            if PARAMETER_CONTEXT_AVAILABLE and self.param_context:
                context = self.param_context.get_parameter_context(param)
                if context:
                    description = context['short']
            
            preview_table.add_row(f"--{param_display}", str(value), description)
        
        self.console.print(preview_table)
        
        # Show estimated impact
        impact_panel = Panel(
            f"[yellow]Estimated Cost:[/yellow] {preset.estimated_cost.title()}\n"
            f"[blue]Estimated Time:[/blue] {preset.estimated_time.title()}\n"
            f"[magenta]Complexity Level:[/magenta] {preset.complexity_level.title()}\n\n"
            f"[green]Primary Use Cases:[/green]\n" +
            "\n".join(f"• {use_case}" for use_case in preset.use_cases[:3]),  # Show first 3 use cases
            title="Expected Impact",
            border_style="yellow"
        )
        self.console.print(impact_panel)
    
    def _compare_presets(self, preset_ids: List[str]) -> None:
        """
        Show a comparison view of multiple presets.
        
        Args:
            preset_ids: List of preset IDs to compare
        """
        if not self.preset_manager or len(preset_ids) < 2:
            return
        
        presets = [self.preset_manager.get_preset(pid) for pid in preset_ids if self.preset_manager.get_preset(pid)]
        if len(presets) < 2:
            return
        
        self.console.print(f"\n[bold cyan]Preset Comparison[/bold cyan]")
        
        # Create comparison table
        comparison_table = Table(title="Preset Comparison")
        comparison_table.add_column("Attribute", style="cyan", width=20)
        
        for preset in presets:
            comparison_table.add_column(f"{preset.icon} {preset.name}", width=20)
        
        # Add comparison rows
        attributes = [
            ("Description", lambda p: p.description[:30] + "..." if len(p.description) > 30 else p.description),
            ("Cost", lambda p: p.estimated_cost.title()),
            ("Time", lambda p: p.estimated_time.title()),
            ("Complexity", lambda p: p.complexity_level.title()),
            ("Models", lambda p: str(p.parameters.get("models", "N/A"))),
            ("Instructions", lambda p: str(p.parameters.get("instructions", "N/A"))),
            ("Combinations", lambda p: str(p.parameters.get("max_combinations", "N/A")))
        ]
        
        for attr_name, attr_func in attributes:
            row = [attr_name]
            for preset in presets:
                row.append(attr_func(preset))
            comparison_table.add_row(*row)
        
        self.console.print(comparison_table)
    
    def _save_current_as_preset(self) -> None:
        """
        Allow user to save current parameter configuration as a custom preset.
        """
        if not self.preset_manager:
            self.console.print("[red]Preset manager not available[/red]")
            return
        
        self.console.print("\n[bold cyan]Save Current Configuration as Preset[/bold cyan]")
        self.console.print("Create a custom preset from your current parameter settings.\n")
        
        # Get preset details from user
        preset_name = Prompt.ask("Enter a name for this preset", default="My Custom Preset")
        preset_description = Prompt.ask("Enter a description for this preset", 
                                      default="Custom configuration created from current settings")
        
        # Ask for purpose category if not already selected
        purpose_category = "custom_exploration"  # Default
        if self.selected_purpose:
            purpose_category = self.selected_purpose.id
        else:
            self.console.print("\nSelect purpose category for this preset:")
            purposes = self.purpose_manager.list_categories() if self.purpose_manager else []
            if purposes:
                purpose_table = Table()
                purpose_table.add_column("#", style="green", width=3)
                purpose_table.add_column("Purpose", style="cyan")
                
                for i, purpose in enumerate(purposes):
                    purpose_table.add_row(str(i + 1), f"{purpose.icon} {purpose.name}")
                
                self.console.print(purpose_table)
                
                purpose_choice = IntPrompt.ask(
                    f"Select purpose category (1-{len(purposes)})",
                    default=len(purposes)  # Default to last one (usually Custom Exploration)
                )
                
                if 1 <= purpose_choice <= len(purposes):
                    purpose_category = purposes[purpose_choice - 1].id
        
        # Get current parameters (exclude None values and system-only params)
        current_params = {}
        excluded_params = {"query", "config_file", "output_file", "save_state", "load_state"}
        
        for param, value in self.params.items():
            if value is not None and param not in excluded_params:
                current_params[param] = value
        
        # Estimate complexity and cost based on current parameters
        complexity = "intermediate"  # Default
        cost = "medium"  # Default
        time = "moderate"  # Default
        
        # Simple heuristics for cost/complexity estimation
        models_count = current_params.get("models", 2)
        instructions_count = current_params.get("instructions", 3)
        max_combinations = current_params.get("max_combinations", 10)
        
        if models_count <= 2 and instructions_count <= 2 and max_combinations <= 8:
            complexity = "beginner"
            cost = "low"
            time = "quick"
        elif models_count >= 4 or instructions_count >= 5 or max_combinations >= 20:
            complexity = "advanced"
            cost = "high"
            time = "extended"
        
        # Create the preset
        try:
            preset = self.preset_manager.create_preset_from_parameters(
                name=preset_name,
                description=preset_description,
                purpose_category=purpose_category,
                parameters=current_params,
                complexity_level=complexity,
                estimated_cost=cost,
                estimated_time=time,
                use_cases=[f"Custom configuration for {preset_name.lower()}"]
            )
            
            # Save the preset
            if self.preset_manager.save_custom_preset(preset):
                self.console.print(f"[green]✓ Successfully saved preset: {preset.name}[/green]")
                self.console.print(f"[dim]Preset ID: {preset.id}[/dim]")
                
                # Show preview of saved preset
                self._show_preset_preview(preset.id)
            else:
                self.console.print(f"[red]✗ Failed to save preset: {preset.name}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Error creating preset: {e}[/red]")
    
    def _select_configuration_path(self):
        """
        Configuration path selection (UX Enhancement - Step 2.3)
        Allows users to choose between quick and detailed configuration paths.
        """
        self.console.print("[bold cyan]Configuration Path Selection[/bold cyan]")
        self.console.print("Choose your preferred configuration approach:\n")
        
        # Create table for configuration paths
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", width=3)
        table.add_column("Path", style="bold")
        table.add_column("Description", style="")
        table.add_column("Best For", style="green")
        table.add_column("Time", style="yellow")
        
        paths = [
            {
                "id": 1,
                "name": "🚀 Quick Configuration",
                "description": "Essential parameters only with smart defaults",
                "best_for": "First-time users, standard workflows",
                "time": "2-3 min",
                "complexity": "basic"
            },
            {
                "id": 2, 
                "name": "⚙️ Detailed Configuration",
                "description": "Full parameter control with advanced options",
                "best_for": "Power users, custom requirements",
                "time": "5-8 min",
                "complexity": "advanced"
            },
            {
                "id": 3,
                "name": "🔧 Expert Configuration", 
                "description": "All options visible, maximum control",
                "best_for": "ISEE experts, research scenarios",
                "time": "8-12 min",
                "complexity": "expert"
            }
        ]
        
        for path in paths:
            table.add_row(
                str(path["id"]),
                path["name"],
                path["description"], 
                path["best_for"],
                path["time"]
            )
        
        self.console.print(table)
        self.console.print()
        
        # Get user selection
        while True:
            choice = Prompt.ask(
                "Select configuration path (1-3, or 0 to use defaults)",
                default="1"
            )
            
            if choice == "0":
                # Use defaults - quick path
                self.configuration_path = "quick"
                self.complexity_level = "basic"
                self.console.print("[green]Using Quick Configuration with smart defaults[/green]")
                break
            elif choice in ["1", "2", "3"]:
                selected_path = paths[int(choice) - 1]
                self.configuration_path = "detailed" if choice in ["2", "3"] else "quick"
                self.complexity_level = selected_path["complexity"]
                
                # Set advanced options visibility based on selection
                if choice == "2":
                    self.show_advanced_options = True
                elif choice == "3":
                    self.show_advanced_options = True
                    # Expert mode - show everything
                    
                self.console.print(f"[green]✓ Selected: {selected_path['name']}[/green]")
                if choice in ["2", "3"]:
                    self.console.print("[dim]Advanced options will be available throughout the wizard[/dim]")
                break
            else:
                self.console.print("[red]Please enter 1, 2, 3, or 0[/red]")
        
        self.console.print()
    
    def _categorize_parameters(self):
        """
        Categorize parameters by complexity level for progressive disclosure.
        Returns dict with parameter categories.
        """
        return {
            "basic": [
                "query", "domain", "models", "instructions", "output_format"
            ],
            "intermediate": [
                "variations", "max_combinations", "sampling_method", 
                "balanced_models", "use_ollama", "simulate"
            ],
            "advanced": [
                "generate_reports", "analyze_results", "synthesize_method",
                "instruction_templates", "dry_run", "output_file"
            ],
            "expert": [
                "save_state", "load_state", "domain_config"
            ]
        }
    
    def _should_show_parameter(self, param_name: str) -> bool:
        """
        Determine if a parameter should be shown based on current complexity level.
        """
        categories = self._categorize_parameters()
        
        # Always show basic parameters
        if param_name in categories["basic"]:
            return True
            
        # Show intermediate parameters for advanced and expert levels
        if param_name in categories["intermediate"]:
            return self.complexity_level in ["advanced", "expert"]
            
        # Show advanced parameters for advanced and expert levels (if advanced options enabled)
        if param_name in categories["advanced"]:
            return self.complexity_level in ["advanced", "expert"] and self.show_advanced_options
            
        # Show expert parameters only for expert level
        if param_name in categories["expert"]:
            return self.complexity_level == "expert"
            
        # Default to showing the parameter
        return True
    
    def _show_advanced_options_toggle(self):
        """
        Show toggle for advanced options if in appropriate complexity level.
        """
        if self.complexity_level in ["advanced", "expert"] and not self.show_advanced_options:
            self.console.print("\n[dim]💡 Advanced options are available for this configuration level[/dim]")
            show_advanced = Confirm.ask(
                "Would you like to see advanced options?",
                default=False
            )
            if show_advanced:
                self.show_advanced_options = True
                self.console.print("[green]✓ Advanced options enabled[/green]")
            else:
                self.console.print("[dim]Advanced options remain hidden (you can enable them later)[/dim]")
    
    def _select_model_collection(self, step_num: int, preset_models_count: bool = False):
        """OpenRouter-first model selection using curated collections."""
        self.console.print(f"\n[bold cyan]Step {step_num}: Model Selection[/bold cyan]")
        
        # Check if OpenRouter collections are available
        if not (self.api_status["openrouter"] and self.openrouter_collections):
            # Fallback to legacy model selection
            self._legacy_model_selection()
            return
        
        # For expert/advanced mode, offer choice between collections and individual models
        if self.complexity_level in ["advanced", "expert"]:
            self.console.print("\n[bold green]🎯 OpenRouter Selection Mode[/bold green]")
            self.console.print("[cyan]Choose your preferred selection approach:[/cyan]\n")
            
            mode_table = Table(title="Selection Modes")
            mode_table.add_column("#", style="cyan", width=3)
            mode_table.add_column("Mode", style="bold green", width=25)
            mode_table.add_column("Description", style="yellow", width=50)
            
            mode_table.add_row("1", "🏆 Individual Top 20 Models", "Select specific models from OpenRouter's top performers")
            mode_table.add_row("2", "📊 Curated Collections", "Use purpose-optimized model collections (recommended)")
            mode_table.add_row("3", "🔧 Legacy Models", "Traditional model selection (limited providers)")
            
            self.console.print(mode_table)
            
            mode_choice = IntPrompt.ask(
                "\nSelect mode (1-3)",
                default=2,
                show_default=True
            )
            
            if mode_choice == 1:
                self._select_individual_models(preset_models_count)
                return
            elif mode_choice == 3:
                self._legacy_model_selection()
                return
            # Continue with collections mode for choice 2
        
        # Show OpenRouter collections as primary experience
        self.console.print("\n[bold green]🚀 Choose Your Model Collection[/bold green]")
        self.console.print("[cyan]Select a curated collection optimized for your purpose and needs:[/cyan]\n")
        
        # Get recommended collection for user's purpose
        purpose_id = self.selected_purpose.id if self.selected_purpose else "custom_exploration"
        recommended_collection = self.openrouter_collections.get_recommended_collection(purpose_id)
        
        # Build collection options - Always prioritize Top Performers as #1
        collections = []
        
        # Always add Top Performers first (priority positioning)
        top_performers = self.openrouter_collections.get_collection("top_performers")
        if top_performers:
            collections.append(top_performers)
        
        # Add purpose-recommended collection as #2 if different from Top Performers
        if recommended_collection and recommended_collection != top_performers:
            collections.append(recommended_collection)
        
        # Add other popular collections
        for collection_id in ["quick_exploration", "deep_analysis", "creative_innovation", "budget_optimizer"]:
            collection = self.openrouter_collections.get_collection(collection_id)
            if collection and collection not in collections:
                collections.append(collection)
        
        # Create selection table
        collections_table = Table(title="🌟 OpenRouter Model Collections")
        collections_table.add_column("#", style="cyan", width=3)
        collections_table.add_column("Collection", style="bold green", width=18)
        collections_table.add_column("Description", style="yellow", width=45)
        collections_table.add_column("Cost", style="blue", width=10)
        collections_table.add_column("Models", style="magenta", width=8)
        
        for i, collection in enumerate(collections, 1):
            is_recommended = collection == recommended_collection
            is_top_performers = collection.id == "top_performers"
            
            name_display = f"{collection.icon} {collection.name}"
            
            # Show both Top Performers indicator and purpose recommendation
            if is_top_performers:
                name_display += " [bold gold](Top Rated)[/bold gold]"
            if is_recommended and not is_top_performers:
                name_display += " [bold yellow](Recommended)[/bold yellow]"
                
            collections_table.add_row(
                str(i),
                name_display,
                collection.description,
                collection.cost_profile.title(),
                str(collection.expected_model_count)
            )
        
        # Add legacy option
        collections_table.add_row(
            str(len(collections) + 1),
            "🔧 Legacy Models",
            "Use traditional model selection (limited providers)",
            "Mixed",
            "Manual"
        )
        
        self.console.print(collections_table)
        
        # Get user choice
        choice_prompt = f"\nSelect a model collection (1-{len(collections) + 1})"
        choice_prompt += f" [green](default: 1 - Top Performers)[/green]"
        choice_prompt += ": "
        
        while True:
            try:
                choice_input = Prompt.ask(choice_prompt).strip()
                if not choice_input:
                    choice = 1  # Default to Top Performers (now always option 1)
                else:
                    choice = int(choice_input)
                
                if 1 <= choice <= len(collections):
                    selected_collection = collections[choice - 1]
                    self._apply_model_collection(selected_collection, preset_models_count)
                    break
                elif choice == len(collections) + 1:
                    # User chose legacy models
                    self.console.print("\n[yellow]Switching to legacy model selection...[/yellow]")
                    self._legacy_model_selection()
                    break
                else:
                    self.console.print(f"[red]Please enter a number between 1 and {len(collections) + 1}[/red]")
            except ValueError:
                self.console.print("[red]Please enter a valid number[/red]")
    
    def _apply_model_collection(self, collection, preset_models_count: bool = False):
        """Apply the selected model collection settings."""
        self.console.print(f"\n[bold green]✓ Selected: {collection.icon} {collection.name}[/bold green]")
        self.console.print(f"[dim]{collection.description}[/dim]")
        
        # Set models count if not preset
        if not preset_models_count:
            self.params["models"] = collection.expected_model_count
            self.console.print(f"[cyan]→ Models: {collection.expected_model_count}[/cyan]")
        
        # Set OpenRouter filters based on collection specs
        if collection.model_specs:
            openrouter_filters = self._collection_specs_to_filters(collection.model_specs)
            if openrouter_filters:
                self.params["openrouter_filters"] = openrouter_filters
                self.console.print(f"[cyan]→ OpenRouter filters configured for {collection.name}[/cyan]")
        
        # Automatically set OpenRouter config file when collection is selected
        self.params["config_file"] = "openrouter_config.json"
        self.console.print("[cyan]→ OpenRouter configuration file selected automatically[/cyan]")
        
        # Set balanced models based on diversity strategy
        if collection.diversity_strategy in ["provider_and_capability", "maximum_provider_diversity"]:
            self.params["balanced_models"] = True
            self.console.print("[cyan]→ Balanced models: Enabled[/cyan]")
        
        # Show cost optimization info
        cost_profile_info = {
            "budget": "Cost-optimized for maximum value",
            "balanced": "Balanced cost and capability",
            "premium": "Premium models for best quality"
        }
        cost_info = cost_profile_info.get(collection.cost_profile, "Mixed cost profile")
        self.console.print(f"[cyan]→ Cost profile: {cost_info}[/cyan]")
        
    def _collection_specs_to_filters(self, model_specs: List[Dict]) -> Dict[str, Any]:
        """Convert collection model specs to OpenRouter filter format."""
        filters = {}
        
        # Aggregate all specs
        all_providers = set()
        all_capabilities = set()
        all_cost_tiers = set()
        preferred_models = []
        
        for spec in model_specs:
            if "providers" in spec:
                all_providers.update([p.value for p in spec["providers"]])
            if "capabilities" in spec:
                all_capabilities.update([c.value for c in spec["capabilities"]])
            if "cost_tiers" in spec:
                all_cost_tiers.update([ct.value for ct in spec["cost_tiers"]])
            if "preference" in spec:
                preferred_models.append(spec["preference"])
        
        if all_providers:
            filters["providers"] = list(all_providers)
        if all_capabilities:
            filters["capabilities"] = list(all_capabilities)
        if all_cost_tiers:
            filters["cost_tiers"] = list(all_cost_tiers)
        if preferred_models:
            filters["preferred_models"] = preferred_models
            
        return filters
    
    def _legacy_model_selection(self):
        """Legacy model selection for fallback or when OpenRouter unavailable."""
        self.console.print("\n[bold yellow]🔧 Legacy Model Selection[/bold yellow]")
        self.console.print("[dim]Using traditional model selection with limited provider options.[/dim]\n")
        
        # Get models count
        models_input = self._get_parameter_input("models", "How many models would you like to use?", "2")
        
        try:
            models_count = int(models_input) if models_input.strip() else 2
        except ValueError:
            self.console.print("[red]Invalid number, using default of 2[/red]")
            models_count = 2
        
        self.params["models"] = models_count
        
        # Show parameter impact
        if models_count > 3:
            self.console.print(f"[yellow]Note: Using {models_count} models will result in {models_count} times more API calls[/yellow]")
        
        # Ask about model balance
        if models_count > 1 and self._should_show_parameter("balanced_models"):
            balanced_models = self._get_boolean_input(
                "balanced_models", 
                "Would you like to balance models across API providers?", 
                "y"
            )
            self.params["balanced_models"] = balanced_models
        
        # Check for Ollama
        if self.api_status["ollama"] and self._should_show_parameter("use_ollama"):
            use_ollama = self._get_boolean_input(
                "use_ollama", 
                "Would you like to include Ollama models?", 
                "n"
            )
            self.params["use_ollama"] = use_ollama
            
            if use_ollama and "ollama_models" in self.api_status:
                self.console.print("[green]Available Ollama models:[/green]")
                for model in self.api_status["ollama_models"]:
                    self.console.print(f"  • {model}")

    def _select_individual_models(self, preset_models_count: bool = False):
        """Select individual models from OpenRouter's Top 20 performers."""
        self.console.print("\n[bold green]🏆 Individual Top 20 Model Selection[/bold green]")
        self.console.print("[cyan]Select specific models from OpenRouter's highest-performing models:[/cyan]\n")
        
        # Get Top 20 models from the collection
        top_performers = self.openrouter_collections.get_collection("top_performers")
        if not top_performers or not top_performers.model_specs:
            self.console.print("[red]Error: Top performers collection not available[/red]")
            self._legacy_model_selection()
            return
        
        # Extract the specific models list
        specific_models = []
        for spec in top_performers.model_specs:
            if "specific_models" in spec:
                specific_models = spec["specific_models"]
                break
        
        if not specific_models:
            self.console.print("[red]Error: No specific models found in top performers[/red]")
            self._legacy_model_selection()
            return
        
        # Create model information with cost estimates and providers
        model_info = []
        for model_id in specific_models:
            provider = model_id.split('/')[0] if '/' in model_id else "unknown"
            model_name = model_id.split('/')[-1] if '/' in model_id else model_id
            
            # Simplified cost estimates (actual costs would come from OpenRouter API)
            cost_estimate = self._estimate_model_cost(model_id)
            quality_score = self._estimate_model_quality(model_id)
            
            model_info.append({
                "id": model_id,
                "name": model_name,
                "provider": provider.title(),
                "cost": cost_estimate,
                "quality": quality_score
            })
        
        # Display models in a rich table with selection interface
        models_table = Table(title="🌟 Top 20 OpenRouter Models", show_header=True, header_style="bold blue")
        models_table.add_column("Select", style="green", width=6)
        models_table.add_column("#", style="cyan", width=3)
        models_table.add_column("Model", style="bold white", width=25)
        models_table.add_column("Provider", style="yellow", width=12)
        models_table.add_column("Cost/1M", style="blue", width=10)
        models_table.add_column("Quality", style="magenta", width=8)
        
        for i, model in enumerate(model_info, 1):
            models_table.add_row(
                "☐",  # Selection checkbox placeholder
                str(i),
                model["name"],
                model["provider"],
                model["cost"],
                f"{model['quality']}/10"
            )
        
        self.console.print(models_table)
        
        # Instructions for selection
        self.console.print("\n[bold cyan]Selection Instructions:[/bold cyan]")
        self.console.print("• Enter model numbers separated by commas (e.g., 1,3,5,7)")
        self.console.print("• Enter ranges with dashes (e.g., 1-5 for models 1 through 5)")
        self.console.print("• Combine both (e.g., 1,3,7-10)")
        self.console.print("• Enter 'all' to select all models")
        self.console.print("• Press Enter for top 3 models (recommended)\n")
        
        # Get user selection
        selection_input = Prompt.ask(
            "Select models",
            default="1,2,3"
        ).strip()
        
        selected_indices = self._parse_model_selection(selection_input, len(model_info))
        
        if not selected_indices:
            self.console.print("[red]No valid models selected, using default top 3[/red]")
            selected_indices = [1, 2, 3]
        
        # Apply selection
        selected_models = [model_info[i-1] for i in selected_indices if 1 <= i <= len(model_info)]
        
        if not selected_models:
            self.console.print("[red]Error in model selection, using default[/red]")
            selected_models = model_info[:3]
        
        # Configure the selection
        self._apply_individual_model_selection(selected_models, preset_models_count)
    
    def _estimate_model_cost(self, model_id: str) -> str:
        """Estimate cost per 1M tokens for a model (simplified)."""
        # Simplified cost mapping - in production, this would use OpenRouter API
        cost_map = {
            "openai/gpt-4o-mini": "$0.15",
            "google/gemini-2.0-flash": "$0.075",
            "anthropic/claude-3.7-sonnet": "$3.00",
            "google/gemini-2.5-pro-preview": "$1.25",
            "anthropic/claude-sonnet-4": "$3.00",
            "deepseek/deepseek-v3-0324-free": "Free",
            "google/gemini-2.5-flash-preview-04-17": "$0.075",
            "deepseek/deepseek-v3-0324": "$0.27",
            "google/gemini-2.5-flash-preview-05-20": "$0.075",
            "openai/gpt-4.1": "$5.00",
            "deepseek/r1-free": "Free",
            "meta-llama/llama-3.3-70b-instruct": "$0.27",
            "mistralai/mistral-nemo": "$0.30",
            "google/gemini-2.0-flash-lite": "$0.075",
            "google/gemini-1.5-flash-8b": "$0.075",
            "openai/gpt-4.1-mini": "$0.60",
            "google/gemini-2.5-flash-preview-05-20-thinking": "$0.075",
            "anthropic/claude-3.5-sonnet": "$3.00",
            "google/gemini-1.5-flash": "$0.075",
            "anthropic/claude-3.7-sonnet-thinking": "$3.00"
        }
        return cost_map.get(model_id, "$0.50")
    
    def _estimate_model_quality(self, model_id: str) -> float:
        """Estimate quality score for a model (simplified)."""
        # Simplified quality mapping based on OpenRouter rankings
        quality_map = {
            "openai/gpt-4o-mini": 9.2,
            "google/gemini-2.0-flash": 9.1,
            "anthropic/claude-3.7-sonnet": 9.0,
            "google/gemini-2.5-pro-preview": 8.9,
            "anthropic/claude-sonnet-4": 8.9,
            "deepseek/deepseek-v3-0324-free": 8.8,
            "google/gemini-2.5-flash-preview-04-17": 8.7,
            "deepseek/deepseek-v3-0324": 8.6,
            "google/gemini-2.5-flash-preview-05-20": 8.5,
            "openai/gpt-4.1": 8.4,
            "deepseek/r1-free": 8.3,
            "meta-llama/llama-3.3-70b-instruct": 8.2,
            "mistralai/mistral-nemo": 8.1,
            "google/gemini-2.0-flash-lite": 8.0,
            "google/gemini-1.5-flash-8b": 7.9,
            "openai/gpt-4.1-mini": 7.8,
            "google/gemini-2.5-flash-preview-05-20-thinking": 7.7,
            "anthropic/claude-3.5-sonnet": 7.6,
            "google/gemini-1.5-flash": 7.5,
            "anthropic/claude-3.7-sonnet-thinking": 7.4
        }
        return quality_map.get(model_id, 7.0)
    
    def _parse_model_selection(self, selection_input: str, max_models: int) -> List[int]:
        """Parse user input for model selection."""
        if not selection_input:
            return [1, 2, 3]  # Default top 3
        
        if selection_input.lower() == "all":
            return list(range(1, max_models + 1))
        
        indices = []
        parts = selection_input.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                # Handle range (e.g., "1-5")
                try:
                    start, end = map(int, part.split('-'))
                    indices.extend(range(start, end + 1))
                except ValueError:
                    self.console.print(f"[yellow]Invalid range: {part}[/yellow]")
            else:
                # Handle single number
                try:
                    indices.append(int(part))
                except ValueError:
                    self.console.print(f"[yellow]Invalid number: {part}[/yellow]")
        
        # Remove duplicates and sort
        unique_indices = sorted(list(set(indices)))
        
        # Filter valid indices
        valid_indices = [i for i in unique_indices if 1 <= i <= max_models]
        
        return valid_indices
    
    def _apply_individual_model_selection(self, selected_models: List[Dict], preset_models_count: bool = False):
        """Apply the individual model selection."""
        self.console.print(f"\n[bold green]✓ Selected {len(selected_models)} Individual Models[/bold green]")
        
        # Display selected models
        for i, model in enumerate(selected_models, 1):
            self.console.print(f"[cyan]{i}. {model['name']} ({model['provider']}) - {model['cost']}/1M - Quality: {model['quality']}/10[/cyan]")
        
        # Set models count if not preset
        if not preset_models_count:
            self.params["models"] = len(selected_models)
            self.console.print(f"[cyan]→ Models count: {len(selected_models)}[/cyan]")
        
        # Create specific model filters for OpenRouter
        model_ids = [model["id"] for model in selected_models]
        openrouter_filters = {
            "specific_models": model_ids,
            "allow_any_from_list": True
        }
        
        self.params["openrouter_filters"] = openrouter_filters
        self.console.print("[cyan]→ OpenRouter specific model filters configured[/cyan]")
        
        # Automatically set OpenRouter config file
        self.params["config_file"] = "openrouter_config.json"
        self.console.print("[cyan]→ OpenRouter configuration file selected automatically[/cyan]")
        
        # Enable balanced models for provider diversity if multiple models
        if len(selected_models) > 1:
            self.params["balanced_models"] = True
            self.console.print("[cyan]→ Balanced models: Enabled for provider diversity[/cyan]")
        
        # Show cost estimate
        total_estimated_cost = self._calculate_selection_cost(selected_models)
        self.console.print(f"[cyan]→ Estimated cost profile: {total_estimated_cost}[/cyan]")
    
    def _calculate_selection_cost(self, selected_models: List[Dict]) -> str:
        """Calculate cost profile for selected models."""
        free_models = sum(1 for model in selected_models if model["cost"] == "Free")
        
        if free_models == len(selected_models):
            return "Free"
        elif free_models > len(selected_models) // 2:
            return "Budget-friendly"
        else:
            costs = []
            for model in selected_models:
                if model["cost"] != "Free":
                    try:
                        cost_val = float(model["cost"].replace("$", ""))
                        costs.append(cost_val)
                    except ValueError:
                        pass
            
            if costs:
                avg_cost = sum(costs) / len(costs)
                if avg_cost < 1.0:
                    return "Budget"
                elif avg_cost < 3.0:
                    return "Balanced"
                else:
                    return "Premium"
            return "Mixed"

    def _configure_openrouter_filters(self):
        """Configure OpenRouter model categorization filters."""
        if not self.openrouter_categorizer:
            return
            
        self.console.print("\n[bold cyan]OpenRouter Model Filtering[/bold cyan]")
        self.console.print("Configure filters to select specific types of models from 300+ available OpenRouter models.\n")
        
        # Ask if user wants to use filters
        use_filters = Confirm.ask(
            "Would you like to filter OpenRouter models by capabilities, cost, or provider?",
            default=False
        )
        
        if not use_filters:
            return
            
        filters = {}
        
        # Provider filtering
        if Confirm.ask("Filter by provider? (Anthropic, OpenAI, Google, Meta, etc.)", default=False):
            provider_options = ["anthropic", "openai", "google", "meta-llama", "mistralai", "cohere", "ai21"]
            self.console.print("\nAvailable providers:")
            for i, provider in enumerate(provider_options, 1):
                self.console.print(f"{i}. {provider.replace('-', ' ').title()}")
            
            provider_input = Prompt.ask(
                "Enter provider numbers (comma-separated) or provider names",
                default=""
            )
            
            if provider_input.strip():
                if provider_input.replace(',', '').replace(' ', '').isdigit():
                    # Numbers provided
                    indices = [int(x.strip()) - 1 for x in provider_input.split(',') if x.strip().isdigit()]
                    selected_providers = [provider_options[i] for i in indices if 0 <= i < len(provider_options)]
                else:
                    # Names provided
                    selected_providers = [p.strip().lower() for p in provider_input.split(',') if p.strip()]
                
                if selected_providers:
                    filters["providers"] = selected_providers
                    self.console.print(f"[green]Selected providers: {', '.join(selected_providers)}[/green]")
        
        # Capability filtering
        if Confirm.ask("Filter by capabilities? (reasoning, coding, fast, creative, etc.)", default=False):
            capability_options = ["reasoning", "coding", "creative", "fast", "large_context", "analysis", "multimodal"]
            self.console.print("\nAvailable capabilities:")
            for i, capability in enumerate(capability_options, 1):
                self.console.print(f"{i}. {capability.replace('_', ' ').title()}")
            
            capability_input = Prompt.ask(
                "Enter capability numbers (comma-separated) or capability names",
                default=""
            )
            
            if capability_input.strip():
                if capability_input.replace(',', '').replace(' ', '').isdigit():
                    # Numbers provided
                    indices = [int(x.strip()) - 1 for x in capability_input.split(',') if x.strip().isdigit()]
                    selected_capabilities = [capability_options[i] for i in indices if 0 <= i < len(capability_options)]
                else:
                    # Names provided
                    selected_capabilities = [c.strip().lower().replace(' ', '_') for c in capability_input.split(',') if c.strip()]
                
                if selected_capabilities:
                    filters["capabilities"] = selected_capabilities
                    self.console.print(f"[green]Selected capabilities: {', '.join(selected_capabilities)}[/green]")
        
        # Cost tier filtering
        if Confirm.ask("Filter by cost tier? (free, budget, standard, premium)", default=False):
            cost_options = ["free", "budget", "standard", "premium", "premium_plus"]
            self.console.print("\nAvailable cost tiers:")
            for i, cost in enumerate(cost_options, 1):
                self.console.print(f"{i}. {cost.replace('_', ' ').title()}")
            
            cost_input = Prompt.ask(
                "Enter cost tier numbers (comma-separated) or tier names",
                default=""
            )
            
            if cost_input.strip():
                if cost_input.replace(',', '').replace(' ', '').isdigit():
                    # Numbers provided
                    indices = [int(x.strip()) - 1 for x in cost_input.split(',') if x.strip().isdigit()]
                    selected_costs = [cost_options[i] for i in indices if 0 <= i < len(cost_options)]
                else:
                    # Names provided
                    selected_costs = [c.strip().lower().replace(' ', '_') for c in cost_input.split(',') if c.strip()]
                
                if selected_costs:
                    filters["cost_tiers"] = selected_costs
                    self.console.print(f"[green]Selected cost tiers: {', '.join(selected_costs)}[/green]")
        
        # Store filters in params for later use
        if filters:
            self.params["openrouter_filters"] = filters
            self.console.print(f"\n[bold green]OpenRouter filters configured![/bold green]")
            self.console.print("[dim]These filters will be applied when selecting OpenRouter models.[/dim]")
        else:
            self.console.print("[yellow]No filters configured - all OpenRouter models will be available.[/yellow]")
    
    def _offer_openrouter_setup(self):
        """Offer interactive OpenRouter API key setup to users."""
        from rich.panel import Panel
        
        # Create an informative panel about OpenRouter
        openrouter_info = Panel.fit(
            "[bold cyan]🚀 OpenRouter - 42.9x Model Diversity Expansion![/bold cyan]\n\n"
            "Get instant access to [bold green]300+ models[/bold green] from [bold green]50+ providers[/bold green]:\n"
            "• [bold]Latest flagships:[/bold] Claude 3.5 Sonnet, GPT-4, Gemini Pro\n"
            "• [bold]Specialized models:[/bold] Coding, reasoning, creative, fast inference\n"
            "• [bold]Cost optimization:[/bold] Free, budget-friendly, and premium tiers\n"
            "• [bold]Intelligent filtering:[/bold] By provider, capability, cost, use case\n"
            "• [bold]Single API key:[/bold] No need to manage multiple providers\n\n"
            "[yellow]⚡ Perfect for ISEE's combinatorial exploration approach![/yellow]\n"
            "[green]🎯 Maximize cognitive diversity with minimal setup effort![/green]",
            border_style="cyan",
            title="🌟 UNLOCK MAXIMUM MODEL ACCESS"
        )
        
        self.console.print(openrouter_info)
        
        # Ask if user wants to set up OpenRouter
        setup_openrouter = Confirm.ask(
            "\n[bold cyan]Would you like to set up OpenRouter access now? (Recommended)[/bold cyan]",
            default=True
        )
        
        if setup_openrouter:
            self._setup_openrouter_api_key()
    
    def _setup_openrouter_api_key(self):
        """Interactive OpenRouter API key setup process."""
        self.console.print("\n[bold green]🔧 OpenRouter Setup Guide[/bold green]")
        
        # Step 1: Guide to getting API key
        self.console.print("\n[bold cyan]Step 1: Get Your OpenRouter API Key[/bold cyan]")
        self.console.print("1. Visit: [link]https://openrouter.ai/keys[/link]")
        self.console.print("2. Sign up or log in to your account")
        self.console.print("3. Create a new API key")
        self.console.print("4. Copy the API key (starts with 'sk-or-...')")
        
        # Offer to open the URL
        open_url = Confirm.ask("\nWould you like me to open the OpenRouter keys page in your browser?", default=True)
        if open_url:
            try:
                import webbrowser
                webbrowser.open("https://openrouter.ai/keys")
                self.console.print("[green]✓ Opened OpenRouter keys page in your browser[/green]")
            except Exception:
                self.console.print("[yellow]Please manually visit: https://openrouter.ai/keys[/yellow]")
        
        self.console.print("\n[bold cyan]Step 2: Enter Your API Key[/bold cyan]")
        
        # Get API key from user
        api_key = Prompt.ask(
            "Paste your OpenRouter API key here",
            password=True,  # Hide the input for security
            default=""
        )
        
        if not api_key:
            self.console.print("[yellow]⏭️ Setup skipped. You can set up OpenRouter later.[/yellow]")
            return False
        
        # Validate API key format
        if not api_key.startswith("sk-or-"):
            self.console.print("[red]⚠️ OpenRouter API keys should start with 'sk-or-'[/red]")
            retry = Confirm.ask("Would you like to try entering the key again?", default=True)
            if retry:
                return self._setup_openrouter_api_key()
            else:
                return False
        
        # Optional: Test the API key
        test_key = Confirm.ask("\nWould you like to test the API key to make sure it works?", default=True)
        if test_key:
            self.console.print("[dim]Testing API key...[/dim]")
            if not self._validate_openrouter_api_key(api_key):
                self.console.print("[red]❌ API key test failed. Please check your key and try again.[/red]")
                retry = Confirm.ask("Would you like to try entering the key again?", default=True)
                if retry:
                    return self._setup_openrouter_api_key()
                else:
                    return False
            else:
                self.console.print("[green]✅ API key test successful![/green]")
        
        # Step 3: Choose how to store the key
        self.console.print("\n[bold cyan]Step 3: Choose Storage Method[/bold cyan]")
        storage_options = [
            "Set for this session only (temporary)",
            "Set environment variable for this terminal session", 
            "Show commands to permanently set the environment variable"
        ]
        
        self.console.print("How would you like to store your API key?")
        for i, option in enumerate(storage_options, 1):
            self.console.print(f"{i}. {option}")
        
        choice = IntPrompt.ask(
            "Enter your choice (1-3)",
            choices=["1", "2", "3"],
            default=1
        )
        
        if choice == 1:
            # Temporary - just set it for this session
            os.environ["OPENROUTER_API_KEY"] = api_key
            self.console.print("[green]✓ OpenRouter API key set for this session![/green]")
            
            # Update API status
            self.api_status["openrouter"] = True
            self.api_status["any_api"] = True
            
            self.console.print("[green]🎉 OpenRouter is now available with 300+ models![/green]")
            return True
            
        elif choice == 2:
            # Set for terminal session
            os.environ["OPENROUTER_API_KEY"] = api_key
            self.console.print("[green]✓ OpenRouter API key set for this terminal session![/green]")
            self.console.print("\n[yellow]To use OpenRouter in future terminal sessions, run:[/yellow]")
            self.console.print(f"[dim]export OPENROUTER_API_KEY=\"{api_key[:12]}...\"[/dim]")
            
            # Update API status
            self.api_status["openrouter"] = True
            self.api_status["any_api"] = True
            
            self.console.print("[green]🎉 OpenRouter is now available with 300+ models![/green]")
            return True
            
        elif choice == 3:
            # Show permanent setup commands
            self.console.print("\n[bold green]Permanent Setup Commands[/bold green]")
            self.console.print("\n[cyan]For bash/zsh (most common):[/cyan]")
            self.console.print(f"[dim]echo 'export OPENROUTER_API_KEY=\"{api_key}\"' >> ~/.bashrc[/dim]")
            self.console.print(f"[dim]echo 'export OPENROUTER_API_KEY=\"{api_key}\"' >> ~/.zshrc[/dim]")
            self.console.print("[dim]source ~/.bashrc  # or ~/.zshrc[/dim]")
            
            self.console.print("\n[cyan]For fish shell:[/cyan]")
            self.console.print(f"[dim]set -Ux OPENROUTER_API_KEY \"{api_key}\"[/dim]")
            
            self.console.print("\n[cyan]For this session:[/cyan]")
            self.console.print(f"[dim]export OPENROUTER_API_KEY=\"{api_key}\"[/dim]")
            
            # Ask if they want to set it for this session too
            set_now = Confirm.ask("\nWould you like to also set it for this session now?", default=True)
            if set_now:
                os.environ["OPENROUTER_API_KEY"] = api_key
                self.api_status["openrouter"] = True
                self.api_status["any_api"] = True
                self.console.print("[green]✓ OpenRouter is now available for this session![/green]")
                return True
        
        return False
    
    def _validate_openrouter_api_key(self, api_key: str) -> bool:
        """Validate an OpenRouter API key by making a test request."""
        try:
            from model_api_integration import OpenRouterClient
            
            # Create a temporary client with the provided key
            temp_client = OpenRouterClient(api_key=api_key)
            
            # Try to get the models list as a validation
            models = temp_client.get_available_models()
            
            # If we get here without exception, the key works
            return len(models) > 0
            
        except Exception as e:
            # Key validation failed
            self.console.print(f"[red]❌ API key validation failed: {str(e)}[/red]")
            return False
    
    def main(self):
        """Main entry point for the command wizard."""
        # Welcome message
        self.console.print("[bold green]ISEE Command Construction Wizard[/bold green]")
        self.console.print("This wizard helps you construct and run valid ISEE commands.\n")
        
        # Show API availability status with prominent OpenRouter promotion
        api_providers = []
        if self.api_status["anthropic"]:
            api_providers.append("Anthropic")
        if self.api_status["openai"]:
            api_providers.append("OpenAI")
        if self.api_status["google"]:
            api_providers.append("Google")
        if self.api_status["openrouter"]:
            api_providers.append("OpenRouter (300+ models)")
        if self.api_status["ollama"]:
            api_providers.append("Ollama")
            
        if api_providers:
            self.console.print(f"[green]Available API providers:[/green] {', '.join(api_providers)}")
            
            # Prominently highlight OpenRouter if not configured but available
            if not self.api_status["openrouter"] and self.openrouter_categorizer:
                self.console.print("\n[bold yellow]⚡ EXPAND YOUR MODEL ACCESS![/bold yellow]")
                self.console.print("[cyan]OpenRouter provides 42.9x more model diversity with 300+ models from 50+ providers![/cyan]")
                self._offer_openrouter_setup()
        else:
            self.console.print("[yellow]No API keys detected. Consider setting API keys or using simulation mode.[/yellow]")
            
            # Offer OpenRouter as primary solution when no APIs are available
            if self.openrouter_categorizer:
                self.console.print("\n[bold cyan]🚀 RECOMMENDED: Start with OpenRouter![/bold cyan]")
                self.console.print("[cyan]Get instant access to 300+ models from all major providers with one API key![/cyan]")
                self._offer_openrouter_setup()
        
        self.console.print()
        
        # Show help option
        self.console.print("[dim]You can type 'help' at any parameter prompt to see detailed information.[/dim]")
        self.console.print("[dim]Type 'help all' to see information about all parameters.[/dim]\n")
        
        # Step 0.5: Configuration Path Selection (UX Enhancement - Step 2.3)
        self._select_configuration_path()
        
        # Step 1: Purpose Selection (UX Enhancement - Step 2.1)
        selected_purpose_id = self._select_purpose()
        
        # Step 1.5: Preset Selection (UX Enhancement - Step 2.2)
        selected_preset_id = self._select_preset(selected_purpose_id)
        
        # Step 2: Query
        step_num = 2 if (selected_purpose_id or selected_preset_id) else 1
        self.console.print(f"[bold cyan]Step {step_num}: Query[/bold cyan]")
            
        # Get query input using our reusable function
        query = self._get_parameter_input("query", "Enter your query")
        self.params["query"] = query if query else None
        
        # Auto-display all available parameters after query entry
        if query:  # Only show if a query was entered
            self.console.print("\n[bold green]Available Parameters Overview[/bold green]")
            self.console.print("[dim]Below are all parameters you can configure for your query:[/dim]\n")
            
            # Use the existing _show_all_parameters_help function
            self._show_all_parameters_help()
        
        # Use unified configuration (automatic)
        config_file = self._get_default_config_file()
        if config_file:
            self.params["config_file"] = config_file
        
        # Domain selection (skip if purpose already set domain)
        step_num += 1
        if not self.params.get("domain"):  # Only show domain selection if not set by purpose
            self._select_domain(step_num)
        else:
            # Domain already set by purpose selection
            self.console.print(f"\n[green]Domain already set by purpose: {self.params['domain']}[/green]")
        # Instruction template selection - Always show cognitive frameworks (Step 3.1 enhancement)
        step_num += 1
        if not self.selected_purpose or not self.selected_purpose.recommended_params.get("instructions"):
            # No preset instructions - full selection
            self.select_instruction_templates(step_num)
        else:
            # Preset instructions - show educational cognitive frameworks overview
            self.console.print(f"\n[green]Instruction templates count set by purpose: {self.params.get('instructions', 'auto')}[/green]")
            
            # Always show cognitive framework education (Step 3.1 enhancement)
            if FRAMEWORK_VISUALIZER_AVAILABLE and self.framework_visualizer:
                self.console.print(f"\n[bold cyan]Step {step_num}: Understanding Cognitive Frameworks[/bold cyan]")
                self.console.print("[dim]Learn about the AI thinking approaches being used in your analysis:[/dim]\n")
                
                # Show cognitive diversity explanation
                self.framework_visualizer.display_cognitive_diversity_explanation()
                
                # Display frameworks overview based on complexity level
                if self.complexity_level == "basic":
                    self.framework_visualizer.display_frameworks_overview("basic")
                    self.console.print("[dim]💡 More frameworks available in Advanced/Expert modes[/dim]\n")
                elif self.complexity_level == "advanced":
                    self.framework_visualizer.display_frameworks_overview("advanced")
                    
                    # Show toggle for all frameworks
                    show_all = Confirm.ask("Show all frameworks (including expert level)?", default=False)
                    if show_all:
                        self.framework_visualizer.display_frameworks_overview("all")
                else:  # expert
                    self.framework_visualizer.display_frameworks_overview("all")
                
                # Offer interactive exploration
                explore = Confirm.ask("\n[bold yellow]Would you like to explore frameworks interactively?[/bold yellow]", default=False)
                if explore:
                    self._interactive_framework_exploration()
        # Models selection - OpenRouter-First Experience (Stage 3)
        step_num += 1
        if not self.selected_purpose or not self.selected_purpose.recommended_params.get("models"):
            self._select_model_collection(step_num)
        else:
            # Models already set by purpose selection - still offer OpenRouter collections
            self.console.print(f"\n[green]Models count set by purpose: {self.params.get('models', 'auto')}[/green]")
            
            # Still offer OpenRouter collections even if models count is preset
            if self.api_status["openrouter"] and self.openrouter_collections:
                self.console.print("\n[bold green]🌟 Enhance with OpenRouter Model Collections![/bold green]")
                self.console.print("[cyan]Choose curated model collections optimized for your purpose.[/cyan]")
                
                enhance_with_openrouter = Confirm.ask(
                    "\n[bold cyan]Would you like to select an OpenRouter model collection?[/bold cyan]", 
                    default=True
                )
                
                if enhance_with_openrouter:
                    self._select_model_collection(step_num, preset_models_count=True)
        # Variations (intermediate parameter)
        step_num += 1
        if (not self.selected_purpose or not self.selected_purpose.recommended_params.get("variations")) and self._should_show_parameter("variations"):
            self.console.print(f"\n[bold cyan]Step {step_num}: Variations[/bold cyan]")
            
            # Get variations count using our reusable function that handles special commands
            variations_input = self._get_parameter_input("variations", "How many variations would you like for each instruction?", "2")
            
            # Convert to integer after handling any special commands
            try:
                variations_count = int(variations_input) if variations_input.strip() else 2
            except ValueError:
                self.console.print("[red]Invalid number, using default of 2[/red]")
                variations_count = 2
                    
            self.params["variations"] = variations_count
            
            # Show total combinations
            models = self.params["models"]
            instructions = self.params["instructions"]
            variations = variations_count
            total_combinations = models * instructions * variations
            
            self.console.print(f"[cyan]Total combinations:[/cyan] {total_combinations}")
            
            if total_combinations > 50:
                self.console.print(f"[yellow]Note: {total_combinations} combinations may result in significant API costs and execution time.[/yellow]")
                self.console.print("[yellow]Consider using --quick mode or setting --max-combinations.[/yellow]")
        else:
            # Variations already set by purpose selection
            self.console.print(f"\n[green]Variations count set by purpose: {self.params.get('variations', 'auto')}[/green]")
        # Sampling method (intermediate parameter)
        step_num += 1
        if (not self.selected_purpose or not self.selected_purpose.recommended_params.get("sampling_method")) and self._should_show_parameter("sampling_method"):
            self.console.print(f"\n[bold cyan]Step {step_num}: Sampling Method[/bold cyan]")
            
            # Use our reusable selection input function
            sampling_options = ["exhaustive", "random", "stratified"]
            descriptions = [
                "Try all combinations", 
                "Randomly sample combinations", 
                "Ensure representative sample"
            ]
            
            sampling_choice_idx = self._get_selection_input(
                "sampling_method",
                "Select a sampling method",
                sampling_options,
                descriptions,
                "1"
            )
            
            self.params["sampling_method"] = sampling_options[sampling_choice_idx]
            
            # Ask for max combinations if not using exhaustive sampling
            if sampling_options[sampling_choice_idx] == "random":
                # Get max combinations input using our reusable function
                max_combinations_input = self._get_parameter_input(
                    "max_combinations", 
                    "Maximum number of combinations to run", 
                    "20"
                )
                
                # Convert to integer
                try:
                    max_combinations = int(max_combinations_input) if max_combinations_input.strip() else 20
                except ValueError:
                    self.console.print("[red]Invalid number, using default of 20[/red]")
                    max_combinations = 20
                
                self.params["max_combinations"] = max_combinations
                
            elif sampling_options[sampling_choice_idx] == "stratified":
                # Get max combinations input using our reusable function
                max_combinations_input = self._get_parameter_input(
                    "max_combinations", 
                    "Maximum number of combinations to run", 
                    "36"
                )
                
                # Convert to integer
                try:
                    max_combinations = int(max_combinations_input) if max_combinations_input.strip() else 36
                except ValueError:
                    self.console.print("[red]Invalid number, using default of 36[/red]")
                    max_combinations = 36
                
                self.params["max_combinations"] = max_combinations
            else:
                self.console.print("[yellow]Invalid selection. Using default (exhaustive).[/yellow]")
                self.params["sampling_method"] = "exhaustive"
        else:
            print(f"\nStep {step_num}: Sampling Method")
            
            # Use our reusable selection input function
            sampling_options = ["exhaustive", "random", "stratified"]
            descriptions = [
                "Try all combinations", 
                "Randomly sample combinations", 
                "Ensure representative sample"
            ]
            
            sampling_choice_idx = self._get_selection_input(
                "sampling_method",
                "Select a sampling method",
                sampling_options,
                descriptions,
                "1"
            )
            
            self.params["sampling_method"] = sampling_options[sampling_choice_idx]
            
            # Ask for max combinations if not using exhaustive sampling
            if sampling_options[sampling_choice_idx] == "random":
                # Get max combinations input using our reusable function
                max_combinations_input = self._get_parameter_input(
                    "max_combinations", 
                    "Maximum number of combinations to run", 
                    "20"
                )
                
                # Convert to integer
                try:
                    max_combinations = int(max_combinations_input) if max_combinations_input.strip() else 20
                except ValueError:
                    print("Invalid number, using default of 20")
                    max_combinations = 20
                
                self.params["max_combinations"] = max_combinations
                
            elif sampling_options[sampling_choice_idx] == "stratified":
                # Get max combinations input using our reusable function
                max_combinations_input = self._get_parameter_input(
                    "max_combinations", 
                    "Maximum number of combinations to run", 
                    "36"
                )
                
                # Convert to integer
                try:
                    max_combinations = int(max_combinations_input) if max_combinations_input.strip() else 36
                except ValueError:
                    print("Invalid number, using default of 36")
                    max_combinations = 36
                
                self.params["max_combinations"] = max_combinations
        # else:
        #     # Sampling method already set by purpose selection
        #         self.console.print(f"\n[green]Sampling method set by purpose: {self.params.get('sampling_method', 'auto')}[/green]")
        #     else:
        #         print(f"\nSampling method set by purpose: {self.params.get('sampling_method', 'auto')}")
        
        # Output options
        step_num += 1
        self.console.print(f"\n[bold cyan]Step {step_num}: Output Options[/bold cyan]")
            
        # Use our reusable selection input function for output format
        format_options = ["markdown", "json", "text"]
        descriptions = [
            "Format results as Markdown", 
            "Format results as JSON", 
            "Format results as plain text"
        ]
            
        format_choice_idx = self._get_selection_input(
            "output_format",
            "Select an output format",
            format_options,
            descriptions,
            "1"
        )
            
        self.params["output_format"] = format_options[format_choice_idx]
            
        # Generate reports - use our reusable boolean input function
        generate_reports = self._get_boolean_input(
            "generate_reports",
            "Generate summary reports?",
            "y"
        )
        self.params["generate_reports"] = generate_reports
            
        # Analyze results - use our reusable boolean input function
        if generate_reports:
            analyze_results = self._get_boolean_input(
                "analyze_results",
                "Analyze results (generate charts and metrics)?",
                "y"
            )
            self.params["analyze_results"] = analyze_results
            
        # Dry run - use our reusable boolean input function
        dry_run = self._get_boolean_input(
            "dry_run",
            "Run in dry-run mode (show but don't execute)?",
            "n"
        )
        self.params["dry_run"] = dry_run
            
        # Simulate - use our reusable boolean input function (intermediate parameter)
        if not dry_run and self._should_show_parameter("simulate"):
            simulate = self._get_boolean_input(
                "simulate",
                "Simulate responses (don't call actual APIs)?",
                "n"
            )
            self.params["simulate"] = simulate
        # Show advanced options toggle if applicable
        if self.complexity_level in ["advanced", "expert"]:
            self._show_advanced_options_toggle()
        
        # Advanced options (only show if appropriate for complexity level)
        if self.complexity_level in ["advanced", "expert"] or self.show_advanced_options:
            step_num += 1
            self.configure_advanced_options(step_num)
        else:
            # Quick configuration - skip advanced options but show what's available
            if self.complexity_level == "basic":
                self.console.print(f"\n[dim]⚡ Quick Configuration: Advanced options skipped (variations: {self.params.get('variations', 2)}, sampling: {self.params.get('sampling_method', 'exhaustive')})[/dim]")
        
        # Update the cost estimate with final parameters (UX Enhancement - Step 1.1)
        if COST_ESTIMATION_AVAILABLE and self.cost_estimator:
            self._update_cost_estimate()
        
        # Preview the command
        self.preview_command()
        
        # Check if the user wants to run the command
        # Generate and validate the command one more time before running
        command = self.generate_command()
        command_validation = self.validate_command(command)
            
        # If command is valid or user wants to proceed with warnings
        if command and (command_validation["valid"] or Confirm.ask(
                "Command has warnings. Run anyway?",
                default=False
            )):
                
            # Update cost estimate before final confirmation
            if COST_ESTIMATION_AVAILABLE and self.cost_estimator:
                self._update_cost_estimate()
                self._display_cost_estimate()
                
            run_command = Confirm.ask(
                "Run this command?",
                default=True
            )
                
            if run_command:
                # Check if we need to show cost warning
                show_cost_warning = False
                    
                # Use cost estimator if available (UX Enhancement - Step 1.1)
                if COST_ESTIMATION_AVAILABLE and self.cost_estimator and self.current_cost_estimate:
                    # If cost warning level is high or very high, show warning
                    if self.current_cost_estimate.get("cost_warning_level") in ["high", "very_high"]:
                        warning_message = self.cost_estimator.get_warning_message(self.current_cost_estimate)
                        if warning_message:
                            self.console.print(f"[bold yellow]Warning:[/bold yellow] {warning_message}")
                            show_cost_warning = True
                # Fallback to simple combination check if cost estimator not available
                elif not self.params.get("simulate"):
                    models = self.params.get("models", 2)
                    instructions = self.params.get("instructions", 3)
                    variations = self.params.get("variations", 2)
                    total_combinations = models * instructions * variations
                        
                    if total_combinations > 36:
                        self.console.print(f"[bold yellow]Warning:[/bold yellow] Running {total_combinations} combinations with real API calls may result in significant costs.")
                        show_cost_warning = True
                    
                # Ask for confirmation if there was a cost warning
                if show_cost_warning:
                    cost_confirm = Confirm.ask(
                        "Are you sure you want to continue?",
                        default=True
                    )
                    if not cost_confirm:
                        self.console.print("[yellow]Command execution cancelled by user.[/yellow]")
                        return
                    
                # Execute the command with error recovery
                command_executed = False
                while not command_executed:
                    # Execute command with error handling
                    success, result, error = self.execute_command(command)
                        
                    if success:
                        command_executed = True
                    elif error == "parameters_need_modification":
                        # Guide user through parameter reconfiguration
                        self.reconfigure_parameters()
                            
                        # Regenerate and preview the command
                        command = self.generate_command()
                        if not command:
                            self.console.print("[yellow]Command generation failed after reconfiguration.[/yellow]")
                            break
                                
                        self.preview_command()
                            
                        # Confirm before re-running
                        retry = Confirm.ask("Run with new parameters?", default=True)
                        if not retry:
                            self.console.print("[yellow]Command execution cancelled by user.[/yellow]")
                            break
                    else:
                        # Execution aborted or other terminal error
                        command_executed = True
            else:
                # Show additional options
                self._show_help_options()
        else:
            # Show additional options if command validation failed
            self._show_help_options()
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="ISEE Command Construction Wizard")
    parser.add_argument("--version", action="store_true", help="Show version information and exit")
    args = parser.parse_args()
    
    if args.version:
        print("ISEE Command Wizard v1.2.0")
        print("Part of the ISEE Meta-Framework for LLM evaluation")
        sys.exit(0)
    
    # Create and run the wizard
    wizard = CommandWizard()
    wizard.main()