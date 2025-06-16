#!/usr/bin/env python3
"""
Debug script to check Web UI available domains
"""

from app import app, ISEEWebDemo

def debug_web_domains():
    """Debug Web UI domain availability"""
    print("🌐 Debugging Web UI Domains...")
    
    # Initialize web demo
    demo = ISEEWebDemo()
    
    # Get domains from Web UI
    domains = demo.get_knowledge_domains()
    
    print(f"📊 Web UI domain categories: {len(domains)}")
    
    for category, domain_list in domains.items():
        print(f"\n📂 {category}: {len(domain_list)} domains")
        for domain in domain_list:
            print(f"   - {domain}")
    
    # Flatten all domains for comparison
    all_web_domains = []
    for category, domain_list in domains.items():
        all_web_domains.extend(domain_list)
    
    print(f"\n📋 All Web UI domains ({len(all_web_domains)}):")
    for domain in sorted(all_web_domains):
        print(f"   - {domain}")

if __name__ == "__main__":
    debug_web_domains()