"""
Enhancement Tracking System for ISEE Framework

Tracks the effectiveness of query enhancements and validates that enhanced queries
actually produce higher quality scores as predicted.
"""

import sqlite3
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class EnhancementTracking:
    """Tracks enhancement usage and effectiveness"""
    enhancement_id: str
    original_query: str
    enhanced_query: str
    enhancement_type: str
    predicted_improvement: str
    confidence_score: float
    
    # Results tracking
    original_avg_score: Optional[float] = None
    enhanced_avg_score: Optional[float] = None
    actual_improvement: Optional[float] = None
    improvement_percentage: Optional[float] = None
    
    # Metadata
    timestamp: datetime = None
    user_selected: bool = False
    run_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class EnhancementTracker:
    """Tracks query enhancement effectiveness and validation"""
    
    def __init__(self, db_path: str = "data/enhancement_tracking.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Initialize the tracking database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create enhancement sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enhancement_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    enhancement_id TEXT UNIQUE NOT NULL,
                    original_query TEXT NOT NULL,
                    enhanced_query TEXT NOT NULL,
                    enhancement_type TEXT NOT NULL,
                    predicted_improvement TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    user_selected BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create enhancement results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enhancement_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    enhancement_id TEXT NOT NULL,
                    run_id TEXT,
                    original_avg_score REAL,
                    enhanced_avg_score REAL,
                    actual_improvement REAL,
                    improvement_percentage REAL,
                    execution_time_seconds REAL,
                    total_combinations INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (enhancement_id) REFERENCES enhancement_sessions (enhancement_id)
                )
            """)
            
            # Create enhancement analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enhancement_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    enhancement_type TEXT NOT NULL,
                    total_enhancements INTEGER DEFAULT 0,
                    total_selected INTEGER DEFAULT 0,
                    avg_confidence_score REAL DEFAULT 0,
                    avg_actual_improvement REAL DEFAULT 0,
                    success_rate REAL DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create validation metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS validation_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_type TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    comparison_baseline REAL,
                    validation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            """)
            
            conn.commit()
    
    def track_enhancement_generation(self, enhancement_result) -> List[str]:
        """
        Track when enhancements are generated for a query
        
        Args:
            enhancement_result: EnhancementResult from query_enhancement.py
            
        Returns:
            List of enhancement IDs created
        """
        enhancement_ids = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for enhancement in enhancement_result.enhanced_versions:
                enhancement_id = f"enh_{int(time.time() * 1000)}_{enhancement.type.value.lower().replace('-', '_')}"
                
                cursor.execute("""
                    INSERT OR REPLACE INTO enhancement_sessions 
                    (enhancement_id, original_query, enhanced_query, enhancement_type, 
                     predicted_improvement, confidence_score, user_selected)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    enhancement_id,
                    enhancement_result.original,
                    enhancement.query,
                    enhancement.type.value,
                    enhancement.expected_quality_improvement,
                    enhancement.confidence_score,
                    False  # Will be updated when user selects
                ))
                
                enhancement_ids.append(enhancement_id)
            
            conn.commit()
        
        logger.info(f"Tracked {len(enhancement_ids)} enhancements generated")
        return enhancement_ids
    
    def track_enhancement_selection(self, enhancement_id: str, selected: bool = True):
        """Track when a user selects an enhancement"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE enhancement_sessions 
                SET user_selected = ? 
                WHERE enhancement_id = ?
            """, (selected, enhancement_id))
            
            conn.commit()
        
        logger.info(f"Tracked enhancement selection: {enhancement_id} -> {selected}")
    
    def track_enhancement_results(self, 
                                enhancement_id: str,
                                run_id: str,
                                original_avg_score: float,
                                enhanced_avg_score: float,
                                execution_time_seconds: float,
                                total_combinations: int):
        """
        Track the actual results of using an enhanced query
        
        Args:
            enhancement_id: ID of the enhancement used
            run_id: ISEE run ID
            original_avg_score: Average score that would have been achieved with original query
            enhanced_avg_score: Actual average score achieved with enhanced query
            execution_time_seconds: Time taken for execution
            total_combinations: Number of combinations executed
        """
        actual_improvement = enhanced_avg_score - original_avg_score
        improvement_percentage = (actual_improvement / original_avg_score) * 100 if original_avg_score > 0 else 0
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO enhancement_results 
                (enhancement_id, run_id, original_avg_score, enhanced_avg_score, 
                 actual_improvement, improvement_percentage, execution_time_seconds, total_combinations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                enhancement_id, run_id, original_avg_score, enhanced_avg_score,
                actual_improvement, improvement_percentage, execution_time_seconds, total_combinations
            ))
            
            conn.commit()
        
        logger.info(f"Tracked enhancement results: {enhancement_id} -> {improvement_percentage:.1f}% improvement")
        
        # Update analytics
        self._update_analytics()
    
    def _update_analytics(self):
        """Update aggregated analytics for enhancement types"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get analytics by enhancement type
            cursor.execute("""
                SELECT 
                    es.enhancement_type,
                    COUNT(*) as total_enhancements,
                    SUM(CASE WHEN es.user_selected THEN 1 ELSE 0 END) as total_selected,
                    AVG(es.confidence_score) as avg_confidence,
                    AVG(er.actual_improvement) as avg_improvement,
                    AVG(CASE WHEN er.actual_improvement > 0 THEN 1.0 ELSE 0.0 END) as success_rate
                FROM enhancement_sessions es
                LEFT JOIN enhancement_results er ON es.enhancement_id = er.enhancement_id
                GROUP BY es.enhancement_type
            """)
            
            analytics_data = cursor.fetchall()
            
            # Update analytics table
            cursor.execute("DELETE FROM enhancement_analytics")
            
            for row in analytics_data:
                cursor.execute("""
                    INSERT INTO enhancement_analytics 
                    (enhancement_type, total_enhancements, total_selected, 
                     avg_confidence_score, avg_actual_improvement, success_rate)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, row)
            
            conn.commit()
    
    def get_enhancement_effectiveness(self, enhancement_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get effectiveness metrics for enhancements
        
        Args:
            enhancement_type: Specific enhancement type to analyze, or None for all
            
        Returns:
            Dictionary with effectiveness metrics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            where_clause = ""
            params = []
            
            if enhancement_type:
                where_clause = "WHERE es.enhancement_type = ?"
                params = [enhancement_type]
            
            cursor.execute(f"""
                SELECT 
                    es.enhancement_type,
                    COUNT(*) as total_generated,
                    SUM(CASE WHEN es.user_selected THEN 1 ELSE 0 END) as total_selected,
                    AVG(es.confidence_score) as avg_confidence,
                    AVG(er.actual_improvement) as avg_improvement,
                    AVG(er.improvement_percentage) as avg_improvement_pct,
                    COUNT(er.id) as total_executed,
                    SUM(CASE WHEN er.actual_improvement > 0 THEN 1 ELSE 0 END) as successful_improvements
                FROM enhancement_sessions es
                LEFT JOIN enhancement_results er ON es.enhancement_id = er.enhancement_id
                {where_clause}
                GROUP BY es.enhancement_type
            """, params)
            
            results = {}
            for row in cursor.fetchall():
                enhancement_type = row[0]
                results[enhancement_type] = {
                    "total_generated": row[1],
                    "total_selected": row[2],
                    "selection_rate": row[2] / row[1] if row[1] > 0 else 0,
                    "avg_confidence": row[3] or 0,
                    "avg_improvement": row[4] or 0,
                    "avg_improvement_percentage": row[5] or 0,
                    "total_executed": row[6],
                    "successful_improvements": row[7] or 0,
                    "success_rate": (row[7] or 0) / row[6] if row[6] > 0 else 0
                }
            
            return results
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        effectiveness = self.get_enhancement_effectiveness()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Overall statistics
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT es.enhancement_id) as total_enhancements,
                    COUNT(DISTINCT CASE WHEN es.user_selected THEN es.enhancement_id END) as total_used,
                    AVG(er.improvement_percentage) as overall_avg_improvement,
                    MIN(er.improvement_percentage) as min_improvement,
                    MAX(er.improvement_percentage) as max_improvement,
                    COUNT(DISTINCT er.run_id) as total_runs_tracked
                FROM enhancement_sessions es
                LEFT JOIN enhancement_results er ON es.enhancement_id = er.enhancement_id
            """)
            
            overall_stats = cursor.fetchone()
            
            # Recent trends (last 30 days)
            cursor.execute("""
                SELECT 
                    COUNT(*) as recent_enhancements,
                    AVG(er.improvement_percentage) as recent_avg_improvement
                FROM enhancement_sessions es
                LEFT JOIN enhancement_results er ON es.enhancement_id = er.enhancement_id
                WHERE es.created_at >= datetime('now', '-30 days')
            """)
            
            recent_stats = cursor.fetchone()
            
            return {
                "overall_statistics": {
                    "total_enhancements_generated": overall_stats[0] or 0,
                    "total_enhancements_used": overall_stats[1] or 0,
                    "usage_rate": (overall_stats[1] or 0) / (overall_stats[0] or 1),
                    "overall_avg_improvement_pct": overall_stats[2] or 0,
                    "min_improvement_pct": overall_stats[3] or 0,
                    "max_improvement_pct": overall_stats[4] or 0,
                    "total_runs_tracked": overall_stats[5] or 0
                },
                "recent_trends": {
                    "recent_enhancements": recent_stats[0] or 0,
                    "recent_avg_improvement_pct": recent_stats[1] or 0
                },
                "by_enhancement_type": effectiveness,
                "validation_status": self._get_validation_status(effectiveness)
            }
    
    def _get_validation_status(self, effectiveness: Dict[str, Any]) -> Dict[str, str]:
        """Determine validation status for each enhancement type"""
        status = {}
        
        for enhancement_type, metrics in effectiveness.items():
            avg_improvement = metrics.get("avg_improvement_percentage", 0)
            success_rate = metrics.get("success_rate", 0)
            total_executed = metrics.get("total_executed", 0)
            
            if total_executed < 3:
                status[enhancement_type] = "INSUFFICIENT_DATA"
            elif avg_improvement >= 15 and success_rate >= 0.7:
                status[enhancement_type] = "VALIDATED"
            elif avg_improvement >= 10 and success_rate >= 0.6:
                status[enhancement_type] = "PROMISING"
            elif avg_improvement >= 5:
                status[enhancement_type] = "MARGINAL"
            else:
                status[enhancement_type] = "UNDERPERFORMING"
        
        return status

# Global tracker instance
_enhancement_tracker = None

def get_enhancement_tracker() -> EnhancementTracker:
    """Get global enhancement tracker instance"""
    global _enhancement_tracker
    if _enhancement_tracker is None:
        _enhancement_tracker = EnhancementTracker()
    return _enhancement_tracker

def track_enhancement_usage(original_query: str, enhanced_query: str, enhancement_type: str) -> str:
    """Simple interface for tracking enhancement usage"""
    tracker = get_enhancement_tracker()
    
    # Create a mock enhancement result for tracking
    from query_enhancement import EnhancementType, QueryEnhancement, EnhancementResult
    
    enhancement = QueryEnhancement(
        type=EnhancementType(enhancement_type),
        query=enhanced_query,
        rationale=f"User selected {enhancement_type} enhancement",
        expected_quality_improvement="15-25% higher scoring",
        confidence_score=0.85
    )
    
    result = EnhancementResult(
        original=original_query,
        enhanced_versions=[enhancement],
        enhancement_analysis="User-selected enhancement",
        processing_time_ms=0.0
    )
    
    enhancement_ids = tracker.track_enhancement_generation(result)
    if enhancement_ids:
        tracker.track_enhancement_selection(enhancement_ids[0], True)
        return enhancement_ids[0]
    
    return ""

# Export key functions
__all__ = [
    'EnhancementTracking',
    'EnhancementTracker',
    'get_enhancement_tracker',
    'track_enhancement_usage'
]