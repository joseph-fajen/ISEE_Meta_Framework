#!/usr/bin/env python3
"""
Automated Parameter Validation Test Framework for ISEE Meta Framework Web UI

This test framework automatically validates that Web UI parameters are correctly
passed through to the backend and properly reflected in CSV exports, preventing
parameter passing bugs like missing domains, frameworks, or models.

Usage:
    python tests/web_ui_parameter_validation.py
    python -m pytest tests/web_ui_parameter_validation.py -v
"""

import unittest
import json
import csv
import io
import tempfile
import os
import sys
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from app import app, ISEEWebDemo
    from cognitive_framework_visualizer import CognitiveFrameworkVisualizer
    from domain_manager import DomainManager, create_default_domains
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


@dataclass
class TestParameters:
    """Test case parameter definition"""
    query: str
    cognitive_frameworks: List[str]
    selected_models: List[str]
    selected_domains: List[str]
    execution_settings: str = "comprehensive"
    max_combinations: int = 100
    expected_records: Optional[int] = None

    def __post_init__(self):
        """Calculate expected records if not provided"""
        if self.expected_records is None:
            base_combinations = len(self.cognitive_frameworks) * len(self.selected_models) * len(self.selected_domains)
            self.expected_records = min(base_combinations, self.max_combinations)


@dataclass
class ValidationResult:
    """Result of parameter validation"""
    test_name: str
    expected_params: TestParameters
    csv_records: int
    missing_frameworks: List[str]
    missing_models: List[str]
    missing_domains: List[str]
    extra_records: int
    missing_records: int
    success: bool
    error_message: Optional[str] = None


class WebUIParameterValidator:
    """Core validation logic for Web UI parameter testing"""
    
    def __init__(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.framework_visualizer = CognitiveFrameworkVisualizer()
        self.domain_manager = DomainManager()
        
        # Initialize domains
        for domain in create_default_domains():
            self.domain_manager.add_domain(domain)
    
    def execute_parameter_test(self, test_params: TestParameters) -> ValidationResult:
        """Execute a parameter validation test"""
        try:
            # Prepare request data for Web UI API
            request_data = {
                "query": test_params.query,
                "cognitive_frameworks": test_params.cognitive_frameworks,
                "selected_models": test_params.selected_models,
                "selected_domains": test_params.selected_domains,
                "execution_settings": test_params.execution_settings,
                "max_combinations": test_params.max_combinations
            }
            
            # Call Web UI preview-queries endpoint to get JSON data
            response = self.client.post('/api/preview-queries', 
                                      data=json.dumps(request_data),
                                      content_type='application/json')
            
            if response.status_code != 200:
                return ValidationResult(
                    test_name="unknown",
                    expected_params=test_params,
                    csv_records=0,
                    missing_frameworks=[],
                    missing_models=[],
                    missing_domains=[],
                    extra_records=0,
                    missing_records=0,
                    success=False,
                    error_message=f"API call failed: {response.status_code} - {response.get_data(as_text=True)}"
                )
            
            # Parse JSON response
            json_data = response.get_data(as_text=True)
            json_response = json.loads(json_data)
            
            if not json_response.get('success'):
                return ValidationResult(
                    test_name="unknown",
                    expected_params=test_params,
                    csv_records=0,
                    missing_frameworks=[],
                    missing_models=[],
                    missing_domains=[],
                    extra_records=0,
                    missing_records=0,
                    success=False,
                    error_message=f"API returned error: {json_response.get('error', 'Unknown error')}"
                )
            
            # Extract query records from JSON
            query_records = json_response.get('queries', [])
            
            # Validate parameters
            return self._validate_query_records(test_params, query_records)
            
        except Exception as e:
            return ValidationResult(
                test_name="unknown",
                expected_params=test_params,
                csv_records=0,
                missing_frameworks=[],
                missing_models=[],
                missing_domains=[],
                extra_records=0,
                missing_records=0,
                success=False,
                error_message=f"Exception: {str(e)}"
            )
    
    def _parse_json_data(self, json_data: str) -> List[Dict[str, str]]:
        """Parse JSON data into list of records"""
        response = json.loads(json_data)
        return response.get('queries', [])
    
    def _validate_query_records(self, test_params: TestParameters, query_records: List[Dict[str, Any]]) -> ValidationResult:
        """Validate query records against expected parameters"""
        
        # Extract actual parameters from query records
        actual_frameworks = set()
        actual_models = set()
        actual_domains = set()
        
        for record in query_records:
            # Extract framework name from template_name
            template_name = record.get('template_name', '')
            if template_name:
                actual_frameworks.add(template_name)
                
            # Extract model name  
            model = record.get('model', '')
            if model:
                actual_models.add(model)
                
            # Extract domain name
            domain_name = record.get('domain_name', '')
            if domain_name:
                actual_domains.add(domain_name)
        
        # Remove empty strings
        actual_frameworks.discard('')
        actual_models.discard('')
        actual_domains.discard('')
        
        # Find missing parameters
        expected_frameworks = set(test_params.cognitive_frameworks)
        expected_models = set(test_params.selected_models)
        expected_domains = set(test_params.selected_domains)
        
        missing_frameworks = list(expected_frameworks - actual_frameworks)
        missing_models = list(expected_models - actual_models)
        missing_domains = list(expected_domains - actual_domains)
        
        # Calculate record counts
        actual_records = len(query_records)
        expected_records = test_params.expected_records
        
        extra_records = max(0, actual_records - expected_records)
        missing_records = max(0, expected_records - actual_records)
        
        # Determine success
        success = (
            len(missing_frameworks) == 0 and
            len(missing_models) == 0 and
            len(missing_domains) == 0 and
            missing_records == 0
        )
        
        return ValidationResult(
            test_name="validation",
            expected_params=test_params,
            csv_records=actual_records,
            missing_frameworks=missing_frameworks,
            missing_models=missing_models,
            missing_domains=missing_domains,
            extra_records=extra_records,
            missing_records=missing_records,
            success=success
        )


class TestWebUIParameterValidation(unittest.TestCase):
    """Comprehensive Web UI parameter validation test suite"""
    
    def setUp(self):
        """Set up test environment"""
        self.validator = WebUIParameterValidator()
        self.test_cases = self._generate_test_cases()
    
    def _generate_test_cases(self) -> List[Tuple[str, TestParameters]]:
        """Generate comprehensive test cases"""
        
        # Available options (dynamically loaded)
        available_frameworks = ["Analytical Framework", "Integrative Framework", 
                              "First Principles Framework", "Contrarian Framework"]
        available_models = ["openai/o3-pro", "google/gemini-2.5-pro-preview", 
                          "deepseek/deepseek-r1-0528-qwen3-8b:free", "anthropic/claude-sonnet-4"]
        available_domains = ["Education", "Technology Innovation", 
                           "Learning Experience Design", "Content Strategy"]
        
        test_cases = [
            # Basic single parameter tests
            ("single_framework_single_model_single_domain", TestParameters(
                query="Test query for single parameters",
                cognitive_frameworks=["Analytical Framework"],
                selected_models=["openai/o3-pro"],
                selected_domains=["Education"]
            )),
            
            # The exact bug case that was discovered
            ("bug_reproduction_case", TestParameters(
                query="How might I design a highly appealing web UI for a prompt meta framework tool?",
                cognitive_frameworks=["Analytical Framework", "Integrative Framework", 
                                    "First Principles Framework", "Contrarian Framework"],
                selected_models=["openai/o3-pro", "google/gemini-2.5-pro-preview", 
                               "deepseek/deepseek-r1-0528-qwen3-8b:free", "anthropic/claude-sonnet-4"],
                selected_domains=["Education", "Technology Innovation", 
                                "Learning Experience Design", "Content Strategy"]
            )),
            
            # Multiple frameworks, single model, single domain
            ("multiple_frameworks", TestParameters(
                query="Test multiple frameworks",
                cognitive_frameworks=["Analytical Framework", "Integrative Framework"],
                selected_models=["anthropic/claude-sonnet-4"],
                selected_domains=["Technology Innovation"]
            )),
            
            # Single framework, multiple models, single domain
            ("multiple_models", TestParameters(
                query="Test multiple models",
                cognitive_frameworks=["First Principles Framework"],
                selected_models=["openai/o3-pro", "anthropic/claude-sonnet-4"],
                selected_domains=["Education"]
            )),
            
            # Single framework, single model, multiple domains
            ("multiple_domains", TestParameters(
                query="Test multiple domains",
                cognitive_frameworks=["Contrarian Framework"],
                selected_models=["google/gemini-2.5-pro-preview"],
                selected_domains=["Education", "Technology Innovation", "Content Strategy"]
            )),
            
            # Edge case: All available parameters
            ("maximum_parameters", TestParameters(
                query="Test maximum parameter combinations",
                cognitive_frameworks=available_frameworks,
                selected_models=available_models,
                selected_domains=available_domains,
                max_combinations=64
            )),
            
            # Edge case: Two of each parameter type
            ("balanced_parameters", TestParameters(
                query="Test balanced parameter selection",
                cognitive_frameworks=["Analytical Framework", "Integrative Framework"],
                selected_models=["openai/o3-pro", "anthropic/claude-sonnet-4"],
                selected_domains=["Education", "Technology Innovation"]
            ))
        ]
        
        return test_cases
    
    def test_parameter_validation_suite(self):
        """Run comprehensive parameter validation tests"""
        results = []
        
        print(f"\n{'='*80}")
        print("ISEE Web UI Parameter Validation Test Suite")
        print(f"{'='*80}")
        
        for test_name, test_params in self.test_cases:
            print(f"\n🧪 Running test: {test_name}")
            print(f"   Frameworks: {len(test_params.cognitive_frameworks)}")
            print(f"   Models: {len(test_params.selected_models)}")
            print(f"   Domains: {len(test_params.selected_domains)}")
            print(f"   Expected records: {test_params.expected_records}")
            
            result = self.validator.execute_parameter_test(test_params)
            result.test_name = test_name
            results.append(result)
            
            if result.success:
                print(f"   ✅ PASSED - {result.csv_records} records generated")
            else:
                print(f"   ❌ FAILED - {result.csv_records} records generated")
                if result.error_message:
                    print(f"      Error: {result.error_message}")
                if result.missing_frameworks:
                    print(f"      Missing frameworks: {result.missing_frameworks}")
                if result.missing_models:
                    print(f"      Missing models: {result.missing_models}")
                if result.missing_domains:
                    print(f"      Missing domains: {result.missing_domains}")
                if result.missing_records:
                    print(f"      Missing records: {result.missing_records}")
        
        # Generate summary report
        self._generate_summary_report(results)
        
        # Assert overall success
        failed_tests = [r for r in results if not r.success]
        if failed_tests:
            self.fail(f"Parameter validation failed for {len(failed_tests)} test cases: {[r.test_name for r in failed_tests]}")
    
    def _generate_summary_report(self, results: List[ValidationResult]):
        """Generate detailed summary report"""
        print(f"\n{'='*80}")
        print("PARAMETER VALIDATION SUMMARY REPORT")
        print(f"{'='*80}")
        
        total_tests = len(results)
        passed_tests = len([r for r in results if r.success])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in results:
                if not result.success:
                    print(f"   {result.test_name}:")
                    if result.missing_domains:
                        print(f"      🚨 CRITICAL: Missing domains: {result.missing_domains}")
                    if result.missing_frameworks:
                        print(f"      Missing frameworks: {result.missing_frameworks}")
                    if result.missing_models:
                        print(f"      Missing models: {result.missing_models}")
                    if result.missing_records:
                        print(f"      Missing records: {result.missing_records}")
        
        print(f"\n{'='*80}")
    
    def test_bug_reproduction_case(self):
        """Specific test for the reported bug case"""
        bug_case = TestParameters(
            query="How might I design a highly appealing web UI for a prompt meta framework tool?",
            cognitive_frameworks=["Analytical Framework", "Integrative Framework", 
                                "First Principles Framework", "Contrarian Framework"],
            selected_models=["openai/o3-pro", "google/gemini-2.5-pro-preview", 
                           "deepseek/deepseek-r1-0528-qwen3-8b:free", "anthropic/claude-sonnet-4"],
            selected_domains=["Education", "Technology Innovation", 
                            "Learning Experience Design", "Content Strategy"]
        )
        
        result = self.validator.execute_parameter_test(bug_case)
        
        # Specific assertions for the reported bug
        self.assertEqual(len(result.missing_domains), 0, 
                        f"Missing domains detected: {result.missing_domains}")
        self.assertEqual(len(result.missing_frameworks), 0,
                        f"Missing frameworks detected: {result.missing_frameworks}")
        self.assertEqual(len(result.missing_models), 0,
                        f"Missing models detected: {result.missing_models}")
        
        # Should have records for all 4 domains
        self.assertGreaterEqual(result.csv_records, 64,  # 4 frameworks * 4 domains * 4 models minimum
                               f"Expected at least 64 records, got {result.csv_records}")


def run_validation_tests():
    """Standalone function to run validation tests"""
    if __name__ == "__main__":
        # Run tests
        unittest.main(verbosity=2)


if __name__ == "__main__":
    run_validation_tests()