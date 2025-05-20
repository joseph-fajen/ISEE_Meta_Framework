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
- Parameter relationships with other settings
- A reminder that you can type "help" or "example" for more details

### 2. Detailed Parameter Help

At any parameter prompt, you can type:
- `help` - View detailed information about the current parameter
- `help all` - View a summary of all available parameters
- `example` - View detailed examples with explanations for the current parameter

### 3. Parameter Impacts in Command Preview

The command preview now includes:
- Descriptions for each parameter 
- A special "Parameter Impacts" section highlighting important effects
- Warnings about potentially expensive parameter combinations
- Alerts about parameter dependencies

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
- **Parameter Relationships**: How this parameter affects or is affected by others

### Visual Indicators
- ✓ Green checkmarks highlight beneficial parameter choices
- ⚠️ Yellow warnings indicate potential issues
- 🚫 Red warnings indicate high costs or problematic combinations

## Using Parameter Context Effectively

### For First-Time Users
1. At the start of the wizard, type `help all` to see all available parameters
2. Read the parameter descriptions before making choices
3. Pay attention to the impact statements to understand consequences
4. Use the `example` command to see concrete usage examples

### When Configuring Complex Commands
1. Use `help` to understand important parameters like sampling methods
2. Check related parameters to understand interactions
3. Use `example` to see concrete examples of parameter values
4. Review the parameter impacts section in the command preview

### To Control Costs and Time
1. Pay attention to warnings about large combination counts
2. Use `help` on parameters like `max_combinations` and `sampling_method`
3. Consider presets like `quick` mode for faster execution
4. Check the combination impact details in the `example` command output

## Example Parameter Context

Here's an example of the enhanced parameter context information for the `models` parameter:

```
Number of different models to use

This parameter determines how many different AI models will process your query. 
Using multiple models allows you to compare responses across different 
architectures and capabilities.

Impact: More models provide greater diversity of responses but increase API 
costs and execution time. Each model adds a multiplier to your total combinations.

Affects --variations: The total number of combinations is models × instructions × variations. 
Increasing models will multiply your combinations by the number of variations.

(Plus 2 more relationships)

(Type 'help' for more information, 'example' for usage examples)
```

## Example Usage Examples

Here's an example of the detailed examples for the `models` parameter:

```
Examples: --models
=============================

Number of different models to use

Example 1: 1
A minimal setting that uses just one model. Fastest and cheapest option, 
but provides no comparative insights across different models.

Example 2: 3
A balanced option that provides good model diversity while keeping combinations 
manageable. With 3 models, 3 instructions, and 2 variations, you'd have 18 combinations.

Impact on combinations: 18 combinations - Moderate execution time and cost
```

## Understanding Parameter Relationships

The enhanced parameter context system now tracks relationships between parameters to help you understand how they affect each other:

- **Multiplicative Relationships**: How parameters like models, instructions, and variations multiply to determine total combinations
- **Dependencies**: Parameters that require other parameters to be enabled
- **Conflicts**: Parameters that may have unintended effects when used together
- **Presets**: How preset options like `quick` and `full` affect multiple parameters

The parameter help and example commands explain these relationships and warn about potential issues.

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

The enhanced parameter context system helps you make informed decisions when configuring ISEE commands. By understanding each parameter's purpose, impact, and relationships, you can create more effective evaluations while controlling costs and execution time.

Remember to use `help`, `help all`, and `example` whenever you need more information about parameters, and pay attention to the relationship warnings to avoid unexpected costs or long execution times.