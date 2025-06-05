"""
Models Parameter Editor for ISEE Configuration Dashboard

This module provides an enhanced parameter editor for the models parameter,
featuring OpenRouter model collections, traditional models, and individual selection.

Features:
- OpenRouter model collections with visual displays
- Cost and quality indicators for each collection
- Individual model selection from Top 20 performers
- Traditional/legacy model options
- Local Ollama model support
- Resource estimation and warnings
"""

from typing import List, Dict, Any, Optional, Union
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Confirm, Prompt

from enhanced_parameter_editor import EnhancedParameterEditor, ParameterItem, SelectionMode


class ModelsParameterEditor(EnhancedParameterEditor):
    """Enhanced editor for models parameter with OpenRouter collections and individual selection"""
    
    def __init__(self, console: Console, dashboard_state, **kwargs):
        models_param = dashboard_state.parameters.get("models")
        current_models = models_param.value if models_param else 3
        super().__init__(console, "models", current_models)
        self.dashboard_state = dashboard_state
        self.selection_mode = SelectionMode.HYBRID  # Support both count and specific selection
        self.show_help_on_start = True
        
        # Model selection modes
        self.selection_modes = {
            "collections": {
                "name": "OpenRouter Collections",
                "icon": "🏆",
                "description": "Curated model collections optimized for specific use cases",
                "recommended": True
            },
            "individual": {
                "name": "Individual OpenRouter Models", 
                "icon": "🎯",
                "description": "Select specific models from Top 20 performers",
                "recommended": False
            },
            "traditional": {
                "name": "Traditional API Models",
                "icon": "🔧", 
                "description": "Direct API models (Claude, GPT, Gemini, etc.)",
                "recommended": False
            },
            "local": {
                "name": "Local Ollama Models",
                "icon": "🖥️",
                "description": "Locally hosted models via Ollama",
                "recommended": False
            }
        }
    
    def load_items(self) -> List[ParameterItem]:
        """Load available model options organized by type"""
        items = []
        
        # 1. Load OpenRouter Collections (Primary recommendation)
        items.extend(self._load_openrouter_collections())
        
        # 2. Load individual OpenRouter models
        items.extend(self._load_individual_openrouter_models())
        
        # 3. Load traditional API models
        items.extend(self._load_traditional_models())
        
        # 4. Load local Ollama models
        items.extend(self._load_ollama_models())
        
        return items
    
    def _load_openrouter_collections(self) -> List[ParameterItem]:
        """Load OpenRouter model collections"""
        items = []
        
        try:
            from openrouter_model_collections import create_default_model_collections
            collections_manager = create_default_model_collections()
            collections = collections_manager.get_all_collections()
            
            for collection in collections:
                # Estimate collection cost and quality
                cost_profile = collection.cost_profile
                expected_count = collection.expected_model_count
                
                # Map cost profiles to estimates
                cost_estimates = {
                    "budget": "$0.05-$0.15",
                    "balanced": "$0.15-$1.00", 
                    "premium": "$1.00-$5.00+"
                }
                
                quality_estimates = {
                    "budget": "7-8",
                    "balanced": "8-9",
                    "premium": "9-10"
                }
                
                metadata = {
                    "type": "openrouter_collection",
                    "cost_profile": cost_profile,
                    "cost_estimate": cost_estimates.get(cost_profile, "$0.50"),
                    "quality_estimate": quality_estimates.get(cost_profile, "8"),
                    "model_count": expected_count,
                    "icon": collection.icon,
                    "collection_id": collection.name.lower().replace(" ", "_"),
                    "recommended": collection.name == "Top 20 Performers",
                    "scope": "multiple_models",
                    "complexity": "optimized"
                }
                
                items.append(ParameterItem(
                    id=f"collection_{collection.name.lower().replace(' ', '_')}",
                    name=f"{collection.icon} {collection.name}",
                    description=collection.description,
                    metadata=metadata
                ))
                
        except Exception as e:
            # Add fallback option if OpenRouter collections unavailable
            items.append(ParameterItem(
                id="collection_fallback",
                name="🏆 OpenRouter Collections (Unavailable)",
                description="OpenRouter model collections not available",
                metadata={
                    "type": "openrouter_collection",
                    "cost_profile": "unknown",
                    "cost_estimate": "N/A",
                    "quality_estimate": "N/A",
                    "model_count": 0,
                    "error": str(e),
                    "scope": "unavailable"
                }
            ))
        
        return items
    
    def _load_individual_openrouter_models(self) -> List[ParameterItem]:
        """Load individual OpenRouter models from Top 20"""
        items = []
        
        try:
            from openrouter_model_collections import create_default_model_collections
            collections_manager = create_default_model_collections()
            top_performers = collections_manager.get_collection("top_performers")
            
            # Extract specific models from Top 20 collection
            specific_models = []
            for spec in top_performers.model_specs:
                if "specific_models" in spec:
                    specific_models = spec["specific_models"][:10]  # Show top 10
                    break
            
            for i, model_id in enumerate(specific_models, 1):
                provider = model_id.split('/')[0] if '/' in model_id else "unknown"
                model_name = model_id.split('/')[-1] if '/' in model_id else model_id
                
                # Estimate cost and quality for individual models
                cost_estimate = self._estimate_model_cost(model_id)
                quality_estimate = self._estimate_model_quality(model_id)
                
                metadata = {
                    "type": "individual_openrouter",
                    "model_id": model_id,
                    "provider": provider.title(),
                    "cost_estimate": cost_estimate,
                    "quality_estimate": f"{quality_estimate}/10",
                    "ranking": i,
                    "scope": "single_model",
                    "complexity": "advanced"
                }
                
                items.append(ParameterItem(
                    id=f"individual_{model_id.replace('/', '_')}",
                    name=f"#{i} {model_name}",
                    description=f"Top {i} OpenRouter performer from {provider.title()}",
                    metadata=metadata
                ))
                
        except Exception:
            # Add fallback if individual models unavailable
            items.append(ParameterItem(
                id="individual_fallback",
                name="🎯 Individual Models (Unavailable)",
                description="Individual OpenRouter model selection not available",
                metadata={
                    "type": "individual_openrouter",
                    "scope": "unavailable"
                }
            ))
        
        return items
    
    def _load_traditional_models(self) -> List[ParameterItem]:
        """Load traditional API models from configuration"""
        items = []
        
        try:
            import json
            with open("unified_config.json", "r") as f:
                config = json.load(f)
                api_models = config.get("models", {}).get("api_models", [])
            
            # Group by provider for better organization
            provider_groups = {}
            for model in api_models:
                provider = model.get("provider", "unknown").upper()
                if provider not in provider_groups:
                    provider_groups[provider] = []
                provider_groups[provider].append(model)
            
            # Create items for each provider group
            for provider, models in provider_groups.items():
                model_count = len(models)
                primary_model = models[0] if models else {}
                
                # Estimate cost based on provider
                provider_costs = {
                    "ANTHROPIC": "$3.00-$15.00",
                    "OPENAI": "$0.15-$30.00", 
                    "GOOGLE": "$0.075-$7.00",
                    "OLLAMA": "Free (Local)"
                }
                
                metadata = {
                    "type": "traditional_api",
                    "provider": provider,
                    "model_count": model_count,
                    "cost_estimate": provider_costs.get(provider, "$1.00-$5.00"),
                    "requires_api_key": primary_model.get("requires", "Unknown"),
                    "scope": "provider_group",
                    "complexity": "standard"
                }
                
                items.append(ParameterItem(
                    id=f"traditional_{provider.lower()}",
                    name=f"🔧 {provider} Models",
                    description=f"{model_count} {provider} models available ({primary_model.get('requires', 'API key required')})",
                    metadata=metadata
                ))
                
        except Exception:
            # Add fallback traditional options
            fallback_providers = ["Anthropic", "OpenAI", "Google", "Local Ollama"]
            for provider in fallback_providers:
                items.append(ParameterItem(
                    id=f"traditional_{provider.lower()}",
                    name=f"🔧 {provider} Models",
                    description=f"Traditional {provider} API models",
                    metadata={
                        "type": "traditional_api",
                        "provider": provider.upper(),
                        "scope": "fallback"
                    }
                ))
        
        return items
    
    def _load_ollama_models(self) -> List[ParameterItem]:
        """Load local Ollama models"""
        items = []
        
        try:
            import json
            with open("ollama_config.json", "r") as f:
                ollama_config = json.load(f)
                ollama_models = ollama_config.get("models", {}).get("api_models", [])
            
            if ollama_models:
                for model in ollama_models[:5]:  # Show first 5 Ollama models
                    model_name = model.get("name", "Unknown")
                    
                    metadata = {
                        "type": "local_ollama",
                        "model_name": model_name,
                        "cost_estimate": "Free (Local)",
                        "quality_estimate": "7-8/10",
                        "requires": "Local Ollama installation",
                        "scope": "local_model",
                        "complexity": "local"
                    }
                    
                    items.append(ParameterItem(
                        id=f"ollama_{model_name.replace('-', '_')}",
                        name=f"🖥️ {model_name}",
                        description="Local Ollama model (free, private)",
                        metadata=metadata
                    ))
            else:
                items.append(ParameterItem(
                    id="ollama_none",
                    name="🖥️ No Local Models",
                    description="No Ollama models configured",
                    metadata={"type": "local_ollama", "scope": "none"}
                ))
                
        except Exception:
            items.append(ParameterItem(
                id="ollama_unavailable",
                name="🖥️ Ollama Unavailable",
                description="Ollama configuration not available",
                metadata={"type": "local_ollama", "scope": "unavailable"}
            ))
        
        return items
    
    def get_display_table(self) -> Table:
        """Create Rich table displaying model options by type"""
        table = Table(
            title="🤖 Available Model Selection Options",
            show_header=True,
            header_style="bold white",
            show_lines=True,
            expand=False
        )
        
        table.add_column("#", style="green", width=3)
        table.add_column("Model Option", style="bold white", min_width=30)
        table.add_column("Type", style="yellow", width=18)
        table.add_column("Cost Est.", style="blue", width=12)
        table.add_column("Quality", style="magenta", width=8)
        table.add_column("Scope", style="cyan", width=12)
        
        # Group items by type for better organization
        current_type = None
        for i, item in enumerate(self.items, 1):
            item_type = item.metadata.get("type", "unknown")
            
            # Add type separator
            if item_type != current_type:
                if current_type is not None:
                    table.add_row("", "", "", "", "", "", style="dim")
                current_type = item_type
            
            # Format cost and quality
            cost = item.metadata.get("cost_estimate", "Unknown")
            quality = item.metadata.get("quality_estimate", "N/A")
            
            # Color code by type
            type_colors = {
                "openrouter_collection": "bright_green",
                "individual_openrouter": "cyan", 
                "traditional_api": "blue",
                "local_ollama": "magenta"
            }
            type_color = type_colors.get(item_type, "white")
            
            # Add recommendation indicator
            recommended = item.metadata.get("recommended", False)
            name_display = f"⭐ {item.name}" if recommended else item.name
            
            scope = item.metadata.get("scope", "unknown").replace("_", " ").title()
            
            table.add_row(
                str(i),
                name_display,
                f"[{type_color}]{item_type.replace('_', ' ').title()}[/{type_color}]",
                cost,
                quality,
                scope
            )
        
        return table
    
    def validate_selection(self, user_input: str) -> bool:
        """Validate model selection"""
        if not user_input or user_input.strip() == "":
            return False
        
        # Handle count-based selection (simple number)
        if user_input.isdigit():
            return int(user_input) > 0
        
        # Handle item selection
        try:
            if "," in user_input or "-" in user_input:
                selected_numbers = self._parse_number_selection(user_input, len(self.items))
                return len(selected_numbers) > 0
            else:
                # Single item selection
                num = int(user_input)
                return 1 <= num <= len(self.items)
        except ValueError:
            return False
    
    def apply_selection(self, selection) -> None:
        """Apply model selection to dashboard state"""
        if isinstance(selection, int):
            if selection <= len(self.items):
                # Item selection - handle based on item type
                selected_item = self.items[selection - 1]
                self._apply_item_selection(selected_item)
            else:
                # Count-based selection
                self.dashboard_state.parameters["models"].value = selection
                self.current_value = selection
        elif isinstance(selection, list):
            # Multiple item selection - use first item's logic for now
            if selection and selection[0] <= len(self.items):
                selected_item = self.items[selection[0] - 1]
                self._apply_item_selection(selected_item)
    
    def _apply_item_selection(self, selected_item: ParameterItem) -> None:
        """Apply specific item selection based on item type"""
        item_type = selected_item.metadata.get("type")
        
        if item_type == "openrouter_collection":
            # Set model count based on collection
            model_count = selected_item.metadata.get("model_count", 3)
            self.dashboard_state.parameters["models"].value = model_count
            
            # Set OpenRouter configuration
            collection_id = selected_item.metadata.get("collection_id")
            if collection_id and hasattr(self.dashboard_state.parameters, "openrouter_filters"):
                self.dashboard_state.parameters["openrouter_filters"].value = f"collection:{collection_id}"
            
            # Ensure config file is set to OpenRouter
            if hasattr(self.dashboard_state.parameters, "config_file"):
                self.dashboard_state.parameters["config_file"].value = "openrouter_config.json"
            
            self.current_value = model_count
            
        elif item_type == "individual_openrouter":
            # Individual model selection
            model_id = selected_item.metadata.get("model_id")
            if model_id:
                self.dashboard_state.parameters["models"].value = 1
                
                # Set specific model filter
                if hasattr(self.dashboard_state.parameters, "openrouter_filters"):
                    self.dashboard_state.parameters["openrouter_filters"].value = f"specific_models:{model_id}"
                
                # Ensure config file is set to OpenRouter
                if hasattr(self.dashboard_state.parameters, "config_file"):
                    self.dashboard_state.parameters["config_file"].value = "openrouter_config.json"
                
                self.current_value = 1
            
        elif item_type == "traditional_api":
            # Traditional API models
            provider = selected_item.metadata.get("provider", "").lower()
            model_count = selected_item.metadata.get("model_count", 3)
            
            # Set appropriate model count
            self.dashboard_state.parameters["models"].value = min(model_count, 3)  # Reasonable default
            
            # Set config file based on provider
            if provider == "ollama":
                if hasattr(self.dashboard_state.parameters, "config_file"):
                    self.dashboard_state.parameters["config_file"].value = "ollama_config.json"
            else:
                if hasattr(self.dashboard_state.parameters, "config_file"):
                    self.dashboard_state.parameters["config_file"].value = "unified_config.json"
            
            self.current_value = min(model_count, 3)
            
        elif item_type == "local_ollama":
            # Local Ollama models
            self.dashboard_state.parameters["models"].value = 1
            
            # Enable Ollama usage
            if hasattr(self.dashboard_state.parameters, "use_ollama"):
                self.dashboard_state.parameters["use_ollama"].value = True
            
            # Set Ollama config
            if hasattr(self.dashboard_state.parameters, "config_file"):
                self.dashboard_state.parameters["config_file"].value = "ollama_config.json"
            
            self.current_value = 1
    
    def _estimate_model_cost(self, model_id: str) -> str:
        """Estimate cost per 1M tokens for a model"""
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
            "openai/gpt-4.1": "$5.00"
        }
        return cost_map.get(model_id, "$0.50")
    
    def _estimate_model_quality(self, model_id: str) -> float:
        """Estimate quality score for a model"""
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
            "openai/gpt-4.1": 9.3
        }
        return quality_map.get(model_id, 7.0)
    
    def _display_parameter_specific_help(self) -> None:
        """Display models-specific help information"""
        self.console.print("\n[bold cyan]Model Selection Help:[/bold cyan]")
        self.console.print("• [green]OpenRouter Collections[/green]: Recommended - curated model sets optimized for specific use cases")
        self.console.print("• [green]Individual Models[/green]: Advanced - select specific high-performing models")
        self.console.print("• [green]Traditional APIs[/green]: Direct API access to specific providers")
        self.console.print("• [green]Local Models[/green]: Free, private Ollama models")
        self.console.print("")
        self.console.print("[bold yellow]Cost vs Quality Guide:[/bold yellow]")
        self.console.print("• [green]Budget ($0.05-$0.15)[/green]: Good quality, cost-effective")
        self.console.print("• [yellow]Balanced ($0.15-$1.00)[/yellow]: High quality, reasonable cost")
        self.console.print("• [red]Premium ($1.00+)[/red]: Highest quality, expensive")
        self.console.print("• [magenta]Free/Local[/magenta]: Variable quality, no API costs")
        self.console.print("")
        self.console.print("[bold white]Model Count Impact:[/bold white]")
        self.console.print("• [cyan]1-2 models[/cyan]: Focused analysis, lower cost")
        self.console.print("• [yellow]3-5 models[/yellow]: Balanced cognitive diversity (recommended)")
        self.console.print("• [red]6+ models[/red]: Maximum diversity, higher cost")
    
    def _show_item_preview(self, item: ParameterItem, number: int) -> None:
        """Enhanced preview showing model option details"""
        item_type = item.metadata.get("type", "unknown")
        
        content = [
            f"[bold cyan]{item.name}[/bold cyan]",
            "",
            f"[yellow]Type:[/yellow] {item_type.replace('_', ' ').title()}",
            f"[yellow]Description:[/yellow] {item.description}",
        ]
        
        # Add type-specific details
        if item_type == "openrouter_collection":
            content.extend([
                f"[yellow]Cost Profile:[/yellow] {item.metadata.get('cost_profile', 'unknown').title()}",
                f"[yellow]Model Count:[/yellow] ~{item.metadata.get('model_count', 'unknown')} models",
                f"[yellow]Cost Estimate:[/yellow] {item.metadata.get('cost_estimate', 'unknown')} per 1M tokens",
                f"[yellow]Quality Range:[/yellow] {item.metadata.get('quality_estimate', 'unknown')}/10",
            ])
        elif item_type == "individual_openrouter":
            content.extend([
                f"[yellow]Provider:[/yellow] {item.metadata.get('provider', 'unknown')}",
                f"[yellow]Ranking:[/yellow] #{item.metadata.get('ranking', 'unknown')} in Top 20",
                f"[yellow]Cost Estimate:[/yellow] {item.metadata.get('cost_estimate', 'unknown')} per 1M tokens",
                f"[yellow]Quality Score:[/yellow] {item.metadata.get('quality_estimate', 'unknown')}",
            ])
        elif item_type == "traditional_api":
            content.extend([
                f"[yellow]Provider:[/yellow] {item.metadata.get('provider', 'unknown')}",
                f"[yellow]Model Count:[/yellow] {item.metadata.get('model_count', 'unknown')} available",
                f"[yellow]API Key Required:[/yellow] {item.metadata.get('requires_api_key', 'unknown')}",
                f"[yellow]Cost Estimate:[/yellow] {item.metadata.get('cost_estimate', 'unknown')} per 1M tokens",
            ])
        elif item_type == "local_ollama":
            content.extend([
                f"[yellow]Model Name:[/yellow] {item.metadata.get('model_name', 'unknown')}",
                f"[yellow]Cost:[/yellow] {item.metadata.get('cost_estimate', 'Free')}",
                f"[yellow]Requirements:[/yellow] {item.metadata.get('requires', 'Local installation')}",
                f"[yellow]Quality:[/yellow] {item.metadata.get('quality_estimate', 'Variable')}",
            ])
        
        # Add recommendation
        if item.metadata.get("recommended"):
            content.extend([
                "",
                "[bold green]⭐ Recommended Option[/bold green]",
                "This option provides optimal balance of quality, cost, and ease of use."
            ])
        
        preview_panel = Panel(
            "\n".join(content),
            title=f"Model Option #{number} Preview",
            border_style="cyan"
        )
        self.console.print(preview_panel)
    
    def _process_selection_input(self, user_input: str) -> bool:
        """Override to handle model count vs item selection"""
        # First try as item selection (if reasonable item number)
        try:
            if user_input.isdigit():
                num = int(user_input)
                if 1 <= num <= len(self.items):
                    # Item selection
                    self.apply_selection(num)
                    selected_item = self.items[num - 1]
                    self.console.print(f"[green]✓ Selected: {selected_item.name}[/green]")
                    return True
                elif num > len(self.items):
                    # Model count selection
                    if num > 10:
                        self.console.print(f"[yellow]⚠️ Warning: {num} models will significantly increase cost[/yellow]")
                        if not Confirm.ask(f"Continue with {num} models?"):
                            return False
                    
                    self.apply_selection(num)
                    self.console.print(f"[green]✓ Set model count to: {num}[/green]")
                    return True
                else:
                    self.console.print(f"[red]Invalid selection. Use 1-{len(self.items)} for options or any number for model count[/red]")
                    return False
        except ValueError:
            pass
        
        # Try multiple selection syntax
        return super()._process_selection_input(user_input)