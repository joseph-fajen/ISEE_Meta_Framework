#!/usr/bin/env python3
"""
Cognitive Diversity Browser for ISEE
Interactive exploration tool for the 66 raw responses with rich filtering and discovery.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
import re

class CognitiveDiversityBrowser:
    def __init__(self, index_file: str):
        """Initialize the browser with a cognitive diversity index file."""
        self.index_file = Path(index_file)
        self.index_data = self.load_index()
        self.responses = self.index_data['responses']
        self.summary = self.index_data['summary']
        
    def load_index(self) -> Dict[str, Any]:
        """Load the cognitive diversity index."""
        if not self.index_file.exists():
            raise FileNotFoundError(f"Index file not found: {self.index_file}")
        
        with open(self.index_file, 'r') as f:
            return json.load(f)
    
    def display_summary(self):
        """Display summary statistics of the run."""
        print("🧠 COGNITIVE DIVERSITY EXPLORATION PLATFORM")
        print("=" * 60)
        print(f"📊 Total Responses: {self.summary['total_responses']}")
        print(f"📈 Score Range: {self.summary['score_statistics']['min']:.3f} - {self.summary['score_statistics']['max']:.3f}")
        print(f"🎯 Average Score: {self.summary['score_statistics']['mean']:.3f}")
        print()
        
        print("🎭 Cognitive Framework Distribution:")
        for framework, count in sorted(self.summary['framework_distribution'].items()):
            print(f"  {framework}: {count}")
        print()
        
        print("🤖 Model Provider Distribution:")
        for model, count in sorted(self.summary['model_distribution'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {model}: {count}")
        print()
        
        print("🏆 Performance Tier Distribution:")
        for tier, count in sorted(self.summary['performance_tier_distribution'].items()):
            print(f"  {tier}: {count}")
        print()

    def filter_responses(self, 
                        min_score: Optional[float] = None,
                        max_score: Optional[float] = None,
                        frameworks: Optional[List[str]] = None,
                        models: Optional[List[str]] = None,
                        domains: Optional[List[str]] = None,
                        performance_tiers: Optional[List[str]] = None,
                        thinking_styles: Optional[List[str]] = None,
                        search_terms: Optional[List[str]] = None,
                        innovation_approaches: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Filter responses based on various criteria."""
        
        filtered = self.responses.copy()
        
        # Score filtering
        if min_score is not None:
            filtered = [r for r in filtered if r['overall_score'] >= min_score]
        if max_score is not None:
            filtered = [r for r in filtered if r['overall_score'] <= max_score]
        
        # Framework filtering
        if frameworks:
            filtered = [r for r in filtered if r['cognitive_framework'] in frameworks]
        
        # Model filtering
        if models:
            filtered = [r for r in filtered if r['model_provider'] in models]
        
        # Domain filtering
        if domains:
            filtered = [r for r in filtered if any(domain in r['domain'] for domain in domains)]
        
        # Performance tier filtering
        if performance_tiers:
            filtered = [r for r in filtered if r['performance_tier'] in performance_tiers]
        
        # Thinking style filtering
        if thinking_styles:
            filtered = [r for r in filtered if r['thinking_style'] in thinking_styles]
        
        # Innovation approach filtering
        if innovation_approaches:
            filtered = [r for r in filtered if r['innovation_approach'] in innovation_approaches]
        
        # Search term filtering
        if search_terms:
            for term in search_terms:
                term_lower = term.lower()
                filtered = [r for r in filtered if 
                           term_lower in r['content_preview'].lower() or
                           term_lower in ' '.join(r['key_concepts']).lower() or
                           term_lower in ' '.join(r['approach_categories']).lower()]
        
        return filtered

    def display_response_summary(self, response: Dict[str, Any], index: int = 0):
        """Display a summary of a single response."""
        print(f"📝 Response #{response['rank_in_run']} | Score: {response['overall_score']:.3f} | {response['performance_tier'].upper()}")
        print(f"🤖 {response['model_provider'].title()} | 🧠 {response['cognitive_framework']}")
        print(f"🌐 {response['domain']}")
        print(f"💭 {response['thinking_style'].title()} thinking | 🎯 {response['innovation_approach'].replace('_', ' ').title()}")
        print(f"🔍 Key concepts: {', '.join(response['key_concepts'][:5])}")
        print(f"📊 Scores - Feasibility: {response['feasibility_score']:.2f} | Impact: {response['impact_score']:.2f} | Novelty: {response['novelty_score']:.2f}")
        
        if response['contrarian_elements']:
            print(f"🔄 Contrarian elements: {len(response['contrarian_elements'])} found")
        
        print(f"📄 Preview: {response['content_preview'][:150]}...")
        print("-" * 60)

    def display_responses(self, responses: List[Dict[str, Any]], limit: int = 10):
        """Display a list of responses with summaries."""
        if not responses:
            print("❌ No responses match the current filters.")
            return
        
        print(f"📋 Showing {min(len(responses), limit)} of {len(responses)} responses:")
        print()
        
        for i, response in enumerate(responses[:limit]):
            self.display_response_summary(response, i)

    def analyze_cognitive_patterns(self, responses: List[Dict[str, Any]]):
        """Analyze patterns in the filtered responses."""
        if not responses:
            return
        
        print("🧠 COGNITIVE DIVERSITY ANALYSIS")
        print("=" * 40)
        
        # Framework effectiveness
        framework_scores = defaultdict(list)
        for r in responses:
            framework_scores[r['cognitive_framework']].append(r['overall_score'])
        
        print("🎭 Framework Performance:")
        framework_avg = {f: sum(scores)/len(scores) for f, scores in framework_scores.items()}
        for framework, avg_score in sorted(framework_avg.items(), key=lambda x: x[1], reverse=True):
            count = len(framework_scores[framework])
            print(f"  {framework}: {avg_score:.3f} avg ({count} responses)")
        print()
        
        # Model specializations
        model_scores = defaultdict(list)
        for r in responses:
            model_scores[r['model_provider']].append(r['overall_score'])
        
        print("🤖 Model Performance:")
        model_avg = {m: sum(scores)/len(scores) for m, scores in model_scores.items()}
        for model, avg_score in sorted(model_avg.items(), key=lambda x: x[1], reverse=True):
            count = len(model_scores[model])
            print(f"  {model}: {avg_score:.3f} avg ({count} responses)")
        print()
        
        # Innovation approaches
        innovation_dist = Counter(r['innovation_approach'] for r in responses)
        print("💡 Innovation Approaches:")
        for approach, count in innovation_dist.most_common():
            print(f"  {approach.replace('_', ' ').title()}: {count}")
        print()
        
        # Outlier detection
        outliers = [r for r in responses if r['outlier_status']]
        print(f"🎯 Outlier Responses: {len(outliers)} found")
        if outliers:
            print("  High-value unique perspectives:")
            for outlier in outliers[:3]:
                print(f"    - {outlier['cognitive_framework']} + {outlier['model_provider']}: {outlier['overall_score']:.3f}")
        print()

    def find_similar_responses(self, response_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find responses similar to a given response."""
        target_response = None
        for r in self.responses:
            if response_id in r['combination_id']:
                target_response = r
                break
        
        if not target_response:
            return []
        
        # Calculate similarity based on multiple factors
        similarities = []
        target_concepts = set(target_response['key_concepts'])
        target_categories = set(target_response['approach_categories'])
        
        for response in self.responses:
            if response['combination_id'] == target_response['combination_id']:
                continue
            
            # Concept similarity
            response_concepts = set(response['key_concepts'])
            concept_similarity = len(target_concepts & response_concepts) / len(target_concepts | response_concepts) if target_concepts | response_concepts else 0
            
            # Category similarity
            response_categories = set(response['approach_categories'])
            category_similarity = len(target_categories & response_categories) / len(target_categories | response_categories) if target_categories | response_categories else 0
            
            # Score similarity
            score_similarity = 1 - abs(target_response['overall_score'] - response['overall_score']) / 0.6  # Normalize to 0-1
            
            # Combined similarity
            combined_similarity = (concept_similarity * 0.4 + category_similarity * 0.3 + score_similarity * 0.3)
            
            similarities.append((response, combined_similarity))
        
        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [response for response, similarity in similarities[:limit]]

    def explore_contrarian_perspectives(self):
        """Find and display contrarian and unique perspectives."""
        print("🔄 CONTRARIAN & UNIQUE PERSPECTIVES")
        print("=" * 40)
        
        # Find responses with contrarian elements
        contrarian_responses = [r for r in self.responses if r['contrarian_elements']]
        
        print(f"📊 {len(contrarian_responses)} responses contain contrarian elements")
        print()
        
        # Group by contrarian approach
        contrarian_frameworks = [r for r in self.responses if 'contrarian' in r['cognitive_framework']]
        print(f"🎭 Explicitly Contrarian Framework: {len(contrarian_frameworks)} responses")
        if contrarian_frameworks:
            avg_score = sum(r['overall_score'] for r in contrarian_frameworks) / len(contrarian_frameworks)
            print(f"   Average performance: {avg_score:.3f}")
        print()
        
        # Find high-performing contrarian responses
        high_performing_contrarian = [r for r in contrarian_responses if r['overall_score'] > 0.52]
        print(f"🏆 High-performing contrarian responses: {len(high_performing_contrarian)}")
        
        for response in high_performing_contrarian[:3]:
            print(f"  📝 {response['cognitive_framework']} + {response['model_provider']}: {response['overall_score']:.3f}")
            if response['contrarian_elements']:
                print(f"     Contrarian insight: {response['contrarian_elements'][0][:100]}...")
        print()

    def search_by_concept(self, concept: str) -> List[Dict[str, Any]]:
        """Search for responses containing specific concepts or technologies."""
        concept_lower = concept.lower()
        matching_responses = []
        
        for response in self.responses:
            # Search in key concepts
            if any(concept_lower in concept.lower() for concept in response['key_concepts']):
                matching_responses.append(response)
                continue
            
            # Search in content preview
            if concept_lower in response['content_preview'].lower():
                matching_responses.append(response)
                continue
        
        # Sort by relevance (score)
        matching_responses.sort(key=lambda x: x['overall_score'], reverse=True)
        return matching_responses

    def interactive_menu(self):
        """Interactive menu for exploring cognitive diversity."""
        while True:
            print("\n🧠 COGNITIVE DIVERSITY EXPLORER")
            print("=" * 40)
            print("1. View summary statistics")
            print("2. Filter and explore responses")
            print("3. Analyze cognitive patterns")
            print("4. Find contrarian perspectives") 
            print("5. Search by concept/technology")
            print("6. Compare cognitive frameworks")
            print("7. Export filtered results")
            print("0. Exit")
            
            try:
                choice = input("\nSelect option (0-7): ").strip()
                
                if choice == "0":
                    print("👋 Happy exploring!")
                    break
                elif choice == "1":
                    self.display_summary()
                elif choice == "2":
                    self.interactive_filter()
                elif choice == "3":
                    responses = self.get_current_filter()
                    self.analyze_cognitive_patterns(responses)
                elif choice == "4":
                    self.explore_contrarian_perspectives()
                elif choice == "5":
                    self.interactive_search()
                elif choice == "6":
                    self.compare_frameworks()
                elif choice == "7":
                    self.export_results()
                else:
                    print("❌ Invalid option. Please try again.")
                    
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def interactive_filter(self):
        """Interactive filtering interface."""
        print("\n🔍 RESPONSE FILTERING")
        print("=" * 30)
        
        # Score filtering
        print("Score filtering (press Enter to skip):")
        min_score_input = input("  Minimum score (0.0-1.0): ").strip()
        min_score = float(min_score_input) if min_score_input else None
        
        max_score_input = input("  Maximum score (0.0-1.0): ").strip()
        max_score = float(max_score_input) if max_score_input else None
        
        # Framework filtering
        available_frameworks = list(self.summary['framework_distribution'].keys())
        print(f"\nAvailable frameworks: {', '.join(available_frameworks)}")
        frameworks_input = input("  Select frameworks (comma-separated): ").strip()
        frameworks = [f.strip() for f in frameworks_input.split(',')] if frameworks_input else None
        
        # Model filtering
        available_models = list(self.summary['model_distribution'].keys())
        print(f"\nAvailable models: {', '.join(available_models)}")
        models_input = input("  Select models (comma-separated): ").strip()
        models = [m.strip() for m in models_input.split(',')] if models_input else None
        
        # Apply filters
        filtered = self.filter_responses(
            min_score=min_score,
            max_score=max_score,
            frameworks=frameworks,
            models=models
        )
        
        print(f"\n✅ Found {len(filtered)} matching responses")
        
        if filtered:
            limit_input = input("How many to display? (default 10): ").strip()
            limit = int(limit_input) if limit_input.isdigit() else 10
            self.display_responses(filtered, limit)

    def interactive_search(self):
        """Interactive concept search."""
        print("\n🔍 CONCEPT SEARCH")
        print("=" * 25)
        
        concept = input("Enter concept/technology to search for: ").strip()
        if not concept:
            print("❌ No search term provided")
            return
        
        results = self.search_by_concept(concept)
        print(f"\n✅ Found {len(results)} responses mentioning '{concept}'")
        
        if results:
            limit_input = input("How many to display? (default 5): ").strip()
            limit = int(limit_input) if limit_input.isdigit() else 5
            self.display_responses(results, limit)

    def compare_frameworks(self):
        """Compare different cognitive frameworks."""
        print("\n🎭 FRAMEWORK COMPARISON")
        print("=" * 30)
        
        available_frameworks = list(self.summary['framework_distribution'].keys())
        print(f"Available frameworks: {', '.join(available_frameworks)}")
        
        framework1 = input("Select first framework: ").strip()
        framework2 = input("Select second framework: ").strip()
        
        if framework1 not in available_frameworks or framework2 not in available_frameworks:
            print("❌ Invalid framework selection")
            return
        
        responses1 = self.filter_responses(frameworks=[framework1])
        responses2 = self.filter_responses(frameworks=[framework2])
        
        print(f"\n📊 Comparison: {framework1} vs {framework2}")
        print("-" * 50)
        
        avg1 = sum(r['overall_score'] for r in responses1) / len(responses1) if responses1 else 0
        avg2 = sum(r['overall_score'] for r in responses2) / len(responses2) if responses2 else 0
        
        print(f"{framework1}: {avg1:.3f} average score ({len(responses1)} responses)")
        print(f"{framework2}: {avg2:.3f} average score ({len(responses2)} responses)")
        
        # Show top response from each
        if responses1:
            top1 = max(responses1, key=lambda x: x['overall_score'])
            print(f"\nTop {framework1} response:")
            self.display_response_summary(top1)
        
        if responses2:
            top2 = max(responses2, key=lambda x: x['overall_score'])
            print(f"\nTop {framework2} response:")
            self.display_response_summary(top2)

    def get_current_filter(self) -> List[Dict[str, Any]]:
        """Get current filtered responses (for now, return all)."""
        return self.responses

    def export_results(self):
        """Export filtered results to JSON."""
        print("\n💾 EXPORT RESULTS")
        print("=" * 25)
        
        responses = self.get_current_filter()
        export_file = input("Export filename (default: cognitive_diversity_export.json): ").strip()
        if not export_file:
            export_file = "cognitive_diversity_export.json"
        
        export_data = {
            "export_timestamp": json.dumps(self.index_data['extraction_timestamp']),
            "total_responses": len(responses),
            "responses": responses
        }
        
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ Exported {len(responses)} responses to {export_file}")

def main():
    """Main execution function."""
    if len(sys.argv) != 2:
        print("Usage: python cognitive_diversity_browser.py <index_file>")
        print("Example: python cognitive_diversity_browser.py data/output/run_20250812_133617/cognitive_diversity_index.json")
        sys.exit(1)
    
    index_file = sys.argv[1]
    
    try:
        browser = CognitiveDiversityBrowser(index_file)
        browser.interactive_menu()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()