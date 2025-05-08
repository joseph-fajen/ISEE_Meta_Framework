# ISEE Command Validation Guide

## Overview

The Command Wizard now includes comprehensive validation capabilities that help you construct valid, efficient ISEE commands. This guide explains how command validation works and how to interpret validation results.

## Types of Validation

The Command Wizard performs several types of validation:

### 1. Required Parameter Validation

Ensures that all required parameters are provided, such as:
- `--query`: A query text must be specified
- Other parameters that may be contextually required based on your selections

### 2. Parameter Value Validation

Checks that parameter values are within valid ranges:
- Numeric parameters (like `models`, `instructions`, and `variations`) must be positive
- Parameter values must match expected types (numbers, text, etc.)
- Values are checked for reasonableness (e.g., warnings for very large values)

### 3. Parameter Relationship Validation

Verifies that interdependent parameters are used correctly:
- `--analyze-results` requires `--generate-reports` to be enabled
- `--export-csv` requires `--generate-reports` to be enabled
- `--no-visualizations` only works with `--analyze-results`
- `--quick` and `--full` are mutually exclusive parameters

### 4. Efficiency Validation

Identifies potential performance or cost issues:
- Warns about large combination counts that may take a long time to execute
- Alerts about potentially expensive API calls when not using simulation
- Suggests optimization strategies for large workloads

### 5. Command Structure Validation

Checks the overall command structure:
- Validates that the command follows correct syntax
- Ensures that all parameter names are valid
- Verifies that parameters are used in the correct context

## Understanding Validation Results

Validation results are presented in three categories:

### Errors

Errors are critical issues that prevent command execution. These must be fixed before the command can run.

Examples of errors:
- Missing required parameters
- Invalid parameter values
- Incompatible parameter combinations

### Warnings

Warnings are potential issues that won't prevent execution but may lead to undesired outcomes.

Examples of warnings:
- Large combination counts that may take a long time to run
- High potential API costs
- Inefficient parameter combinations

### Suggestions

Suggestions are recommendations for improving your command, even if it's already valid.

Examples of suggestions:
- Using `--quick` mode for large combination counts
- Adding `--balanced-models` when using multiple models
- Setting `--max-combinations` to limit execution time

## Visual Indicators

If you're using a terminal that supports rich formatting, validation results include visual cues:

- **Command Border Color**:
  - 🟢 **Green**: Command is valid with no warnings
  - 🟡 **Yellow**: Command has warnings but can be executed
  - 🔴 **Red**: Command has errors and cannot be executed

- **Message Icons**:
  - ❌ **Red X**: Errors that must be fixed
  - ⚠️ **Yellow Warning**: Potential issues to consider
  - 💡 **Green Lightbulb**: Suggestions for improvement

## Responding to Validation Results

Here's how to respond to different validation results:

### Handling Errors

1. **Read the error message** carefully to understand what's wrong
2. **Fix the identified issue** by changing the relevant parameter
3. **Preview the command again** to verify the error is resolved

### Addressing Warnings

1. **Consider the impact** of the warning on your use case
2. **Modify parameters** if the warning affects your goals
3. **Proceed with caution** if you choose to ignore the warning

### Applying Suggestions

1. **Review each suggestion** to understand its benefit
2. **Apply suggestions** that align with your objectives
3. **Ignore suggestions** that don't apply to your specific needs

## Cost and Performance Optimization

The validation system provides specific guidance for optimizing cost and performance:

### Managing API Costs

- Use `--simulate` during development to avoid API charges
- Set `--max-combinations` to limit the number of API calls
- Use `--quick` mode for an optimized sample of combinations
- Consider using `--balanced-models` to distribute calls across providers

### Improving Performance

- Use `--stratified` sampling for large combination spaces
- Limit the number of models, instructions, and variations
- Consider using `--quick` mode for faster execution
- Use appropriate `--max-combinations` values for your needs

## Examples

### Example 1: Missing Required Parameter

```
Error: Query is required
```

**Solution**: Add a query using `--query "Your query here"`

### Example 2: Parameter Relationship Error

```
Error: analyze_results requires generate_reports to be enabled
Suggestion: Enable --generate-reports to use --analyze-results
```

**Solution**: Add the `--generate-reports` parameter or remove `--analyze-results`

### Example 3: Performance Warning

```
Warning: Large combination count (150) may take a long time to execute
Suggestion: Consider using --quick mode to reduce combinations
Suggestion: Or set --max-combinations to limit the number of executions
```

**Solution**: Add `--quick` or `--max-combinations 50` to limit execution time

## Advanced Validation Features

### Execution Time Estimates

The Command Wizard now provides rough execution time estimates based on your parameter selections. These estimates consider:

- Total combination count
- Whether you're using real API calls or simulation
- Any limits applied through `--max-combinations`

### API Cost Warnings

When running with real API calls (not using `--simulate`), the Command Wizard provides:

- Warnings for potentially expensive operations
- Additional confirmation prompts for high-cost commands
- Suggestions for reducing costs while maintaining results quality

## Conclusion

The command validation system helps you create more effective ISEE commands by:

1. Preventing errors before they occur
2. Warning about potential issues
3. Providing actionable suggestions for improvement
4. Estimating execution time and costs

By addressing validation feedback, you can create more efficient, effective ISEE commands that produce better results while minimizing execution time and API costs.