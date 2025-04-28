#!/usr/bin/env python3
"""
ISEE Command Wizard Phase 2 Implementation

This script applies the Phase 2 improvements to the command_wizard.py file.
It implements model selection alignment, parameter mapping, configuration
integration, and reporting integration.
"""

import os
import sys
import subprocess
import re
import shutil
from datetime import datetime

# Add path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import the implementation modules
from tests.command_wizard.phase2.model_selection_implementation import (
    get_provider_diverse_models,
    get_model_display_names,
    get_balanced_distribution_explanation,
    update_command_wizard_with_model_selection_improvements
)

from tests.command_wizard.phase2.parameter_mapping_implementation import (
    extract_main_parameters,
    validate_parameters,
    show_help_options,
    configure_advanced_options,
    update_command_wizard_with_parameter_improvements
)

from tests.command_wizard.phase2.config_integration_implementation import (
    select_config_file,
    validate_config_file,
    get_config_description,
    get_config_explanation,
    update_command_wizard_with_config_improvements
)

from tests.command_wizard.phase2.reporting_integration_implementation import (
    get_timestamped_output_dir,
    choose_output_directory,
    select_report_format,
    configure_visualization_options,
    get_reporting_explanation,
    update_command_wizard_with_reporting_improvements
)


def backup_command_wizard():
    """Create a backup of the original command_wizard.py file."""
    original_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'command_wizard.py')
    backup_path = original_path + '.phase2.backup'
    
    # Create backup if it doesn't exist
    if not os.path.exists(backup_path):
        shutil.copy2(original_path, backup_path)
        print(f"Created backup of command_wizard.py at {backup_path}")
    else:
        print(f"Backup already exists at {backup_path}")


def apply_model_selection_improvements(file_content):
    """Apply model selection improvements to the command_wizard.py file.
    
    Args:
        file_content: Content of the command_wizard.py file.
        
    Returns:
        Updated file content.
    """
    # Add the _get_provider_diverse_models method
    provider_diverse_models_method = """
    def _get_provider_diverse_models(self, model_count: int) -> List[str]:
        \"\"\"Select models ensuring diversity across providers.
        
        Args:
            model_count: Number of models to select.
            
        Returns:
            List of model IDs ensuring provider diversity.
        \"\"\"
        # Create simulated model configs based on available APIs
        model_configs = {}
        
        # Add Anthropic models if available
        if self.api_status["anthropic"]:
            model_configs["claude-3-opus"] = {
                "id": "claude-3-opus",
                "name": "Claude 3 Opus",
                "provider": "anthropic"
            }
            model_configs["claude-3-sonnet"] = {
                "id": "claude-3-sonnet",
                "name": "Claude 3 Sonnet",
                "provider": "anthropic"
            }
            model_configs["claude-3-haiku"] = {
                "id": "claude-3-haiku",
                "name": "Claude 3 Haiku",
                "provider": "anthropic"
            }
        
        # Add OpenAI models if available
        if self.api_status["openai"]:
            model_configs["gpt-4-turbo"] = {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "provider": "openai"
            }
            model_configs["gpt-3.5-turbo"] = {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "provider": "openai"
            }
        
        # Add Google models if available
        if self.api_status["google"]:
            model_configs["gemini-2.5-pro"] = {
                "id": "gemini-2.5-pro",
                "name": "Gemini 2.5 Pro",
                "provider": "google"
            }
        
        # Add Ollama models if available
        if self.api_status["ollama"] and "ollama_models" in self.api_status:
            for model_name in self.api_status.get("ollama_models", [])[:3]:  # Limit to 3 models for simplicity
                model_configs[model_name] = {
                    "id": model_name,
                    "name": model_name,
                    "provider": "ollama"
                }
        
        # If no API providers are available, use placeholder models
        if not model_configs:
            return [f"model_{i}" for i in range(1, model_count + 1)]
        
        # Apply the selection logic from main.py
        models = list(model_configs.keys())
        if model_count >= len(models):
            return models  # Return all available models
        
        # Group by provider
        provider_models = {}
        for model_id in models:
            model_config = model_configs[model_id]
            provider = model_config.get("provider", "")
            provider_models.setdefault(provider, []).append(model_id)
        
        # Select models to ensure diversity across providers
        selected_models = []
        
        # First, select one model from each provider
        for provider in provider_models:
            if provider_models[provider] and len(selected_models) < model_count:
                selected_models.append(provider_models[provider][0])
        
        # If we still need more models, add additional ones
        providers_cycle = list(provider_models.keys())
        idx = 0
        while len(selected_models) < model_count and idx < 100:  # avoid infinite loop
            provider = providers_cycle[idx % len(providers_cycle)]
            provider_list = provider_models[provider]
            if len(provider_list) > 1:  # If there are more models from this provider
                for model in provider_list[1:]:
                    if model not in selected_models and len(selected_models) < model_count:
                        selected_models.append(model)
            idx += 1
        
        return selected_models
    """
    
    # Update the configure_models method to use _get_provider_diverse_models
    configure_models_updated = """
    def configure_models(self) -> Tuple[int, bool, bool]:
        \"\"\"Configure model selection parameters.
        
        Returns:
            Tuple of (model_count, use_ollama, balanced_models)
        \"\"\"
        if RICH_AVAILABLE:
            self.console.print("\\n[bold cyan]Step 3: Configure Model Selection[/bold cyan]")
            
            # Show available models based on API status
            models_table = Table(title="Available Model Providers")
            models_table.add_column("Provider", style="cyan")
            models_table.add_column("Status")
            models_table.add_column("Models")
            
            if self.api_status["anthropic"]:
                models_table.add_row("Anthropic", "✅ Available", "Claude 3 Sonnet, Haiku, Opus")
            else:
                models_table.add_row("Anthropic", "❌ Not available", "")
                
            if self.api_status["openai"]:
                models_table.add_row("OpenAI", "✅ Available", "GPT-4 Turbo, GPT-3.5 Turbo")
            else:
                models_table.add_row("OpenAI", "❌ Not available", "")
                
            if self.api_status["google"]:
                models_table.add_row("Google", "✅ Available", "Gemini 2.5 Pro")
            else:
                models_table.add_row("Google", "❌ Not available", "")
                
            if self.api_status["ollama"]:
                ollama_models_str = ", ".join(self.api_status.get("ollama_models", [])[:3])
                if len(self.api_status.get("ollama_models", [])) > 3:
                    ollama_models_str += f" (+{len(self.api_status.get('ollama_models', [])) - 3} more)"
                models_table.add_row("Ollama", "✅ Available", ollama_models_str)
            else:
                models_table.add_row("Ollama", "❌ Not available", "")
            
            self.console.print(models_table)
            
            # Determine how many models to use
            max_available_models = sum([
                self.api_status["anthropic"],
                self.api_status["openai"],
                self.api_status["google"],
                self.api_status["ollama"]
            ])
            if max_available_models == 0:
                max_available_models = 1  # Simulation mode will be used
                
            # Calculate a reasonable max (avoid unreasonable numbers)
            reasonable_max = max(max_available_models, 8)  # Allow at least all available models
            
            model_count = IntPrompt.ask(
                f"How many different models would you like to use? (max recommended: {reasonable_max})",
                default=2,
                show_default=True
            )
            
            # Warn if too many models selected
            if model_count > reasonable_max:
                self.console.print(f"[yellow]Warning: You selected {model_count} models, which is more than the recommended maximum of {reasonable_max}.[/yellow]")
                self.console.print("[yellow]This may lead to very large numbers of combinations and longer execution times.[/yellow]")
                proceed = Confirm.ask("Continue with this many models?", default=False)
                if not proceed:
                    model_count = IntPrompt.ask(
                        f"How many different models would you like to use?",
                        default=min(reasonable_max, 4),
                        show_default=True
                    )
            
            # Get provider-diverse model selection
            selected_models = self._get_provider_diverse_models(model_count)
            selected_model_names = []
            
            # Get readable names for the models
            for model_id in selected_models:
                if "claude" in model_id:
                    selected_model_names.append(f"Anthropic: {model_id}")
                elif "gpt" in model_id:
                    selected_model_names.append(f"OpenAI: {model_id}")
                elif "gemini" in model_id:
                    selected_model_names.append(f"Google: {model_id}")
                else:
                    selected_model_names.append(f"Ollama: {model_id}")
            
            # Display selected models
            self.console.print("\\n[cyan]Selected Models:[/cyan]")
            for name in selected_model_names:
                self.console.print(f"- {name}")
            
            # Ask about Ollama if available
            use_ollama = False
            if self.api_status["ollama"]:
                use_ollama = Confirm.ask(
                    "Would you like to include Ollama models?",
                    default=True
                )
            
            # Ask about balanced model representation
            balanced_models = False
            if model_count > 1:
                # Show explanation first since help_text isn't supported
                if RICH_AVAILABLE:
                    self.console.print("[dim]Balanced model distribution:[/dim]")
                    self.console.print("[dim]- Interleaves models across combinations, ensuring each model gets similar template/query varieties[/dim]")
                    self.console.print("[dim]- Without balancing, combinations are grouped by model type[/dim]")
                balanced_models = Confirm.ask(
                    "Ensure balanced representation of models across combinations?",
                    default=True
                )
        else:
            print("\\nStep 3: Configure Model Selection")
            
            # Show available models based on API status
            print("Available Model Providers:")
            
            if self.api_status["anthropic"]:
                print("✓ Anthropic: Available (Claude 3 Sonnet, Haiku, Opus)")
            else:
                print("✗ Anthropic: Not available")
                
            if self.api_status["openai"]:
                print("✓ OpenAI: Available (GPT-4 Turbo, GPT-3.5 Turbo)")
            else:
                print("✗ OpenAI: Not available")
                
            if self.api_status["google"]:
                print("✓ Google: Available (Gemini 2.5 Pro)")
            else:
                print("✗ Google: Not available")
                
            if self.api_status["ollama"]:
                ollama_models_str = ", ".join(self.api_status.get("ollama_models", [])[:3])
                if len(self.api_status.get("ollama_models", [])) > 3:
                    ollama_models_str += f" (+{len(self.api_status.get('ollama_models', [])) - 3} more)"
                print(f"✓ Ollama: Available ({ollama_models_str})")
            else:
                print("✗ Ollama: Not available")
            
            # Determine how many models to use
            max_available_models = sum([
                self.api_status["anthropic"],
                self.api_status["openai"],
                self.api_status["google"],
                self.api_status["ollama"]
            ])
            if max_available_models == 0:
                max_available_models = 1  # Simulation mode will be used
                
            # Calculate a reasonable max (avoid unreasonable numbers)
            reasonable_max = max(max_available_models, 8)  # Allow at least all available models
            
            while True:
                try:
                    model_count_input = input(f"How many different models would you like to use? (max recommended: {reasonable_max}) [2]: ")
                    model_count = int(model_count_input) if model_count_input else 2
                    if model_count < 1:
                        print("Please enter a positive number.")
                        continue
                    
                    # Warn if too many models selected
                    if model_count > reasonable_max:
                        print(f"Warning: You selected {model_count} models, which is more than the recommended maximum of {reasonable_max}.")
                        print("This may lead to very large numbers of combinations and longer execution times.")
                        proceed_input = input("Continue with this many models? (y/n) [n]: ").lower()
                        proceed = proceed_input in ["y", "yes"]
                        if not proceed:
                            continue
                    
                    break
                except ValueError:
                    print("Please enter a number.")
            
            # Get provider-diverse model selection
            selected_models = self._get_provider_diverse_models(model_count)
            selected_model_names = []
            
            # Get readable names for the models
            for model_id in selected_models:
                if "claude" in model_id:
                    selected_model_names.append(f"Anthropic: {model_id}")
                elif "gpt" in model_id:
                    selected_model_names.append(f"OpenAI: {model_id}")
                elif "gemini" in model_id:
                    selected_model_names.append(f"Google: {model_id}")
                else:
                    selected_model_names.append(f"Ollama: {model_id}")
            
            # Display selected models
            print("\\nSelected Models:")
            for name in selected_model_names:
                print(f"- {name}")
            
            # Ask about Ollama if available
            use_ollama = False
            if self.api_status["ollama"]:
                use_ollama_input = input("Would you like to include Ollama models? (y/n) [y]: ").lower()
                use_ollama = use_ollama_input in ["", "y", "yes"]
            
            # Ask about balanced model representation
            balanced_models = False
            if model_count > 1:
                print("Balanced model distribution:")
                print("- Interleaves models across combinations, ensuring each model gets similar template/query varieties")
                print("- Without balancing, combinations are grouped by model type")
                
                balanced_input = input("Ensure balanced representation of models across combinations? (y/n) [y]: ").lower()
                balanced_models = balanced_input in ["", "y", "yes"]
        
        # Store selected models for later use
        self.selected_models = selected_models
        self.selected_model_names = selected_model_names
        
        self.params["models"] = model_count
        self.params["use_ollama"] = use_ollama
        self.params["balanced_models"] = balanced_models
        
        return model_count, use_ollama, balanced_models
    """
    
    # Apply changes to the file content
    file_content = file_content.replace("def __init__(self):", f"def __init__(self):\n        # Store selected models\n        self.selected_models = []\n        self.selected_model_names = []")
    
    # Add the _get_provider_diverse_models method
    method_pattern = r'def configure_models\(self\)'
    file_content = re.sub(method_pattern, f"{provider_diverse_models_method}\n    def configure_models(self)", file_content)
    
    # Update the configure_models method
    method_pattern = r'def configure_models.*?def configure_cognitive_diversity'
    file_content = re.sub(method_pattern, f"{configure_models_updated}\n    def configure_cognitive_diversity", file_content, flags=re.DOTALL)
    
    # Update the preview_command method to include selected models in the explanation
    preview_command_pattern = r'# Basic parameters\s+command_summary \+= f"- Process the query:'
    preview_command_replacement = """# Basic parameters
            command_summary += f"- Process the query: \\"{self.params['query']}\\""\\n
            
            # Model configuration with provider diversity
            if hasattr(self, 'selected_model_names') and self.selected_model_names:
                selected_models_str = ", ".join(self.selected_model_names)
                command_summary += f"- Use {len(self.selected_models)} different models ({selected_models_str})\\n"
            else:
                command_summary += f"- Use {self.params['models']} different models"""
    
    file_content = re.sub(preview_command_pattern, preview_command_replacement, file_content)
    
    return file_content


def apply_parameter_mapping_improvements(file_content):
    """Apply parameter mapping improvements to the command_wizard.py file.
    
    Args:
        file_content: Content of the command_wizard.py file.
        
    Returns:
        Updated file content.
    """
    # Add the _extract_main_parameters method
    extract_main_parameters_method = """
    def _extract_main_parameters(self) -> Dict[str, Dict[str, Any]]:
        \"\"\"Extract parameters from main.py using the help command.
        
        Returns:
            Dictionary mapping parameter names to their details.
        \"\"\"
        try:
            # Run main.py --help to get parameter information
            result = subprocess.run(["python", "main.py", "--help"], 
                                    capture_output=True, text=True)
            help_text = result.stdout
            
            # Extract parameters using regex
            param_pattern = r"(?:--([a-zA-Z0-9_-]+))(?: ((?:\\{[^}]+\\})|(?:[A-Z_]+)))?"
            params = {}
            choice_pattern = r"\\{([^}]+)\\}"
            
            # Find parameters and their types
            for line in help_text.split("\\n"):
                for match in re.finditer(param_pattern, line):
                    param_name = match.group(1)
                    param_type = "flag"  # Default type is flag (boolean)
                    choices = None
                    
                    # If there's a type indicator
                    if match.group(2):
                        type_indicator = match.group(2)
                        
                        # Check if it's a choice type
                        choice_match = re.search(choice_pattern, type_indicator)
                        if choice_match:
                            param_type = "choice"
                            choices = [choice.strip() for choice in choice_match.group(1).split(",")]
                        else:
                            # Otherwise it's a value type
                            param_type = "text"
                    
                    # Store parameter details
                    params[param_name] = {
                        "type": param_type,
                        "required": False,  # Assume not required by default
                    }
                    
                    # Add choices if available
                    if choices:
                        params[param_name]["choices"] = choices
            
            return params
        except Exception as e:
            if RICH_AVAILABLE:
                self.console.print(f"[yellow]Warning: Could not extract parameters from main.py: {str(e)}[/yellow]")
            else:
                print(f"Warning: Could not extract parameters from main.py: {str(e)}")
            
            # Return an empty dict if extraction fails
            return {}
    """
    
    # Add the _validate_parameters method
    validate_parameters_method = """
    def _validate_parameters(self) -> Dict[str, Any]:
        \"\"\"Validate wizard parameters against main.py parameters.
        
        Returns:
            Dictionary with validation results.
        \"\"\"
        # Extract main.py parameters
        main_params = self._extract_main_parameters()
        
        # Initialize validation result
        validation = {
            "valid": True,
            "issues": []
        }
        
        # Check each wizard parameter against main.py parameters
        for param_name, param_value in self.params.items():
            # Skip None/empty values
            if param_value is None or (isinstance(param_value, str) and not param_value):
                continue
            
            # Convert wizard parameter name to main.py parameter name
            main_param_name = param_name.replace("_", "-")
            
            # Check if the parameter exists in main.py
            if main_param_name not in main_params:
                # Some parameters are handled specially
                if param_name in ["specific_templates", "load_state", "config_file"]:
                    continue
                
                validation["valid"] = False
                validation["issues"].append(f"Parameter '{param_name}' does not exist in main.py")
                continue
            
            # Get main.py parameter details
            main_param = main_params[main_param_name]
            
            # Validate based on parameter type
            if main_param["type"] == "choice" and param_value not in main_param.get("choices", []):
                validation["valid"] = False
                validation["issues"].append(
                    f"Invalid value '{param_value}' for parameter '{param_name}'. "
                    f"Valid choices: {', '.join(main_param.get('choices', []))}"
                )
        
        # Validate parameter dependencies
        if self.params.get("analyze_results") and not self.params.get("generate_reports"):
            validation["valid"] = False
            validation["issues"].append("'analyze_results' requires 'generate_reports' to be enabled")
        
        return validation
    """
    
    # Add the _show_help_options method
    show_help_options_method = """
    def _show_help_options(self) -> None:
        \"\"\"Show help information about available command-line options.\"\"\"
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
                "usage": "python main.py --quick --query \\"Your query here\\""
            },
            {
                "name": "--full",
                "description": "Run in full mode (exhaustive combinations)",
                "usage": "python main.py --full --query \\"Your query here\\""
            }
        ]
        
        if RICH_AVAILABLE:
            self.console.print("\\n[bold cyan]Additional Command-Line Options[/bold cyan]")
            
            options_table = Table(title="Helpful Options")
            options_table.add_column("Option", style="green")
            options_table.add_column("Description", style="cyan")
            options_table.add_column("Example", style="yellow")
            
            for option in help_info:
                options_table.add_row(option["name"], option["description"], option["usage"])
            
            self.console.print(options_table)
        else:
            print("\\nAdditional Command-Line Options:")
            for option in help_info:
                print(f"{option['name']}: {option['description']}")
                print(f"  Example: {option['usage']}")
                print()
    """
    
    # Add the configure_advanced_options method
    configure_advanced_options_method = """
    def configure_advanced_options(self) -> Dict[str, Any]:
        \"\"\"Configure advanced options not covered by other steps.
        
        Returns:
            Dictionary of advanced options.
        \"\"\"
        advanced_params = {}
        
        if RICH_AVAILABLE:
            self.console.print("\\n[bold cyan]Advanced Options[/bold cyan]")
            
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
            print("\\nAdvanced Options")
            
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
    """
    
    # Update the generate_command method to use validated parameters
    generate_command_updated = """
    def generate_command(self) -> str:
        \"\"\"Generate the ISEE command based on user selections.
        
        Returns:
            The generated command string.
        \"\"\"
        # Validate parameters first
        validation = self._validate_parameters()
        if not validation["valid"]:
            if RICH_AVAILABLE:
                self.console.print("[yellow]Warning: Command has validation issues:[/yellow]")
                for issue in validation["issues"]:
                    self.console.print(f"[yellow]- {issue}[/yellow]")
            else:
                print("Warning: Command has validation issues:")
                for issue in validation["issues"]:
                    print(f"- {issue}")
                    
        cmd_parts = ["python main.py"]
        
        # Check if unified_config.json exists and add it to ensure real models are used
        if self.params.get("config_file"):
            cmd_parts.append(f'--config "{self.params["config_file"]}"')
        elif os.path.exists("unified_config.json"):
            cmd_parts.append("--config unified_config.json")
            # Also add a note to the object for display in preview
            self.using_unified_config = True
        else:
            self.using_unified_config = False
        
        # Add domain config if specified
        if self.params.get("domain_config"):
            cmd_parts.append(f'--domain-config "{self.params["domain_config"]}"')
        
        # Add query parameter
        if self.params["query"]:
            cmd_parts.append(f'--query "{self.params["query"]}"')
        
        # Add domain parameter
        if self.params["domain"]:
            cmd_parts.append(f'--domain "{self.params["domain"]}"')
        
        # Add model parameters
        cmd_parts.append(f'--models {self.params["models"]}')
        if self.params["use_ollama"]:
            cmd_parts.append("--use-ollama")
        if self.params["balanced_models"]:
            cmd_parts.append("--balanced-models")
        
        # Add instruction parameters
        # Just use the count parameter since --instruction-templates isn't supported yet
        cmd_parts.append(f'--instructions {self.params["instructions"]}')
        
        # Store the specific templates in a comment that appears in the command preview
        # but doesn't get executed (for future implementation)
        if self.params.get("specific_templates"):
            self.specific_templates_comment = f"# Selected templates: {','.join(self.params['specific_templates'])}"
        else:
            self.specific_templates_comment = None
        
        # Add variation parameters
        cmd_parts.append(f'--variations {self.params["variations"]}')
        
        # Add execution parameters
        if self.params["max_combinations"]:
            cmd_parts.append(f'--max-combinations {self.params["max_combinations"]}')
        
        cmd_parts.append(f'--sampling-method {self.params["sampling_method"]}')
        
        if self.params["synthesize_method"] != "cluster_based":
            cmd_parts.append(f'--synthesize-method {self.params["synthesize_method"]}')
        
        # Add output parameters
        cmd_parts.append(f'--output-format {self.params["output_format"]}')
        
        if self.params["output_file"]:
            cmd_parts.append(f'--output-file "{self.params["output_file"]}"')
        
        # Add output directory if specified
        if self.params.get("output_directory"):
            cmd_parts.append(f'--output-directory "{self.params["output_directory"]}"')
        
        # Add reporting parameters
        if self.params["generate_reports"]:
            cmd_parts.append("--generate-reports")
            
            # Add report format if specified
            if self.params.get("report_format"):
                cmd_parts.append(f'--report-format {self.params["report_format"]}')
        
        if self.params["analyze_results"]:
            cmd_parts.append("--analyze-results")
            
            # Add export CSV if specified
            if self.params.get("export_csv"):
                cmd_parts.append("--export-csv")
            
            # Add no visualizations if specified
            if self.params.get("no_visualizations"):
                cmd_parts.append("--no-visualizations")
        
        # Add execution mode parameters
        if self.params["simulate"]:
            cmd_parts.append("--simulate")
        
        if self.params["dry_run"]:
            cmd_parts.append("--dry-run")
        
        if self.params["save_state"]:
            cmd_parts.append(f'--save-state "{self.params["save_state"]}"')
        
        # Add quick/full mode parameters
        if self.params.get("quick"):
            cmd_parts.append("--quick")
        
        if self.params.get("full"):
            cmd_parts.append("--full")
        
        return " ".join(cmd_parts)
    """
    
    # Update the run_wizard method to include advanced options and parameter validation
    run_wizard_updated = """
    def run_wizard(self) -> None:
        \"\"\"Run the complete wizard flow.\"\"\"
        # Show welcome message
        self.show_welcome()
        
        # Select configuration file
        config_file = self._select_config_file()
        if config_file:
            self.params["config_file"] = config_file
        
        # Get basic query information
        self.get_query()
        self.select_domain()
        
        # Configure models
        self.configure_models()
        
        # Configure cognitive diversity
        _, _, _ = self.configure_cognitive_diversity()
        
        # Configure execution parameters
        self.configure_execution()
        
        # Configure output options
        self.configure_output()
        
        # Configure execution mode
        self.configure_execution_mode()
        
        # Configure advanced options
        self.configure_advanced_options()
        
        # Validate parameters
        validation = self._validate_parameters()
        if not validation["valid"]:
            if RICH_AVAILABLE:
                self.console.print("\\n[bold red]Parameter Validation Issues:[/bold red]")
                for issue in validation["issues"]:
                    self.console.print(f"[red]- {issue}[/red]")
                
                self.console.print("[yellow]The command may not work as expected. Would you like to continue anyway?[/yellow]")
                continue_anyway = Confirm.ask("Continue anyway?", default=False)
                if not continue_anyway:
                    if RICH_AVAILABLE:
                        self.console.print("[red]Wizard aborted.[/red]")
                    else:
                        print("Wizard aborted.")
                    return
            else:
                print("\\nParameter Validation Issues:")
                for issue in validation["issues"]:
                    print(f"- {issue}")
                
                print("The command may not work as expected. Would you like to continue anyway?")
                continue_input = input("Continue anyway? (y/n) [n]: ").lower()
                continue_anyway = continue_input in ["y", "yes"]
                if not continue_anyway:
                    print("Wizard aborted.")
                    return
        
        # Generate and preview the command
        command = self.generate_command()
        self.preview_command(command)
        
        # Show additional help options
        self._show_help_options()
        
        # Copy to clipboard if possible
        clipboard_success = self.copy_to_clipboard(command)
        
        if clipboard_success and RICH_AVAILABLE:
            self.console.print("\\n[green]Command copied to clipboard![/green]")
        elif clipboard_success:
            print("\\nCommand copied to clipboard!")
        
        # Execute the command if requested
        self.execute_command(command)
    """
    
    # Apply changes to the file content
    file_content = file_content.replace("import os", "import os\nimport re")
    
    # Add the extract_main_parameters method
    method_pattern = r'def _load_domain_configs\(self\).*?def show_welcome'
    file_content = re.sub(method_pattern, f"def _load_domain_configs(self):\n        \"\"\"Try to load domain-specific configuration files.\"\"\"{extract_main_parameters_method}{validate_parameters_method}{show_help_options_method}{configure_advanced_options_method}\n    \n    def show_welcome", file_content, flags=re.DOTALL)
    
    # Update the generate_command method
    method_pattern = r'def generate_command\(self\).*?def preview_command'
    file_content = re.sub(method_pattern, f"{generate_command_updated}\n    \n    def preview_command", file_content, flags=re.DOTALL)
    
    # Update the run_wizard method
    method_pattern = r'def run_wizard\(self\).*?def main'
    file_content = re.sub(method_pattern, f"{run_wizard_updated}\n\n\ndef main", file_content, flags=re.DOTALL)
    
    return file_content


def apply_config_integration_improvements(file_content):
    """Apply configuration integration improvements to the command_wizard.py file.
    
    Args:
        file_content: Content of the command_wizard.py file.
        
    Returns:
        Updated file content.
    """
    # Add the _select_config_file method
    select_config_file_method = """
    def _select_config_file(self) -> Optional[str]:
        \"\"\"Allow the user to select a configuration file.
        
        Returns:
            Selected configuration file or None if no file is selected.
        \"\"\"
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
            self.console.print("\\n[bold cyan]Configuration File Selection[/bold cyan]")
            
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
            print("\\nConfiguration File Selection")
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
    """
    
    # Add the _validate_config_file method
    validate_config_file_method = """
    def _validate_config_file(self, config_path: str) -> bool:
        \"\"\"Validate that a configuration file is compatible with the ISEE framework.
        
        Args:
            config_path: Path to the configuration file.
            
        Returns:
            True if the configuration file is valid, False otherwise.
        \"\"\"
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
    """
    
    # Add the _get_config_description method
    get_config_description_method = """
    def _get_config_description(self, config_path: str) -> str:
        \"\"\"Get a description for a configuration file.
        
        Args:
            config_path: Path to the configuration file.
            
        Returns:
            Description of the configuration file.
        \"\"\"
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
    """
    
    # Update the preview_command method to enhance configuration explanation
    preview_command_updated = """
        # Display config file usage information
        if self.params.get("config_file") or hasattr(self, 'using_unified_config') and self.using_unified_config:
            config_file = self.params.get("config_file", "unified_config.json")
            
            if RICH_AVAILABLE:
                self.console.print(Panel(
                    f"[green]Using {config_file} for model configuration[/green]\\n\\n"
                    "The configuration file maps model IDs to actual API providers and includes:\\n"
                    "- Model names and versions\\n"
                    "- API provider information\\n"
                    "- Model-specific parameters\\n\\n"
                    "This ensures the correct models are used for each API provider.",
                    title="Configuration Information",
                    border_style="green"
                ))
            else:
                print(f"\\nCONFIGURATION INFORMATION:")
                print(f"Using {config_file} for model configuration")
                print("The configuration file maps model IDs to actual API providers and includes:")
                print("- Model names and versions")
                print("- API provider information")
                print("- Model-specific parameters")
                print("\\nThis ensures the correct models are used for each API provider.")
                print("-" * 70)
    """
    
    # Apply changes to the file content
    # Add the configuration methods
    method_pattern = r'def _load_domain_configs\(self\).*?def show_welcome'
    new_methods = f"def _load_domain_configs(self):\n        \"\"\"Try to load domain-specific configuration files.\"\"\"{select_config_file_method}{validate_config_file_method}{get_config_description_method}\n    \n    def show_welcome"
    file_content = re.sub(method_pattern, new_methods, file_content, flags=re.DOTALL)
    
    # Update the preview_command method
    method_pattern = r'if hasattr\(self, \'using_unified_config\'\) and self.using_unified_config:.*?# Explain what the command will do'
    file_content = re.sub(method_pattern, f"{preview_command_updated}\n            \n            # Explain what the command will do", file_content, flags=re.DOTALL)
    
    return file_content


def apply_reporting_integration_improvements(file_content):
    """Apply reporting integration improvements to the command_wizard.py file.
    
    Args:
        file_content: Content of the command_wizard.py file.
        
    Returns:
        Updated file content.
    """
    # Add the _get_timestamped_output_dir method
    get_timestamped_output_dir_method = """
    def _get_timestamped_output_dir(self) -> str:
        \"\"\"Generate a timestamped output directory path.
        
        Returns:
            Path to the timestamped output directory.
        \"\"\"
        # Match the format used in main.py
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join("data", "output", f"run_{timestamp}")
    """
    
    # Add the _choose_output_directory method
    choose_output_directory_method = """
    def _choose_output_directory(self) -> Optional[str]:
        \"\"\"Allow the user to choose an output directory.
        
        Returns:
            Selected output directory or None to use the default.
        \"\"\"
        # Default directory
        default_dir = self._get_timestamped_output_dir()
        
        if RICH_AVAILABLE:
            self.console.print("\\n[bold cyan]Output Directory[/bold cyan]")
            
            # Show the default directory
            self.console.print(f"Default directory: [green]{default_dir}[/green]")
            
            # Ask if the user wants to specify a custom directory
            use_custom_dir = Confirm.ask(
                "Would you like to specify a custom output directory?",
                default=False
            )
            
            if not use_custom_dir:
                return default_dir
            
            # Get the custom directory
            custom_dir = Prompt.ask(
                "Enter custom output directory",
                default="data/output/custom"
            )
            
            # Validate the directory
            if not os.path.exists(os.path.dirname(custom_dir)):
                self.console.print(f"[yellow]Warning: Parent directory '{os.path.dirname(custom_dir)}' does not exist. It will be created if you proceed.[/yellow]")
                create_dir = Confirm.ask(
                    "Create directory?",
                    default=True
                )
                if create_dir:
                    return custom_dir
                else:
                    return default_dir
            
            return custom_dir
        else:
            print("\\nOutput Directory")
            
            # Show the default directory
            print(f"Default directory: {default_dir}")
            
            # Ask if the user wants to specify a custom directory
            use_custom_dir_input = input("Would you like to specify a custom output directory? (y/n) [n]: ").lower()
            use_custom_dir = use_custom_dir_input in ["y", "yes"]
            
            if not use_custom_dir:
                return default_dir
            
            # Get the custom directory
            custom_dir_input = input("Enter custom output directory [data/output/custom]: ")
            custom_dir = custom_dir_input if custom_dir_input else "data/output/custom"
            
            # Validate the directory
            if not os.path.exists(os.path.dirname(custom_dir)):
                print(f"Warning: Parent directory '{os.path.dirname(custom_dir)}' does not exist. It will be created if you proceed.")
                create_dir_input = input("Create directory? (y/n) [y]: ").lower()
                create_dir = create_dir_input in ["", "y", "yes"]
                if create_dir:
                    return custom_dir
                else:
                    return default_dir
            
            return custom_dir
    """
    
    # Add the _select_report_format method
    select_report_format_method = """
    def _select_report_format(self) -> str:
        \"\"\"Allow the user to select the report format.
        
        Returns:
            Selected report format.
        \"\"\"
        formats = ["markdown", "json"]
        
        if RICH_AVAILABLE:
            self.console.print("\\n[bold cyan]Report Format[/bold cyan]")
            
            # Show available formats
            self.console.print("Available formats:")
            for i, format_name in enumerate(formats, 1):
                self.console.print(f"{i}. {format_name}")
            
            # Get the selection
            format_choice = IntPrompt.ask(
                "Select report format",
                default=1,
                show_default=True
            )
            
            if 1 <= format_choice <= len(formats):
                return formats[format_choice - 1]
            else:
                return formats[0]  # Default to first format
        else:
            print("\\nReport Format")
            
            # Show available formats
            print("Available formats:")
            for i, format_name in enumerate(formats, 1):
                print(f"{i}. {format_name}")
            
            # Get the selection
            format_choice_input = input("Select report format [1]: ")
            
            try:
                format_choice = int(format_choice_input) if format_choice_input else 1
                if 1 <= format_choice <= len(formats):
                    return formats[format_choice - 1]
                else:
                    return formats[0]  # Default to first format
            except ValueError:
                return formats[0]  # Default to first format
    """
    
    # Add the _configure_visualization_options method
    configure_visualization_options_method = """
    def _configure_visualization_options(self) -> Tuple[bool, bool]:
        \"\"\"Configure visualization options.
        
        Returns:
            Tuple of (export_csv, no_visualizations).
        \"\"\"
        if RICH_AVAILABLE:
            self.console.print("\\n[bold cyan]Visualization Options[/bold cyan]")
            
            # Export CSV option
            export_csv = Confirm.ask(
                "Export data as CSV files for analysis?",
                default=True
            )
            
            # No visualizations option
            no_visualizations = Confirm.ask(
                "Skip generating visualization charts?",
                default=False
            )
            
            # If no visualizations, explain what will be skipped
            if no_visualizations:
                self.console.print("[dim]Visualization charts like model performance comparison, template effectiveness, and diversity analysis will be skipped.[/dim]")
        else:
            print("\\nVisualization Options")
            
            # Export CSV option
            export_csv_input = input("Export data as CSV files for analysis? (y/n) [y]: ").lower()
            export_csv = export_csv_input in ["", "y", "yes"]
            
            # No visualizations option
            no_viz_input = input("Skip generating visualization charts? (y/n) [n]: ").lower()
            no_visualizations = no_viz_input in ["y", "yes"]
            
            # If no visualizations, explain what will be skipped
            if no_visualizations:
                print("Visualization charts like model performance comparison, template effectiveness, and diversity analysis will be skipped.")
        
        return export_csv, no_visualizations
    """
    
    # Update the configure_output method
    configure_output_updated = """
    def configure_output(self) -> Tuple[str, Optional[str], bool, bool]:
        \"\"\"Configure output parameters.
        
        Returns:
            Tuple of (output_format, output_file, generate_reports, analyze_results)
        \"\"\"
        if RICH_AVAILABLE:
            self.console.print("\\n[bold cyan]Step 6: Configure Output Options[/bold cyan]")
            
            # Output format selection
            output_formats = {
                "1": "markdown",
                "2": "json"
            }
            
            self.console.print("\\nOutput Formats:")
            for key, value in output_formats.items():
                self.console.print(f"  {key}. {value}")
            
            format_choice = Prompt.ask(
                "Select output format",
                choices=["1", "2"],
                default="1"
            )
            output_format = output_formats[format_choice]
            
            # Output file
            use_custom_file = Confirm.ask(
                "Would you like to specify an output filename?",
                default=False
            )
            
            output_file = None
            if use_custom_file:
                extension = "md" if output_format == "markdown" else "json"
                output_file = Prompt.ask(
                    "Enter output filename",
                    default=f"isee_results.{extension}"
                )
            
            # Output directory
            output_dir = self._choose_output_directory()
            if output_dir:
                self.params["output_directory"] = output_dir
            
            # Generate reports
            generate_reports = Confirm.ask(
                "Generate detailed reports?",
                default=True
            )
            
            # Report format (if generating reports)
            if generate_reports:
                report_format = self._select_report_format()
                self.params["report_format"] = report_format
            
            # Analyze results
            analyze_results = False
            if generate_reports:
                analyze_results = Confirm.ask(
                    "Perform analysis with visualizations?",
                    default=True
                )
                
                # Visualization options (if analyzing results)
                if analyze_results:
                    export_csv, no_visualizations = self._configure_visualization_options()
                    self.params["export_csv"] = export_csv
                    self.params["no_visualizations"] = no_visualizations
        else:
            print("\\nStep 6: Configure Output Options")
            
            # Output format selection
            print("\\nOutput Formats:")
            print("  1. markdown")
            print("  2. json")
            
            while True:
                format_choice = input("Select output format [1]: ")
                if format_choice == "":
                    format_choice = "1"
                
                if format_choice in ["1", "2"]:
                    break
                print("Invalid selection. Please try again.")
            
            output_format_map = {
                "1": "markdown",
                "2": "json"
            }
            output_format = output_format_map[format_choice]
            
            # Output file
            use_custom_file_input = input("Would you like to specify an output filename? (y/n) [n]: ").lower()
            use_custom_file = use_custom_file_input in ["y", "yes"]
            
            output_file = None
            if use_custom_file:
                extension = "md" if output_format == "markdown" else "json"
                output_file = input(f"Enter output filename [isee_results.{extension}]: ")
                if not output_file:
                    output_file = f"isee_results.{extension}"
            
            # Output directory
            output_dir = self._choose_output_directory()
            if output_dir:
                self.params["output_directory"] = output_dir
            
            # Generate reports
            generate_reports_input = input("Generate detailed reports? (y/n) [y]: ").lower()
            generate_reports = generate_reports_input in ["", "y", "yes"]
            
            # Report format (if generating reports)
            if generate_reports:
                report_format = self._select_report_format()
                self.params["report_format"] = report_format
            
            # Analyze results
            analyze_results = False
            if generate_reports:
                analyze_results_input = input("Perform analysis with visualizations? (y/n) [y]: ").lower()
                analyze_results = analyze_results_input in ["", "y", "yes"]
                
                # Visualization options (if analyzing results)
                if analyze_results:
                    export_csv, no_visualizations = self._configure_visualization_options()
                    self.params["export_csv"] = export_csv
                    self.params["no_visualizations"] = no_visualizations
        
        self.params["output_format"] = output_format
        self.params["output_file"] = output_file
        self.params["generate_reports"] = generate_reports
        self.params["analyze_results"] = analyze_results
        
        return output_format, output_file, generate_reports, analyze_results
    """
    
    # Update the preview_command method for better reporting explanation
    enhanced_reporting_explanation = """
            # Add output directory explanation
            if self.params.get("output_directory"):
                command_summary += f"- Save all outputs to the directory: {self.params['output_directory']}\\n"
            else:
                command_summary += f"- Save all outputs to a timestamped directory (e.g., data/output/run_20230101_120000)\\n"
            
            # Output format and file
            command_summary += f"- Generate main output in {self.params['output_format']} format\\n"
            
            if self.params["output_file"]:
                command_summary += f"- Save main output to {self.params['output_file']}\\n"
            else:
                command_summary += "- Save main output to an automatically generated file\\n"
            
            # Detailed reporting explanation if enabled
            if self.params["generate_reports"]:
                report_format = self.params.get("report_format", "markdown")
                command_summary += f"- Generate detailed reports in {report_format} format\\n"
                command_summary += "  Including: combination details, results, model performance, template effectiveness\\n"
                
                if self.params["analyze_results"]:
                    command_summary += "- Perform analysis with the following outputs:\\n"
                    
                    if not self.params.get("no_visualizations", False):
                        command_summary += "  - Visualization charts (performance comparisons, effectiveness metrics)\\n"
                    
                    if self.params.get("export_csv", False):
                        command_summary += "  - CSV data files for further analysis\\n"
                    
                    command_summary += "  - Analysis summary report\\n"
    """
    
    # Apply changes to the file content
    # Add the reporting methods
    method_pattern = r'def _load_domain_configs\(self\).*?def show_welcome'
    new_methods = f"def _load_domain_configs(self):\n        \"\"\"Try to load domain-specific configuration files.\"\"\"{get_timestamped_output_dir_method}{choose_output_directory_method}{select_report_format_method}{configure_visualization_options_method}\n    \n    def show_welcome"
    file_content = re.sub(method_pattern, new_methods, file_content, flags=re.DOTALL)
    
    # Update the configure_output method
    method_pattern = r'def configure_output\(self\).*?def configure_execution_mode'
    file_content = re.sub(method_pattern, f"{configure_output_updated}\n    \n    def configure_execution_mode", file_content, flags=re.DOTALL)
    
    # Update the preview_command method for better reporting explanation
    method_pattern = r'# Output\s+command_summary \+= f"- Generate output in \{self\.params\[\'output_format\'\]\} format\\n'
    file_content = re.sub(method_pattern, enhanced_reporting_explanation, file_content)
    
    return file_content


def apply_combined_improvements():
    """Apply all Phase 2 improvements to command_wizard.py."""
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get the path to command_wizard.py (root project directory)
    command_wizard_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))), 'command_wizard.py')
    
    # Create a backup of command_wizard.py
    backup_path = command_wizard_path + '.phase2.backup'
    shutil.copy2(command_wizard_path, backup_path)
    print(f"Created backup of command_wizard.py at {backup_path}")
    
    # Read the current content
    with open(command_wizard_path, 'r') as f:
        file_content = f.read()
    
    # Apply all improvements
    file_content = apply_model_selection_improvements(file_content)
    file_content = apply_parameter_mapping_improvements(file_content)
    file_content = apply_config_integration_improvements(file_content)
    file_content = apply_reporting_integration_improvements(file_content)
    
    # Write the updated content
    with open(command_wizard_path, 'w') as f:
        f.write(file_content)
    
    print(f"Applied all Phase 2 improvements to {command_wizard_path}")
    

if __name__ == "__main__":
    # Apply all Phase 2 improvements
    apply_combined_improvements()