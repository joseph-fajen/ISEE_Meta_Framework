# ISEE Command Error Recovery Guide

## Overview

The Command Wizard now includes robust error recovery mechanisms that help you troubleshoot and resolve issues that occur during command execution. This guide explains how error recovery works and how to make the most of these features.

## Error Recovery Process

When an error occurs during command execution, the Command Wizard:

1. **Detects and Classifies the Error**: Analyzes the error message to determine its type and severity
2. **Provides Contextual Information**: Explains what went wrong in user-friendly terms
3. **Suggests Recovery Options**: Offers specific actions based on the error type
4. **Guides You Through Recovery**: Helps you fix the issue without restarting the wizard

## Types of Errors and Recovery Options

### API Key Errors

When API keys are missing or invalid, the wizard offers:

- Switching to simulation mode 
- Using a different API provider
- Guidance on setting API key environment variables

Example:
```
Error: Missing or invalid API key for Anthropic

Suggestions:
- Check that you have set the ANTHROPIC_API_KEY environment variable
- Consider using simulation mode with --simulate for testing without API access
- Check that your API key is valid and has not expired

Would you like to switch to simulation mode instead? [Y/n]
```

### Ollama Errors

When Ollama is not running or accessible, the wizard offers:

- Disabling Ollama and continuing with cloud models only
- Switching to simulation mode
- Guidance on starting Ollama

Example:
```
Error: Ollama is not running or accessible

Suggestions:
- Ensure Ollama is installed and running (https://ollama.com)
- Run 'ollama serve' in a separate terminal
- Consider using cloud API models instead

Options:
1. Disable Ollama and continue with cloud models only
2. Switch to simulation mode
3. Try again after starting Ollama
```

### Parameter Errors

When there are issues with command parameters, the wizard offers:

- Interactive parameter reconfiguration
- Guidance on correct parameter usage
- Explanations of parameter requirements

Example:
```
Error: Missing or invalid parameter: --query

Suggestions:
- Provide a valid value for --query
- Check the parameter name and format
- Try running with --help to see all available parameters

Would you like to modify command parameters? [Y/n]
```

### Resource Errors

When you encounter API rate limits or timeouts, the wizard offers:

- Reducing the number of combinations
- Switching to simulation mode
- Waiting and retrying automatically

Example:
```
Error: API rate limit or timeout occurred

Suggestions:
- Try again after a brief pause
- Reduce the number of combinations or use --max-combinations
- Consider using --simulate for testing without API calls

Options:
1. Reduce the number of combinations
2. Switch to simulation mode
3. Wait and try again
```

## Interactive Parameter Reconfiguration

For many errors, the Command Wizard offers parameter reconfiguration to fix issues without restarting:

1. The wizard displays your current parameters
2. You select which parameter to modify
3. You enter a new value for that parameter
4. The wizard regenerates the command with the updated parameter
5. You confirm whether to run the updated command

This is especially useful for:
- Fixing invalid parameter values
- Adjusting combination counts after rate limit errors
- Enabling simulation mode when API keys aren't working
- Modifying output options when file writing fails

## Automatic Recovery

For some errors, the Command Wizard can automatically recover:

- **API Issues**: Can switch to simulation mode
- **Rate Limits**: Can reduce combination counts or add delays
- **Ollama Issues**: Can disable Ollama and use cloud models
- **Parameter Issues**: Can guide you through fixing invalid parameters

The wizard will always ask for confirmation before attempting automatic recovery.

## Error Severity Levels

Errors are classified by severity to help you understand their impact:

- **Critical**: Errors that completely prevent execution (missing executable, invalid syntax)
- **High**: Errors that prevent successful execution but may be recoverable (API authentication)
- **Medium**: Errors that affect results but don't prevent execution (rate limits)
- **Low**: Warnings and minor issues that you may choose to ignore

## Best Practices

To get the most out of error recovery:

1. **Read Error Messages Carefully**: They contain specific information about what went wrong
2. **Consider Suggested Solutions**: The wizard suggests the most likely fixes for each error
3. **Use Parameter Reconfiguration**: Often, a simple parameter change can resolve the issue
4. **Test with Simulation Mode**: Before using real APIs, test with `--simulate` to validate your command

## Conclusion

The error recovery system helps you resolve issues that occur during command execution without having to restart the wizard or manually troubleshoot problems. By providing contextual information, suggesting recovery options, and guiding you through the recovery process, it makes using the ISEE framework more efficient and less frustrating.

If you encounter persistent errors that can't be resolved through the recovery mechanisms, check the main ISEE documentation or report the issue to the project maintainers.