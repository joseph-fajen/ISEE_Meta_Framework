# ISEE Command Parameter Context Guide

## Overview

The Command Wizard now provides detailed explanations and context for every parameter, helping you understand the purpose, impact, and relationships between different settings. This guide explains how to access and use this information to create more effective ISEE commands.

## Ways to Access Parameter Help

The Command Wizard offers several ways to access help for parameters:

### 1. Contextual Information During Input

When you're prompted to enter a parameter value, the wizard automatically displays:
- A brief description of the parameter
- The current value (if any)
- How the parameter impacts execution
- A reminder that you can type "help" for more details

### 2. Detailed Parameter Help

At any parameter prompt, you can type:
- `help` - View detailed information about the current parameter
- `help all` - View a summary of all available parameters

### 3. Parameter Impacts in Command Preview

The command preview now includes:
- Descriptions for each parameter 
- A special "Parameter Impacts" section highlighting important effects
- Warnings about potentially expensive parameter combinations

## What You'll Learn from Parameter Help

For each parameter, you can access:

### Basic Information
- **Short Description**: What the parameter does
- **Long Description**: Detailed explanation of the parameter's purpose and function
- **Current Value**: What value is currently set (if any)

### Impact and Usage Guidance
- **Impact**: How the parameter affects execution time, API costs, or results
- **Examples**: Sample values to demonstrate typical usage
- **Related Parameters**: Other parameters that interact with or affect this one

### Visual Indicators
- ✓ Green checkmarks highlight beneficial parameter choices
- ⚠️ Yellow warnings indicate potential issues or high costs

## Using Parameter Help Effectively

### For First-Time Users
1. At the start of the wizard, type `help all` to see all available parameters
2. Read the parameter descriptions before making choices
3. Pay attention to the impact statements to understand consequences

### When Configuring Complex Commands
1. Use `help` to understand important parameters like sampling methods
2. Check related parameters to understand interactions
3. Review the parameter impacts section in the command preview

### To Control Costs and Time
1. Pay attention to warnings about large combination counts
2. Use `help` on parameters like `max_combinations` and `sampling_method`
3. Consider presets like `quick` mode for faster execution

## Example Parameter Help

Here's an example of the detailed help for the `models` parameter:

```
Help: --models
=============================

The number of different models to use

This parameter determines how many different AI models will process your query. 
Using multiple models allows you to compare responses across different 
architectures and capabilities.

Impact: More models provide greater diversity of responses but increase API 
costs and execution time. Each model adds a multiplier to your total combinations.

Examples:
  • 2
  • 3
  • 5

Related parameters:
  • --balanced-models: Balance models across providers
  • --use-ollama: Include Ollama local models
  • --simulate: Simulate responses without API calls
```

## Understanding Parameter Relationships

Parameters often have complex relationships that affect each other:

- `analyze_results` requires `generate_reports` to be enabled
- `instruction_templates` overrides the `instructions` count parameter
- `quick` and `full` presets affect multiple sampling parameters
- `no_visualizations` only has an effect when `analyze_results` is enabled

The parameter help system explains these relationships and warns about potential conflicts.

## Key Parameters to Understand

These parameters have the greatest impact on execution and results:

### 1. Combination Control Parameters
- `models`: Number of different models to use
- `instructions`: Number of different instruction prompts
- `variations`: Number of query variations
- These multiply together to determine total combinations

### 2. Sampling Parameters
- `sampling_method`: How combinations are selected
- `max_combinations`: Upper limit on executed combinations
- `quick`: Preset for stratified sampling with 36 combinations
- `full`: Preset for exhaustive combinations

### 3. Output Configuration
- `generate_reports`: Creates summary reports
- `analyze_results`: Performs analysis with visualizations
- `synthesize_method`: How model responses are combined

## Conclusion

The parameter context and explanations feature helps you make informed decisions when configuring ISEE commands. By understanding each parameter's purpose, impact, and relationships, you can create more effective evaluations while controlling costs and execution time.

Remember to use `help` and `help all` whenever you need more information about parameters, and pay attention to the impact warnings in the command preview to avoid unexpected costs or long execution times.