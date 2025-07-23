#!/usr/bin/env python3
"""
Test Suite for Dynamic Query Variation System

This test suite validates the new dynamic context-sensitive query variation system
against various query types and complexity levels.
"""

import os
import sys
import logging
from typing import List, Dict, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dynamic_query_variation import DynamicQueryVariator, QueryAnalysis
from query_generator import QueryGenerator, Query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DynamicVariationTestSuite:
    """Comprehensive test suite for dynamic query variations."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.variator = DynamicQueryVariator()
        self.query_generator = QueryGenerator(use_dynamic_variations=True)
        self.test_results = []
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results."""
        logger.info("Starting Dynamic Query Variation Test Suite")
        logger.info("=" * 60)
        
        # Define test queries across complexity spectrum
        test_queries = [
            # Simple queries
            {
                "text": "How can we improve education?",
                "expected_complexity": "simple",
                "expected_should_vary": True,
                "category": "Simple Educational"
            },
            {
                "text": "What are good ways to reduce stress?",
                "expected_complexity": "simple", 
                "expected_should_vary": True,
                "category": "Simple Health"
            },
            
            # Moderate complexity queries
            {
                "text": "How might we design urban transportation systems that balance efficiency, sustainability, and accessibility for diverse populations?",
                "expected_complexity": "moderate",
                "expected_should_vary": True,
                "category": "Moderate Urban Planning"
            },
            {
                "text": "What strategies can organizations use to foster innovation while maintaining operational stability?",
                "expected_complexity": "moderate",
                "expected_should_vary": True,
                "category": "Moderate Business"
            },
            
            # Complex queries
            {
                "text": "How might we develop a comprehensive framework for evaluating the long-term societal impacts of artificial intelligence deployment across healthcare, education, and employment sectors while accounting for regulatory, ethical, and technological considerations?",
                "expected_complexity": "complex",
                "expected_should_vary": True,  # Should still vary but carefully
                "expected_protective": True,
                "category": "Complex AI Policy"
            },
            
            # Highly structured/technical queries
            {
                "text": "What are the implications of implementing a comprehensive blockchain-based formal verification methodology for smart contract security auditing, specifically examining the integration of zero-knowledge proofs with automated theorem proving for vulnerability detection?",
                "expected_complexity": "highly_structured",
                "expected_should_vary": False,  # Should not vary
                "expected_protective": True,
                "category": "Highly Structured Technical"
            },
            {
                "text": "How should we systematically evaluate the thermodynamic efficiency of novel quantum heat engines operating in the non-equilibrium regime, considering both coherence preservation and energy extraction optimization under decoherence constraints?",
                "expected_complexity": "highly_structured",
                "expected_should_vary": False,
                "expected_protective": True,
                "category": "Highly Structured Physics"
            }
        ]
        
        results = {
            "total_tests": len(test_queries),
            "passed": 0,
            "failed": 0,
            "test_details": [],
            "summary": {}
        }
        
        # Run tests for each query
        for i, test_query in enumerate(test_queries, 1):
            logger.info(f"\nTest {i}/{len(test_queries)}: {test_query['category']}")
            logger.info(f"Query: {test_query['text'][:80]}...")
            
            test_result = self._run_single_test(test_query)
            results["test_details"].append(test_result)
            
            if test_result["passed"]:
                results["passed"] += 1
                logger.info("✅ PASSED")
            else:
                results["failed"] += 1
                logger.info("❌ FAILED")
                logger.info(f"   Reason: {test_result['failure_reason']}")
        
        # Generate summary statistics
        results["summary"] = self._generate_summary(results["test_details"])
        
        # Test integration with legacy system
        integration_result = self._test_legacy_integration()
        results["integration_test"] = integration_result
        
        logger.info("\n" + "=" * 60)
        logger.info("Test Suite Results:")
        logger.info(f"Total Tests: {results['total_tests']}")
        logger.info(f"Passed: {results['passed']}")
        logger.info(f"Failed: {results['failed']}")
        logger.info(f"Success Rate: {results['passed']/results['total_tests']*100:.1f}%")
        
        return results
    
    def _run_single_test(self, test_query: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case."""
        result = {
            "query": test_query["text"],
            "category": test_query["category"],
            "passed": True,
            "failure_reason": "",
            "analysis": None,
            "variations": [],
            "analysis_accuracy": 0.0
        }
        
        try:
            # Test query analysis
            analysis = self.variator.analyze_query(test_query["text"])
            result["analysis"] = {
                "complexity": analysis.complexity_level,
                "should_vary": analysis.should_vary,
                "protective_mode": analysis.protective_mode,
                "confidence": analysis.confidence,
                "topic_domain": analysis.topic_domain,
                "tone": analysis.tone
            }
            
            # Check analysis accuracy
            accuracy_score = 0.0
            total_checks = 0
            
            # Check complexity classification
            if "expected_complexity" in test_query:
                total_checks += 1
                if analysis.complexity_level == test_query["expected_complexity"]:
                    accuracy_score += 1
                else:
                    result["passed"] = False
                    result["failure_reason"] += f"Expected complexity '{test_query['expected_complexity']}', got '{analysis.complexity_level}'. "
            
            # Check should_vary prediction
            if "expected_should_vary" in test_query:
                total_checks += 1
                if analysis.should_vary == test_query["expected_should_vary"]:
                    accuracy_score += 1
                else:
                    result["passed"] = False
                    result["failure_reason"] += f"Expected should_vary {test_query['expected_should_vary']}, got {analysis.should_vary}. "
            
            # Check protective mode
            if "expected_protective" in test_query:
                total_checks += 1
                if analysis.protective_mode == test_query["expected_protective"]:
                    accuracy_score += 1
                else:
                    result["passed"] = False
                    result["failure_reason"] += f"Expected protective_mode {test_query['expected_protective']}, got {analysis.protective_mode}. "
            
            result["analysis_accuracy"] = accuracy_score / total_checks if total_checks > 0 else 1.0
            
            # Test variation generation
            variations = self.variator.generate_variations(test_query["text"], max_variations=2)
            result["variations"] = [{"text": v.text, "strategy": v.strategy, "confidence": v.confidence} for v in variations]
            
            # Validate variation count based on analysis
            expected_variation_count = 2 if analysis.should_vary else 0
            if len(variations) > expected_variation_count:
                result["passed"] = False
                result["failure_reason"] += f"Generated too many variations ({len(variations)} > {expected_variation_count}). "
            
            # Quality checks for generated variations
            if variations:
                for var in variations:
                    # Check that variation is different from original
                    if var.text.strip().lower() == test_query["text"].strip().lower():
                        result["passed"] = False
                        result["failure_reason"] += "Generated variation identical to original. "
                    
                    # Check that variation is not empty
                    if not var.text.strip():
                        result["passed"] = False
                        result["failure_reason"] += "Generated empty variation. "
                    
                    # Check confidence score is reasonable
                    if var.confidence < 0.0 or var.confidence > 1.0:
                        result["passed"] = False
                        result["failure_reason"] += f"Invalid confidence score: {var.confidence}. "
            
        except Exception as e:
            result["passed"] = False
            result["failure_reason"] = f"Exception during test: {str(e)}"
            logger.error(f"Test failed with exception: {e}")
        
        return result
    
    def _test_legacy_integration(self) -> Dict[str, Any]:
        """Test integration with legacy QueryGenerator system."""
        logger.info("\nTesting Legacy Integration...")
        
        result = {
            "passed": True,
            "failure_reason": "",
            "tests": []
        }
        
        try:
            # Test with dynamic variations enabled
            test_query = Query(id="integration_test", text="How can we improve remote work productivity?")
            self.query_generator.add_base_query(test_query)
            
            variations = self.query_generator.generate_variations("integration_test", count=2)
            
            test_result = {
                "test_name": "Dynamic variations enabled",
                "variations_generated": len(variations),
                "passed": True,
                "details": []
            }
            
            # Validate that variations were generated
            if len(variations) == 0:
                test_result["passed"] = False
                test_result["details"].append("No variations generated when expected")
            
            # Check that variations have proper metadata
            for var in variations:
                if "variation_strategy" not in var.variables:
                    test_result["passed"] = False
                    test_result["details"].append("Missing variation_strategy metadata")
                if "variation_confidence" not in var.variables:
                    test_result["passed"] = False
                    test_result["details"].append("Missing variation_confidence metadata")
            
            result["tests"].append(test_result)
            
            # Test fallback to static variations
            static_generator = QueryGenerator(use_dynamic_variations=False)
            static_generator.add_base_query(test_query)
            static_variations = static_generator.generate_variations("integration_test", count=2)
            
            static_test_result = {
                "test_name": "Static variations fallback",
                "variations_generated": len(static_variations),
                "passed": len(static_variations) > 0,
                "details": ["Static fallback working"] if len(static_variations) > 0 else ["Static fallback failed"]
            }
            
            result["tests"].append(static_test_result)
            
            # Overall integration test result
            result["passed"] = all(test["passed"] for test in result["tests"])
            if not result["passed"]:
                result["failure_reason"] = "Some integration tests failed"
                
        except Exception as e:
            result["passed"] = False
            result["failure_reason"] = f"Integration test exception: {str(e)}"
        
        return result
    
    def _generate_summary(self, test_details: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from test results."""
        summary = {
            "complexity_accuracy": {},
            "variation_quality": {},
            "protective_mode_accuracy": 0.0,
            "average_confidence": 0.0
        }
        
        # Analyze complexity classification accuracy
        complexity_tests = [t for t in test_details if t["analysis"]]
        complexity_correct = 0
        protective_correct = 0
        total_confidence = 0.0
        
        for test in complexity_tests:
            analysis = test["analysis"]
            total_confidence += analysis["confidence"]
            
            # Track complexity accuracy by category
            category = test["category"]
            if category not in summary["complexity_accuracy"]:
                summary["complexity_accuracy"][category] = {"correct": 0, "total": 0}
            
            summary["complexity_accuracy"][category]["total"] += 1
            if test["analysis_accuracy"] > 0.8:  # Consider >80% accuracy as correct
                summary["complexity_accuracy"][category]["correct"] += 1
                complexity_correct += 1
            
            # Track protective mode accuracy
            if analysis.get("protective_mode") is not None:
                protective_correct += 1
        
        summary["overall_accuracy"] = complexity_correct / len(complexity_tests) if complexity_tests else 0.0
        summary["average_confidence"] = total_confidence / len(complexity_tests) if complexity_tests else 0.0
        
        # Analyze variation quality
        variation_tests = [t for t in test_details if t["variations"]]
        total_variations = sum(len(t["variations"]) for t in variation_tests)
        
        summary["variation_quality"] = {
            "total_variations_generated": total_variations,
            "average_per_query": total_variations / len(variation_tests) if variation_tests else 0.0,
            "unique_strategies_used": len(set(v["strategy"] for t in variation_tests for v in t["variations"]))
        }
        
        return summary

def main():
    """Run the dynamic variation test suite."""
    if not os.getenv('OPENROUTER_API_KEY'):
        logger.warning("No OPENROUTER_API_KEY found. Some tests may use fallback analysis.")
        print("\nTo run full tests, set your OpenRouter API key:")
        print("export OPENROUTER_API_KEY='your_api_key_here'")
        print("\nContinuing with limited testing...\n")
    
    test_suite = DynamicVariationTestSuite()
    results = test_suite.run_all_tests()
    
    # Save detailed results
    import json
    with open("dynamic_variation_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"\nDetailed results saved to: dynamic_variation_test_results.json")
    
    # Return appropriate exit code
    return 0 if results["failed"] == 0 else 1

if __name__ == "__main__":
    exit(main())