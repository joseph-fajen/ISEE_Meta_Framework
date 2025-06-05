"""
Unified Parameter Editor for ISEE Configuration Dashboard

This module provides enhanced parameter editors for simpler parameters that
don't require extensive customization but benefit from the standardized framework.

Handles:
- sampling_method: Strategic sampling approaches
- max_combinations: Resource management with smart limits
- output_format: Result format selection with examples
- Boolean toggles: Enhanced toggle interfaces with explanations
"""

from typing import List, Dict, Any, Optional, Union
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Confirm, IntPrompt

from enhanced_parameter_editor import EnhancedParameterEditor, ParameterItem, SelectionMode


class SamplingMethodParameterEditor(EnhancedParameterEditor):
    """Enhanced editor for sampling_method parameter with strategic explanations"""
    
    def __init__(self, console: Console, dashboard_state, **kwargs):
        method_param = dashboard_state.parameters.get("sampling_method")
        current_method = method_param.value if method_param else "random"
        super().__init__(console, "sampling_method", current_method)
        self.dashboard_state = dashboard_state
        self.selection_mode = SelectionMode.SINGLE
        self.show_help_on_start = True
    
    def load_items(self) -> List[ParameterItem]:
        """Load available sampling methods with detailed explanations"""
        sampling_methods = [
            {
                "id": "random",
                "name": "Random Sampling",
                "description": "Randomly selects combinations for maximum diversity and unbiased exploration",
                "strategy": "Exploration",
                "best_for": "Discovery, broad analysis, unbiased results",
                "trade_offs": "May miss systematic patterns",
                "complexity": "Simple",
                "icon": "🎲",
                "recommended_for": ["exploratory research", "creative ideation", "broad discovery"]
            },
            {
                "id": "stratified",
                "name": "Stratified Sampling", 
                "description": "Ensures balanced representation across different parameter dimensions",
                "strategy": "Balanced",
                "best_for": "Comprehensive coverage, fair representation",
                "trade_offs": "May be less creative, more predictable",
                "complexity": "Moderate",
                "icon": "⚖️",
                "recommended_for": ["systematic analysis", "comprehensive evaluation", "balanced perspectives"]
            },
            {
                "id": "systematic",
                "name": "Systematic Sampling",
                "description": "Uses structured intervals to ensure even coverage across parameter space",
                "strategy": "Structured",
                "best_for": "Methodical analysis, reproducible results",
                "trade_offs": "May miss edge cases, less serendipitous",
                "complexity": "Advanced", 
                "icon": "📐",
                "recommended_for": ["scientific research", "methodical evaluation", "structured analysis"]
            },
            {
                "id": "adaptive",
                "name": "Adaptive Sampling",
                "description": "Dynamically adjusts sampling based on initial results for optimal coverage",
                "strategy": "Intelligent",
                "best_for": "Quality optimization, efficient exploration",
                "trade_offs": "More complex, requires computational overhead",
                "complexity": "Expert",
                "icon": "🧠",
                "recommended_for": ["advanced research", "optimization tasks", "quality-focused analysis"]
            }
        ]
        
        items = []
        for method_data in sampling_methods:
            metadata = {
                "strategy": method_data["strategy"],
                "best_for": method_data["best_for"],
                "trade_offs": method_data["trade_offs"],
                "complexity": method_data["complexity"],
                "icon": method_data["icon"],
                "recommended_for": method_data["recommended_for"]
            }
            
            items.append(ParameterItem(
                id=method_data["id"],
                name=f"{method_data['icon']} {method_data['name']}",
                description=method_data["description"],
                metadata=metadata
            ))
        
        return items
    
    def get_display_table(self) -> Table:
        """Create Rich table showing sampling methods with strategic information"""
        table = Table(
            title="🔬 Sampling Strategy Selection",
            show_header=True,
            header_style="bold white",
            show_lines=True
        )
        
        table.add_column("#", style="green", width=3)
        table.add_column("Method", style="bold cyan", min_width=20)
        table.add_column("Strategy", style="yellow", width=12)
        table.add_column("Complexity", style="blue", width=10)
        table.add_column("Best For", style="white", max_width=35)
        
        for i, item in enumerate(self.items, 1):
            # Highlight current selection
            style = "bold green" if item.id == self.current_value else None
            
            table.add_row(
                str(i),
                item.name,
                item.metadata.get("strategy", "Unknown"),
                item.metadata.get("complexity", "Unknown"),
                item.metadata.get("best_for", "General use"),
                style=style
            )
        
        return table
    
    def validate_selection(self, user_input: str) -> bool:
        """Validate sampling method selection"""
        try:
            num = int(user_input)
            return 1 <= num <= len(self.items)
        except ValueError:
            return False
    
    def apply_selection(self, selection: int) -> None:
        """Apply sampling method selection to dashboard state"""
        if 1 <= selection <= len(self.items):
            selected_method = self.items[selection - 1]
            method_id = selected_method.id
            self.dashboard_state.parameters["sampling_method"].value = method_id
            self.current_value = method_id
    
    def _show_item_preview(self, item: ParameterItem, number: int) -> None:
        """Enhanced preview for sampling methods"""
        icon = item.metadata.get("icon", "🔬")
        strategy = item.metadata.get("strategy", "Unknown")
        complexity = item.metadata.get("complexity", "Unknown")
        
        content = [
            f"[bold cyan]{item.name}[/bold cyan]",
            "",
            f"[yellow]Strategy Type:[/yellow] {strategy}",
            f"[yellow]Complexity:[/yellow] {complexity}",
            f"[yellow]Description:[/yellow] {item.description}",
            "",
            f"[green]Best For:[/green] {item.metadata.get('best_for', 'General use')}",
            f"[red]Trade-offs:[/red] {item.metadata.get('trade_offs', 'None identified')}",
            "",
            "[bold blue]Recommended Use Cases:[/bold blue]"
        ]
        
        # Add recommended use cases
        for use_case in item.metadata.get("recommended_for", []):
            content.append(f"• {use_case.title()}")
        
        preview_panel = Panel(
            "\n".join(content),
            title=f"Sampling Method #{number} Preview",
            border_style="cyan"
        )
        self.console.print(preview_panel)
    
    def _display_parameter_specific_help(self) -> None:
        """Display sampling method-specific help"""
        self.console.print("\n[bold cyan]Sampling Strategy Guide:[/bold cyan]")
        self.console.print("• [green]Random[/green]: Best for discovery and unbiased exploration")
        self.console.print("• [yellow]Stratified[/yellow]: Ensures balanced representation across parameters")
        self.console.print("• [blue]Systematic[/blue]: Methodical coverage for scientific analysis")
        self.console.print("• [magenta]Adaptive[/magenta]: Intelligent optimization for advanced users")
        self.console.print("")
        self.console.print("[bold yellow]Impact on Results:[/bold yellow]")
        self.console.print("• Sampling method affects which combinations are selected from the total possibility space")
        self.console.print("• Different methods can lead to different insights and conclusions")
        self.console.print("• Choose based on your analysis goals and available resources")


class MaxCombinationsParameterEditor(EnhancedParameterEditor):
    """Enhanced editor for max_combinations parameter with resource guidance"""
    
    def __init__(self, console: Console, dashboard_state, **kwargs):
        max_param = dashboard_state.parameters.get("max_combinations")
        current_max = max_param.value if max_param else 12
        super().__init__(console, "max_combinations", current_max)
        self.dashboard_state = dashboard_state
        self.selection_mode = SelectionMode.HYBRID  # Both presets and custom values
        self.show_help_on_start = True
        
        # Resource limits based on typical usage patterns
        self.resource_profiles = {
            "quick": {"max": 5, "time": "2-5 min", "cost": "$1-3", "description": "Fast exploration"},
            "standard": {"max": 12, "time": "5-15 min", "cost": "$3-8", "description": "Balanced analysis"},
            "comprehensive": {"max": 25, "time": "15-40 min", "cost": "$8-20", "description": "Thorough investigation"},
            "extensive": {"max": 50, "time": "40-90 min", "cost": "$20-50", "description": "Maximum coverage"},
            "research": {"max": 100, "time": "90+ min", "cost": "$50+", "description": "Research-grade analysis"}
        }
    
    def load_items(self) -> List[ParameterItem]:
        """Load combination limits with resource profiles"""
        items = []
        
        for profile_id, profile_data in self.resource_profiles.items():
            max_combinations = profile_data["max"]
            time_estimate = profile_data["time"]
            cost_estimate = profile_data["cost"]
            description = profile_data["description"]
            
            # Determine complexity and icon based on profile
            if max_combinations <= 10:
                complexity = "Basic"
                icon = "⚡"
                color = "green"
            elif max_combinations <= 30:
                complexity = "Intermediate"
                icon = "⚖️"
                color = "yellow"
            else:
                complexity = "Advanced"
                icon = "🔬"
                color = "red"
            
            metadata = {
                "max_combinations": max_combinations,
                "time_estimate": time_estimate,
                "cost_estimate": cost_estimate,
                "complexity": complexity,
                "icon": icon,
                "color": color,
                "profile_type": profile_id
            }
            
            items.append(ParameterItem(
                id=f"profile_{profile_id}",
                name=f"{icon} {profile_id.title()} ({max_combinations} combinations)",
                description=f"{description} - {time_estimate}, ~{cost_estimate}",
                metadata=metadata
            ))
        
        return items
    
    def get_display_table(self) -> Table:
        """Create Rich table showing combination limits with resource estimates"""
        table = Table(
            title="⚙️ Combination Limits & Resource Profiles",
            show_header=True,
            header_style="bold white",
            show_lines=True
        )
        
        table.add_column("#", style="green", width=3)
        table.add_column("Profile", style="bold cyan", min_width=25)
        table.add_column("Combinations", style="yellow", width=12)
        table.add_column("Time Est.", style="blue", width=10)
        table.add_column("Cost Est.", style="magenta", width=10)
        table.add_column("Complexity", style="white", width=12)
        
        for i, item in enumerate(self.items, 1):
            color = item.metadata.get("color", "white")
            combinations = item.metadata.get("max_combinations", "Unknown")
            time_est = item.metadata.get("time_estimate", "Unknown")
            cost_est = item.metadata.get("cost_estimate", "Unknown")
            complexity = item.metadata.get("complexity", "Unknown")
            
            # Highlight if close to current value
            style = "bold green" if abs(combinations - self.current_value) <= 2 else None
            
            table.add_row(
                str(i),
                f"[{color}]{item.name}[/{color}]",
                str(combinations),
                time_est,
                cost_est,
                complexity,
                style=style
            )
        
        return table
    
    def validate_selection(self, user_input: str) -> bool:
        """Validate combination limit selection"""
        try:
            if user_input.isdigit():
                num = int(user_input)
                # Allow both profile selection and direct number input
                return num > 0
            return False
        except ValueError:
            return False
    
    def apply_selection(self, selection: Union[int, str]) -> None:
        """Apply combination limit selection"""
        if isinstance(selection, int):
            if selection <= len(self.items):
                # Profile selection
                selected_profile = self.items[selection - 1]
                max_combinations = selected_profile.metadata.get("max_combinations", 12)
                self.dashboard_state.parameters["max_combinations"].value = max_combinations
                self.current_value = max_combinations
            else:
                # Direct number input
                self.dashboard_state.parameters["max_combinations"].value = selection
                self.current_value = selection
    
    def _process_selection_input(self, user_input: str) -> bool:
        """Override to handle both profile and direct number selection"""
        try:
            num = int(user_input)
            
            if 1 <= num <= len(self.items):
                # Profile selection
                self.apply_selection(num)
                selected_profile = self.items[num - 1]
                max_combinations = selected_profile.metadata.get("max_combinations", 12)
                self.console.print(f"[green]✓ Selected {selected_profile.metadata.get('profile_type', 'profile').title()} profile: {max_combinations} combinations[/green]")
                return True
            else:
                # Direct number input - validate resource limits
                if num > 200:
                    self.console.print("[red]⚠️ Very high combination count may cause performance issues[/red]")
                    if not Confirm.ask(f"Continue with {num} combinations?"):
                        return False
                elif num > 50:
                    self.console.print(f"[yellow]⚠️ {num} combinations will be expensive and time-consuming[/yellow]")
                    if not Confirm.ask(f"Continue with {num} combinations?"):
                        return False
                
                self.apply_selection(num)
                self.console.print(f"[green]✓ Set custom limit: {num} combinations[/green]")
                return True
                
        except ValueError:
            self.console.print("[red]Please enter a valid number[/red]")
            return False
    
    def _display_parameter_specific_help(self) -> None:
        """Display combination limits-specific help"""
        self.console.print("\n[bold cyan]Combination Limits Guide:[/bold cyan]")
        self.console.print("• Higher limits = more comprehensive but more expensive")
        self.console.print("• Lower limits = faster and cheaper but less coverage")
        self.console.print("• Choose based on your time, budget, and depth requirements")
        self.console.print("")
        self.console.print("[bold yellow]Resource Planning:[/bold yellow]")
        self.console.print("• ⚡ Quick (≤10): Rapid insights, minimal cost")
        self.console.print("• ⚖️ Standard (10-30): Balanced exploration")
        self.console.print("• 🔬 Advanced (30+): Research-grade analysis")


class OutputFormatParameterEditor(EnhancedParameterEditor):
    """Enhanced editor for output_format parameter with format examples"""
    
    def __init__(self, console: Console, dashboard_state, **kwargs):
        format_param = dashboard_state.parameters.get("output_format")
        current_format = format_param.value if format_param else "json"
        super().__init__(console, "output_format", current_format)
        self.dashboard_state = dashboard_state
        self.selection_mode = SelectionMode.SINGLE
        self.show_help_on_start = True
    
    def load_items(self) -> List[ParameterItem]:
        """Load available output formats with examples and use cases"""
        formats = [
            {
                "id": "json",
                "name": "JSON",
                "description": "Structured data format ideal for programmatic processing and APIs",
                "icon": "📄",
                "use_cases": ["API integration", "data processing", "web applications"],
                "pros": ["Machine readable", "Structured", "Widely supported"],
                "cons": ["Not human-friendly", "Complex for simple viewing"],
                "example": '{"ideas": [{"id": 1, "text": "Innovation idea", "score": 8.5}]}',
                "best_for": "automated processing"
            },
            {
                "id": "yaml",
                "name": "YAML",
                "description": "Human-readable data format that's also machine-processable",
                "icon": "📋",
                "use_cases": ["configuration files", "documentation", "readable exports"],
                "pros": ["Human readable", "Clean syntax", "Supports comments"],
                "cons": ["Indentation sensitive", "Less universal than JSON"],
                "example": "ideas:\n  - id: 1\n    text: Innovation idea\n    score: 8.5",
                "best_for": "human review and documentation"
            },
            {
                "id": "text",
                "name": "Plain Text",
                "description": "Simple, readable text format for easy sharing and reading",
                "icon": "📝",
                "use_cases": ["reports", "email sharing", "presentations"],
                "pros": ["Universally readable", "Easy to share", "No special tools needed"],
                "cons": ["No structure", "Limited formatting", "Hard to process"],
                "example": "1. Innovation idea (Score: 8.5)\n   Generated through systematic analysis...",
                "best_for": "human consumption and sharing"
            },
            {
                "id": "csv",
                "name": "CSV",
                "description": "Comma-separated values for spreadsheet analysis and data import",
                "icon": "📊",
                "use_cases": ["spreadsheet analysis", "data import", "statistical analysis"],
                "pros": ["Spreadsheet compatible", "Data analysis friendly", "Simple structure"],
                "cons": ["Limited formatting", "No nested data", "Comma conflicts"],
                "example": "id,text,score,category\n1,Innovation idea,8.5,Technology",
                "best_for": "spreadsheet analysis and data import"
            },
            {
                "id": "markdown",
                "name": "Markdown",
                "description": "Formatted text that renders nicely in documentation and web contexts",
                "icon": "📖",
                "use_cases": ["documentation", "reports", "GitHub/web display"],
                "pros": ["Formatted text", "Web-friendly", "Readable as text"],
                "cons": ["Limited data structure", "Formatting focused"],
                "example": "# Innovation Ideas\n\n## Idea 1 (Score: 8.5)\nGenerated through...",
                "best_for": "documentation and reports"
            }
        ]
        
        items = []
        for format_data in formats:
            metadata = {
                "icon": format_data["icon"],
                "use_cases": format_data["use_cases"],
                "pros": format_data["pros"],
                "cons": format_data["cons"],
                "example": format_data["example"],
                "best_for": format_data["best_for"]
            }
            
            items.append(ParameterItem(
                id=format_data["id"],
                name=f"{format_data['icon']} {format_data['name']}",
                description=format_data["description"],
                metadata=metadata
            ))
        
        return items
    
    def get_display_table(self) -> Table:
        """Create Rich table showing output formats with use case information"""
        table = Table(
            title="📁 Output Format Selection",
            show_header=True,
            header_style="bold white",
            show_lines=True
        )
        
        table.add_column("#", style="green", width=3)
        table.add_column("Format", style="bold cyan", min_width=15)
        table.add_column("Best For", style="yellow", max_width=25)
        table.add_column("Primary Use Cases", style="white", max_width=35)
        
        for i, item in enumerate(self.items, 1):
            # Highlight current selection
            style = "bold green" if item.id == self.current_value else None
            
            best_for = item.metadata.get("best_for", "general use")
            use_cases = ", ".join(item.metadata.get("use_cases", [])[:3])
            
            table.add_row(
                str(i),
                item.name,
                best_for.title(),
                use_cases,
                style=style
            )
        
        return table
    
    def validate_selection(self, user_input: str) -> bool:
        """Validate output format selection"""
        try:
            num = int(user_input)
            return 1 <= num <= len(self.items)
        except ValueError:
            return False
    
    def apply_selection(self, selection: int) -> None:
        """Apply output format selection to dashboard state"""
        if 1 <= selection <= len(self.items):
            selected_format = self.items[selection - 1]
            format_id = selected_format.id
            self.dashboard_state.parameters["output_format"].value = format_id
            self.current_value = format_id
    
    def _show_item_preview(self, item: ParameterItem, number: int) -> None:
        """Enhanced preview for output formats with examples"""
        icon = item.metadata.get("icon", "📁")
        best_for = item.metadata.get("best_for", "general use")
        
        content = [
            f"[bold cyan]{item.name}[/bold cyan]",
            "",
            f"[yellow]Description:[/yellow] {item.description}",
            f"[yellow]Best For:[/yellow] {best_for.title()}",
            "",
            "[green]Advantages:[/green]"
        ]
        
        # Add pros
        for pro in item.metadata.get("pros", []):
            content.append(f"  ✓ {pro}")
        
        content.append("\n[red]Considerations:[/red]")
        # Add cons
        for con in item.metadata.get("cons", []):
            content.append(f"  • {con}")
        
        # Add example
        example = item.metadata.get("example", "No example available")
        content.extend([
            "",
            "[bold blue]Example Output:[/bold blue]",
            f"[dim]{example[:100]}{'...' if len(example) > 100 else ''}[/dim]"
        ])
        
        preview_panel = Panel(
            "\n".join(content),
            title=f"Output Format #{number} Preview",
            border_style="cyan"
        )
        self.console.print(preview_panel)
    
    def _display_parameter_specific_help(self) -> None:
        """Display output format-specific help"""
        self.console.print("\n[bold cyan]Output Format Selection Guide:[/bold cyan]")
        self.console.print("• [green]JSON[/green]: Best for APIs and automated processing")
        self.console.print("• [yellow]YAML[/yellow]: Good balance of readability and structure")
        self.console.print("• [blue]Text[/blue]: Simplest for human reading and sharing")
        self.console.print("• [magenta]CSV[/magenta]: Ideal for spreadsheet analysis")
        self.console.print("• [cyan]Markdown[/cyan]: Perfect for documentation and reports")
        self.console.print("")
        self.console.print("[bold yellow]Consider Your Workflow:[/bold yellow]")
        self.console.print("• How will you use the results?")
        self.console.print("• Do you need machine processing or human reading?")
        self.console.print("• Will you import into other tools?")


# Factory function for creating unified parameter editors
def create_unified_parameter_editor(parameter_name: str, console: Console, dashboard_state, **kwargs) -> Optional[EnhancedParameterEditor]:
    """Create unified parameter editors for simpler parameters"""
    
    if parameter_name == "sampling_method":
        return SamplingMethodParameterEditor(console, dashboard_state, **kwargs)
    elif parameter_name == "max_combinations":
        return MaxCombinationsParameterEditor(console, dashboard_state, **kwargs)
    elif parameter_name == "output_format":
        return OutputFormatParameterEditor(console, dashboard_state, **kwargs)
    else:
        return None