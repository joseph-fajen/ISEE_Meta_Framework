#!/usr/bin/env python3
"""
ISEE Performance Tracker - SQLite Database for Collection Performance Analysis
Automatically ingests test results and tracks performance trends.
"""

import sqlite3
import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import hashlib

class PerformanceTracker:
    def __init__(self, db_path: str = "data/performance_tracking.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with performance tracking tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test runs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_runs (
                run_id TEXT PRIMARY KEY,
                timestamp DATETIME,
                collection_name TEXT,
                collection_id TEXT,
                query_text TEXT,
                query_hash TEXT,
                total_combinations INTEGER,
                executed_combinations INTEGER,
                total_execution_time_seconds INTEGER,
                avg_score REAL,
                max_score REAL,
                min_score REAL,
                avg_response_length REAL,
                frameworks_used TEXT,
                domains_used TEXT,
                notes TEXT
            )
        ''')
        
        # Model performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                model_id TEXT,
                model_name TEXT,
                model_provider TEXT,
                cost_tier TEXT,
                source_type TEXT,
                combination_count INTEGER,
                avg_score REAL,
                min_score REAL,
                max_score REAL,
                avg_response_length REAL,
                avg_execution_time_seconds REAL,
                success_rate REAL,
                total_response_chars INTEGER,
                FOREIGN KEY(run_id) REFERENCES test_runs(run_id)
            )
        ''')
        
        # Framework performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS framework_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                framework_id TEXT,
                framework_name TEXT,
                combination_count INTEGER,
                avg_score REAL,
                min_score REAL,
                max_score REAL,
                avg_response_length REAL,
                FOREIGN KEY(run_id) REFERENCES test_runs(run_id)
            )
        ''')
        
        # Performance issues table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                model_id TEXT,
                issue_type TEXT,
                issue_description TEXT,
                severity TEXT,
                detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(run_id) REFERENCES test_runs(run_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ Performance tracking database initialized at {self.db_path}")
    
    def generate_query_hash(self, query_text: str) -> str:
        """Generate consistent hash for query text"""
        return hashlib.md5(query_text.encode()).hexdigest()[:8]
    
    def parse_run_directory(self, run_dir: Path) -> Dict:
        """Parse a test run directory and extract all performance data"""
        run_data = {
            'run_id': run_dir.name,
            'run_path': str(run_dir),
            'files_found': []
        }
        
        # Parse run summary
        summary_file = run_dir / "run_summary.md"
        if summary_file.exists():
            run_data['files_found'].append('run_summary.md')
            with open(summary_file, 'r') as f:
                content = f.read()
                
            # Extract key metrics using regex
            run_data['timestamp'] = self._extract_timestamp(content)
            run_data['query_text'] = self._extract_query(content)
            run_data['total_combinations'] = self._extract_number(content, r'Total Combinations.*?(\d+)')
            run_data['executed_combinations'] = self._extract_number(content, r'Executed Combinations.*?(\d+)')
            run_data['avg_response_length'] = self._extract_number(content, r'Average Response Length.*?(\d+)')
            run_data['avg_score'] = self._extract_float(content, r'Average Score.*?([\d.]+)')
            run_data['max_score'] = self._extract_float(content, r'Max Score.*?([\d.]+)')
            run_data['min_score'] = self._extract_float(content, r'Min Score.*?([\d.]+)')
            run_data['models_used'] = self._extract_number(content, r'Models Used.*?(\d+)')
            run_data['instructions_used'] = self._extract_number(content, r'Instructions Used.*?(\d+)')
            run_data['domains_used'] = self._extract_number(content, r'Domains Used.*?(\d+)')
        
        # Parse model performance CSV
        model_perf_file = run_dir / "model_performance.csv"
        if model_perf_file.exists():
            run_data['files_found'].append('model_performance.csv')
            run_data['model_performance'] = pd.read_csv(model_perf_file)
        
        # Parse combinations CSV for framework analysis
        combinations_file = run_dir / "combinations.csv"
        if combinations_file.exists():
            run_data['files_found'].append('combinations.csv')
            run_data['combinations'] = pd.read_csv(combinations_file)
        
        return run_data
    
    def _extract_timestamp(self, content: str) -> datetime:
        """Extract timestamp from run summary"""
        match = re.search(r'Timestamp.*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', content)
        if match:
            return datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
        return datetime.now()
    
    def _extract_query(self, content: str) -> str:
        """Extract query text from run summary"""
        match = re.search(r'Query.*?"([^"]+)"', content, re.DOTALL)
        return match.group(1) if match else ""
    
    def _extract_number(self, content: str, pattern: str) -> int:
        """Extract integer from content using regex pattern"""
        match = re.search(pattern, content)
        return int(match.group(1)) if match else 0
    
    def _extract_float(self, content: str, pattern: str) -> float:
        """Extract float from content using regex pattern"""
        match = re.search(pattern, content)
        return float(match.group(1)) if match else 0.0
    
    def ingest_test_run(self, run_directory: str, collection_name: str = None) -> bool:
        """Ingest a test run directory into the performance database"""
        run_dir = Path(run_directory)
        if not run_dir.exists():
            print(f"❌ Run directory not found: {run_directory}")
            return False
        
        print(f"🔍 Processing test run: {run_dir.name}")
        run_data = self.parse_run_directory(run_dir)
        
        if not run_data.get('query_text'):
            print(f"⚠️  Could not extract query text from {run_dir.name}")
            return False
        
        # Determine collection info
        if not collection_name:
            collection_name = self._infer_collection_name(run_data)
        
        # Calculate execution time from run_id timestamp
        execution_time = self._calculate_execution_time(run_dir)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert test run record
            cursor.execute('''
                INSERT OR REPLACE INTO test_runs 
                (run_id, timestamp, collection_name, collection_id, query_text, query_hash,
                 total_combinations, executed_combinations, total_execution_time_seconds,
                 avg_score, max_score, min_score, avg_response_length, frameworks_used, domains_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                run_data['run_id'],
                run_data['timestamp'],
                collection_name,
                collection_name.lower().replace(' ', '_'),
                run_data['query_text'],
                self.generate_query_hash(run_data['query_text']),
                run_data.get('total_combinations', 0),
                run_data.get('executed_combinations', 0),
                execution_time,
                run_data.get('avg_score', 0.0),
                run_data.get('max_score', 0.0),
                run_data.get('min_score', 0.0),
                run_data.get('avg_response_length', 0.0),
                str(run_data.get('instructions_used', 0)),
                str(run_data.get('domains_used', 0))
            ))
            
            # Insert model performance records
            if 'model_performance' in run_data:
                df = run_data['model_performance']
                for _, row in df.iterrows():
                    cursor.execute('''
                        INSERT OR REPLACE INTO model_performance
                        (run_id, model_id, model_name, model_provider, combination_count,
                         avg_score, min_score, max_score, avg_response_length, avg_execution_time_seconds)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        run_data['run_id'],
                        row['model_id'],
                        row['model_name'],
                        row['model_provider'],
                        row['count'],
                        row['avg_score'],
                        row['min_score'],
                        row['max_score'],
                        row['avg_response_length'],
                        row['avg_execution_time']
                    ))
            
            # Detect and log performance issues
            self._detect_performance_issues(cursor, run_data)
            
            conn.commit()
            print(f"✅ Successfully ingested test run {run_data['run_id']}")
            return True
            
        except Exception as e:
            print(f"❌ Error ingesting test run: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def _infer_collection_name(self, run_data: Dict) -> str:
        """Infer collection name from run data"""
        # Logic to determine collection based on models, timing, etc.
        if 'model_performance' in run_data:
            model_names = run_data['model_performance']['model_name'].tolist()
            if 'grok-3' in str(model_names).lower():
                return "Premium Diversity"
            elif 'grok-3-mini' in str(model_names).lower():
                return "Reliable Exploration"
        return "Unknown Collection"
    
    def _calculate_execution_time(self, run_dir: Path) -> int:
        """Calculate execution time from directory timestamps"""
        # Parse timestamp from directory name: run_20250626_121159
        dir_pattern = r'run_(\d{8})_(\d{6})'
        match = re.search(dir_pattern, run_dir.name)
        if match:
            # For now, return 0 - we'll need log analysis for actual time
            return 0
        return 0
    
    def _detect_performance_issues(self, cursor, run_data: Dict):
        """Detect and log performance issues"""
        if 'model_performance' not in run_data:
            return
        
        df = run_data['model_performance']
        run_id = run_data['run_id']
        
        for _, row in df.iterrows():
            issues = []
            
            # Detect poor performance
            if row['avg_score'] < 0.3:
                issues.append(('poor_quality', f"Low average score: {row['avg_score']:.3f}", 'high'))
            
            # Detect slow performance
            if row['avg_execution_time'] > 60:
                issues.append(('slow_execution', f"Slow execution: {row['avg_execution_time']:.1f}s", 'medium'))
            
            # Detect empty responses
            if row['avg_response_length'] < 100:
                issues.append(('short_responses', f"Very short responses: {row['avg_response_length']:.0f} chars", 'high'))
            
            # Log issues
            for issue_type, description, severity in issues:
                cursor.execute('''
                    INSERT INTO performance_issues 
                    (run_id, model_id, issue_type, issue_description, severity)
                    VALUES (?, ?, ?, ?, ?)
                ''', (run_id, row['model_id'], issue_type, description, severity))
    
    def get_collection_performance_summary(self, collection_name: str = None) -> pd.DataFrame:
        """Get performance summary for collections"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT collection_name, COUNT(*) as test_count,
                   AVG(avg_score) as avg_score,
                   AVG(total_execution_time_seconds) as avg_execution_time,
                   AVG(avg_response_length) as avg_response_length,
                   MAX(timestamp) as last_test
            FROM test_runs
        '''
        
        if collection_name:
            query += f" WHERE collection_name = '{collection_name}'"
        
        query += " GROUP BY collection_name ORDER BY last_test DESC"
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_model_trends(self, model_id: str = None, days: int = 30) -> pd.DataFrame:
        """Get model performance trends"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT mp.model_id, mp.model_name, mp.model_provider,
                   tr.collection_name, tr.timestamp,
                   mp.avg_score, mp.avg_execution_time_seconds, mp.avg_response_length
            FROM model_performance mp
            JOIN test_runs tr ON mp.run_id = tr.run_id
            WHERE tr.timestamp >= datetime('now', '-{} days')
        '''.format(days)
        
        if model_id:
            query += f" AND mp.model_id = '{model_id}'"
        
        query += " ORDER BY tr.timestamp DESC"
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_performance_issues(self, severity: str = None) -> pd.DataFrame:
        """Get performance issues summary"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT pi.run_id, tr.collection_name, tr.timestamp,
                   pi.model_id, mp.model_name,
                   pi.issue_type, pi.issue_description, pi.severity
            FROM performance_issues pi
            JOIN test_runs tr ON pi.run_id = tr.run_id
            LEFT JOIN model_performance mp ON pi.run_id = mp.run_id AND pi.model_id = mp.model_id
        '''
        
        if severity:
            query += f" WHERE pi.severity = '{severity}'"
        
        query += " ORDER BY pi.detected_at DESC"
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

def main():
    """Command line interface for performance tracker"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ISEE Performance Tracker')
    parser.add_argument('--ingest', help='Ingest test run directory')
    parser.add_argument('--collection', help='Collection name for ingestion')
    parser.add_argument('--summary', action='store_true', help='Show collection performance summary')
    parser.add_argument('--trends', help='Show trends for specific model')
    parser.add_argument('--issues', action='store_true', help='Show performance issues')
    
    args = parser.parse_args()
    
    tracker = PerformanceTracker()
    
    if args.ingest:
        success = tracker.ingest_test_run(args.ingest, args.collection)
        if success:
            print(f"✅ Successfully ingested {args.ingest}")
        else:
            print(f"❌ Failed to ingest {args.ingest}")
    
    if args.summary:
        df = tracker.get_collection_performance_summary()
        print("\n📊 Collection Performance Summary:")
        print(df.to_string(index=False))
    
    if args.trends:
        df = tracker.get_model_trends(args.trends)
        print(f"\n📈 Performance Trends for {args.trends}:")
        print(df.to_string(index=False))
    
    if args.issues:
        df = tracker.get_performance_issues()
        print("\n⚠️  Performance Issues:")
        print(df.to_string(index=False))

if __name__ == "__main__":
    main()