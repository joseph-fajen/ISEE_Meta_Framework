#!/usr/bin/env python3
"""
ISEE Command Wizard Test Runner

Runs all tests for the ISEE Command Construction Wizard.
"""

import unittest
import sys
import os
import argparse
from typing import List, Optional

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import test modules
from tests.command_wizard.test_api_detection import TestAPIDetection
from tests.command_wizard.test_domain_loading import TestDomainLoading
from tests.command_wizard.test_template_selection import TestTemplateSelection
from tests.command_wizard.test_command_construction import TestCommandConstruction

def create_test_suite() -> unittest.TestSuite:
    """Create a test suite containing all command wizard tests.
    
    Returns:
        A unittest.TestSuite containing all tests.
    """
    suite = unittest.TestSuite()
    
    # Add API detection tests
    suite.addTest(unittest.makeSuite(TestAPIDetection))
    
    # Add domain loading tests
    suite.addTest(unittest.makeSuite(TestDomainLoading))
    
    # Add template selection tests
    suite.addTest(unittest.makeSuite(TestTemplateSelection))
    
    # Add command construction tests
    suite.addTest(unittest.makeSuite(TestCommandConstruction))
    
    return suite

def run_specific_tests(test_names: List[str]) -> None:
    """Run specific tests by name.
    
    Args:
        test_names: List of test names to run.
    """
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Build a mapping of test classes
    test_classes = {
        'api': TestAPIDetection,
        'domain': TestDomainLoading,
        'template': TestTemplateSelection,
        'command': TestCommandConstruction
    }
    
    for name in test_names:
        # If it's a class name
        if name in test_classes:
            suite.addTest(unittest.makeSuite(test_classes[name]))
        else:
            # Try to find the test in each class
            found = False
            for cls_name, cls in test_classes.items():
                test_case_names = loader.getTestCaseNames(cls)
                for test_case_name in test_case_names:
                    if name in test_case_name:
                        # Create a suite for this specific test
                        cls_suite = unittest.TestSuite()
                        cls_suite.addTest(cls(test_case_name))
                        suite.addTest(cls_suite)
                        found = True
            
            if not found:
                print(f"Warning: No test found matching '{name}'")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

def main() -> None:
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description='Run tests for the ISEE Command Wizard')
    parser.add_argument('--tests', nargs='+', help='Run specific tests')
    parser.add_argument('--list', action='store_true', help='List available tests')
    parser.add_argument('--verbosity', type=int, default=2, help='Verbosity level (1-3)')
    args = parser.parse_args()
    
    if args.list:
        print("Available test categories:")
        print("  api     - API detection tests")
        print("  domain  - Domain loading tests")
        print("  template - Template selection tests")
        print("  command - Command construction tests")
        
        # Print individual test names
        loader = unittest.TestLoader()
        print("\nAvailable individual tests:")
        
        test_classes = {
            'API Detection': TestAPIDetection,
            'Domain Loading': TestDomainLoading,
            'Template Selection': TestTemplateSelection,
            'Command Construction': TestCommandConstruction
        }
        
        for category, cls in test_classes.items():
            print(f"\n{category}:")
            for test_name in loader.getTestCaseNames(cls):
                print(f"  {test_name}")
        
        sys.exit(0)
    
    if args.tests:
        run_specific_tests(args.tests)
    else:
        # Run all tests
        suite = create_test_suite()
        runner = unittest.TextTestRunner(verbosity=args.verbosity)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            sys.exit(0)
        else:
            sys.exit(1)

if __name__ == "__main__":
    main()