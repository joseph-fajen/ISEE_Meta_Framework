#!/usr/bin/env python3
"""
Test Script for Domain Search Feature

This script tests the domain search implementation in the Command Wizard.
"""

import os
import sys
import re
import subprocess
from typing import List, Dict, Any, Optional, Tuple

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import from project
from domain_manager import DomainManager, Domain, create_default_domains
from command_wizard import CommandWizard


def test_domain_filter_by_category():
    """Test that domains can be filtered by category."""
    # Create a command wizard instance
    wizard = CommandWizard()
    
    # Test filtering for education domains
    education_domains = wizard._filter_domains_by_category(
        wizard.domain_manager.list_domains(), 
        "education"
    )
    
    # Verify we got some results
    print(f"Found {len(education_domains)} domains in the 'education' category:")
    for domain in education_domains:
        print(f"- {domain.name}")
    
    if len(education_domains) > 0:
        print("✅ Domain filtering by category works")
        return True
    else:
        print("❌ No education domains found - filtering failed")
        return False


def test_domain_search():
    """Test domain search functionality."""
    # Create a command wizard instance
    wizard = CommandWizard()
    
    # Get all domains
    all_domains = wizard.domain_manager.list_domains()
    print(f"Total domains available: {len(all_domains)}")
    
    # Test searching for 'learning'
    search_results = wizard.domain_manager.search_domains("learning")
    
    # Print search results
    print(f"Search for 'learning' returned {len(search_results)} domains:")
    for domain in search_results:
        print(f"- {domain.name}")
        
    if len(search_results) > 0:
        print("✅ Domain search works")
        return True
    else:
        print("❌ No domains found for 'learning' - search failed")
        return False


def test_combined_filter_and_search():
    """Test that filtering and searching can be combined."""
    # Create a command wizard instance
    wizard = CommandWizard()
    
    # Get all domains
    all_domains = wizard.domain_manager.list_domains()
    
    # First filter by technology category
    tech_domains = wizard._filter_domains_by_category(all_domains, "technology")
    
    # Then search within those results for "innovation"
    search_results = []
    for domain in tech_domains:
        # Check if 'innovation' appears in name, description or keywords
        if (
            "innovation" in domain.name.lower() or 
            "innovation" in domain.description.lower() or
            any("innovation" in kw.lower() for kw in domain.keywords)
        ):
            search_results.append(domain)
    
    # Print results
    print(f"Technology domains containing 'innovation': {len(search_results)}")
    for domain in search_results:
        print(f"- {domain.name}")
        
    if len(search_results) > 0:
        print("✅ Combined filtering and searching works")
        return True
    else:
        print("❌ No domains found matching both filters - combined filtering failed")
        # Try if any domain has 'innovation' to validate test setup
        any_innovation = wizard.domain_manager.search_domains("innovation")
        if len(any_innovation) > 0:
            print(f"Note: Found {len(any_innovation)} domains with 'innovation' keyword but none in tech category")
        return False


def run_all_tests():
    """Run all domain search tests."""
    print("Testing Domain Search Implementation")
    print("=" * 40)
    
    test_results = []
    test_results.append(("Domain Category Filtering", test_domain_filter_by_category()))
    test_results.append(("Domain Keyword Search", test_domain_search()))
    test_results.append(("Combined Filtering and Search", test_combined_filter_and_search()))
    
    print("\nTest Summary:")
    print("=" * 40)
    all_passed = True
    for name, result in test_results:
        status = "PASSED" if result else "FAILED"
        if not result:
            all_passed = False
        print(f"{name}: {status}")
    
    if all_passed:
        print("\n✅ All domain search tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed. See details above.")
        return 1


if __name__ == "__main__":
    # Run all tests
    exit_code = run_all_tests()
    sys.exit(exit_code)