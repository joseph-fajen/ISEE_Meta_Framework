"""
Enhanced Parameter Editor Framework

This module provides a reusable framework for creating rich, interactive parameter editors
in the ISEE Configuration Dashboard. It extracts successful patterns from the instruction
template enhancement to standardize all parameter editing experiences.

Key Features:
- Rich visual displays with tables and panels
- Advanced selection syntax (ranges, lists, specific selections)
- Special commands (preview, compare, help, done)
- Real-time validation and feedback
- Consistent user experience patterns
"""

from typing import List, Dict, Any, Optional, Union, Callable
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from abc import ABC, abstractmethod


class ParameterItem:
    """Represents a single selectable item in a parameter editor"""
    
    def __init__(self, id: str, name: str, description: str = "", metadata: Dict[str, Any] = None):
        self.id = id
        self.name = name
        self.description = description
        self.metadata = metadata or {}


class SelectionMode:
    """Defines the types of selection modes supported"""
    SINGLE = "single"           # Single item selection
    MULTIPLE = "multiple"       # Multiple item selection with syntax support
    COUNT_BASED = "count"       # Numeric count (e.g., "use first 5")
    HYBRID = "hybrid"           # Both count-based and specific selection


class EnhancedParameterEditor(ABC):
    """
    Abstract base class for enhanced parameter editors.
    
    Provides standardized patterns for:
    - Rich visual displays
    - Advanced selection syntax
    - Special command handling
    - Real-time validation
    """
    
    def __init__(self, console: Console, parameter_name: str, current_value: Any = None):
        self.console = console
        self.parameter_name = parameter_name
        self.current_value = current_value
        self.items: List[ParameterItem] = []
        self.selection_mode = SelectionMode.MULTIPLE
        self.show_help_on_start = True
        
    @abstractmethod
    def load_items(self) -> List[ParameterItem]:
        """Load the available items for this parameter"""
        pass
    
    @abstractmethod
    def get_display_table(self) -> Table:
        """Create the Rich table for displaying items"""
        pass
    
    @abstractmethod
    def validate_selection(self, user_input: str) -> bool:
        """Validate user input"""
        pass
    
    @abstractmethod
    def apply_selection(self, selection: Union[int, List[int], str]) -> None:
        """Apply the validated selection to the dashboard state"""
        pass
    
    def edit_parameter(self) -> None:
        """Main entry point for parameter editing"""
        try:
            self.items = self.load_items()
            if not self.items:
                self.console.print(f"[red]No items available for {self.parameter_name}[/red]")
                return
            
            self._display_parameter_interface()
            self._handle_user_interaction()
            
        except Exception as e:
            self.console.print(f"[red]Error editing {self.parameter_name}: {e}[/red]")
    
    def _display_parameter_interface(self) -> None:
        """Display the parameter editing interface"""
        self.console.print(f"\n[bold cyan]Configure {self.parameter_name.title()}:[/bold cyan]")
        
        # Display items table
        table = self.get_display_table()
        self.console.print(table)
        
        # Show current selection
        self._display_current_selection()
        
        # Show help if enabled
        if self.show_help_on_start:
            self._display_selection_help()
    
    def _display_current_selection(self) -> None:
        """Display the current parameter selection"""
        if self.current_value:
            self.console.print(f"\n[bold green]Current Selection:[/bold green] {self.current_value}")
        else:
            self.console.print(f"\n[bold green]Current Selection:[/bold green] [dim]None[/dim]")
    
    def _display_selection_help(self) -> None:
        """Display selection help based on selection mode"""
        self.console.print("\n[bold yellow]Selection Options:[/bold yellow]")
        
        if self.selection_mode in [SelectionMode.MULTIPLE, SelectionMode.HYBRID]:
            self.console.print("• [cyan]Specific[/cyan] (e.g., '1,3,5' or '2-4') - Select specific items")
        
        if self.selection_mode in [SelectionMode.COUNT_BASED, SelectionMode.HYBRID]:
            self.console.print("• [cyan]Count[/cyan] (e.g., '5') - Use first N items")
        
        if self.selection_mode == SelectionMode.SINGLE:
            self.console.print("• [cyan]Number[/cyan] (e.g., '3') - Select single item")
        
        self.console.print("• [cyan]Special commands:[/cyan] 'preview <number>', 'compare <num1> <num2>', 'help', 'done'")
    
    def _handle_user_interaction(self) -> None:
        """Handle user input and special commands"""
        while True:
            default_value = str(self.current_value) if self.current_value else ""
            user_input = Prompt.ask(f"{self.parameter_name.title()} selection", default=default_value).strip()
            
            if user_input.lower() == "done":
                return  # Exit without updating
            
            # Handle special commands
            if self._handle_special_commands(user_input):
                continue
            
            # Handle selection input
            if self._process_selection_input(user_input):
                break
    
    def _handle_special_commands(self, user_input: str) -> bool:
        """Handle special commands like preview, compare, help"""
        lower_input = user_input.lower()
        
        if lower_input.startswith("preview "):
            self._handle_preview_command(user_input)
            return True
        elif lower_input.startswith("compare "):
            self._handle_compare_command(user_input)
            return True
        elif lower_input == "help":
            self._handle_help_command()
            return True
        
        return False
    
    def _handle_preview_command(self, user_input: str) -> None:
        """Handle preview command"""
        try:
            parts = user_input.split()
            if len(parts) >= 2:
                num = int(parts[1])
                if 1 <= num <= len(self.items):
                    item = self.items[num - 1]
                    self._show_item_preview(item, num)
                else:
                    self.console.print(f"[red]Invalid number. Use 1-{len(self.items)}[/red]")
            else:
                self.console.print("[red]Usage: preview <number>[/red]")
        except (ValueError, IndexError):
            self.console.print("[red]Invalid command format. Use 'preview <number>'[/red]")
    
    def _handle_compare_command(self, user_input: str) -> None:
        """Handle compare command"""
        try:
            parts = user_input.split()
            if len(parts) >= 3:
                num1, num2 = int(parts[1]), int(parts[2])
                if 1 <= num1 <= len(self.items) and 1 <= num2 <= len(self.items):
                    item1, item2 = self.items[num1 - 1], self.items[num2 - 1]
                    self._show_item_comparison(item1, item2, num1, num2)
                else:
                    self.console.print(f"[red]Invalid numbers. Use 1-{len(self.items)}[/red]")
            else:
                self.console.print("[red]Usage: compare <num1> <num2>[/red]")
        except (ValueError, IndexError):
            self.console.print("[red]Invalid command format. Use 'compare <num1> <num2>'[/red]")
    
    def _handle_help_command(self) -> None:
        """Handle help command"""
        self._display_selection_help()
        self._display_parameter_specific_help()
    
    def _show_item_preview(self, item: ParameterItem, number: int) -> None:
        """Show preview of a specific item"""
        content = [
            f"[bold cyan]{item.name}[/bold cyan]",
            "",
            f"[yellow]Description:[/yellow] {item.description or 'No description available'}",
        ]
        
        # Add metadata if available
        if item.metadata:
            content.append("")
            for key, value in item.metadata.items():
                content.append(f"[yellow]{key.title()}:[/yellow] {value}")
        
        preview_panel = Panel(
            "\n".join(content),
            title=f"{self.parameter_name.title()} #{number} Preview",
            border_style="cyan"
        )
        self.console.print(preview_panel)
    
    def _show_item_comparison(self, item1: ParameterItem, item2: ParameterItem, num1: int, num2: int) -> None:
        """Show comparison between two items"""
        compare_table = Table(show_header=True, header_style="bold yellow")
        compare_table.add_column("Aspect", style="cyan", min_width=15)
        compare_table.add_column(f"#{num1} {item1.name}", style="green", max_width=35)
        compare_table.add_column(f"#{num2} {item2.name}", style="blue", max_width=35)
        
        compare_table.add_row("Name", item1.name, item2.name)
        compare_table.add_row("Description", 
                            item1.description[:50] + "..." if len(item1.description or "") > 50 else item1.description or "N/A",
                            item2.description[:50] + "..." if len(item2.description or "") > 50 else item2.description or "N/A")
        
        # Add metadata comparisons
        all_keys = set(item1.metadata.keys()) | set(item2.metadata.keys())
        for key in sorted(all_keys):
            val1 = item1.metadata.get(key, "N/A")
            val2 = item2.metadata.get(key, "N/A")
            compare_table.add_row(key.title(), str(val1), str(val2))
        
        self.console.print(Panel(compare_table, title=f"{self.parameter_name.title()} Comparison", border_style="yellow"))
    
    def _display_parameter_specific_help(self) -> None:
        """Override in subclasses for parameter-specific help"""
        pass
    
    def _process_selection_input(self, user_input: str) -> bool:
        """Process selection input based on selection mode"""
        try:
            if self.selection_mode == SelectionMode.SINGLE:
                return self._process_single_selection(user_input)
            elif self.selection_mode == SelectionMode.COUNT_BASED:
                return self._process_count_selection(user_input)
            elif self.selection_mode == SelectionMode.MULTIPLE:
                return self._process_multiple_selection(user_input)
            elif self.selection_mode == SelectionMode.HYBRID:
                return self._process_hybrid_selection(user_input)
        except ValueError as e:
            self.console.print(f"[red]{e}[/red]")
            return False
        
        return False
    
    def _process_single_selection(self, user_input: str) -> bool:
        """Process single item selection"""
        try:
            num = int(user_input)
            if 1 <= num <= len(self.items):
                self.apply_selection(num)
                self.console.print(f"[green]✓ Selected: {self.items[num-1].name}[/green]")
                return True
            else:
                self.console.print(f"[red]Invalid number. Use 1-{len(self.items)}[/red]")
        except ValueError:
            self.console.print("[red]Please enter a valid number[/red]")
        return False
    
    def _process_count_selection(self, user_input: str) -> bool:
        """Process count-based selection"""
        try:
            count = int(user_input)
            if count < 1:
                self.console.print("[red]Please enter a number greater than 0[/red]")
                return False
            elif count > len(self.items):
                self.console.print(f"[red]Maximum {len(self.items)} items available[/red]")
                return False
            
            self.apply_selection(count)
            self.console.print(f"[green]✓ Set to use first {count} items[/green]")
            return True
        except ValueError:
            self.console.print("[red]Please enter a valid number[/red]")
        return False
    
    def _process_multiple_selection(self, user_input: str) -> bool:
        """Process multiple item selection with advanced syntax"""
        try:
            selected_numbers = self._parse_number_selection(user_input, len(self.items))
            if selected_numbers:
                self.apply_selection(selected_numbers)
                self.console.print(f"\n[green]✓ Selected {len(selected_numbers)} items:[/green]")
                for num in selected_numbers:
                    self.console.print(f"  • [cyan]{self.items[num-1].name}[/cyan]")
                return True
        except ValueError as e:
            self.console.print(f"[red]{e}[/red]")
            self.console.print("[dim]Examples: '1,3,5' (specific), '2-4' (range)[/dim]")
        return False
    
    def _process_hybrid_selection(self, user_input: str) -> bool:
        """Process hybrid selection (count or specific)"""
        # Try count-based first
        try:
            count = int(user_input)
            return self._process_count_selection(user_input)
        except ValueError:
            # Try multiple selection
            return self._process_multiple_selection(user_input)
    
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
                    raise ValueError(f"Invalid number format: {part}")
        
        # Remove duplicates and sort
        return sorted(list(set(numbers)))


class ParameterEditorFactory:
    """Factory for creating enhanced parameter editors"""
    
    @staticmethod
    def create_editor(parameter_name: str, console: Console, dashboard_state, **kwargs) -> EnhancedParameterEditor:
        """Create an appropriate editor for the given parameter"""
        
        # Import specific editors here to avoid circular imports
        if parameter_name == "query":
            from .query_parameter_editor import QueryParameterEditor
            return QueryParameterEditor(console, dashboard_state, **kwargs)
        elif parameter_name == "variations":
            from .variations_parameter_editor import VariationsParameterEditor
            return VariationsParameterEditor(console, dashboard_state, **kwargs)
        elif parameter_name == "domain":
            from .domain_parameter_editor import DomainParameterEditor
            return DomainParameterEditor(console, dashboard_state, **kwargs)
        elif parameter_name == "instruction_templates":
            # This already exists and works well
            return None  # Keep existing implementation
        else:
            raise ValueError(f"No enhanced editor available for parameter: {parameter_name}")