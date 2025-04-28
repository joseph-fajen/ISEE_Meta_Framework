# Parameter Mapping Implementation Plan

This document outlines the changes needed to improve the Command Wizard's parameter mapping to align with the main.py command-line interface.

## Current Issues

1. **Parameter Consistency**: Many parameters in the Command Wizard don't match their counterparts in main.py in terms of type or validation.
2. **Missing Parameters**: Several parameters available in main.py are not exposed in the wizard.
3. **Parameter Dependencies**: Dependencies between parameters are not properly validated.
4. **Parameter Help**: There's limited help information about available parameters and their effects.

## Implementation Plan

### 1. Add Parameter Extraction from main.py

Add a method to dynamically extract parameters from main.py to ensure the wizard stays in sync with main.py's CLI:

```python
def _extract_main_parameters(self) -> Dict[str, Dict[str, Any]]:
    """Extract parameters from main.py using the help command.
    
    Returns:
        Dictionary mapping parameter names to their details.
    """
    try:
        # Run main.py --help to get parameter information
        result = subprocess.run(["python", "main.py", "--help"], 
                                capture_output=True, text=True)
        help_text = result.stdout
        
        # Extract parameters using regex
        param_pattern = r"(?:--([a-zA-Z0-9_-]+))(?: ((?:\{[^}]+\})|(?:[A-Z_]+)))?"
        params = {}
        choice_pattern = r"\{([^}]+)\}"
        
        # Find parameters and their types
        for line in help_text.split("\n"):
            for match in re.finditer(param_pattern, line):
                param_name = match.group(1).replace("-", "_")
                param_type = "flag"  # Default type is flag (boolean)
                choices = None
                
                # If there's a type indicator
                if match.group(2):
                    type_indicator = match.group(2)
                    
                    # Check if it's a choice type
                    choice_match = re.search(choice_pattern, type_indicator)
                    if choice_match:
                        param_type = "choice"
                        choices = [choice.strip() for choice in choice_match.group(1).split(",")]
                    else:
                        # Otherwise it's a value type
                        param_type = "text"
                
                # Store parameter details
                params[param_name] = {
                    "type": param_type,
                    "required": False,  # Assume not required by default
                }
                
                # Add choices if available
                if choices:
                    params[param_name]["choices"] = choices
        
        return params
    except Exception as e:
        if RICH_AVAILABLE:
            self.console.print(f"[yellow]Warning: Could not extract parameters from main.py: {str(e)}[/yellow]")
        else:
            print(f"Warning: Could not extract parameters from main.py: {str(e)}")
        
        # Return an empty dict if extraction fails
        return {}
```

### 2. Add Parameter Validation

Add validation for parameters to ensure they match main.py's expectations:

```python
def _validate_parameters(self) -> Dict[str, Any]:
    """Validate wizard parameters against main.py parameters.
    
    Returns:
        Dictionary with validation results.
    """
    # Extract main.py parameters
    main_params = self._extract_main_parameters()
    
    # Initialize validation result
    validation = {
        "valid": True,
        "issues": []
    }
    
    # Check each wizard parameter against main.py parameters
    for param_name, param_value in self.params.items():
        # Skip None/empty values
        if param_value is None or (isinstance(param_value, str) and not param_value):
            continue
        
        # Convert wizard parameter name to main.py parameter name
        main_param_name = param_name.replace("_", "-")
        
        # Check if the parameter exists in main.py
        if main_param_name not in main_params:
            # Some parameters are handled specially
            if param_name in ["specific_templates", "load_state"]:
                continue
            
            validation["valid"] = False
            validation["issues"].append(f"Parameter '{param_name}' does not exist in main.py")
            continue
        
        # Get main.py parameter details
        main_param = main_params[main_param_name]
        
        # Validate based on parameter type
        if main_param["type"] == "choice" and param_value not in main_param.get("choices", []):
            validation["valid"] = False
            validation["issues"].append(
                f"Invalid value '{param_value}' for parameter '{param_name}'. "
                f"Valid choices: {', '.join(main_param.get('choices', []))}"
            )
    
    # Validate parameter dependencies
    if self.params["analyze_results"] and not self.params["generate_reports"]:
        validation["valid"] = False
        validation["issues"].append("'analyze_results' requires 'generate_reports' to be enabled")
    
    return validation
```

### 3. Update Command Generation with Validated Parameters

Update the `generate_command` method to use the validated parameters:

```python
def generate_command(self) -> str:
    """Generate the ISEE command based on user selections.
    
    Returns:
        The generated command string.
    """
    # Validate parameters first
    validation = self._validate_parameters()
    if not validation["valid"]:
        if RICH_AVAILABLE:
            self.console.print("[yellow]Warning: Command has validation issues:[/yellow]")
            for issue in validation["issues"]:
                self.console.print(f"[yellow]- {issue}[/yellow]")
        else:
            print("Warning: Command has validation issues:")
            for issue in validation["issues"]:
                print(f"- {issue}")
    
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
    
    # Continue with rest of the command generation...
```

### 4. Add Help Option Information

Add method to display help information about parameters:

```python
def _show_help_options(self) -> None:
    """Show help information about available command-line options."""
    help_info = [
        {
            "name": "--help",
            "description": "Show the help message and exit",
            "usage": "python main.py --help"
        },
        {
            "name": "--list-domains",
            "description": "List all available domains and exit",
            "usage": "python main.py --list-domains"
        },
        {
            "name": "--quick",
            "description": "Run in quick mode (stratified sampling with 36 combinations)",
            "usage": "python main.py --quick --query \"Your query here\""
        },
        {
            "name": "--full",
            "description": "Run in full mode (exhaustive combinations)",
            "usage": "python main.py --full --query \"Your query here\""
        }
    ]
    
    if RICH_AVAILABLE:
        self.console.print("\n[bold cyan]Additional Command-Line Options[/bold cyan]")
        
        options_table = Table(title="Helpful Options")
        options_table.add_column("Option", style="green")
        options_table.add_column("Description", style="cyan")
        options_table.add_column("Example", style="yellow")
        
        for option in help_info:
            options_table.add_row(option["name"], option["description"], option["usage"])
        
        self.console.print(options_table)
    else:
        print("\nAdditional Command-Line Options:")
        for option in help_info:
            print(f"{option['name']}: {option['description']}")
            print(f"  Example: {option['usage']}")
            print()
```

### 5. Add Support for Additional Parameters

Add support for parameters missing from the wizard but available in main.py:

```python
def configure_advanced_options(self) -> None:
    """Configure advanced options not covered by other steps."""
    if RICH_AVAILABLE:
        self.console.print("\n[bold cyan]Advanced Options[/bold cyan]")
        
        # Domain config
        use_domain_config = Confirm.ask(
            "Would you like to use a domain-specific configuration file?",
            default=False
        )
        
        if use_domain_config:
            domain_config_files = [f for f in os.listdir() if f.endswith('.json') and 'domain' in f.lower()]
            if domain_config_files:
                self.console.print("Available domain configuration files:")
                for i, file in enumerate(domain_config_files, 1):
                    self.console.print(f"{i}. {file}")
                
                domain_config_choice = IntPrompt.ask(
                    "Select a domain configuration file by number (or 0 to skip)",
                    default=0
                )
                
                if domain_config_choice > 0 and domain_config_choice <= len(domain_config_files):
                    self.params["domain_config"] = domain_config_files[domain_config_choice - 1]
            else:
                self.console.print("[yellow]No domain configuration files found.[/yellow]")
        
        # Report format
        if self.params["generate_reports"]:
            report_format_choices = ["markdown", "json"]
            report_format_index = IntPrompt.ask(
                "Select report format (1=markdown, 2=json)",
                default=1
            )
            if 1 <= report_format_index <= len(report_format_choices):
                self.params["report_format"] = report_format_choices[report_format_index - 1]
        
        # Export CSV
        if self.params["generate_reports"]:
            export_csv = Confirm.ask(
                "Export data as CSV files for analysis?",
                default=False
            )
            self.params["export_csv"] = export_csv
        
        # No visualizations
        if self.params["analyze_results"]:
            no_visualizations = Confirm.ask(
                "Skip generating visualization charts?",
                default=False
            )
            self.params["no_visualizations"] = no_visualizations
        
        # Quick/Full mode
        use_preset = Confirm.ask(
            "Use a preset running mode (quick or full)?",
            default=False
        )
        
        if use_preset:
            preset_choices = ["quick", "full"]
            preset_names = ["Quick mode (stratified sampling with 36 combinations)", 
                           "Full mode (exhaustive combinations)"]
            
            self.console.print("Available presets:")
            for i, (preset, desc) in enumerate(zip(preset_choices, preset_names), 1):
                self.console.print(f"{i}. {desc}")
            
            preset_choice = IntPrompt.ask(
                "Select a preset by number",
                default=1
            )
            
            if 1 <= preset_choice <= len(preset_choices):
                preset = preset_choices[preset_choice - 1]
                self.params[preset] = True
                
                # Update related parameters based on the preset
                if preset == "quick":
                    self.params["sampling_method"] = "stratified"
                    self.params["max_combinations"] = 36
                elif preset == "full":
                    self.params["sampling_method"] = "exhaustive"
                    self.params["max_combinations"] = None
    else:
        # Plain text version...
        # Similar implementation for non-rich UI
```

### 6. Add Parameter Dependencies Handling

Update the wizard flow to handle parameter dependencies:

```python
def configure_output(self) -> Tuple[str, Optional[str], bool, bool]:
    """Configure output parameters.
    
    Returns:
        Tuple of (output_format, output_file, generate_reports, analyze_results)
    """
    # ... existing implementation ...
    
    # Analyze results
    analyze_results = False
    if generate_reports:
        if RICH_AVAILABLE:
            analyze_results = Confirm.ask(
                "Perform analysis with visualizations?",
                default=True
            )
        else:
            analyze_results_input = input("Perform analysis with visualizations? (y/n) [y]: ").lower()
            analyze_results = analyze_results_input in ["", "y", "yes"]
    elif RICH_AVAILABLE and analyze_results:
        # If user tries to enable analysis without reports
        self.console.print("[yellow]Note: Analysis requires reports to be generated. Enabling reports.[/yellow]")
        generate_reports = True
    
    # ... rest of the implementation ...
```

## Update Wizard Flow

Update the `run_wizard` method to incorporate the new parameter validation and help options:

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
    
    # Configure cognitive diversity
    _, _, _ = self.configure_cognitive_diversity()
    
    # Configure execution parameters
    self.configure_execution()
    
    # Configure output options
    self.configure_output()
    
    # Configure execution mode
    self.configure_execution_mode()
    
    # Configure advanced options
    self.configure_advanced_options()
    
    # Validate parameters
    validation = self._validate_parameters()
    if not validation["valid"]:
        if RICH_AVAILABLE:
            self.console.print("\n[bold red]Parameter Validation Issues:[/bold red]")
            for issue in validation["issues"]:
                self.console.print(f"[red]- {issue}[/red]")
            
            self.console.print("[yellow]The command may not work as expected. Would you like to continue anyway?[/yellow]")
            continue_anyway = Confirm.ask("Continue anyway?", default=False)
            if not continue_anyway:
                if RICH_AVAILABLE:
                    self.console.print("[red]Wizard aborted.[/red]")
                else:
                    print("Wizard aborted.")
                return
        else:
            print("\nParameter Validation Issues:")
            for issue in validation["issues"]:
                print(f"- {issue}")
            
            print("The command may not work as expected. Would you like to continue anyway?")
            continue_input = input("Continue anyway? (y/n) [n]: ").lower()
            continue_anyway = continue_input in ["y", "yes"]
            if not continue_anyway:
                print("Wizard aborted.")
                return
    
    # Generate and preview the command
    command = self.generate_command()
    self.preview_command(command)
    
    # Show additional help options
    self._show_help_options()
    
    # Copy to clipboard if possible
    clipboard_success = self.copy_to_clipboard(command)
    
    if clipboard_success and RICH_AVAILABLE:
        self.console.print("\n[green]Command copied to clipboard![/green]")
    elif clipboard_success:
        print("\nCommand copied to clipboard!")
    
    # Execute the command if requested
    self.execute_command(command)
```

## Testing Strategy

1. Test parameter extraction from main.py
2. Test parameter validation with valid and invalid parameters
3. Test parameter dependencies handling
4. Test integration of help options
5. Test advanced parameter configuration

## Benefits

1. Better alignment with main.py's command-line parameters
2. Improved validation to prevent invalid commands
3. More comprehensive parameter support
4. Better guidance for users on available options