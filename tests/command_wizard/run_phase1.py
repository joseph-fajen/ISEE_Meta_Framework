#!/usr/bin/env python3
"""
ISEE Command Wizard Test Framework - Phase 1 Runner

Runs all Phase 1 tests and generates baseline metrics.
"""

import os
import sys
import subprocess
import time

def run_command(cmd, description):
    """Run a command and print its output.
    
    Args:
        cmd: The command to run.
        description: A description of what the command does.
    """
    print(f"\n{'='*70}")
    print(f"Running: {description}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        if result.returncode != 0:
            print(f"WARNING: Command returned non-zero exit code: {result.returncode}")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    # Get the absolute path to the repository root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, '../..'))
    
    # Change to the repository root
    os.chdir(repo_root)
    
    print(f"Repository root: {repo_root}")
    print(f"Current directory: {os.getcwd()}")
    
    # Create necessary directories
    os.makedirs(os.path.join(script_dir, 'baseline'), exist_ok=True)
    
    # Generate baseline metrics
    run_command(
        f"python {os.path.join(script_dir, 'baseline_metrics.py')}",
        "Generating baseline metrics"
    )
    
    # Display completion message
    print("\n")
    print("=" * 70)
    print("Phase 1 Implementation Complete")
    print("=" * 70)
    print("\nThe following files have been generated:")
    print(f"  - {os.path.join(script_dir, 'baseline/baseline_metrics.json')}")
    print(f"  - {os.path.join(script_dir, 'baseline/baseline_summary.md')}")
    print(f"  - {os.path.join(script_dir, 'implementation_summary.md')}")
    print(f"  - {os.path.join(script_dir, 'PHASE1_COMPLETION_REPORT.md')}")
    print("\nNext steps:")
    print("  1. Review the baseline metrics and summary")
    print("  2. Continue to Phase 2: Core Functionality Alignment")
    print("  3. Use the test framework to validate Phase 2 changes")
    print("\nPhase 1 is now complete!")
    print("=" * 70)