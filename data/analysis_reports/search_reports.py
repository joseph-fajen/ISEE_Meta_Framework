#!/usr/bin/env python3
import json
import sys
from datetime import datetime

def search_reports(query=None, min_score=None, max_score=None, model_name=None, days_back=None):
    """Search analysis reports by various criteria"""
    try:
        with open('/Users/josephfajen/git/ISEE_Meta_Framework/data/analysis_reports/index.json', 'r') as f:
            index_data = json.load(f)
    except FileNotFoundError:
        print("No index.json found")
        return []
    
    results = []
    for report in index_data.get('reports', []):
        # Query text search
        if query and query.lower() not in report.get('query_summary', '').lower():
            continue
            
        # Score filtering
        if min_score and (not report.get('avg_score') or float(report['avg_score']) < min_score):
            continue
        if max_score and (not report.get('avg_score') or float(report['avg_score']) > max_score):
            continue
            
        # Model name search
        if model_name and (model_name.lower() not in report.get('top_performer', '').lower() and 
                          model_name.lower() not in report.get('worst_performer', '').lower()):
            continue
            
        # Date filtering
        if days_back:
            report_date = datetime.fromisoformat(report['analysis_date'])
            if (datetime.now() - report_date).days > days_back:
                continue
                
        results.append(report)
    
    return results

def print_results(results):
    """Print search results in a formatted way"""
    if not results:
        print("No reports found matching criteria")
        return
        
    print(f"\nFound {len(results)} reports:")
    print("-" * 80)
    for report in results:
        print(f"Date: {report['analysis_date']}")
        print(f"Run: {report['run_analyzed']}")
        print(f"Query: {report['query_summary'][:60]}...")
        print(f"Score: {report.get('avg_score', 'N/A')} | Top: {report.get('top_performer', 'N/A')}")
        print(f"File: {report['file_path']}")
        if 'key_findings' in report:
            print(f"Key Findings: {len(report['key_findings'])} items")
        print("-" * 40)

if __name__ == "__main__":
    # Command line interface
    if len(sys.argv) == 1:
        # Show recent reports
        results = search_reports(days_back=30)
        print("Recent reports (last 30 days):")
        print_results(results)
    elif sys.argv[1] == "query" and len(sys.argv) > 2:
        results = search_reports(query=" ".join(sys.argv[2:]))
        print_results(results)
    elif sys.argv[1] == "low_score":
        threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.4
        results = search_reports(max_score=threshold)
        print(f"Reports with score <= {threshold}:")
        print_results(results)
    elif sys.argv[1] == "model" and len(sys.argv) > 2:
        results = search_reports(model_name=" ".join(sys.argv[2:]))
        print_results(results)
    else:
        print("Usage:")
        print("  python3 search_reports.py                    # Recent reports")
        print("  python3 search_reports.py query <text>       # Search by query text")
        print("  python3 search_reports.py low_score [0.4]    # Reports with low scores")
        print("  python3 search_reports.py model <name>       # Reports mentioning model")