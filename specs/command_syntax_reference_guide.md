# ISEE Command Syntax Reference Guide

## Overview

This document provides a comprehensive reference for the command syntax of the Idea Synthesis and Extraction Engine (ISEE). It is organized hierarchically from essential to advanced options, making it suitable for both new users and power users.

## Command Taxonomy

The ISEE command system can be categorized into nine functional parameter groups:

1. **Core Configuration Parameters**: Define how the framework is initialized (e.g., `--config`, `--domain-config`)
2. **Input Parameters**: Define the actual innovation query and domain (e.g., `--query`, `--domain`)
3. **Model Selection Parameters**: Control which AI models are used (e.g., `--models`, `--use-ollama`, `--balanced-models`)
4. **Instruction Selection Parameters**: Determine cognitive approaches (e.g., `--instructions`)
5. **Query Variation Parameters**: Control how queries are diversified (e.g., `--variations`)
6. **Execution Control Parameters**: Determine how combinations are sampled (e.g., `--max-combinations`, `--sampling-method`)
7. **Output Control Parameters**: Define how results are saved and formatted (e.g., `--output-format`, `--output-file`)
8. **Analysis Parameters**: Control additional processing of results (e.g., `--generate-reports`, `--analyze-results`)
9. **Mode Parameters**: Overall operating modes (e.g., `--simulate`, `--dry-run`, `--quick`, `--full`)

## Essential Command Elements

At minimum, a functional ISEE command requires only a query:

```bash
python main.py --query "Your innovation question here" --simulate
```

This minimal command will:
- Use default domain selection (all available domains)
- Use simulated responses (no API calls)
- Apply default models (2)
- Use default instructions (3)
- Generate default query variations (2)
- Use default sampling method ("exhaustive" unless max-combinations is specified)
- Output to an automatically generated file in a timestamped run-specific directory

## Core Command Parameters

### Input Parameters

| Parameter | Description | Default Value | Example |
|-----------|-------------|---------------|---------|
| `--query` | The innovation question to explore | None (Required) | `--query "How might we improve urban mobility?"` |
| `--domain` | The domain context for the query | All available domains | `--domain "Urban Planning"` |

### Model Selection Parameters

| Parameter | Description | Default Value | Example |
|-----------|-------------|---------------|---------|
| `--models` | Number of models to use | 2 | `--models 3` |
| `--use-ollama` | Include local Ollama models | False | `--use-ollama` |
| `--balanced-models` | Ensure balanced representation of models across combinations | False | `--balanced-models` |

### Instruction Selection Parameters

| Parameter | Description | Default Value | Example |
|-----------|-------------|---------------|---------|
| `--instructions` | Number of instruction templates to use | 3 | `--instructions 3` |

### Query Variation Parameters

| Parameter | Description | Default Value | Example |
|-----------|-------------|---------------|---------|
| `--variations` | Number of query variations to generate | 2 | `--variations 2` |

## Advanced Command Parameters

### Core Configuration Parameters

| Parameter | Description | Default Value | Example |
|-----------|-------------|---------------|---------|
| `--config` | Path to configuration file | None | `--config sample_config.json` |
| `--domain-config` | Path to domain-specific configuration | None | `--domain-config tech_writing_domains.json` |
| `--save-state` | Save application state to file | None | `--save-state "project_state.json"` |
| `--load-state` | Load application state from file | None | `--load-state "project_state.json"` |
| `--list-domains` | List all available domains and exit | False | `--list-domains` |

### Execution Control Parameters

| Parameter | Description | Default Value | Example |
|-----------|-------------|---------------|---------|
| `--max-combinations` | Maximum number of combinations to execute | None (all combinations) | `--max-combinations 15` |
| `--sampling-method` | Method for sampling combinations | "exhaustive" | `--sampling-method adaptive` |
| `--synthesize-method` | Method for synthesizing ideas | "cluster_based" | `--synthesize-method cross_pollination` (Note: cross_pollination currently has placeholder functionality) |

### Output Control Parameters

| Parameter | Description | Default Value | Example |
|-----------|-------------|---------------|---------|
| `--output-format` | Format for output | "markdown" | `--output-format json` |
| `--output-file` | Path to save output | Auto-generated timestamped file | `--output-file "results.md"` |
| `--output-directory` | Directory to save reports to | Run-specific timestamped directory | `--output-directory "my_reports"` |
| `--report-format` | Format for generated reports | "markdown" | `--report-format json` |

### Analysis Parameters

| Parameter | Description | Default Value | Example |
|-----------|-------------|---------------|---------|
| `--generate-reports` | Generate detailed reports | False | `--generate-reports` |
| `--export-csv` | Export data as CSV files | False | `--export-csv` |
| `--analyze-results` | Perform analysis with visualizations | False | `--analyze-results` |
| `--no-visualizations` | Skip generating visualization charts during analysis | False | `--no-visualizations` |

### Mode Parameters

| Parameter | Description | Default Value | Example |
|-----------|-------------|---------------|---------|
| `--simulate` | Use simulated responses instead of real API calls | False (auto-enabled if no API keys available) | `--simulate` |
| `--dry-run` | Preview execution without running | False | `--dry-run` |
| `--quick` | Run in quick mode (stratified sampling with 36 combinations) | False | `--quick` |
| `--full` | Run in full (exhaustive) mode | False | `--full` |

## Common Command Patterns

### Minimal Exploration (Simulation)

```bash
python main.py --query "How might we improve urban transportation?" --simulate
```

### Standard Exploration (Real API)

```bash
python main.py --query "How might we improve urban transportation?" --domain "Urban Planning" --models 2 --instructions 3 --variations 2 --max-combinations 12 --output-file "transportation_ideas.md"
```

### Comprehensive Exploration

```bash
python main.py --config unified_config.json --query "How might we improve urban transportation?" --domain "Urban Planning" --models 5 --instructions 4 --variations 3 --max-combinations 20 --balanced-models --generate-reports --analyze-results --export-csv
```

### Cross-Provider Exploration

```bash
python main.py --config sample_config.json --query "How might we improve urban transportation?" --use-ollama --models 5 --balanced-models --output-file "cross_provider_results.md"
```

### Domain-Specific Configuration

```bash
python main.py --domain-config tech_writing_domains.json --query "How can we improve documentation?" --domain "Technical Documentation" --models 3
```

### Save and Resume Workflow

```bash
# Initial run
python main.py --query "How might we improve urban transportation?" --save-state "transportation_project.json"

# Resume later
python main.py --load-state "transportation_project.json" --generate-reports --analyze-results
```

## Quick Reference

### Shortcut Command Options

| Shortcut | Equivalent | Description |
|----------|------------|-------------|
| `--quick` | `--sampling-method stratified --max-combinations 36` | Run in quick mode with limited combinations |
| `--full` | `--sampling-method exhaustive --max-combinations None` | Run with exhaustive combinations |

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Unknown domain | Check available domains with `--list-domains` |
| API errors | Verify API keys in .env file or use `--simulate` |
| Command too complex | Use a configuration file with `--config` |
| Need to preview execution | Add `--dry-run` to see what would be executed |
| Long-running process | Save state with `--save-state` and resume later |
| Ollama models not found | Make sure Ollama is running with `ollama serve` |
| Need to use specific models | Use a custom config file or `--balanced-models` to ensure diversity |

## Advanced Usage Notes

1. **Configuration Files**: For complex setups, using a configuration file with `--config` is more maintainable than specifying all parameters on the command line.

2. **Model Balance**: The `--balanced-models` flag is critical when comparing multiple model providers as it ensures fair representation across all combinations rather than clustering by model type. This creates a better distribution for comparing the cognitive approaches of different models.

3. **Combinations Optimization**: The sampling method significantly impacts execution time:
   - `exhaustive`: Tries all possible combinations (can be very large)
   - `stratified`: Ensures representation across all dimensions 
   - `adaptive`: Currently falls back to stratified sampling (placeholder for future implementation)

4. **State Management**: For long-running projects, use `--save-state` and `--load-state` to preserve work between sessions.

5. **Domain Specialization**: When working in a specific field, consider creating a domain-specific configuration file with relevant domains.

## Conclusion

This reference guide provides a comprehensive overview of the ISEE command syntax. For new users, starting with the essential parameters and gradually incorporating advanced options as needed is recommended. For complex innovation projects, using configuration files and the state management system will yield the most effective results.

For further details on specific aspects of the system, refer to the specialized documentation in the `docs/` directory.
