#!/usr/bin/env python3
"""
Cognitive Diversity Metadata Extractor for ISEE
Transforms raw responses into rich, explorable cognitive diversity data.
"""

import json
import os
import re
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import hashlib
from collections import Counter

class CognitiveDiversityExtractor:
    def __init__(self, run_directory: str):
        """Initialize the extractor with a specific ISEE run directory."""
        self.run_directory = Path(run_directory)
        self.raw_responses_dir = self.run_directory / "raw_responses"
        self.combinations_csv = self.run_directory / "combinations.csv"
        self.metadata_output = self.run_directory / "cognitive_diversity_index.json"
        
        # Load cognitive framework descriptions for analysis
        self.framework_characteristics = {
            "ins_analytical": {
                "thinking_style": "analytical",
                "perspective_type": "systematic",
                "specialization": "Systematic problem breakdown and logical analysis",
                "focus_area": "technical",
                "complexity_level": "intermediate"
            },
            "ins_creative": {
                "thinking_style": "creative", 
                "perspective_type": "innovative",
                "specialization": "Novel solution generation and ideation",
                "focus_area": "strategic",
                "complexity_level": "advanced"
            },
            "ins_critical": {
                "thinking_style": "critical",
                "perspective_type": "evaluative", 
                "specialization": "Rigorous evaluation and challenge assumptions",
                "focus_area": "theoretical",
                "complexity_level": "advanced"
            },
            "ins_contrarian": {
                "thinking_style": "contrarian",
                "perspective_type": "contrarian",
                "specialization": "Alternative perspectives and challenging conventional wisdom",
                "focus_area": "strategic", 
                "complexity_level": "expert"
            },
            "ins_systems": {
                "thinking_style": "systematic",
                "perspective_type": "holistic",
                "specialization": "Holistic interconnection analysis and system-level thinking",
                "focus_area": "strategic",
                "complexity_level": "expert"
            },
            "ins_pragmatic": {
                "thinking_style": "practical",
                "perspective_type": "pragmatic",
                "specialization": "Implementation-focused analysis and practical solutions",
                "focus_area": "practical",
                "complexity_level": "intermediate"
            },
            "ins_first_principles": {
                "thinking_style": "analytical",
                "perspective_type": "foundational",
                "specialization": "Fundamental assumptions examination and ground-up reasoning",
                "focus_area": "theoretical",
                "complexity_level": "expert"
            },
            "ins_integrative": {
                "thinking_style": "integrative",
                "perspective_type": "synthesizing", 
                "specialization": "Cross-domain synthesis and connection-making",
                "focus_area": "strategic",
                "complexity_level": "advanced"
            },
            "ins_historical": {
                "thinking_style": "historical",
                "perspective_type": "retrospective",
                "specialization": "Past patterns and lessons learned analysis",
                "focus_area": "strategic",
                "complexity_level": "intermediate"
            },
            "ins_futurist": {
                "thinking_style": "futurist",
                "perspective_type": "forward-looking",
                "specialization": "Future implications and trend analysis",
                "focus_area": "strategic", 
                "complexity_level": "advanced"
            },
            "ins_disruption": {
                "thinking_style": "disruptive",
                "perspective_type": "transformative",
                "specialization": "Breakthrough innovations and paradigm shifts",
                "focus_area": "strategic",
                "complexity_level": "expert"
            }
        }
        
        # Model provider specializations
        self.model_specializations = {
            "claude": "Deep reasoning and nuanced analysis",
            "gpt": "Versatile problem-solving and clear communication",
            "gemini": "Multimodal reasoning and comprehensive analysis", 
            "grok": "Innovative thinking and unconventional approaches",
            "deepseek": "Technical depth and engineering focus",
            "perplexity": "Research-oriented analysis and fact integration",
            "llama": "Open-source flexibility and efficient processing",
            "qwen": "Multilingual and cross-cultural perspectives",
            "mixtral": "Mixture-of-experts specialized reasoning",
            "o3": "Advanced reasoning and complex problem solving"
        }

    def load_performance_data(self) -> Dict[str, Dict]:
        """Load performance data from combinations.csv."""
        performance_data = {}
        
        if not self.combinations_csv.exists():
            print(f"Warning: {self.combinations_csv} not found")
            return performance_data
            
        with open(self.combinations_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                combination_id = row['combination_id']
                performance_data[combination_id] = {
                    'overall_score': float(row.get('overall_score', 0)),
                    'actionability_score': float(row.get('actionability', 0)),
                    'comprehensiveness_score': float(row.get('comprehensiveness', 0)),
                    'feasibility_score': float(row.get('feasibility', 0)),
                    'impact_score': float(row.get('impact', 0)),
                    'novelty_score': float(row.get('novelty', 0)),
                    'specificity_score': float(row.get('specificity', 0)),
                    'response_length_chars': int(row.get('response_length', 0)),
                    'execution_time': float(row.get('execution_time', 0))
                }
        
        return performance_data

    def extract_key_concepts(self, content: str) -> List[str]:
        """Extract key concepts and technologies from response content."""
        # Technology and framework patterns
        tech_patterns = [
            r'\b(?:DSPy|GPT|Claude|LLM|AI|ML|NLP|RAG|API|SDK|framework|library|model|algorithm)\b',
            r'\b(?:Python|JavaScript|React|Vue|Flask|Django|Docker|Kubernetes|AWS|Azure|GCP)\b',
            r'\b(?:machine learning|deep learning|neural network|transformer|fine-tuning|prompt engineering)\b',
            r'\b(?:classification|regression|clustering|optimization|evaluation|training|inference)\b'
        ]
        
        concepts = set()
        content_lower = content.lower()
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            concepts.update(matches)
        
        # Extract quoted terms and technical terminology
        quoted_terms = re.findall(r'"([^"]+)"', content)
        concepts.update([term.lower() for term in quoted_terms if len(term) > 3])
        
        # Extract capitalized terms (likely proper nouns/technologies)
        capitalized = re.findall(r'\b[A-Z][a-zA-Z]{2,}\b', content)
        concepts.update([term.lower() for term in capitalized if len(term) > 3])
        
        return list(concepts)[:20]  # Limit to top 20 concepts

    def analyze_approach_categories(self, content: str) -> List[str]:
        """Identify the types of approaches mentioned in the response."""
        categories = []
        content_lower = content.lower()
        
        approach_patterns = {
            'implementation': [r'implement', r'build', r'create', r'develop', r'code', r'deploy'],
            'analysis': [r'analyz', r'evaluat', r'assess', r'examin', r'investigat'],
            'strategy': [r'strateg', r'plan', r'approach', r'methodolog', r'framework'],
            'research': [r'research', r'study', r'investigat', r'explor', r'discover'],
            'comparison': [r'compar', r'contrast', r'versus', r'alternative', r'option'],
            'optimization': [r'optim', r'improv', r'enhanc', r'refin', r'tune'],
            'demonstration': [r'demonstrat', r'show', r'proof', r'example', r'prototype'],
            'measurement': [r'measur', r'metric', r'benchmark', r'evaluat', r'assess']
        }
        
        for category, patterns in approach_patterns.items():
            if any(re.search(pattern, content_lower) for pattern in patterns):
                categories.append(category)
        
        return categories

    def extract_success_metrics(self, content: str) -> List[str]:
        """Extract mentioned success criteria and metrics."""
        metrics = []
        
        # Pattern for common metrics
        metric_patterns = [
            r'accuracy|precision|recall|f1|score|percentage|%',
            r'time|speed|latency|throughput|performance',
            r'cost|budget|expense|roi|return on investment',
            r'user satisfaction|engagement|adoption|usage',
            r'error rate|failure rate|success rate',
            r'scalability|reliability|availability|uptime'
        ]
        
        for pattern in metric_patterns:
            matches = re.findall(pattern, content.lower())
            metrics.extend(matches)
        
        # Extract specific numeric targets
        numeric_targets = re.findall(r'(\d+(?:\.\d+)?)\s*(?:%|percent|times|x|fold)', content.lower())
        metrics.extend([f"{num}x improvement" for num in numeric_targets])
        
        return list(set(metrics))[:10]  # Limit and deduplicate

    def analyze_tone_characteristics(self, content: str) -> List[str]:
        """Analyze the tone and style characteristics of the response."""
        characteristics = []
        content_lower = content.lower()
        
        tone_indicators = {
            'formal': [r'furthermore', r'therefore', r'consequently', r'moreover'],
            'practical': [r'step-by-step', r'hands-on', r'practical', r'actionable'],
            'innovative': [r'novel', r'breakthrough', r'revolutionary', r'cutting-edge'],
            'cautious': [r'however', r'potential risks', r'considerations', r'challenges'],
            'ambitious': [r'transform', r'revolutionize', r'significantly', r'dramatically'],
            'technical': [r'algorithm', r'implementation', r'architecture', r'specification'],
            'collaborative': [r'team', r'together', r'collective', r'shared', r'community']
        }
        
        for tone, indicators in tone_indicators.items():
            if any(re.search(indicator, content_lower) for indicator in indicators):
                characteristics.append(tone)
        
        # Analyze sentence structure for complexity
        sentences = content.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        if avg_sentence_length > 25:
            characteristics.append('complex')
        elif avg_sentence_length < 15:
            characteristics.append('concise')
        
        return characteristics

    def calculate_performance_tier(self, overall_score: float) -> str:
        """Determine performance tier based on score."""
        if overall_score >= 0.55:
            return "excellent"
        elif overall_score >= 0.50:
            return "good"
        elif overall_score >= 0.45:
            return "average"
        else:
            return "poor"

    def determine_innovation_approach(self, content: str, novelty_score: float) -> str:
        """Determine the type of innovation approach."""
        content_lower = content.lower()
        
        if novelty_score > 0.1 or any(term in content_lower for term in ['revolutionary', 'paradigm', 'breakthrough', 'transform']):
            return "paradigm_shift"
        elif any(term in content_lower for term in ['disrupt', 'challenge', 'alternative', 'new approach']):
            return "disruptive"
        elif any(term in content_lower for term in ['combine', 'integrate', 'synthesis', 'hybrid']):
            return "synthesis"
        else:
            return "incremental"

    def extract_contrarian_elements(self, content: str, framework: str) -> List[str]:
        """Identify contrarian or challenging elements in the response."""
        elements = []
        content_lower = content.lower()
        
        contrarian_phrases = [
            'however', 'contrary to', 'instead of', 'rather than', 'alternative to',
            'challenge', 'question', 'reconsider', 'traditional approach',
            'conventional wisdom', 'opposite', 'different perspective'
        ]
        
        for phrase in contrarian_phrases:
            if phrase in content_lower:
                # Extract context around the contrarian phrase
                start = max(0, content_lower.find(phrase) - 50)
                end = min(len(content), content_lower.find(phrase) + 100)
                context = content[start:end].strip()
                elements.append(context)
        
        # If this is a contrarian framework, mark it specially
        if framework == "ins_contrarian":
            elements.append("Explicitly contrarian framework approach")
        
        return elements[:5]  # Limit to 5 most relevant

    def process_single_response(self, filepath: Path, performance_data: Dict) -> Dict[str, Any]:
        """Process a single raw response file and extract all metadata."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract basic metadata from file header
        lines = content.split('\n')
        metadata = {}
        
        for line in lines[:20]:  # Check first 20 lines for metadata
            if line.startswith('**Combination ID:**'):
                metadata['combination_id'] = line.split('**Combination ID:**', 1)[1].strip()
            elif line.startswith('**Model:**'):
                metadata['model_id'] = line.split('**Model:**', 1)[1].strip()
            elif line.startswith('**Template:**'):
                metadata['cognitive_framework'] = line.split('**Template:**', 1)[1].strip()
            elif line.startswith('**Domain:**'):
                metadata['domain'] = line.split('**Domain:**', 1)[1].strip()
            elif line.startswith('**Duration:**'):
                duration_str = line.split('**Duration:**', 1)[1].strip()
                metadata['duration_seconds'] = float(re.findall(r'[\d.]+', duration_str)[0])
        
        # Extract response content (everything after "## Raw Response")
        response_start = content.find("## Raw Response")
        if response_start != -1:
            response_content = content[response_start + len("## Raw Response"):].strip()
        else:
            response_content = content
        
        # Get performance data
        combination_id = metadata.get('combination_id', '')
        perf_data = performance_data.get(combination_id, {})
        
        # Extract model provider from model_id
        model_id = metadata.get('model_id', '')
        model_provider = 'unknown'
        for provider in ['claude', 'gpt', 'gemini', 'grok', 'deepseek', 'perplexity', 'llama', 'qwen', 'mixtral', 'o3']:
            if provider in model_id.lower():
                model_provider = provider
                break
        
        # Get framework characteristics
        framework = metadata.get('cognitive_framework', '')
        framework_info = self.framework_characteristics.get(framework, {})
        
        # Build comprehensive metadata
        enhanced_metadata = {
            # Core metadata
            "combination_id": combination_id,
            "model_id": model_id,
            "model_provider": model_provider,
            "cognitive_framework": framework,
            "domain": metadata.get('domain', ''),
            "duration_seconds": metadata.get('duration_seconds', 0),
            "response_length_chars": len(response_content),
            "response_length_words": len(response_content.split()),
            
            # Performance metadata
            "overall_score": perf_data.get('overall_score', 0),
            "actionability_score": perf_data.get('actionability_score', 0),
            "comprehensiveness_score": perf_data.get('comprehensiveness_score', 0),
            "feasibility_score": perf_data.get('feasibility_score', 0),
            "impact_score": perf_data.get('impact_score', 0),
            "novelty_score": perf_data.get('novelty_score', 0),
            "specificity_score": perf_data.get('specificity_score', 0),
            "performance_tier": self.calculate_performance_tier(perf_data.get('overall_score', 0)),
            
            # Cognitive analysis
            "thinking_style": framework_info.get('thinking_style', 'unknown'),
            "perspective_type": framework_info.get('perspective_type', 'unknown'),
            "complexity_level": framework_info.get('complexity_level', 'intermediate'),
            "focus_area": framework_info.get('focus_area', 'unknown'),
            "innovation_approach": self.determine_innovation_approach(response_content, perf_data.get('novelty_score', 0)),
            
            # Content analysis
            "key_concepts": self.extract_key_concepts(response_content),
            "approach_categories": self.analyze_approach_categories(response_content),
            "success_metrics_mentioned": self.extract_success_metrics(response_content),
            "tone_characteristics": self.analyze_tone_characteristics(response_content),
            
            # Cognitive diversity tags
            "framework_specialization": framework_info.get('specialization', 'Unknown specialization'),
            "model_specialization": self.model_specializations.get(model_provider, 'Unknown specialization'),
            "contrarian_elements": self.extract_contrarian_elements(response_content, framework),
            "outlier_status": perf_data.get('overall_score', 0.5) < 0.4 or perf_data.get('overall_score', 0.5) > 0.57,
            
            # File reference
            "file_path": str(filepath.relative_to(self.run_directory)),
            "content_preview": response_content[:300] + "..." if len(response_content) > 300 else response_content
        }
        
        return enhanced_metadata

    def calculate_ranking_and_percentiles(self, all_metadata: List[Dict]) -> List[Dict]:
        """Calculate rankings and percentiles for all responses."""
        # Sort by overall score for ranking
        sorted_by_score = sorted(all_metadata, key=lambda x: x['overall_score'], reverse=True)
        
        for i, metadata in enumerate(sorted_by_score):
            metadata['rank_in_run'] = i + 1
            metadata['percentile_score'] = ((len(sorted_by_score) - i) / len(sorted_by_score)) * 100
        
        return all_metadata

    def process_all_responses(self) -> Dict[str, Any]:
        """Process all raw responses and create comprehensive metadata index."""
        if not self.raw_responses_dir.exists():
            raise FileNotFoundError(f"Raw responses directory not found: {self.raw_responses_dir}")
        
        print(f"Processing responses from: {self.raw_responses_dir}")
        
        # Load performance data
        performance_data = self.load_performance_data()
        print(f"Loaded performance data for {len(performance_data)} combinations")
        
        # Process all response files
        all_metadata = []
        response_files = list(self.raw_responses_dir.glob("*.md"))
        
        print(f"Processing {len(response_files)} response files...")
        
        for i, filepath in enumerate(response_files):
            if i % 10 == 0:
                print(f"  Processed {i}/{len(response_files)} files...")
            
            try:
                metadata = self.process_single_response(filepath, performance_data)
                all_metadata.append(metadata)
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
                continue
        
        # Calculate rankings and percentiles
        all_metadata = self.calculate_ranking_and_percentiles(all_metadata)
        
        # Create summary statistics
        scores = [m['overall_score'] for m in all_metadata]
        frameworks = [m['cognitive_framework'] for m in all_metadata]
        models = [m['model_provider'] for m in all_metadata]
        
        summary = {
            "total_responses": len(all_metadata),
            "score_statistics": {
                "min": min(scores) if scores else 0,
                "max": max(scores) if scores else 0,
                "mean": sum(scores) / len(scores) if scores else 0,
                "median": sorted(scores)[len(scores)//2] if scores else 0
            },
            "framework_distribution": dict(Counter(frameworks)),
            "model_distribution": dict(Counter(models)),
            "performance_tier_distribution": dict(Counter(m['performance_tier'] for m in all_metadata))
        }
        
        # Create the final index
        index = {
            "metadata_version": "1.0",
            "extraction_timestamp": datetime.now().isoformat(),
            "run_directory": str(self.run_directory),
            "summary": summary,
            "responses": all_metadata
        }
        
        print(f"✅ Processed {len(all_metadata)} responses successfully")
        return index

    def save_index(self, index: Dict[str, Any]):
        """Save the cognitive diversity index to file."""
        with open(self.metadata_output, 'w') as f:
            json.dump(index, f, indent=2)
        
        print(f"💾 Saved cognitive diversity index to: {self.metadata_output}")
        print(f"📊 Index contains {len(index['responses'])} responses with enhanced metadata")

def main():
    """Main execution function."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python cognitive_diversity_extractor.py <run_directory>")
        print("Example: python cognitive_diversity_extractor.py data/output/run_20250812_133617")
        sys.exit(1)
    
    run_directory = sys.argv[1]
    
    try:
        extractor = CognitiveDiversityExtractor(run_directory)
        index = extractor.process_all_responses()
        extractor.save_index(index)
        
        print("\n🎉 Cognitive Diversity Extraction Complete!")
        print(f"📁 Enhanced metadata saved to: {extractor.metadata_output}")
        print(f"🔍 Ready for cognitive diversity exploration!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()