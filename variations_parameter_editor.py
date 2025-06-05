"""
Enhanced Variations Parameter Editor

Provides rich, interactive editing for the variations parameter with:
- Impact analysis for different variation counts
- Strategic guidance on optimal variation selection
- Real-time cost and quality implications
- Visual representation of variation effects
"""

from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from enhanced_parameter_editor import EnhancedParameterEditor, ParameterItem, SelectionMode


class VariationsParameterEditor(EnhancedParameterEditor):
    """Enhanced editor for variations parameter with strategic guidance"""
    
    def __init__(self, console: Console, dashboard_state, **kwargs):
        variations_param = dashboard_state.parameters.get("variations")
        current_variations = variations_param.value if variations_param else 2
        super().__init__(console, "variations", current_variations)
        self.dashboard_state = dashboard_state
        self.selection_mode = SelectionMode.SINGLE
        self.show_help_on_start = True
        
        # Variation configuration options
        self.variation_configs = [
            {
                "count": 1,
                "name": "Single Variation",
                "description": "Fastest execution, minimal exploration",
                "use_case": "Quick tests, proof of concepts",
                "quality_score": 3,
                "exploration_score": 1,
                "cost_multiplier": 1.0,
                "time_multiplier": 1.0,
                "recommended_for": ["Beginner-Friendly", "Quick Exploration"]
            },
            {
                "count": 2,
                "name": "Dual Variation",
                "description": "Balanced approach with alternative perspectives",
                "use_case": "Standard exploration, comparative analysis",
                "quality_score": 6,
                "exploration_score": 4,
                "cost_multiplier": 2.0,
                "time_multiplier": 2.0,
                "recommended_for": ["Quick Exploration", "Content Creation", "Problem Solving"]
            },
            {
                "count": 3,
                "name": "Triple Variation",
                "description": "Good diversity with manageable complexity",
                "use_case": "Comprehensive analysis, multiple angles",
                "quality_score": 8,
                "exploration_score": 7,
                "cost_multiplier": 3.0,
                "time_multiplier": 3.0,
                "recommended_for": ["Deep Analysis", "Creative Innovation", "Strategic Planning"]
            },
            {
                "count": 4,
                "name": "Quadruple Variation",
                "description": "High diversity, thorough exploration",
                "use_case": "Critical decisions, maximum perspective range",
                "quality_score": 9,
                "exploration_score": 9,
                "cost_multiplier": 4.0,
                "time_multiplier": 4.0,
                "recommended_for": ["Deep Analysis", "Strategic Planning", "Learning Design"]
            },
            {
                "count": 5,
                "name": "Quintuple Variation",
                "description": "Maximum exploration with diminishing returns",
                "use_case": "Research projects, exhaustive analysis",
                "quality_score": 9,
                "exploration_score": 10,
                "cost_multiplier": 5.0,
                "time_multiplier": 5.0,
                "recommended_for": ["Deep Analysis", "Learning Design", "Custom Exploration"]
            }
        ]
    
    def load_items(self) -> List[ParameterItem]:
        """Load variation configuration options"""
        items = []
        
        for config in self.variation_configs:
            # Calculate estimated impact
            base_combinations = self._get_base_combinations()
            estimated_combinations = base_combinations * config["cost_multiplier"]
            estimated_cost = estimated_combinations * 0.08
            estimated_time = config["time_multiplier"] * 6.0  # Base 6 minutes
            
            item = ParameterItem(
                id=f"variations_{config['count']}",
                name=config["name"],
                description=config["description"],
                metadata={
                    "count": config["count"],
                    "use_case": config["use_case"],
                    "quality_score": config["quality_score"],
                    "exploration_score": config["exploration_score"],
                    "estimated_combinations": int(estimated_combinations),
                    "estimated_cost": estimated_cost,
                    "estimated_time": estimated_time,
                    "recommended_for": config["recommended_for"]
                }
            )
            items.append(item)
        
        return items
    
    def get_display_table(self) -> Table:
        """Create Rich table for displaying variation options"""
        table = Table(show_header=True, header_style="bold blue", show_lines=True)
        table.add_column("#", style="green", width=3)
        table.add_column("Variations", style="cyan", width=12)
        table.add_column("Name", style="white", min_width=15)
        table.add_column("Quality", style="yellow", width=8)
        table.add_column("Exploration", style="magenta", width=11)
        table.add_column("Est. Cost", style="red", width=10)
        table.add_column("Est. Time", style="blue", width=10)
        
        for i, item in enumerate(self.items, 1):
            # Style quality and exploration scores
            quality_style = self._get_score_style(item.metadata["quality_score"])
            exploration_style = self._get_score_style(item.metadata["exploration_score"])
            
            table.add_row(
                str(i),
                str(item.metadata["count"]),
                item.name,
                f"[{quality_style}]{item.metadata['quality_score']}/10[/{quality_style}]",
                f"[{exploration_style}]{item.metadata['exploration_score']}/10[/{exploration_style}]",
                f"${item.metadata['estimated_cost']:.2f}",
                f"{item.metadata['estimated_time']:.1f}m"
            )
        
        return table
    
    def validate_selection(self, user_input: str) -> bool:
        """Validate variations selection"""
        try:
            count = int(user_input)
            if count < 1:
                self.console.print("[red]Variations must be at least 1[/red]")
                return False
            elif count > 10:
                self.console.print("[red]Maximum 10 variations recommended for cost control[/red]")
                return False
            return True
        except ValueError:
            self.console.print("[red]Please enter a valid number[/red]")
            return False
    
    def apply_selection(self, selection: Any) -> None:
        """Apply variations selection to dashboard state"""
        if isinstance(selection, int) and selection <= len(self.items):
            # User selected a predefined configuration
            selected_item = self.items[selection - 1]
            variations_count = selected_item.metadata["count"]
        else:
            # User entered custom number (handled via custom input)
            variations_count = int(selection)
        
        self.dashboard_state.update_parameter("variations", variations_count)
        self.console.print(f"[green]✓ Variations set to {variations_count}[/green]")
    
    def edit_parameter(self) -> None:
        """Enhanced variations editing with strategic guidance"""
        try:
            self.items = self.load_items()
            
            self.console.print(f"\n[bold cyan]Configure Variations:[/bold cyan]")
            self.console.print("Variations control how many different approaches each model uses for your query.")
            
            # Show current variations
            variations_param = self.dashboard_state.parameters.get("variations")
            current_variations = variations_param.value if variations_param else 2
            self.console.print(f"\n[bold green]Current Variations:[/bold green] {current_variations}")
            
            # Show strategic impact
            self._show_strategic_impact()
            
            # Display options table
            table = self.get_display_table()
            self.console.print(table)
            
            # Show current recommendation
            self._show_current_recommendation()
            
            # Show options
            self.console.print("\n[bold yellow]Options:[/bold yellow]")
            self.console.print("• [cyan]Number[/cyan] (1-5) - Select predefined configuration")
            self.console.print("• [cyan]Custom[/cyan] - Enter custom variation count")
            self.console.print("• [cyan]Special commands:[/cyan] 'preview <number>', 'impact', 'help', 'done'")
            
            while True:
                user_input = Prompt.ask("Variations selection", default=str(current_variations)).strip()
                
                if user_input.lower() == "done":
                    return
                elif user_input.lower() == "impact":
                    self._show_impact_analysis()
                    continue
                elif user_input.lower() == "custom":
                    self._handle_custom_variations_input()
                    break
                
                # Handle special commands
                if self._handle_special_commands(user_input):
                    continue
                
                # Try to select predefined configuration
                try:
                    num = int(user_input)
                    if 1 <= num <= len(self.items):
                        selected_item = self.items[num - 1]
                        
                        # Show selection preview
                        self._show_variations_preview(selected_item, num)
                        
                        # Confirm selection
                        if Prompt.ask("Use this configuration?", choices=["y", "n"], default="y") == "y":
                            self.apply_selection(num)
                            break
                    elif num > len(self.items):
                        # Custom number
                        if self.validate_selection(user_input):
                            self._show_custom_variations_analysis(num)
                            if Prompt.ask("Use this custom configuration?", choices=["y", "n"], default="y") == "y":
                                self.apply_selection(num)
                                break
                    else:
                        self.console.print(f"[red]Invalid number. Use 1-{len(self.items)} or enter custom number[/red]")
                except ValueError:
                    self.console.print("[red]Please enter a valid number[/red]")
        
        except Exception as e:
            self.console.print(f"[red]Error editing variations: {e}[/red]")
    
    def _show_strategic_impact(self) -> None:
        """Show strategic impact of variations"""
        impact_content = [
            "[bold yellow]Strategic Impact of Variations:[/bold yellow]",
            "",
            "• [green]More variations[/green] = More diverse perspectives and higher quality insights",
            "• [red]More variations[/red] = Higher cost and longer execution time",
            "• [cyan]Sweet spot[/cyan] = 2-3 variations for most use cases",
            "• [yellow]Diminishing returns[/yellow] = Beyond 4 variations, improvement plateaus"
        ]
        
        impact_panel = Panel(
            "\n".join(impact_content),
            title="Strategic Guidance",
            border_style="yellow"
        )
        self.console.print(impact_panel)
    
    def _show_current_recommendation(self) -> None:
        """Show recommendation based on current dashboard state"""
        # Get current purpose if available
        purpose_param = self.dashboard_state.parameters.get("purpose")
        purpose = purpose_param.value if purpose_param else ""
        
        if purpose:
            if purpose in ["Beginner-Friendly", "Quick Exploration"]:
                recommended = "2 variations for balanced exploration"
                style = "green"
            elif purpose in ["Content Creation", "Problem Solving"]:
                recommended = "3 variations for comprehensive analysis"
                style = "cyan"
            elif purpose in ["Deep Analysis", "Strategic Planning"]:
                recommended = "4 variations for maximum insight quality"
                style = "yellow"
            else:
                recommended = "2-3 variations for most scenarios"
                style = "white"
            
            self.console.print(f"\n[{style}]💡 Recommendation for {purpose}: {recommended}[/{style}]")
    
    def _show_impact_analysis(self) -> None:
        """Show detailed impact analysis"""
        analysis_table = Table(title="Variations Impact Analysis", show_header=True, header_style="bold yellow")
        analysis_table.add_column("Variations", style="cyan")
        analysis_table.add_column("Quality Gain", style="green")
        analysis_table.add_column("Cost Impact", style="red")
        analysis_table.add_column("Time Impact", style="blue")
        analysis_table.add_column("Recommended For", style="white")
        
        for item in self.items:
            quality_gain = f"+{(item.metadata['quality_score'] - 3) * 10}%"
            cost_impact = f"+{(item.metadata['cost_multiplier'] - 1) * 100:.0f}%"
            time_impact = f"+{(item.metadata['time_multiplier'] - 1) * 100:.0f}%"
            recommended = ", ".join(item.metadata["recommended_for"][:2])
            
            analysis_table.add_row(
                str(item.metadata["count"]),
                quality_gain,
                cost_impact,
                time_impact,
                recommended
            )
        
        self.console.print(analysis_table)
    
    def _show_variations_preview(self, item: ParameterItem, number: int) -> None:
        """Show preview of a variations configuration"""
        content = [
            f"[bold cyan]{item.name}[/bold cyan]",
            "",
            f"[yellow]Variations Count:[/yellow] {item.metadata['count']}",
            f"[yellow]Description:[/yellow] {item.description}",
            f"[yellow]Use Case:[/yellow] {item.metadata['use_case']}",
            "",
            f"[yellow]Quality Score:[/yellow] {item.metadata['quality_score']}/10",
            f"[yellow]Exploration Score:[/yellow] {item.metadata['exploration_score']}/10",
            "",
            f"[yellow]Estimated Cost:[/yellow] ${item.metadata['estimated_cost']:.2f}",
            f"[yellow]Estimated Time:[/yellow] {item.metadata['estimated_time']:.1f} minutes",
            f"[yellow]Estimated Combinations:[/yellow] {item.metadata['estimated_combinations']}",
            "",
            f"[yellow]Recommended For:[/yellow] {', '.join(item.metadata['recommended_for'])}"
        ]
        
        preview_panel = Panel(
            "\n".join(content),
            title=f"Variations Configuration #{number} Preview",
            border_style="cyan"
        )
        self.console.print(preview_panel)
    
    def _handle_custom_variations_input(self) -> None:
        """Handle custom variations input"""
        self.console.print("\n[bold cyan]Enter Custom Variations Count:[/bold cyan]")
        self.console.print("[dim]Tip: Consider cost vs. quality trade-offs[/dim]")
        
        while True:
            variations_param = self.dashboard_state.parameters.get("variations")
            current_variations = variations_param.value if variations_param else 2
            variations = Prompt.ask("Variations count", default=str(current_variations)).strip()
            
            if variations.lower() == "done":
                return
            
            if self.validate_selection(variations):
                variations_count = int(variations)
                self._show_custom_variations_analysis(variations_count)
                
                if Prompt.ask("Use this configuration?", choices=["y", "n"], default="y") == "y":
                    self.apply_selection(variations_count)
                    break
            else:
                self.console.print("[dim]Please try again or type 'done' to cancel[/dim]")
    
    def _show_custom_variations_analysis(self, count: int) -> None:
        """Show analysis for custom variations count"""
        base_combinations = self._get_base_combinations()
        estimated_combinations = base_combinations * count
        estimated_cost = estimated_combinations * 0.08
        estimated_time = count * 6.0
        
        # Assess quality and exploration scores
        quality_score = min(10, 3 + (count - 1) * 1.5)
        exploration_score = min(10, count * 2)
        
        analysis_content = [
            f"[yellow]Variations Count:[/yellow] {count}",
            f"[yellow]Quality Score:[/yellow] {quality_score:.1f}/10",
            f"[yellow]Exploration Score:[/yellow] {exploration_score:.1f}/10",
            "",
            f"[yellow]Estimated Combinations:[/yellow] {estimated_combinations}",
            f"[yellow]Estimated Cost:[/yellow] ${estimated_cost:.2f}",
            f"[yellow]Estimated Time:[/yellow] {estimated_time:.1f} minutes",
            "",
            self._get_variations_assessment(count)
        ]
        
        analysis_panel = Panel(
            "\n".join(analysis_content),
            title="Custom Variations Analysis",
            border_style="cyan"
        )
        self.console.print(analysis_panel)
    
    def _get_variations_assessment(self, count: int) -> str:
        """Get assessment text for variations count"""
        if count == 1:
            return "[red]⚠️ Minimal exploration - Consider 2+ for better insights[/red]"
        elif count == 2:
            return "[green]✓ Good balance of cost and exploration[/green]"
        elif count == 3:
            return "[cyan]✓ Comprehensive analysis with good ROI[/cyan]"
        elif count == 4:
            return "[yellow]⚡ High-quality insights with increased cost[/yellow]"
        elif count >= 5:
            return "[magenta]🔥 Maximum exploration - diminishing returns likely[/magenta]"
        else:
            return ""
    
    def _get_base_combinations(self) -> int:
        """Get base combinations from current dashboard state"""
        # Simple estimation - in real implementation, calculate from current parameters
        return 12
    
    def _get_score_style(self, score: int) -> str:
        """Get color style based on score"""
        if score <= 3:
            return "red"
        elif score <= 6:
            return "yellow"
        elif score <= 8:
            return "green"
        else:
            return "bright_green"
    
    def _display_parameter_specific_help(self) -> None:
        """Display variations-specific help"""
        help_content = [
            "[bold yellow]Variations Best Practices:[/bold yellow]",
            "",
            "• Start with 2-3 variations for most projects",
            "• Use 1 variation only for quick tests or proofs of concept",
            "• Consider 4+ variations for critical decisions or research",
            "• Balance quality needs with budget and time constraints",
            "",
            "[bold yellow]Quality vs Cost Trade-offs:[/bold yellow]",
            "• Each variation multiplies both cost and execution time",
            "• Quality improvements plateau after 4-5 variations",
            "• Consider your specific use case and requirements"
        ]
        
        help_panel = Panel(
            "\n".join(help_content),
            title="Variations Help",
            border_style="yellow"
        )
        self.console.print(help_panel)