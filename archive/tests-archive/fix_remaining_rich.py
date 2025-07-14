#!/usr/bin/env python3
"""
Script to fix remaining RICH_AVAILABLE references.
"""
import re

def fix_remaining_rich_references(filename):
    """Fix remaining RICH_AVAILABLE references by removing conditionals."""
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Count original references
    original_count = content.count('RICH_AVAILABLE')
    print(f"Found {original_count} RICH_AVAILABLE references")
    
    # Pattern for simple conditional blocks: if RICH_AVAILABLE: ... else: ...
    # This handles most remaining cases
    lines = content.split('\n')
    result_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a RICH_AVAILABLE conditional
        if 'if RICH_AVAILABLE:' in line:
            # Get the indentation level
            indent_match = re.match(r'^(\s*)', line)
            base_indent = indent_match.group(1) if indent_match else ''
            rich_indent = base_indent + '    '
            
            # Collect Rich implementation lines
            rich_lines = []
            i += 1
            
            # Collect lines until we hit 'else:' at the same indentation level
            while i < len(lines):
                current_line = lines[i]
                
                # Check if this is the else clause
                if current_line.strip() == 'else:' and current_line.startswith(base_indent) and len(current_line) == len(base_indent) + 5:
                    # Skip the else and collect fallback lines until next unindented line
                    i += 1
                    while i < len(lines) and (lines[i].startswith(rich_indent) or lines[i].strip() == ''):
                        i += 1
                    break
                # Check if this line belongs to the Rich block
                elif current_line.startswith(rich_indent) or current_line.strip() == '':
                    # Remove extra indentation and add to rich_lines
                    if current_line.strip():
                        dedented = base_indent + current_line[len(rich_indent):]
                        rich_lines.append(dedented)
                    else:
                        rich_lines.append(current_line)
                    i += 1
                else:
                    # End of Rich block without else clause
                    break
            
            # Add the dedented Rich lines
            result_lines.extend(rich_lines)
        else:
            result_lines.append(line)
            i += 1
    
    new_content = '\n'.join(result_lines)
    new_count = new_content.count('RICH_AVAILABLE')
    removed = original_count - new_count
    
    print(f"Removed {removed} RICH_AVAILABLE references")
    print(f"Remaining: {new_count}")
    
    return new_content

if __name__ == "__main__":
    filename = "command_wizard.py"
    print(f"Fixing remaining RICH_AVAILABLE references in {filename}...")
    
    # Backup
    with open(filename, 'r') as f:
        original = f.read()
    
    with open(f"{filename}.backup2", 'w') as f:
        f.write(original)
    
    # Fix
    fixed = fix_remaining_rich_references(filename)
    
    # Write result
    with open(filename, 'w') as f:
        f.write(fixed)
    
    print("Fix complete!")
    print(f"Backup saved to {filename}.backup2")