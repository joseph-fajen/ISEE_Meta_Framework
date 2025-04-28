# Reporting Integration Implementation Plan

This document outlines the changes needed to improve the Command Wizard's integration with the ISEE framework's reporting and analysis subsystems.

## Current Issues

1. **Output Directory Structure**: The wizard doesn't reflect the newer run-specific directory structure in `main.py`.
2. **Report Format Options**: The wizard allows enabling reporting but doesn't offer options for different report formats.
3. **Visualization Options**: There are no options for customizing visualizations or CSV export.
4. **Reporting Explanation**: The explanation of what reports and visualizations will be generated is limited.

## Implementation Plan

### 1. Add Timestamped Output Directory Support

Add support for the run-specific directory structure used in main.py:

```python
def _get_timestamped_output_dir(self) -> str:
    """Generate a timestamped output directory path.
    
    Returns:
        Path to the timestamped output directory.
    """
    # Match the format used in main.py
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join("data", "output", f"run_{timestamp}")
```

### 2. Add Custom Output Directory Selection

Add a method to allow selecting a custom output directory:

```python
def _choose_output_directory(self) -> Optional[str]:
    """Allow the user to choose an output directory.
    
    Returns:
        Selected output directory or None to use the default.
    """
    if RICH_AVAILABLE:
        self.console.print("\n[bold cyan]Output Directory[/bold cyan]")
        
        # Show the default directory
        default_dir = self._get_timestamped_output_dir()
        self.console.print(f"Default directory: [green]{default_dir}[/green]")
        
        # Ask if the user wants to specify a custom directory
        use_custom_dir = Confirm.ask(
            "Would you like to specify a custom output directory?",
            default=False
        )
        
        if not use_custom_dir:
            return None
        
        # Get the custom directory
        custom_dir = Prompt.ask(
            "Enter custom output directory",
            default="data/output/custom"
        )
        
        # Validate the directory
        if not os.path.exists(os.path.dirname(custom_dir)):
            self.console.print(f"[yellow]Warning: Parent directory '{os.path.dirname(custom_dir)}' does not exist. It will be created if you proceed.[/yellow]")
            create_dir = Confirm.ask(
                "Create directory?",
                default=True
            )
            if create_dir:
                return custom_dir
            else:
                return None
        
        return custom_dir
    else:
        print("\nOutput Directory")
        
        # Show the default directory
        default_dir = self._get_timestamped_output_dir()
        print(f"Default directory: {default_dir}")
        
        # Ask if the user wants to specify a custom directory
        use_custom_dir_input = input("Would you like to specify a custom output directory? (y/n) [n]: ").lower()
        use_custom_dir = use_custom_dir_input in ["y", "yes"]
        
        if not use_custom_dir:
            return None
        
        # Get the custom directory
        custom_dir_input = input("Enter custom output directory [data/output/custom]: ")
        custom_dir = custom_dir_input if custom_dir_input else "data/output/custom"
        
        # Validate the directory
        if not os.path.exists(os.path.dirname(custom_dir)):
            print(f"Warning: Parent directory '{os.path.dirname(custom_dir)}' does not exist. It will be created if you proceed.")
            create_dir_input = input("Create directory? (y/n) [y]: ").lower()
            create_dir = create_dir_input in ["", "y", "yes"]
            if create_dir:
                return custom_dir
            else:
                return None
        
        return custom_dir
```

### 3. Add Report Format Selection

Add method to select the report format:

```python
def _select_report_format(self) -> str:
    """Allow the user to select the report format.
    
    Returns:
        Selected report format.
    """
    formats = ["markdown", "json"]
    
    if RICH_AVAILABLE:
        self.console.print("\n[bold cyan]Report Format[/bold cyan]")
        
        # Show available formats
        self.console.print("Available formats:")
        for i, format_name in enumerate(formats, 1):
            self.console.print(f"{i}. {format_name}")
        
        # Get the selection
        format_choice = IntPrompt.ask(
            "Select report format",
            default=1,
            show_default=True
        )
        
        if 1 <= format_choice <= len(formats):
            return formats[format_choice - 1]
        else:
            return formats[0]  # Default to first format
    else:
        print("\nReport Format")
        
        # Show available formats
        print("Available formats:")
        for i, format_name in enumerate(formats, 1):
            print(f"{i}. {format_name}")
        
        # Get the selection
        format_choice_input = input("Select report format [1]: ")
        
        try:
            format_choice = int(format_choice_input) if format_choice_input else 1
            if 1 <= format_choice <= len(formats):
                return formats[format_choice - 1]
            else:
                return formats[0]  # Default to first format
        except ValueError:
            return formats[0]  # Default to first format
```

### 4. Add Visualization Options

Add methods to configure visualization and export options:

```python
def _configure_visualization_options(self) -> Tuple[bool, bool]:
    """Configure visualization options.
    
    Returns:
        Tuple of (export_csv, no_visualizations).
    """
    if RICH_AVAILABLE:
        self.console.print("\n[bold cyan]Visualization Options[/bold cyan]")
        
        # Export CSV option
        export_csv = Confirm.ask(
            "Export data as CSV files for analysis?",
            default=True
        )
        
        # No visualizations option
        no_visualizations = Confirm.ask(
            "Skip generating visualization charts?",
            default=False
        )
        
        # If no visualizations, explain what will be skipped
        if no_visualizations:
            self.console.print("[dim]Visualization charts like model performance comparison, template effectiveness, and diversity analysis will be skipped.[/dim]")
    else:
        print("\nVisualization Options")
        
        # Export CSV option
        export_csv_input = input("Export data as CSV files for analysis? (y/n) [y]: ").lower()
        export_csv = export_csv_input in ["", "y", "yes"]
        
        # No visualizations option
        no_viz_input = input("Skip generating visualization charts? (y/n) [n]: ").lower()
        no_visualizations = no_viz_input in ["y", "yes"]
        
        # If no visualizations, explain what will be skipped
        if no_visualizations:
            print("Visualization charts like model performance comparison, template effectiveness, and diversity analysis will be skipped.")
    
    return export_csv, no_visualizations
```

### 5. Update Configure Output to Include Reporting Options

Update the `configure_output` method to include comprehensive reporting options:

```python
def configure_output(self) -> Dict[str, Any]:
    """Configure output parameters.
    
    Returns:
        Dictionary of output parameters.
    """
    output_params = {}
    
    if RICH_AVAILABLE:
        self.console.print("\n[bold cyan]Step 6: Configure Output Options[/bold cyan]")
        
        # Output format selection
        output_formats = {
            "1": "markdown",
            "2": "json"
        }
        
        self.console.print("\nOutput Formats:")
        for key, value in output_formats.items():
            self.console.print(f"  {key}. {value}")
        
        format_choice = Prompt.ask(
            "Select output format",
            choices=["1", "2"],
            default="1"
        )
        output_format = output_formats[format_choice]
        output_params["output_format"] = output_format
        
        # Output file
        use_custom_file = Confirm.ask(
            "Would you like to specify an output filename?",
            default=False
        )
        
        output_file = None
        if use_custom_file:
            extension = "md" if output_format == "markdown" else "json"
            output_file = Prompt.ask(
                "Enter output filename",
                default=f"isee_results.{extension}"
            )
            output_params["output_file"] = output_file
        
        # Output directory
        output_dir = self._choose_output_directory()
        if output_dir:
            output_params["output_directory"] = output_dir
        
        # Generate reports
        generate_reports = Confirm.ask(
            "Generate detailed reports?",
            default=True
        )
        output_params["generate_reports"] = generate_reports
        
        # Report format (if generating reports)
        if generate_reports:
            report_format = self._select_report_format()
            output_params["report_format"] = report_format
        
        # Analyze results
        analyze_results = False
        if generate_reports:
            analyze_results = Confirm.ask(
                "Perform analysis with visualizations?",
                default=True
            )
            output_params["analyze_results"] = analyze_results
            
            # Visualization options (if analyzing results)
            if analyze_results:
                export_csv, no_visualizations = self._configure_visualization_options()
                output_params["export_csv"] = export_csv
                output_params["no_visualizations"] = no_visualizations
    else:
        # Plain text interface implementation
        # Similar to the Rich interface but using regular input/print
    
    # Update the wizard parameters
    self.params.update(output_params)
    
    return output_params
```

### 6. Update Generate Command to Include Reporting Parameters

Update the `generate_command` method to include all reporting parameters:

```python
def generate_command(self) -> str:
    """Generate the ISEE command based on user selections.
    
    Returns:
        The generated command string.
    """
    cmd_parts = ["python main.py"]
    
    # ... existing code ...
    
    # Add reporting parameters
    if self.params["generate_reports"]:
        cmd_parts.append("--generate-reports")
        
        # Add report format if specified
        if self.params.get("report_format"):
            cmd_parts.append(f'--report-format {self.params["report_format"]}')
    
    if self.params["analyze_results"]:
        cmd_parts.append("--analyze-results")
        
        # Add export CSV if specified
        if self.params.get("export_csv"):
            cmd_parts.append("--export-csv")
        
        # Add no visualizations if specified
        if self.params.get("no_visualizations"):
            cmd_parts.append("--no-visualizations")
    
    # Add output directory if specified
    if self.params.get("output_directory"):
        cmd_parts.append(f'--output-directory "{self.params["output_directory"]}"')
    
    # ... rest of the method ...
```

### 7. Update Preview Command with Better Reporting Explanation

Enhance the `preview_command` method to better explain reporting and visualization:

```python
def preview_command(self, command: str) -> None:
    """Preview the generated command.
    
    Args:
        command: The generated command string.
    """
    # ... existing code ...
    
    # Explain what the command will do
    command_summary = "This command will:\n"
    
    # ... existing code ...
    
    # Add output directory explanation if specified
    if self.params.get("output_directory"):
        command_summary += f"- Save all outputs to the directory: {self.params['output_directory']}\n"
    else:
        command_summary += f"- Save all outputs to a timestamped directory (e.g., data/output/run_20230101_120000)\n"
    
    # Output format and file
    command_summary += f"- Generate main output in {self.params['output_format']} format\n"
    
    if self.params["output_file"]:
        command_summary += f"- Save main output to {self.params['output_file']}\n"
    else:
        command_summary += "- Save main output to an automatically generated file\n"
    
    # Detailed reporting explanation if enabled
    if self.params["generate_reports"]:
        report_format = self.params.get("report_format", "markdown")
        command_summary += f"- Generate detailed reports in {report_format} format\n"
        command_summary += "  Including: combination details, results, model performance, template effectiveness\n"
        
        if self.params["analyze_results"]:
            command_summary += "- Perform analysis with the following outputs:\n"
            
            if not self.params.get("no_visualizations", False):
                command_summary += "  - Visualization charts (performance comparisons, effectiveness metrics)\n"
            
            if self.params.get("export_csv", False):
                command_summary += "  - CSV data files for further analysis\n"
            
            command_summary += "  - Analysis summary report\n"
    
    # ... rest of the method ...
```

## Testing Strategy

1. Test timestamped output directory generation
2. Test custom output directory selection
3. Test report format selection
4. Test visualization options configuration
5. Test command generation with reporting parameters
6. Test the reporting explanation

## Benefits

1. Better integration with main.py's output directory structure
2. More comprehensive reporting options
3. Clearer explanation of what reports and visualizations will be generated
4. Better customization of analysis and visualization outputs