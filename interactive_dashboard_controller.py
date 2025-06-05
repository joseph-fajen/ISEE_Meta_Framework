"""
Interactive Dashboard Controller for ISEE Framework

This module provides interactive controls and real-time parameter adjustment
capabilities for the Configuration Dashboard.

Part of UX Enhancement Roadmap - Step 3.2: Simple Configuration Dashboard
"""

from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import time

# Rich imports for interactive UI
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich import box

# Import dashboard components
try:
    from configuration_dashboard import ConfigurationDashboard, DashboardMode, ParameterStatus
    from parameter_context import PARAMETER_CATEGORIES
    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False

class InteractionMode(Enum):
    """Dashboard interaction modes"""
    NAVIGATE = "navigate"
    EDIT = "edit"
    EXECUTE = "execute"

class InteractiveDashboardController:
    """Controller for interactive dashboard operations and real-time updates"""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize the interactive controller.
        
        Args:
            console: Rich console instance. If None, creates a new one.
        """
        self.console = console or Console()
        
        if DASHBOARD_AVAILABLE:
            self.dashboard = ConfigurationDashboard(self.console)
        else:
            self.dashboard = None
            self.console.print("[red]Error: Dashboard components not available[/]")
        
        self.interaction_mode = InteractionMode.NAVIGATE
        self.live_display = None
        self.running = False
        
        # Interactive controls mapping
        self.controls = {
            "1": self._switch_to_overview,
            "2": self._switch_to_detailed,
            "3": self._switch_to_expert,
            "e": self._edit_parameters,
            "r": self._reset_parameters,
            "p": self._preview_command,
            "x": self._execute_command,
            "h": self._show_help,
            "q": self._quit_dashboard
        }
        
        # Parameter editing controls
        self.edit_controls = {
            "query": self._edit_query,
            "domain": self._edit_domain,
            "models": self._edit_models,
            "instructions": self._edit_instructions,
            "instruction_templates": self._edit_instructions,  # Same method handles both
            "variations": self._edit_variations,
            "max_combinations": self._edit_max_combinations,
            "sampling_method": self._edit_sampling_method,
            "balanced_models": self._toggle_balanced_models,
            "use_ollama": self._toggle_use_ollama,
            "openrouter_filters": self._edit_openrouter_filters,
            "simulate": self._toggle_simulate,
            "dry_run": self._toggle_dry_run,
            "quick": self._toggle_quick,
            "full": self._toggle_full,
            "output_format": self._edit_output_format,
            "generate_reports": self._toggle_generate_reports,
            "analyze_results": self._toggle_analyze_results
        }
    
    def run_interactive_dashboard(self) -> Optional[str]:
        """Run the interactive dashboard with live updates.
        
        Returns:
            Generated command string if executed, None if cancelled
        """
        if not self.dashboard:
            return None
        
        self.running = True
        
        try:
            # Main interaction loop
            while self.running:
                self._display_current_state()
                command = self._get_user_input()
                
                if command in self.controls:
                    result = self.controls[command]()
                    if result:  # Command execution returns the command string
                        return result
                else:
                    self._handle_invalid_input(command)
                    
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Dashboard cancelled by user[/]")
        except Exception as e:
            self.console.print(f"\n[red]Dashboard error: {str(e)}[/]")
        
        return None
    
    def _display_current_state(self):
        """Display the current dashboard state"""
        self.console.clear()
        self.dashboard.display_dashboard(self.dashboard.state.mode)
        self._display_controls()
    
    def _display_controls(self):
        """Display available controls at the bottom"""
        controls_text = Text()
        controls_text.append("\nControls: ", style="bold")
        
        if self.interaction_mode == InteractionMode.NAVIGATE:
            controls_text.append("[1] Overview  ", style="cyan")
            controls_text.append("[2] Detailed  ", style="cyan") 
            controls_text.append("[3] Expert  ", style="cyan")
            controls_text.append("[E] Edit  ", style="green")
            controls_text.append("[R] Reset  ", style="yellow")
            controls_text.append("[P] Preview  ", style="magenta")
            controls_text.append("[X] Execute  ", style="bold green")
            controls_text.append("[H] Help  ", style="blue")
            controls_text.append("[Q] Quit", style="red")
        elif self.interaction_mode == InteractionMode.EDIT:
            controls_text.append("Enter parameter name to edit, or 'done' to finish", style="green")
        
        self.console.print(controls_text)
    
    def _get_user_input(self) -> str:
        """Get user input with appropriate prompt"""
        if self.interaction_mode == InteractionMode.NAVIGATE:
            return Prompt.ask("Command").lower().strip()
        elif self.interaction_mode == InteractionMode.EDIT:
            return Prompt.ask("Parameter to edit").lower().strip()
        else:
            return Prompt.ask("Input").lower().strip()
    
    def _switch_to_overview(self):
        """Switch to overview mode"""
        self.dashboard.display_dashboard(DashboardMode.OVERVIEW)
    
    def _switch_to_detailed(self):
        """Switch to detailed mode"""
        self.dashboard.display_dashboard(DashboardMode.DETAILED)
    
    def _switch_to_expert(self):
        """Switch to expert mode"""
        self.dashboard.display_dashboard(DashboardMode.EXPERT)
    
    def _edit_parameters(self):
        """Enter parameter editing mode"""
        self.interaction_mode = InteractionMode.EDIT
        
        self.console.print("\n[bold green]Parameter Editing Mode[/]")
        self.console.print("Available parameters:")
        
        # Display available parameters by category
        for category_name, category_info in PARAMETER_CATEGORIES.items():
            color = self.dashboard.category_colors.get(category_name, "white")
            self.console.print(f"\n[bold {color}]{category_info['name']}:[/]")
            
            for param_name in category_info["parameters"]:
                if param_name in self.dashboard.state.parameters:
                    param = self.dashboard.state.parameters[param_name]
                    value_text = self.dashboard._format_parameter_value(param.value)
                    self.console.print(f"  {param_name}: {value_text}")
        
        # Parameter editing loop
        while self.interaction_mode == InteractionMode.EDIT:
            param_name = Prompt.ask("\nParameter to edit (or 'done' to finish)").lower().strip()
            
            if param_name == "done":
                self.interaction_mode = InteractionMode.NAVIGATE
                break
            elif param_name in self.edit_controls:
                try:
                    self.edit_controls[param_name]()
                    self.console.print(f"[green]✓ Updated {param_name}[/]")
                except Exception as e:
                    self.console.print(f"[red]Error updating {param_name}: {str(e)}[/]")
            else:
                self.console.print(f"[red]Unknown parameter: {param_name}[/]")
                self.console.print("Use 'done' to finish editing")
    
    def _edit_query(self):
        """Edit the query parameter with enhanced interface"""
        try:
            from query_parameter_editor import QueryParameterEditor
            editor = QueryParameterEditor(self.console, self.dashboard.state)
            editor.edit_parameter()
        except ImportError as e:
            self.console.print(f"[red]Enhanced query editor not available: {e}[/red]")
            # Fallback to simple editor
            current = self.dashboard.state.parameters["query"].value
            new_value = Prompt.ask("Enter query text", default=current)
            self.dashboard.update_parameter("query", new_value)
    
    def _edit_domain(self):
        """Edit the domain parameter with available domain reference"""
        current = self.dashboard.state.parameters["domain"].value
        
        # Display available domains as reference
        self.console.print("\n[bold cyan]Available Domain Options:[/bold cyan]")
        
        # Load and display default domains from domain_manager
        try:
            from domain_manager import create_default_domains
            default_domains = create_default_domains()
            
            # Show domains in a clean table format
            from rich.table import Table
            domain_table = Table(show_header=True, header_style="bold blue", show_lines=True)
            domain_table.add_column("Name", style="cyan", min_width=20)
            domain_table.add_column("Description", style="white", max_width=60)
            domain_table.add_column("Keywords", style="dim", max_width=40)
            
            for domain in default_domains:
                # Truncate description and keywords for display
                desc = domain.description[:55] + "..." if len(domain.description) > 55 else domain.description
                keywords = ", ".join(domain.keywords[:3])
                if len(domain.keywords) > 3:
                    keywords += "..."
                
                domain_table.add_row(domain.name, desc, keywords)
            
            self.console.print(domain_table)
            
        except Exception as e:
            # Fallback to simple list if domain_manager fails
            fallback_domains = [
                "Urban Planning", "Education", "Healthcare", "Sustainability", "Technology Innovation"
            ]
            self.console.print("\n[bold cyan]Example Domains:[/bold cyan]")
            for i, domain in enumerate(fallback_domains, 1):
                self.console.print(f"  {i}. [cyan]{domain}[/cyan]")
        
        # Show additional domain files if they exist
        self.console.print("\n[bold green]Additional Domain Collections:[/bold green]")
        domain_files = [
            ("tech_writing_domains.json", "Technical Writing"),
            ("learning_design_domains.json", "Learning Design")
        ]
        
        for filename, description in domain_files:
            try:
                import os
                if os.path.exists(filename):
                    self.console.print(f"  • [green]{description}[/green] domains available in {filename}")
            except:
                pass
        
        self.console.print("\n[dim]💡 Tips:[/dim]")
        self.console.print("  [dim]• You can enter any domain name - not limited to the list above[/dim]")
        self.console.print("  [dim]• Use descriptive domain names for better query contextualization[/dim]")
        self.console.print("  [dim]• Type 'done' to exit without changing[/dim]")
        
        while True:
            new_value = Prompt.ask(f"\nEnter domain", default=current)
            if new_value.lower().strip() == "done":
                return  # Exit without updating
            self.dashboard.update_parameter("domain", new_value)
            break
    
    def _edit_models(self):
        """Edit the models parameter with available model options reference"""
        current = self.dashboard.state.parameters["models"].value
        
        # Display comprehensive model selection options
        self.console.print("\n[bold cyan]Available Model Selection Options:[/bold cyan]")
        
        # 1. OpenRouter Model Collections (Primary Recommendation)
        self.console.print("\n[bold green]🏆 OpenRouter Model Collections (Recommended):[/bold green]")
        try:
            from openrouter_model_collections import create_default_model_collections
            collections_manager = create_default_model_collections()
            collections = collections_manager.get_all_collections()
            
            # Display collections in a clean table
            from rich.table import Table
            collections_table = Table(show_header=True, header_style="bold green", show_lines=True)
            collections_table.add_column("Collection", style="cyan", min_width=18)
            collections_table.add_column("Description", style="white", max_width=45)
            collections_table.add_column("Cost Profile", style="yellow", min_width=12)
            collections_table.add_column("Models", style="dim", min_width=8)
            
            for collection in collections:
                cost_color = {"budget": "green", "balanced": "yellow", "premium": "red"}.get(collection.cost_profile, "white")
                collections_table.add_row(
                    f"{collection.icon} {collection.name}",
                    collection.description[:42] + ("..." if len(collection.description) > 42 else ""),
                    f"[{cost_color}]{collection.cost_profile}[/{cost_color}]",
                    str(collection.expected_model_count)
                )
            
            self.console.print(collections_table)
            self.console.print("  [dim]💡 OpenRouter provides access to 300+ models from 50+ providers[/dim]")
            
        except Exception as e:
            self.console.print("  [red]⚠️ OpenRouter collections unavailable[/red]")
        
        # 2. Traditional/Legacy Models
        self.console.print("\n[bold blue]🔧 Traditional Model Options:[/bold blue]")
        try:
            import json
            with open("unified_config.json", "r") as f:
                config = json.load(f)
                api_models = config.get("models", {}).get("api_models", [])
            
            traditional_table = Table(show_header=True, header_style="bold blue")
            traditional_table.add_column("Model", style="cyan", min_width=20)
            traditional_table.add_column("Provider", style="green", min_width=12)
            traditional_table.add_column("API Key Required", style="yellow", min_width=18)
            
            for model in api_models[:6]:  # Show first 6 traditional models
                traditional_table.add_row(
                    model.get("name", "Unknown"),
                    model.get("provider", "Unknown").upper(),
                    model.get("requires", "Unknown")
                )
            
            self.console.print(traditional_table)
            if len(api_models) > 6:
                self.console.print(f"  [dim]... and {len(api_models) - 6} more traditional models available[/dim]")
                
        except Exception as e:
            self.console.print("  [red]⚠️ Traditional model config unavailable[/red]")
        
        # 3. Ollama Local Models
        self.console.print("\n[bold magenta]🖥️ Local Ollama Models:[/bold magenta]")
        try:
            import json
            with open("ollama_config.json", "r") as f:
                ollama_config = json.load(f)
                ollama_models = ollama_config.get("models", {}).get("api_models", [])
            
            if ollama_models:
                self.console.print(f"  • {len(ollama_models)} local Ollama models available")
                for model in ollama_models[:3]:  # Show first 3 Ollama models
                    self.console.print(f"    - [magenta]{model.get('name', 'Unknown')}[/magenta]")
                if len(ollama_models) > 3:
                    self.console.print(f"    ... and {len(ollama_models) - 3} more")
            else:
                self.console.print("  [dim]No Ollama models configured[/dim]")
                
        except Exception:
            self.console.print("  [dim]Ollama configuration not available[/dim]")
        
        # 4. Model Count Selection Tips
        self.console.print("\n[bold white]📊 Model Count Selection Guide:[/bold white]")
        count_guide = [
            "• [green]1-2 models[/green]: Quick, focused analysis",
            "• [yellow]3-5 models[/yellow]: Balanced cognitive diversity (recommended)",
            "• [red]6+ models[/red]: Maximum diversity but higher cost"
        ]
        for tip in count_guide:
            self.console.print(f"  {tip}")
        
        self.console.print("\n[dim]💡 Tips:[/dim]")
        self.console.print("  [dim]• Model count determines cognitive diversity vs cost[/dim]")
        self.console.print("  [dim]• OpenRouter collections provide optimized model selection[/dim]")
        self.console.print("  [dim]• Use balanced_models parameter for maximum provider diversity[/dim]")
        self.console.print("  [dim]• Type 'select' to choose specific OpenRouter models by number[/dim]")
        self.console.print("  [dim]• Type 'done' to exit without changing[/dim]")
        
        while True:
            try:
                user_input = Prompt.ask(f"\nEnter number of models (or 'select' for specific OpenRouter models)", default=str(current))
                if user_input.lower().strip() == "done":
                    return  # Exit without updating
                elif user_input.lower().strip() == "select":
                    # Enter specific OpenRouter model selection mode
                    if self._select_specific_openrouter_models():
                        return  # Successfully selected specific models
                    else:
                        continue  # Return to model count selection
                
                new_value = int(user_input)
                
                # Check resource limits with enhanced feedback
                if new_value > 10:
                    self.console.print(f"[yellow]⚠️ Warning: {new_value} models will significantly increase cost and execution time[/]")
                    if not Confirm.ask(f"[yellow]Continue with {new_value} models?[/]"):
                        continue  # Ask again
                elif new_value > 5:
                    self.console.print(f"[yellow]💰 Note: {new_value} models provides high diversity but may be expensive[/]")
                
                self.dashboard.update_parameter("models", new_value)
                break
                
            except ValueError:
                self.console.print("[red]Please enter a valid integer number or 'select'[/]")
    
    def _select_specific_openrouter_models(self) -> bool:
        """Allow user to select specific OpenRouter models by number."""
        
        self.console.print("\n[bold cyan]🏆 Top 20 OpenRouter Models - Individual Selection[/bold cyan]")
        
        # Get Top 20 models from OpenRouter collections
        try:
            from openrouter_model_collections import create_default_model_collections
            collections_manager = create_default_model_collections()
            top_performers = collections_manager.get_collection("top_performers")
            
            specific_models = []
            for spec in top_performers.model_specs:
                if "specific_models" in spec:
                    specific_models = spec["specific_models"]
                    break
            
            if not specific_models:
                self.console.print("[red]❌ No specific models found in Top Performers collection[/]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]❌ Error loading OpenRouter models: {e}[/]")
            return False
        
        # Process model information
        model_info = []
        for model_id in specific_models:
            provider = model_id.split('/')[0] if '/' in model_id else "unknown"
            model_name = model_id.split('/')[-1] if '/' in model_id else model_id
            cost_estimate = self._estimate_model_cost(model_id)
            quality_score = self._estimate_model_quality(model_id)
            
            model_info.append({
                "id": model_id,
                "name": model_name,
                "provider": provider.title(),
                "cost": cost_estimate,
                "quality": quality_score
            })
        
        # Display models in Rich table
        from rich.table import Table
        models_table = Table(title="🌟 Top 20 OpenRouter Models", show_header=True, header_style="bold blue")
        models_table.add_column("Select", style="green", width=6)
        models_table.add_column("#", style="cyan", width=3)
        models_table.add_column("Model", style="bold white", min_width=25)
        models_table.add_column("Provider", style="yellow", width=12)
        models_table.add_column("Cost/1M", style="blue", width=10)
        models_table.add_column("Quality", style="magenta", width=8)
        
        for i, model in enumerate(model_info, 1):
            models_table.add_row("☐", str(i), model["name"], model["provider"], 
                                model["cost"], f"{model['quality']}/10")
        
        self.console.print(models_table)
        
        # Show selection syntax
        self.console.print("\n[bold white]Selection Syntax:[/bold white]")
        syntax_examples = [
            "• [cyan]1,3,5[/cyan] - Select specific models by number",
            "• [cyan]1-5[/cyan] - Select range of models (1 through 5)",
            "• [cyan]1,3,7-10[/cyan] - Combine specific numbers and ranges",
            "• [cyan]all[/cyan] - Select all 20 models",
            "• [cyan][Enter][/cyan] - Default: top 3 models (1,2,3)"
        ]
        for example in syntax_examples:
            self.console.print(f"  {example}")
        
        # Get user selection
        while True:
            user_selection = Prompt.ask("\nSelect models (or 'back' to return)", default="1,2,3")
            
            if user_selection.lower() == "back":
                return False
            
            # Parse selection using adapted command wizard logic
            selected_indices = self._parse_model_selection(user_selection, len(model_info))
            
            if not selected_indices:
                self.console.print("[red]No valid models selected. Please try again.[/]")
                continue
            
            # Get selected models
            selected_models = [model_info[i-1] for i in selected_indices if 1 <= i <= len(model_info)]
            
            # Display selection confirmation
            self.console.print(f"\n[bold green]✓ Selected {len(selected_models)} Models:[/bold green]")
            
            selection_table = Table(show_header=True, header_style="bold green")
            selection_table.add_column("#", style="cyan", width=3)
            selection_table.add_column("Model", style="white", min_width=25)
            selection_table.add_column("Provider", style="yellow", width=12)
            selection_table.add_column("Cost/1M", style="blue", width=10)
            
            total_cost_estimate = 0
            for model in selected_models:
                selection_table.add_row(
                    str(model_info.index(model) + 1),
                    model["name"], 
                    model["provider"], 
                    model["cost"]
                )
                # Simple cost estimation for confirmation
                if model["cost"] != "Free" and "$" in model["cost"]:
                    try:
                        cost_val = float(model["cost"].replace("$", ""))
                        total_cost_estimate += cost_val
                    except:
                        pass
            
            self.console.print(selection_table)
            
            if total_cost_estimate > 0:
                self.console.print(f"\n[yellow]💰 Estimated total cost: ~${total_cost_estimate:.2f} per 1M tokens[/]")
            
            # Confirm selection
            if Confirm.ask(f"\n[bold]Apply selection of {len(selected_models)} specific OpenRouter models?[/]"):
                # Update dashboard parameters
                self.dashboard.update_parameter("models", len(selected_models))
                
                # Set OpenRouter filters for specific model selection
                openrouter_filters = f"specific_models:{','.join([model['id'] for model in selected_models])}"
                if hasattr(self.dashboard.state.parameters, "openrouter_filters"):
                    self.dashboard.update_parameter("openrouter_filters", openrouter_filters)
                
                # Ensure config file is set to OpenRouter
                if hasattr(self.dashboard.state.parameters, "config_file"):
                    self.dashboard.update_parameter("config_file", "openrouter_config.json")
                
                # Enable balanced models for diversity
                if hasattr(self.dashboard.state.parameters, "balanced_models"):
                    self.dashboard.update_parameter("balanced_models", True)
                
                self.console.print(f"[green]✅ Applied selection: {len(selected_models)} specific OpenRouter models[/]")
                return True
            else:
                continue  # Allow user to re-select
    
    def _parse_model_selection(self, selection_input: str, max_models: int) -> List[int]:
        """Parse user input for model selection (adapted from command wizard)."""
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
    
    def _estimate_model_cost(self, model_id: str) -> str:
        """Estimate cost per 1M tokens for a model (adapted from command wizard)."""
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
        """Estimate quality score for a model (adapted from command wizard)."""
        # Simplified quality mapping based on OpenRouter rankings
        quality_map = {
            "openai/gpt-4o-mini": 8.5,
            "google/gemini-2.0-flash": 9.0,
            "anthropic/claude-3.7-sonnet": 9.5,
            "google/gemini-2.5-pro-preview": 9.2,
            "anthropic/claude-sonnet-4": 9.7,
            "deepseek/deepseek-v3-0324-free": 8.0,
            "google/gemini-2.5-flash-preview-04-17": 9.0,
            "deepseek/deepseek-v3-0324": 8.5,
            "google/gemini-2.5-flash-preview-05-20": 9.1,
            "openai/gpt-4.1": 9.3,
            "deepseek/r1-free": 7.5,
            "meta-llama/llama-3.3-70b-instruct": 8.2,
            "mistralai/mistral-nemo": 7.8,
            "google/gemini-2.0-flash-lite": 8.5,
            "google/gemini-1.5-flash-8b": 8.0,
            "openai/gpt-4.1-mini": 8.7,
            "google/gemini-2.5-flash-preview-05-20-thinking": 9.2,
            "anthropic/claude-3.5-sonnet": 9.4,
            "google/gemini-1.5-flash": 8.8,
            "anthropic/claude-3.7-sonnet-thinking": 9.6
        }
        return quality_map.get(model_id, 7.0)
    
    def _edit_instructions(self):
        """Edit instruction templates with advanced selection support"""
        current = self.dashboard.state.parameters["instructions"].value
        
        # Load template library
        try:
            from instruction_templates import create_default_library
            template_library = create_default_library()
            templates = template_library.list_templates()
        except Exception as e:
            self.console.print(f"[red]Error loading templates: {e}[/red]")
            return
        
        # Display available instruction templates
        self.console.print("\n[bold cyan]Available Instruction Templates (Cognitive Frameworks):[/bold cyan]")
        
        # Show templates in a clean table format
        from rich.table import Table
        template_table = Table(show_header=True, header_style="bold blue", show_lines=True)
        template_table.add_column("#", style="green", width=3)
        template_table.add_column("Framework", style="cyan", min_width=20)
        template_table.add_column("Cognitive Style", style="yellow", min_width=15)
        template_table.add_column("Strength", style="white", max_width=25)
        
        for i, template in enumerate(templates, 1):
            cognitive_style = template.metadata.get("cognitive_style", "Unknown")
            strength = template.metadata.get("strength", "General reasoning")
            
            template_table.add_row(
                str(i),
                template.name,
                cognitive_style.title(),
                strength.title()
            )
        
        self.console.print(template_table)
        
        # Show current selection
        current_selection = self.dashboard.state.parameters.get("instruction_templates")
        if current_selection and current_selection.value:
            current_template_ids = current_selection.value.split(",")
            self.console.print(f"\n[bold green]Current Selection:[/bold green] {len(current_template_ids)} specific templates")
            for template_id in current_template_ids:
                template = next((t for t in templates if t.id == template_id), None)
                if template:
                    self.console.print(f"  ✓ [green]{template.name}[/green]")
        else:
            self.console.print(f"\n[bold green]Current Selection:[/bold green] Using [yellow]{current}[/yellow] instruction templates (first {current} from list)")
        
        # Selection options
        self.console.print("\n[bold yellow]Selection Options:[/bold yellow]")
        self.console.print("• [cyan]Number[/cyan] (e.g., '5') - Use first N templates")
        self.console.print("• [cyan]Specific[/cyan] (e.g., '1,3,5' or '2-4') - Select specific templates")
        self.console.print("• [cyan]Special commands:[/cyan] 'preview <number>', 'compare <num1> <num2>', 'help', 'done'")
        
        selected_templates = []
        
        while True:
            user_input = Prompt.ask("Template selection", default=str(current)).strip()
            
            if user_input.lower() == "done":
                return  # Exit without updating
            
            # Handle special commands
            if user_input.lower().startswith("preview "):
                self._handle_template_preview(user_input, templates)
                continue
            elif user_input.lower().startswith("compare "):
                self._handle_template_compare(user_input, templates)
                continue
            elif user_input.lower() == "help":
                self._show_template_help()
                continue
            
            # Try to parse as simple number first
            try:
                simple_count = int(user_input)
                if simple_count < 1:
                    self.console.print("[red]Please enter a number greater than 0[/red]")
                    continue
                elif simple_count > len(templates):
                    self.console.print(f"[red]Maximum {len(templates)} templates available[/red]")
                    continue
                
                # Clear any specific template selection and use count-based
                if "instruction_templates" in self.dashboard.state.parameters:
                    self.dashboard.update_parameter("instruction_templates", "")
                self.dashboard.update_parameter("instructions", simple_count)
                self.console.print(f"[green]✓ Set to use first {simple_count} templates[/green]")
                break
                
            except ValueError:
                # Try to parse as advanced selection
                try:
                    selected_numbers = self._parse_number_selection(user_input, len(templates))
                    if selected_numbers:
                        # Convert numbers to template IDs
                        selected_template_ids = [templates[num - 1].id for num in selected_numbers]
                        
                        # Update parameters
                        self.dashboard.update_parameter("instruction_templates", ",".join(selected_template_ids))
                        self.dashboard.update_parameter("instructions", len(selected_template_ids))
                        
                        # Show confirmation
                        self.console.print(f"\n[green]✓ Selected {len(selected_template_ids)} specific templates:[/green]")
                        for template_id in selected_template_ids:
                            template = next(t for t in templates if t.id == template_id)
                            self.console.print(f"  • [cyan]{template.name}[/cyan]")
                        break
                        
                except ValueError as e:
                    self.console.print(f"[red]{e}[/red]")
                    self.console.print("[dim]Examples: '5' (first 5), '1,3,5' (specific), '2-4' (range)[/dim]")
    
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
    
    def _handle_template_preview(self, user_input: str, templates: List):
        """Handle template preview command"""
        try:
            parts = user_input.split()
            if len(parts) >= 2:
                num = int(parts[1])
                if 1 <= num <= len(templates):
                    template = templates[num - 1]
                    
                    # Display template details
                    from rich.panel import Panel
                    content = [
                        f"[bold cyan]{template.name}[/bold cyan]",
                        "",
                        f"[yellow]Cognitive Style:[/yellow] {template.metadata.get('cognitive_style', 'Unknown').title()}",
                        f"[yellow]Strength:[/yellow] {template.metadata.get('strength', 'General reasoning').title()}",
                        "",
                        "[yellow]Template Description:[/yellow]",
                        template.template.replace("{domain}", "[domain]")[:200] + "..."
                    ]
                    
                    preview_panel = Panel(
                        "\n".join(content),
                        title=f"Template #{num} Preview",
                        border_style="cyan"
                    )
                    self.console.print(preview_panel)
                else:
                    self.console.print(f"[red]Invalid number. Use 1-{len(templates)}[/red]")
            else:
                self.console.print("[red]Usage: preview <number>[/red]")
        except (ValueError, IndexError):
            self.console.print("[red]Invalid command format. Use 'preview <number>'[/red]")
    
    def _handle_template_compare(self, user_input: str, templates: List):
        """Handle template comparison command"""
        try:
            parts = user_input.split()
            if len(parts) >= 3:
                num1, num2 = int(parts[1]), int(parts[2])
                if 1 <= num1 <= len(templates) and 1 <= num2 <= len(templates):
                    template1 = templates[num1 - 1]
                    template2 = templates[num2 - 1]
                    
                    # Create comparison table
                    from rich.table import Table
                    compare_table = Table(show_header=True, header_style="bold yellow")
                    compare_table.add_column("Aspect", style="cyan", min_width=15)
                    compare_table.add_column(f"#{num1} {template1.name}", style="green", max_width=35)
                    compare_table.add_column(f"#{num2} {template2.name}", style="blue", max_width=35)
                    
                    compare_table.add_row(
                        "Cognitive Style",
                        template1.metadata.get('cognitive_style', 'Unknown').title(),
                        template2.metadata.get('cognitive_style', 'Unknown').title()
                    )
                    compare_table.add_row(
                        "Strength",
                        template1.metadata.get('strength', 'General reasoning').title(),
                        template2.metadata.get('strength', 'General reasoning').title()
                    )
                    
                    self.console.print(f"\n[bold yellow]Template Comparison:[/bold yellow]")
                    self.console.print(compare_table)
                else:
                    self.console.print(f"[red]Invalid numbers. Use 1-{len(templates)}[/red]")
            else:
                self.console.print("[red]Usage: compare <num1> <num2>[/red]")
        except (ValueError, IndexError):
            self.console.print("[red]Invalid command format. Use 'compare <num1> <num2>'[/red]")
    
    def _show_template_help(self):
        """Show template selection help"""
        self.console.print("\n[bold cyan]Template Selection Help:[/bold cyan]")
        self.console.print("• [green]Number only[/green]: '5' - Use first 5 templates from the list")
        self.console.print("• [green]Specific selection[/green]: '1,3,5' - Use templates #1, #3, and #5")
        self.console.print("• [green]Range selection[/green]: '2-4' - Use templates #2, #3, and #4")
        self.console.print("• [green]Mixed selection[/green]: '1,3-5,8' - Use templates #1, #3-5, and #8")
        self.console.print("")
        self.console.print("[bold yellow]Special Commands:[/bold yellow]")
        self.console.print("• [cyan]preview <number>[/cyan] - See detailed information about a template")
        self.console.print("• [cyan]compare <num1> <num2>[/cyan] - Compare two templates side by side")
        self.console.print("• [cyan]help[/cyan] - Show this help message")
        self.console.print("• [cyan]done[/cyan] - Exit without making changes")
        self.console.print("")
    
    def _edit_variations(self):
        """Edit the variations parameter with enhanced interface"""
        try:
            from variations_parameter_editor import VariationsParameterEditor
            editor = VariationsParameterEditor(self.console, self.dashboard.state)
            editor.edit_parameter()
        except ImportError as e:
            self.console.print(f"[red]Enhanced variations editor not available: {e}[/red]")
            # Fallback to simple editor
            current = self.dashboard.state.parameters["variations"].value
            while True:
                try:
                    user_input = Prompt.ask("Number of query variations", default=str(current))
                    if user_input.lower().strip() == "done":
                        return  # Exit without updating
                    
                    new_value = int(user_input)
                    self.dashboard.update_parameter("variations", new_value)
                    break
                    
                except ValueError:
                    self.console.print("[red]Please enter a valid integer number[/]")
    
    def _edit_max_combinations(self):
        """Edit the max_combinations parameter"""
        current = self.dashboard.state.parameters["max_combinations"].value
        while True:
            try:
                user_input = Prompt.ask("Maximum combinations", default=str(current))
                if user_input.lower().strip() == "done":
                    return  # Exit without updating
                
                new_value = int(user_input)
                
                # Check resource limits
                if new_value > 50:
                    if not Confirm.ask(f"[yellow]Warning: {new_value} combinations may be expensive. Continue?[/]"):
                        continue  # Ask again
                
                self.dashboard.update_parameter("max_combinations", new_value)
                break
                
            except ValueError:
                self.console.print("[red]Please enter a valid integer number[/]")
    
    def _edit_sampling_method(self):
        """Edit the sampling_method parameter"""
        methods = ["random", "stratified", "systematic"]
        current = self.dashboard.state.parameters["sampling_method"].value
        
        self.console.print("Available sampling methods:")
        for i, method in enumerate(methods, 1):
            marker = "→" if method == current else " "
            self.console.print(f"{marker} {i}. {method}")
        
        choice = IntPrompt.ask("Select method (1-3)", default=methods.index(current) + 1)
        if 1 <= choice <= len(methods):
            self.dashboard.update_parameter("sampling_method", methods[choice - 1])
    
    def _toggle_balanced_models(self):
        """Toggle the balanced_models parameter"""
        current = self.dashboard.state.parameters["balanced_models"].value
        new_value = not current
        self.dashboard.update_parameter("balanced_models", new_value)
        self.console.print(f"Balanced models: {'enabled' if new_value else 'disabled'}")
    
    def _toggle_use_ollama(self):
        """Toggle the use_ollama parameter"""
        current = self.dashboard.state.parameters["use_ollama"].value
        new_value = not current
        self.dashboard.update_parameter("use_ollama", new_value)
        self.console.print(f"Use Ollama: {'enabled' if new_value else 'disabled'}")
    
    def _toggle_simulate(self):
        """Toggle the simulate parameter"""
        current = self.dashboard.state.parameters["simulate"].value
        new_value = not current
        self.dashboard.update_parameter("simulate", new_value)
        self.console.print(f"Simulation mode: {'enabled' if new_value else 'disabled'}")
    
    def _toggle_dry_run(self):
        """Toggle the dry_run parameter"""
        current = self.dashboard.state.parameters["dry_run"].value
        new_value = not current
        self.dashboard.update_parameter("dry_run", new_value)
        self.console.print(f"Dry run mode: {'enabled' if new_value else 'disabled'}")
    
    def _edit_openrouter_filters(self):
        """Edit the openrouter_filters parameter"""
        current = self.dashboard.state.parameters.get("openrouter_filters")
        current_value = current.value if current else ""
        
        # Display available filter options
        self.console.print("\n[bold cyan]OpenRouter Filter Options:[/bold cyan]")
        
        # Provider filters
        self.console.print("\n[bold green]Providers:[/bold green]")
        providers = [
            "anthropic", "openai", "google", "meta-llama", "mistralai", 
            "cohere", "ai21", "togetherai", "fireworks", "perplexityai"
        ]
        for i, provider in enumerate(providers, 1):
            self.console.print(f"  {i:2d}. provider:{provider}")
        
        # Capability filters  
        self.console.print("\n[bold blue]Capabilities:[/bold blue]")
        capabilities = [
            "reasoning", "creative", "coding", "analysis", "multimodal",
            "large_context", "fast", "instruction_following", "conversational"
        ]
        for i, cap in enumerate(capabilities, 1):
            self.console.print(f"  {i:2d}. capability:{cap}")
        
        # Cost tier filters
        self.console.print("\n[bold yellow]Cost Tiers:[/bold yellow]")
        cost_tiers = ["free", "budget", "standard", "premium", "premium_plus"]
        for i, tier in enumerate(cost_tiers, 1):
            self.console.print(f"  {i:2d}. cost_tier:{tier}")
        
        # Use case filters
        self.console.print("\n[bold magenta]Use Cases:[/bold magenta]")
        use_cases = [
            "content_creation", "deep_analysis", "quick_exploration",
            "problem_solving", "creative_innovation", "code_generation"
        ]
        for i, uc in enumerate(use_cases, 1):
            self.console.print(f"  {i:2d}. use_case:{uc}")
        
        # Examples
        self.console.print("\n[bold white]Example Filter Strings:[/bold white]")
        examples = [
            "provider:anthropic",
            "provider:openai,cost_tier:budget", 
            "capability:reasoning,cost_tier:premium",
            "provider:google,capability:coding,capability:fast",
            "cost_tier:budget,capability:large_context",
            "use_case:deep_analysis,provider:anthropic,cost_tier:standard"
        ]
        for i, example in enumerate(examples, 1):
            self.console.print(f"  {i}. [cyan]{example}[/cyan]")
        
        self.console.print("\n[dim]💡 Tips:[/dim]")
        self.console.print("  [dim]• Use colon (:) to separate filter type from value[/dim]")
        self.console.print("  [dim]• Use comma (,) to combine multiple filters[/dim]")  
        self.console.print("  [dim]• Type 'done' to exit without changing[/dim]")
        
        while True:
            user_input = Prompt.ask(f"\nEnter OpenRouter filters", default=current_value or "")
            if user_input.lower().strip() == "done":
                return  # Exit without updating
            
            # Basic validation
            if user_input and not self._validate_openrouter_filters(user_input):
                self.console.print("[red]Invalid filter format. Please check the examples above.[/red]")
                continue
                
            self.dashboard.update_parameter("openrouter_filters", user_input)
            break
    
    def _validate_openrouter_filters(self, filter_string: str) -> bool:
        """Validate OpenRouter filter string format"""
        if not filter_string.strip():
            return True  # Empty string is valid
        
        valid_prefixes = [
            "provider:", "capability:", "cost_tier:", "use_case:"
        ]
        
        # Split by comma and check each filter
        filters = [f.strip() for f in filter_string.split(",")]
        for filter_part in filters:
            if not any(filter_part.startswith(prefix) for prefix in valid_prefixes):
                return False
            if ":" not in filter_part:
                return False
        
        return True
    
    def _toggle_quick(self):
        """Toggle the quick parameter"""
        current = self.dashboard.state.parameters.get("quick")
        current_value = current.value if current else False
        new_value = not current_value
        self.dashboard.update_parameter("quick", new_value)
        self.console.print(f"Quick mode: {'enabled' if new_value else 'disabled'}")
    
    def _toggle_full(self):
        """Toggle the full parameter"""
        current = self.dashboard.state.parameters.get("full")
        current_value = current.value if current else False
        new_value = not current_value
        self.dashboard.update_parameter("full", new_value)
        self.console.print(f"Full mode: {'enabled' if new_value else 'disabled'}")
    
    def _edit_output_format(self):
        """Edit the output_format parameter"""
        formats = ["json", "yaml", "text", "csv"]
        current = self.dashboard.state.parameters.get("output_format")
        current_value = current.value if current else "json"
        
        self.console.print("Available output formats:")
        for i, fmt in enumerate(formats, 1):
            marker = "→" if fmt == current_value else " "
            self.console.print(f"{marker} {i}. {fmt}")
        
        while True:
            user_input = Prompt.ask("Select format (1-4)", default=str(formats.index(current_value) + 1))
            if user_input.lower().strip() == "done":
                return  # Exit without updating
            
            try:
                choice = int(user_input)
                if 1 <= choice <= len(formats):
                    self.dashboard.update_parameter("output_format", formats[choice - 1])
                    break
                else:
                    self.console.print("[red]Please enter a number between 1 and 4[/]")
            except ValueError:
                self.console.print("[red]Please enter a valid number[/]")
    
    def _toggle_generate_reports(self):
        """Toggle the generate_reports parameter"""
        current = self.dashboard.state.parameters.get("generate_reports")
        current_value = current.value if current else False
        new_value = not current_value
        self.dashboard.update_parameter("generate_reports", new_value)
        self.console.print(f"Generate reports: {'enabled' if new_value else 'disabled'}")
    
    def _toggle_analyze_results(self):
        """Toggle the analyze_results parameter"""
        current = self.dashboard.state.parameters.get("analyze_results")
        current_value = current.value if current else False
        new_value = not current_value
        self.dashboard.update_parameter("analyze_results", new_value)
        self.console.print(f"Analyze results: {'enabled' if new_value else 'disabled'}")
    
    def _reset_parameters(self):
        """Reset all parameters to defaults"""
        if Confirm.ask("[yellow]Reset all parameters to defaults?[/]"):
            for param in self.dashboard.state.parameters.values():
                param.value = param.default_value
                param.status = ParameterStatus.DEFAULT
            
            self.dashboard._update_estimates()
            self.console.print("[green]✓ All parameters reset to defaults[/]")
    
    def _preview_command(self):
        """Preview the generated command"""
        command = self.dashboard._build_command()
        
        preview_panel = Panel(
            command,
            title="Generated Command",
            border_style="magenta",
            expand=False
        )
        
        self.console.print("\n")
        self.console.print(preview_panel)
        
        # Show cost/time estimates
        cost = self.dashboard.state.total_cost
        time_min = self.dashboard.state.total_time
        combinations = self.dashboard.state.combination_count
        
        estimates_text = f"Estimated: ${cost:.2f}, {time_min:.1f} min, {combinations:,} combinations"
        self.console.print(f"\n[cyan]{estimates_text}[/]")
        
        # Show warnings if any
        if self.dashboard.state.resource_warnings:
            self.console.print("\n[yellow]⚠️ Warnings:[/]")
            for warning in self.dashboard.state.resource_warnings:
                self.console.print(f"  • {warning}")
        
        Prompt.ask("\nPress Enter to continue")
    
    def _execute_command(self) -> str:
        """Execute the generated command"""
        command = self.dashboard._build_command()
        
        # Show final confirmation
        self.console.print("\n[bold]Ready to execute:[/]")
        self.console.print(f"[cyan]{command}[/]")
        
        cost = self.dashboard.state.total_cost
        time_min = self.dashboard.state.total_time
        combinations = self.dashboard.state.combination_count
        
        self.console.print(f"\nEstimated: [yellow]${cost:.2f}[/], [yellow]{time_min:.1f} min[/], [cyan]{combinations:,} combinations[/]")
        
        # Check for warnings
        if self.dashboard.state.resource_warnings:
            self.console.print("\n[bold red]⚠️ Resource Warnings:[/]")
            for warning in self.dashboard.state.resource_warnings:
                self.console.print(f"  [red]• {warning}[/]")
            
            if not Confirm.ask("\n[yellow]Execute despite warnings?[/]"):
                return None
        
        if Confirm.ask("\n[bold green]Execute this command?[/]"):
            self.running = False
            return command
        
        return None
    
    def _show_help(self):
        """Show help information"""
        help_text = """
[bold cyan]ISEE Configuration Dashboard Help[/]

[bold]Navigation:[/]
• [cyan]1, 2, 3[/] - Switch between Overview, Detailed, and Expert modes
• [green]E[/] - Enter parameter editing mode
• [yellow]R[/] - Reset all parameters to defaults
• [magenta]P[/] - Preview generated command
• [bold green]X[/] - Execute the command
• [red]Q[/] - Quit dashboard

[bold]Parameter Categories:[/]
• [cyan]Basic[/] - Core parameters (query, domain, models, etc.)
• [green]Sampling[/] - Combination control (max_combinations, sampling_method)
• [blue]Models[/] - Model selection options (balanced_models, use_ollama)
• [magenta]Output[/] - Output format and reporting options
• [yellow]Advanced[/] - Specialized options (dry_run, state management)

[bold]Real-time Features:[/]
• Cost and time estimates update automatically
• Resource warnings appear when limits approached
• Parameter relationships shown in detailed mode
• Color coding indicates parameter status and impact

[bold]Tips:[/]
• Start with a clear query to get accurate cost estimates
• Use simulation mode for testing without API costs
• Check resource warnings before executing expensive runs
• Use balanced models for maximum cognitive diversity
        """
        
        help_panel = Panel(
            help_text,
            title="Dashboard Help",
            border_style="blue",
            expand=False
        )
        
        self.console.print(help_panel)
        Prompt.ask("\nPress Enter to continue")
    
    def _quit_dashboard(self):
        """Quit the dashboard"""
        self.running = False
        self.console.print("[yellow]Exiting dashboard...[/]")
    
    def _handle_invalid_input(self, command: str):
        """Handle invalid user input"""
        self.console.print(f"[red]Unknown command: '{command}'[/]")
        self.console.print("Press 'H' for help or 'Q' to quit")
        time.sleep(1)

def run_interactive_dashboard(console: Optional[Console] = None) -> Optional[str]:
    """Run the interactive configuration dashboard.
    
    Args:
        console: Rich console instance. If None, creates a new one.
        
    Returns:
        Generated command string if executed, None if cancelled
    """
    controller = InteractiveDashboardController(console)
    return controller.run_interactive_dashboard()

if __name__ == "__main__":
    result = run_interactive_dashboard()
    if result:
        print(f"Generated command: {result}")
    else:
        print("Dashboard cancelled")