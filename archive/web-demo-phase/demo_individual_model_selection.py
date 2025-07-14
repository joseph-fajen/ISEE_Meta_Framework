#!/usr/bin/env python3
"""
Demo: Enhanced Individual Model Selection

This script demonstrates the new individual Top 20 model selection functionality.
"""

import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from command_wizard import CommandWizard
    from openrouter_model_collections import create_default_model_collections
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def demo_individual_model_selection():
    """Demonstrate the individual model selection feature."""
    console = Console()
    
    console.print(Panel.fit(
        "[bold blue]🏆 ISEE Framework: Enhanced Individual Model Selection Demo[/bold blue]\n"
        "[cyan]Testing the new Top 20 OpenRouter model selection capability[/cyan]",
        border_style="blue"
    ))
    
    # Create wizard instance
    wizard = CommandWizard()
    
    # Set up for expert mode (required for individual selection)
    wizard.complexity_level = "expert"
    wizard.api_status = {
        "openrouter": True,
        "anthropic": False,
        "openai": False,
        "google": False,
        "ollama": False
    }
    
    # Set up OpenRouter collections
    wizard.openrouter_collections = create_default_model_collections()
    
    console.print("\n[bold green]✓ Setup Complete[/bold green]")
    console.print(f"[cyan]→ Complexity Level: {wizard.complexity_level}[/cyan]")
    console.print(f"[cyan]→ OpenRouter Status: {wizard.api_status['openrouter']}[/cyan]")
    console.print(f"[cyan]→ Collections Available: {len(wizard.openrouter_collections.get_all_collections())}[/cyan]")
    
    # Test model parsing
    console.print("\n[bold yellow]📊 Testing Model Selection Parsing[/bold yellow]")
    
    test_cases = [
        ("1,3,5", "Individual models"),
        ("1-3", "Range selection"),
        ("1,3-5,7", "Mixed selection"),
        ("all", "All models"),
        ("", "Default (top 3)")
    ]
    
    parse_table = Table(title="Selection Parsing Tests")
    parse_table.add_column("Input", style="cyan")
    parse_table.add_column("Description", style="yellow")
    parse_table.add_column("Result", style="green")
    
    for input_str, description in test_cases:
        result = wizard._parse_model_selection(input_str, 20)
        result_str = str(result) if len(result) <= 5 else f"{result[:5]}... ({len(result)} total)"
        parse_table.add_row(f'"{input_str}"', description, result_str)
    
    console.print(parse_table)
    
    # Test cost and quality estimation
    console.print("\n[bold yellow]💰 Testing Cost & Quality Estimation[/bold yellow]")
    
    sample_models = [
        "openai/gpt-4o-mini",
        "google/gemini-2.0-flash", 
        "anthropic/claude-3.7-sonnet",
        "deepseek/deepseek-v3-0324-free",
        "unknown/test-model"
    ]
    
    estimation_table = Table(title="Model Estimates")
    estimation_table.add_column("Model", style="cyan")
    estimation_table.add_column("Cost/1M", style="blue")
    estimation_table.add_column("Quality", style="magenta")
    
    for model_id in sample_models:
        cost = wizard._estimate_model_cost(model_id)
        quality = wizard._estimate_model_quality(model_id)
        model_name = model_id.split('/')[-1] if '/' in model_id else model_id
        estimation_table.add_row(model_name, cost, f"{quality}/10")
    
    console.print(estimation_table)
    
    # Test Top 20 collection access
    console.print("\n[bold yellow]🏆 Testing Top 20 Collection[/bold yellow]")
    
    top_performers = wizard.openrouter_collections.get_collection("top_performers")
    if top_performers:
        console.print(f"[green]✓ Top Performers collection found[/green]")
        console.print(f"[cyan]→ Name: {top_performers.name}[/cyan]")
        console.print(f"[cyan]→ Description: {top_performers.description}[/cyan]")
        console.print(f"[cyan]→ Expected models: {top_performers.expected_model_count}[/cyan]")
        
        # Extract specific models
        specific_models = []
        for spec in top_performers.model_specs:
            if "specific_models" in spec:
                specific_models = spec["specific_models"]
                break
        
        console.print(f"[cyan]→ Available models: {len(specific_models)}[/cyan]")
        
        # Show first 5 models
        if specific_models:
            console.print("\n[bold]Top 5 Models:[/bold]")
            for i, model_id in enumerate(specific_models[:5], 1):
                provider = model_id.split('/')[0] if '/' in model_id else "unknown"
                model_name = model_id.split('/')[-1] if '/' in model_id else model_id
                cost = wizard._estimate_model_cost(model_id)
                quality = wizard._estimate_model_quality(model_id)
                console.print(f"[cyan]{i}. {model_name} ({provider.title()}) - {cost}/1M - {quality}/10[/cyan]")
    else:
        console.print("[red]✗ Top Performers collection not found[/red]")
    
    # Test cost profile calculation
    console.print("\n[bold yellow]📈 Testing Cost Profile Calculation[/bold yellow]")
    
    test_selections = [
        [{"cost": "Free", "id": "model1"}, {"cost": "Free", "id": "model2"}],
        [{"cost": "$0.15", "id": "model1"}, {"cost": "$0.30", "id": "model2"}],
        [{"cost": "$3.00", "id": "model1"}, {"cost": "$5.00", "id": "model2"}],
        [{"cost": "Free", "id": "model1"}, {"cost": "$3.00", "id": "model2"}]
    ]
    
    profile_table = Table(title="Cost Profile Tests")
    profile_table.add_column("Selection", style="cyan")
    profile_table.add_column("Profile", style="green")
    
    for i, selection in enumerate(test_selections, 1):
        costs = [model["cost"] for model in selection]
        profile = wizard._calculate_selection_cost(selection)
        profile_table.add_row(f"Test {i}: {costs}", profile)
    
    console.print(profile_table)
    
    # Summary
    console.print(Panel.fit(
        "[bold green]🎉 Demo Complete![/bold green]\n"
        "[cyan]The enhanced individual model selection is ready for use in expert/advanced mode.[/cyan]\n\n"
        "[yellow]Key Features Implemented:[/yellow]\n"
        "• Individual Top 20 model selection in expert mode\n"
        "• Flexible selection parsing (ranges, lists, 'all')\n"
        "• Cost and quality estimation for each model\n"
        "• Automatic cost profile calculation\n"
        "• Rich table interface with provider information\n"
        "• Integration with existing OpenRouter collections",
        border_style="green"
    ))

if __name__ == "__main__":
    demo_individual_model_selection()