#!/usr/bin/env python3
"""
Analyze dependencies of core working files to understand which modules are essential.
"""
import ast
import os
from pathlib import Path

def find_imports(file_path):
    """Extract all imports from a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def analyze_dependencies():
    """Analyze dependencies of core working files"""
    core_files = ['app.py', 'main.py']
    local_imports = set()
    
    for file in core_files:
        if os.path.exists(file):
            imports = find_imports(file)
            print(f'\n{file} imports:')
            for imp in sorted(set(imports)):
                print(f'  {imp}')
                # Track local module imports (no dots, likely local files)
                if '.' not in imp and not imp.startswith('_'):
                    # Check if this corresponds to a .py file in current directory
                    potential_file = f"{imp}.py"
                    if os.path.exists(potential_file):
                        local_imports.add(potential_file)
                        print(f"    -> LOCAL MODULE: {potential_file}")
    
    print(f"\nIdentified local modules used by working system:")
    for module in sorted(local_imports):
        print(f"  KEEP: {module}")
    
    return local_imports

def identify_all_python_files():
    """Get all Python files in root directory"""
    all_py_files = set()
    for item in os.listdir('.'):
        if item.endswith('.py') and os.path.isfile(item):
            all_py_files.add(item)
    
    print(f"\nAll Python files in root directory ({len(all_py_files)}):")
    for file in sorted(all_py_files):
        print(f"  {file}")
    
    return all_py_files

if __name__ == "__main__":
    print("=== ISEE Repository Dependency Analysis ===")
    
    # Analyze core dependencies
    essential_modules = analyze_dependencies()
    
    # Show all Python files
    all_files = identify_all_python_files()
    
    # Identify potential archive candidates
    potential_archive = all_files - essential_modules - {'app.py', 'main.py'}
    
    print(f"\nPotential files to archive ({len(potential_archive)}):")
    for file in sorted(potential_archive):
        print(f"  ARCHIVE: {file}")
    
    print(f"\nSummary:")
    print(f"  Essential files: {len(essential_modules) + 2}")  # +2 for app.py, main.py
    print(f"  Archive candidates: {len(potential_archive)}")
    print(f"  Total Python files: {len(all_files)}")