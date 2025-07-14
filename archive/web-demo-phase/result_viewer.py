"""
Result Viewer for ISEE Framework

This utility helps visualize and analyze the results from the ISEE framework.
It provides a simple interface for exploring the generated ideas, their scores,
and the relationships between different combinations.
"""

import os
import json
import argparse
from typing import Dict, Any, List, Optional, Tuple
import time
from datetime import datetime

def load_state(file_path: str) -> Dict[str, Any]:
    """Load a state file.
    
    Args:
        file_path: Path to the state file.
        
    Returns:
        The loaded state.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    with open(file_path, 'r') as f:
        state = json.load(f)
    
    return state

def format_timestamp(timestamp: float) -> str:
    """Format a Unix timestamp as a human-readable string.
    
    Args:
        timestamp: Unix timestamp.
        
    Returns:
        Formatted timestamp string.
    """
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def display_combination_info(combination: Dict[str, Any]) -> None:
    """Display information about a combination.
    
    Args:
        combination: Combination dictionary.
    """
    print(f"ID: {combination['id']}")
    print(f"Model: {combination['model']}")
    print(f"Template: {combination['template']}")
    print(f"Query: {combination['query']}")
    print(f"Domain: {combination['domain']}")

def display_result_info(result: Dict[str, Any]) -> None:
    """Display information about a result.
    
    Args:
        result: Result dictionary.
    """
    print(f"Combination ID: {result['combination_id']}")
    print("\nPrompt:")
    print("-" * 80)
    print(result['prompt'])
    print("-" * 80)
    
    print("\nResponse:")
    print("-" * 80)
    print(result['response'])
    print("-" * 80)
    
    if 'metadata' in result:
        print("\nMetadata:")
        for key, value in result['metadata'].items():
            if key == 'timestamp':
                value = format_timestamp(value)
            print(f"- {key}: {value}")

def display_evaluation_info(combination_id: str, evaluation: Dict[str, float]) -> None:
    """Display evaluation information for a result.
    
    Args:
        combination_id: ID of the combination.
        evaluation: Evaluation scores.
    """
    print(f"Evaluation for combination: {combination_id}")
    print("\nScores:")
    
    # Sort by score (descending)
    sorted_scores = sorted(
        [(criterion, score) for criterion, score in evaluation.items() if criterion != 'overall'],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Display individual scores
    for criterion, score in sorted_scores:
        print(f"- {criterion}: {score:.4f}")
    
    # Display overall score
    if 'overall' in evaluation:
        print("\nOverall Score:", f"{evaluation['overall']:.4f}")

def display_idea_info(idea_id: str, idea: Dict[str, Any]) -> None:
    """Display information about a synthesized idea.
    
    Args:
        idea_id: ID of the idea.
        idea: Idea dictionary.
    """
    print(f"ID: {idea_id}")
    print(f"Title: {idea['title']}")
    print("\nDescription:")
    print(idea['description'])
    
    print("\nContent:")
    print("-" * 80)
    print(idea['text'])
    print("-" * 80)
    
    if 'source_combinations' in idea:
        print("\nSource Combinations:")
        for combo_id in idea['source_combinations']:
            print(f"- {combo_id}")
    
    if 'metadata' in idea:
        print("\nMetadata:")
        for key, value in idea['metadata'].items():
            print(f"- {key}: {value}")

def list_top_results(state: Dict[str, Any], criterion: str = 'overall', n: int = 10) -> List[Tuple[str, float]]:
    """List the top N results based on a specific criterion.
    
    Args:
        state: The application state.
        criterion: The criterion to sort by.
        n: Number of top results to return.
        
    Returns:
        List of (combination_id, score) tuples sorted by the criterion in descending order.
    """
    if 'evaluations' not in state or not state['evaluations']:
        print("No evaluations found in the state")
        return []
    
    # Get all evaluations
    evaluations = state['evaluations']
    
    # Filter evaluations that have the requested criterion
    scored_results = []
    for combo_id, scores in evaluations.items():
        if criterion in scores:
            scored_results.append((combo_id, scores[criterion]))
    
    # Sort by score in descending order
    scored_results.sort(key=lambda x: x[1], reverse=True)
    
    # Return the top N
    return scored_results[:n]

def display_state_summary(state: Dict[str, Any]) -> None:
    """Display a summary of the state.
    
    Args:
        state: The application state.
    """
    print("=== ISEE State Summary ===\n")
    
    # Count entities
    combinations_count = len(state.get('combinations', []))
    results_count = len(state.get('results', {}))
    evaluations_count = len(state.get('evaluations', {}))
    ideas_count = len(state.get('synthesized_ideas', {}))
    
    print(f"Combinations: {combinations_count}")
    print(f"Results: {results_count}")
    print(f"Evaluations: {evaluations_count}")
    print(f"Synthesized Ideas: {ideas_count}")
    
    # Display top results if available
    if evaluations_count > 0:
        print("\nTop 5 Results by Overall Score:")
        top_results = list_top_results(state, 'overall', 5)
        
        for i, (combo_id, score) in enumerate(top_results, 1):
            print(f"{i}. {combo_id} (Score: {score:.4f})")
    
    # Display ideas if available
    if ideas_count > 0:
        print("\nSynthesized Ideas:")
        for i, (idea_id, idea) in enumerate(state.get('synthesized_ideas', {}).items(), 1):
            print(f"{i}. {idea['title']}")

def interactive_viewer(state: Dict[str, Any]) -> None:
    """Run an interactive viewer for exploring the state.
    
    Args:
        state: The application state.
    """
    while True:
        print("\n=== ISEE Result Viewer ===")
        print("1. View state summary")
        print("2. View top results")
        print("3. View result details")
        print("4. View synthesized ideas")
        print("5. Export to markdown")
        print("0. Exit")
        
        choice = input("\nEnter choice: ")
        
        if choice == '0':
            break
        
        elif choice == '1':
            display_state_summary(state)
        
        elif choice == '2':
            criterion = input("Sort by criterion (default: overall): ") or 'overall'
            try:
                n = int(input("Number of results to show (default: 10): ") or 10)
            except ValueError:
                n = 10
            
            top_results = list_top_results(state, criterion, n)
            
            print(f"\nTop {len(top_results)} Results by {criterion.capitalize()} Score:")
            for i, (combo_id, score) in enumerate(top_results, 1):
                print(f"{i}. {combo_id} (Score: {score:.4f})")
            
            # Allow viewing details
            if top_results:
                try:
                    idx = int(input("\nEnter number to view details (0 to skip): "))
                    if 1 <= idx <= len(top_results):
                        combo_id = top_results[idx-1][0]
                        print("\n" + "=" * 80)
                        
                        # Display result
                        if combo_id in state.get('results', {}):
                            display_result_info(state['results'][combo_id])
                        
                        # Display evaluation
                        if combo_id in state.get('evaluations', {}):
                            print("\n" + "-" * 80)
                            display_evaluation_info(combo_id, state['evaluations'][combo_id])
                        
                        print("=" * 80)
                except ValueError:
                    pass
        
        elif choice == '3':
            combo_id = input("Enter combination ID: ")
            
            if combo_id in state.get('results', {}):
                print("\n" + "=" * 80)
                display_result_info(state['results'][combo_id])
                
                if combo_id in state.get('evaluations', {}):
                    print("\n" + "-" * 80)
                    display_evaluation_info(combo_id, state['evaluations'][combo_id])
                
                print("=" * 80)
            else:
                print(f"No result found with ID: {combo_id}")
        
        elif choice == '4':
            ideas = state.get('synthesized_ideas', {})
            
            if not ideas:
                print("No synthesized ideas found in the state")
                continue
            
            print("\nSynthesized Ideas:")
            for i, (idea_id, idea) in enumerate(ideas.items(), 1):
                print(f"{i}. {idea['title']}")
            
            try:
                idx = int(input("\nEnter number to view details (0 to skip): "))
                if 1 <= idx <= len(ideas):
                    idea_id = list(ideas.keys())[idx-1]
                    print("\n" + "=" * 80)
                    display_idea_info(idea_id, ideas[idea_id])
                    print("=" * 80)
            except ValueError:
                pass
        
        elif choice == '5':
            output_path = input("Enter output file path: ")
            
            try:
                # Format ideas as markdown
                ideas = state.get('synthesized_ideas', {})
                
                if not ideas:
                    print("No synthesized ideas found in the state")
                    continue
                
                output = "# Synthesized Ideas\n\n"
                
                for idea_id, idea in ideas.items():
                    output += f"## {idea['title']}\n\n"
                    output += f"{idea['description']}\n\n"
                    output += f"### Key Points\n\n"
                    output += f"{idea['text']}\n\n"
                    
                    if 'metadata' in idea:
                        output += "### Metadata\n\n"
                        for key, value in idea['metadata'].items():
                            output += f"- **{key}**: {value}\n"
                    
                    output += "\n---\n\n"
                
                # Write to file
                with open(output_path, 'w') as f:
                    f.write(output)
                
                print(f"Output saved to {output_path}")
            
            except Exception as e:
                print(f"Error exporting ideas: {str(e)}")
        
        else:
            print("Invalid choice, please try again")
        
        # Pause before showing menu again
        input("\nPress Enter to continue...")

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="ISEE Result Viewer")
    parser.add_argument("--state", required=True, help="Path to state file")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--summary", action="store_true", help="Display state summary")
    parser.add_argument("--top", type=int, help="Display top N results")
    parser.add_argument("--criterion", default="overall", help="Criterion to sort by")
    parser.add_argument("--result", help="Display details for a specific result")
    parser.add_argument("--idea", help="Display details for a specific idea")
    
    args = parser.parse_args()
    
    try:
        # Load the state
        state = load_state(args.state)
        
        # Interactive mode
        if args.interactive:
            interactive_viewer(state)
            return
        
        # Summary
        if args.summary:
            display_state_summary(state)
        
        # Top results
        if args.top:
            top_results = list_top_results(state, args.criterion, args.top)
            
            print(f"\nTop {len(top_results)} Results by {args.criterion.capitalize()} Score:")
            for i, (combo_id, score) in enumerate(top_results, 1):
                print(f"{i}. {combo_id} (Score: {score:.4f})")
        
        # Result details
        if args.result:
            if args.result in state.get('results', {}):
                print("\n" + "=" * 80)
                display_result_info(state['results'][args.result])
                
                if args.result in state.get('evaluations', {}):
                    print("\n" + "-" * 80)
                    display_evaluation_info(args.result, state['evaluations'][args.result])
                
                print("=" * 80)
            else:
                print(f"No result found with ID: {args.result}")
        
        # Idea details
        if args.idea:
            ideas = state.get('synthesized_ideas', {})
            if args.idea in ideas:
                print("\n" + "=" * 80)
                display_idea_info(args.idea, ideas[args.idea])
                print("=" * 80)
            else:
                print(f"No idea found with ID: {args.idea}")
    
    except FileNotFoundError:
        print(f"State file not found: {args.state}")
    except json.JSONDecodeError:
        print(f"Invalid JSON in state file: {args.state}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
