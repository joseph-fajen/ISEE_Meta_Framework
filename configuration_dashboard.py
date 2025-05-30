"""
Configuration Dashboard for ISEE Framework

This module provides a visual, interactive dashboard for configuring ISEE parameters
with real-time updates and parameter relationship visualization.

Part of UX Enhancement Roadmap - Step 3.2: Simple Configuration Dashboard
"""

from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json

# Rich imports for UI components
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.rule import Rule
from rich.align import Align
from rich import box

# Import existing ISEE components
try:
    from parameter_context import ParameterContext, PARAMETER_CATEGORIES
    from cost_estimation import CostEstimator
    from cognitive_framework_visualizer import CognitiveFrameworkVisualizer
    from main import ISEEGuardrails
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False

class DashboardMode(Enum):
    """Dashboard display modes"""
    OVERVIEW = "overview"
    DETAILED = "detailed" 
    EXPERT = "expert"

class ParameterStatus(Enum):
    """Parameter status indicators"""
    DEFAULT = "default"
    MODIFIED = "modified"
    WARNING = "warning"
    ERROR = "error"

@dataclass
class ParameterState:
    """Represents the current state of a parameter"""
    name: str
    value: Any
    default_value: Any
    category: str
    status: ParameterStatus = ParameterStatus.DEFAULT
    dependencies: List[str] = field(default_factory=list)
    impact_score: float = 0.0
    cost_impact: float = 0.0

@dataclass 
class DashboardState:
    """Represents the complete dashboard configuration state"""
    parameters: Dict[str, ParameterState] = field(default_factory=dict)
    total_cost: float = 0.0
    total_time: float = 0.0
    combination_count: int = 0
    resource_warnings: List[str] = field(default_factory=list)
    mode: DashboardMode = DashboardMode.OVERVIEW

class ConfigurationDashboard:
    """Interactive visual dashboard for ISEE parameter configuration"""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize the configuration dashboard.
        
        Args:
            console: Rich console instance. If None, creates a new one.
        """
        self.console = console or Console()
        self.state = DashboardState()
        
        # Initialize components if available
        if COMPONENTS_AVAILABLE:
            self.parameter_context = ParameterContext()
            self.cost_estimator = CostEstimator()
            self.framework_visualizer = CognitiveFrameworkVisualizer(self.console)
            self.guardrails = ISEEGuardrails()
        else:
            self.parameter_context = None
            self.cost_estimator = None
            self.framework_visualizer = None
            self.guardrails = None
        
        # Category color mapping (from Step 1.3)
        self.category_colors = {
            "basic": "cyan",
            "sampling": "green", 
            "models": "blue",
            "output": "magenta",
            "advanced": "yellow"
        }
        
        # Initialize default parameter states
        self._initialize_parameters()
        
        # Update callbacks for real-time changes
        self.update_callbacks: List[Callable] = []
    
    def _initialize_parameters(self):
        """Initialize parameter states with defaults"""
        if not self.parameter_context:
            return
            
        for category_name, category_info in PARAMETER_CATEGORIES.items():
            for param_name in category_info["parameters"]:
                context = self.parameter_context.get_parameter_context(param_name)
                
                # Determine default value based on parameter type
                default_value = self._get_default_value(param_name, context)
                
                self.state.parameters[param_name] = ParameterState(
                    name=param_name,
                    value=default_value,
                    default_value=default_value,
                    category=category_name,
                    dependencies=context.get("relationships", {}).get("affects", [])
                )
    
    def _get_default_value(self, param_name: str, context: Dict) -> Any:
        """Get sensible default value for a parameter"""
        defaults = {
            "query": "",
            "domain": "Technology Innovation",
            "models": 3,
            "instructions": 3,
            "variations": 2,
            "sampling_method": "stratified",
            "max_combinations": 12,
            "balanced_models": False,
            "use_ollama": False,
            "simulate": False,
            "output_format": "json",
            "dry_run": False
        }
        return defaults.get(param_name, "")
    
    def display_dashboard(self, mode: DashboardMode = DashboardMode.OVERVIEW):
        """Display the main dashboard interface"""
        self.state.mode = mode
        
        # Create main layout
        layout = Layout()
        
        # Configure layout structure based on mode
        if mode == DashboardMode.OVERVIEW:
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="main", ratio=1),
                Layout(name="footer", size=5)
            )
            layout["main"].split_row(
                Layout(name="parameters", ratio=2),
                Layout(name="status", ratio=1)
            )
        else:
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="main", ratio=1),
                Layout(name="footer", size=5)
            )
            layout["main"].split_row(
                Layout(name="left", ratio=1),
                Layout(name="right", ratio=1)
            )
            layout["left"].split_column(
                Layout(name="parameters"),
                Layout(name="relationships")
            )
            layout["right"].split_column(
                Layout(name="status"),
                Layout(name="preview")
            )
        
        # Populate layout sections
        layout["header"].update(self._create_header())
        
        if mode == DashboardMode.OVERVIEW:
            layout["parameters"].update(self._create_parameter_overview())
            layout["status"].update(self._create_status_panel())
        else:
            layout["parameters"].update(self._create_detailed_parameters())
            layout["relationships"].update(self._create_relationships_panel())
            layout["status"].update(self._create_status_panel())
            layout["preview"].update(self._create_command_preview())
        
        layout["footer"].update(self._create_footer())
        
        # Display the complete dashboard
        self.console.clear()
        self.console.print(layout)
    
    def _create_header(self) -> Panel:
        """Create dashboard header with title and mode indicator"""
        mode_text = {
            DashboardMode.OVERVIEW: "Overview",
            DashboardMode.DETAILED: "Detailed",
            DashboardMode.EXPERT: "Expert"
        }
        
        title = Text("ISEE Configuration Dashboard", style="bold white")
        mode = Text(f"Mode: {mode_text[self.state.mode]}", style="dim")
        
        header_content = Columns([title, mode], align="center")
        
        return Panel(
            header_content,
            style="bold blue",
            box=box.DOUBLE
        )
    
    def _create_parameter_overview(self) -> Panel:
        """Create overview of all parameter categories"""
        table = Table(show_header=True, header_style="bold white", box=box.ROUNDED)
        table.add_column("Category", style="bold", width=15)
        table.add_column("Parameters", width=40)
        table.add_column("Status", width=10)
        table.add_column("Impact", width=10)
        
        for category_name, category_info in PARAMETER_CATEGORIES.items():
            color = self.category_colors.get(category_name, "white")
            
            # Get parameters in this category
            params_in_category = [p for p in self.state.parameters.values() 
                                if p.category == category_name]
            
            # Calculate status summary
            modified_count = sum(1 for p in params_in_category 
                               if p.status == ParameterStatus.MODIFIED)
            warning_count = sum(1 for p in params_in_category 
                              if p.status == ParameterStatus.WARNING)
            
            # Create parameter summary
            param_summary = f"{len(params_in_category)} parameters"
            if modified_count > 0:
                param_summary += f" ({modified_count} modified)"
            
            # Status indicator
            if warning_count > 0:
                status = "[yellow]⚠️ Warning[/]"
            elif modified_count > 0:
                status = "[green]✓ Modified[/]"
            else:
                status = "[dim]Default[/]"
            
            # Impact score (simplified)
            total_impact = sum(p.impact_score for p in params_in_category)
            impact_text = self._format_impact_score(total_impact)
            
            table.add_row(
                f"[{color}]{category_info['name']}[/]",
                param_summary,
                status,
                impact_text
            )
        
        return Panel(
            table,
            title="Parameter Categories",
            border_style="cyan"
        )
    
    def _create_detailed_parameters(self) -> Panel:
        """Create detailed parameter listing"""
        table = Table(show_header=True, header_style="bold white", box=box.ROUNDED)
        table.add_column("Parameter", width=20)
        table.add_column("Value", width=15)
        table.add_column("Status", width=10)
        
        # Group by category
        for category_name, category_info in PARAMETER_CATEGORIES.items():
            color = self.category_colors.get(category_name, "white")
            
            # Add category header
            table.add_row(
                f"[bold {color}]{category_info['name']}[/]",
                "",
                "",
                style="dim"
            )
            
            # Add parameters in category
            params_in_category = [p for p in self.state.parameters.values() 
                                if p.category == category_name]
            
            for param in sorted(params_in_category, key=lambda p: p.name):
                status_text = self._get_status_text(param.status)
                value_text = self._format_parameter_value(param.value)
                
                table.add_row(
                    f"  {param.name}",
                    value_text,
                    status_text
                )
        
        return Panel(
            table,
            title="Parameter Details",
            border_style="cyan"
        )
    
    def _create_status_panel(self) -> Panel:
        """Create status panel with cost, time, and warnings"""
        # Update current estimates
        self._update_estimates()
        
        # Cost and time display
        cost_text = Text()
        cost_text.append("Estimated Cost: ", style="bold")
        cost_text.append(f"${self.state.total_cost:.2f}", 
                        style="green" if self.state.total_cost < 5.0 else "yellow" if self.state.total_cost < 15.0 else "red")
        
        time_text = Text()
        time_text.append("Estimated Time: ", style="bold")
        time_text.append(f"{self.state.total_time:.1f} min", 
                        style="green" if self.state.total_time < 10 else "yellow" if self.state.total_time < 30 else "red")
        
        combo_text = Text()
        combo_text.append("Combinations: ", style="bold")
        combo_text.append(f"{self.state.combination_count:,}", style="cyan")
        
        # Resource warnings
        warnings_content = []
        if self.state.resource_warnings:
            warnings_content.append(Text("⚠️ Warnings:", style="bold yellow"))
            for warning in self.state.resource_warnings:
                warnings_content.append(Text(f"• {warning}", style="yellow"))
        else:
            warnings_content.append(Text("✓ No warnings", style="green"))
        
        # Combine all content
        status_content = [cost_text, time_text, combo_text, Text("")]
        status_content.extend(warnings_content)
        
        return Panel(
            Align.left("\n".join(str(content) for content in status_content)),
            title="Resource Status",
            border_style="green" if not self.state.resource_warnings else "yellow"
        )
    
    def _create_relationships_panel(self) -> Panel:
        """Create parameter relationships visualization"""
        # Simple relationship display for now
        table = Table(show_header=True, header_style="bold white", box=box.SIMPLE)
        table.add_column("Parameter", width=15)
        table.add_column("Affects", width=25)
        
        for param in self.state.parameters.values():
            if param.dependencies:
                table.add_row(
                    param.name,
                    ", ".join(param.dependencies)
                )
        
        return Panel(
            table,
            title="Parameter Relationships",
            border_style="blue"
        )
    
    def _create_command_preview(self) -> Panel:
        """Create command preview panel"""
        command = self._build_command()
        
        preview_text = Text()
        preview_text.append("Generated Command:\n\n", style="bold")
        preview_text.append(command, style="cyan")
        
        return Panel(
            preview_text,
            title="Command Preview",
            border_style="magenta"
        )
    
    def _create_footer(self) -> Panel:
        """Create footer with navigation options"""
        footer_text = Text()
        footer_text.append("Navigation: ", style="bold")
        footer_text.append("[1] Overview  ", style="cyan")
        footer_text.append("[2] Detailed  ", style="cyan") 
        footer_text.append("[3] Expert  ", style="cyan")
        footer_text.append("[E] Execute  ", style="green")
        footer_text.append("[Q] Quit", style="red")
        
        return Panel(
            Align.center(footer_text),
            style="dim"
        )
    
    def _update_estimates(self):
        """Update cost and time estimates based on current parameters"""
        if not self.cost_estimator:
            self.state.total_cost = 0.0
            self.state.total_time = 0.0
            self.state.combination_count = 0
            return
        
        # Build parameter dict for estimation
        params = {name: param.value for name, param in self.state.parameters.items()}
        
        # Calculate combination count
        models = params.get("models", 3)
        instructions = params.get("instructions", 3) 
        variations = params.get("variations", 2)
        max_combinations = params.get("max_combinations", 12)
        
        total_combinations = models * instructions * variations
        self.state.combination_count = min(total_combinations, max_combinations)
        
        # Estimate costs
        try:
            cost_breakdown = self.cost_estimator.estimate_total_cost(
                models=models,
                instructions=instructions,
                variations=variations,
                max_combinations=max_combinations,
                query_text=params.get("query", "test query"),
                use_ollama=params.get("use_ollama", False)
            )
            self.state.total_cost = cost_breakdown["total_cost"]
            self.state.total_time = cost_breakdown.get("estimated_time_minutes", 0)
        except Exception:
            self.state.total_cost = self.state.combination_count * 0.08
            self.state.total_time = self.state.combination_count * 0.5
        
        # Check for resource warnings
        self._update_resource_warnings()
    
    def _update_resource_warnings(self):
        """Update resource protection warnings"""
        self.state.resource_warnings = []
        
        if not self.guardrails:
            return
        
        # Check guardrails
        try:
            params = {name: param.value for name, param in self.state.parameters.items()}
            warning_info = self.guardrails.validate_resource_limits(
                combination_count=self.state.combination_count,
                estimated_cost=self.state.total_cost,
                estimated_time_minutes=self.state.total_time,
                **params
            )
            
            if not warning_info["allowed"]:
                self.state.resource_warnings.append(warning_info["message"])
            
            for warning in warning_info.get("warnings", []):
                self.state.resource_warnings.append(warning)
                
        except Exception:
            pass
    
    def _get_status_text(self, status: ParameterStatus) -> str:
        """Get colored status text"""
        status_map = {
            ParameterStatus.DEFAULT: "[dim]Default[/]",
            ParameterStatus.MODIFIED: "[green]Modified[/]",
            ParameterStatus.WARNING: "[yellow]Warning[/]",
            ParameterStatus.ERROR: "[red]Error[/]"
        }
        return status_map.get(status, "[dim]Unknown[/]")
    
    def _format_parameter_value(self, value: Any) -> str:
        """Format parameter value for display"""
        if isinstance(value, bool):
            return "✓" if value else "✗"
        elif isinstance(value, str) and len(value) > 20:
            return f"{value[:17]}..."
        else:
            return str(value)
    
    def _format_impact_score(self, score: float) -> str:
        """Format impact score for display"""
        if score < 1.0:
            return "[green]Low[/]"
        elif score < 3.0:
            return "[yellow]Medium[/]"
        else:
            return "[red]High[/]"
    
    def _build_command(self) -> str:
        """Build ISEE command from current parameters"""
        params = self.state.parameters
        
        cmd_parts = ["python main.py"]
        
        # Add basic parameters
        if "query" in params and params["query"].value:
            cmd_parts.append(f'--query "{params["query"].value}"')
        if "domain" in params and params["domain"].value != "Technology Innovation":
            cmd_parts.append(f'--domain "{params["domain"].value}"')
        if "models" in params and params["models"].value != 3:
            cmd_parts.append(f'--models {params["models"].value}')
        if "instructions" in params and params["instructions"].value != 3:
            cmd_parts.append(f'--instructions {params["instructions"].value}')
        if "variations" in params and params["variations"].value != 2:
            cmd_parts.append(f'--variations {params["variations"].value}')
        
        # Add sampling parameters
        if "max_combinations" in params and params["max_combinations"].value != 12:
            cmd_parts.append(f'--max-combinations {params["max_combinations"].value}')
        if "sampling_method" in params and params["sampling_method"].value != "stratified":
            cmd_parts.append(f'--sampling-method {params["sampling_method"].value}')
        
        # Add boolean flags
        if "balanced_models" in params and params["balanced_models"].value:
            cmd_parts.append("--balanced-models")
        if "use_ollama" in params and params["use_ollama"].value:
            cmd_parts.append("--use-ollama")
        if "simulate" in params and params["simulate"].value:
            cmd_parts.append("--simulate")
        if "dry_run" in params and params["dry_run"].value:
            cmd_parts.append("--dry-run")
        
        return " ".join(cmd_parts)
    
    def update_parameter(self, name: str, value: Any):
        """Update a parameter value and trigger updates"""
        if name in self.state.parameters:
            param = self.state.parameters[name]
            param.value = value
            param.status = ParameterStatus.MODIFIED if value != param.default_value else ParameterStatus.DEFAULT
            
            # Trigger update callbacks
            for callback in self.update_callbacks:
                callback(name, value)
            
            # Update estimates
            self._update_estimates()
    
    def add_update_callback(self, callback: Callable):
        """Add callback for parameter updates"""
        self.update_callbacks.append(callback)
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get current configuration as dictionary"""
        return {name: param.value for name, param in self.state.parameters.items()}
    
    def load_config(self, config: Dict[str, Any]):
        """Load configuration from dictionary"""
        for name, value in config.items():
            if name in self.state.parameters:
                self.update_parameter(name, value)

def create_configuration_dashboard(console: Optional[Console] = None) -> ConfigurationDashboard:
    """Factory function to create a configuration dashboard"""
    return ConfigurationDashboard(console)

# Interactive dashboard runner
def run_interactive_dashboard():
    """Run the interactive configuration dashboard"""
    console = Console()
    dashboard = create_configuration_dashboard(console)
    
    # Display initial dashboard
    dashboard.display_dashboard(DashboardMode.OVERVIEW)
    
    # Simple interaction loop (to be enhanced)
    console.print("\n[bold cyan]Dashboard displayed! Press Enter to continue...[/]")
    input()

if __name__ == "__main__":
    run_interactive_dashboard()