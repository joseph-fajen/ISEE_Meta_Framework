#!/usr/bin/env python3
"""
Raw Response Reader

Reads and displays raw LLM responses saved by the modified ISEE framework.
"""

import os
import glob
from pathlib import Path

def read_raw_responses(run_directory: str = None):
    """Read all raw responses from a run directory."""
    
    if run_directory is None:
        # Use latest run
        latest_link = Path("data/output/latest")
        if latest_link.exists():
            run_directory = str(latest_link.resolve())
        else:
            print("No run directory specified and no latest link found")
            return
    
    responses_dir = Path(run_directory) / "raw_responses"
    
    if not responses_dir.exists():
        print(f"No raw_responses directory found in {run_directory}")
        print("Make sure to run ISEE after enabling raw response storage")
        return
    
    response_files = list(responses_dir.glob("*.md"))
    
    if not response_files:
        print(f"No response files found in {responses_dir}")
        return
    
    print(f"Found {len(response_files)} raw responses in {responses_dir}")
    
    for i, filepath in enumerate(sorted(response_files), 1):
        print(f"\n{'='*80}")
        print(f"Response {i}/{len(response_files)}: {filepath.name}")
        print('='*80)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
        
        if i < len(response_files):
            input("\nPress Enter to continue to next response...")

def list_responses(run_directory: str = None):
    """List all available raw responses."""
    
    if run_directory is None:
        latest_link = Path("data/output/latest")
        if latest_link.exists():
            run_directory = str(latest_link.resolve())
        else:
            print("No run directory specified and no latest link found")
            return
    
    responses_dir = Path(run_directory) / "raw_responses"
    
    if not responses_dir.exists():
        print(f"No raw_responses directory found in {run_directory}")
        return
    
    response_files = list(responses_dir.glob("*.md"))
    
    print(f"\nRaw Responses in {run_directory}:")
    print(f"{'='*50}")
    
    for i, filepath in enumerate(sorted(response_files), 1):
        # Extract info from filename
        name_parts = filepath.stem.split('_')
        if len(name_parts) >= 3:
            combo_id = name_parts[0]
            model = '_'.join(name_parts[1:-1])
            template = name_parts[-1]
            print(f"{i:2d}. {combo_id} | {model} | {template}")
        else:
            print(f"{i:2d}. {filepath.name}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            list_responses(sys.argv[2] if len(sys.argv) > 2 else None)
        else:
            read_raw_responses(sys.argv[1])
    else:
        print("Raw Response Reader")
        print("Usage:")
        print("  python read_raw_responses.py [run_directory]")
        print("  python read_raw_responses.py --list [run_directory]")
        print("")
        list_responses()
