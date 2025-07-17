# Template Selection Guide for ISEE

## Overview

The ISEE Meta-Framework includes a powerful template selection feature that allows you to control exactly which cognitive approaches are used for your innovation challenges. This guide explains how to use template selection in both the Command Wizard and through direct command-line parameters.

## Available Templates

The ISEE Framework includes the following cognitive approach templates:

| ID | Name | Cognitive Style | Strength |
|----|------|----------------|----------|
| `ins_analytical` | Analytical Framework | analytical | structured reasoning |
| `ins_creative` | Creative Framework | divergent | novel ideation |
| `ins_critical` | Critical Framework | critical | assumption challenging |
| `ins_integrative` | Integrative Framework | integrative | synthesis |
| `ins_pragmatic` | Pragmatic Framework | pragmatic | implementation focus |
| `ins_first_principles` | First Principles Framework | reductive | fundamental analysis |
| `ins_systems` | Systems Thinking Framework | systems | holistic analysis |
| `ins_contrarian` | Contrarian Framework | contrarian | challenging orthodoxy |
| `ins_historical` | Historical Framework | historical | pattern recognition |
| `ins_futurist` | Future-Oriented Framework | futurist | trend extrapolation |

## Using Template Selection in the Command Wizard

The Command Wizard allows you to select specific templates interactively:

1. **Launch the Command Wizard**:
   ```
   python command_wizard.py
   ```

2. **In Step 4 (Configure Cognitive Diversity)**:
   - You'll see a table of available cognitive approaches
   - When asked "Would you like to select specific cognitive approaches?", choose "Yes"
   - Enter the numbers of the approaches you want to use (comma-separated, e.g., "1,3,7,9")
   - The wizard will verify your selections and display the selected approaches

3. **Preview and Execute**:
   - In the command preview, you'll see details of your selected templates 
   - The command will include the `--instruction-templates` parameter with your selected template IDs

## Using Template Selection in Command Line

You can bypass the wizard and directly specify templates in the command line:

```bash
python main.py --query "Your innovation challenge" --instruction-templates "ins_creative,ins_systems,ins_futurist"
```

This command will only use the Creative Framework, Systems Thinking Framework, and Future-Oriented Framework for your innovation challenge.

## Choosing the Right Templates

Different templates work better for different types of innovation challenges:

- **For technical challenges**: Consider using Analytical, First Principles, and Systems Thinking
- **For creative innovation**: Try Creative, Contrarian, and Future-Oriented templates
- **For practical implementation**: Combine Pragmatic, Integrative, and Historical approaches

## Balancing Cognitive Diversity

While you can select any combination of templates, using templates with different cognitive styles often produces the most comprehensive results. For example:

- **Balanced approach**: Combine analytical, creative, and pragmatic templates
- **Future-focused approach**: Combine systems thinking, first principles, and futurist templates 
- **Critical review approach**: Combine critical, contrarian, and historical templates

## Technical Details

When using specific templates:

- The `--instruction-templates` parameter overrides the `--instructions` count parameter
- Template IDs must be valid and exist in the template library
- At least one template must be selected when using the feature
- Templates are applied in the order specified

## Examples

1. **Technical Solution Design**:
   ```
   python main.py --query "How might we improve battery efficiency in electric vehicles?" --instruction-templates "ins_analytical,ins_first_principles,ins_systems"
   ```

2. **Business Innovation**:
   ```
   python main.py --query "How might we create new revenue streams for our content platform?" --instruction-templates "ins_creative,ins_futurist,ins_pragmatic,ins_integrative"
   ```

3. **Critical Assessment**:
   ```
   python main.py --query "How might we address climate change through policy?" --instruction-templates "ins_critical,ins_historical,ins_contrarian"
   ```

## Best Practices

1. **Start with diversity**: Select 3-5 templates with different cognitive styles
2. **Experiment**: Try different combinations to see which work best for your challenges
3. **Compare results**: Use different template sets on the same query to compare approaches
4. **Custom combinations**: Create standard template sets for different types of challenges

## Troubleshooting

- **Invalid template ID error**: Check the table above for correct template IDs
- **Too many templates**: Using too many templates can create excessive combinations; consider using 3-5 templates
- **Missing template error**: Ensure you're using a current version of the ISEE framework with all templates