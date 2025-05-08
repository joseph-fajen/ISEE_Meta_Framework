# Template Selection Implementation Plan

## Overview

The current Command Wizard allows users to select specific templates but doesn't properly pass these selections to the `main.py` command. This implementation plan outlines the changes needed to fully support specific template selection.

## Current State Analysis

1. **In command_wizard.py**:
   - The Command Wizard allows selection of specific templates in the `configure_cognitive_diversity` method (lines 486-640)
   - Selected template IDs are stored in `self.params["specific_templates"]` (line 638)
   - When generating the command in `generate_command`, only a comment is added (lines 1052-1055):
     ```python
     if self.params.get("specific_templates"):
         self.specific_templates_comment = f"# Selected templates: {','.join(self.params['specific_templates'])}"
     else:
         self.specific_templates_comment = None
     ```
   - These selected templates are not actually added to the command with a parameter

2. **In main.py**:
   - The `main.py` script has a parameter `--instruction-templates` that accepts a comma-separated list of template IDs
   - This parameter overrides the `--instructions` count parameter

3. **In instruction_templates.py**:
   - A TemplateLibrary class manages all available templates
   - Each template has an ID (e.g., "ins_analytical", "ins_creative")
   - The `create_default_library()` function creates 10 default templates

## Implementation Tasks

1. **Update the `generate_command` Method**:
   - Modify the method to convert specific template IDs to a comma-separated string
   - Add the `--instruction-templates` parameter to the command when specific templates are selected
   - Remove the existing commenting mechanism (which is only for display purposes)

2. **Enhance the Command Preview**:
   - Update the command explanation to display the selected template names (not just IDs)
   - Provide more context about what each selected template specializes in

3. **Add Validation**:
   - Ensure selected template IDs exist in the template library
   - Validate that at least one template is selected when using specific templates

## Implementation Details

### Command Generation Logic

```python
# In generate_command method
if self.params.get("specific_templates"):
    # Convert template IDs to comma-separated string
    template_ids = ','.join(self.params["specific_templates"])
    cmd_parts.append(f'--instruction-templates "{template_ids}"')
else:
    # Just use the count parameter since specific templates aren't selected
    cmd_parts.append(f'--instructions {self.params["instructions"]}')
```

### Command Preview Enhancement

```python
# In preview_command method
if self.params.get("specific_templates"):
    # Get template names for display
    template_names = []
    for template_id in self.params["specific_templates"]:
        try:
            template = self.template_library.get_template(template_id)
            template_names.append(f"{template.name} ({template.metadata.get('strength', 'N/A')})")
        except KeyError:
            template_names.append(f"{template_id} (unknown)")
    
    command_summary += f"- Use {len(template_names)} specific cognitive approaches:\n"
    for name in template_names:
        command_summary += f"  - {name}\n"
else:
    command_summary += f"- Apply {self.params['instructions']} different cognitive approaches\n"
```

### Validation Logic

```python
# In _validate_parameters method
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
        validation["issues"].append("At least one template must be selected when using specific templates")
```

## Testing Plan

1. **Template Selection Test**:
   - Test selecting specific templates through the Command Wizard UI
   - Verify selected templates appear in the generated command
   - Check command explanation shows template names and strengths

2. **Command Execution Test**:
   - Execute commands with specific templates
   - Verify main.py correctly uses only the specified templates

3. **Validation Test**:
   - Test validation of invalid template IDs
   - Test validation of empty template selection

## User Experience Improvements

1. **Better Template Descriptions**:
   - Show template strengths in the selection UI
   - Add examples of when to use different templates

2. **Template Grouping**:
   - Optionally group templates by cognitive style for easier selection

3. **Summary Preview**:
   - After selection, show a summary of selected templates with descriptions

## Next Steps

After implementing this feature, we'll need to:

1. Update the command_wizard.py documentation to explain the template selection feature
2. Create examples showing how to use specific templates
3. Add tests to verify the functionality