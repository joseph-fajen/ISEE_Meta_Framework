#!/usr/bin/env python3
"""
Debug script to check available cognitive frameworks
"""

from app import app, ISEEWebDemo
import json

def debug_frameworks():
    """Debug cognitive framework availability"""
    print("🧠 Debugging Cognitive Frameworks...")
    
    # Initialize web demo
    demo = ISEEWebDemo()
    
    # Get frameworks from Web UI
    frameworks = demo.get_cognitive_frameworks()
    
    print(f"📊 Web UI frameworks: {len(frameworks)}")
    
    for framework in frameworks:
        print(f"   - {framework.get('name', 'Unknown')}")
    
    # Also check with framework visualizer directly
    from cognitive_framework_visualizer import CognitiveFrameworkVisualizer
    visualizer = CognitiveFrameworkVisualizer()
    
    all_frameworks = []
    for level in ["basic", "advanced", "expert"]:
        level_frameworks = visualizer.get_frameworks_for_complexity(level)
        all_frameworks.extend(level_frameworks)
    
    print(f"\n📋 All framework visualizer frameworks ({len(all_frameworks)}):")
    for framework in all_frameworks:
        print(f"   - {framework.get('name', 'Unknown')}")
    
    # Also check config file templates
    with open('openrouter_config.json', 'r') as f:
        config = json.load(f)
    
    if 'instructions' in config:
        print(f"\n📄 Config file instruction templates ({len(config['instructions'])}):")
        for template in config['instructions']:
            print(f"   - {template.get('name', 'Unknown')} (id: {template.get('id', 'Unknown')})")

if __name__ == "__main__":
    debug_frameworks()