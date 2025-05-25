#!/usr/bin/env python3
"""
Test script for the Cost Estimation module.
"""

import sys
from cost_estimation import CostEstimator

def test_cost_estimation():
    """Test basic cost estimation functionality."""
    # Create a cost estimator
    cost_estimator = CostEstimator()
    
    # Test scenario 1: Simple query with default parameters
    params1 = {
        "query": "How might we improve transportation?",
        "domain": "Transportation",
        "models": 2,
        "instructions": 3,
        "variations": 2,
        "simulate": False
    }
    
    estimate1 = cost_estimator.estimate_cost(params1)
    print("\n=== Test Scenario 1: Basic Query with Default Parameters ===")
    print(f"Total Cost: ${estimate1['total_cost']:.2f}")
    print(f"Time Estimate: {estimate1['time_estimate_min']:.2f}-{estimate1['time_estimate_max']:.2f} minutes")
    print(f"Combinations: {estimate1['combinations_estimate']}")
    print(f"Cost Warning Level: {estimate1['cost_warning_level']}")
    print(f"Time Warning Level: {estimate1['time_warning_level']}")
    
    # Test scenario 2: More complex query with more models and variations
    params2 = {
        "query": "How might we improve education systems to better prepare students for future challenges?",
        "domain": "Education",
        "models": 5,
        "instructions": 5,
        "variations": 3,
        "max_combinations": 50,
        "simulate": False
    }
    
    estimate2 = cost_estimator.estimate_cost(params2)
    print("\n=== Test Scenario 2: Complex Query with More Parameters ===")
    print(f"Total Cost: ${estimate2['total_cost']:.2f}")
    print(f"Time Estimate: {estimate2['time_estimate_min']:.2f}-{estimate2['time_estimate_max']:.2f} minutes")
    print(f"Combinations: {estimate2['combinations_estimate']}")
    print(f"Cost Warning Level: {estimate2['cost_warning_level']}")
    print(f"Time Warning Level: {estimate2['time_warning_level']}")
    
    # Test scenario 3: Simulation mode (should be zero cost)
    params3 = {
        "query": "How might we reduce carbon emissions?",
        "domain": "Environment",
        "models": 3,
        "instructions": 3,
        "variations": 2,
        "simulate": True
    }
    
    estimate3 = cost_estimator.estimate_cost(params3)
    print("\n=== Test Scenario 3: Simulation Mode ===")
    print(f"Total Cost: ${estimate3['total_cost']:.2f}")
    print(f"Time Estimate: {estimate3['time_estimate_min']:.2f}-{estimate3['time_estimate_max']:.2f} minutes")
    print(f"Combinations: {estimate3.get('combinations_estimate', 0)}")
    print(f"Is Simulation: {estimate3.get('is_simulation', False)}")
    
    # Test warning message
    warning_message = cost_estimator.get_warning_message(estimate2)
    if warning_message:
        print("\n=== Warning Message ===")
        print(warning_message)
    
    # Test visual indicators
    print("\n=== Visual Indicators ===")
    print(f"Cost Indicator for Scenario 1: {cost_estimator.get_cost_indicator(estimate1)}")
    print(f"Cost Indicator for Scenario 2: {cost_estimator.get_cost_indicator(estimate2)}")
    print(f"Cost Indicator for Scenario 3: {cost_estimator.get_cost_indicator(estimate3)}")
    print(f"Time Indicator for Scenario 1: {cost_estimator.get_time_indicator(estimate1)}")
    print(f"Time Indicator for Scenario 2: {cost_estimator.get_time_indicator(estimate2)}")
    print(f"Time Indicator for Scenario 3: {cost_estimator.get_time_indicator(estimate3)}")

if __name__ == "__main__":
    test_cost_estimation()