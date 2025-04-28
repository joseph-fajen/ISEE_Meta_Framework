# Model Selection Implementation Plan

This document outlines the changes needed to align the Command Wizard's model selection logic with the core logic in `main.py`.

## Current Issues

1. **Model Selection Logic**: The Command Wizard simply collects a model count but doesn't implement the sophisticated provider-diverse selection logic from `main.py`.
2. **Balanced Model Distribution**: While the wizard has a flag for "balanced models," it doesn't provide a clear explanation that matches the implementation in `main.py`.

## Implementation Plan

### 1. Add Provider-Diverse Model Selection

1. Add a method to the Command Wizard that implements the model selection logic from `main.py`
2. Update the model selection UI to show how models will be selected with diversity in mind

```python
def _get_provider_diverse_models(self, model_count: int) -> List[str]:
    """Select models ensuring diversity across providers.
    
    Args:
        model_count: Number of models to select.
        
    Returns:
        List of model IDs ensuring provider diversity.
    """
    # Create simulated model configs based on available APIs
    model_configs = {}
    
    # Add Anthropic models if available
    if self.api_status["anthropic"]:
        model_configs["claude-3-opus"] = {
            "id": "claude-3-opus",
            "name": "Claude 3 Opus",
            "provider": "anthropic"
        }
        model_configs["claude-3-sonnet"] = {
            "id": "claude-3-sonnet",
            "name": "Claude 3 Sonnet",
            "provider": "anthropic"
        }
        model_configs["claude-3-haiku"] = {
            "id": "claude-3-haiku",
            "name": "Claude 3 Haiku",
            "provider": "anthropic"
        }
    
    # Add OpenAI models if available
    if self.api_status["openai"]:
        model_configs["gpt-4-turbo"] = {
            "id": "gpt-4-turbo",
            "name": "GPT-4 Turbo",
            "provider": "openai"
        }
        model_configs["gpt-3.5-turbo"] = {
            "id": "gpt-3.5-turbo",
            "name": "GPT-3.5 Turbo",
            "provider": "openai"
        }
    
    # Add Google models if available
    if self.api_status["google"]:
        model_configs["gemini-2.5-pro"] = {
            "id": "gemini-2.5-pro",
            "name": "Gemini 2.5 Pro",
            "provider": "google"
        }
    
    # Add Ollama models if available
    if self.api_status["ollama"] and "ollama_models" in self.api_status:
        for model_name in self.api_status["ollama_models"]:
            model_configs[model_name] = {
                "id": model_name,
                "name": model_name,
                "provider": "ollama"
            }
    
    # If no API providers are available, use placeholder models
    if not model_configs:
        return [f"model_{i}" for i in range(1, model_count + 1)]
    
    # Apply the selection logic from main.py
    models = list(model_configs.keys())
    if model_count >= len(models):
        return models  # Return all available models
    
    # Group by provider
    provider_models = {}
    for model_id in models:
        model_config = model_configs[model_id]
        provider = model_config.get("provider", "")
        provider_models.setdefault(provider, []).append(model_id)
    
    # Select models to ensure diversity across providers
    selected_models = []
    
    # First, select one model from each provider
    for provider in provider_models:
        if provider_models[provider] and len(selected_models) < model_count:
            selected_models.append(provider_models[provider][0])
    
    # If we still need more models, add additional ones
    providers_cycle = list(provider_models.keys())
    idx = 0
    while len(selected_models) < model_count and idx < 100:  # avoid infinite loop
        provider = providers_cycle[idx % len(providers_cycle)]
        provider_list = provider_models[provider]
        if len(provider_list) > 1:  # If there are more models from this provider
            for model in provider_list[1:]:
                if model not in selected_models and len(selected_models) < model_count:
                    selected_models.append(model)
        idx += 1
    
    return selected_models
```

### 2. Update Balanced Model Distribution UI

1. Improve explanation of the balanced model distribution
2. Provide a preview of how models will be distributed

```python
# Add to the configure_models method
if model_count > 1:
    # Show explanation first since help_text isn't supported
    if RICH_AVAILABLE:
        self.console.print("[dim]Balanced model distribution:[/dim]")
        self.console.print("[dim]- Interleaves models across combinations, ensuring each model gets similar template/query varieties[/dim]")
        self.console.print("[dim]- Without balancing, combinations are grouped by model type[/dim]")
    else:
        print("Balanced model distribution:")
        print("- Interleaves models across combinations, ensuring each model gets similar template/query varieties")
        print("- Without balancing, combinations are grouped by model type")
    
    balanced_models = Confirm.ask(
        "Ensure balanced representation of models across combinations?",
        default=True
    )
```

### 3. Add Model Selection Preview

1. Add a preview of the selected models based on the chosen model count
2. Show how provider diversity is ensured

```python
# Add after model count selection
selected_models = self._get_provider_diverse_models(model_count)
selected_model_names = []

# Get readable names for the models
for model_id in selected_models:
    if "claude" in model_id:
        selected_model_names.append(f"Anthropic: {model_id}")
    elif "gpt" in model_id:
        selected_model_names.append(f"OpenAI: {model_id}")
    elif "gemini" in model_id:
        selected_model_names.append(f"Google: {model_id}")
    else:
        selected_model_names.append(f"Ollama: {model_id}")

if RICH_AVAILABLE:
    self.console.print("\n[cyan]Selected Models:[/cyan]")
    for name in selected_model_names:
        self.console.print(f"- {name}")
else:
    print("\nSelected Models:")
    for name in selected_model_names:
        print(f"- {name}")
```

### 4. Update Command Preview

1. Enhance the command preview to explain the model selection
2. Indicate how the `--balanced-models` flag affects combination distribution

```python
# Add to the preview_command method's "command_summary" construction
command_summary += f"- Use {len(selected_models)} different models ({', '.join(selected_model_names)})\n"

if self.params["balanced_models"]:
    command_summary += "- Ensure balanced distribution of models across combinations (models interleaved across combinations)\n"
else:
    command_summary += "- Models will be grouped in the combinations (not interleaved)\n"
```

## Testing Strategy

1. Test provider-diverse model selection with different API availability scenarios
2. Test balanced model distribution and verify distribution patterns
3. Compare the wizard's selection logic with main.py's implementation

## Benefits

1. More accurate preview of which models will be used
2. Better understanding for users of how models will be distributed
3. Closer alignment with the core framework's model selection logic