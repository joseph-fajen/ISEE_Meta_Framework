#!/usr/bin/env python3
"""
Template Selection Implementation for Command Wizard (Phase 3)

This module implements proper template selection in the Command Wizard, allowing
users to select specific templates and pass them correctly to the main.py command.
"""

import os
import sys
import re
from typing import List, Dict, Any, Optional, Tuple

# Add parent directory to path to allow importing from the main project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import required modules from the main project
from instruction_templates import TemplateLibrary, create_default_library


def get_template_display_info(template_ids: List[str]) -> List[Dict[str, str]]:
    """Get display information for the specified templates.
    
    Args:
        template_ids: List of template IDs.
        
    Returns:
        List of dictionaries with template display information.
    """
    # Create a template library to look up template information
    template_library = create_default_library()
    
    # Get display information for each template
    template_info = []
    for template_id in template_ids:
        try:
            template = template_library.get_template(template_id)
            template_info.append({
                "id": template_id,
                "name": template.name,
                "strength": template.metadata.get("strength", "Not specified"),
                "style": template.metadata.get("cognitive_style", "Not specified")
            })
        except KeyError:
            # Handle unknown template IDs
            template_info.append({
                "id": template_id,
                "name": f"Unknown template ({template_id})",
                "strength": "Unknown",
                "style": "Unknown"
            })
    
    return template_info


def update_generate_command(file_content: str) -> str:
    """Update the generate_command method to properly handle specific templates.
    
    Args:
        file_content: Original file content.
        
    Returns:
        Updated file content.
    """
    # Find the section in generate_command where instruction parameters are added
    pattern = r"""# Add instruction parameters
.*?# Just use the count parameter since --instruction-templates isn't supported yet
.*?cmd_parts\.append\(f'--instructions \{self\.params\["instructions"\]\}'\)

.*?# Store the specific templates in a comment that appears in the command preview
.*?# but doesn't get executed \(for future implementation\)
.*?if self\.params\.get\("specific_templates"\):
.*?self\.specific_templates_comment = f"# Selected templates: \{','.join\(self\.params\['specific_templates'\]\)\}"
.*?else:
.*?self\.specific_templates_comment = None"""
    
    # Create the replacement code
    replacement = """# Add instruction parameters
        if self.params.get("specific_templates"):
            # Convert template IDs to comma-separated string and use --instruction-templates parameter
            template_ids = ','.join(self.params["specific_templates"])
            cmd_parts.append(f'--instruction-templates "{template_ids}"')
        else:
            # Just use the count parameter since specific templates aren't selected
            cmd_parts.append(f'--instructions {self.params["instructions"]}')"""
    
    # Replace the existing implementation with the new one
    updated_content = re.sub(pattern, replacement, file_content, flags=re.DOTALL)
    
    return updated_content


def update_preview_command(file_content: str) -> str:
    """Update the preview_command method to show template information.
    
    Args:
        file_content: Original file content.
        
    Returns:
        Updated file content.
    """
    # Find the section in preview_command where cognitive diversity is explained
    pattern = r"""# Cognitive diversity
.*?if self\.params\.get\("specific_templates"\):
.*?instruction_count = len\(self\.params\["specific_templates"\]\)
.*?command_summary \+= f"- Apply \{instruction_count\} specific cognitive approaches \(user-selected\)\\n"
.*?else:
.*?command_summary \+= f"- Apply \{self\.params\['instructions'\]\} different cognitive approaches\\n"
.*?command_summary \+= f"- Generate \{self\.params\['variations'\]\} variations of your query\\n"""
    
    # Create the replacement code
    replacement = """# Cognitive diversity
            if self.params.get("specific_templates"):
                # Get template names and information for display
                template_info = []
                for template_id in self.params["specific_templates"]:
                    try:
                        template = self.template_library.get_template(template_id)
                        template_info.append({
                            "name": template.name,
                            "strength": template.metadata.get("strength", "Not specified")
                        })
                    except KeyError:
                        template_info.append({
                            "name": f"Unknown template ({template_id})",
                            "strength": "Unknown"
                        })
                
                # Show detailed information about the selected templates
                instruction_count = len(self.params["specific_templates"])
                command_summary += f"- Apply {instruction_count} specific cognitive approaches:\\n"
                for info in template_info:
                    command_summary += f"  - {info['name']} (Strength: {info['strength']})\\n"
            else:
                command_summary += f"- Apply {self.params['instructions']} different cognitive approaches\\n"
            command_summary += f"- Generate {self.params['variations']} variations of your query\\n"""
    
    # Replace the existing implementation with the new one
    updated_content = re.sub(pattern, replacement, file_content, flags=re.DOTALL)
    
    return updated_content


def update_validation_method(file_content: str) -> str:
    """Update the _validate_parameters method to validate template selections.
    
    Args:
        file_content: Original file content.
        
    Returns:
        Updated file content.
    """
    # Find the validation method
    validation_pattern = r"""def _validate_parameters\(self\) -> Dict\[str, Any\]:
        \"\"\"Validate wizard parameters against main\.py parameters\.
        
        Returns:
            Dictionary with validation results\.
        \"\"\"
        # Extract main\.py parameters
        main_params = self\._extract_main_parameters\(\)
        
        # Initialize validation result
        validation = {
            "valid": True,
            "issues": \[\]
        }"""
    
    # Add template validation logic
    template_validation = """def _validate_parameters(self) -> Dict[str, Any]:
        \"\"\"Validate wizard parameters against main.py parameters.
        
        Returns:
            Dictionary with validation results.
        \"\"\"
        # Extract main.py parameters
        main_params = self._extract_main_parameters()
        
        # Initialize validation result
        validation = {
            "valid": True,
            "issues": []
        }
        
        # Validate template selections if specific templates are used
        if self.params.get("specific_templates"):
            # Check that templates exist
            invalid_templates = []
            for template_id in self.params["specific_templates"]:
                try:
                    self.template_library.get_template(template_id)
                except KeyError:
                    invalid_templates.append(template_id)
            
            if invalid_templates:
                validation["valid"] = False
                validation["issues"].append(
                    f"Invalid template IDs: {', '.join(invalid_templates)}"
                )
            
            # Check that at least one template is selected
            if not self.params["specific_templates"]:
                validation["valid"] = False
                validation["issues"].append("At least one template must be selected when using specific templates")"""
    
    # Replace the existing implementation with the new one
    updated_content = re.sub(validation_pattern, template_validation, file_content, flags=re.DOTALL)
    
    return updated_content


def enhance_template_selection_ui(file_content: str) -> str:
    """Enhance the template selection UI to provide more information.
    
    Args:
        file_content: Original file content.
        
    Returns:
        Updated file content.
    """
    # Find the templates table in the configure_cognitive_diversity method
    templates_table_pattern = r"""templates_table = Table\(title="Available Cognitive Approaches"\)
            templates_table\.add_column\("#", style="green"\)
            templates_table\.add_column\("Approach", style="cyan"\)
            templates_table\.add_column\("Description"\)
            
            for i, template in enumerate\(templates, 1\):
                templates_table\.add_row\(
                    str\(i\),
                    template\.name, 
                    f"\{template\.metadata\.get\('strength', 'N/A'\)\}"
                \)"""
    
    # Create enhanced templates table with more columns
    enhanced_templates_table = """templates_table = Table(title="Available Cognitive Approaches")
            templates_table.add_column("#", style="green")
            templates_table.add_column("Approach", style="cyan")
            templates_table.add_column("Strength")
            templates_table.add_column("Style")
            templates_table.add_column("ID", style="dim")
            
            for i, template in enumerate(templates, 1):
                templates_table.add_row(
                    str(i),
                    template.name, 
                    f"{template.metadata.get('strength', 'N/A')}",
                    f"{template.metadata.get('cognitive_style', 'N/A')}",
                    template.id
                )"""
    
    # Replace the existing implementation with the new one
    updated_content = re.sub(templates_table_pattern, enhanced_templates_table, file_content, flags=re.DOTALL)
    
    # For non-rich mode, enhance the template display too
    non_rich_pattern = r"""for i, \(name, template\) in enumerate\(zip\(template_names, templates\), 1\):
                print\(f"\{i\}\. \{name\} \(\{template\.metadata\.get\('strength', 'N/A'\)\}\)"\)"""
    
    enhanced_non_rich = """for i, (name, template) in enumerate(zip(template_names, templates), 1):
                print(f"{i}. {name}")
                print(f"   Strength: {template.metadata.get('strength', 'N/A')}")
                print(f"   Style: {template.metadata.get('cognitive_style', 'N/A')}")
                print(f"   ID: {template.id}")"""
    
    updated_content = re.sub(non_rich_pattern, enhanced_non_rich, updated_content, flags=re.DOTALL)
    
    return updated_content


def apply_template_selection_improvements(file_path: str) -> None:
    """Apply all template selection improvements to the command_wizard.py file.
    
    Args:
        file_path: Path to the command_wizard.py file.
    """
    # Read the original file content
    with open(file_path, 'r') as f:
        file_content = f.read()
    
    # Make a backup of the original file
    backup_path = file_path + '.phase3.backup'
    with open(backup_path, 'w') as f:
        f.write(file_content)
    print(f"Created backup of command_wizard.py at {backup_path}")
    
    # Apply each improvement
    file_content = update_generate_command(file_content)
    file_content = update_preview_command(file_content)
    file_content = update_validation_method(file_content)
    file_content = enhance_template_selection_ui(file_content)
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(file_content)
    
    print(f"Applied template selection improvements to {file_path}")


if __name__ == "__main__":
    # Get the path to command_wizard.py
    command_wizard_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../command_wizard.py'))
    
    # Apply the improvements
    apply_template_selection_improvements(command_wizard_path)