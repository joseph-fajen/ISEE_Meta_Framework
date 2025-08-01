#!/usr/bin/env python3
"""
Script to undo ISEE run folder organization
"""
import os
import shutil

def undo_organization():
    output_dir = "/Users/josephfajen/git/ISEE_Meta_Framework/data/output"
    log_file = os.path.join(output_dir, "organization_log.txt")
    
    if not os.path.exists(log_file):
        print("No organization log found. Cannot undo.")
        return
    
    os.chdir(output_dir)
    
    # Read moves from log
    with open(log_file, "r") as f:
        lines = f.readlines()
    
    moves = []
    for line in lines:
        line = line.strip()
        if " -> " in line and not line.startswith("=") and "Log" not in line:
            parts = line.split(" -> ")
            if len(parts) == 2:
                moves.append((parts[0], parts[1]))
    
    print(f"Found {len(moves)} moves to undo...")
    
    # Undo moves in reverse order
    for original, moved_to in reversed(moves):
        if os.path.exists(moved_to):
            print(f"Restoring {moved_to} -> {original}")
            shutil.move(moved_to, original)
        else:
            print(f"Warning: {moved_to} not found")
    
    # Remove empty directories
    empty_dirs = []
    for root, dirs, files in os.walk(".", topdown=False):
        if root != "." and not files and not dirs:
            empty_dirs.append(root)
    
    for dir_path in empty_dirs:
        try:
            os.rmdir(dir_path)
            print(f"Removed empty directory: {dir_path}")
        except OSError:
            pass
    
    # Remove symlink
    if os.path.islink("latest"):
        os.unlink("latest")
        print("Removed 'latest' symlink")
    
    print("Organization undone successfully!")

if __name__ == "__main__":
    undo_organization()