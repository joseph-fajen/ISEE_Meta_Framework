#!/usr/bin/env python3
"""
Test script for instruction templates display
"""
import sys
from instruction_templates import create_default_library

def test_list_templates():
    """Test listing all templates"""
    # Initialize template library
    template_library = create_default_library()
    
    # Get templates using list_templates()
    templates = template_library.list_templates()
    
    # Display templates
    print(f"Found {len(templates)} templates:")
    for template in templates:
        print(f"- {template.id}: {template.name}")
        print(f"  Template: {template.template[:50]}...")

if __name__ == "__main__":
    test_list_templates()