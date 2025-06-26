#!/usr/bin/env python3
"""
ISEE Performance Analysis - Advanced queries and comparisons
"""

import sqlite3
import pandas as pd
from performance_tracker import PerformanceTracker

class PerformanceAnalyzer:
    def __init__(self, db_path: str = "data/performance_tracking.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
    
    def compare_collections(self):
        """Compare performance across collections"""
        query = '''
            SELECT 
                tr.collection_name,
                COUNT(DISTINCT tr.run_id) as test_runs,
                AVG(tr.avg_score) as avg_score,
                AVG(tr.avg_response_length) as avg_response_length,
                COUNT(DISTINCT mp.model_id) as unique_models,
                AVG(mp.avg_execution_time_seconds) as avg_model_speed,
                COUNT(pi.id) as total_issues,
                SUM(CASE WHEN pi.severity = 'high' THEN 1 ELSE 0 END) as high_severity_issues
            FROM test_runs tr
            LEFT JOIN model_performance mp ON tr.run_id = mp.run_id
            LEFT JOIN performance_issues pi ON tr.run_id = pi.run_id
            GROUP BY tr.collection_name
            ORDER BY avg_score DESC
        '''
        
        df = pd.read_sql_query(query, self.conn)
        print("🏆 Collection Performance Comparison:")
        print(df.to_string(index=False))
        return df
    
    def model_performance_ranking(self, collection_name: str = None):
        """Rank models by performance"""
        query = '''
            SELECT 
                mp.model_name,
                mp.model_provider,
                tr.collection_name,
                AVG(mp.avg_score) as avg_score,
                AVG(mp.avg_execution_time_seconds) as avg_speed,
                AVG(mp.avg_response_length) as avg_length,
                COUNT(pi.id) as issue_count
            FROM model_performance mp
            JOIN test_runs tr ON mp.run_id = tr.run_id
            LEFT JOIN performance_issues pi ON mp.run_id = pi.run_id AND mp.model_id = pi.model_id
        '''
        
        if collection_name:
            query += f" WHERE tr.collection_name = '{collection_name}'"
        
        query += '''
            GROUP BY mp.model_name, mp.model_provider, tr.collection_name
            ORDER BY avg_score DESC, avg_speed ASC
        '''
        
        df = pd.read_sql_query(query, self.conn)
        print(f"📊 Model Performance Ranking {f'({collection_name})' if collection_name else '(All Collections)'}:")
        print(df.to_string(index=False))
        return df
    
    def provider_analysis(self):
        """Analyze performance by provider"""
        query = '''
            SELECT 
                mp.model_provider,
                COUNT(DISTINCT mp.model_id) as model_count,
                AVG(mp.avg_score) as avg_score,
                AVG(mp.avg_execution_time_seconds) as avg_speed,
                COUNT(pi.id) as total_issues
            FROM model_performance mp
            LEFT JOIN performance_issues pi ON mp.run_id = pi.run_id AND mp.model_id = pi.model_id
            GROUP BY mp.model_provider
            ORDER BY avg_score DESC
        '''
        
        df = pd.read_sql_query(query, self.conn)
        print("🌍 Provider Performance Analysis:")
        print(df.to_string(index=False))
        return df
    
    def recommend_model_replacements(self, collection_name: str):
        """Recommend model replacements based on performance issues"""
        # Get models with high severity issues
        query = '''
            SELECT DISTINCT
                pi.model_id,
                mp.model_name,
                mp.model_provider,
                GROUP_CONCAT(pi.issue_type) as issues,
                AVG(mp.avg_score) as avg_score,
                AVG(mp.avg_execution_time_seconds) as avg_speed
            FROM performance_issues pi
            JOIN model_performance mp ON pi.run_id = mp.run_id AND pi.model_id = mp.model_id
            JOIN test_runs tr ON pi.run_id = tr.run_id
            WHERE tr.collection_name = ? AND pi.severity = 'high'
            GROUP BY pi.model_id, mp.model_name, mp.model_provider
        '''
        
        problem_models = pd.read_sql_query(query, self.conn, params=[collection_name])
        
        if len(problem_models) == 0:
            print(f"✅ No high-severity issues found in {collection_name} collection")
            return
        
        print(f"⚠️  Models with high-severity issues in {collection_name}:")
        for _, model in problem_models.iterrows():
            print(f"  🚨 {model['model_name']} ({model['model_provider']})")
            print(f"     Issues: {model['issues']}")
            print(f"     Performance: Score {model['avg_score']:.3f}, Speed {model['avg_speed']:.1f}s")
            print(f"     💡 Recommendation: Consider replacement")
            print()
    
    def cost_tier_analysis(self):
        """Analyze performance by cost tier (if available)"""
        # This would require cost tier data in model_performance table
        # For now, show a placeholder implementation
        print("💰 Cost Tier Analysis:")
        print("(Cost tier data integration needed)")
    
    def generate_optimization_report(self, collection_name: str):
        """Generate comprehensive optimization report for a collection"""
        print(f"\n{'='*60}")
        print(f"🎯 OPTIMIZATION REPORT: {collection_name}")
        print(f"{'='*60}")
        
        # Collection summary
        print("\n1. COLLECTION OVERVIEW:")
        self.compare_collections()
        
        print(f"\n2. MODEL PERFORMANCE IN {collection_name}:")
        self.model_performance_ranking(collection_name)
        
        print(f"\n3. REPLACEMENT RECOMMENDATIONS FOR {collection_name}:")
        self.recommend_model_replacements(collection_name)
        
        print("\n4. PROVIDER ANALYSIS:")
        self.provider_analysis()

def main():
    """Command line interface for performance analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ISEE Performance Analysis')
    parser.add_argument('--compare', action='store_true', help='Compare collections')
    parser.add_argument('--models', help='Show model ranking for collection')
    parser.add_argument('--providers', action='store_true', help='Analyze by provider')
    parser.add_argument('--recommend', help='Get replacement recommendations for collection')
    parser.add_argument('--report', help='Generate optimization report for collection')
    
    args = parser.parse_args()
    
    analyzer = PerformanceAnalyzer()
    
    if args.compare:
        analyzer.compare_collections()
    
    if args.models:
        analyzer.model_performance_ranking(args.models)
    
    if args.providers:
        analyzer.provider_analysis()
    
    if args.recommend:
        analyzer.recommend_model_replacements(args.recommend)
    
    if args.report:
        analyzer.generate_optimization_report(args.report)

if __name__ == "__main__":
    main()