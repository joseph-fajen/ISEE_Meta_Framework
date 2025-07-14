#!/usr/bin/env python3
"""
Test the integration of cost estimation with CommandWizard
"""

import sys

# Test importing the modules
print("Testing module imports...")
try:
    from cost_estimation import CostEstimator
    print("✓ Successfully imported CostEstimator")
except ImportError as e:
    print(f"✗ Failed to import CostEstimator: {e}")
    sys.exit(1)

try:
    from command_wizard import CommandWizard, COST_ESTIMATION_AVAILABLE
    print(f"✓ Successfully imported CommandWizard (Cost estimation available: {COST_ESTIMATION_AVAILABLE})")
except ImportError as e:
    print(f"✗ Failed to import CommandWizard: {e}")
    sys.exit(1)

# Create instances to test initialization
print("\nTesting object initialization...")
try:
    estimator = CostEstimator()
    print("✓ Successfully created CostEstimator instance")
except Exception as e:
    print(f"✗ Failed to create CostEstimator instance: {e}")
    sys.exit(1)

try:
    wizard = CommandWizard()
    print("✓ Successfully created CommandWizard instance with cost estimation integration")
    print(f"✓ Cost estimator initialized: {wizard.cost_estimator is not None}")
except Exception as e:
    print(f"✗ Failed to create CommandWizard instance: {e}")
    sys.exit(1)

# Test basic cost estimation functionality with wizard parameters
print("\nTesting cost estimation with wizard parameters...")
try:
    # Set some parameters
    wizard.params["query"] = "How might we improve urban mobility?"
    wizard.params["models"] = 2
    wizard.params["instructions"] = 3
    wizard.params["variations"] = 2
    
    # Update the cost estimate
    estimate = wizard._update_cost_estimate()
    
    # Verify estimate was created
    if not wizard.current_cost_estimate:
        raise ValueError("Cost estimate not created")
    
    print(f"✓ Cost estimate created successfully")
    print(f"  - Estimated cost: ${estimate.get('total_cost', 0):.2f}")
    print(f"  - Estimated time: {estimate.get('time_estimate_min', 0):.1f}-{estimate.get('time_estimate_max', 0):.1f} minutes")
    print(f"  - Combinations: {estimate.get('combinations_estimate', 0)}")
    
    # Test warning message
    warning = wizard.cost_estimator.get_warning_message(estimate)
    print(f"  - Warning present: {warning is not None}")
    
    print("✓ All integration tests passed!")
except Exception as e:
    print(f"✗ Cost estimation integration test failed: {e}")
    sys.exit(1)