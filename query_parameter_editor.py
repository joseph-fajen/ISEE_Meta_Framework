"""
Enhanced Query Parameter Editor

Provides rich, interactive editing for the query parameter with:
- Query validation and suggestions
- Example queries with context
- Real-time feedback and impact analysis
- Special commands for query exploration
"""

from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from enhanced_parameter_editor import EnhancedParameterEditor, ParameterItem, SelectionMode


class QueryParameterEditor(EnhancedParameterEditor):
    """Enhanced editor for query parameters with validation and examples"""
    
    def __init__(self, console: Console, dashboard_state, **kwargs):
        super().__init__(console, "query", dashboard_state.parameters.get("query", {}).get("value", ""))
        self.dashboard_state = dashboard_state
        self.selection_mode = SelectionMode.SINGLE
        self.show_help_on_start = True
        
        # Query categories and examples
        self.query_categories = {
            "Innovation & Creativity": [
                "How can we revolutionize customer experience in digital banking?",
                "What are breakthrough approaches to sustainable urban transportation?",
                "How might we reimagine remote work collaboration for maximum creativity?",
                "What innovative solutions could address food waste in restaurants?"
            ],
            "Problem Solving": [
                "How can small businesses improve cash flow during economic uncertainty?",
                "What strategies can reduce employee burnout in healthcare?",
                "How might we improve online learning engagement for students?",
                "What approaches could reduce plastic waste in packaging?"
            ],
            "Strategic Planning": [
                "What market opportunities exist for AI-powered education tools?",
                "How should companies prepare for the future of work?",
                "What competitive advantages can emerge from sustainability initiatives?",
                "How can organizations build resilience against supply chain disruptions?"
            ],
            "Technology & Innovation": [
                "How can blockchain technology improve supply chain transparency?",
                "What are the ethical implications of AI in hiring decisions?",
                "How might quantum computing transform financial modeling?",
                "What opportunities exist for IoT in smart city development?"
            ],
            "Learning & Development": [
                "How can we design effective microlearning programs for busy professionals?",
                "What pedagogical approaches best support adult learners?",
                "How might we personalize learning experiences at scale?",
                "What role should AI play in educational assessment?"
            ]
        }
    
    def load_items(self) -> List[ParameterItem]:
        """Load example queries as selectable items"""
        items = []
        
        for category, queries in self.query_categories.items():
            for i, query in enumerate(queries, 1):
                item = ParameterItem(
                    id=f"{category.lower().replace(' ', '_')}_{i}",
                    name=query,
                    description=f"Example {category.lower()} query",
                    metadata={
                        "category": category,
                        "length": len(query),
                        "complexity": self._assess_query_complexity(query),
                        "estimated_combinations": self._estimate_combinations(query)
                    }
                )
                items.append(item)
        
        return items
    
    def get_display_table(self) -> Table:
        """Create Rich table for displaying query examples"""
        table = Table(show_header=True, header_style="bold blue", show_lines=True)
        table.add_column("#", style="green", width=3)
        table.add_column("Category", style="cyan", min_width=15)
        table.add_column("Example Query", style="white", max_width=50)
        table.add_column("Complexity", style="yellow", width=10)
        table.add_column("Est. Combinations", style="magenta", width=12)
        
        for i, item in enumerate(self.items, 1):
            # Truncate long queries for table display
            display_query = item.name[:45] + "..." if len(item.name) > 45 else item.name
            
            table.add_row(
                str(i),
                item.metadata["category"],
                display_query,
                item.metadata["complexity"].title(),
                str(item.metadata["estimated_combinations"])
            )
        
        return table
    
    def validate_selection(self, user_input: str) -> bool:
        """Validate query input"""
        if not user_input or len(user_input.strip()) < 5:
            self.console.print("[red]Query must be at least 5 characters long[/red]")
            return False
        
        if len(user_input) > 500:
            self.console.print("[red]Query too long. Please keep under 500 characters[/red]")
            return False
        
        return True
    
    def apply_selection(self, selection: Any) -> None:
        """Apply query selection to dashboard state"""
        if isinstance(selection, int):
            # User selected an example query
            selected_item = self.items[selection - 1]
            query_text = selected_item.name
            self.dashboard_state.update_parameter("query", query_text)
            self.console.print(f"[green]✓ Query set from example[/green]")
        else:
            # User entered custom query
            self.dashboard_state.update_parameter("query", selection)
            self.console.print(f"[green]✓ Custom query set[/green]")
    
    def edit_parameter(self) -> None:
        """Enhanced query editing with custom input option"""
        try:
            self.items = self.load_items()
            
            self.console.print(f"\n[bold cyan]Configure Query:[/bold cyan]")
            self.console.print("You can either select an example query or enter your own custom query.")
            
            # Show current query
            current_query = self.dashboard_state.parameters.get("query", {}).get("value", "")
            if current_query:
                self.console.print(f"\n[bold green]Current Query:[/bold green]")
                query_panel = Panel(current_query, border_style="green", padding=(0, 1))
                self.console.print(query_panel)
            
            # Show options
            self.console.print("\n[bold yellow]Options:[/bold yellow]")
            self.console.print("• [cyan]1[/cyan] - Enter custom query")
            self.console.print("• [cyan]2[/cyan] - Browse example queries")
            self.console.print("• [cyan]done[/cyan] - Keep current query")
            
            while True:
                choice = Prompt.ask("Choose option", choices=["1", "2", "done"], default="done").strip()
                
                if choice == "done":
                    return
                elif choice == "1":
                    self._handle_custom_query_input()
                    break
                elif choice == "2":
                    self._handle_example_query_selection()
                    break
        
        except Exception as e:
            self.console.print(f"[red]Error editing query: {e}[/red]")
    
    def _handle_custom_query_input(self) -> None:
        """Handle custom query input with validation and feedback"""
        self.console.print("\n[bold cyan]Enter Custom Query:[/bold cyan]")
        self.console.print("[dim]Tip: Be specific and clear about what you want to explore[/dim]")
        
        while True:
            current_query = self.dashboard_state.parameters.get("query", {}).get("value", "")
            query = Prompt.ask("Your query", default=current_query).strip()
            
            if query.lower() == "done":
                return
            
            if self.validate_selection(query):
                # Show query analysis
                self._show_query_analysis(query)
                
                # Confirm
                if Prompt.ask("Use this query?", choices=["y", "n"], default="y") == "y":
                    self.apply_selection(query)
                    break
                else:
                    continue
            else:
                self.console.print("[dim]Please try again or type 'done' to cancel[/dim]")
    
    def _handle_example_query_selection(self) -> None:
        """Handle example query selection"""
        # Display examples table
        table = self.get_display_table()
        self.console.print(table)
        
        # Show selection help
        self.console.print("\n[bold yellow]Selection Options:[/bold yellow]")
        self.console.print("• [cyan]Number[/cyan] (e.g., '5') - Select example query")
        self.console.print("• [cyan]Special commands:[/cyan] 'preview <number>', 'help', 'done'")
        
        while True:
            user_input = Prompt.ask("Select example query", default="done").strip()
            
            if user_input.lower() == "done":
                return
            
            # Handle special commands
            if self._handle_special_commands(user_input):
                continue
            
            # Try to select example
            try:
                num = int(user_input)
                if 1 <= num <= len(self.items):
                    selected_item = self.items[num - 1]
                    
                    # Show query preview
                    self._show_query_preview(selected_item, num)
                    
                    # Confirm selection
                    if Prompt.ask("Use this query?", choices=["y", "n"], default="y") == "y":
                        self.apply_selection(num)
                        break
                else:
                    self.console.print(f"[red]Invalid number. Use 1-{len(self.items)}[/red]")
            except ValueError:
                self.console.print("[red]Please enter a valid number[/red]")
    
    def _show_query_analysis(self, query: str) -> None:
        """Show analysis of a query"""
        complexity = self._assess_query_complexity(query)
        estimated_combinations = self._estimate_combinations(query)
        
        analysis_content = [
            f"[yellow]Query Length:[/yellow] {len(query)} characters",
            f"[yellow]Complexity:[/yellow] {complexity.title()}",
            f"[yellow]Estimated Combinations:[/yellow] {estimated_combinations}",
            f"[yellow]Estimated Cost:[/yellow] ${estimated_combinations * 0.08:.2f}",
            "",
            "[yellow]Query Preview:[/yellow]",
            query
        ]
        
        analysis_panel = Panel(
            "\n".join(analysis_content),
            title="Query Analysis",
            border_style="cyan"
        )
        self.console.print(analysis_panel)
    
    def _show_query_preview(self, item: ParameterItem, number: int) -> None:
        """Show preview of a query example"""
        content = [
            f"[bold cyan]{item.metadata['category']}[/bold cyan]",
            "",
            f"[yellow]Query:[/yellow]",
            item.name,
            "",
            f"[yellow]Complexity:[/yellow] {item.metadata['complexity'].title()}",
            f"[yellow]Estimated Combinations:[/yellow] {item.metadata['estimated_combinations']}",
            f"[yellow]Estimated Cost:[/yellow] ${item.metadata['estimated_combinations'] * 0.08:.2f}",
        ]
        
        preview_panel = Panel(
            "\n".join(content),
            title=f"Query Example #{number} Preview",
            border_style="cyan"
        )
        self.console.print(preview_panel)
    
    def _assess_query_complexity(self, query: str) -> str:
        """Assess query complexity based on length and content"""
        if len(query) < 50:
            return "simple"
        elif len(query) < 150:
            return "moderate"
        else:
            return "complex"
    
    def _estimate_combinations(self, query: str) -> int:
        """Estimate number of combinations for a query"""
        # Simple estimation based on query characteristics
        base_combinations = 12  # Default dashboard setting
        
        if "innovative" in query.lower() or "creative" in query.lower():
            return base_combinations + 8
        elif "strategic" in query.lower() or "planning" in query.lower():
            return base_combinations + 4
        else:
            return base_combinations
    
    def _display_parameter_specific_help(self) -> None:
        """Display query-specific help"""
        help_content = [
            "[bold yellow]Query Best Practices:[/bold yellow]",
            "",
            "• Be specific about your domain or context",
            "• Use action-oriented language ('How can we...', 'What strategies...')",
            "• Include key constraints or requirements",
            "• Avoid overly broad or vague questions",
            "",
            "[bold yellow]Examples of Good Queries:[/bold yellow]",
            "• 'How can we reduce customer churn in SaaS products?'",
            "• 'What innovative approaches exist for remote team collaboration?'",
            "• 'How might we improve the onboarding experience for new employees?'"
        ]
        
        help_panel = Panel(
            "\n".join(help_content),
            title="Query Help",
            border_style="yellow"
        )
        self.console.print(help_panel)