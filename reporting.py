"""
Reporting Module for ISEE Framework

This module provides basic reporting functionality for the ISEE Meta-Framework.
Phase 1 implementation includes:
- Run Summary Report
- Combination Metadata Report
- CSV Data Exports
"""

import os
import json
import csv
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

class ReportingSystem:
    """Reporting system for ISEE Framework."""
    
    def __init__(self, output_directory: str = "data/output", report_format: str = "markdown", export_csv: bool = False):
        """Initialize the reporting system.
        
        Args:
            output_directory: Directory to save reports to.
            report_format: Format for reports (markdown, json).
            export_csv: Whether to export data as CSV files.
        """
        self.output_directory = output_directory
        self.report_format = report_format
        self.export_csv = export_csv
        
        # Ensure the output directory exists
        os.makedirs(output_directory, exist_ok=True)
    
    def generate_run_summary(
        self,
        query: str,
        combinations: List[Dict[str, Any]],
        results: Dict[str, Any],
        evaluations: Dict[str, Dict[str, float]],
        synthesized_ideas: Dict[str, Any],
        config: Dict[str, Any],
        model_configs: Dict[str, Any],
        run_params: Dict[str, Any]
    ) -> str:
        """Generate a run summary report.
        
        Args:
            query: The query used for the run.
            combinations: List of combination dictionaries.
            results: Dictionary mapping combination IDs to results.
            evaluations: Dictionary mapping combination IDs to evaluation scores.
            synthesized_ideas: Dictionary of synthesized ideas.
            config: Configuration dictionary.
            model_configs: Model configuration dictionary.
            run_params: Run parameters dictionary.
            
        Returns:
            Report content as a string.
        """
        if self.report_format == "markdown":
            return self._generate_run_summary_markdown(
                query, combinations, results, evaluations, 
                synthesized_ideas, config, model_configs, run_params
            )
        elif self.report_format == "json":
            return self._generate_run_summary_json(
                query, combinations, results, evaluations, 
                synthesized_ideas, config, model_configs, run_params
            )
        else:
            raise ValueError(f"Unsupported report format: {self.report_format}")
    
    def _generate_run_summary_markdown(
        self,
        query: str,
        combinations: List[Dict[str, Any]],
        results: Dict[str, Any],
        evaluations: Dict[str, Dict[str, float]],
        synthesized_ideas: Dict[str, Any],
        config: Dict[str, Any],
        model_configs: Dict[str, Any],
        run_params: Dict[str, Any]
    ) -> str:
        """Generate a run summary report in Markdown format.
        
        Args:
            query: The query used for the run.
            combinations: List of combination dictionaries.
            results: Dictionary mapping combination IDs to results.
            evaluations: Dictionary mapping combination IDs to evaluation scores.
            synthesized_ideas: Dictionary of synthesized ideas.
            config: Configuration dictionary.
            model_configs: Model configuration dictionary.
            run_params: Run parameters dictionary.
            
        Returns:
            Report content as a string in Markdown format.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get unique models, instructions, and domains from combinations
        models = set()
        instructions = set() 
        domains = set()
        for combo in combinations:
            models.add(combo["model"])
            instructions.add(combo["template"])
            domains.add(combo["domain"])
        
        # Calculate statistics for response length and scores
        lengths = []
        scores = []
        for combo_id, result in results.items():
            if "response" in result:
                lengths.append(len(result["response"]))
            
            if combo_id in evaluations:
                if "overall" in evaluations[combo_id]:
                    scores.append(evaluations[combo_id]["overall"])
        
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        min_score = min(scores) if scores else 0
        max_score = max(scores) if scores else 0
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Format run parameters
        sampling_method = run_params.get("sampling_method", "exhaustive")
        max_combinations = run_params.get("max_combinations", "all")
        
        # Build the markdown report
        report = [
            "# ISEE Meta-Framework Run Summary",
            "",
            "## Run Configuration",
            f"- **Query**: \"{query}\"",
            f"- **Timestamp**: {timestamp}",
            f"- **Sampling Method**: {sampling_method}",
            f"- **Max Combinations**: {max_combinations}",
            f"- **Models Used**: {len(models)}",
            f"- **Instructions Used**: {len(instructions)}",
            f"- **Domains Used**: {len(domains)}",
            "",
            "## Run Statistics",
            f"- **Total Combinations**: {len(combinations)}",
            f"- **Executed Combinations**: {len(results)}",
            f"- **Average Response Length**: {int(avg_length):,} characters",
        ]
        
        if scores:
            report.extend([
                f"- **Min Score**: {min_score:.3f}",
                f"- **Max Score**: {max_score:.3f}",
                f"- **Average Score**: {avg_score:.3f}",
            ])
        
        # Add top synthesized ideas
        if synthesized_ideas:
            report.extend([
                "",
                "## Top Synthesized Ideas",
            ])
            
            for i, (idea_id, idea) in enumerate(synthesized_ideas.items(), 1):
                # Calculate average score from source combinations
                source_scores = []
                source_models = {}
                
                if "source_combinations" in idea:
                    for source_id in idea["source_combinations"]:
                        if source_id in evaluations and "overall" in evaluations[source_id]:
                            source_scores.append(evaluations[source_id]["overall"])
                        
                        # Track which models contributed to this idea
                        if source_id in results and "metadata" in results[source_id]:
                            model = results[source_id]["metadata"].get("model", "unknown")
                            source_models[model] = source_models.get(model, 0) + 1
                
                avg_source_score = sum(source_scores) / len(source_scores) if source_scores else 0
                
                # Format model contributions
                model_contributions = []
                total_sources = sum(source_models.values())
                for model, count in source_models.items():
                    # Get model name from config if available
                    model_name = model
                    if model in model_configs:
                        model_name = model_configs[model].get("name", model)
                    
                    percentage = (count / total_sources) * 100 if total_sources > 0 else 0
                    model_contributions.append(f"{model_name} ({percentage:.1f}%)")
                
                # Add the idea to the report
                report.extend([
                    f"{i}. **{idea.get('title', f'Synthesized Idea {i}')}** (Avg Score: {avg_source_score:.4f})",
                    f"   - Primary Contributors: {', '.join(model_contributions)}" if model_contributions else "   - No contributor information available",
                    f"   - Key Points: {idea.get('description', 'No description available')}",
                    ""
                ])
        
        # Add top individual responses
        if evaluations:
            report.extend([
                "## Top Individual Responses",
            ])
            
            # Sort combinations by overall score
            scored_combos = [(combo_id, evaluations[combo_id].get("overall", 0)) 
                            for combo_id in evaluations 
                            if combo_id in results]
            
            # Sort by score in descending order
            scored_combos.sort(key=lambda x: x[1], reverse=True)
            
            # Take top 3 (or fewer if available)
            top_n = min(3, len(scored_combos))
            for i, (combo_id, score) in enumerate(scored_combos[:top_n], 1):
                # Get model and instruction information
                combo_parts = combo_id.split("_")
                model_id = combo_parts[0]
                if len(combo_parts) > 1:
                    model_id = f"{combo_parts[0]}_{combo_parts[1]}"
                
                instruction_id = combo_parts[2] if len(combo_parts) > 2 else ""
                
                # Get model name from config if available
                model_name = model_id
                if model_id in model_configs:
                    model_name = model_configs[model_id].get("name", model_id)
                
                # Get instruction name based on the id template
                instruction_name = instruction_id.replace("ins_", "").capitalize()
                
                report.append(f"{i}. **{model_name} with {instruction_name} Instruction** (Score: {score:.3f})")
        
        # Join with line breaks
        return "\n".join(report)
    
    def _generate_run_summary_json(
        self,
        query: str,
        combinations: List[Dict[str, Any]],
        results: Dict[str, Any],
        evaluations: Dict[str, Dict[str, float]],
        synthesized_ideas: Dict[str, Any],
        config: Dict[str, Any],
        model_configs: Dict[str, Any],
        run_params: Dict[str, Any]
    ) -> str:
        """Generate a run summary report in JSON format.
        
        Args:
            query: The query used for the run.
            combinations: List of combination dictionaries.
            results: Dictionary mapping combination IDs to results.
            evaluations: Dictionary mapping combination IDs to evaluation scores.
            synthesized_ideas: Dictionary of synthesized ideas.
            config: Configuration dictionary.
            model_configs: Model configuration dictionary.
            run_params: Run parameters dictionary.
            
        Returns:
            Report content as a JSON string.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get unique models, instructions, and domains from combinations
        models = set()
        instructions = set()
        domains = set()
        for combo in combinations:
            models.add(combo["model"])
            instructions.add(combo["template"])
            domains.add(combo["domain"])
        
        # Calculate statistics for response length and scores
        lengths = []
        scores = []
        for combo_id, result in results.items():
            if "response" in result:
                lengths.append(len(result["response"]))
            
            if combo_id in evaluations:
                if "overall" in evaluations[combo_id]:
                    scores.append(evaluations[combo_id]["overall"])
        
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        min_score = min(scores) if scores else 0
        max_score = max(scores) if scores else 0
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Format run parameters
        sampling_method = run_params.get("sampling_method", "exhaustive")
        max_combinations = run_params.get("max_combinations", "all")
        
        # Build the top ideas section
        top_ideas = []
        if synthesized_ideas:
            for idea_id, idea in synthesized_ideas.items():
                # Calculate average score from source combinations
                source_scores = []
                source_models = {}
                
                if "source_combinations" in idea:
                    for source_id in idea["source_combinations"]:
                        if source_id in evaluations and "overall" in evaluations[source_id]:
                            source_scores.append(evaluations[source_id]["overall"])
                        
                        # Track which models contributed to this idea
                        if source_id in results and "metadata" in results[source_id]:
                            model = results[source_id]["metadata"].get("model", "unknown")
                            source_models[model] = source_models.get(model, 0) + 1
                
                avg_source_score = sum(source_scores) / len(source_scores) if source_scores else 0
                
                # Format model contributions
                model_contributions = {}
                total_sources = sum(source_models.values())
                for model, count in source_models.items():
                    # Get model name from config if available
                    model_name = model
                    if model in model_configs:
                        model_name = model_configs[model].get("name", model)
                    
                    percentage = (count / total_sources) * 100 if total_sources > 0 else 0
                    model_contributions[model_name] = {
                        "count": count,
                        "percentage": percentage
                    }
                
                # Add the idea to the report
                top_ideas.append({
                    "id": idea_id,
                    "title": idea.get("title", f"Synthesized Idea"),
                    "description": idea.get("description", "No description available"),
                    "avg_score": avg_source_score,
                    "contributors": model_contributions
                })
        
        # Build the top responses section
        top_responses = []
        if evaluations:
            # Sort combinations by overall score
            scored_combos = [(combo_id, evaluations[combo_id].get("overall", 0)) 
                             for combo_id in evaluations 
                             if combo_id in results]
            
            # Sort by score in descending order
            scored_combos.sort(key=lambda x: x[1], reverse=True)
            
            # Take top 3 (or fewer if available)
            top_n = min(3, len(scored_combos))
            for i, (combo_id, score) in enumerate(scored_combos[:top_n], 1):
                # Get model and instruction information
                combo_parts = combo_id.split("_")
                model_id = combo_parts[0]
                if len(combo_parts) > 1:
                    model_id = f"{combo_parts[0]}_{combo_parts[1]}"
                
                instruction_id = combo_parts[2] if len(combo_parts) > 2 else ""
                
                # Get model name from config if available
                model_name = model_id
                if model_id in model_configs:
                    model_name = model_configs[model_id].get("name", model_id)
                
                # Get instruction name based on the id template
                instruction_name = instruction_id.replace("ins_", "").capitalize()
                
                top_responses.append({
                    "rank": i,
                    "combination_id": combo_id,
                    "model": model_name,
                    "instruction": instruction_name,
                    "score": score
                })
        
        # Build the complete JSON report
        report_data = {
            "run_configuration": {
                "query": query,
                "timestamp": timestamp,
                "sampling_method": sampling_method,
                "max_combinations": max_combinations,
                "models_count": len(models),
                "instructions_count": len(instructions),
                "domains_count": len(domains)
            },
            "run_statistics": {
                "total_combinations": len(combinations),
                "executed_combinations": len(results),
                "avg_response_length": int(avg_length),
                "min_score": min_score if scores else None,
                "max_score": max_score if scores else None,
                "avg_score": avg_score if scores else None
            },
            "top_ideas": top_ideas,
            "top_responses": top_responses
        }
        
        # Return as formatted JSON string
        return json.dumps(report_data, indent=2)
    
    def generate_metadata_report(
        self,
        combinations: List[Dict[str, Any]],
        results: Dict[str, Any],
        evaluations: Dict[str, Dict[str, float]],
        model_configs: Dict[str, Any],
        instruction_templates: Dict[str, Any]
    ) -> str:
        """Generate a metadata report for all combinations.
        
        Args:
            combinations: List of combination dictionaries.
            results: Dictionary mapping combination IDs to results.
            evaluations: Dictionary mapping combination IDs to evaluation scores.
            model_configs: Model configuration dictionary.
            instruction_templates: Dictionary of instruction templates.
            
        Returns:
            Report content as a string.
        """
        if self.report_format == "markdown":
            return self._generate_metadata_report_markdown(
                combinations, results, evaluations, model_configs, instruction_templates
            )
        elif self.report_format == "json":
            return self._generate_metadata_report_json(
                combinations, results, evaluations, model_configs, instruction_templates
            )
        else:
            raise ValueError(f"Unsupported report format: {self.report_format}")
    
    def _generate_metadata_report_markdown(
        self,
        combinations: List[Dict[str, Any]],
        results: Dict[str, Any],
        evaluations: Dict[str, Dict[str, float]],
        model_configs: Dict[str, Any],
        instruction_templates: Dict[str, Any]
    ) -> str:
        """Generate a metadata report in Markdown format.
        
        Args:
            combinations: List of combination dictionaries.
            results: Dictionary mapping combination IDs to results.
            evaluations: Dictionary mapping combination IDs to evaluation scores.
            model_configs: Model configuration dictionary.
            instruction_templates: Dictionary of instruction templates.
            
        Returns:
            Report content as a string in Markdown format.
        """
        # Build the markdown report
        report = [
            "# ISEE Meta-Framework Combination Metadata Report",
            "",
            "This report provides metadata about all combinations generated and executed in this run.",
            "",
            "## Combination Overview",
            "",
            f"- **Total Combinations**: {len(combinations)}",
            f"- **Executed Combinations**: {len(results)}",
            f"- **Evaluated Combinations**: {len(evaluations)}",
            "",
            "## Combination Details",
            "",
            "| ID | Model | Instruction | Domain | Response Length | Score |",
            "|---|---|---|---|---|---|",
        ]
        
        # Add each combination
        for combo in combinations:
            combo_id = combo["id"]
            
            # Get model name from config if available
            model_id = combo["model"]
            model_name = model_id
            if model_id in model_configs:
                model_name = model_configs[model_id].get("name", model_id)
            
            # Get instruction name
            instruction_id = combo["template"]
            instruction_name = instruction_id.replace("ins_", "").capitalize()
            
            # Get domain name
            domain_id = combo["domain"]
            domain_name = domain_id.replace("domain_", "").capitalize()
            
            # Get response length and score if available
            response_length = "N/A"
            if combo_id in results and "response" in results[combo_id]:
                response_length = f"{len(results[combo_id]['response']):,}"
            
            score = "N/A"
            if combo_id in evaluations and "overall" in evaluations[combo_id]:
                score = f"{evaluations[combo_id]['overall']:.3f}"
            
            # Add to the report
            report.append(f"| {combo_id} | {model_name} | {instruction_name} | {domain_name} | {response_length} | {score} |")
        
        # Join with line breaks
        return "\n".join(report)
    
    def _generate_metadata_report_json(
        self,
        combinations: List[Dict[str, Any]],
        results: Dict[str, Any],
        evaluations: Dict[str, Dict[str, float]],
        model_configs: Dict[str, Any],
        instruction_templates: Dict[str, Any]
    ) -> str:
        """Generate a metadata report in JSON format.
        
        Args:
            combinations: List of combination dictionaries.
            results: Dictionary mapping combination IDs to results.
            evaluations: Dictionary mapping combination IDs to evaluation scores.
            model_configs: Model configuration dictionary.
            instruction_templates: Dictionary of instruction templates.
            
        Returns:
            Report content as a JSON string.
        """
        # Build the overview section
        overview = {
            "total_combinations": len(combinations),
            "executed_combinations": len(results),
            "evaluated_combinations": len(evaluations)
        }
        
        # Build the combinations section
        combinations_data = []
        for combo in combinations:
            combo_id = combo["id"]
            
            # Get model name from config if available
            model_id = combo["model"]
            model_name = model_id
            if model_id in model_configs:
                model_name = model_configs[model_id].get("name", model_id)
            
            # Get instruction name
            instruction_id = combo["template"]
            instruction_name = instruction_id.replace("ins_", "").capitalize()
            
            # Get domain name
            domain_id = combo["domain"]
            domain_name = domain_id.replace("domain_", "").capitalize()
            
            # Get response length and score if available
            response_length = None
            if combo_id in results and "response" in results[combo_id]:
                response_length = len(results[combo_id]["response"])
            
            score = None
            if combo_id in evaluations and "overall" in evaluations[combo_id]:
                score = evaluations[combo_id]["overall"]
            
            # Add execution time if available
            execution_time = None
            if combo_id in results and "metadata" in results[combo_id]:
                execution_time = results[combo_id]["metadata"].get("duration")
            
            # Add to the report
            combinations_data.append({
                "id": combo_id,
                "model": {
                    "id": model_id,
                    "name": model_name
                },
                "instruction": {
                    "id": instruction_id,
                    "name": instruction_name
                },
                "domain": {
                    "id": domain_id,
                    "name": domain_name
                },
                "execution": {
                    "response_length": response_length,
                    "execution_time": execution_time
                },
                "evaluation": {
                    "overall_score": score,
                    "component_scores": evaluations.get(combo_id, {})
                }
            })
        
        # Build the complete JSON report
        report_data = {
            "overview": overview,
            "combinations": combinations_data
        }
        
        # Return as formatted JSON string
        return json.dumps(report_data, indent=2)
    
    def save_report(self, report_name: str, content: str) -> str:
        """Save a report to a file.
        
        Args:
            report_name: Name of the report.
            content: Report content.
            
        Returns:
            Path to the saved report file.
        """
        # Generate a timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Determine file extension based on report format
        extension = self.report_format
        
        # Create filename
        filename = f"{report_name}_{timestamp}.{extension}"
        file_path = os.path.join(self.output_directory, filename)
        
        # Write the content to the file
        with open(file_path, 'w') as f:
            f.write(content)
        
        return file_path

    def export_data_to_csv(
        self, 
        combinations: List[Dict[str, Any]],
        results: Dict[str, Any],
        evaluations: Dict[str, Dict[str, float]],
        synthesized_ideas: Dict[str, Any],
        model_configs: Dict[str, Any]
    ) -> Dict[str, str]:
        """Export data to CSV files.
        
        Args:
            combinations: List of combination dictionaries.
            results: Dictionary mapping combination IDs to results.
            evaluations: Dictionary mapping combination IDs to evaluation scores.
            synthesized_ideas: Dictionary of synthesized ideas.
            model_configs: Model configuration dictionary.
            
        Returns:
            Dictionary mapping CSV file names to file paths.
        """
        csv_files = {}
        
        # Generate combination metadata CSV
        combinations_csv = self._generate_combinations_csv(
            combinations, results, evaluations, model_configs
        )
        csv_files["combinations"] = combinations_csv
        
        # Generate ideas CSV
        if synthesized_ideas:
            ideas_csv = self._generate_ideas_csv(
                synthesized_ideas, results, evaluations, model_configs
            )
            csv_files["ideas"] = ideas_csv
        
        # Generate models performance CSV if we have pandas available
        if PANDAS_AVAILABLE and results:
            models_csv = self._generate_models_csv(
                combinations, results, evaluations, model_configs
            )
            csv_files["models"] = models_csv
        
        return csv_files
    
    def _generate_combinations_csv(
        self,
        combinations: List[Dict[str, Any]],
        results: Dict[str, Any],
        evaluations: Dict[str, Dict[str, float]],
        model_configs: Dict[str, Any]
    ) -> str:
        """Generate a CSV file with combination metadata.
        
        Args:
            combinations: List of combination dictionaries.
            results: Dictionary mapping combination IDs to results.
            evaluations: Dictionary mapping combination IDs to evaluation scores.
            model_configs: Model configuration dictionary.
            
        Returns:
            Path to the generated CSV file.
        """
        # Generate a timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"combinations_{timestamp}.csv"
        file_path = os.path.join(self.output_directory, filename)
        
        # Prepare the CSV data
        headers = [
            "combination_id", 
            "model_id", 
            "model_name",
            "instruction_id", 
            "domain_id", 
            "query_id",
            "executed", 
            "response_length", 
            "execution_time", 
            "overall_score"
        ]
        
        # Add headers for each evaluation criterion
        criterion_headers = set()
        for combo_id, scores in evaluations.items():
            for criterion in scores.keys():
                if criterion != "overall":
                    criterion_headers.add(criterion)
        
        all_headers = headers + sorted(list(criterion_headers))
        
        # Write the CSV file
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(all_headers)
            
            for combo in combinations:
                combo_id = combo["id"]
                model_id = combo["model"]
                instruction_id = combo["template"]
                domain_id = combo["domain"]
                query_id = combo["query"]
                
                # Get model name from config
                model_name = model_id
                if model_id in model_configs:
                    model_name = model_configs[model_id].get("name", model_id)
                
                # Determine if the combination was executed
                executed = combo_id in results
                
                # Get response length and execution time if available
                response_length = None
                execution_time = None
                if executed and "response" in results[combo_id]:
                    response_length = len(results[combo_id]["response"])
                    if "metadata" in results[combo_id]:
                        execution_time = results[combo_id]["metadata"].get("duration")
                
                # Get evaluation scores if available
                overall_score = None
                criterion_scores = {}
                if combo_id in evaluations:
                    for criterion, score in evaluations[combo_id].items():
                        if criterion == "overall":
                            overall_score = score
                        else:
                            criterion_scores[criterion] = score
                
                # Prepare the row data
                row = [
                    combo_id,
                    model_id,
                    model_name,
                    instruction_id,
                    domain_id,
                    query_id,
                    executed,
                    response_length,
                    execution_time,
                    overall_score
                ]
                
                # Add scores for each criterion
                for criterion in sorted(list(criterion_headers)):
                    row.append(criterion_scores.get(criterion))
                
                writer.writerow(row)
        
        return file_path
    
    def _generate_ideas_csv(
        self,
        synthesized_ideas: Dict[str, Any],
        results: Dict[str, Any],
        evaluations: Dict[str, Dict[str, float]],
        model_configs: Dict[str, Any]
    ) -> str:
        """Generate a CSV file with synthesized ideas data.
        
        Args:
            synthesized_ideas: Dictionary of synthesized ideas.
            results: Dictionary mapping combination IDs to results.
            evaluations: Dictionary mapping combination IDs to evaluation scores.
            model_configs: Model configuration dictionary.
            
        Returns:
            Path to the generated CSV file.
        """
        # Generate a timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ideas_{timestamp}.csv"
        file_path = os.path.join(self.output_directory, filename)
        
        # Prepare the CSV data
        headers = [
            "idea_id", 
            "title", 
            "description", 
            "source_count", 
            "avg_score",
            "contributing_models", 
            "synthesis_method"
        ]
        
        # Write the CSV file
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for idea_id, idea in synthesized_ideas.items():
                # Calculate average score from source combinations
                source_scores = []
                source_models = set()
                source_count = 0
                
                if "source_combinations" in idea:
                    source_count = len(idea["source_combinations"])
                    for source_id in idea["source_combinations"]:
                        if source_id in evaluations and "overall" in evaluations[source_id]:
                            source_scores.append(evaluations[source_id]["overall"])
                        
                        # Track which models contributed to this idea
                        if source_id in results and "metadata" in results[source_id]:
                            model = results[source_id]["metadata"].get("model", "unknown")
                            # Get model name from config if available
                            model_name = model
                            if model in model_configs:
                                model_name = model_configs[model].get("name", model)
                            source_models.add(model_name)
                
                avg_source_score = sum(source_scores) / len(source_scores) if source_scores else None
                contributing_models = ", ".join(sorted(list(source_models))) if source_models else ""
                
                synthesis_method = ""
                if "metadata" in idea:
                    synthesis_method = idea["metadata"].get("method", "")
                
                # Prepare the row data
                row = [
                    idea_id,
                    idea.get("title", ""),
                    idea.get("description", ""),
                    source_count,
                    avg_source_score,
                    contributing_models,
                    synthesis_method
                ]
                
                writer.writerow(row)
        
        return file_path
    
    def _generate_models_csv(
        self,
        combinations: List[Dict[str, Any]],
        results: Dict[str, Any],
        evaluations: Dict[str, Dict[str, float]],
        model_configs: Dict[str, Any]
    ) -> str:
        """Generate a CSV file with model performance data.
        
        Args:
            combinations: List of combination dictionaries.
            results: Dictionary mapping combination IDs to results.
            evaluations: Dictionary mapping combination IDs to evaluation scores.
            model_configs: Model configuration dictionary.
            
        Returns:
            Path to the generated CSV file.
        """
        # Generate a timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"model_performance_{timestamp}.csv"
        file_path = os.path.join(self.output_directory, filename)
        
        # Use pandas for aggregating data
        model_data = []
        
        for combo in combinations:
            combo_id = combo["id"]
            model_id = combo["model"]
            
            # Skip if not executed
            if combo_id not in results:
                continue
            
            # Get model name from config
            model_name = model_id
            if model_id in model_configs:
                model_name = model_configs[model_id].get("name", model_id)
                model_provider = model_configs[model_id].get("provider", "unknown")
            else:
                model_provider = "unknown"
            
            # Get response length and execution time if available
            response_length = None
            execution_time = None
            if "response" in results[combo_id]:
                response_length = len(results[combo_id]["response"])
                if "metadata" in results[combo_id]:
                    execution_time = results[combo_id]["metadata"].get("duration")
            
            # Get score if available
            score = None
            if combo_id in evaluations and "overall" in evaluations[combo_id]:
                score = evaluations[combo_id]["overall"]
            
            # Add to data
            model_data.append({
                "model_id": model_id,
                "model_name": model_name,
                "model_provider": model_provider,
                "response_length": response_length,
                "execution_time": execution_time,
                "score": score
            })
        
        # Convert to pandas DataFrame and aggregate
        if not model_data:
            # If no data, create empty CSV
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["model_id", "model_name", "model_provider", "count", "avg_score", "avg_response_length", "avg_execution_time"])
            return file_path
        
        df = pd.DataFrame(model_data)
        
        # Group by model and aggregate
        model_stats = df.groupby(["model_id", "model_name", "model_provider"]).agg({
            "model_id": "count",
            "score": ["mean", "min", "max"],
            "response_length": "mean",
            "execution_time": "mean"
        }).reset_index()
        
        # Flatten multi-level columns
        model_stats.columns = [
            "model_id", "model_name", "model_provider", "count",
            "avg_score", "min_score", "max_score",
            "avg_response_length", "avg_execution_time"
        ]
        
        # Save to CSV
        model_stats.to_csv(file_path, index=False)
        
        return file_path

def generate_reports(
    app, 
    args,
    query: str,
    combinations: List[Dict[str, Any]],
    results: Dict[str, Any],
    evaluations: Dict[str, Dict[str, float]],
    synthesized_ideas: Dict[str, Any]
) -> Dict[str, str]:
    """Generate reports for the current run.
    
    Args:
        app: The ISEEApplication instance.
        args: Command-line arguments.
        query: The query used for the run.
        combinations: List of combination dictionaries.
        results: Dictionary mapping combination IDs to results.
        evaluations: Dictionary mapping combination IDs to evaluation scores.
        synthesized_ideas: Dictionary of synthesized ideas.
        
    Returns:
        Dictionary mapping report names to file paths.
    """
    # Determine output directory
    output_directory = args.output_directory if args.output_directory else "data/output"
    
    # Determine report format
    report_format = args.report_format if args.report_format else "markdown"
    
    # Determine if CSV export is requested
    export_csv = args.export_csv if hasattr(args, 'export_csv') else False
    
    # Create reporting system
    reporting_system = ReportingSystem(
        output_directory=output_directory, 
        report_format=report_format,
        export_csv=export_csv
    )
    
    # Gather run parameters
    run_params = {
        "sampling_method": args.sampling_method,
        "max_combinations": args.max_combinations,
        "models": args.models,
        "instructions": args.instructions,
        "variations": args.variations,
        "balanced_models": args.balanced_models,
        "synthesize_method": args.synthesize_method
    }
    
    # Generate the reports
    report_files = {}
    
    # Generate run summary report
    run_summary = reporting_system.generate_run_summary(
        query=query,
        combinations=combinations,
        results=results,
        evaluations=evaluations,
        synthesized_ideas=synthesized_ideas,
        config={},  # Full config not needed for basic report
        model_configs=app.model_configs,
        run_params=run_params
    )
    
    # Save the run summary report
    summary_file = reporting_system.save_report("run_summary", run_summary)
    report_files["summary"] = summary_file
    
    # Generate metadata report
    metadata_report = reporting_system.generate_metadata_report(
        combinations=combinations,
        results=results,
        evaluations=evaluations,
        model_configs=app.model_configs,
        instruction_templates={}  # Not used in basic metadata report
    )
    
    # Save the metadata report
    metadata_file = reporting_system.save_report("metadata", metadata_report)
    report_files["metadata"] = metadata_file
    
    # Export data to CSV if requested
    if export_csv:
        csv_files = reporting_system.export_data_to_csv(
            combinations=combinations,
            results=results,
            evaluations=evaluations,
            synthesized_ideas=synthesized_ideas,
            model_configs=app.model_configs
        )
        
        # Add CSV files to report files
        for csv_name, csv_path in csv_files.items():
            report_files[f"csv_{csv_name}"] = csv_path
    
    return report_files