"""
Domain Parameter Editor for ISEE Configuration Dashboard

This module provides an enhanced parameter editor for the domain parameter,
following the standardized framework patterns established in Phase 1.

Features:
- Visual domain categories display
- Category-based filtering
- Custom domain input with validation
- Domain examples and descriptions
- Preview and comparison capabilities
"""

from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from enhanced_parameter_editor import EnhancedParameterEditor, ParameterItem, SelectionMode


class DomainParameterEditor(EnhancedParameterEditor):
    """Enhanced editor for domain parameter with category filtering and examples"""
    
    def __init__(self, console: Console, dashboard, **kwargs):
        domain_param = dashboard.state.parameters.get("domain")
        current_domain = domain_param.value if domain_param else ""
        super().__init__(console, "domain", current_domain)
        self.dashboard = dashboard
        self.selection_mode = SelectionMode.HYBRID  # Both category selection and custom input
        self.show_help_on_start = True
        
        # Domain categories for organization
        self.domain_categories = {
            "innovation": {
                "name": "Innovation & Technology",
                "color": "bright_blue",
                "icon": "🚀",
                "domains": [
                    "Technology Innovation", "Product Development", "Digital Transformation",
                    "Artificial Intelligence", "Biotechnology", "Renewable Energy"
                ]
            },
            "business": {
                "name": "Business & Strategy", 
                "color": "green",
                "icon": "💼",
                "domains": [
                    "Business Strategy", "Market Analysis", "Financial Planning",
                    "Operations Management", "Supply Chain", "Customer Experience"
                ]
            },
            "education": {
                "name": "Education & Learning",
                "color": "yellow",
                "icon": "📚",
                "domains": [
                    "Curriculum Design", "Educational Technology", "Learning Assessment",
                    "Student Engagement", "Teacher Training", "Educational Research"
                ]
            },
            "health": {
                "name": "Healthcare & Wellness",
                "color": "red",
                "icon": "🏥",
                "domains": [
                    "Public Health", "Medical Research", "Healthcare Policy",
                    "Mental Health", "Nutrition", "Preventive Care"
                ]
            },
            "sustainability": {
                "name": "Sustainability & Environment",
                "color": "bright_green",
                "icon": "🌱",
                "domains": [
                    "Environmental Policy", "Climate Change", "Sustainable Development",
                    "Circular Economy", "Green Technology", "Conservation"
                ]
            },
            "social": {
                "name": "Social & Community",
                "color": "magenta",
                "icon": "🤝",
                "domains": [
                    "Social Impact", "Community Development", "Urban Planning",
                    "Public Policy", "Social Justice", "Cultural Studies"
                ]
            },
            "research": {
                "name": "Research & Analysis",
                "color": "cyan",
                "icon": "🔬",
                "domains": [
                    "Scientific Research", "Data Analysis", "Market Research",
                    "Academic Writing", "Literature Review", "Experimental Design"
                ]
            },
            "creative": {
                "name": "Creative & Design",
                "color": "bright_magenta",
                "icon": "🎨",
                "domains": [
                    "Creative Writing", "Design Thinking", "Content Creation",
                    "Brand Development", "User Experience", "Digital Media"
                ]
            }
        }
    
    def load_items(self) -> List[ParameterItem]:
        """Load domain categories and examples as selectable items"""
        items = []
        
        # Add predefined domain categories
        for category_id, category_info in self.domain_categories.items():
            for i, domain_name in enumerate(category_info["domains"]):
                item_id = f"{category_id}_{i}"
                description = f"From {category_info['name']} category"
                metadata = {
                    "category": category_info["name"],
                    "category_color": category_info["color"],
                    "category_icon": category_info["icon"],
                    "complexity": "medium",
                    "scope": "broad",
                    "applications": "research, innovation, analysis"
                }
                
                items.append(ParameterItem(
                    id=item_id,
                    name=domain_name,
                    description=description,
                    metadata=metadata
                ))
        
        # Load external domain files if available
        items.extend(self._load_external_domains())
        
        return items
    
    def _load_external_domains(self) -> List[ParameterItem]:
        """Load domains from external JSON files"""
        external_items = []
        
        # Try to load tech writing domains
        try:
            import json
            import os
            
            tech_writing_file = "tech_writing_domains.json"
            if os.path.exists(tech_writing_file):
                with open(tech_writing_file, 'r') as f:
                    tech_data = json.load(f)
                    for domain_data in tech_data.get("domains", []):
                        external_items.append(ParameterItem(
                            id=f"tech_{domain_data.get('id', 'unknown')}",
                            name=domain_data.get("name", "Unknown"),
                            description="From Technical Writing collection",
                            metadata={
                                "category": "Technical Writing",
                                "category_color": "blue",
                                "category_icon": "📝",
                                "source": "tech_writing_domains.json",
                                "complexity": "advanced",
                                "scope": "specialized"
                            }
                        ))
        except Exception:
            pass  # Silently handle missing files
        
        # Try to load learning design domains
        try:
            learning_design_file = "learning_design_domains.json"
            if os.path.exists(learning_design_file):
                with open(learning_design_file, 'r') as f:
                    learning_data = json.load(f)
                    for domain_data in learning_data.get("domains", []):
                        external_items.append(ParameterItem(
                            id=f"learning_{domain_data.get('id', 'unknown')}",
                            name=domain_data.get("name", "Unknown"),
                            description="From Learning Design collection",
                            metadata={
                                "category": "Learning Design",
                                "category_color": "bright_yellow",
                                "category_icon": "🎓",
                                "source": "learning_design_domains.json",
                                "complexity": "advanced",
                                "scope": "specialized"
                            }
                        ))
        except Exception:
            pass  # Silently handle missing files
        
        return external_items
    
    def get_display_table(self) -> Table:
        """Create Rich table displaying domains organized by category"""
        table = Table(
            title="🌐 Available Domain Categories",
            show_header=True,
            header_style="bold white",
            show_lines=True,
            expand=False
        )
        
        table.add_column("#", style="green", width=3)
        table.add_column("Domain", style="bold white", min_width=25)
        table.add_column("Category", style="yellow", min_width=20)
        table.add_column("Scope", style="cyan", width=12)
        table.add_column("Applications", style="dim", max_width=25)
        
        # Group items by category for better organization
        current_category = None
        for i, item in enumerate(self.items, 1):
            category_name = item.metadata.get("category", "Other")
            category_color = item.metadata.get("category_color", "white")
            category_icon = item.metadata.get("category_icon", "📁")
            
            # Add category separator
            if category_name != current_category:
                if current_category is not None:  # Don't add separator before first category
                    table.add_row("", "", "", "", "", style="dim")
                current_category = category_name
            
            scope = item.metadata.get("scope", "medium")
            applications = item.metadata.get("applications", "general use")
            
            # Truncate applications if too long
            if len(applications) > 25:
                applications = applications[:22] + "..."
            
            table.add_row(
                str(i),
                item.name,
                f"[{category_color}]{category_icon} {category_name}[/{category_color}]",
                scope.title(),
                applications
            )
        
        return table
    
    def validate_selection(self, user_input: str) -> bool:
        """Validate domain selection or custom input"""
        if not user_input or user_input.strip() == "":
            return False
        
        # Custom domain input is always valid (let users be creative)
        if not user_input.isdigit() and "," not in user_input and "-" not in user_input:
            return True
        
        # Validate numeric selection using parent method
        try:
            if user_input.isdigit():
                num = int(user_input)
                return 1 <= num <= len(self.items)
            else:
                # Validate selection syntax
                selected_numbers = self._parse_number_selection(user_input, len(self.items))
                return len(selected_numbers) > 0
        except ValueError:
            return False
    
    def apply_selection(self, selection) -> None:
        """Apply domain selection to dashboard state"""
        if isinstance(selection, int):
            # Single domain selection
            if 1 <= selection <= len(self.items):
                selected_domain = self.items[selection - 1].name
                self.dashboard.update_parameter("domain", selected_domain)
                self.current_value = selected_domain
        elif isinstance(selection, list):
            # Multiple domain selection - use first one for now
            if selection and 1 <= selection[0] <= len(self.items):
                selected_domain = self.items[selection[0] - 1].name
                self.dashboard.update_parameter("domain", selected_domain)
                self.current_value = selected_domain
        elif isinstance(selection, str):
            # Custom domain input
            self.dashboard.update_parameter("domain", selection)
            self.current_value = selection
    
    def _process_selection_input(self, user_input: str) -> bool:
        """Override to handle custom domain input"""
        # Check if input is a custom domain (not numeric selection)
        if not user_input.isdigit() and "," not in user_input and "-" not in user_input:
            # Custom domain input
            if self.validate_selection(user_input):
                self.apply_selection(user_input)
                self.console.print(f"[green]✓ Set custom domain: {user_input}[/green]")
                return True
            else:
                self.console.print("[red]Invalid domain name[/red]")
                return False
        
        # Use parent method for numeric selections
        return super()._process_selection_input(user_input)
    
    def _display_parameter_specific_help(self) -> None:
        """Display domain-specific help information"""
        self.console.print("\n[bold cyan]Domain Selection Help:[/bold cyan]")
        self.console.print("• [green]Select by number[/green]: Choose from categorized domains above")
        self.console.print("• [green]Custom domain[/green]: Type any domain name for specialized focus")
        self.console.print("• [green]Examples[/green]: 'Healthcare Innovation', 'Urban Sustainability', 'Educational Technology'")
        self.console.print("")
        self.console.print("[bold yellow]Domain Impact:[/bold yellow]")
        self.console.print("• Domains provide context for query generation and idea evaluation")
        self.console.print("• Specific domains yield more targeted and relevant results")
        self.console.print("• Broad domains allow for more diverse perspective exploration")
        self.console.print("")
        self.console.print("[bold white]Category Guide:[/bold white]")
        
        # Show category quick reference
        for category_info in self.domain_categories.values():
            icon = category_info["icon"]
            name = category_info["name"]
            color = category_info["color"]
            self.console.print(f"• [{color}]{icon} {name}[/{color}]: {len(category_info['domains'])} domains")
    
    def _show_item_preview(self, item: ParameterItem, number: int) -> None:
        """Enhanced preview showing domain details and examples"""
        category_icon = item.metadata.get("category_icon", "📁")
        category_name = item.metadata.get("category", "General")
        category_color = item.metadata.get("category_color", "white")
        
        content = [
            f"[bold cyan]{item.name}[/bold cyan]",
            "",
            f"[yellow]Category:[/yellow] [{category_color}]{category_icon} {category_name}[/{category_color}]",
            f"[yellow]Description:[/yellow] {item.description}",
            f"[yellow]Scope:[/yellow] {item.metadata.get('scope', 'medium').title()}",
            f"[yellow]Complexity:[/yellow] {item.metadata.get('complexity', 'medium').title()}",
        ]
        
        # Add example queries for this domain
        content.extend([
            "",
            "[bold green]Example Query Applications:[/bold green]",
            f"• 'How can we improve {item.name.lower()} through innovative approaches?'",
            f"• 'What are emerging trends in {item.name.lower()}?'",
            f"• 'Identify key challenges and solutions in {item.name.lower()}'",
        ])
        
        # Add source information if available
        source = item.metadata.get("source")
        if source:
            content.extend([
                "",
                f"[dim]Source: {source}[/dim]"
            ])
        
        preview_panel = Panel(
            "\n".join(content),
            title=f"Domain #{number} Preview",
            border_style="cyan"
        )
        self.console.print(preview_panel)
    
    def _show_item_comparison(self, item1: ParameterItem, item2: ParameterItem, num1: int, num2: int) -> None:
        """Enhanced comparison showing domain characteristics"""
        compare_table = Table(show_header=True, header_style="bold yellow")
        compare_table.add_column("Characteristic", style="cyan", min_width=15)
        compare_table.add_column(f"#{num1} {item1.name}", style="green", max_width=30)
        compare_table.add_column(f"#{num2} {item2.name}", style="blue", max_width=30)
        
        compare_table.add_row("Domain Name", item1.name, item2.name)
        compare_table.add_row("Category",
                            f"{item1.metadata.get('category_icon', '📁')} {item1.metadata.get('category', 'General')}",
                            f"{item2.metadata.get('category_icon', '📁')} {item2.metadata.get('category', 'General')}")
        compare_table.add_row("Scope", 
                            item1.metadata.get('scope', 'medium').title(),
                            item2.metadata.get('scope', 'medium').title())
        compare_table.add_row("Complexity",
                            item1.metadata.get('complexity', 'medium').title(),
                            item2.metadata.get('complexity', 'medium').title())
        compare_table.add_row("Applications",
                            item1.metadata.get('applications', 'general')[:25] + "...",
                            item2.metadata.get('applications', 'general')[:25] + "...")
        
        # Add recommendations
        content = [
            compare_table,
            "",
            "[bold green]Selection Recommendations:[/bold green]",
            f"• Choose [green]{item1.name}[/green] for {item1.metadata.get('scope', 'medium')} scope {item1.metadata.get('complexity', 'medium')} complexity work",
            f"• Choose [blue]{item2.name}[/blue] for {item2.metadata.get('scope', 'medium')} scope {item2.metadata.get('complexity', 'medium')} complexity work"
        ]
        
        comparison_panel = Panel(
            "\n".join([str(compare_table), 
                      "\n[bold green]Selection Recommendations:[/bold green]",
                      f"• Choose [green]{item1.name}[/green] for {item1.metadata.get('scope', 'medium')} scope work",
                      f"• Choose [blue]{item2.name}[/blue] for {item2.metadata.get('scope', 'medium')} scope work"]),
            title="Domain Comparison",
            border_style="yellow"
        )
        self.console.print(comparison_panel)
    
    def edit_parameter(self) -> None:
        """Enhanced edit with category filtering option"""
        try:
            self.items = self.load_items()
            if not self.items:
                self.console.print(f"[red]No domains available for selection[/red]")
                return
            
            # Show category overview first
            self._show_category_overview()
            
            # Then show the full interface
            self._display_parameter_interface()
            self._handle_user_interaction()
            
        except Exception as e:
            self.console.print(f"[red]Error editing domain: {e}[/red]")
    
    def _show_category_overview(self) -> None:
        """Show a compact overview of domain categories"""
        self.console.print("\n[bold white]📁 Domain Categories Overview:[/bold white]")
        
        overview_table = Table(show_header=True, header_style="bold blue", show_lines=False)
        overview_table.add_column("Category", style="cyan", min_width=25)
        overview_table.add_column("Domains", style="white", width=8)
        overview_table.add_column("Focus", style="yellow", max_width=30)
        
        for category_info in self.domain_categories.values():
            icon = category_info["icon"]
            name = category_info["name"]
            color = category_info["color"]
            count = len(category_info["domains"])
            
            # Create focus description
            if "Innovation" in name:
                focus = "Future-oriented, technology-driven"
            elif "Business" in name:
                focus = "Strategic, market-focused"
            elif "Education" in name:
                focus = "Learning-centered, pedagogical"
            elif "Healthcare" in name:
                focus = "Health outcomes, medical research"
            elif "Sustainability" in name:
                focus = "Environmental, long-term impact"
            elif "Social" in name:
                focus = "Community-centered, societal"
            elif "Research" in name:
                focus = "Data-driven, analytical"
            elif "Creative" in name:
                focus = "Design-thinking, innovative"
            else:
                focus = "General purpose"
            
            overview_table.add_row(
                f"[{color}]{icon} {name}[/{color}]",
                str(count),
                focus
            )
        
        self.console.print(overview_table)
        self.console.print("[dim]💡 You can also enter any custom domain name for specialized focus[/dim]")