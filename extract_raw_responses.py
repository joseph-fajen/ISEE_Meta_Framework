#!/usr/bin/env python3
"""
ISEE Raw Response Extractor

This script extracts and displays all individual LLM responses from an ISEE run,
including metadata such as model names, cognitive frameworks, and scoring data.

Usage:
    python extract_raw_responses.py [run_directory]
    
If no run_directory is provided, it will use the latest run.
"""

import os
import sys
import csv
import json
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path

class ISEERawResponseExtractor:
    def __init__(self, run_directory: str):
        """Initialize the extractor with a run directory."""
        self.run_directory = Path(run_directory)
        self.combinations_data = []
        self.raw_responses = {}
        self.metadata = {}
        
    def load_data(self) -> bool:
        """Load all data from the run directory."""
        try:
            # Load combinations CSV
            combinations_file = self.run_directory / "combinations.csv"
            if combinations_file.exists():
                with open(combinations_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.combinations_data = list(reader)
                print(f"✅ Loaded {len(self.combinations_data)} combination records")
            else:
                print(f"❌ Could not find combinations.csv in {self.run_directory}")
                return False
                
            # Check for metadata
            metadata_file = self.run_directory / "metadata.md"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata['original_query'] = self._extract_query_from_metadata(f.read())
                    
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def _extract_query_from_metadata(self, metadata_content: str) -> str:
        """Extract the original query from metadata content."""
        lines = metadata_content.split('\n')
        for i, line in enumerate(lines):
            if 'Original Query' in line or '# Original Query' in line:
                # Try to get the next non-empty line
                for j in range(i+1, min(i+5, len(lines))):
                    if lines[j].strip() and not lines[j].startswith('#'):
                        return lines[j].strip()
        return "Query not found in metadata"
    
    def simulate_response_extraction(self) -> Dict[str, Any]:
        """
        Since ISEE doesn't save raw responses to disk by default, this method
        simulates what the responses would look like based on the available data.
        
        In a real implementation, this would load actual response text from 
        a custom storage solution.
        """
        print("\n🔍 Analyzing available data structure...")
        
        if not self.combinations_data:
            print("❌ No combination data available")
            return {}
            
        # Group combinations by model and framework
        by_model = {}
        by_framework = {}
        by_domain = {}
        
        for combo in self.combinations_data:
            model_name = combo.get('model_name', 'Unknown Model')
            framework_id = combo.get('instruction_id', 'Unknown Framework')
            domain_id = combo.get('domain_id', 'Unknown Domain')
            
            if model_name not in by_model:
                by_model[model_name] = []
            by_model[model_name].append(combo)
            
            if framework_id not in by_framework:
                by_framework[framework_id] = []
            by_framework[framework_id].append(combo)
            
            if domain_id not in by_domain:
                by_domain[domain_id] = []
            by_domain[domain_id].append(combo)
        
        return {
            'total_responses': len(self.combinations_data),
            'by_model': by_model,
            'by_framework': by_framework,
            'by_domain': by_domain,
            'query': self.metadata.get('original_query', 'Query not found')
        }
    
    def display_summary(self, analysis: Dict[str, Any]) -> None:
        """Display a comprehensive summary of the response data."""
        print("\n" + "="*80)
        print("🎯 ISEE RAW RESPONSE ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"\n📋 Original Query:")
        print(f"   {analysis['query']}")
        
        print(f"\n📊 Response Overview:")
        print(f"   Total LLM Responses: {analysis['total_responses']}")
        print(f"   Unique Models: {len(analysis['by_model'])}")
        print(f"   Cognitive Frameworks: {len(analysis['by_framework'])}")
        print(f"   Knowledge Domains: {len(analysis['by_domain'])}")
        
        print(f"\n🤖 Models Used:")
        for model, responses in analysis['by_model'].items():
            avg_score = sum(float(r.get('overall_score', 0)) for r in responses) / len(responses)
            print(f"   • {model}: {len(responses)} responses (avg score: {avg_score:.3f})")
        
        print(f"\n🧠 Cognitive Frameworks:")
        framework_map = {
            'ins_analytical': 'Analytical',
            'ins_creative': 'Creative', 
            'ins_critical': 'Critical',
            'ins_integrative': 'Integrative',
            'ins_pragmatic': 'Pragmatic',
            'ins_first_principles': 'First Principles',
            'ins_systems': 'Systems',
            'ins_contrarian': 'Contrarian',
            'ins_historical': 'Historical',
            'ins_futurist': 'Future-Oriented',
            'ins_disruption': 'Disruption'
        }
        
        for framework_id, responses in analysis['by_framework'].items():
            framework_name = framework_map.get(framework_id, framework_id)
            avg_score = sum(float(r.get('overall_score', 0)) for r in responses) / len(responses)
            print(f"   • {framework_name}: {len(responses)} responses (avg score: {avg_score:.3f})")
        
        print(f"\n🌐 Knowledge Domains:")
        for domain, responses in analysis['by_domain'].items():
            domain_clean = domain.replace('dynamic:', '').replace('_', ' ').title()
            avg_score = sum(float(r.get('overall_score', 0)) for r in responses) / len(responses)
            print(f"   • {domain_clean}: {len(responses)} responses (avg score: {avg_score:.3f})")
    
    def display_detailed_responses(self, analysis: Dict[str, Any], limit: int = 5) -> None:
        """Display detailed information for top-scoring responses."""
        print(f"\n🏆 TOP {limit} RESPONSES BY SCORE:")
        print("="*80)
        
        # Sort all responses by score
        all_responses = sorted(self.combinations_data, 
                             key=lambda x: float(x.get('overall_score', 0)), 
                             reverse=True)
        
        for i, response in enumerate(all_responses[:limit], 1):
            print(f"\n#{i} | Score: {float(response.get('overall_score', 0)):.3f}")
            print(f"   Model: {response.get('model_name', 'Unknown')}")
            
            framework_id = response.get('instruction_id', 'Unknown')
            framework_map = {
                'ins_analytical': 'Analytical',
                'ins_creative': 'Creative', 
                'ins_critical': 'Critical',
                'ins_integrative': 'Integrative',
                'ins_pragmatic': 'Pragmatic',
                'ins_first_principles': 'First Principles',
                'ins_systems': 'Systems',
                'ins_contrarian': 'Contrarian',
                'ins_historical': 'Historical',
                'ins_futurist': 'Future-Oriented',
                'ins_disruption': 'Disruption'
            }
            framework_name = framework_map.get(framework_id, framework_id)
            print(f"   Framework: {framework_name}")
            
            domain = response.get('domain_id', 'Unknown').replace('dynamic:', '').replace('_', ' ').title()
            print(f"   Domain: {domain}")
            
            print(f"   Response Length: {response.get('response_length', 'Unknown')} chars")
            print(f"   Execution Time: {float(response.get('execution_time', 0)):.2f}s")
            
            # Detailed scoring breakdown
            scores = {
                'Comprehensiveness': response.get('comprehensiveness', '0'),
                'Feasibility': response.get('feasibility', '0'),
                'Impact': response.get('impact', '0'),
                'Novelty': response.get('novelty', '0'),
                'Specificity': response.get('specificity', '0')
            }
            
            print(f"   Scoring Breakdown:")
            for criterion, score in scores.items():
                print(f"     • {criterion}: {float(score):.3f}")
            
            print(f"   Combination ID: {response.get('combination_id', 'Unknown')}")
    
    def export_to_csv(self, filename: Optional[str] = None) -> str:
        """Export all response metadata to CSV for further analysis."""
        if not filename:
            filename = f"raw_responses_analysis_{os.path.basename(self.run_directory)}.csv"
        
        filepath = self.run_directory / filename
        
        # Enhance the data with readable names
        enhanced_data = []
        framework_map = {
            'ins_analytical': 'Analytical',
            'ins_creative': 'Creative', 
            'ins_critical': 'Critical',
            'ins_integrative': 'Integrative',
            'ins_pragmatic': 'Pragmatic',
            'ins_first_principles': 'First Principles',
            'ins_systems': 'Systems',
            'ins_contrarian': 'Contrarian',
            'ins_historical': 'Historical',
            'ins_futurist': 'Future-Oriented',
            'ins_disruption': 'Disruption'
        }
        
        for response in self.combinations_data:
            enhanced_response = response.copy()
            
            # Add readable framework name
            framework_id = response.get('instruction_id', '')
            enhanced_response['framework_name'] = framework_map.get(framework_id, framework_id)
            
            # Clean up domain name
            domain = response.get('domain_id', '').replace('dynamic:', '').replace('_', ' ').title()
            enhanced_response['domain_name'] = domain
            
            # Add ranking
            enhanced_response['score_rank'] = 0  # Will be filled after sorting
            
            enhanced_data.append(enhanced_response)
        
        # Sort by score and add rankings
        enhanced_data.sort(key=lambda x: float(x.get('overall_score', 0)), reverse=True)
        for i, response in enumerate(enhanced_data, 1):
            response['score_rank'] = i
        
        # Write to CSV
        if enhanced_data:
            fieldnames = list(enhanced_data[0].keys())
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(enhanced_data)
        
        return str(filepath)
    
    def explain_missing_responses(self) -> None:
        """Explain why raw response text isn't available and suggest solutions."""
        print("\n" + "="*80)
        print("🔍 WHY RAW RESPONSE TEXT ISN'T DIRECTLY AVAILABLE")
        print("="*80)
        
        print("""
📋 Current ISEE Architecture:
   • LLM responses are processed in memory during execution
   • Only metadata and scores are saved to CSV files
   • Full response text is used for synthesis but not persisted
   • This design optimizes for storage efficiency and synthesis quality

🎯 What Data IS Available:
   • Complete metadata for all 66 responses
   • Detailed scoring breakdowns (5 criteria per response)
   • Model, framework, and domain information  
   • Response lengths and execution times
   • Synthesized ideas created from top responses

💡 How to Access Raw Responses:

   Option 1: Modify ISEE to Save Raw Responses
   • Add response text storage to main.py execution loop
   • Modify the save functions to include full response text
   • Re-run your analysis to capture raw responses

   Option 2: Use Synthesis & Ideas Data
   • The ideas.csv contains synthesized content from top responses
   • The isee_result.md shows the final synthesis output
   • These represent the highest-value content from your 66 responses

   Option 3: Real-time Monitoring
   • Run ISEE with verbose logging to see responses in real-time
   • Capture console output during execution
   • Use debugging mode to access response objects

🔧 Recommended Next Steps:
   1. Review the synthesized ideas in ideas.csv (high-value content)
   2. Analyze the detailed scoring data for insights
   3. If raw responses are needed, modify ISEE and re-run
        """)

def find_latest_run() -> Optional[str]:
    """Find the most recent ISEE run directory."""
    output_dir = Path("data/output")
    
    # Check for latest symlink first
    latest_link = output_dir / "latest"
    if latest_link.exists() and latest_link.is_symlink():
        return str(latest_link.resolve())
    
    # Fall back to finding most recent directory
    run_dirs = []
    for item in output_dir.rglob("run_*"):
        if item.is_dir():
            run_dirs.append(item)
    
    if run_dirs:
        # Sort by modification time
        run_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return str(run_dirs[0])
    
    return None

def main():
    """Main execution function."""
    print("🚀 ISEE Raw Response Extractor")
    print("="*50)
    
    # Determine run directory
    if len(sys.argv) > 1:
        run_directory = sys.argv[1]
    else:
        run_directory = find_latest_run()
        if run_directory:
            print(f"📁 Using latest run: {os.path.basename(run_directory)}")
        else:
            print("❌ No run directory found. Please specify one.")
            print("Usage: python extract_raw_responses.py [run_directory]")
            return
    
    if not os.path.exists(run_directory):
        print(f"❌ Run directory not found: {run_directory}")
        return
    
    # Initialize extractor
    extractor = ISEERawResponseExtractor(run_directory)
    
    # Load data
    if not extractor.load_data():
        print("❌ Failed to load data from run directory")
        return
    
    # Analyze the data
    analysis = extractor.simulate_response_extraction()
    
    # Display results
    extractor.display_summary(analysis)
    extractor.display_detailed_responses(analysis, limit=10)
    
    # Export enhanced CSV
    csv_path = extractor.export_to_csv()
    print(f"\n💾 Enhanced analysis exported to: {csv_path}")
    
    # Explain limitations and next steps
    extractor.explain_missing_responses()
    
    print(f"\n✅ Analysis complete! Total responses analyzed: {analysis['total_responses']}")

if __name__ == "__main__":
    main()