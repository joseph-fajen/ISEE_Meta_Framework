#!/usr/bin/env python3
"""
Categorize files for archiving by development phase.
"""
import os
import glob

def categorize_files_for_archiving():
    """Categorize files by development phase for archiving"""
    
    # Files to archive by phase
    cli_phase_files = [
        'command_wizard.py*',
        'isee_prototype_pseudocode.py',
        # CLI-specific components
    ]
    
    rich_cli_phase_files = [
        'configuration_dashboard.py',
        'enhanced_parameter_editor.py', 
        'interactive_dashboard_controller.py',
        'unified_parameter_editor.py',
        'parameter_context.py',
        'domain_parameter_editor.py',
        'models_parameter_editor.py',
        'query_parameter_editor.py',
        'variations_parameter_editor.py',
        'enhanced_parameter_editors.py',
        'preset_manager.py',
        'purpose_categories.py',
        'update_config_domains.py',
        # Rich CLI UI components
    ]
    
    web_demo_phase_files = [
        'enhanced_test.html',
        'demo_individual_model_selection.py',
        'result_viewer.py',
        'quick_test_report.py',
        'openrouter_categorization.py',
        'performance_analysis.py',
        # Previous web demo attempts
    ]
    
    tests_and_debug_files = [
        'test_*.py',
        'debug_*.py',
        'fix_remaining_rich.py',
        'migrate_rich_only.py',
        'move_output_files.py',
        'analyze_dependencies.py',
        # All test and debug files
    ]
    
    backup_files = [
        '*.backup*',
        '*.broken',
        'unified_config_backup.json',
        # Backup and broken files
    ]
    
    # Essential files to keep (from dependency analysis)
    essential_files = {
        'app.py',
        'main.py',
        'isee-ui.html',
        'analysis.py',
        'cognitive_framework_visualizer.py',
        'cost_estimation.py',
        'domain_manager.py',
        'evaluation_scoring.py',
        'instruction_templates.py',
        'model_api_integration.py',
        'openrouter_model_collections.py',
        'openrouter_rankings_service.py',
        'query_generator.py',
        'report_generator.py',
        'reporting.py',
        'performance_tracker.py',
        'requirements.txt',
        'README.md',
        'CLAUDE.md',
        'unified_config.json',
        'openrouter_config.json',
        '.env.template',
        '.gitignore',
    }
    
    categories = {
        'cli-phase': cli_phase_files,
        'rich-cli-phase': rich_cli_phase_files,
        'web-demo-phase': web_demo_phase_files,
        'tests-archive': tests_and_debug_files,
        'backup-files': backup_files,
    }
    
    print("=== FILE CATEGORIZATION FOR ARCHIVING ===")
    
    for category, patterns in categories.items():
        print(f"\n{category.upper()}:")
        found_files = []
        for pattern in patterns:
            matches = glob.glob(pattern)
            found_files.extend(matches)
        
        for file in sorted(set(found_files)):
            if os.path.isfile(file) and file not in essential_files:
                print(f"  -> {file}")
    
    print(f"\nESSENTIAL FILES TO KEEP:")
    for file in sorted(essential_files):
        if os.path.exists(file):
            print(f"  KEEP: {file}")
    
    return categories

if __name__ == "__main__":
    categorize_files_for_archiving()