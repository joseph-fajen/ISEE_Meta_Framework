#!/usr/bin/env python3
"""
ISEE Raw Response Storage Enabler

This script modifies the ISEE main.py file to save raw LLM responses to disk
during execution, allowing complete access to all individual responses.

Usage:
    python enable_raw_response_storage.py [--backup] [--undo]
    
Options:
    --backup    Create a backup of main.py before modification
    --undo      Restore from backup (reverses the modification)
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

class ISEEResponseStorageEnabler:
    def __init__(self):
        self.main_py_path = Path("main.py")
        self.backup_path = Path("main.py.backup")
        
    def create_backup(self) -> bool:
        """Create a backup of the main.py file."""
        try:
            shutil.copy2(self.main_py_path, self.backup_path)
            print(f"✅ Created backup: {self.backup_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return False
    
    def restore_backup(self) -> bool:
        """Restore from backup."""
        try:
            if not self.backup_path.exists():
                print(f"❌ Backup file not found: {self.backup_path}")
                return False
            
            shutil.copy2(self.backup_path, self.main_py_path)
            print(f"✅ Restored from backup: {self.backup_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to restore backup: {e}")
            return False
    
    def add_response_storage(self) -> bool:
        """Modify main.py to add raw response storage functionality."""
        try:
            with open(self.main_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if already modified
            if 'save_raw_response' in content:
                print("✅ Raw response storage already enabled in main.py")
                return True
            
            # Find the ISEEFramework class and add the new method
            class_insertion = '''
    def save_raw_response(self, result: Dict[str, Any], combination: Dict[str, Any]) -> None:
        """Save raw response text to individual files."""
        try:
            # Create responses directory
            responses_dir = Path(self.output_directory) / "raw_responses"
            responses_dir.mkdir(exist_ok=True)
            
            # Generate filename
            combo_id = result.get("combination_id", "unknown")
            model_name = combination.get("model", "unknown").replace("/", "_")
            template_id = combination.get("template", "unknown")
            
            filename = f"{combo_id}_{model_name}_{template_id}.md"
            filepath = responses_dir / filename
            
            # Save response with metadata
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Raw Response Data\\n\\n")
                f.write(f"**Combination ID:** {combo_id}\\n")
                f.write(f"**Model:** {combination.get('model', 'Unknown')}\\n")
                f.write(f"**Template:** {combination.get('template', 'Unknown')}\\n")
                f.write(f"**Domain:** {combination.get('domain', 'Unknown')}\\n")
                f.write(f"**Query:** {combination.get('query', 'Unknown')}\\n")
                f.write(f"**Timestamp:** {result.get('metadata', {}).get('timestamp', 'Unknown')}\\n")
                f.write(f"**Duration:** {result.get('metadata', {}).get('duration', 'Unknown')}s\\n\\n")
                f.write(f"## Prompt Sent to Model\\n\\n")
                f.write(f"```\\n{result.get('prompt', 'Prompt not available')}\\n```\\n\\n")
                f.write(f"## Raw Response\\n\\n")
                f.write(result.get("response", "Response not available"))
                
        except Exception as e:
            print(f"Warning: Failed to save raw response for {combo_id}: {e}")
'''
            
            # Insert the method into the ISEEFramework class
            # Find the ISEEApplication class and insert the method
            class_start = content.find('class ISEEApplication:')
            if class_start == -1:
                print("❌ Could not find ISEEApplication class")
                return False
            
            # Find the execute_combinations method to insert before it
            execute_method = content.find('    def execute_combinations(')
            if execute_method == -1:
                print("❌ Could not find execute_combinations method")
                return False
            
            # Insert the new method before execute_combinations
            modified_content = content[:execute_method] + class_insertion + "\n" + content[execute_method:]
            
            # Find where results are processed and add saving call
            # Look for the line where results are stored
            original_line = '            self.results[combo["id"]] = result'
            result_processing = '''            self.results[combo["id"]] = result
            
            # Save raw response to disk
            self.save_raw_response(result, combo)'''
            
            if original_line in modified_content:
                modified_content = modified_content.replace(
                    original_line, 
                    result_processing
                )
            else:
                print("❌ Could not find result storage line to modify")
                return False
            
            # Add import for Path at the top
            if "from pathlib import Path" not in modified_content:
                import_section = "import time\nimport json\nimport csv\nfrom pathlib import Path"
                modified_content = modified_content.replace("import time\nimport json\nimport csv", import_section)
            
            # Write the modified content
            with open(self.main_py_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            print("✅ Successfully added raw response storage to main.py")
            return True
            
        except Exception as e:
            print(f"❌ Failed to modify main.py: {e}")
            return False
    
    def create_response_reader(self) -> None:
        """Create a script to read saved raw responses."""
        reader_script = '''#!/usr/bin/env python3
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
        print(f"\\n{'='*80}")
        print(f"Response {i}/{len(response_files)}: {filepath.name}")
        print('='*80)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
        
        if i < len(response_files):
            input("\\nPress Enter to continue to next response...")

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
    
    print(f"\\nRaw Responses in {run_directory}:")
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
'''
        
        with open("read_raw_responses.py", 'w', encoding='utf-8') as f:
            f.write(reader_script)
        
        # Make it executable
        os.chmod("read_raw_responses.py", 0o755)
        print("✅ Created read_raw_responses.py script")

def main():
    parser = argparse.ArgumentParser(description="Enable raw response storage in ISEE")
    parser.add_argument("--backup", action="store_true", help="Create backup before modification")
    parser.add_argument("--undo", action="store_true", help="Restore from backup")
    
    args = parser.parse_args()
    
    enabler = ISEEResponseStorageEnabler()
    
    print("🔧 ISEE Raw Response Storage Enabler")
    print("="*50)
    
    if args.undo:
        if enabler.restore_backup():
            print("✅ Successfully restored main.py from backup")
        else:
            print("❌ Failed to restore backup")
        return
    
    if not enabler.main_py_path.exists():
        print(f"❌ main.py not found in current directory")
        return
    
    # Create backup if requested
    if args.backup:
        if not enabler.create_backup():
            print("❌ Backup failed, aborting modification")
            return
    
    # Add response storage functionality
    if enabler.add_response_storage():
        print("✅ Raw response storage enabled successfully!")
        
        # Create reader script
        enabler.create_response_reader()
        
        print("\\n📋 Next Steps:")
        print("1. Run ISEE normally: python main.py --query 'your query' ...")
        print("2. Raw responses will be saved to: [output_dir]/raw_responses/")
        print("3. Use read_raw_responses.py to view saved responses")
        print("4. Use --undo to restore original main.py if needed")
        
    else:
        print("❌ Failed to enable raw response storage")

if __name__ == "__main__":
    main()