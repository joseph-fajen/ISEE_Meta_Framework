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

try:
    # Try to import rich for enhanced terminal output
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.table import Table
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Note: For an enhanced experience, install rich: pip install rich")

# Import components from the ISEE framework
try:
    from domain_manager import DomainManager, Domain, create_default_domains
    from instruction_templates import TemplateLibrary, create_default_library
    from model_api_integration import ModelAPIFactory
except ImportError as e:
    print(f"Error importing ISEE components: {str(e)}")
    print("Make sure you're running this script from the ISEE framework directory.")
    sys.exit(1)

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
        if "anthropic" in error_str.lower():
            provider = "Anthropic"
        elif "openai" in error_str.lower():
            provider = "OpenAI"
        elif "google" in error_str.lower():
            provider = "Google"
        
        return EnvironmentError(
            "ENV-001",
            f"Missing or invalid API key{f' for {provider}' if provider else ''}",
            {"command": command, "provider": provider, "error": error_str},
            [
                f"Check that you have set the {'ANTHROPIC_API_KEY' if provider == 'Anthropic' else 'OPENAI_API_KEY' if provider == 'OpenAI' else 'GOOGLE_API_KEY' if provider == 'Google' else 'required API key'} environment variable",
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
            
        if RICH_AVAILABLE:
            command_wizard.console.print(f"[yellow]The parameter '{param_name}' is required.[/yellow]")
            value = Prompt.ask(f"Please provide a value for {param_name}")
            if value:
                command_wizard.params[param_name] = value
                return True
        else:
            print(f"The parameter '{param_name}' is required.")
            value = input(f"Please provide a value for {param_name}: ")
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
            
        if RICH_AVAILABLE:
            message = "An API key is missing or invalid"
            if provider:
                message = f"The API key for {provider} is missing or invalid"
            
            command_wizard.console.print(f"[yellow]{message}.[/yellow]")
            use_simulation = Confirm.ask("Would you like to switch to simulation mode instead?", default=True)
            if use_simulation:
                command_wizard.params["simulate"] = True
                return True
        else:
            message = "An API key is missing or invalid"
            if provider:
                message = f"The API key for {provider} is missing or invalid"
                
            print(f"{message}.")
            use_simulation = input("Would you like to switch to simulation mode instead? (y/n) [y]: ").lower() in ["", "y", "yes"]
            if use_simulation:
                command_wizard.params["simulate"] = True
                return True
                
        return False
        
    def _recover_ollama_not_running(self, command_wizard):
        if RICH_AVAILABLE:
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
        else:
            print("Ollama is not running or not accessible.")
            print("Options:")
            print("1. Disable Ollama and continue with cloud models only")
            print("2. Switch to simulation mode")
            print("3. Try again after starting Ollama")
            
            try:
                choice = input("What would you like to do? (1-3): ")
                if choice == "1":
                    command_wizard.params["use_ollama"] = False
                    return True
                elif choice == "2":
                    command_wizard.params["simulate"] = True
                    return True
            except ValueError:
                pass
                
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
        if RICH_AVAILABLE:
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
        else:
            print("API rate limit exceeded.")
            print("Options:")
            print("1. Reduce the number of combinations")
            print("2. Switch to simulation mode")
            print("3. Wait and try again")
            
            try:
                choice = input("What would you like to do? (1-3): ")
                if choice == "1":
                    # Guide to reduce combinations
                    current = command_wizard.params.get("max_combinations")
                    if not current:
                        # Calculate current potential combinations
                        models = command_wizard.params.get("models", 2)
                        instructions = command_wizard.params.get("instructions", 3)
                        variations = command_wizard.params.get("variations", 2)
                        total = models * instructions * variations
                        suggested = max(10, total // 2)
                        print(f"Current potential combinations: {total}")
                        print(f"Suggested max: {suggested}")
                        
                        new_max_input = input(f"Set maximum combinations [{suggested}]: ")
                        new_max = int(new_max_input) if new_max_input else suggested
                        command_wizard.params["max_combinations"] = new_max
                        return True
                    else:
                        suggested = max(10, current // 2)
                        new_max_input = input(f"Set maximum combinations [{suggested}]: ")
                        new_max = int(new_max_input) if new_max_input else suggested
                        command_wizard.params["max_combinations"] = new_max
                        return True
                elif choice == "2":
                    command_wizard.params["simulate"] = True
                    return True
                elif choice == "3":
                    print("Waiting to retry...")
                    time.sleep(5)  # Simple wait and retry
                    return True
            except (ValueError, IndexError):
                pass
                
        return False
    
    def _recover_timeout(self, command_wizard):
        # Similar to rate limit recovery but with focus on timeout issues
        if RICH_AVAILABLE:
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
        else:
            # Non-rich version
            # ...
            return self._recover_rate_limit(command_wizard)  # Reuse implementation
                
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
        # Store selected models
        self.selected_models = []
        self.selected_model_names = []
        """Initialize the command wizard."""
        # Initialize console for rich output
        self.console = Console() if RICH_AVAILABLE else None
        
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
    
    def _show_parameter_help(self, param_name: str) -> None:
        """
        Show detailed help for a specific parameter.
        
        Args:
            param_name: The name of the parameter to show help for.
        """
        # Clean up parameter name (replace dashes with underscores)
        clean_param = param_name.replace("-", "_")
        
        if clean_param not in PARAMETER_DESCRIPTIONS:
            if RICH_AVAILABLE:
                self.console.print(f"[yellow]No detailed help available for parameter: {param_name}[/yellow]")
            else:
                print(f"No detailed help available for parameter: {param_name}")
            return

        desc = PARAMETER_DESCRIPTIONS[clean_param]
        
        if RICH_AVAILABLE:
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
        else:
            # Plain text version
            print(f"\nHelp: --{param_name}")
            print(f"{desc['short']}")
            print(f"\n{desc['long']}")
            
            # Show impact
            print(f"\nImpact: {desc['impact']}")
            
            # Show examples if available
            if "examples" in desc and desc["examples"]:
                print("\nExamples:")
                for example in desc["examples"]:
                    print(f"  • {example}")
            
            # Show related parameters
            if "related" in desc and desc["related"]:
                print("\nRelated parameters:")
                for related in desc["related"]:
                    if related in PARAMETER_DESCRIPTIONS:
                        related_display = related.replace("_", "-")
                        print(f"  • --{related_display}: {PARAMETER_DESCRIPTIONS[related]['short']}")
            print()  # Add an empty line at the end
    
    def _show_parameter_context(self, param_name: str, current_value: Any = None) -> None:
        """
        Show contextual information about a parameter when requesting input.
        
        Args:
            param_name: The name of the parameter
            current_value: The current value of the parameter, if any
        """
        if param_name not in PARAMETER_DESCRIPTIONS:
            return
            
        desc = PARAMETER_DESCRIPTIONS[param_name]
        
        if RICH_AVAILABLE:
            # Show brief description with option to get more help
            self.console.print(f"[yellow]{desc['short']}[/yellow]")
            
            # Show current value if there is one
            if current_value is not None:
                self.console.print(f"Current value: [green]{current_value}[/green]")
                
            # Show brief impact statement
            self.console.print(f"Impact: {desc['impact']}")
            
            # Show a hint about getting more help
            self.console.print("[dim](Type 'help' for more detailed information)[/dim]")
        else:
            # Plain text version
            print(f"{desc['short']}")
            
            # Show current value if there is one
            if current_value is not None:
                print(f"Current value: {current_value}")
                
            # Show brief impact statement
            print(f"Impact: {desc['impact']}")
            
            # Show a hint about getting more help
            print("(Type 'help' for more detailed information)")
            
    def _show_all_parameters_help(self) -> None:
        """Show a summary of all available parameters and their descriptions."""
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]All Available Parameters[/bold cyan]")
            
            # Create a table for parameters
            params_table = Table(title="Command Parameters")
            params_table.add_column("Parameter", style="cyan")
            params_table.add_column("Description", style="yellow")
            params_table.add_column("Current Value", style="green")
            
            # Add parameters to table, grouped by category
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
    
    def _detect_apis(self) -> Dict[str, bool]:
        """Detect available API keys and models.
        
        Returns:
            Dictionary of API availability status.
        """
        status = {
            "anthropic": False,
            "openai": False,
            "google": False,
            "ollama": False,
            "any_api": False,
        }
        
        # Check for API keys
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")
        google_key = os.environ.get("GOOGLE_API_KEY")
        
        if anthropic_key:
            status["anthropic"] = True
            status["any_api"] = True
        
        if openai_key:
            status["openai"] = True
            status["any_api"] = True
            
        if google_key:
            status["google"] = True
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
                if RICH_AVAILABLE:
                    self.console.print(f"[green]Loaded domains from {file}[/green]")
                else:
                    print(f"Loaded domains from {file}")
            except Exception as e:
                if RICH_AVAILABLE:
                    self.console.print(f"[yellow]Error loading domains from {file}: {str(e)}[/yellow]")
                else:
                    print(f"Error loading domains from {file}: {str(e)}")
    
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
        
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Configuration File Selection[/bold cyan]")
            
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
        else:
            print("\nConfiguration File Selection")
            print("Available Configuration Files:")
            
            for i, config_file in enumerate(potential_configs, 1):
                description = self._get_config_description(config_file)
                print(f"{i}. {config_file} - {description}")
            
            print("0. No configuration file")
            
            # Ask if the user wants to select a configuration file
            use_config_input = input(f"Would you like to use a configuration file? (y/n) [{'y' if 'unified_config.json' in potential_configs else 'n'}]: ").lower()
            if not use_config_input:
                use_config = "unified_config.json" in potential_configs
            else:
                use_config = use_config_input in ["y", "yes"]
            
            if not use_config:
                return None
            
            # Allow selection of configuration file
            while True:
                try:
                    choice_input = input(f"Select a configuration file by number (or 0 to skip) [{'1' if 'unified_config.json' in potential_configs else '0'}]: ")
                    if not choice_input:
                        choice = 1 if "unified_config.json" in potential_configs else 0
                    else:
                        choice = int(choice_input)
                    
                    if choice == 0:
                        return None
                    
                    if 1 <= choice <= len(potential_configs):
                        selected_config = potential_configs[choice - 1]
                        
                        # Validate the config file
                        if self._validate_config_file(selected_config):
                            return selected_config
                        else:
                            print(f"Warning: {selected_config} does not appear to be a valid ISEE configuration file. It may be missing required model mappings.")
                            use_anyway_input = input("Use this configuration file anyway? (y/n) [n]: ").lower()
                            use_anyway = use_anyway_input in ["y", "yes"]
                            if use_anyway:
                                return selected_config
                    else:
                        print("Invalid selection. Please try again.")
                except ValueError:
                    print("Please enter a number.")
        
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
        
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Additional Command-Line Options[/bold cyan]")
            
            options_table = Table(title="Helpful Options")
            options_table.add_column("Option", style="green")
            options_table.add_column("Description", style="cyan")
            options_table.add_column("Example", style="yellow")
            
            for option in help_info:
                options_table.add_row(option["name"], option["description"], option["usage"])
            
            self.console.print(options_table)
        else:
            print("\nAdditional Command-Line Options:")
            for option in help_info:
                print(f"{option['name']}: {option['description']}")
                print(f"  Example: {option['usage']}")
                print()
    
    def configure_advanced_options(self) -> Dict[str, Any]:
        """Configure advanced options not covered by other steps.
        
        Returns:
            Dictionary of advanced options.
        """
        advanced_params = {}
        
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Advanced Options[/bold cyan]")
            
            # Show parameter context for advanced options
            self._show_parameter_context("advanced_options", self.params.get("advanced_options", {}))
            
            # Domain config
            use_domain_config = Confirm.ask(
                "Would you like to use a domain-specific configuration file?",
                default=False
            )
            
            if use_domain_config:
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
        else:
            print("\nAdvanced Options")
            
            # Show parameter context for advanced options
            self._show_parameter_context("advanced_options", self.params.get("advanced_options", {}))
            
            # Domain config
            use_domain_config_input = input("Would you like to use a domain-specific configuration file? (y/n) [n]: ").lower()
            use_domain_config = use_domain_config_input in ["y", "yes"]
            
            if use_domain_config:
                domain_config_files = [f for f in os.listdir() if f.endswith('.json') and 'domain' in f.lower()]
                if domain_config_files:
                    print("Available domain configuration files:")
                    for i, file in enumerate(domain_config_files, 1):
                        print(f"{i}. {file}")
                    
                    try:
                        domain_config_choice_input = input("Select a domain configuration file by number (or 0 to skip) [0]: ")
                        domain_config_choice = int(domain_config_choice_input) if domain_config_choice_input else 0
                        
                        if domain_config_choice > 0 and domain_config_choice <= len(domain_config_files):
                            advanced_params["domain_config"] = domain_config_files[domain_config_choice - 1]
                    except ValueError:
                        print("Invalid selection. Skipping domain configuration.")
                else:
                    print("No domain configuration files found.")
            
            # Report format
            if self.params["generate_reports"]:
                report_format_choices = ["markdown", "json"]
                print("Report formats:")
                for i, format_name in enumerate(report_format_choices, 1):
                    print(f"{i}. {format_name}")
                
                try:
                    report_format_index_input = input("Select report format [1]: ")
                    report_format_index = int(report_format_index_input) if report_format_index_input else 1
                    
                    if 1 <= report_format_index <= len(report_format_choices):
                        advanced_params["report_format"] = report_format_choices[report_format_index - 1]
                except ValueError:
                    advanced_params["report_format"] = "markdown"  # Default to markdown
            
            # Export CSV
            if self.params["generate_reports"]:
                export_csv_input = input("Export data as CSV files for analysis? (y/n) [n]: ").lower()
                export_csv = export_csv_input in ["y", "yes"]
                advanced_params["export_csv"] = export_csv
            
            # No visualizations
            if self.params["analyze_results"]:
                no_viz_input = input("Skip generating visualization charts? (y/n) [n]: ").lower()
                no_visualizations = no_viz_input in ["y", "yes"]
                advanced_params["no_visualizations"] = no_visualizations
            
            # Quick/Full mode
            use_preset_input = input("Use a preset running mode (quick or full)? (y/n) [n]: ").lower()
            use_preset = use_preset_input in ["y", "yes"]
            
            if use_preset:
                preset_choices = ["quick", "full"]
                preset_names = ["Quick mode (stratified sampling with 36 combinations)", 
                               "Full mode (exhaustive combinations)"]
                
                print("Available presets:")
                for i, (preset, desc) in enumerate(zip(preset_choices, preset_names), 1):
                    print(f"{i}. {desc}")
                
                try:
                    preset_choice_input = input("Select a preset by number [1]: ")
                    preset_choice = int(preset_choice_input) if preset_choice_input else 1
                    
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
                except ValueError:
                    print("Invalid selection. Skipping preset selection.")
        
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
        
        if RICH_AVAILABLE:
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
        else:
            # Display errors
            if validation["errors"]:
                print("\nCommand Validation Errors:")
                for error in validation["errors"]:
                    print(f"- {error}")
            
            # Display warnings
            if validation["warnings"]:
                print("\nCommand Validation Warnings:")
                for warning in validation["warnings"]:
                    print(f"- {warning}")
            
            # Display suggestions
            if validation["suggestions"]:
                print("\nSuggestions for Improvement:")
                for suggestion in validation["suggestions"]:
                    print(f"- {suggestion}")
                    
            # If there are errors, provide a summary
            if not validation["valid"]:
                print("\nCommand cannot be executed due to validation errors.")
                return False
                
            # If there are only warnings, ask the user if they want to continue
            if validation["warnings"]:
                user_input = input("\nContinue despite warnings? (y/n) [y]: ").lower()
                return user_input in ["", "y", "yes"]
            
            return True
    
    def select_instruction_templates(self) -> None:
        """Allow the user to select specific instruction templates."""
        # Get all available templates
        templates = self.template_library.templates
        
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Instruction Template Selection[/bold cyan]")
            
            # Show parameter context
            self._show_parameter_context("instructions", self.params["instructions"])
            
            # Display available templates
            templates_table = Table(title="Available Templates")
            templates_table.add_column("ID", style="green")
            templates_table.add_column("Name", style="cyan")
            templates_table.add_column("Description")
            
            for template in templates:
                templates_table.add_row(template.id, template.name, template.description[:50] + "..." if len(template.description) > 50 else template.description)
            
            self.console.print(templates_table)
            
            # Ask if the user wants to select specific templates
            select_templates = Confirm.ask(
                "Would you like to select specific instruction templates?",
                default=False
            )
            
            if select_templates:
                # Get template selections from user
                selected_templates = []
                while True:
                    template_id = Prompt.ask(
                        "Enter a template ID to include (or leave empty to finish)",
                        default=""
                    )
                    
                    if not template_id:
                        break
                    
                    # Validate the template ID
                    valid_ids = [template.id for template in templates]
                    if template_id in valid_ids:
                        if template_id not in selected_templates:
                            selected_templates.append(template_id)
                            self.console.print(f"Added template: [green]{template_id}[/green]")
                        else:
                            self.console.print(f"[yellow]Template {template_id} is already selected.[/yellow]")
                    else:
                        self.console.print(f"[red]Invalid template ID: {template_id}[/red]")
                
                if selected_templates:
                    # Convert the list to a comma-separated string
                    self.params["instruction_templates"] = ",".join(selected_templates)
                    self.console.print(f"Selected templates: [green]{self.params['instruction_templates']}[/green]")
        else:
            print("\nInstruction Template Selection")
            
            # Show parameter context
            self._show_parameter_context("instructions", self.params["instructions"])
            
            # Display available templates
            print("Available Templates:")
            for template in templates:
                print(f"{template.id}: {template.name} - {template.description[:50] + '...' if len(template.description) > 50 else template.description}")
            
            # Ask if the user wants to select specific templates
            select_templates_input = input("Would you like to select specific instruction templates? (y/n) [n]: ").lower()
            select_templates = select_templates_input in ["y", "yes"]
            
            if select_templates:
                # Get template selections from user
                selected_templates = []
                while True:
                    template_id = input("Enter a template ID to include (or leave empty to finish): ")
                    
                    if not template_id:
                        break
                    
                    # Validate the template ID
                    valid_ids = [template.id for template in templates]
                    if template_id in valid_ids:
                        if template_id not in selected_templates:
                            selected_templates.append(template_id)
                            print(f"Added template: {template_id}")
                        else:
                            print(f"Template {template_id} is already selected.")
                    else:
                        print(f"Invalid template ID: {template_id}")
                
                if selected_templates:
                    # Convert the list to a comma-separated string
                    self.params["instruction_templates"] = ",".join(selected_templates)
                    print(f"Selected templates: {self.params['instruction_templates']}")
    
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
        if self.params["sampling_method"]:
            command_parts.append(f"--sampling-method {self.params['sampling_method']}")
        
        # Add max combinations
        if self.params["max_combinations"]:
            command_parts.append(f"--max-combinations {self.params['max_combinations']}")
        
        # Add use ollama
        if self.params["use_ollama"]:
            command_parts.append("--use-ollama")
        
        # Add balanced models
        if self.params["balanced_models"]:
            command_parts.append("--balanced-models")
        
        # Add output format
        if self.params["output_format"]:
            command_parts.append(f"--output-format {self.params['output_format']}")
        
        # Add output file
        if self.params["output_file"]:
            command_parts.append(f"--output-file \"{self.params['output_file']}\"")
        
        # Add simulate
        if self.params["simulate"]:
            command_parts.append("--simulate")
        
        # Add dry run
        if self.params["dry_run"]:
            command_parts.append("--dry-run")
        
        # Add generate reports
        if self.params["generate_reports"]:
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
        if self.params["save_state"]:
            command_parts.append(f"--save-state \"{self.params['save_state']}\"")
        
        # Add load state
        if self.params["load_state"]:
            command_parts.append(f"--load-state \"{self.params['load_state']}\"")
        
        # Add synthesize method
        if self.params["synthesize_method"]:
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
        if RICH_AVAILABLE:
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
        else:
            # Non-rich interface version
            print("\nParameter Reconfiguration")
            
            # Display current parameters
            print("Current Parameters:")
            for param, value in self.params.items():
                if value is not None:
                    print(f"{param}: {value}")
            
            # Allow user to modify parameters
            while True:
                modify_input = input("Would you like to modify a parameter? (y/n) [y]: ").lower()
                modify = modify_input in ["", "y", "yes"]
                if not modify:
                    break
                    
                # Let user select parameter to modify
                param_choices = list(self.params.keys())
                param_names = [name.replace("_", "-") for name in param_choices]
                
                for i, name in enumerate(param_names, 1):
                    print(f"{i}. {name}")
                    
                try:
                    param_idx_input = input("Select a parameter to modify: ")
                    param_idx = int(param_idx_input)
                    
                    if param_idx < 1 or param_idx > len(param_choices):
                        print("Invalid selection.")
                        continue
                        
                    param_name = param_choices[param_idx-1]
                    current_value = self.params[param_name]
                    
                    # Get new value
                    if isinstance(current_value, bool):
                        new_value_input = input(f"New value for {param_name} (y/n) [{current_value}]: ").lower()
                        new_value = new_value_input in ["y", "yes"] if new_value_input else current_value
                    elif isinstance(current_value, int):
                        new_value_input = input(f"New value for {param_name} [{current_value}]: ")
                        try:
                            new_value = int(new_value_input) if new_value_input else current_value
                        except ValueError:
                            print("Invalid integer value. Parameter not updated.")
                            continue
                    else:
                        default = str(current_value) if current_value is not None else ""
                        new_value = input(f"New value for {param_name} [{default}]: ") or default
                        
                    # Convert string to appropriate type if needed
                    if param_name in ["models", "instructions", "variations", "max_combinations"]:
                        try:
                            new_value = int(new_value)
                        except ValueError:
                            print("Invalid integer value. Parameter not updated.")
                            continue
                            
                    # Update parameter
                    self.params[param_name] = new_value
                    print(f"Updated {param_name} to {new_value}")
                except ValueError:
                    print("Invalid input. Please enter a number.")
    
    def execute_command(self, command: str) -> Tuple[bool, Any, Optional[str]]:
        """
        Execute a command with error handling and recovery.
        
        Args:
            command: The command string to execute
            
        Returns:
            Tuple of (success, result, error)
        """
        if RICH_AVAILABLE:
            self.console.print(f"[bold green]Running:[/bold green] {command}")
        else:
            print(f"Running: {command}")
            
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            if RICH_AVAILABLE:
                self.console.print("[bold green]Command completed successfully.[/bold green]")
            else:
                print("Command completed successfully.")
            return (True, result, None)
        except subprocess.CalledProcessError as e:
            # Detect and classify the error
            error = detect_error_type(e, command)
            
            # Create recovery strategy
            recovery_strategy = create_recovery_strategy(error)
            
            # Display error information
            if RICH_AVAILABLE:
                self.console.print(f"[bold red]Error:[/bold red] {recovery_strategy.get_user_friendly_message()}")
                
                # Display suggestions
                if recovery_strategy.get_suggestions():
                    self.console.print("[bold yellow]Suggestions:[/bold yellow]")
                    for suggestion in recovery_strategy.get_suggestions():
                        self.console.print(f"- {suggestion}")
            else:
                print(f"Error: {recovery_strategy.get_user_friendly_message()}")
                
                # Display suggestions
                if recovery_strategy.get_suggestions():
                    print("Suggestions:")
                    for suggestion in recovery_strategy.get_suggestions():
                        print(f"- {suggestion}")
                        
            # Attempt recovery if possible
            if recovery_strategy.can_auto_recover():
                if RICH_AVAILABLE:
                    attempt_recovery = Confirm.ask("Would you like to attempt automatic recovery?", default=True)
                else:
                    attempt_recovery = input("Would you like to attempt automatic recovery? (y/n) [y]: ").lower() in ["", "y", "yes"]
                    
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
            if RICH_AVAILABLE:
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
            else:
                print("Options:")
                print("1. Try again with the same command")
                print("2. Modify command parameters")
                print("3. Switch to simulation mode")
                print("4. Abort execution")
                
                try:
                    choice = input("What would you like to do? (1-4): ")
                    
                    if choice == "1":
                        return self.execute_command(command)
                    elif choice == "2":
                        # Return to parameter configuration
                        return (False, None, "parameters_need_modification")
                    elif choice == "3":
                        self.params["simulate"] = True
                        updated_command = self.generate_command()
                        if updated_command:
                            return self.execute_command(updated_command)
                        else:
                            return (False, None, "command_generation_failed")
                    else:
                        return (False, None, "execution_aborted")
                except (ValueError, IndexError):
                    # Default to abort if there's an error
                    return (False, None, "execution_aborted")
                    
        except Exception as e:
            # Handle unexpected errors
            if RICH_AVAILABLE:
                self.console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
            else:
                print(f"Unexpected error: {str(e)}")
            
            return (False, None, "unexpected_error")

    def preview_command(self) -> None:
        """Preview the command that will be run."""
        command = self.generate_command()
        
        if not command:
            return
            
        # Validate the constructed command
        command_validation = self.validate_command(command)
        
        if RICH_AVAILABLE:
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
            
            # Show preview of what the command will do
            params_table = Table(title="Command Parameters")
            params_table.add_column("Parameter", style="cyan")
            params_table.add_column("Value", style="green")
            params_table.add_column("Description", style="yellow")
            
            # Create a list of parameters to show with descriptions
            displayed_params = []
            
            # Basic parameters
            displayed_params.append(("Query", self.params["query"] or "", "query"))
            displayed_params.append(("Domain", self.params["domain"] or "Default", "domain"))
            
            if "config_file" in self.params and self.params["config_file"]:
                displayed_params.append(("Configuration", self.params["config_file"], None))
            
            # Calculate and show total combinations
            models = self.params.get("models", 2)
            instructions = self.params.get("instructions", 3)
            variations = self.params.get("variations", 2)
            total_combinations = models * instructions * variations
            
            if self.params.get("max_combinations"):
                max_combinations = min(total_combinations, self.params["max_combinations"])
                displayed_params.append(("Total Combinations", f"{total_combinations} (limited to {max_combinations})", "max_combinations"))
            else:
                displayed_params.append(("Total Combinations", str(total_combinations), None))
            
            # Show details about selected templates if any
            if self.params.get("instruction_templates"):
                template_ids = self.params["instruction_templates"].split(",")
                displayed_params.append(("Instruction Templates", ", ".join(template_ids), "instruction_templates"))
                
                # Get template details for a separate row
                template_details = []
                for template_id in template_ids:
                    if template_id in self.template_library.templates:
                        template = self.template_library.templates[template_id]
                        template_details.append(f"• {template.name}: {template.description[:50]}...")
                
                if template_details:
                    displayed_params.append(("Template Details", "\n".join(template_details), None))
            else:
                displayed_params.append(("Number of Instructions", str(self.params["instructions"]), "instructions"))
            
            displayed_params.append(("Number of Models", str(self.params["models"]), "models"))
            displayed_params.append(("Number of Variations", str(self.params["variations"]), "variations"))
            displayed_params.append(("Sampling Method", self.params["sampling_method"], "sampling_method"))
            
            # Add flags as a separate section if they're enabled
            flags = []
            if self.params.get("balanced_models"):
                flags.append(("balanced_models", "Balanced model distribution"))
            if self.params.get("use_ollama"):
                flags.append(("use_ollama", "Including Ollama models"))
            if self.params.get("simulate"):
                flags.append(("simulate", "Simulating responses (no API calls)"))
            if self.params.get("dry_run"):
                flags.append(("dry_run", "Dry run mode (no execution)"))
            if self.params.get("generate_reports"):
                flags.append(("generate_reports", "Generate summary reports"))
            if self.params.get("analyze_results"):
                flags.append(("analyze_results", "Analyze results with charts"))
            
            # Add all parameters with descriptions to the table
            for label, value, param_name in displayed_params:
                if param_name and param_name in PARAMETER_DESCRIPTIONS:
                    desc = PARAMETER_DESCRIPTIONS[param_name]["short"]
                    params_table.add_row(label, str(value), desc)
                else:
                    params_table.add_row(label, str(value), "")
            
            # Add flags section if there are any enabled
            if flags:
                params_table.add_row("[bold]Enabled Flags[/bold]", "", "")
                for param_name, label in flags:
                    if param_name in PARAMETER_DESCRIPTIONS:
                        desc = PARAMETER_DESCRIPTIONS[param_name]["short"]
                        params_table.add_row(f"--{param_name.replace('_', '-')}", "Yes", desc)
            
            self.console.print(params_table)
            
            # Add impact panel to show how parameters affect execution
            impact_items = []
            
            # Add specific impact statements based on selected parameters
            if total_combinations > 50:
                impact_items.append(f"⚠️ Running {total_combinations} combinations may result in significant API costs")
            
            if self.params.get("models", 0) > 3:
                impact_items.append(f"⚠️ Using {models} models increases API costs proportionally")
            
            if self.params.get("balanced_models"):
                impact_items.append("✓ Balanced model distribution ensures even representation across providers")
            
            if self.params.get("sampling_method") == "stratified" or self.params.get("quick"):
                impact_items.append("✓ Stratified sampling provides good coverage with fewer combinations")
            
            if self.params.get("simulate"):
                impact_items.append("✓ Simulation mode avoids all API costs (but provides placeholder responses)")
            
            if impact_items:
                impact_panel = Panel(
                    "\n".join(impact_items),
                    title="Parameter Impacts",
                    border_style="yellow"
                )
                self.console.print(impact_panel)
            
            # Provide execution estimate if applicable
            if not self.params.get("simulate") and not self.params.get("dry_run"):
                estimate_seconds = total_combinations * 3  # Rough estimate: 3 seconds per combination
                mins, secs = divmod(estimate_seconds, 60)
                hours, mins = divmod(mins, 60)
                
                if hours > 0:
                    time_estimate = f"{int(hours)}h {int(mins)}m"
                elif mins > 0:
                    time_estimate = f"{int(mins)}m {int(secs)}s"
                else:
                    time_estimate = f"{int(secs)}s"
                
                self.console.print(f"[cyan]Estimated execution time:[/cyan] {time_estimate}")
        else:
            print("\nCommand Preview")
            print("Generated Command:")
            print(command)
            
            # Display command validation results if there are issues
            if not command_validation["valid"] or command_validation["warnings"]:
                print("\nCommand Validation:")
                
                if command_validation["errors"]:
                    print("Errors:")
                    for error in command_validation["errors"]:
                        print(f"- {error}")
                
                if command_validation["warnings"]:
                    print("Warnings:")
                    for warning in command_validation["warnings"]:
                        print(f"- {warning}")
                
                if command_validation["suggestions"]:
                    print("Suggestions:")
                    for suggestion in command_validation["suggestions"]:
                        print(f"- {suggestion}")
            
            print("\nCommand Parameters:")
            print(f"Query: {self.params['query'] or ''}")
            print(f"Domain: {self.params['domain'] or 'Default'}")
            
            if "config_file" in self.params and self.params["config_file"]:
                print(f"Configuration: {self.params['config_file']}")
            
            # Calculate and show total combinations
            models = self.params.get("models", 2)
            instructions = self.params.get("instructions", 3)
            variations = self.params.get("variations", 2)
            total_combinations = models * instructions * variations
            
            if self.params.get("max_combinations"):
                max_combinations = min(total_combinations, self.params["max_combinations"])
                print(f"Total Combinations: {total_combinations} (limited to {max_combinations})")
            else:
                print(f"Total Combinations: {total_combinations}")
            
            # Show details about selected templates if any
            if self.params.get("instruction_templates"):
                template_ids = self.params["instruction_templates"].split(",")
                print(f"Instruction Templates: {', '.join(template_ids)}")
                
                # Get template details
                print("Template Details:")
                for template_id in template_ids:
                    if template_id in self.template_library.templates:
                        template = self.template_library.templates[template_id]
                        print(f"• {template.name}: {template.description[:50]}...")
            else:
                print(f"Number of Instructions: {self.params['instructions']}")
            
            print(f"Number of Models: {self.params['models']}")
            print(f"Number of Variations: {self.params['variations']}")
            
            # Provide execution estimate if applicable
            if not self.params.get("simulate") and not self.params.get("dry_run"):
                estimate_seconds = total_combinations * 3  # Rough estimate: 3 seconds per combination
                mins, secs = divmod(estimate_seconds, 60)
                hours, mins = divmod(mins, 60)
                
                if hours > 0:
                    time_estimate = f"{int(hours)}h {int(mins)}m"
                elif mins > 0:
                    time_estimate = f"{int(mins)}m {int(secs)}s"
                else:
                    time_estimate = f"{int(secs)}s"
                
                print(f"Estimated execution time: {time_estimate}")
    
    def main(self):
        """Main entry point for the command wizard."""
        # Welcome message
        if RICH_AVAILABLE:
            self.console.print("[bold green]ISEE Command Construction Wizard[/bold green]")
            self.console.print("This wizard helps you construct and run valid ISEE commands.\n")
            
            # Show help option
            self.console.print("[dim]You can type 'help' at any parameter prompt to see detailed information.[/dim]")
            self.console.print("[dim]Type 'help all' to see information about all parameters.[/dim]\n")
        else:
            print("ISEE Command Construction Wizard")
            print("This wizard helps you construct and run valid ISEE commands.\n")
            print("You can type 'help' at any parameter prompt to see detailed information.")
            print("Type 'help all' to see information about all parameters.\n")
        
        # Step 1: Query
        if RICH_AVAILABLE:
            self.console.print("[bold cyan]Step 1: Query[/bold cyan]")
            
            # Show parameter context
            self._show_parameter_context("query", self.params["query"])
            
            # Get query with help support
            while True:
                query = Prompt.ask("Enter your query", default="")
                
                if query.lower() == "help":
                    self._show_parameter_help("query")
                    continue
                elif query.lower() == "help all":
                    self._show_all_parameters_help()
                    continue
                else:
                    break
                    
            self.params["query"] = query if query else None
        else:
            print("Step 1: Query")
            
            # Show parameter context
            self._show_parameter_context("query", self.params["query"])
            
            # Get query with help support
            while True:
                query = input("Enter your query: ")
                
                if query.lower() == "help":
                    self._show_parameter_help("query")
                    continue
                elif query.lower() == "help all":
                    self._show_all_parameters_help()
                    continue
                else:
                    break
                    
            self.params["query"] = query if query else None
        
        # Step 2: Select configuration file (optional)
        config_file = self._select_config_file()
        if config_file:
            self.params["config_file"] = config_file
        
        # Step 3: Domain selection
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Step 3: Domain Selection[/bold cyan]")
            
            # Show parameter context
            self._show_parameter_context("domain", self.params["domain"])
            
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
            
            domain_names = [domain.name for domain in domains]
            
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
                    domain_name = domain.name.replace(
                        search_query, 
                        f"[bold yellow]{search_query}[/bold yellow]", 
                        flags=re.IGNORECASE
                    )
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
        else:
            print("\nStep 3: Domain Selection")
            
            # Show parameter context
            self._show_parameter_context("domain", self.params["domain"])
            
            # Display available categories for filtering
            categories = ["education", "technology", "business", "design", "healthcare"]
            descriptions = {
                "education": "Educational domains related to teaching, learning, and instruction",
                "technology": "Technology-focused domains including software, digital transformation, and AI",
                "business": "Business-related domains for corporate, management, and workplace",
                "design": "Design-oriented domains for UX, creative work, and interfaces",
                "healthcare": "Healthcare domains for medical applications, patient care, and wellness"
            }
            
            print("Domain Categories:")
            for category in categories:
                print(f"- {category.capitalize()}: {descriptions.get(category, '')}")
            
            # Allow filtering by category
            category_filter = input("Filter by category (or leave empty for all): ")
            
            # Get all domains first
            all_domains = self.domain_manager.list_domains()
            
            # Filter by category if specified
            if category_filter:
                filtered_domains = self._filter_domains_by_category(all_domains, category_filter)
                if not filtered_domains:
                    print(f"No domains in category '{category_filter}'. Showing all domains.")
                    filtered_domains = all_domains
                else:
                    print(f"Found {len(filtered_domains)} domains in category '{category_filter}'.")
            else:
                filtered_domains = all_domains
            
            # Add search functionality
            search_query = input("Search domains by keyword (or leave empty to see all): ")
            
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
                    print(f"No domains matched your search '{search_query}'. Showing all domains in current filter.")
                    domains = filtered_domains
                else:
                    print(f"Found {len(search_domains)} matching domains for '{search_query}'.")
                    domains = search_domains
            else:
                domains = filtered_domains
            
            domain_names = [domain.name for domain in domains]
            
            print("Available Domains:")
            for i, domain in enumerate(domains, 1):
                desc = domain.description[:50] + "..." if len(domain.description) > 50 else domain.description
                keywords = ", ".join(domain.keywords[:3])
                if len(domain.keywords) > 3:
                    keywords += "..."
                print(f"{i}. {domain.name} - {desc}")
                print(f"   Keywords: {keywords}")
            
            print("0. Default domain")
            
            try:
                domain_choice = int(input("Select a domain by number (or 0 for default) [0]: ") or "0")
                
                if domain_choice > 0 and domain_choice <= len(domains):
                    selected_domain = domains[domain_choice - 1]
                    self.params["domain"] = selected_domain.name
                    
                    # Show detailed information about selected domain
                    print(f"Selected domain: {selected_domain.name}")
                    print(f"Description: {selected_domain.description}")
                    
                    if selected_domain.keywords:
                        print(f"Keywords: {', '.join(selected_domain.keywords)}")
                    
                    # Show related domains if available
                    try:
                        related_domains = self.domain_manager.get_related_domains(selected_domain.id, min_matches=1)
                        if related_domains:
                            print("\nRelated domains you might consider:")
                            for rel_domain in related_domains[:3]:  # Show up to 3 related domains
                                print(f"- {rel_domain.name}")
                    except Exception:
                        # Silently handle any errors getting related domains
                        pass
                else:
                    print("Using default domain.")
            except ValueError:
                print("Invalid selection. Using default domain.")
        
        # Step 4: Instruction template selection
        self.select_instruction_templates()
        
        # Step 5: Models selection
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Step 5: Model Selection[/bold cyan]")
            
            # Show model parameter context
            self._show_parameter_context("models", self.params["models"])
            
            # Get models count with help support
            while True:
                models_input = IntPrompt.ask(
                    "How many models would you like to use?",
                    default=2
                )
                
                if models_input is None:
                    continue
                
                if str(models_input).lower() == "help":
                    self._show_parameter_help("models")
                    continue
                elif str(models_input).lower() == "help all":
                    self._show_all_parameters_help()
                    continue
                else:
                    models_count = models_input
                    break
            
            self.params["models"] = models_count
            
            # Show parameter impact of the selected model count
            if models_count > 3:
                self.console.print(f"[yellow]Note: Using {models_count} models will result in {models_count} times more API calls[/yellow]")
            
            # Ask about model balance with context
            if models_count > 1:
                self._show_parameter_context("balanced_models", self.params["balanced_models"])
                
                while True:
                    balanced_input = Prompt.ask(
                        "Would you like to balance models across API providers? (y/n)",
                        default="y"
                    ).lower()
                    
                    if balanced_input == "help":
                        self._show_parameter_help("balanced_models")
                        continue
                    elif balanced_input == "help all":
                        self._show_all_parameters_help()
                        continue
                    else:
                        balanced_models = balanced_input in ["y", "yes", ""]
                        break
                        
                self.params["balanced_models"] = balanced_models
            
            # Check for Ollama with context
            if self.api_status["ollama"]:
                self._show_parameter_context("use_ollama", self.params["use_ollama"])
                
                while True:
                    ollama_input = Prompt.ask(
                        "Would you like to include Ollama models? (y/n)",
                        default="n"
                    ).lower()
                    
                    if ollama_input == "help":
                        self._show_parameter_help("use_ollama")
                        continue
                    elif ollama_input == "help all":
                        self._show_all_parameters_help()
                        continue
                    else:
                        use_ollama = ollama_input in ["y", "yes"]
                        break
                        
                self.params["use_ollama"] = use_ollama
                
                # Show discovered models if enabled
                if use_ollama and "ollama_models" in self.api_status:
                    self.console.print("[green]Available Ollama models:[/green]")
                    for model in self.api_status["ollama_models"]:
                        self.console.print(f"  • {model}")
        else:
            print("\nStep 5: Model Selection")
            
            # Show model parameter context
            self._show_parameter_context("models", self.params["models"])
            
            # Get models count with help support
            while True:
                models_input = input("How many models would you like to use? [2]: ")
                
                if not models_input:
                    models_count = 2
                    break
                
                if models_input.lower() == "help":
                    self._show_parameter_help("models")
                    continue
                elif models_input.lower() == "help all":
                    self._show_all_parameters_help()
                    continue
                else:
                    try:
                        models_count = int(models_input)
                        break
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                        continue
            
            self.params["models"] = models_count
            
            # Show parameter impact of the selected model count
            if models_count > 3:
                print(f"Note: Using {models_count} models will result in {models_count} times more API calls")
            
            # Ask about model balance with context
            if models_count > 1:
                self._show_parameter_context("balanced_models", self.params["balanced_models"])
                
                while True:
                    balanced_input = input("Would you like to balance models across API providers? (y/n) [y]: ").lower()
                    
                    if balanced_input == "help":
                        self._show_parameter_help("balanced_models")
                        continue
                    elif balanced_input == "help all":
                        self._show_all_parameters_help()
                        continue
                    elif not balanced_input:
                        balanced_models = True
                        break
                    else:
                        balanced_models = balanced_input in ["y", "yes"]
                        break
                        
                self.params["balanced_models"] = balanced_models
            
            # Check for Ollama with context
            if self.api_status["ollama"]:
                self._show_parameter_context("use_ollama", self.params["use_ollama"])
                
                while True:
                    ollama_input = input("Would you like to include Ollama models? (y/n) [n]: ").lower()
                    
                    if ollama_input == "help":
                        self._show_parameter_help("use_ollama")
                        continue
                    elif ollama_input == "help all":
                        self._show_all_parameters_help()
                        continue
                    elif not ollama_input:
                        use_ollama = False
                        break
                    else:
                        use_ollama = ollama_input in ["y", "yes"]
                        break
                        
                self.params["use_ollama"] = use_ollama
                
                # Show discovered models if enabled
                if use_ollama and "ollama_models" in self.api_status:
                    print("Available Ollama models:")
                    for model in self.api_status["ollama_models"]:
                        print(f"  • {model}")
        
        # Step 6: Variations
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Step 6: Variations[/bold cyan]")
            
            # Show variations parameter context
            self._show_parameter_context("variations", self.params["variations"])
            
            # Get variations count with help support
            while True:
                variations_input = IntPrompt.ask(
                    "How many variations would you like for each instruction?",
                    default=2
                )
                
                if variations_input is None:
                    continue
                
                if str(variations_input).lower() == "help":
                    self._show_parameter_help("variations")
                    continue
                elif str(variations_input).lower() == "help all":
                    self._show_all_parameters_help()
                    continue
                else:
                    variations_count = variations_input
                    break
                    
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
            print("\nStep 6: Variations")
            
            # Show variations parameter context
            self._show_parameter_context("variations", self.params["variations"])
            
            # Get variations count with help support
            while True:
                variations_input = input("How many variations would you like for each instruction? [2]: ")
                
                if not variations_input:
                    variations_count = 2
                    break
                
                if variations_input.lower() == "help":
                    self._show_parameter_help("variations")
                    continue
                elif variations_input.lower() == "help all":
                    self._show_all_parameters_help()
                    continue
                else:
                    try:
                        variations_count = int(variations_input)
                        break
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                        continue
                        
            self.params["variations"] = variations_count
            
            # Show total combinations
            models = self.params["models"]
            instructions = self.params["instructions"]
            variations = variations_count
            total_combinations = models * instructions * variations
            
            print(f"Total combinations: {total_combinations}")
            
            if total_combinations > 50:
                print(f"Note: {total_combinations} combinations may result in significant API costs and execution time.")
                print("Consider using --quick mode or setting --max-combinations.")
        
        # Step 7: Sampling method
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Step 7: Sampling Method[/bold cyan]")
            
            # Show parameter context
            self._show_parameter_context("sampling_method", self.params["sampling_method"])
            
            self.console.print("Available sampling methods:")
            self.console.print("1. Exhaustive - Try all combinations")
            self.console.print("2. Random - Randomly sample combinations")
            self.console.print("3. Stratified - Ensure representative sample")
            
            sampling_choice = IntPrompt.ask(
                "Select a sampling method",
                default=1
            )
            
            if sampling_choice == 1:
                self.params["sampling_method"] = "exhaustive"
            elif sampling_choice == 2:
                self.params["sampling_method"] = "random"
                
                # Ask for max combinations
                max_combinations = IntPrompt.ask(
                    "Maximum number of combinations to run",
                    default=20
                )
                self.params["max_combinations"] = max_combinations
            elif sampling_choice == 3:
                self.params["sampling_method"] = "stratified"
                
                # Ask for max combinations
                max_combinations = IntPrompt.ask(
                    "Maximum number of combinations to run",
                    default=36
                )
                self.params["max_combinations"] = max_combinations
            else:
                self.console.print("[yellow]Invalid selection. Using default (exhaustive).[/yellow]")
                self.params["sampling_method"] = "exhaustive"
        else:
            print("\nStep 7: Sampling Method")
            
            # Show parameter context
            self._show_parameter_context("sampling_method", self.params["sampling_method"])
            
            print("Available sampling methods:")
            print("1. Exhaustive - Try all combinations")
            print("2. Random - Randomly sample combinations")
            print("3. Stratified - Ensure representative sample")
            
            try:
                sampling_choice_input = input("Select a sampling method [1]: ")
                sampling_choice = int(sampling_choice_input) if sampling_choice_input else 1
                
                if sampling_choice == 1:
                    self.params["sampling_method"] = "exhaustive"
                elif sampling_choice == 2:
                    self.params["sampling_method"] = "random"
                    
                    # Ask for max combinations
                    max_combinations_input = input("Maximum number of combinations to run [20]: ")
                    max_combinations = int(max_combinations_input) if max_combinations_input else 20
                    self.params["max_combinations"] = max_combinations
                elif sampling_choice == 3:
                    self.params["sampling_method"] = "stratified"
                    
                    # Ask for max combinations
                    max_combinations_input = input("Maximum number of combinations to run [36]: ")
                    max_combinations = int(max_combinations_input) if max_combinations_input else 36
                    self.params["max_combinations"] = max_combinations
                else:
                    print("Invalid selection. Using default (exhaustive).")
                    self.params["sampling_method"] = "exhaustive"
            except ValueError:
                print("Invalid input. Using default (exhaustive).")
                self.params["sampling_method"] = "exhaustive"
        
        # Step 8: Output options
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Step 8: Output Options[/bold cyan]")
            
            # Show parameter context
            self._show_parameter_context("output_format", self.params["output_format"])
            
            # Output format
            self.console.print("Available output formats:")
            self.console.print("1. markdown - Format results as Markdown")
            self.console.print("2. json - Format results as JSON")
            self.console.print("3. text - Format results as plain text")
            
            format_choice = IntPrompt.ask(
                "Select an output format",
                default=1
            )
            
            if format_choice == 1:
                self.params["output_format"] = "markdown"
            elif format_choice == 2:
                self.params["output_format"] = "json"
            elif format_choice == 3:
                self.params["output_format"] = "text"
            else:
                self.console.print("[yellow]Invalid selection. Using default (markdown).[/yellow]")
                self.params["output_format"] = "markdown"
            
            # Generate reports
            generate_reports = Confirm.ask(
                "Generate summary reports?",
                default=True
            )
            self.params["generate_reports"] = generate_reports
            
            # Analyze results
            if generate_reports:
                analyze_results = Confirm.ask(
                    "Analyze results (generate charts and metrics)?",
                    default=True
                )
                self.params["analyze_results"] = analyze_results
            
            # Dry run
            dry_run = Confirm.ask(
                "Run in dry-run mode (show but don't execute)?",
                default=False
            )
            self.params["dry_run"] = dry_run
            
            # Simulate
            if not dry_run:
                simulate = Confirm.ask(
                    "Simulate responses (don't call actual APIs)?",
                    default=False
                )
                self.params["simulate"] = simulate
        else:
            print("\nStep 8: Output Options")
            
            # Show parameter context
            self._show_parameter_context("output_format", self.params["output_format"])
            
            # Output format
            print("Available output formats:")
            print("1. markdown - Format results as Markdown")
            print("2. json - Format results as JSON")
            print("3. text - Format results as plain text")
            
            try:
                format_choice_input = input("Select an output format [1]: ")
                format_choice = int(format_choice_input) if format_choice_input else 1
                
                if format_choice == 1:
                    self.params["output_format"] = "markdown"
                elif format_choice == 2:
                    self.params["output_format"] = "json"
                elif format_choice == 3:
                    self.params["output_format"] = "text"
                else:
                    print("Invalid selection. Using default (markdown).")
                    self.params["output_format"] = "markdown"
            except ValueError:
                print("Invalid input. Using default (markdown).")
                self.params["output_format"] = "markdown"
            
            # Generate reports
            generate_reports_input = input("Generate summary reports? (y/n) [y]: ").lower()
            generate_reports = generate_reports_input in ["", "y", "yes"] if generate_reports_input else True
            self.params["generate_reports"] = generate_reports
            
            # Analyze results
            if generate_reports:
                analyze_results_input = input("Analyze results (generate charts and metrics)? (y/n) [y]: ").lower()
                analyze_results = analyze_results_input in ["", "y", "yes"] if analyze_results_input else True
                self.params["analyze_results"] = analyze_results
            
            # Dry run
            dry_run_input = input("Run in dry-run mode (show but don't execute)? (y/n) [n]: ").lower()
            dry_run = dry_run_input in ["y", "yes"]
            self.params["dry_run"] = dry_run
            
            # Simulate
            if not dry_run:
                simulate_input = input("Simulate responses (don't call actual APIs)? (y/n) [n]: ").lower()
                simulate = simulate_input in ["y", "yes"]
                self.params["simulate"] = simulate
        
        # Step 9: Advanced options
        self.configure_advanced_options()
        
        # Preview the command
        self.preview_command()
        
        # Check if the user wants to run the command
        if RICH_AVAILABLE:
            # Generate and validate the command one more time before running
            command = self.generate_command()
            command_validation = self.validate_command(command)
            
            # If command is valid or user wants to proceed with warnings
            if command and (command_validation["valid"] or Confirm.ask(
                    "Command has warnings. Run anyway?",
                    default=False
                )):
                
                run_command = Confirm.ask(
                    "Run this command?",
                    default=True
                )
                
                if run_command:
                    # Display potential cost warning for real API calls with many combinations
                    models = self.params.get("models", 2)
                    instructions = self.params.get("instructions", 3)
                    variations = self.params.get("variations", 2)
                    total_combinations = models * instructions * variations
                    
                    if not self.params.get("simulate") and total_combinations > 36:
                        self.console.print(f"[bold yellow]Warning:[/bold yellow] Running {total_combinations} combinations with real API calls may result in significant costs.")
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
        else:
            # Generate and validate the command one more time before running
            command = self.generate_command()
            command_validation = self.validate_command(command)
            
            # If command is valid or user wants to proceed with warnings
            proceed_with_warnings = True
            if command and not command_validation["valid"]:
                print("Command cannot be executed due to validation errors.")
                # Show additional options
                self._show_help_options()
                return
            elif command and command_validation["warnings"]:
                proceed_input = input("Command has warnings. Run anyway? (y/n) [n]: ").lower()
                proceed_with_warnings = proceed_input in ["y", "yes"]
                
            if command and proceed_with_warnings:
                run_command_input = input("Run this command? (y/n) [y]: ").lower()
                run_command = run_command_input in ["", "y", "yes"] if run_command_input else True
                
                if run_command:
                    # Display potential cost warning for real API calls with many combinations
                    models = self.params.get("models", 2)
                    instructions = self.params.get("instructions", 3)
                    variations = self.params.get("variations", 2)
                    total_combinations = models * instructions * variations
                    
                    if not self.params.get("simulate") and total_combinations > 36:
                        print(f"Warning: Running {total_combinations} combinations with real API calls may result in significant costs.")
                        cost_confirm_input = input("Are you sure you want to continue? (y/n) [y]: ").lower()
                        if cost_confirm_input not in ["", "y", "yes"]:
                            print("Command execution cancelled by user.")
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
                                print("Command generation failed after reconfiguration.")
                                break
                                
                            self.preview_command()
                            
                            # Confirm before re-running
                            retry_input = input("Run with new parameters? (y/n) [y]: ").lower()
                            retry = retry_input in ["", "y", "yes"]
                            if not retry:
                                print("Command execution cancelled by user.")
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