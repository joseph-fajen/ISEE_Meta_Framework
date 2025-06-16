#!/usr/bin/env python3
"""
Update openrouter_config.json to include all 15 domains
"""

import json
from domain_manager import create_default_domains

def update_config_domains():
    """Update the openrouter_config.json file with all 15 domains"""
    
    # Load current config
    with open('openrouter_config.json', 'r') as f:
        config = json.load(f)
    
    # Get all default domains
    all_domains = create_default_domains()
    
    # Convert domains to dict format
    domains_json = []
    for domain in all_domains:
        domains_json.append(domain.to_dict())
    
    # Replace domains section
    config['domains'] = domains_json
    
    # Save updated config
    with open('openrouter_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Updated openrouter_config.json with {len(domains_json)} domains")
    
    # Print summary
    print("\n📋 Updated domains:")
    for domain in all_domains:
        print(f"   - {domain.id}: {domain.name}")

if __name__ == "__main__":
    update_config_domains()