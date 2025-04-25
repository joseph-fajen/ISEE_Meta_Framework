"""
Analysis Module for ISEE Framework

This module provides basic analysis of ISEE run results based on CSV exports.
It generates insights about model performance, domains, and instruction templates.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class ResultAnalyzer:
    """Analyzer for ISEE run results."""
    
    def __init__(self, data_directory: str = "data/output", output_directory: str = None):
        """Initialize the analyzer.
        
        Args:
            data_directory: Directory containing the CSV data files.
            output_directory: Directory to save analysis outputs to. If None, uses data_directory.
        """
        self.data_directory = data_directory
        self.output_directory = output_directory if output_directory else data_directory
        
        # Ensure the output directory exists
        os.makedirs(self.output_directory, exist_ok=True)
        
        # Data frames
        self.combinations_df = None
        self.ideas_df = None
        self.model_performance_df = None
        
        # Analysis results
        self.analysis_results = {}
    
    def load_data(self, run_timestamp: str = None) -> bool:
        """Load data from CSV files.
        
        Args:
            run_timestamp: Timestamp of the run to analyze. If None, uses the most recent run.
                           With the new directory structure, this parameter is ignored.
            
        Returns:
            True if data was loaded successfully, False otherwise.
        """
        try:
            # With the new directory structure, we use simple filenames directly
            # No need to derive timestamps since each run has its own directory
            
            # Construct file paths using simple names
            combinations_path = os.path.join(self.data_directory, "combinations.csv")
            ideas_path = os.path.join(self.data_directory, "ideas.csv")
            model_perf_path = os.path.join(self.data_directory, "model_performance.csv")
            
            # Load data frames
            if os.path.exists(combinations_path):
                self.combinations_df = pd.read_csv(combinations_path)
            else:
                print(f"Combinations file not found: {combinations_path}")
                return False
            
            if os.path.exists(ideas_path):
                self.ideas_df = pd.read_csv(ideas_path)
            else:
                print(f"Ideas file not found, but continuing with analysis: {ideas_path}")
            
            if os.path.exists(model_perf_path):
                self.model_performance_df = pd.read_csv(model_perf_path)
            else:
                print(f"Model performance file not found: {model_perf_path}")
                # We can generate this from combinations if needed
                self._generate_model_performance_df()
            
            return True
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False
    
    def _generate_model_performance_df(self):
        """Generate model performance DataFrame from combinations data if the CSV is missing."""
        if self.combinations_df is None:
            return
        
        try:
            # Group by model and aggregate
            model_stats = self.combinations_df.groupby(['model_id', 'model_name']).agg({
                'model_id': 'count',
                'overall_score': ['mean', 'min', 'max'],
                'response_length': 'mean',
                'execution_time': 'mean'
            }).reset_index()
            
            # Flatten multi-level columns
            model_stats.columns = [
                'model_id', 'model_name', 'count',
                'avg_score', 'min_score', 'max_score',
                'avg_response_length', 'avg_execution_time'
            ]
            
            # Add a provider column (empty)
            model_stats['model_provider'] = 'unknown'
            
            self.model_performance_df = model_stats
            
        except Exception as e:
            print(f"Error generating model performance data: {str(e)}")
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze the loaded data and generate insights.
        
        Returns:
            Dictionary of analysis results.
        """
        if self.combinations_df is None:
            print("No data loaded for analysis")
            return {}
        
        # Initialize results dictionary
        results = {
            "basic_stats": {},
            "model_performance": {},
            "domain_performance": {},
            "instruction_performance": {},
            "scoring_components": {},
            "top_performers": {},
            "recommendations": []
        }
        
        # Get basic statistics
        results["basic_stats"] = {
            "total_combinations": len(self.combinations_df),
            "executed_combinations": self.combinations_df['executed'].sum(),
            "average_response_length": self.combinations_df['response_length'].mean(),
            "average_execution_time": self.combinations_df['execution_time'].mean(),
            "average_score": self.combinations_df['overall_score'].mean()
        }
        
        # Analyze model performance
        if self.model_performance_df is not None:
            results["model_performance"] = self.model_performance_df.to_dict(orient='records')
            # Find best model
            best_model_idx = self.model_performance_df['avg_score'].idxmax()
            results["top_performers"]["best_model"] = self.model_performance_df.iloc[best_model_idx].to_dict()
        
        # Analyze domain performance
        domain_perf = self.combinations_df.groupby('domain_id').agg({
            'overall_score': ['mean', 'min', 'max', 'count'],
            'execution_time': 'mean'
        })
        
        # Flatten the multi-index
        domain_perf.columns = ['avg_score', 'min_score', 'max_score', 'count', 'avg_execution_time']
        domain_perf = domain_perf.reset_index()
        
        results["domain_performance"] = domain_perf.to_dict(orient='records')
        
        # Find best domain
        best_domain_idx = domain_perf['avg_score'].idxmax()
        results["top_performers"]["best_domain"] = domain_perf.iloc[best_domain_idx].to_dict()
        
        # Analyze instruction performance
        instruction_perf = self.combinations_df.groupby('instruction_id').agg({
            'overall_score': ['mean', 'min', 'max', 'count']
        })
        
        # Flatten the multi-index
        instruction_perf.columns = ['avg_score', 'min_score', 'max_score', 'count']
        instruction_perf = instruction_perf.reset_index()
        
        results["instruction_performance"] = instruction_perf.to_dict(orient='records')
        
        # Find best instruction
        best_instruction_idx = instruction_perf['avg_score'].idxmax()
        results["top_performers"]["best_instruction"] = instruction_perf.iloc[best_instruction_idx].to_dict()
        
        # Analyze scoring components
        score_components = [col for col in self.combinations_df.columns 
                           if col not in ['combination_id', 'model_id', 'model_name', 'instruction_id', 
                                         'domain_id', 'query_id', 'executed', 'response_length', 
                                         'execution_time', 'overall_score']]
        
        if score_components:
            component_avgs = self.combinations_df[score_components].mean().to_dict()
            results["scoring_components"] = component_avgs
        
        # Find best combination
        best_combo_idx = self.combinations_df['overall_score'].idxmax()
        results["top_performers"]["best_combination"] = self.combinations_df.iloc[best_combo_idx].to_dict()
        
        # Generate recommendations
        self._generate_recommendations(results)
        
        self.analysis_results = results
        return results
    
    def _generate_recommendations(self, results: Dict[str, Any]):
        """Generate recommendations based on analysis results.
        
        Args:
            results: Dictionary of analysis results.
        """
        recommendations = []
        
        # Recommend best model
        if "best_model" in results["top_performers"]:
            best_model = results["top_performers"]["best_model"]
            recommendations.append(
                f"Use {best_model['model_name']} for best results (avg score: {best_model['avg_score']:.3f})"
            )
        
        # Recommend best domain focus
        if "best_domain" in results["top_performers"]:
            best_domain = results["top_performers"]["best_domain"]
            domain_name = best_domain['domain_id'].replace("domain_", "").replace("_", " ").title()
            recommendations.append(
                f"Focus on {domain_name} aspects (avg score: {best_domain['avg_score']:.3f})"
            )
        
        # Recommend best instruction template
        if "best_instruction" in results["top_performers"]:
            best_instruction = results["top_performers"]["best_instruction"]
            instruction_name = best_instruction['instruction_id'].replace("ins_", "").replace("_", " ").title()
            recommendations.append(
                f"Use the {instruction_name} Framework approach (avg score: {best_instruction['avg_score']:.3f})"
            )
        
        # Recommend based on scoring components
        if "scoring_components" in results and results["scoring_components"]:
            components = list(results["scoring_components"].items())
            components.sort(key=lambda x: x[1], reverse=True)
            top_component = components[0][0].title()
            bottom_component = components[-1][0].title()
            
            recommendations.append(
                f"Emphasize {top_component} in your approach (scored highest: {components[0][1]:.3f})"
            )
            recommendations.append(
                f"Consider ways to improve {bottom_component} (scored lowest: {components[-1][1]:.3f})"
            )
        
        results["recommendations"] = recommendations
    
    def generate_report(self, output_format: str = "markdown") -> str:
        """Generate a report from the analysis results.
        
        Args:
            output_format: Format for the report (markdown, json).
            
        Returns:
            Report content as a string.
        """
        if not self.analysis_results:
            self.analyze()
        
        if output_format == "markdown":
            return self._generate_markdown_report()
        elif output_format == "json":
            import json
            return json.dumps(self.analysis_results, indent=2)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _generate_markdown_report(self) -> str:
        """Generate a markdown report from the analysis results.
        
        Returns:
            Report content as a markdown string.
        """
        results = self.analysis_results
        if not results:
            return "No analysis results available"
        
        # Build the markdown report
        report = [
            "# ISEE Run Analysis Report",
            "",
            "## Summary Statistics",
            ""
        ]
        
        # Add basic statistics
        if "basic_stats" in results:
            stats = results["basic_stats"]
            report.extend([
                f"- **Total Combinations**: {stats.get('total_combinations', 'N/A')}",
                f"- **Executed Combinations**: {stats.get('executed_combinations', 'N/A')}",
                f"- **Average Response Length**: {int(stats.get('average_response_length', 0)):,} characters",
                f"- **Average Execution Time**: {stats.get('average_execution_time', 'N/A'):.2f} seconds",
                f"- **Average Score**: {stats.get('average_score', 'N/A'):.3f}",
                ""
            ])
        
        # Add model performance
        if "model_performance" in results and results["model_performance"]:
            report.extend([
                "## Model Performance",
                "",
                "| Model | Count | Avg Score | Min Score | Max Score | Avg Length | Avg Time |",
                "|-------|-------|-----------|-----------|-----------|------------|----------|"
            ])
            
            for model in results["model_performance"]:
                report.append(
                    f"| {model.get('model_name', 'Unknown')} | "
                    f"{model.get('count', 'N/A')} | "
                    f"{model.get('avg_score', 'N/A'):.3f} | "
                    f"{model.get('min_score', 'N/A'):.3f} | "
                    f"{model.get('max_score', 'N/A'):.3f} | "
                    f"{int(model.get('avg_response_length', 0)):,} | "
                    f"{model.get('avg_execution_time', 'N/A'):.2f}s |"
                )
            
            report.append("")
        
        # Add domain performance
        if "domain_performance" in results and results["domain_performance"]:
            report.extend([
                "## Domain Performance",
                "",
                "| Domain | Count | Avg Score | Min Score | Max Score |",
                "|--------|-------|-----------|-----------|-----------|"
            ])
            
            for domain in results["domain_performance"]:
                domain_name = domain['domain_id'].replace("domain_", "").replace("_", " ").title()
                report.append(
                    f"| {domain_name} | "
                    f"{domain.get('count', 'N/A')} | "
                    f"{domain.get('avg_score', 'N/A'):.3f} | "
                    f"{domain.get('min_score', 'N/A'):.3f} | "
                    f"{domain.get('max_score', 'N/A'):.3f} |"
                )
            
            report.append("")
        
        # Add instruction performance
        if "instruction_performance" in results and results["instruction_performance"]:
            report.extend([
                "## Instruction Framework Performance",
                "",
                "| Framework | Count | Avg Score | Min Score | Max Score |",
                "|-----------|-------|-----------|-----------|-----------|"
            ])
            
            for instruction in results["instruction_performance"]:
                instruction_name = instruction['instruction_id'].replace("ins_", "").replace("_", " ").title()
                report.append(
                    f"| {instruction_name} | "
                    f"{instruction.get('count', 'N/A')} | "
                    f"{instruction.get('avg_score', 'N/A'):.3f} | "
                    f"{instruction.get('min_score', 'N/A'):.3f} | "
                    f"{instruction.get('max_score', 'N/A'):.3f} |"
                )
            
            report.append("")
        
        # Add scoring components
        if "scoring_components" in results and results["scoring_components"]:
            components = list(results["scoring_components"].items())
            components.sort(key=lambda x: x[1], reverse=True)
            
            report.extend([
                "## Scoring Component Analysis",
                "",
                "| Component | Average Score |",
                "|-----------|---------------|"
            ])
            
            for component, score in components:
                component_name = component.title()
                report.append(f"| {component_name} | {score:.3f} |")
            
            report.append("")
        
        # Add top performers
        if "top_performers" in results:
            report.extend([
                "## Top Performers",
                ""
            ])
            
            if "best_model" in results["top_performers"]:
                best_model = results["top_performers"]["best_model"]
                report.append(f"- **Best Model**: {best_model.get('model_name', 'Unknown')} (Score: {best_model.get('avg_score', 'N/A'):.3f})")
            
            if "best_domain" in results["top_performers"]:
                best_domain = results["top_performers"]["best_domain"]
                domain_name = best_domain['domain_id'].replace("domain_", "").replace("_", " ").title()
                report.append(f"- **Best Domain**: {domain_name} (Score: {best_domain.get('avg_score', 'N/A'):.3f})")
            
            if "best_instruction" in results["top_performers"]:
                best_instruction = results["top_performers"]["best_instruction"]
                instruction_name = best_instruction['instruction_id'].replace("ins_", "").replace("_", " ").title()
                report.append(f"- **Best Instruction Framework**: {instruction_name} (Score: {best_instruction.get('avg_score', 'N/A'):.3f})")
            
            if "best_combination" in results["top_performers"]:
                best_combo = results["top_performers"]["best_combination"]
                model_name = best_combo.get('model_name', 'Unknown')
                instruction_name = best_combo.get('instruction_id', '').replace("ins_", "").replace("_", " ").title()
                domain_name = best_combo.get('domain_id', '').replace("domain_", "").replace("_", " ").title()
                report.append(f"- **Best Combination**: {model_name} with {instruction_name} in {domain_name} (Score: {best_combo.get('overall_score', 'N/A'):.3f})")
            
            report.append("")
        
        # Add recommendations
        if "recommendations" in results and results["recommendations"]:
            report.extend([
                "## Recommendations",
                ""
            ])
            
            for i, recommendation in enumerate(results["recommendations"], 1):
                report.append(f"{i}. {recommendation}")
            
            report.append("")
        
        # Join with line breaks
        return "\n".join(report)
    
    def generate_visualizations(self) -> List[str]:
        """Generate visualizations from the analysis results.
        
        Returns:
            List of paths to generated visualization files.
        """
        if not self.analysis_results or not self.combinations_df is not None:
            print("No data available for visualizations")
            return []
        
        # With run-specific directories, we don't need timestamps in filenames
        visualization_files = []
        
        try:
            # Create model performance chart
            if self.model_performance_df is not None and len(self.model_performance_df) > 0:
                plt.figure(figsize=(10, 6))
                plt.bar(self.model_performance_df['model_name'], self.model_performance_df['avg_score'])
                plt.xlabel('Model')
                plt.ylabel('Average Score')
                plt.title('Model Performance Comparison')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                
                file_path = os.path.join(self.output_directory, "model_comparison.png")
                plt.savefig(file_path)
                plt.close()
                visualization_files.append(file_path)
            
            # Create domain performance chart
            domain_perf = self.combinations_df.groupby('domain_id')['overall_score'].mean().reset_index()
            domain_perf['domain_name'] = domain_perf['domain_id'].apply(
                lambda x: x.replace("domain_", "").replace("_", " ").title())
            
            if len(domain_perf) > 0:
                plt.figure(figsize=(10, 6))
                plt.bar(domain_perf['domain_name'], domain_perf['overall_score'])
                plt.xlabel('Domain')
                plt.ylabel('Average Score')
                plt.title('Domain Performance Comparison')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                
                file_path = os.path.join(self.output_directory, "domain_comparison.png")
                plt.savefig(file_path)
                plt.close()
                visualization_files.append(file_path)
            
            # Create instruction performance chart
            instruction_perf = self.combinations_df.groupby('instruction_id')['overall_score'].mean().reset_index()
            instruction_perf['instruction_name'] = instruction_perf['instruction_id'].apply(
                lambda x: x.replace("ins_", "").replace("_", " ").title())
            
            if len(instruction_perf) > 0:
                plt.figure(figsize=(10, 6))
                plt.bar(instruction_perf['instruction_name'], instruction_perf['overall_score'])
                plt.xlabel('Instruction Framework')
                plt.ylabel('Average Score')
                plt.title('Instruction Framework Performance')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                
                file_path = os.path.join(self.output_directory, "instruction_comparison.png")
                plt.savefig(file_path)
                plt.close()
                visualization_files.append(file_path)
            
            # Create scoring components chart
            score_components = [col for col in self.combinations_df.columns 
                              if col not in ['combination_id', 'model_id', 'model_name', 'instruction_id', 
                                            'domain_id', 'query_id', 'executed', 'response_length', 
                                            'execution_time', 'overall_score']]
            
            if score_components:
                component_avgs = self.combinations_df[score_components].mean().sort_values(ascending=False)
                
                plt.figure(figsize=(10, 6))
                plt.bar(component_avgs.index, component_avgs.values)
                plt.xlabel('Scoring Component')
                plt.ylabel('Average Score')
                plt.title('Scoring Component Analysis')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                
                file_path = os.path.join(self.output_directory, "scoring_components.png")
                plt.savefig(file_path)
                plt.close()
                visualization_files.append(file_path)
                
        except Exception as e:
            print(f"Error generating visualizations: {str(e)}")
        
        return visualization_files

def analyze_results(
    data_directory: str = "data/output", 
    output_directory: str = None,
    output_format: str = "markdown",
    run_timestamp: str = None,
    generate_visualizations: bool = True
) -> Tuple[str, List[str]]:
    """Analyze ISEE run results.
    
    Args:
        data_directory: Directory containing the CSV data files.
        output_directory: Directory to save analysis outputs to. If None, uses data_directory.
        output_format: Format for the report (markdown, json).
        run_timestamp: Timestamp of the run to analyze. If None, uses the most recent run.
        generate_visualizations: Whether to generate visualization charts.
        
    Returns:
        Tuple of (report content, list of visualization file paths).
    """
    analyzer = ResultAnalyzer(data_directory, output_directory)
    
    # Load data
    if not analyzer.load_data(run_timestamp):
        return "Failed to load data for analysis", []
    
    # Analyze data
    analyzer.analyze()
    
    # Generate report
    report = analyzer.generate_report(output_format)
    
    # Generate visualizations if requested
    visualization_files = []
    if generate_visualizations:
        visualization_files = analyzer.generate_visualizations()
    
    return report, visualization_files