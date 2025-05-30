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
            "variations": self._edit_variations,
            "max_combinations": self._edit_max_combinations,
            "sampling_method": self._edit_sampling_method,
            "balanced_models": self._toggle_balanced_models,
            "use_ollama": self._toggle_use_ollama,
            "simulate": self._toggle_simulate,
            "dry_run": self._toggle_dry_run
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
            # Start with overview mode
            self.dashboard.display_dashboard(DashboardMode.OVERVIEW)
            
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
        """Edit the query parameter"""
        current = self.dashboard.state.parameters["query"].value
        new_value = Prompt.ask("Enter query text", default=current)
        self.dashboard.update_parameter("query", new_value)
    
    def _edit_domain(self):
        """Edit the domain parameter"""
        current = self.dashboard.state.parameters["domain"].value
        new_value = Prompt.ask("Enter domain", default=current)
        self.dashboard.update_parameter("domain", new_value)
    
    def _edit_models(self):
        """Edit the models parameter"""
        current = self.dashboard.state.parameters["models"].value
        new_value = IntPrompt.ask("Number of models", default=current)
        
        # Check resource limits
        if new_value > 10:
            if not Confirm.ask(f"[yellow]Warning: {new_value} models may be expensive. Continue?[/]"):
                return
        
        self.dashboard.update_parameter("models", new_value)
    
    def _edit_instructions(self):
        """Edit the instructions parameter"""
        current = self.dashboard.state.parameters["instructions"].value
        new_value = IntPrompt.ask("Number of instruction templates", default=current)
        self.dashboard.update_parameter("instructions", new_value)
    
    def _edit_variations(self):
        """Edit the variations parameter"""
        current = self.dashboard.state.parameters["variations"].value
        new_value = IntPrompt.ask("Number of query variations", default=current)
        self.dashboard.update_parameter("variations", new_value)
    
    def _edit_max_combinations(self):
        """Edit the max_combinations parameter"""
        current = self.dashboard.state.parameters["max_combinations"].value
        new_value = IntPrompt.ask("Maximum combinations", default=current)
        
        # Check resource limits
        if new_value > 50:
            if not Confirm.ask(f"[yellow]Warning: {new_value} combinations may be expensive. Continue?[/]"):
                return
        
        self.dashboard.update_parameter("max_combinations", new_value)
    
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