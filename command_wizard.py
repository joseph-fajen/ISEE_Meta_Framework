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
    def _get_timestamped_output_dir(self) -> str:
        """Generate a timestamped output directory path.
        
        Returns:
            Path to the timestamped output directory.
        """
        # Match the format used in main.py
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join("data", "output", f"run_{timestamp}")
    
    def _choose_output_directory(self) -> Optional[str]:
        """Allow the user to choose an output directory.
        
        Returns:
            Selected output directory or None to use the default.
        """
        # Default directory
        default_dir = self._get_timestamped_output_dir()
        
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Output Directory[/bold cyan]")
            
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
            print("\nOutput Directory")
            
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
    
    def _select_report_format(self) -> str:
        """Allow the user to select the report format.
        
        Returns:
            Selected report format.
        """
        formats = ["markdown", "json"]
        
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Report Format[/bold cyan]")
            
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
            print("\nReport Format")
            
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
    
    def _configure_visualization_options(self) -> Tuple[bool, bool]:
        """Configure visualization options.
        
        Returns:
            Tuple of (export_csv, no_visualizations).
        """
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Visualization Options[/bold cyan]")
            
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
            print("\nVisualization Options")
            
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
    
    
    def show_welcome(self) -> None:
        """Display welcome message and API status."""
        if RICH_AVAILABLE:
            self.console.print(Panel.fit(
                "[bold blue]ISEE Command Construction Wizard[/bold blue]\n\n"
                "This wizard will guide you through creating an ISEE command with the right parameters.",
                title="Welcome",
                border_style="blue"
            ))
            
            # Show API status
            api_table = Table(title="API Status")
            api_table.add_column("Provider", style="cyan")
            api_table.add_column("Status", style="green")
            
            api_table.add_row("Anthropic API", "✅ Available" if self.api_status["anthropic"] else "❌ Not found")
            api_table.add_row("OpenAI API", "✅ Available" if self.api_status["openai"] else "❌ Not found")
            api_table.add_row("Google API", "✅ Available" if self.api_status["google"] else "❌ Not found")
            
            if self.api_status["ollama"]:
                models_str = ", ".join(self.api_status.get("ollama_models", [])[:3])
                if len(self.api_status.get("ollama_models", [])) > 3:
                    models_str += f" (+{len(self.api_status.get('ollama_models', [])) - 3} more)"
                api_table.add_row("Ollama", f"✅ Available ({models_str})")
            else:
                api_table.add_row("Ollama", "❌ Not running or no models")
            
            self.console.print(api_table)
            
            # Show simulation mode notice if no APIs are available
            if not self.api_status["any_api"] and not self.api_status["ollama"]:
                self.console.print(Panel(
                    "[yellow]No API providers detected. The wizard will use simulation mode.[/yellow]",
                    border_style="yellow"
                ))
        else:
            print("="*70)
            print("ISEE Command Construction Wizard")
            print("="*70)
            print("This wizard will guide you through creating an ISEE command with the right parameters.")
            print()
            
            print("API Status:")
            print(f"Anthropic API: {'Available' if self.api_status['anthropic'] else 'Not found'}")
            print(f"OpenAI API: {'Available' if self.api_status['openai'] else 'Not found'}")
            print(f"Google API: {'Available' if self.api_status['google'] else 'Not found'}")
            
            if self.api_status["ollama"]:
                models_str = ", ".join(self.api_status.get("ollama_models", [])[:3])
                if len(self.api_status.get("ollama_models", [])) > 3:
                    models_str += f" (+{len(self.api_status.get('ollama_models', [])) - 3} more)"
                print(f"Ollama: Available ({models_str})")
            else:
                print("Ollama: Not running or no models")
            
            if not self.api_status["any_api"] and not self.api_status["ollama"]:
                print("\nWARNING: No API providers detected. The wizard will use simulation mode.")
            
            print("-"*70)
            
    def get_query(self) -> str:
        """Get the innovation query from the user.
        
        Returns:
            The query string.
        """
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Step 1: Define Your Innovation Challenge[/bold cyan]")
            query = Prompt.ask(
                "What innovation challenge would you like to explore?",
                default="How might we improve urban transportation?"
            )
        else:
            print("\nStep 1: Define Your Innovation Challenge")
            query = input("What innovation challenge would you like to explore? [How might we improve urban transportation?]: ")
            if not query:
                query = "How might we improve urban transportation?"
        
        self.params["query"] = query
        return query
    
    def select_domain(self) -> Optional[str]:
        """Allow the user to select a domain.
        
        Returns:
            The selected domain name or None if no domain is selected.
        """
        domains = self.domain_manager.list_domains()
        domain_names = [domain.name for domain in domains]
        
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Step 2: Select Problem Domain[/bold cyan]")
            
            # Display domains in a table
            domain_table = Table(title="Available Domains")
            domain_table.add_column("Domain", style="cyan")
            domain_table.add_column("Description")
            
            for domain in domains:
                domain_table.add_row(domain.name, domain.description)
            
            self.console.print(domain_table)
            
            # Ask if the user wants to specify a domain
            use_domain = Confirm.ask("Would you like to specify a domain for your query?", default=True)
            
            if use_domain:
                print("Available domains:")
                for i, name in enumerate(domain_names, 1):
                    print(f"{i}. {name}")
                
                while True:
                    choice = IntPrompt.ask(
                        "Select a domain by number (or 0 to skip)",
                        default=0,
                        show_default=True
                    )
                    
                    if choice == 0:
                        return None
                    
                    if 1 <= choice <= len(domain_names):
                        selected_domain = domain_names[choice - 1]
                        self.params["domain"] = selected_domain
                        return selected_domain
                    
                    self.console.print("[yellow]Invalid selection. Please try again.[/yellow]")
            else:
                return None
        else:
            print("\nStep 2: Select Problem Domain")
            print("Available domains:")
            
            for i, name in enumerate(domain_names, 1):
                print(f"{i}. {name}")
            
            print("0. No specific domain (use all)")
            
            while True:
                try:
                    choice = int(input("Select a domain by number (or 0 to skip): ") or "0")
                    
                    if choice == 0:
                        return None
                    
                    if 1 <= choice <= len(domain_names):
                        selected_domain = domain_names[choice - 1]
                        self.params["domain"] = selected_domain
                        return selected_domain
                    
                    print("Invalid selection. Please try again.")
                except ValueError:
                    print("Please enter a number.")
    
    
    def _get_provider_diverse_models(self, model_count: int) -> List[str]:
        """Select models ensuring diversity across providers.
        
        Args:
            model_count: Number of models to select.
            
        Returns:
            List of model IDs ensuring provider diversity.
        """
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
    
    
    def configure_models(self) -> Tuple[int, bool, bool]:
        """Configure model selection parameters.
        
        Returns:
            Tuple of (model_count, use_ollama, balanced_models)
        """
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Step 3: Configure Model Selection[/bold cyan]")
            
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
            self.console.print("\n[cyan]Selected Models:[/cyan]")
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
            print("\nStep 3: Configure Model Selection")
            
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
            print("\nSelected Models:")
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
    
    def configure_cognitive_diversity(self) -> Tuple[int, int, Optional[List[str]]]:
        """Configure cognitive diversity parameters.
        
        Returns:
            Tuple of (instruction_count, variation_count, specific_templates)
        """
        # Get available templates
        templates = self.template_library.list_templates()
        template_names = [template.name for template in templates]
        template_ids = [template.id for template in templates]
        
        # Dictionary mapping template index to template ID
        template_index_to_id = {i+1: template_id for i, template_id in enumerate(template_ids)}
        
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Step 4: Configure Cognitive Diversity[/bold cyan]")
            
            # Display available cognitive approaches with numbers
            templates_table = Table(title="Available Cognitive Approaches")
            templates_table.add_column("#", style="green")
            templates_table.add_column("Approach", style="cyan")
            templates_table.add_column("Description")
            
            for i, template in enumerate(templates, 1):
                templates_table.add_row(
                    str(i),
                    template.name, 
                    f"{template.metadata.get('strength', 'N/A')}"
                )
            
            self.console.print(templates_table)
            
            # Ask if the user wants to select specific approaches
            use_specific = Confirm.ask(
                "Would you like to select specific cognitive approaches?",
                default=False
            )
            
            specific_templates = None
            if use_specific:
                # Allow selection of specific templates
                while True:
                    selection_input = Prompt.ask(
                        "Enter the numbers of the approaches you want to use (comma-separated, e.g., '1,3,7,9')"
                    )
                    
                    try:
                        # Parse the input into a list of numbers
                        selections = [int(x.strip()) for x in selection_input.split(",")]
                        
                        # Validate selections
                        if not selections:
                            self.console.print("[yellow]Please select at least one approach.[/yellow]")
                            continue
                            
                        invalid_selections = [s for s in selections if s < 1 or s > len(templates)]
                        if invalid_selections:
                            self.console.print(f"[yellow]Invalid selections: {', '.join(map(str, invalid_selections))}. Please enter numbers between 1 and {len(templates)}.[/yellow]")
                            continue
                        
                        # Convert selections to template IDs
                        specific_templates = [template_index_to_id[s] for s in selections]
                        instruction_count = len(specific_templates)
                        
                        # Show selected templates
                        self.console.print(f"[green]Selected {instruction_count} approaches: {', '.join([template_names[i-1] for i in selections])}[/green]")
                        break
                    except ValueError:
                        self.console.print("[yellow]Invalid input. Please enter numbers separated by commas.[/yellow]")
            else:
                # Just determine the count
                instruction_count = IntPrompt.ask(
                    "How many different cognitive approaches would you like to use?",
                    default=3,
                    show_default=True
                )
            
            # Determine variation count
            variation_count = IntPrompt.ask(
                "How many query variations would you like to generate?",
                default=2,
                show_default=True
            )
        else:
            print("\nStep 4: Configure Cognitive Diversity")
            
            # Display available cognitive approaches with numbers
            print("Available Cognitive Approaches:")
            
            for i, (name, template) in enumerate(zip(template_names, templates), 1):
                print(f"{i}. {name} ({template.metadata.get('strength', 'N/A')})")
            
            # Ask if the user wants to select specific approaches
            use_specific_input = input("Would you like to select specific cognitive approaches? (y/n) [n]: ").lower()
            use_specific = use_specific_input in ["y", "yes"]
            
            specific_templates = None
            if use_specific:
                # Allow selection of specific templates
                while True:
                    selection_input = input("Enter the numbers of the approaches you want to use (comma-separated, e.g., '1,3,7,9'): ")
                    
                    try:
                        # Parse the input into a list of numbers
                        selections = [int(x.strip()) for x in selection_input.split(",")]
                        
                        # Validate selections
                        if not selections:
                            print("Please select at least one approach.")
                            continue
                            
                        invalid_selections = [s for s in selections if s < 1 or s > len(templates)]
                        if invalid_selections:
                            print(f"Invalid selections: {', '.join(map(str, invalid_selections))}. Please enter numbers between 1 and {len(templates)}.")
                            continue
                        
                        # Convert selections to template IDs
                        specific_templates = [template_index_to_id[s] for s in selections]
                        instruction_count = len(specific_templates)
                        
                        # Show selected templates
                        print(f"Selected {instruction_count} approaches: {', '.join([template_names[i-1] for i in selections])}")
                        break
                    except ValueError:
                        print("Invalid input. Please enter numbers separated by commas.")
            else:
                # Just determine the count
                while True:
                    try:
                        instruction_input = input("How many different cognitive approaches would you like to use? [3]: ")
                        instruction_count = int(instruction_input) if instruction_input else 3
                        if instruction_count < 1:
                            print("Please enter a positive number.")
                            continue
                        break
                    except ValueError:
                        print("Please enter a number.")
            
            # Determine variation count
            while True:
                try:
                    variation_input = input("How many query variations would you like to generate? [2]: ")
                    variation_count = int(variation_input) if variation_input else 2
                    if variation_count < 1:
                        print("Please enter a positive number.")
                        continue
                    break
                except ValueError:
                    print("Please enter a number.")
        
        self.params["instructions"] = instruction_count
        self.params["variations"] = variation_count
        self.params["specific_templates"] = specific_templates
        
        return instruction_count, variation_count, specific_templates
    
    def configure_execution(self) -> Tuple[int, str, str]:
        """Configure execution parameters.
        
        Returns:
            Tuple of (max_combinations, sampling_method, synthesis_method)
        """
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Step 5: Configure Execution Parameters[/bold cyan]")
            
            # Calculate default max combinations based on other parameters
            total_combinations = self.params["models"] * self.params["instructions"] * self.params["variations"]
            
            # Determine reasonable default and limits
            if total_combinations > 100:
                if RICH_AVAILABLE:
                    self.console.print(f"[yellow]Warning: Your current settings would generate {total_combinations} combinations, which may take a long time to execute.[/yellow]")
                
                # Recommend stratified sampling with a reasonable limit
                suggested_limit = min(total_combinations, 50)  # Suggest at most 50 combinations
                
                # Ask if the user wants to limit combinations (default to yes for large numbers)
                use_max = True  # Force limit for large combination counts
            else:
                # For smaller combination counts, ask if they want to limit
                use_max = Confirm.ask(
                    f"Would you like to limit the total number of combinations? (Default: all {total_combinations} combinations)",
                    default=total_combinations > 36
                )
            
            max_combinations = None
            if use_max:
                # For large combination counts, suggest a lower default
                if total_combinations > 100:
                    suggested_default = min(50, total_combinations)
                    # Also suggest stratified sampling
                    self.console.print("[dim](For large combination counts, stratified sampling is recommended.)[/dim]")
                else:
                    suggested_default = min(total_combinations, 36)
                
                max_combinations = IntPrompt.ask(
                    "Maximum number of combinations to execute",
                    default=suggested_default,
                    show_default=True
                )
            
            # Sampling method selection with definitions
            sampling_methods = {
                "1": {
                    "name": "exhaustive",
                    "definition": "Tries all possible combinations (can be very large)"
                },
                "2": {
                    "name": "stratified",
                    "definition": "Ensures balanced representation across all dimensions while reducing total combinations"
                },
                "3": {
                    "name": "adaptive",
                    "definition": "Falls back to stratified sampling currently (placeholder for future implementation)"
                }
            }
            
            self.console.print("\nSampling Methods:")
            for key, value in sampling_methods.items():
                self.console.print(f"  {key}. [cyan]{value['name']}[/cyan]: {value['definition']}")
            
            # Default to stratified sampling for large combination counts
            if total_combinations > 100 and max_combinations:
                default_sampling = "2"  # stratified
            else:
                default_sampling = "1" if not max_combinations else "2"
                
            sampling_choice = Prompt.ask(
                "Select sampling method",
                choices=["1", "2", "3"],
                default=default_sampling
            )
            sampling_method = sampling_methods[sampling_choice]["name"]
            
            # Synthesis method selection with definitions
            synthesis_methods = {
                "1": {
                    "name": "cluster_based",
                    "definition": "Groups similar ideas into clusters and presents representative ideas from each cluster"
                },
                "2": {
                    "name": "cross_pollination",
                    "definition": "Attempts to combine elements from top results (currently has placeholder functionality)"
                }
            }
            
            self.console.print("\nSynthesis Methods:")
            for key, value in synthesis_methods.items():
                self.console.print(f"  {key}. [cyan]{value['name']}[/cyan]: {value['definition']}")
            
            synthesis_choice = Prompt.ask(
                "Select synthesis method",
                choices=["1", "2"],
                default="1"
            )
            synthesis_method = synthesis_methods[synthesis_choice]["name"]
        else:
            print("\nStep 5: Configure Execution Parameters")
            
            # Calculate total combinations based on other parameters
            total_combinations = self.params["models"] * self.params["instructions"] * self.params["variations"]
            
            # Determine reasonable default and limits
            use_max = False
            if total_combinations > 100:
                print(f"Warning: Your current settings would generate {total_combinations} combinations, which may take a long time to execute.")
                
                # Force limit for large combination counts
                use_max = True
                print("A limit on combinations will be applied.")
            else:
                # For smaller combination counts, ask if they want to limit
                use_max_input = input(f"Would you like to limit the total number of combinations? (Default: all {total_combinations} combinations) (y/n) [{('y' if total_combinations > 36 else 'n')}]: ").lower()
                if not use_max_input:
                    use_max = total_combinations > 36
                else:
                    use_max = use_max_input in ["y", "yes"]
            
            max_combinations = None
            if use_max:
                # For large combination counts, suggest a lower default
                if total_combinations > 100:
                    suggested_default = min(50, total_combinations)
                    # Also suggest stratified sampling
                    print("(For large combination counts, stratified sampling is recommended.)")
                else:
                    suggested_default = min(total_combinations, 36)
                
                while True:
                    try:
                        max_input = input(f"Maximum number of combinations to execute [{suggested_default}]: ")
                        max_combinations = int(max_input) if max_input else suggested_default
                        if max_combinations < 1:
                            print("Please enter a positive number.")
                            continue
                        break
                    except ValueError:
                        print("Please enter a number.")
            
            # Sampling method selection with definitions
            print("\nSampling Methods:")
            print("  1. exhaustive: Tries all possible combinations (can be very large)")
            print("  2. stratified: Ensures balanced representation across all dimensions while reducing total combinations")
            print("  3. adaptive: Falls back to stratified sampling currently (placeholder for future implementation)")
            
            # Default to stratified sampling for large combination counts
            if total_combinations > 100 and max_combinations:
                default_sampling_choice = "2"  # stratified
                default_sampling_text = "2"
            else:
                default_sampling_choice = "1" if not max_combinations else "2"
                default_sampling_text = "1 if no limit, 2 if limited"
                
            while True:
                sampling_choice = input(f"Select sampling method [{default_sampling_text}]: ")
                if sampling_choice == "":
                    sampling_choice = default_sampling_choice
                
                if sampling_choice in ["1", "2", "3"]:
                    break
                print("Invalid selection. Please try again.")
            
            sampling_method_map = {
                "1": "exhaustive",
                "2": "stratified",
                "3": "adaptive"
            }
            sampling_method = sampling_method_map[sampling_choice]
            
            # Synthesis method selection with definitions
            print("\nSynthesis Methods:")
            print("  1. cluster_based: Groups similar ideas into clusters and presents representative ideas from each cluster")
            print("  2. cross_pollination: Attempts to combine elements from top results (currently has placeholder functionality)")
            
            while True:
                synthesis_choice = input("Select synthesis method [1]: ")
                if synthesis_choice == "":
                    synthesis_choice = "1"
                
                if synthesis_choice in ["1", "2"]:
                    break
                print("Invalid selection. Please try again.")
            
            synthesis_method_map = {
                "1": "cluster_based",
                "2": "cross_pollination"
            }
            synthesis_method = synthesis_method_map[synthesis_choice]
        
        self.params["max_combinations"] = max_combinations
        self.params["sampling_method"] = sampling_method
        self.params["synthesize_method"] = synthesis_method
        
        return max_combinations, sampling_method, synthesis_method
    
    
    def configure_output(self) -> Tuple[str, Optional[str], bool, bool]:
        """Configure output parameters.
        
        Returns:
            Tuple of (output_format, output_file, generate_reports, analyze_results)
        """
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Step 6: Configure Output Options[/bold cyan]")
            
            # Output format selection
            output_formats = {
                "1": "markdown",
                "2": "json"
            }
            
            self.console.print("\nOutput Formats:")
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
            print("\nStep 6: Configure Output Options")
            
            # Output format selection
            print("\nOutput Formats:")
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
    
    
    def configure_execution_mode(self) -> Tuple[bool, bool, Optional[str]]:
        """Configure execution mode parameters.
        
        Returns:
            Tuple of (simulate, dry_run, save_state)
        """
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Step 7: Configure Execution Mode[/bold cyan]")
            
            # Determine if simulation should be used
            simulate = False
            if not self.api_status["any_api"] and not self.api_status["ollama"]:
                self.console.print("[yellow]No API providers detected. Simulation mode will be used.[/yellow]")
                simulate = True
            else:
                simulate = Confirm.ask(
                    "Use simulation mode (no real API calls)?",
                    default=False
                )
            
            # Determine if this should be a dry run
            dry_run = Confirm.ask(
                "Run in dry-run mode (preview execution without running)?",
                default=False
            )
            
            # Determine if state should be saved
            save_state = Confirm.ask(
                "Save state for later continuation?",
                default=False
            )
            
            state_file = None
            if save_state:
                state_file = Prompt.ask(
                    "Enter state filename",
                    default="isee_state.json"
                )
        else:
            print("\nStep 7: Configure Execution Mode")
            
            # Determine if simulation should be used
            simulate = False
            if not self.api_status["any_api"] and not self.api_status["ollama"]:
                print("No API providers detected. Simulation mode will be used.")
                simulate = True
            else:
                simulate_input = input("Use simulation mode (no real API calls)? (y/n) [n]: ").lower()
                simulate = simulate_input in ["y", "yes"]
            
            # Determine if this should be a dry run
            dry_run_input = input("Run in dry-run mode (preview execution without running)? (y/n) [n]: ").lower()
            dry_run = dry_run_input in ["y", "yes"]
            
            # Determine if state should be saved
            save_state_input = input("Save state for later continuation? (y/n) [n]: ").lower()
            save_state = save_state_input in ["y", "yes"]
            
            state_file = None
            if save_state:
                state_file = input("Enter state filename [isee_state.json]: ")
                if not state_file:
                    state_file = "isee_state.json"
        
        self.params["simulate"] = simulate
        self.params["dry_run"] = dry_run
        self.params["save_state"] = state_file
        
        return simulate, dry_run, state_file
    
    
    def generate_command(self) -> str:
        """Generate the ISEE command based on user selections.
        
        Returns:
            The generated command string.
        """
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
    
    
    def preview_command(self, command: str) -> None:
        """Preview the generated command.
        
        Args:
            command: The generated command string.
        """
        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]Command Preview[/bold cyan]")
            
            # Display the command in a panel
            if hasattr(self, 'specific_templates_comment') and self.specific_templates_comment:
                # If specific templates were selected, show them in a comment above the command
                display_command = f"{self.specific_templates_comment}\n{command}"
                self.console.print(Panel(
                    display_command,
                    title="Generated Command (with template selections as comment)",
                    border_style="green"
                ))
            else:
                self.console.print(Panel(
                    command,
                    title="Generated Command",
                    border_style="green"
                ))
            
        # Display config file usage information
        if self.params.get("config_file") or hasattr(self, 'using_unified_config') and self.using_unified_config:
            config_file = self.params.get("config_file", "unified_config.json")
            
            if RICH_AVAILABLE:
                self.console.print(Panel(
                    f"[green]Using {config_file} for model configuration[/green]\n\n"
                    "The configuration file maps model IDs to actual API providers and includes:\n"
                    "- Model names and versions\n"
                    "- API provider information\n"
                    "- Model-specific parameters\n\n"
                    "This ensures the correct models are used for each API provider.",
                    title="Configuration Information",
                    border_style="green"
                ))
            else:
                print(f"\nCONFIGURATION INFORMATION:")
                print(f"Using {config_file} for model configuration")
                print("The configuration file maps model IDs to actual API providers and includes:")
                print("- Model names and versions")
                print("- API provider information")
                print("- Model-specific parameters")
                print("\nThis ensures the correct models are used for each API provider.")
                print("-" * 70)
    
            
            # Explain what the command will do
            command_summary = "This command will:\n"
            
            # Basic parameters
            command_summary += f"- Process the query: \"{self.params['query']}\"\n"
            
            # Model configuration with provider diversity
            if hasattr(self, 'selected_model_names') and self.selected_model_names:
                selected_models_str = ", ".join(self.selected_model_names)
                command_summary += f"- Use {len(self.selected_models)} different models ({selected_models_str})\n"
            else:
                command_summary += f"- Use {self.params['models']} different models\n"
            
            if self.params["domain"]:
                command_summary += f"- In the domain: {self.params['domain']}\n"
            else:
                command_summary += "- Using all available domains\n"
            
            # Add unified config note to summary
            
        # Display config file usage information
        if self.params.get("config_file") or hasattr(self, 'using_unified_config') and self.using_unified_config:
            config_file = self.params.get("config_file", "unified_config.json")
            
            if RICH_AVAILABLE:
                self.console.print(Panel(
                    f"[green]Using {config_file} for model configuration[/green]\n\n"
                    "The configuration file maps model IDs to actual API providers and includes:\n"
                    "- Model names and versions\n"
                    "- API provider information\n"
                    "- Model-specific parameters\n\n"
                    "This ensures the correct models are used for each API provider.",
                    title="Configuration Information",
                    border_style="green"
                ))
            else:
                print(f"\nCONFIGURATION INFORMATION:")
                print(f"Using {config_file} for model configuration")
                print("The configuration file maps model IDs to actual API providers and includes:")
                print("- Model names and versions")
                print("- API provider information")
                print("- Model-specific parameters")
                print("\nThis ensures the correct models are used for each API provider.")
                print("-" * 70)
    
            
            # Explain what the command will do
            print("\nThis command will:")
            
            # Basic parameters
            print(f"- Process the query: \"{self.params['query']}\"")
            
            if self.params["domain"]:
                print(f"- In the domain: {self.params['domain']}")
            else:
                print("- Using all available domains")
            
            # Model configuration
            print(f"- Use {self.params['models']} different models", end="")
            if self.params["use_ollama"]:
                print(" (including Ollama models)")
            else:
                print()
            
            # Add unified config note to summary
            if hasattr(self, 'using_unified_config') and self.using_unified_config:
                print("- Use real model API calls with unified_config.json mapping")
            elif not self.params["simulate"]:
                print("- [Note: Without --config, models may default to simulation]")
            
            if self.params["balanced_models"]:
                print("- Ensure balanced representation of models across combinations")
            
            # Cognitive diversity
            if self.params.get("specific_templates"):
                instruction_count = len(self.params["specific_templates"])
                print(f"- Apply {instruction_count} specific cognitive approaches (user-selected)")
            else:
                print(f"- Apply {self.params['instructions']} different cognitive approaches")
            print(f"- Generate {self.params['variations']} variations of your query")
            
            # Execution
            if self.params["max_combinations"]:
                print(f"- Execute up to {self.params['max_combinations']} combinations")
            else:
                total_combinations = self.params["models"] * self.params["instructions"] * self.params["variations"]
                print(f"- Execute all {total_combinations} possible combinations")
            
            print(f"- Use {self.params['sampling_method']} sampling method")
            print(f"- Use {self.params['synthesize_method']} synthesis method")
            
            # Output
            print(f"- Generate output in {self.params['output_format']} format")
            
            if self.params["output_file"]:
                print(f"- Save output to {self.params['output_file']}")
            else:
                print("- Save output to an automatically generated file")
            
            if self.params["generate_reports"]:
                print("- Generate detailed reports")
                
                if self.params["analyze_results"]:
                    print("- Perform analysis with visualizations")
            
            # Execution mode
            if self.params["simulate"]:
                print("- Run in simulation mode (no API calls)")
            
            if self.params["dry_run"]:
                print("- Run in dry-run mode (preview only)")
            
            if self.params["save_state"]:
                print(f"- Save state to {self.params['save_state']} for later continuation")
    
    def execute_command(self, command: str) -> bool:
        """Execute the generated command.
        
        Args:
            command: The command to execute.
            
        Returns:
            True if the command was executed, False otherwise.
        """
        if RICH_AVAILABLE:
            execute = Confirm.ask(
                "\nWould you like to execute this command now?",
                default=True
            )
        else:
            execute_input = input("\nWould you like to execute this command now? (y/n) [y]: ").lower()
            execute = execute_input in ["", "y", "yes"]
        
        if execute:
            if RICH_AVAILABLE:
                self.console.print("\n[bold green]Executing command...[/bold green]")
            else:
                print("\nExecuting command...")
            
            try:
                # Execute the command
                result = subprocess.run(command, shell=True)
                
                if result.returncode == 0:
                    if RICH_AVAILABLE:
                        self.console.print("\n[bold green]Command executed successfully![/bold green]")
                    else:
                        print("\nCommand executed successfully!")
                else:
                    if RICH_AVAILABLE:
                        self.console.print(f"\n[bold red]Command failed with exit code {result.returncode}[/bold red]")
                    else:
                        print(f"\nCommand failed with exit code {result.returncode}")
                
                return True
            except Exception as e:
                if RICH_AVAILABLE:
                    self.console.print(f"\n[bold red]Error executing command: {str(e)}[/bold red]")
                else:
                    print(f"\nError executing command: {str(e)}")
                return False
        else:
            if RICH_AVAILABLE:
                self.console.print("\nCommand not executed. You can run it manually using the command above.")
            else:
                print("\nCommand not executed. You can run it manually using the command above.")
            return False
    
    def copy_to_clipboard(self, command: str) -> bool:
        """Copy the command to the clipboard.
        
        Args:
            command: The command to copy.
            
        Returns:
            True if the command was copied, False otherwise.
        """
        try:
            # Try platform-specific clipboard commands
            if sys.platform == "darwin":  # macOS
                process = subprocess.Popen(
                    "pbcopy", env={"LANG": "en_US.UTF-8"}, stdin=subprocess.PIPE
                )
                process.communicate(command.encode("utf-8"))
                return True
            elif sys.platform == "win32":  # Windows
                process = subprocess.Popen(
                    "clip", stdin=subprocess.PIPE
                )
                process.communicate(command.encode("utf-8"))
                return True
            else:  # Linux/Unix
                try:
                    process = subprocess.Popen(
                        ["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE
                    )
                    process.communicate(command.encode("utf-8"))
                    return True
                except FileNotFoundError:
                    try:
                        process = subprocess.Popen(
                            ["xsel", "--clipboard", "--input"], stdin=subprocess.PIPE
                        )
                        process.communicate(command.encode("utf-8"))
                        return True
                    except FileNotFoundError:
                        return False
        except Exception:
            return False
    
    
    def run_wizard(self) -> None:
        """Run the complete wizard flow."""
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
                self.console.print("\n[bold red]Parameter Validation Issues:[/bold red]")
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
                print("\nParameter Validation Issues:")
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
            self.console.print("\n[green]Command copied to clipboard![/green]")
        elif clipboard_success:
            print("\nCommand copied to clipboard!")
        
        # Execute the command if requested
        self.execute_command(command)
    


def main():
    """Main entry point for the command wizard."""
    parser = argparse.ArgumentParser(description="ISEE Command Construction Wizard")
    args = parser.parse_args()
    
    # Create and run the wizard
    wizard = CommandWizard()
    wizard.run_wizard()


if __name__ == "__main__":
    main()