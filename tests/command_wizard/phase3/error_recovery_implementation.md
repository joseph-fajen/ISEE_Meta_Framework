# Error Recovery Implementation

## Overview

This document outlines the implementation of error recovery mechanisms in the ISEE Command Wizard. The goal was to enhance the wizard's ability to detect, classify, and recover from errors that occur during command execution, as specified in Phase 3 of the Command Wizard roadmap.

## Implementation Components

### 1. Error Classification System

The error classification system consists of:

- **Base `CommandError` Class**: Provides the foundation for all error types with error code, message, details, and suggestions
- **Specialized Error Subclasses**: `ValidationError`, `EnvironmentError`, `ExecutionError`, and `ResourceError` for different error categories
- **Error Code Registry**: Standardized error codes with predefined messages for consistency

```python
class CommandError:
    """Base class for all command execution errors."""
    def __init__(self, error_code, message, details=None, suggestions=None):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.suggestions = suggestions or []
```

### 2. Error Detection System

The `detect_error_type` function analyzes error messages to classify errors:

- Uses pattern matching to identify error signatures
- Maps to appropriate error types and codes
- Extracts contextual details (e.g., missing parameter names)
- Provides targeted suggestions for resolution

```python
def detect_error_type(error, command, env_state=None):
    """
    Analyze an error and classify it by type.
    """
    error_str = str(error)
    
    # Check for API key issues
    if any(key in error_str.lower() for key in ["api key", "apikey", "authentication"]):
        # ...
        return EnvironmentError(...)
    
    # Check for other error types
    # ...
```

### 3. Recovery Strategy Pattern

The recovery system implements the Strategy pattern:

- **Base `RecoveryStrategy` Class**: Provides interface for all recovery strategies
- **Specialized Strategy Classes**: Implement recovery logic for different error types
- **Strategy Factory Function**: `create_recovery_strategy` creates appropriate strategy based on error type

```python
class RecoveryStrategy:
    """Base class for all recovery strategies."""
    def __init__(self, error):
        self.error = error
        
    def can_auto_recover(self):
        """Check if automatic recovery is possible."""
        return False
        
    def attempt_recovery(self, command_wizard):
        """Attempt to recover from the error."""
        raise NotImplementedError("Subclasses must implement this method")
```

### 4. Interactive Recovery UI

The recovery UI provides a consistent interface for both rich and plain terminal modes:

- Displays errors with appropriate formatting
- Presents recovery options based on error type
- Guides users through parameter reconfiguration
- Provides feedback on recovery progress

For Rich terminals:
```python
if RICH_AVAILABLE:
    self.console.print(f"[bold red]Error:[/bold red] {recovery_strategy.get_user_friendly_message()}")
    
    # Display suggestions
    if recovery_strategy.get_suggestions():
        self.console.print("[bold yellow]Suggestions:[/bold yellow]")
        for suggestion in recovery_strategy.get_suggestions():
            self.console.print(f"- {suggestion}")
```

### 5. Parameter Reconfiguration System

The `reconfigure_parameters` method allows interactive modification of command parameters:

- Displays current parameter values
- Allows selection of parameters to modify
- Validates new parameter values
- Updates parameters in real-time
- Regenerates command with updated parameters

### 6. Enhanced Command Execution

The enhanced `execute_command` method supports error recovery:

- Executes commands with detailed error handling
- Analyzes errors using the detection system
- Applies appropriate recovery strategies
- Supports recovery loops for multi-step recovery
- Returns structured results with success status and error details

### 7. Main Execution Loop

The main method now includes a recovery loop:

- Executes commands with error handling
- Processes error recovery results
- Supports parameter reconfiguration
- Enables command regeneration after recovery
- Allows users to abort or retry execution

## Error Recovery Flow

1. **Command Execution**:
   ```python
   success, result, error = self.execute_command(command)
   ```

2. **Error Detection**:
   ```python
   error = detect_error_type(e, command)
   ```

3. **Recovery Strategy Selection**:
   ```python
   recovery_strategy = create_recovery_strategy(error)
   ```

4. **Automatic Recovery Attempt** (if possible):
   ```python
   if recovery_strategy.can_auto_recover():
       # Attempt automatic recovery
       recovery_succeeded = recovery_strategy.attempt_recovery(self)
   ```

5. **Manual Recovery Options** (if automatic recovery fails or isn't possible):
   ```python
   # Present recovery options
   options = [
       "Try again with the same command",
       "Modify command parameters",
       "Switch to simulation mode",
       "Abort execution"
   ]
   ```

6. **Parameter Reconfiguration** (if selected):
   ```python
   self.reconfigure_parameters()
   ```

7. **Command Regeneration**:
   ```python
   updated_command = self.generate_command()
   ```

8. **Retry Execution**:
   ```python
   return self.execute_command(updated_command)
   ```

## Specific Recovery Implementations

### 1. API Key Error Recovery

```python
def _recover_missing_api_key(self, command_wizard):
    # Offer to switch to simulation mode
    use_simulation = Confirm.ask("Would you like to switch to simulation mode instead?")
    if use_simulation:
        command_wizard.params["simulate"] = True
        return True
    return False
```

### 2. Ollama Error Recovery

```python
def _recover_ollama_not_running(self, command_wizard):
    # Offer options: disable Ollama, use simulation, or try again
    options = [
        "Disable Ollama and continue with cloud models only",
        "Switch to simulation mode",
        "Try again after starting Ollama"
    ]
    # ...
```

### 3. Rate Limit Error Recovery

```python
def _recover_rate_limit(self, command_wizard):
    # Calculate current potential combinations
    models = command_wizard.params.get("models", 2)
    instructions = command_wizard.params.get("instructions", 3)
    variations = command_wizard.params.get("variations", 2)
    total = models * instructions * variations
    suggested = max(10, total // 2)
    
    # Offer to reduce combinations
    command_wizard.params["max_combinations"] = new_max
    # ...
```

## Error Pattern Recognition

The implementation includes pattern recognition for common error types:

- API Key errors: Authentication failures, unauthorized access
- Ollama errors: Connection refused, service not running
- Parameter errors: Missing parameters, invalid values
- File errors: Not found, permission denied
- Resource errors: Rate limits, timeouts, memory constraints

Each pattern is mapped to specific suggestions and recovery strategies.

## Testing

The implementation includes comprehensive tests in `test_error_recovery.py`:

1. **Error Detection Tests**:
   - Verify correct classification of different error types
   - Test extraction of contextual information from error messages
   - Confirm appropriate suggestion generation

2. **Recovery Strategy Tests**:
   - Test strategy selection based on error type
   - Verify auto-recovery capabilities
   - Test recovery option presentation

3. **End-to-End Recovery Tests**:
   - Test complete recovery loops for different error scenarios
   - Verify parameter reconfiguration
   - Test command regeneration after recovery

## Future Enhancements

Potential future enhancements could include:

1. **Learning-Based Recovery**: Track successful recovery patterns to improve suggestions
2. **Preemptive Validation**: Detect potential issues before execution
3. **Multi-Step Recovery Workflows**: Handle complex error scenarios
4. **Extended Pattern Recognition**: Improve detection of additional error types
5. **Recovery Telemetry**: Track recovery success rates to improve the system

## Conclusion

The error recovery implementation significantly enhances the robustness of the Command Wizard by providing a structured approach to detecting, classifying, and recovering from errors. By offering both automatic and guided recovery options, it improves the user experience and reduces frustration when errors occur.