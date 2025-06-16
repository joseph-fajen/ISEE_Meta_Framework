#!/usr/bin/env python3
"""
Test Runner for ISEE Meta Framework Web UI Parameter Validation

This script provides a convenient way to run parameter validation tests
with detailed output and reporting.

Usage:
    python tests/test_runner.py                    # Run all tests
    python tests/test_runner.py --bug-only         # Run only bug reproduction test
    python tests/test_runner.py --verbose          # Verbose output
    python tests/test_runner.py --help             # Show help
"""

import argparse
import sys
import os
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.web_ui_parameter_validation import TestWebUIParameterValidation, WebUIParameterValidator


def run_bug_reproduction_test():
    """Run only the specific bug reproduction test"""
    print("🚨 Running Bug Reproduction Test")
    print("="*50)
    
    suite = unittest.TestSuite()
    suite.addTest(TestWebUIParameterValidation('test_bug_reproduction_case'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_full_validation_suite():
    """Run the complete parameter validation test suite"""
    print("🧪 Running Full Parameter Validation Suite")
    print("="*50)
    
    suite = unittest.TestSuite()
    suite.addTest(TestWebUIParameterValidation('test_parameter_validation_suite'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_quick_validation():
    """Run a quick validation of key endpoints"""
    print("⚡ Running Quick Validation")
    print("="*30)
    
    try:
        validator = WebUIParameterValidator()
        
        # Test 1: Simple case
        from tests.web_ui_parameter_validation import TestParameters
        simple_test = TestParameters(
            query="Simple test query",
            cognitive_frameworks=["Analytical Framework"],
            selected_models=["anthropic/claude-sonnet-4"],
            selected_domains=["Education"]
        )
        
        result = validator.execute_parameter_test(simple_test)
        if result.success:
            print("✅ Simple test: PASSED")
        else:
            print(f"❌ Simple test: FAILED - {result.error_message}")
            return False
        
        # Test 2: The specific bug case
        bug_test = TestParameters(
            query="How might I design a web UI?",
            cognitive_frameworks=["Analytical Framework", "Contrarian Framework"],
            selected_models=["openai/o3-pro", "anthropic/claude-sonnet-4"],
            selected_domains=["Education", "Technology Innovation", "Content Strategy"]
        )
        
        result = validator.execute_parameter_test(bug_test)
        if result.success:
            print("✅ Multi-domain test: PASSED")
        else:
            print(f"❌ Multi-domain test: FAILED")
            if result.missing_domains:
                print(f"   🚨 Missing domains: {result.missing_domains}")
            return False
        
        print("\n🎉 Quick validation completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Quick validation failed: {e}")
        return False


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(
        description="ISEE Meta Framework Web UI Parameter Validation Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tests/test_runner.py                 # Run full validation suite
  python tests/test_runner.py --bug-only      # Test specific bug reproduction
  python tests/test_runner.py --quick         # Quick validation check
  python tests/test_runner.py --verbose       # Verbose output
        """
    )
    
    parser.add_argument('--bug-only', action='store_true',
                        help='Run only the bug reproduction test')
    parser.add_argument('--quick', action='store_true',
                        help='Run quick validation tests')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Set up environment
    if args.verbose:
        os.environ['VERBOSE'] = '1'
    
    print("🧬 ISEE Meta Framework - Web UI Parameter Validation")
    print("="*60)
    
    try:
        if args.quick:
            success = run_quick_validation()
        elif args.bug_only:
            success = run_bug_reproduction_test()
        else:
            success = run_full_validation_suite()
        
        if success:
            print("\n🎉 All tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. See output above for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()