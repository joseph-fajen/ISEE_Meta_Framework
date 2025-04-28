#!/usr/bin/env python3
"""
Test Script for Command Validation Feature

This script tests the command validation implementation in the Command Wizard.
"""

import os
import sys
import re
import subprocess
from typing import List, Dict, Any, Optional, Tuple

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import from project
from command_wizard import CommandWizard


def test_parameter_validation():
    """Test that the parameter validation correctly identifies issues."""
    # Create a command wizard instance
    wizard = CommandWizard()
    
    # Test with missing required parameter (query)
    wizard.params = {
        "query": None,
        "domain": "Technology",
        "models": 2,
        "instructions": 3,
        "variations": 2
    }
    
    validation = wizard._validate_parameters()
    print("Test with missing query:")
    print(f"Valid: {validation['valid']}")
    print(f"Errors: {validation['errors']}")
    
    if not validation["valid"] and any("Query is required" in error for error in validation["errors"]):
        print("✅ Required parameter validation works")
    else:
        print("❌ Required parameter validation failed")
        return False
    
    # Test with invalid parameter values
    wizard.params = {
        "query": "How to improve urban mobility?",
        "domain": "Technology",
        "models": -1,  # Invalid value
        "instructions": 0,  # Invalid value
        "variations": 2
    }
    
    validation = wizard._validate_parameters()
    print("\nTest with invalid parameter values:")
    print(f"Valid: {validation['valid']}")
    print(f"Errors: {validation['errors']}")
    
    if not validation["valid"] and any("must be a positive integer" in error for error in validation["errors"]):
        print("✅ Parameter value validation works")
    else:
        print("❌ Parameter value validation failed")
        return False
    
    # Test parameter relationship validation
    wizard.params = {
        "query": "How to improve urban mobility?",
        "domain": "Technology",
        "models": 2,
        "instructions": 3,
        "variations": 2,
        "analyze_results": True,
        "generate_reports": False  # This is required when analyze_results is True
    }
    
    validation = wizard._validate_parameters()
    print("\nTest parameter relationship validation:")
    print(f"Valid: {validation['valid']}")
    print(f"Errors: {validation['errors']}")
    
    if not validation["valid"] and any("analyze_results requires generate_reports" in error for error in validation["errors"]):
        print("✅ Parameter relationship validation works")
    else:
        print("❌ Parameter relationship validation failed")
        return False
    
    # Test warning for high combination counts
    wizard.params = {
        "query": "How to improve urban mobility?",
        "domain": "Technology",
        "models": 5,
        "instructions": 10,
        "variations": 3,  # This creates 150 combinations
        "sampling_method": "exhaustive",
        "generate_reports": True,
        "analyze_results": True
    }
    
    validation = wizard._validate_parameters()
    print("\nTest high combination count warning:")
    print(f"Warnings: {validation['warnings']}")
    print(f"Suggestions: {validation['suggestions']}")
    
    if any("Large combination count" in warning for warning in validation["warnings"]):
        print("✅ High combination count warning works")
    else:
        print("❌ High combination count warning failed")
        return False
    
    return True


def test_command_validation():
    """Test that the command validation correctly identifies issues."""
    # Create a command wizard instance
    wizard = CommandWizard()
    
    # Test with valid command
    valid_command = "python main.py --query \"How to improve urban mobility?\" --domain \"Technology\" --models 2 --instructions 3 --variations 2 --sampling-method exhaustive --quick"
    
    validation = wizard.validate_command(valid_command)
    print("\nTest with valid command:")
    print(f"Valid: {validation['valid']}")
    print(f"Warnings: {validation['warnings']}")
    
    if validation["valid"] and not validation["errors"]:
        print("✅ Valid command validation works")
    else:
        print("❌ Valid command validation failed")
        return False
    
    # Test with missing required parameter
    invalid_command = "python main.py --domain \"Technology\" --models 2 --instructions 3 --variations 2"
    
    validation = wizard.validate_command(invalid_command)
    print("\nTest command with missing query:")
    print(f"Valid: {validation['valid']}")
    print(f"Errors: {validation['errors']}")
    
    if not validation["valid"] and any("Missing required parameter: --query" in error for error in validation["errors"]):
        print("✅ Command with missing required parameter validation works")
    else:
        print("❌ Command with missing required parameter validation failed")
        return False
    
    # Test warning for high combination count
    high_cost_command = "python main.py --query \"How to improve urban mobility?\" --domain \"Technology\" --models 5 --instructions 10 --variations 3"
    
    validation = wizard.validate_command(high_cost_command)
    print("\nTest command with high combination count:")
    print(f"Warnings: {validation['warnings']}")
    
    if any("combinations" in warning for warning in validation["warnings"]):
        print("✅ Command with high combination count warning works")
    else:
        print("❌ Command with high combination count warning failed")
        return False
    
    return True


def run_all_tests():
    """Run all command validation tests."""
    print("Testing Command Validation Implementation")
    print("=" * 40)
    
    test_results = []
    test_results.append(("Parameter Validation", test_parameter_validation()))
    test_results.append(("Command Validation", test_command_validation()))
    
    print("\nTest Summary:")
    print("=" * 40)
    all_passed = True
    for name, result in test_results:
        status = "PASSED" if result else "FAILED"
        if not result:
            all_passed = False
        print(f"{name}: {status}")
    
    if all_passed:
        print("\n✅ All command validation tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed. See details above.")
        return 1


if __name__ == "__main__":
    # Run all tests
    exit_code = run_all_tests()
    sys.exit(exit_code)