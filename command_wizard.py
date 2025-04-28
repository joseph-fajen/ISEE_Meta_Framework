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
        # Implementation details
        pass
        
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
    
    def _validate_parameters(self) -> bool:
        """Validate all parameters before generating the command.
        
        Returns:
            True if all required parameters are valid, False otherwise.
        """
        # Check that required parameters are set
        if not self.params["query"]:
            if RICH_AVAILABLE:
                self.console.print("[bold red]Error:[/bold red] Query is required.")
            else:
                print("Error: Query is required.")
            return False
        
        # Validate template IDs if specified
        if self.params.get("instruction_templates"):
            template_ids = self.params["instruction_templates"].split(",")
            valid_template_ids = list(self.template_library.templates.keys())
            
            for template_id in template_ids:
                if template_id not in valid_template_ids:
                    if RICH_AVAILABLE:
                        self.console.print(f"[bold red]Error:[/bold red] Invalid template ID: {template_id}")
                    else:
                        print(f"Error: Invalid template ID: {template_id}")
                    return False
        
        return True
    
    def select_instruction_templates(self) -> None:
        """Allow the user to select specific instruction templates."""
        # Get all available templates
        templates = self.template_library.templates
        
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Instruction Template Selection[/bold cyan]")
            
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
        if not self._validate_parameters():
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
    
    def preview_command(self) -> None:
        """Preview the command that will be run."""
        command = self.generate_command()
        
        if not command:
            return
        
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Command Preview[/bold cyan]")
            
            # Create panel for command
            command_panel = Panel(
                command,
                title="Generated Command",
                border_style="green"
            )
            self.console.print(command_panel)
            
            # Show preview of what the command will do
            params_table = Table(title="Command Parameters")
            params_table.add_column("Parameter", style="cyan")
            params_table.add_column("Value", style="green")
            
            # Add core parameters to the table
            params_table.add_row("Query", self.params["query"] or "")
            params_table.add_row("Domain", self.params["domain"] or "Default")
            
            if "config_file" in self.params and self.params["config_file"]:
                params_table.add_row("Configuration", self.params["config_file"])
            
            # Show details about selected templates if any
            if self.params.get("instruction_templates"):
                template_ids = self.params["instruction_templates"].split(",")
                params_table.add_row("Instruction Templates", ", ".join(template_ids))
                
                # Get template details
                template_details = []
                for template_id in template_ids:
                    for template in self.template_library.templates:
                        if template.id == template_id:
                            template_details.append(f"• {template.name}: {template.description[:50]}...")
                
                if template_details:
                    params_table.add_row("Template Details", "\n".join(template_details))
            else:
                params_table.add_row("Number of Instructions", str(self.params["instructions"]))
            
            params_table.add_row("Number of Models", str(self.params["models"]))
            params_table.add_row("Number of Variations", str(self.params["variations"]))
            
            self.console.print(params_table)
        else:
            print("\nCommand Preview")
            print("Generated Command:")
            print(command)
            
            print("\nCommand Parameters:")
            print(f"Query: {self.params['query'] or ''}")
            print(f"Domain: {self.params['domain'] or 'Default'}")
            
            if "config_file" in self.params and self.params["config_file"]:
                print(f"Configuration: {self.params['config_file']}")
            
            # Show details about selected templates if any
            if self.params.get("instruction_templates"):
                template_ids = self.params["instruction_templates"].split(",")
                print(f"Instruction Templates: {', '.join(template_ids)}")
                
                # Get template details
                print("Template Details:")
                for template_id in template_ids:
                    for template in self.template_library.templates:
                        if template.id == template_id:
                            print(f"• {template.name}: {template.description[:50]}...")
            else:
                print(f"Number of Instructions: {self.params['instructions']}")
            
            print(f"Number of Models: {self.params['models']}")
            print(f"Number of Variations: {self.params['variations']}")
    
    def main(self):
        """Main entry point for the command wizard."""
        # Welcome message
        if RICH_AVAILABLE:
            self.console.print("[bold green]ISEE Command Construction Wizard[/bold green]")
            self.console.print("This wizard helps you construct and run valid ISEE commands.\n")
        else:
            print("ISEE Command Construction Wizard")
            print("This wizard helps you construct and run valid ISEE commands.\n")
        
        # Step 1: Query
        if RICH_AVAILABLE:
            self.console.print("[bold cyan]Step 1: Query[/bold cyan]")
            query = Prompt.ask("Enter your query", default="")
            self.params["query"] = query if query else None
        else:
            print("Step 1: Query")
            query = input("Enter your query: ")
            self.params["query"] = query if query else None
        
        # Step 2: Select configuration file (optional)
        config_file = self._select_config_file()
        if config_file:
            self.params["config_file"] = config_file
        
        # Step 3: Domain selection
        domains = self.domain_manager.list_domains()
        domain_names = [domain.name for domain in domains]
        
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Step 3: Domain Selection[/bold cyan]")
            
            # Display available domains
            domains_table = Table(title="Available Domains")
            domains_table.add_column("#", style="green")
            domains_table.add_column("Domain", style="cyan")
            domains_table.add_column("Description")
            
            for i, domain in enumerate(domains, 1):
                domains_table.add_row(str(i), domain.name, domain.description[:50] + "..." if len(domain.description) > 50 else domain.description)
            
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
                
                self.console.print(f"Selected domain: [green]{selected_domain.name}[/green]")
                self.console.print(f"Description: {selected_domain.description}")
            else:
                self.console.print("Using default domain.")
        else:
            print("\nStep 3: Domain Selection")
            print("Available Domains:")
            
            for i, domain in enumerate(domains, 1):
                print(f"{i}. {domain.name} - {domain.description[:50] + '...' if len(domain.description) > 50 else domain.description}")
            
            print("0. Default domain")
            
            try:
                domain_choice = int(input("Select a domain by number (or 0 for default) [0]: ") or "0")
                
                if domain_choice > 0 and domain_choice <= len(domains):
                    selected_domain = domains[domain_choice - 1]
                    self.params["domain"] = selected_domain.name
                    
                    print(f"Selected domain: {selected_domain.name}")
                    print(f"Description: {selected_domain.description}")
                else:
                    print("Using default domain.")
            except ValueError:
                print("Invalid selection. Using default domain.")
        
        # Step 4: Instruction template selection
        self.select_instruction_templates()
        
        # Step 5: Models selection
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Step 5: Model Selection[/bold cyan]")
            
            models_count = IntPrompt.ask(
                "How many models would you like to use?",
                default=2
            )
            self.params["models"] = models_count
            
            # Ask about model balance
            if models_count > 1:
                balanced_models = Confirm.ask(
                    "Would you like to balance models across API providers?",
                    default=True
                )
                self.params["balanced_models"] = balanced_models
            
            # Check for Ollama
            if self.api_status["ollama"]:
                use_ollama = Confirm.ask(
                    "Would you like to include Ollama models?",
                    default=False
                )
                self.params["use_ollama"] = use_ollama
        else:
            print("\nStep 5: Model Selection")
            
            try:
                models_count_input = input("How many models would you like to use? [2]: ")
                models_count = int(models_count_input) if models_count_input else 2
                self.params["models"] = models_count
                
                # Ask about model balance
                if models_count > 1:
                    balanced_models_input = input("Would you like to balance models across API providers? (y/n) [y]: ").lower()
                    balanced_models = balanced_models_input in ["", "y", "yes"] if balanced_models_input else True
                    self.params["balanced_models"] = balanced_models
                
                # Check for Ollama
                if self.api_status["ollama"]:
                    use_ollama_input = input("Would you like to include Ollama models? (y/n) [n]: ").lower()
                    use_ollama = use_ollama_input in ["y", "yes"]
                    self.params["use_ollama"] = use_ollama
            except ValueError:
                print("Invalid input. Using default value (2 models).")
                self.params["models"] = 2
        
        # Step 6: Variations
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Step 6: Variations[/bold cyan]")
            
            variations_count = IntPrompt.ask(
                "How many variations would you like for each instruction?",
                default=2
            )
            self.params["variations"] = variations_count
        else:
            print("\nStep 6: Variations")
            
            try:
                variations_count_input = input("How many variations would you like for each instruction? [2]: ")
                variations_count = int(variations_count_input) if variations_count_input else 2
                self.params["variations"] = variations_count
            except ValueError:
                print("Invalid input. Using default value (2 variations).")
                self.params["variations"] = 2
        
        # Step 7: Sampling method
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Step 7: Sampling Method[/bold cyan]")
            
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
            run_command = Confirm.ask(
                "Run this command?",
                default=True
            )
            
            if run_command:
                command = self.generate_command()
                self.console.print(f"[bold green]Running:[/bold green] {command}")
                
                # Execute the command
                try:
                    subprocess.run(command, shell=True, check=True)
                    self.console.print("[bold green]Command completed successfully.[/bold green]")
                except subprocess.CalledProcessError as e:
                    self.console.print(f"[bold red]Error:[/bold red] {str(e)}")
            else:
                # Show additional options
                self._show_help_options()
        else:
            run_command_input = input("Run this command? (y/n) [y]: ").lower()
            run_command = run_command_input in ["", "y", "yes"] if run_command_input else True
            
            if run_command:
                command = self.generate_command()
                print(f"Running: {command}")
                
                # Execute the command
                try:
                    subprocess.run(command, shell=True, check=True)
                    print("Command completed successfully.")
                except subprocess.CalledProcessError as e:
                    print(f"Error: {str(e)}")
            else:
                # Show additional options
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