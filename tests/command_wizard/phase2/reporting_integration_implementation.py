#!/usr/bin/env python3
"""
ISEE Command Wizard Reporting Integration Implementation

Implementation of improved reporting integration for the ISEE Command Wizard.
This file will be used to update the command_wizard.py with better reporting features.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Add path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

def get_timestamped_output_dir() -> str:
    """Generate a timestamped output directory path.
    
    Returns:
        Path to the timestamped output directory.
    """
    # Match the format used in main.py
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join("data", "output", f"run_{timestamp}")


def choose_output_directory() -> Optional[str]:
    """Allow the user to choose an output directory.
    
    Returns:
        Selected output directory or None to use the default.
    """
    # Default directory
    default_dir = get_timestamped_output_dir()
    
    # In a real implementation, this would ask the user to select a directory
    # For this simulation, return the default directory
    return default_dir


def select_report_format() -> str:
    """Allow the user to select the report format.
    
    Returns:
        Selected report format.
    """
    formats = ["markdown", "json"]
    
    # In a real implementation, this would ask the user to select a format
    # For this simulation, return the default format
    return formats[0]  # Default to markdown


def configure_visualization_options() -> Tuple[bool, bool]:
    """Configure visualization options.
    
    Returns:
        Tuple of (export_csv, no_visualizations).
    """
    # In a real implementation, this would ask the user to configure options
    # For this simulation, return default values
    export_csv = True
    no_visualizations = False
    
    return export_csv, no_visualizations


def configure_output(params: Dict[str, Any], rich_available: bool) -> Dict[str, Any]:
    """Configure output parameters.
    
    Args:
        params: Current wizard parameters.
        rich_available: Whether Rich formatting is available.
        
    Returns:
        Updated parameters.
    """
    output_params = params.copy()
    
    # Set output format (default to markdown)
    output_params["output_format"] = "markdown"
    
    # Set output file (optional)
    output_params["output_file"] = "isee_results.md"
    
    # Set output directory
    output_dir = choose_output_directory()
    if output_dir:
        output_params["output_directory"] = output_dir
    
    # Set reporting options
    output_params["generate_reports"] = True
    
    # Set report format
    if output_params["generate_reports"]:
        output_params["report_format"] = select_report_format()
    
    # Set analysis options
    output_params["analyze_results"] = True
    
    # Set visualization options
    if output_params["analyze_results"]:
        export_csv, no_visualizations = configure_visualization_options()
        output_params["export_csv"] = export_csv
        output_params["no_visualizations"] = no_visualizations
    
    return output_params


def get_reporting_explanation(params: Dict[str, Any], rich_available: bool) -> str:
    """Get explanation text for reporting options.
    
    Args:
        params: Wizard parameters.
        rich_available: Whether Rich formatting is available.
        
    Returns:
        Explanation text.
    """
    explanation = ""
    
    # Add output directory explanation
    if params.get("output_directory"):
        explanation += f"- Save all outputs to the directory: {params['output_directory']}\n"
    else:
        explanation += f"- Save all outputs to a timestamped directory (e.g., data/output/run_20230101_120000)\n"
    
    # Add output format and file explanation
    explanation += f"- Generate main output in {params['output_format']} format\n"
    
    if params.get("output_file"):
        explanation += f"- Save main output to {params['output_file']}\n"
    else:
        explanation += "- Save main output to an automatically generated file\n"
    
    # Add reporting explanation
    if params.get("generate_reports"):
        report_format = params.get("report_format", "markdown")
        explanation += f"- Generate detailed reports in {report_format} format\n"
        explanation += "  Including: combination details, results, model performance, template effectiveness\n"
        
        if params.get("analyze_results"):
            explanation += "- Perform analysis with the following outputs:\n"
            
            if not params.get("no_visualizations", False):
                explanation += "  - Visualization charts (performance comparisons, effectiveness metrics)\n"
            
            if params.get("export_csv", False):
                explanation += "  - CSV data files for further analysis\n"
            
            explanation += "  - Analysis summary report\n"
    
    if rich_available:
        # In a real implementation, we would add rich formatting here
        pass
    
    return explanation


def generate_command_with_reporting(params: Dict[str, Any]) -> str:
    """Generate command with reporting options.
    
    Args:
        params: Wizard parameters.
        
    Returns:
        Command with reporting options.
    """
    cmd_parts = ["python main.py"]
    
    # Add basic parameters
    if params.get("query"):
        cmd_parts.append(f'--query "{params["query"]}"')
    
    # Add output format
    if params.get("output_format"):
        cmd_parts.append(f'--output-format {params["output_format"]}')
    
    # Add output file if specified
    if params.get("output_file"):
        cmd_parts.append(f'--output-file "{params["output_file"]}"')
    
    # Add output directory if specified
    if params.get("output_directory"):
        cmd_parts.append(f'--output-directory "{params["output_directory"]}"')
    
    # Add reporting parameters
    if params.get("generate_reports"):
        cmd_parts.append("--generate-reports")
        
        # Add report format if specified
        if params.get("report_format"):
            cmd_parts.append(f'--report-format {params["report_format"]}')
    
    if params.get("analyze_results"):
        cmd_parts.append("--analyze-results")
        
        # Add export CSV if specified
        if params.get("export_csv"):
            cmd_parts.append("--export-csv")
        
        # Add no visualizations if specified
        if params.get("no_visualizations"):
            cmd_parts.append("--no-visualizations")
    
    # Return the command
    return " ".join(cmd_parts)


def update_command_wizard_with_reporting_improvements():
    """Update CommandWizard with reporting improvements.
    
    This function lists all the changes needed in command_wizard.py to
    implement the improved reporting integration.
    """
    changes = [
        {
            "method": "CommandWizard._get_timestamped_output_dir",
            "implementation": get_timestamped_output_dir,
            "description": "Add method to generate timestamped output directory"
        },
        {
            "method": "CommandWizard._choose_output_directory",
            "implementation": choose_output_directory,
            "description": "Add method to select output directory"
        },
        {
            "method": "CommandWizard._select_report_format",
            "implementation": select_report_format,
            "description": "Add method to select report format"
        },
        {
            "method": "CommandWizard._configure_visualization_options",
            "implementation": configure_visualization_options,
            "description": "Add method to configure visualization options"
        },
        {
            "method": "CommandWizard.configure_output",
            "change": "Update to include comprehensive reporting options",
            "description": "Update to include comprehensive reporting options"
        },
        {
            "method": "CommandWizard.generate_command",
            "change": "Update to include reporting parameters",
            "description": "Update to include all reporting parameters"
        },
        {
            "method": "CommandWizard.preview_command",
            "change": "Enhance reporting explanation",
            "description": "Add better explanation of reporting options"
        }
    ]
    
    return changes


if __name__ == "__main__":
    # Example usage to test the implementation
    output_dir = get_timestamped_output_dir()
    print(f"Timestamped output directory: {output_dir}")
    
    # Test report format selection
    report_format = select_report_format()
    print(f"Selected report format: {report_format}")
    
    # Test visualization options
    export_csv, no_visualizations = configure_visualization_options()
    print(f"Export CSV: {export_csv}")
    print(f"No visualizations: {no_visualizations}")
    
    # Test output configuration
    params = {
        "query": "How might we improve urban transportation?",
    }
    
    output_params = configure_output(params, False)
    print(f"\nOutput parameters: {output_params}")
    
    # Test reporting explanation
    explanation = get_reporting_explanation(output_params, False)
    print(f"\nReporting explanation:\n{explanation}")
    
    # Test command generation
    command = generate_command_with_reporting(output_params)
    print(f"\nGenerated command:\n{command}")