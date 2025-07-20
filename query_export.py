"""
Query Export Module for ISEE Framework

This module provides functionality to export detailed query combinations
for analysis and debugging purposes.
"""

import csv
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

def export_query_combinations_csv(
    combinations: List[Dict[str, Any]], 
    output_path: str,
    include_variations_analysis: bool = True
) -> str:
    """
    Export query combinations to a detailed CSV file.
    
    Args:
        combinations: List of combination dictionaries from generate_combinations()
        output_path: Path to save the CSV file
        include_variations_analysis: Whether to include dynamic variation analysis data
        
    Returns:
        Path to the created CSV file
    """
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        # Define CSV columns
        fieldnames = [
            'combination_id',
            'query_text', 
            'query_type',  # 'original' or 'variation'
            'variation_strategy',
            'variation_confidence',
            'complexity_analysis',
            'domain_analysis',
            'protective_mode',
            'model_id',
            'model_name',
            'framework_id',
            'framework_name',
            'domain_id',
            'domain_name',
            'instruction_template',
            'complete_prompt'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Process each combination
        for combo in combinations:
            # Extract query information
            query = combo.get('query', {})
            query_text = query.get('text', 'Unknown Query')
            query_variables = query.get('variables', {})
            
            # Determine if this is a variation
            is_variation = 'variation_strategy' in query_variables
            query_type = 'variation' if is_variation else 'original'
            
            # Extract variation metadata
            variation_strategy = query_variables.get('variation_strategy', '')
            variation_confidence = query_variables.get('variation_confidence', '')
            
            # Extract dynamic analysis data if available
            dynamic_analysis = query_variables.get('dynamic_analysis', {})
            complexity_analysis = dynamic_analysis.get('complexity', '')
            domain_analysis = dynamic_analysis.get('domain', '')
            protective_mode = dynamic_analysis.get('protective_mode', '')
            
            # Extract other combination data
            model = combo.get('model', {})
            framework = combo.get('framework', {})
            domain = combo.get('domain', {})
            instruction = combo.get('instruction', {})
            
            # Build complete prompt (simplified version)
            complete_prompt = f"{instruction.get('text', 'Unknown Instruction')}: {query_text}"
            if domain.get('name'):
                complete_prompt += f" (Domain: {domain.get('name')})"
            
            # Write row to CSV
            writer.writerow({
                'combination_id': combo.get('id', 'unknown'),
                'query_text': query_text,
                'query_type': query_type,
                'variation_strategy': variation_strategy,
                'variation_confidence': variation_confidence,
                'complexity_analysis': complexity_analysis,
                'domain_analysis': domain_analysis,
                'protective_mode': protective_mode,
                'model_id': model.get('id', 'unknown'),
                'model_name': model.get('name', 'Unknown Model'),
                'framework_id': framework.get('id', 'unknown'),
                'framework_name': framework.get('name', 'Unknown Framework'),
                'domain_id': domain.get('id', 'unknown'),
                'domain_name': domain.get('name', 'Unknown Domain'),
                'instruction_template': instruction.get('name', 'Unknown Template'),
                'complete_prompt': complete_prompt
            })
    
    return output_path

def export_query_summary_json(
    combinations: List[Dict[str, Any]], 
    output_path: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Export a JSON summary of query combinations with metadata.
    
    Args:
        combinations: List of combination dictionaries
        output_path: Path to save the JSON file
        metadata: Optional metadata to include (timestamps, settings, etc.)
        
    Returns:
        Path to the created JSON file
    """
    
    # Count statistics
    total_combinations = len(combinations)
    original_queries = sum(1 for c in combinations if not c.get('query', {}).get('variables', {}).get('variation_strategy'))
    variation_queries = total_combinations - original_queries
    
    # Extract unique elements
    unique_models = set(c.get('model', {}).get('id', 'unknown') for c in combinations)
    unique_frameworks = set(c.get('framework', {}).get('id', 'unknown') for c in combinations)
    unique_domains = set(c.get('domain', {}).get('id', 'unknown') for c in combinations)
    
    # Group variations by strategy
    variation_strategies = {}
    for combo in combinations:
        strategy = combo.get('query', {}).get('variables', {}).get('variation_strategy')
        if strategy:
            variation_strategies[strategy] = variation_strategies.get(strategy, 0) + 1
    
    summary = {
        'export_timestamp': datetime.now().isoformat(),
        'metadata': metadata or {},
        'statistics': {
            'total_combinations': total_combinations,
            'original_queries': original_queries,
            'variation_queries': variation_queries,
            'unique_models': len(unique_models),
            'unique_frameworks': len(unique_frameworks),
            'unique_domains': len(unique_domains)
        },
        'variation_strategies': variation_strategies,
        'models_used': list(unique_models),
        'frameworks_used': list(unique_frameworks),
        'domains_used': list(unique_domains),
        'sample_queries': [
            {
                'type': 'original' if not c.get('query', {}).get('variables', {}).get('variation_strategy') else 'variation',
                'text': c.get('query', {}).get('text', 'Unknown'),
                'strategy': c.get('query', {}).get('variables', {}).get('variation_strategy', ''),
                'model': c.get('model', {}).get('name', 'Unknown'),
                'framework': c.get('framework', {}).get('name', 'Unknown'),
                'domain': c.get('domain', {}).get('name', 'Unknown')
            }
            for c in combinations[:5]  # First 5 as samples
        ]
    }
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(summary, jsonfile, indent=2, ensure_ascii=False)
    
    return output_path

def create_query_export_filename(base_name: str, output_dir: str, extension: str = 'csv') -> str:
    """
    Create a timestamped filename for query exports.
    
    Args:
        base_name: Base name for the file (e.g., 'queries_detailed')
        output_dir: Output directory path
        extension: File extension (without dot)
        
    Returns:
        Full path to the export file
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{base_name}_{timestamp}.{extension}"
    return os.path.join(output_dir, filename)

# Convenience function for typical usage
def auto_export_queries(
    combinations: List[Dict[str, Any]], 
    output_dir: str,
    run_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Automatically export queries in both CSV and JSON formats.
    
    Args:
        combinations: List of combination dictionaries
        output_dir: Output directory for export files
        run_metadata: Optional metadata about the run
        
    Returns:
        Dictionary with paths to created files
    """
    
    # Create timestamped filenames
    csv_path = create_query_export_filename('queries_detailed', output_dir, 'csv')
    json_path = create_query_export_filename('queries_summary', output_dir, 'json')
    
    # Export both formats
    csv_file = export_query_combinations_csv(combinations, csv_path)
    json_file = export_query_summary_json(combinations, json_path, run_metadata)
    
    return {
        'csv': csv_file,
        'json': json_file,
        'count': len(combinations)
    }