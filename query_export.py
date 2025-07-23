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
    include_variations_analysis: bool = True,
    isee_engine=None
) -> str:
    """
    Export query combinations to a detailed CSV file.
    
    Args:
        combinations: List of combination dictionaries from generate_combinations()
        output_path: Path to save the CSV file
        include_variations_analysis: Whether to include dynamic variation analysis data
        isee_engine: Optional ISEE engine instance for looking up full objects
        
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
            # Handle both old format (simple IDs) and new format (full objects)
            
            # Extract query information
            query_data = combo.get('query', {})
            if isinstance(query_data, str):
                # Old format: query is just an ID string
                query_id = query_data
                query_text = f"Query {query_id}"
                query_variables = {}
                
                # Try to look up full query if engine provided
                if isee_engine and hasattr(isee_engine, 'query_generator'):
                    try:
                        full_query = isee_engine.query_generator.get_query_by_id(query_id)
                        if full_query:
                            query_text = full_query.text
                            query_variables = getattr(full_query, 'variables', {})
                    except Exception as e:
                        # Log the error for debugging but don't fail
                        print(f"Warning: Could not look up query {query_id}: {e}")
                        pass
            else:
                # New format: query is a dict with full data
                query_text = query_data.get('text', 'Unknown Query')
                query_variables = query_data.get('variables', {})
            
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
            
            # Extract model information
            model_data = combo.get('model', {})
            if isinstance(model_data, str):
                # Old format: model is just an ID string
                model_id = model_data
                model_name = f"Model {model_id}"
                
                # Try to look up full model name if engine provided
                if isee_engine and hasattr(isee_engine, 'model_configs'):
                    try:
                        model_config = isee_engine.model_configs.get(model_id, {})
                        model_name = model_config.get('name', model_name)
                    except:
                        pass
            else:
                # New format: model is a dict
                model_id = model_data.get('id', 'unknown')
                model_name = model_data.get('name', 'Unknown Model')
            
            # Extract framework/template information
            template_data = combo.get('template', combo.get('framework', {}))
            if isinstance(template_data, str):
                # Old format: template is just an ID string
                template_id = template_data
                template_name = f"Template {template_id}"
                
                # Try to look up full template if engine provided
                if isee_engine and hasattr(isee_engine, 'template_library'):
                    try:
                        full_template = isee_engine.template_library.get_template(template_id)
                        template_name = full_template.name
                    except:
                        pass
            else:
                # New format: template is a dict
                template_id = template_data.get('id', 'unknown')
                template_name = template_data.get('name', 'Unknown Template')
            
            # Extract domain information
            domain_data = combo.get('domain', {})
            if isinstance(domain_data, str):
                # Old format: domain is just an ID string
                domain_id = domain_data
                # Handle dynamic domains specially
                if domain_id.startswith('dynamic:'):
                    dynamic_name = domain_id.replace('dynamic:', '')
                    domain_name = dynamic_name  # Clean name without prefix
                else:
                    domain_name = f"Domain {domain_id}"
                
                # Try to look up full domain if engine provided
                if isee_engine and hasattr(isee_engine, 'domain_manager'):
                    try:
                        full_domain = isee_engine.domain_manager.get_domain(domain_id)
                        domain_name = full_domain.name
                    except:
                        pass
            else:
                # New format: domain is a dict
                domain_id = domain_data.get('id', 'unknown')
                domain_name = domain_data.get('name', 'Unknown Domain')
            
            # Build complete prompt using the REAL prompt construction logic
            complete_prompt = f"{template_name}: {query_text}"
            if domain_name and domain_name != 'Unknown Domain':
                complete_prompt += f" (Domain: {domain_name})"
            
            # Try to build the ACTUAL complete prompt that gets sent to LLMs
            if isee_engine:
                try:
                    # Get the actual instruction template
                    template_obj = None
                    if hasattr(isee_engine, 'template_library'):
                        template_obj = isee_engine.template_library.get_template(template_id)
                    
                    # For dynamic domains, use proper formatted description
                    if domain_id.startswith('dynamic:'):
                        dynamic_name = domain_id.replace('dynamic:', '')
                        domain_description = f"the Domain of {dynamic_name}"
                    else:
                        domain_description = domain_name
                    if hasattr(isee_engine, 'domain_manager') and not domain_id.startswith('dynamic:'):
                        try:
                            domain_obj = isee_engine.domain_manager.get_domain(domain_id)
                            domain_description = domain_obj.description
                        except:
                            pass
                    
                    # Use the actual query text we already extracted
                    # (whether from original query or variation)
                    actual_query_text = query_text
                    
                    # If we have the template, build the real prompt
                    if template_obj:
                        # Create a simple variables dict for template formatting
                        template_variables = {"domain": domain_description}
                        
                        formatted_instruction = template_obj.format(template_variables)
                        complete_prompt = f"{formatted_instruction}\n\n{actual_query_text}"
                        
                except Exception as e:
                    # Fall back to simplified version if anything fails
                    print(f"Warning: Could not build complete prompt for {combo.get('id', 'unknown')}: {e}")
                    pass
            
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
                'model_id': model_id,
                'model_name': model_name,
                'framework_id': template_id,
                'framework_name': template_name,
                'domain_id': domain_id,
                'domain_name': domain_name,
                'instruction_template': template_name,
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
    
    # Handle both old format (string IDs) and new format (dict objects)
    original_queries = 0
    for c in combinations:
        query_data = c.get('query', {})
        if isinstance(query_data, str):
            # Old format: assume all are original queries unless we can determine otherwise
            original_queries += 1
        else:
            # New format: check for variation_strategy
            if not query_data.get('variables', {}).get('variation_strategy'):
                original_queries += 1
    
    variation_queries = total_combinations - original_queries
    
    # Extract unique elements (handle both formats)
    unique_models = set()
    unique_frameworks = set()
    unique_domains = set()
    
    for c in combinations:
        # Model IDs
        model_data = c.get('model', {})
        if isinstance(model_data, str):
            unique_models.add(model_data)
        else:
            unique_models.add(model_data.get('id', 'unknown'))
        
        # Framework IDs
        framework_data = c.get('framework', c.get('template', {}))
        if isinstance(framework_data, str):
            unique_frameworks.add(framework_data)
        else:
            unique_frameworks.add(framework_data.get('id', 'unknown'))
        
        # Domain IDs
        domain_data = c.get('domain', {})
        if isinstance(domain_data, str):
            unique_domains.add(domain_data)
        else:
            unique_domains.add(domain_data.get('id', 'unknown'))
    
    # Group variations by strategy
    variation_strategies = {}
    for combo in combinations:
        query_data = combo.get('query', {})
        if isinstance(query_data, str):
            # Old format: no variation strategy info available
            continue
        else:
            # New format: check for variation_strategy
            strategy = query_data.get('variables', {}).get('variation_strategy')
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
        'sample_queries': []
    }
    
    # Generate sample queries (first 5 combinations)
    for c in combinations[:5]:
        query_data = c.get('query', {})
        model_data = c.get('model', {})
        framework_data = c.get('framework', c.get('template', {}))
        domain_data = c.get('domain', {})
        
        # Handle both formats
        if isinstance(query_data, str):
            query_type = 'original'
            query_text = f'Query {query_data}'
            strategy = ''
        else:
            query_type = 'original' if not query_data.get('variables', {}).get('variation_strategy') else 'variation'
            query_text = query_data.get('text', 'Unknown')
            strategy = query_data.get('variables', {}).get('variation_strategy', '')
        
        if isinstance(model_data, str):
            model_name = f'Model {model_data}'
        else:
            model_name = model_data.get('name', 'Unknown')
            
        if isinstance(framework_data, str):
            framework_name = f'Framework {framework_data}'
        else:
            framework_name = framework_data.get('name', 'Unknown')
            
        if isinstance(domain_data, str):
            domain_name = f'Domain {domain_data}'
        else:
            domain_name = domain_data.get('name', 'Unknown')
        
        summary['sample_queries'].append({
            'type': query_type,
            'text': query_text,
            'strategy': strategy,
            'model': model_name,
            'framework': framework_name,
            'domain': domain_name
        })
    
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
    run_metadata: Optional[Dict[str, Any]] = None,
    isee_engine=None
) -> Dict[str, str]:
    """
    Automatically export queries in both CSV and JSON formats.
    
    Args:
        combinations: List of combination dictionaries
        output_dir: Output directory for export files
        run_metadata: Optional metadata about the run
        isee_engine: Optional ISEE engine instance for looking up full objects
        
    Returns:
        Dictionary with paths to created files
    """
    
    # Create timestamped filenames
    csv_path = create_query_export_filename('queries_detailed', output_dir, 'csv')
    json_path = create_query_export_filename('queries_summary', output_dir, 'json')
    
    # Export both formats
    csv_file = export_query_combinations_csv(combinations, csv_path, True, isee_engine)
    json_file = export_query_summary_json(combinations, json_path, run_metadata)
    
    return {
        'csv': csv_file,
        'json': json_file,
        'count': len(combinations)
    }