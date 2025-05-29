"""
Cognitive Framework Visualizer for ISEE Command Wizard

This module provides visualization capabilities for cognitive frameworks to help users
understand the diversity of AI thinking approaches available in the ISEE system.

Part of UX Enhancement Roadmap - Step 3.1: Cognitive Frameworks Visualization
"""

from typing import Dict, List, Optional, Tuple, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from instruction_templates import InstructionTemplate, TemplateLibrary, create_default_library


class CognitiveFrameworkVisualizer:
    """Visualizes cognitive frameworks with Rich components for enhanced user understanding."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize the visualizer.
        
        Args:
            console: Rich console instance. If None, creates a new one.
        """
        self.console = console or Console()
        self.template_library = create_default_library()
        
        # Framework icon mapping for visual identification
        self.framework_icons = {
            "ins_analytical": "🔍",
            "ins_creative": "💡", 
            "ins_critical": "⚖️",
            "ins_integrative": "🔗",
            "ins_pragmatic": "🔧",
            "ins_first_principles": "🧱",
            "ins_systems": "🌐",
            "ins_contrarian": "🔄",
            "ins_historical": "📚",
            "ins_futurist": "🚀"
        }
        
        # Framework complexity categorization for progressive disclosure
        self.complexity_levels = {
            "basic": ["ins_analytical", "ins_creative", "ins_pragmatic"],
            "advanced": ["ins_critical", "ins_integrative", "ins_systems", "ins_historical"],
            "expert": ["ins_first_principles", "ins_contrarian", "ins_futurist"]
        }
        
        # Example query demonstrations
        self.example_queries = {
            "ins_analytical": {
                "query": "How can we improve team productivity?",
                "approach": "Systematic analysis of productivity metrics, bottleneck identification, evidence-based solutions"
            },
            "ins_creative": {
                "query": "How can we improve team productivity?", 
                "approach": "Brainstorm unconventional workspace designs, gamification, radical flexibility experiments"
            },
            "ins_critical": {
                "query": "How can we improve team productivity?",
                "approach": "Challenge assumption that productivity needs improving, question measurement validity"
            },
            "ins_integrative": {
                "query": "How can we improve team productivity?",
                "approach": "Synthesize individual psychology, team dynamics, organizational culture, and technology factors"
            },
            "ins_pragmatic": {
                "query": "How can we improve team productivity?",
                "approach": "Focus on immediately implementable changes with clear ROI and minimal disruption"
            },
            "ins_first_principles": {
                "query": "How can we improve team productivity?",
                "approach": "Break down to fundamental: What is work? What creates value? Rebuild from basics"
            },
            "ins_systems": {
                "query": "How can we improve team productivity?",
                "approach": "Map interdependencies, feedback loops, emergent behaviors across the entire organizational system"
            },
            "ins_contrarian": {
                "query": "How can we improve team productivity?",
                "approach": "Question why productivity is the goal - maybe slow, thoughtful work creates more value"
            },
            "ins_historical": {
                "query": "How can we improve team productivity?",
                "approach": "Study productivity movements, industrial evolution, successful/failed organizational changes"
            },
            "ins_futurist": {
                "query": "How can we improve team productivity?",
                "approach": "Consider AI collaboration, remote work evolution, changing nature of knowledge work"
            }
        }
    
    def display_frameworks_overview(self, complexity_level: str = "all") -> None:
        """Display an overview of all cognitive frameworks.
        
        Args:
            complexity_level: Filter by complexity ("basic", "advanced", "expert", "all")
        """
        if complexity_level == "all":
            frameworks = self.template_library.list_templates()
        else:
            framework_ids = self.complexity_levels.get(complexity_level, [])
            frameworks = [self.template_library.get_template(fid) for fid in framework_ids]
        
        table = Table(
            title=f"🧠 Cognitive Frameworks ({complexity_level.title()} Level)" if complexity_level != "all" else "🧠 Cognitive Frameworks",
            show_header=True,
            header_style="bold cyan",
            border_style="cyan"
        )
        
        table.add_column("Icon", style="bold", width=4)
        table.add_column("Framework", style="bold blue", width=20)
        table.add_column("Cognitive Style", style="green", width=15)
        table.add_column("Strength", style="yellow", width=25)
        table.add_column("Best For", style="magenta", width=30)
        
        # Define "best for" descriptions
        best_for_map = {
            "ins_analytical": "Structured problem-solving, data-driven decisions",
            "ins_creative": "Innovation, brainstorming, novel solutions",
            "ins_critical": "Risk assessment, assumption testing",
            "ins_integrative": "Complex multi-factor problems",
            "ins_pragmatic": "Quick wins, resource-constrained scenarios",
            "ins_first_principles": "Fundamental breakthroughs, paradigm shifts",
            "ins_systems": "Organizational change, ecosystem thinking",
            "ins_contrarian": "Challenging status quo, finding blind spots",
            "ins_historical": "Learning from precedents, pattern recognition",
            "ins_futurist": "Strategic planning, anticipating trends"
        }
        
        for framework in frameworks:
            icon = self.framework_icons.get(framework.id, "🤔")
            cognitive_style = framework.metadata.get("cognitive_style", "Unknown")
            strength = framework.metadata.get("strength", "General analysis")
            best_for = best_for_map.get(framework.id, "Various applications")
            
            table.add_row(
                icon,
                framework.name.replace(" Framework", ""),
                cognitive_style.title(),
                strength.title(),
                best_for
            )
        
        self.console.print("\n")
        self.console.print(table)
        self.console.print("\n[dim]💡 Tip: Use 'preview <number>' to see examples, 'compare <num1> <num2>' to compare frameworks[/dim]\n")
    
    def display_framework_detail(self, framework_id: str) -> None:
        """Display detailed view of a specific framework.
        
        Args:
            framework_id: ID of the framework to display
        """
        try:
            framework = self.template_library.get_template(framework_id)
            example = self.example_queries.get(framework_id, {})
            
            icon = self.framework_icons.get(framework_id, "🤔")
            
            # Create the main panel content
            content = []
            
            # Framework description
            content.append(f"[bold cyan]Cognitive Style:[/bold cyan] {framework.metadata.get('cognitive_style', 'Unknown').title()}")
            content.append(f"[bold green]Core Strength:[/bold green] {framework.metadata.get('strength', 'General analysis').title()}")
            content.append("")
            
            # Framework template (simplified for display)
            template_preview = framework.template.replace("{domain}", "[bold]your domain[/bold]")
            content.append(f"[bold yellow]Approach:[/bold yellow]")
            content.append(f"[dim]{template_preview}[/dim]")
            content.append("")
            
            # Example demonstration
            if example:
                content.append(f"[bold magenta]Example Application:[/bold magenta]")
                content.append(f"[bold]Query:[/bold] {example['query']}")
                content.append(f"[bold]This framework would:[/bold] {example['approach']}")
            
            panel = Panel(
                "\n".join(content),
                title=f"{icon} {framework.name}",
                border_style="cyan",
                padding=(1, 2)
            )
            
            self.console.print("\n")
            self.console.print(panel)
            self.console.print()
            
        except KeyError:
            self.console.print(f"[red]❌ Framework '{framework_id}' not found[/red]")
    
    def display_framework_comparison(self, framework_id1: str, framework_id2: str) -> None:
        """Display side-by-side comparison of two frameworks.
        
        Args:
            framework_id1: ID of first framework
            framework_id2: ID of second framework
        """
        try:
            framework1 = self.template_library.get_template(framework_id1)
            framework2 = self.template_library.get_template(framework_id2)
            example1 = self.example_queries.get(framework_id1, {})
            example2 = self.example_queries.get(framework_id2, {})
            
            # Create comparison table
            table = Table(
                title="🔄 Framework Comparison",
                show_header=True,
                header_style="bold cyan",
                border_style="cyan"
            )
            
            table.add_column("Aspect", style="bold yellow", width=20)
            table.add_column(f"{self.framework_icons.get(framework_id1, '🤔')} {framework1.name}", style="blue", width=35)
            table.add_column(f"{self.framework_icons.get(framework_id2, '🤔')} {framework2.name}", style="green", width=35)
            
            # Add comparison rows
            table.add_row(
                "Cognitive Style",
                framework1.metadata.get('cognitive_style', 'Unknown').title(),
                framework2.metadata.get('cognitive_style', 'Unknown').title()
            )
            
            table.add_row(
                "Core Strength", 
                framework1.metadata.get('strength', 'General').title(),
                framework2.metadata.get('strength', 'General').title()
            )
            
            if example1 and example2:
                table.add_row(
                    "Example Approach",
                    example1.get('approach', 'No example available'),
                    example2.get('approach', 'No example available')
                )
            
            # When to use each
            when_to_use = {
                "ins_analytical": "Need structured, data-driven solutions",
                "ins_creative": "Seeking breakthrough innovations",
                "ins_critical": "Risk assessment required",
                "ins_integrative": "Multiple perspectives needed",
                "ins_pragmatic": "Quick, practical solutions needed",
                "ins_first_principles": "Fundamental rethinking required",
                "ins_systems": "Complex interconnections involved", 
                "ins_contrarian": "Challenging assumptions needed",
                "ins_historical": "Learning from past patterns",
                "ins_futurist": "Long-term strategic thinking"
            }
            
            table.add_row(
                "Best When",
                when_to_use.get(framework_id1, "Various situations"),
                when_to_use.get(framework_id2, "Various situations")
            )
            
            self.console.print("\n")
            self.console.print(table)
            self.console.print()
            
        except KeyError as e:
            self.console.print(f"[red]❌ Framework not found: {e}[/red]")
    
    def get_frameworks_for_complexity(self, complexity_level: str) -> List[Tuple[str, str]]:
        """Get framework options for a given complexity level.
        
        Args:
            complexity_level: "basic", "advanced", or "expert"
            
        Returns:
            List of (framework_id, display_name) tuples
        """
        framework_ids = self.complexity_levels.get(complexity_level, [])
        frameworks = []
        
        for fid in framework_ids:
            try:
                framework = self.template_library.get_template(fid)
                icon = self.framework_icons.get(fid, "🤔")
                display_name = f"{icon} {framework.name.replace(' Framework', '')}"
                frameworks.append((fid, display_name))
            except KeyError:
                continue
                
        return frameworks
    
    def display_cognitive_diversity_explanation(self) -> None:
        """Display explanation of cognitive diversity concept."""
        explanation = """
🧠 [bold cyan]Cognitive Diversity in AI Innovation[/bold cyan]

The ISEE framework leverages [bold]cognitive diversity[/bold] - the power of approaching the same problem 
from multiple thinking perspectives. Just as diverse teams generate better solutions, using 
diverse AI cognitive frameworks produces richer, more comprehensive results.

[bold yellow]How It Works:[/bold yellow]
• Each framework represents a different 'thinking style' for AI models
• The same query processed through multiple frameworks yields varied approaches
• ISEE combines these diverse perspectives to find novel solutions
• More cognitive diversity = broader exploration of possibility space

[bold green]Example:[/bold green] "Improve customer retention"
• [bold]Analytical:[/bold] Data analysis → identify churn predictors → targeted interventions
• [bold]Creative:[/bold] Gamification → loyalty adventures → emotional connection campaigns  
• [bold]Systems:[/bold] Map customer journey → identify friction points → ecosystem redesign

[bold magenta]Result:[/bold magenta] A comprehensive solution that no single approach would discover alone.
        """
        
        panel = Panel(
            explanation.strip(),
            title="💡 Why Cognitive Diversity Matters",
            border_style="cyan",
            padding=(1, 2)
        )
        
        self.console.print("\n")
        self.console.print(panel)
        self.console.print()


def create_framework_visualizer(console: Optional[Console] = None) -> CognitiveFrameworkVisualizer:
    """Create a cognitive framework visualizer instance.
    
    Args:
        console: Optional Rich console instance
        
    Returns:
        Configured CognitiveFrameworkVisualizer
    """
    return CognitiveFrameworkVisualizer(console)