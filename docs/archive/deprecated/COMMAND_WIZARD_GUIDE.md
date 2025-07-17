# ISEE Command Wizard Guide

The ISEE Command Wizard is an interactive tool that helps you construct valid ISEE commands with the right parameters and options. It guides you through a series of questions to configure an ISEE command that matches your needs.

## Installation

The Command Wizard is included in the ISEE Meta Framework. To use it with the best experience, make sure you have the optional dependencies installed:

```bash
pip install -r requirements.txt
```

## Running the Command Wizard

You can run the Command Wizard with:

```bash
python command_wizard.py
```

Or if the file is made executable:

```bash
./command_wizard.py
```

## Features

The Command Wizard offers:

1. **Interactive Parameter Selection**: Step-by-step guidance through all ISEE command options
2. **Automatic API Detection**: Detects available API keys and local models
3. **Enhanced Command Preview**: Categorized parameter displays with detailed explanations and impact analysis
4. **Interactive Preview Commands**: Access preview functionality during parameter input with `preview`, `preview detailed`, and `preview summary`
5. **Parameter Context Help**: Comprehensive help system with examples and cross-parameter relationships
6. **Cost and Time Estimation**: Real-time estimates with visual indicators and warnings
7. **Command Explanation**: Provides a human-readable summary of what the command will do
8. **Clipboard Integration**: Copies the generated command to your clipboard (when available)
9. **Direct Execution**: Offers to run the command for you

## Wizard Flow

The wizard follows this logical progression:

1. **Define Your Innovation Challenge**: Enter your innovation query
2. **Select Problem Domain**: Choose from available domains
3. **Configure Model Selection**: Select how many and which models to use
4. **Configure Cognitive Diversity**: Determine cognitive approaches and query variations
5. **Configure Execution Parameters**: Set combinations and sampling methods
6. **Configure Output Options**: Define output formats and reporting
7. **Configure Execution Mode**: Set simulation, dry run, and state options
8. **Enhanced Command Preview**: Review categorized parameters with impact analysis

## Enhanced UI

If you have the `rich` library installed, the Command Wizard will provide an enhanced terminal UI with:

- Colored output
- Formatted tables
- Interactive prompts
- Progress indicators

## Enhanced Command Preview

The Command Wizard includes a powerful preview system that helps you understand your command configuration:

### Parameter Categorization

Parameters are organized into color-coded categories:

- **Basic Parameters** (Cyan): Core settings like query, domain, models, instructions, variations
- **Sampling Control** (Green): Options that control combination selection and limits
- **Model Selection** (Blue): Settings for model providers and simulation modes
- **Output Options** (Magenta): Configuration for reports, exports, and visualizations
- **Advanced Options** (Yellow): Specialized settings for state management and fine-tuning

### Interactive Preview Commands

During parameter input, you can use these special commands:

- `preview` - Show current command preview with your current parameter mode
- `preview detailed` - Show detailed view with full parameter descriptions
- `preview summary` - Show compact view with just parameter names and values
- `help` - Get detailed help for the current parameter
- `example` - See concrete examples for the current parameter

### Parameter Impact Analysis

The preview includes an impact analysis panel that shows:

- **Cost warnings** for potentially expensive configurations
- **Quality insights** about combination diversity and coverage
- **Best practice recommendations** based on your selections
- **Resource optimization tips** for balancing cost and quality

### Before/After Comparisons

When you modify parameters, the preview automatically shows:

- **Change tracking** highlighting what you've modified
- **Impact differences** showing how changes affect execution
- **Visual indicators** for parameter modifications

## Example Usage

Here's a typical workflow:

1. Run the wizard: `python command_wizard.py`
2. Follow the interactive prompts to configure your command
3. Use `preview` commands during input to see how your selections affect the final command
4. Review the categorized command preview with impact analysis
5. Choose to execute, copy, or note the command for later use

## Tips

- If you're new to ISEE, accept the default values for a standard exploration
- The wizard will auto-detect your available API keys and Ollama models
- Use simulation mode for testing without consuming API credits
- The command can be copied to your clipboard for later use or modification
- Use dry-run mode to preview execution without running actual API calls
- Use `preview detailed` to understand what each parameter does before making changes
- Watch the Parameter Impact Analysis for cost and quality optimization suggestions
- Take advantage of the before/after comparisons when experimenting with different settings