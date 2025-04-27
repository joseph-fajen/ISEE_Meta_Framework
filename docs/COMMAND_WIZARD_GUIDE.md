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
3. **Command Preview**: Shows you the constructed command before running it
4. **Command Explanation**: Provides a human-readable summary of what the command will do
5. **Clipboard Integration**: Copies the generated command to your clipboard (when available)
6. **Direct Execution**: Offers to run the command for you

## Wizard Flow

The wizard follows this logical progression:

1. **Define Your Innovation Challenge**: Enter your innovation query
2. **Select Problem Domain**: Choose from available domains
3. **Configure Model Selection**: Select how many and which models to use
4. **Configure Cognitive Diversity**: Determine cognitive approaches and query variations
5. **Configure Execution Parameters**: Set combinations and sampling methods
6. **Configure Output Options**: Define output formats and reporting
7. **Configure Execution Mode**: Set simulation, dry run, and state options

## Enhanced UI

If you have the `rich` library installed, the Command Wizard will provide an enhanced terminal UI with:

- Colored output
- Formatted tables
- Interactive prompts
- Progress indicators

## Example Usage

Here's a typical workflow:

1. Run the wizard: `python command_wizard.py`
2. Follow the interactive prompts to configure your command
3. Review the command and summary
4. Choose to execute, copy, or note the command for later use

## Tips

- If you're new to ISEE, accept the default values for a standard exploration
- The wizard will auto-detect your available API keys and Ollama models
- Use simulation mode for testing without consuming API credits
- The command can be copied to your clipboard for later use or modification
- Use dry-run mode to preview execution without running actual API calls