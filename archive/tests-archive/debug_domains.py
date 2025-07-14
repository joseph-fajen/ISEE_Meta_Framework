#!/usr/bin/env python3
"""
Debug script to check available domains vs requested domains
"""

from domain_manager import DomainManager, create_default_domains

def debug_domains():
    """Debug domain availability and matching"""
    print("🏗️ Debugging Domain Matching...")
    
    # Initialize domain manager
    dm = DomainManager()
    for domain in create_default_domains():
        dm.add_domain(domain)
    
    print(f"📊 Total domains loaded: {len(dm.domains)}")
    
    # List all available domains
    print("\n📋 Available domains:")
    for domain_id, domain in dm.domains.items():
        print(f"   {domain_id}: {domain.name}")
    
    # Test the domains that are failing in tests
    test_domains = [
        "Education", 
        "Technology Innovation", 
        "Learning Experience Design", 
        "Content Strategy"
    ]
    
    print("\n🔍 Testing domain matching:")
    for test_domain in test_domains:
        matching_domains = dm.search_domains(test_domain)
        print(f"   '{test_domain}' -> {len(matching_domains)} matches")
        for match in matching_domains:
            print(f"      - {match.id}: {match.name}")
        if not matching_domains:
            # Try partial matching
            partial_matches = []
            for domain_id, domain in dm.domains.items():
                if test_domain.lower() in domain.name.lower() or domain.name.lower() in test_domain.lower():
                    partial_matches.append(domain)
            if partial_matches:
                print(f"      Possible partial matches:")
                for match in partial_matches:
                    print(f"        - {match.id}: {match.name}")

if __name__ == "__main__":
    debug_domains()