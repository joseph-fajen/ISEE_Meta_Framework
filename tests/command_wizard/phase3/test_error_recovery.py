#!/usr/bin/env python3
"""
Test Script for Error Recovery Features

This script tests the error recovery mechanisms in the Command Wizard.
"""

import os
import sys
import re
import subprocess
from typing import List, Dict, Any, Optional, Tuple

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import from project
from command_wizard import (
    CommandWizard, 
    CommandError, ValidationError, EnvironmentError, ExecutionError, ResourceError,
    detect_error_type, create_recovery_strategy
)


def test_error_detection():
    """Test that the error detection system correctly identifies error types."""
    print("Testing Error Detection\n" + "=" * 20)
    
    # Test API key error detection
    command = "python main.py --query 'test' --models 2"
    api_error = subprocess.CalledProcessError(
        1, command, 
        output="", 
        stderr="Error: Authentication failed. Check your API key."
    )
    
    error = detect_error_type(api_error, command)
    print("API Key Error Test:")
    print(f"Error code: {error.error_code}")
    print(f"Message: {error.message}")
    print(f"Suggestions: {error.suggestions}")
    
    if isinstance(error, EnvironmentError) and error.error_code == "ENV-001":
        print("✅ API Key error correctly detected")
    else:
        print("❌ API Key error detection failed")
        return False
    
    # Test Ollama error detection
    command = "python main.py --query 'test' --use-ollama"
    ollama_error = subprocess.CalledProcessError(
        1, command, 
        output="", 
        stderr="Error: Failed to connect to Ollama server. Connection refused."
    )
    
    error = detect_error_type(ollama_error, command)
    print("\nOllama Error Test:")
    print(f"Error code: {error.error_code}")
    print(f"Message: {error.message}")
    print(f"Suggestions: {error.suggestions}")
    
    if isinstance(error, EnvironmentError) and error.error_code == "ENV-003":
        print("✅ Ollama error correctly detected")
    else:
        print("❌ Ollama error detection failed")
        return False
    
    # Test parameter error detection
    command = "python main.py --models 2"
    param_error = subprocess.CalledProcessError(
        1, command, 
        output="", 
        stderr="Error: the following arguments are required: --query"
    )
    
    error = detect_error_type(param_error, command)
    print("\nParameter Error Test:")
    print(f"Error code: {error.error_code}")
    print(f"Message: {error.message}")
    print(f"Suggestions: {error.suggestions}")
    
    if isinstance(error, ValidationError) or "parameter" in error.message.lower():
        print("✅ Parameter error correctly detected")
    else:
        print("❌ Parameter error detection failed")
        return False
    
    return True


def test_recovery_strategies():
    """Test that recovery strategies correctly handle different error types."""
    print("\nTesting Recovery Strategies\n" + "=" * 20)
    
    # Create a test wizard instance
    wizard = CommandWizard()
    
    # Test API key error recovery
    api_error = EnvironmentError(
        "ENV-001",
        "Missing or invalid API key for Anthropic",
        {"provider": "Anthropic"},
        ["Check that you have set the ANTHROPIC_API_KEY environment variable"]
    )
    
    strategy = create_recovery_strategy(api_error)
    print("API Key Error Recovery Test:")
    print(f"Can auto-recover: {strategy.can_auto_recover()}")
    print(f"User message: {strategy.get_user_friendly_message()}")
    print(f"Suggestions: {strategy.get_suggestions()}")
    
    if strategy.can_auto_recover():
        print("✅ API Key error recovery strategy correctly configured")
    else:
        print("❌ API Key error recovery strategy incorrectly configured")
        return False
    
    # Test Ollama error recovery
    ollama_error = EnvironmentError(
        "ENV-003",
        "Ollama is not running or accessible",
        {},
        ["Ensure Ollama is installed and running"]
    )
    
    strategy = create_recovery_strategy(ollama_error)
    print("\nOllama Error Recovery Test:")
    print(f"Can auto-recover: {strategy.can_auto_recover()}")
    print(f"User message: {strategy.get_user_friendly_message()}")
    print(f"Suggestions: {strategy.get_suggestions()}")
    
    if strategy.can_auto_recover():
        print("✅ Ollama error recovery strategy correctly configured")
    else:
        print("❌ Ollama error recovery strategy incorrectly configured")
        return False
    
    # Test API rate limit error recovery
    rate_limit_error = ResourceError(
        "RES-001",
        "API rate limit exceeded",
        {},
        ["Try again after a brief pause"]
    )
    
    strategy = create_recovery_strategy(rate_limit_error)
    print("\nRate Limit Error Recovery Test:")
    print(f"Can auto-recover: {strategy.can_auto_recover()}")
    print(f"User message: {strategy.get_user_friendly_message()}")
    print(f"Suggestions: {strategy.get_suggestions()}")
    
    if strategy.can_auto_recover():
        print("✅ Rate limit error recovery strategy correctly configured")
    else:
        print("❌ Rate limit error recovery strategy incorrectly configured")
        return False
    
    return True


def run_all_tests():
    """Run all error recovery tests."""
    print("Testing Command Wizard Error Recovery Implementation")
    print("=" * 50)
    
    test_results = []
    test_results.append(("Error Detection", test_error_detection()))
    test_results.append(("Recovery Strategies", test_recovery_strategies()))
    
    print("\nTest Summary:")
    print("=" * 50)
    all_passed = True
    for name, result in test_results:
        status = "PASSED" if result else "FAILED"
        if not result:
            all_passed = False
        print(f"{name}: {status}")
    
    if all_passed:
        print("\n✅ All error recovery tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed. See details above.")
        return 1


if __name__ == "__main__":
    # Run all tests
    exit_code = run_all_tests()
    sys.exit(exit_code)