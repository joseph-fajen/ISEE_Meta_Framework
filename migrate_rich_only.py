#!/usr/bin/env python3
"""
Script to migrate command_wizard.py to Rich-only by removing RICH_AVAILABLE conditionals.
"""

import re
import sys

def migrate_rich_only(filename):
    """Remove RICH_AVAILABLE conditionals and keep only Rich implementations."""
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Pattern 1: Simple if RICH_AVAILABLE: ... else: ... blocks
    pattern1 = re.compile(
        r'(\s+)if RICH_AVAILABLE:\n'
        r'((?:\1[ ]{4}.*\n)*)'  # Rich implementation (indented 4 more spaces)
        r'\1else:\n'
        r'((?:\1[ ]{4}.*\n)*)',  # Fallback implementation
        re.MULTILINE
    )
    
    def replace_pattern1(match):
        indent = match.group(1)
        rich_code = match.group(2)
        # Remove the extra 4-space indentation from Rich code
        rich_lines = rich_code.split('\n')
        dedented_lines = []
        for line in rich_lines:
            if line.strip():  # Non-empty line
                if line.startswith(indent + '    '):
                    dedented_lines.append(indent + line[len(indent) + 4:])
                else:
                    dedented_lines.append(line)
            else:
                dedented_lines.append(line)
        return '\n'.join(dedented_lines)
    
    # Apply pattern 1
    content = pattern1.sub(replace_pattern1, content)
    
    # Pattern 2: Standalone if RICH_AVAILABLE: blocks (no else)
    pattern2 = re.compile(
        r'(\s+)if RICH_AVAILABLE:\n'
        r'((?:\1[ ]{4}.*\n)*)',  # Rich implementation only
        re.MULTILINE
    )
    
    def replace_pattern2(match):
        indent = match.group(1)
        rich_code = match.group(2)
        # Remove the extra 4-space indentation from Rich code
        rich_lines = rich_code.split('\n')
        dedented_lines = []
        for line in rich_lines:
            if line.strip():  # Non-empty line
                if line.startswith(indent + '    '):
                    dedented_lines.append(indent + line[len(indent) + 4:])
                else:
                    dedented_lines.append(line)
            else:
                dedented_lines.append(line)
        return '\n'.join(dedented_lines)
    
    # Apply pattern 2 
    content = pattern2.sub(replace_pattern2, content)
    
    return content

if __name__ == "__main__":
    filename = "command_wizard.py"
    print(f"Migrating {filename} to Rich-only...")
    
    # Backup original
    with open(filename, 'r') as f:
        original = f.read()
    
    with open(f"{filename}.backup", 'w') as f:
        f.write(original)
    
    # Migrate
    migrated = migrate_rich_only(filename)
    
    # Write result
    with open(filename, 'w') as f:
        f.write(migrated)
    
    print("Migration complete!")
    print(f"Original backed up to {filename}.backup")
    
    # Show stats
    original_lines = len(original.splitlines())
    migrated_lines = len(migrated.splitlines())
    reduction = original_lines - migrated_lines
    percentage = (reduction / original_lines) * 100
    
    print(f"File size reduction: {original_lines} → {migrated_lines} lines ({reduction} lines removed, {percentage:.1f}% reduction)")