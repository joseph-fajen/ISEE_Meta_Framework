# Configuration Integration Implementation Plan

This document outlines the changes needed to improve the Command Wizard's configuration file handling to align with the core logic in `main.py`.

## Current Issues

1. **Configuration File Selection**: The Command Wizard currently only checks for "unified_config.json" but doesn't provide options for selecting other configuration files.
2. **Configuration File Explanation**: The explanation of the unified_config.json file is limited and doesn't clearly explain its purpose or how it maps to actual APIs.
3. **Configuration Validation**: There's no validation of the selected configuration file to ensure it's compatible with the ISEE framework.

## Implementation Plan

### 1. Add Configuration File Selection

Add a new method to allow selecting from available configuration files:

```python
def _select_config_file(self) -> Optional[str]:
    """Allow the user to select a configuration file.
    
    Returns:
        Selected configuration file or None if no file is selected.
    """
    # Find all JSON files that might be configuration files
    potential_configs = [f for f in os.listdir() if f.endswith('.json') and 'config' in f.lower()]
    
    if not potential_configs:
        return None
    
    # Sort config files with unified_config.json first
    if "unified_config.json" in potential_configs:
        potential_configs.remove("unified_config.json")
        potential_configs.insert(0, "unified_config.json")
    
    if RICH_AVAILABLE:
        self.console.print("\n[bold cyan]Configuration File Selection[/bold cyan]")
        
        # Display available configuration files
        configs_table = Table(title="Available Configuration Files")
        configs_table.add_column("#", style="green")
        configs_table.add_column("File", style="cyan")
        configs_table.add_column("Description")
        
        for i, config_file in enumerate(potential_configs, 1):
            description = self._get_config_description(config_file)
            configs_table.add_row(str(i), config_file, description)
        
        self.console.print(configs_table)
        
        # Ask if the user wants to select a configuration file
        use_config = Confirm.ask(
            "Would you like to use a configuration file?",
            default=True if "unified_config.json" in potential_configs else False
        )
        
        if not use_config:
            return None
        
        # Allow selection of configuration file
        while True:
            choice = IntPrompt.ask(
                "Select a configuration file by number (or 0 to skip)",
                default=1 if "unified_config.json" in potential_configs else 0,
                show_default=True
            )
            
            if choice == 0:
                return None
            
            if 1 <= choice <= len(potential_configs):
                selected_config = potential_configs[choice - 1]
                
                # Validate the config file
                if self._validate_config_file(selected_config):
                    return selected_config
                else:
                    self.console.print(f"[yellow]Warning: {selected_config} does not appear to be a valid ISEE configuration file. It may be missing required model mappings.[/yellow]")
                    use_anyway = Confirm.ask("Use this configuration file anyway?", default=False)
                    if use_anyway:
                        return selected_config
            else:
                self.console.print("[yellow]Invalid selection. Please try again.[/yellow]")
    else:
        print("\nConfiguration File Selection")
        print("Available Configuration Files:")
        
        for i, config_file in enumerate(potential_configs, 1):
            description = self._get_config_description(config_file)
            print(f"{i}. {config_file} - {description}")
        
        print("0. No configuration file")
        
        # Ask if the user wants to select a configuration file
        use_config_input = input(f"Would you like to use a configuration file? (y/n) [{'y' if 'unified_config.json' in potential_configs else 'n'}]: ").lower()
        if not use_config_input:
            use_config = "unified_config.json" in potential_configs
        else:
            use_config = use_config_input in ["y", "yes"]
        
        if not use_config:
            return None
        
        # Allow selection of configuration file
        while True:
            try:
                choice_input = input(f"Select a configuration file by number (or 0 to skip) [{'1' if 'unified_config.json' in potential_configs else '0'}]: ")
                if not choice_input:
                    choice = 1 if "unified_config.json" in potential_configs else 0
                else:
                    choice = int(choice_input)
                
                if choice == 0:
                    return None
                
                if 1 <= choice <= len(potential_configs):
                    selected_config = potential_configs[choice - 1]
                    
                    # Validate the config file
                    if self._validate_config_file(selected_config):
                        return selected_config
                    else:
                        print(f"Warning: {selected_config} does not appear to be a valid ISEE configuration file. It may be missing required model mappings.")
                        use_anyway_input = input("Use this configuration file anyway? (y/n) [n]: ").lower()
                        use_anyway = use_anyway_input in ["y", "yes"]
                        if use_anyway:
                            return selected_config
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a number.")
                
        return None
```

### 2. Add Configuration Validation

Add validation to ensure the selected configuration file is compatible with the ISEE framework:

```python
def _validate_config_file(self, config_path: str) -> bool:
    """Validate that a configuration file is compatible with the ISEE framework.
    
    Args:
        config_path: Path to the configuration file.
        
    Returns:
        True if the configuration file is valid, False otherwise.
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check if the config file has the expected structure
        if not isinstance(config, dict):
            return False
        
        # Check for models configuration
        if "models" not in config:
            return False
        
        # Ensure models is either a list or a dict with sections
        models = config["models"]
        if not (isinstance(models, list) or isinstance(models, dict)):
            return False
        
        # If it's a dict, check for expected sections
        if isinstance(models, dict):
            if not any(section in models for section in ["api_models", "ollama_models"]):
                return False
        
        return True
    except (json.JSONDecodeError, IOError):
        return False
```

### 3. Add Configuration Description Function

Add a function to provide descriptions for configuration files:

```python
def _get_config_description(self, config_path: str) -> str:
    """Get a description for a configuration file.
    
    Args:
        config_path: Path to the configuration file.
        
    Returns:
        Description of the configuration file.
    """
    # Check for known configuration files
    if config_path == "unified_config.json":
        return "Unified configuration with models mapped to API providers"
    elif config_path == "sample_config.json":
        return "Sample configuration for demonstration purposes"
    elif config_path == "gemini_test_config.json":
        return "Configuration for testing Google Gemini models"
    elif config_path == "ollama_config.json":
        return "Configuration for Ollama models"
    
    # Try to read the file and determine its purpose
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if "models" in config:
            models = config["models"]
            model_count = 0
            
            if isinstance(models, list):
                model_count = len(models)
            elif isinstance(models, dict):
                # Count models in each section
                api_models = models.get("api_models", [])
                ollama_models = models.get("ollama_models", [])
                model_count = len(api_models) + len(ollama_models)
            
            return f"Configuration with {model_count} model mappings"
    except (json.JSONDecodeError, IOError):
        pass
    
    return "Unknown configuration file"
```

### 4. Update Command Generation to Use Selected Config

Modify the `generate_command` method to use the selected configuration file:

```python
def generate_command(self) -> str:
    """Generate the ISEE command based on user selections.
    
    Returns:
        The generated command string.
    """
    cmd_parts = ["python main.py"]
    
    # Add config parameter if a configuration file was selected
    if self.params.get("config_file"):
        cmd_parts.append(f'--config "{self.params["config_file"]}"')
    # Otherwise, use unified_config.json if it exists as a fallback
    elif os.path.exists("unified_config.json"):
        cmd_parts.append('--config unified_config.json')
        # Also add a note to the object for display in preview
        self.using_unified_config = True
    else:
        self.using_unified_config = False
    
    # Rest of the command generation...
```

### 5. Enhance Configuration Explanation

Enhance the command preview to better explain the purpose and impact of the configuration file:

```python
def preview_command(self, command: str) -> None:
    """Preview the generated command.
    
    Args:
        command: The generated command string.
    """
    # Display config file usage information
    if self.params.get("config_file") or hasattr(self, 'using_unified_config') and self.using_unified_config:
        config_file = self.params.get("config_file", "unified_config.json")
        
        if RICH_AVAILABLE:
            self.console.print(Panel(
                f"[green]Using {config_file} for model configuration[/green]\n\n"
                "The configuration file maps model IDs to actual API providers and includes:\n"
                "- Model names and versions\n"
                "- API provider information\n"
                "- Model-specific parameters\n\n"
                "This ensures the correct models are used for each API provider.",
                title="Configuration Information",
                border_style="green"
            ))
        else:
            print(f"\nCONFIGURATION INFORMATION:")
            print(f"Using {config_file} for model configuration")
            print("The configuration file maps model IDs to actual API providers and includes:")
            print("- Model names and versions")
            print("- API provider information")
            print("- Model-specific parameters")
            print("\nThis ensures the correct models are used for each API provider.")
    
    # Rest of the preview implementation...
```

## Adding Configuration Step to Wizard Flow

Add a new step to the wizard flow to select a configuration file:

```python
def run_wizard(self) -> None:
    """Run the complete wizard flow."""
    # Show welcome message
    self.show_welcome()
    
    # Select configuration file
    config_file = self._select_config_file()
    if config_file:
        self.params["config_file"] = config_file
    
    # Get basic query information
    self.get_query()
    self.select_domain()
    
    # Configure models
    self.configure_models()
    
    # Rest of the wizard flow...
```

## Testing Strategy

1. Test configuration file selection with various available files
2. Test configuration file validation with valid and invalid files
3. Test the explanation of configuration files
4. Test the command construction with different configuration options

## Benefits

1. More flexibility in choosing configuration files
2. Better validation to prevent using incompatible configuration files
3. Clearer explanation of the purpose and impact of configuration files
4. Better alignment with the main.py parameter handling