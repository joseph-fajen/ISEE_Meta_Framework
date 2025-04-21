#!/usr/bin/env python3
"""
Helper script to migrate existing output files to the new directory structure.

This script scans the root directory for markdown and JSON files that match
common output patterns and moves them to the appropriate directories in
the data folder structure.
"""

import os
import re
import shutil
import sys
from datetime import datetime

# Patterns for identifying different file types
OUTPUT_PATTERNS = [
    r'.*_ideas\.md$',
    r'.*_result\.md$',
    r'ai_documentation_.*\.md$',
    r'.*_comprehensive\.md$',
    r'.*_balanced\.md$',
    r'.*_creative.*\.md$',
]

STATE_PATTERNS = [
    r'.*_state\.json$',
    r'ai_documentation_state\.json$',
]

def ensure_directories():
    """Create necessary directories if they don't exist."""
    os.makedirs("data/output", exist_ok=True)
    os.makedirs("data/state", exist_ok=True)

def should_move_to_output(filename):
    """Check if a file should be moved to the output directory."""
    for pattern in OUTPUT_PATTERNS:
        if re.match(pattern, filename):
            return True
    return filename.endswith('.md') and not filename.startswith('README')

def should_move_to_state(filename):
    """Check if a file should be moved to the state directory."""
    for pattern in STATE_PATTERNS:
        if re.match(pattern, filename):
            return True
    return False

def move_files():
    """Move files to their appropriate directories."""
    files_in_root = [f for f in os.listdir('.') if os.path.isfile(f)]
    
    output_files = []
    state_files = []
    
    for filename in files_in_root:
        if should_move_to_output(filename):
            output_files.append(filename)
        elif should_move_to_state(filename):
            state_files.append(filename)
    
    # Print summary of what will be moved
    if output_files:
        print(f"Will move {len(output_files)} files to data/output/:")
        for f in output_files:
            print(f"  - {f}")
    
    if state_files:
        print(f"Will move {len(state_files)} files to data/state/:")
        for f in state_files:
            print(f"  - {f}")
    
    if not output_files and not state_files:
        print("No files to move.")
        return
    
    # Ask for confirmation
    if not 'CI' in os.environ:
        confirmation = input("\nProceed with moving these files? [y/N] ").lower().strip()
        if confirmation != 'y':
            print("Operation cancelled.")
            return
    
    # Move files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for filename in output_files:
        dest = os.path.join("data", "output", filename)
        print(f"Moving {filename} to {dest}")
        shutil.move(filename, dest)
    
    for filename in state_files:
        dest = os.path.join("data", "state", filename)
        print(f"Moving {filename} to {dest}")
        shutil.move(filename, dest)
    
    print(f"\nSuccessfully moved {len(output_files)} output files and {len(state_files)} state files.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Usage: python move_output_files.py")
        print("This script moves existing output files to the new directory structure.")
        print("It will scan for output files in the root directory and move them to data/output/ or data/state/.")
        sys.exit(0)
    
    ensure_directories()
    move_files()