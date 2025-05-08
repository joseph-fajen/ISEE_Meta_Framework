# Command Validation Implementation

## Overview

This document outlines the implementation of enhanced command validation capabilities in the ISEE Command Wizard. The goal was to add comprehensive validation that helps users construct valid and efficient commands, as specified in Phase 3 of the Command Wizard roadmap.

## Implementation Components

### 1. Enhanced Parameter Validation

The `_validate_parameters` method has been expanded to provide more comprehensive validation:

- Returns a structured validation result with:
  - `valid`: Boolean indicating if all parameters are valid
  - `errors`: List of critical errors that prevent command execution
  - `warnings`: List of potential issues that won't prevent execution
  - `suggestions`: List of recommendations for improving the command

- Validates parameter relationships:
  - `analyze_results` requires `generate_reports` to be enabled
  - `export_csv` requires `generate_reports` to be enabled
  - `no_visualizations` requires `analyze_results` to be enabled
  - `quick` and `full` are mutually exclusive

- Validates parameter value ranges:
  - Numeric parameters must be positive
  - Warns about excessively high values that may cause performance or cost issues

- Provides efficiency warnings:
  - Warns about large combination counts (models × instructions × variations)
  - Suggests optimizations like using `--quick` mode for large combinations
  - Includes cost warnings for non-simulated runs with high combinations

- Offers optimization suggestions:
  - Recommends `--balanced-models` when using multiple models
  - Suggests appropriate sampling methods based on combination counts

### 2. Command String Validation

A new `validate_command` method validates the constructed command string:

- Parses the command to extract parameters
- Checks for missing required parameters
- Validates parameter syntax and values
- Identifies potential issues with the constructed command
- Provides warnings for potentially expensive or long-running commands

### 3. Validation Results Display

The `_display_validation_results` method presents validation results to users:

- Displays errors, warnings, and suggestions with appropriate formatting
- Uses color coding with the Rich library when available
- Allows users to continue despite warnings after confirmation
- Provides different display formats for rich terminal vs. plain text

### 4. Preview Enhancement

The `preview_command` method has been enhanced to:

- Show validation results with the command preview
- Color-code the command based on validation status
- Display more detailed information about the command's expected behavior
- Include execution time and cost estimates

### 5. Execution Validation

The command execution flow now includes validation checks:

- Validates the command before execution
- Requires explicit confirmation for potentially expensive operations
- Provides helpful error recovery suggestions when commands fail
- Aborts execution if critical errors are found

## Implementation Details

### Parameter Validation Logic

The parameter validation uses these primary validation approaches:

1. **Required Parameter Checks**:
   ```python
   if not self.params["query"]:
       validation["valid"] = False
       validation["errors"].append("Query is required")
   ```

2. **Parameter Relationship Validation**:
   ```python
   if self.params.get("analyze_results") and not self.params.get("generate_reports"):
       validation["valid"] = False
       validation["errors"].append("analyze_results requires generate_reports to be enabled")
   ```

3. **Value Range Validation**:
   ```python
   if self.params.get("models", 0) <= 0:
       validation["valid"] = False
       validation["errors"].append("models must be a positive integer")
   ```

4. **Efficiency Warnings**:
   ```python
   total_combinations = models * instructions * variations
   if total_combinations > 100:
       validation["warnings"].append(f"Large combination count ({total_combinations}) may take a long time to execute")
   ```

### Command Validation Logic

The command string validation uses regex to extract parameters and then validates them:

```python
param_pattern = r'--(\w+)(?:[= ]"([^"]*)"| ([^ "]*)|)'
params = {}

for match in re.finditer(param_pattern, command):
    param_name = match.group(1)
    param_value = match.group(2) if match.group(2) else match.group(3)
    
    if param_value is None:
        params[param_name] = True
    else:
        params[param_name] = param_value
```

## Display Implementation

The rich display implementation uses color-coded tables and panels:

```python
if validation["errors"]:
    self.console.print("\n[bold red]Command Validation Errors:[/bold red]")
    for error in validation["errors"]:
        self.console.print(f"❌ {error}")
```

Plain text output provides the same information without formatting:

```python
if validation["errors"]:
    print("\nCommand Validation Errors:")
    for error in validation["errors"]:
        print(f"- {error}")
```

## Testing

The implementation includes comprehensive tests in `test_command_validation.py`:

1. **Parameter Validation Tests**:
   - Required parameter validation
   - Parameter value range validation
   - Parameter relationship validation
   - High combination count warnings

2. **Command Validation Tests**:
   - Valid command validation
   - Missing required parameter validation
   - High combination count warnings

## Documentation

A comprehensive user guide has been created to explain the command validation features, including:

- Types of validations performed
- Warning and error meanings
- How to interpret and respond to validation results
- Best practices for efficient command construction

## User Experience Improvements

The enhanced validation provides several UX improvements:

1. **Color-Coded Feedback**: Makes issues immediately visible
2. **Progressive Disclosure**: Shows more details for warnings and errors
3. **Execution Estimates**: Helps users anticipate command runtime
4. **Cost Warnings**: Alerts users to potentially expensive operations
5. **Actionable Suggestions**: Provides specific recommendations for improvements

## Future Enhancements

Potential future enhancements could include:

1. **Auto-correction**: Automatically fix common issues when possible
2. **Validation Profiles**: Different validation rules for different use cases
3. **API Cost Estimation**: More accurate cost estimates based on model pricing
4. **Caching Validation**: Remember previous validation results for similar commands
5. **Configuration-based Validation**: Apply different validation rules based on config