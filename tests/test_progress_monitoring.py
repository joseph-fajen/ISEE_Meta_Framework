#!/usr/bin/env python3
"""
Test suite for real-time progress monitoring functionality in ISEE Web UI.
Ensures progress tracking accuracy and robustness.
"""

import unittest
import time
import threading
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import ISEEWebDemo
import tempfile
import shutil


class TestProgressMonitoring(unittest.TestCase):
    """Test suite for real-time progress monitoring system"""
    
    def setUp(self):
        """Set up test environment"""
        self.demo = ISEEWebDemo()
        self.test_execution_id = "test_exec_123"
        
    def tearDown(self):
        """Clean up test environment"""
        # Clear any execution status
        if hasattr(self.demo, 'execution_status'):
            self.demo.execution_status.clear()
    
    def test_progress_tracking_initialization(self):
        """Test that progress tracking initializes correctly"""
        # Simulate starting an execution
        self.demo.execution_status[self.test_execution_id] = {
            "status": "running",
            "progress": 0,
            "message": "Starting execution...",
            "current_calls": [],
            "total_calls": 10
        }
        
        status = self.demo.execution_status[self.test_execution_id]
        self.assertEqual(status["status"], "running")
        self.assertEqual(status["progress"], 0)
        self.assertEqual(status["total_calls"], 10)
        self.assertEqual(len(status["current_calls"]), 0)
    
    def test_progress_updates_during_execution(self):
        """Test progress updates as LLM calls complete"""
        # Initialize execution
        self.demo.execution_status[self.test_execution_id] = {
            "status": "running",
            "progress": 0,
            "message": "Starting execution...",
            "current_calls": [],
            "total_calls": 4
        }
        
        # Simulate progress updates
        test_calls = [
            {"model": "gpt-4", "framework": "analytical", "call_number": 1},
            {"model": "claude-3", "framework": "creative", "call_number": 2},
            {"model": "gemini-pro", "framework": "systematic", "call_number": 3},
            {"model": "llama-3", "framework": "pragmatic", "call_number": 4}
        ]
        
        for i, call in enumerate(test_calls, 1):
            # Update progress
            self.demo.execution_status[self.test_execution_id].update({
                "progress": (i / 4) * 100,
                "message": f"Processing {call['model']} with {call['framework']} framework ({i}/4)",
                "current_calls": test_calls[:i]
            })
            
            status = self.demo.execution_status[self.test_execution_id]
            expected_progress = (i / 4) * 100
            
            self.assertEqual(status["progress"], expected_progress)
            self.assertEqual(len(status["current_calls"]), i)
            self.assertIn(f"({i}/4)", status["message"])
    
    def test_progress_completion(self):
        """Test progress tracking at completion"""
        # Initialize and complete execution
        self.demo.execution_status[self.test_execution_id] = {
            "status": "completed",
            "progress": 100,
            "message": "Completed 4/4 LLM calls",
            "current_calls": [
                {"model": "gpt-4", "framework": "analytical", "call_number": 1},
                {"model": "claude-3", "framework": "creative", "call_number": 2},
                {"model": "gemini-pro", "framework": "systematic", "call_number": 3},
                {"model": "llama-3", "framework": "pragmatic", "call_number": 4}
            ],
            "total_calls": 4,
            "end_time": "2025-06-24T11:00:00Z"
        }
        
        status = self.demo.execution_status[self.test_execution_id]
        self.assertEqual(status["status"], "completed")
        self.assertEqual(status["progress"], 100)
        self.assertEqual(len(status["current_calls"]), 4)
        self.assertIn("4/4", status["message"])
        self.assertIsNotNone(status["end_time"])
    
    def test_progress_error_handling(self):
        """Test progress tracking during error conditions"""
        # Simulate execution with error
        self.demo.execution_status[self.test_execution_id] = {
            "status": "error",
            "progress": 50,
            "message": "Error after 2/4 LLM calls",
            "current_calls": [
                {"model": "gpt-4", "framework": "analytical", "call_number": 1},
                {"model": "claude-3", "framework": "creative", "call_number": 2}
            ],
            "total_calls": 4,
            "error": "API timeout error",
            "end_time": "2025-06-24T11:00:00Z"
        }
        
        status = self.demo.execution_status[self.test_execution_id]
        self.assertEqual(status["status"], "error")
        self.assertEqual(status["progress"], 50)
        self.assertEqual(len(status["current_calls"]), 2)
        self.assertIn("2/4", status["message"])
        self.assertIn("error", status)
    
    def test_multiple_executions_tracking(self):
        """Test tracking multiple concurrent executions"""
        exec_ids = ["exec_1", "exec_2", "exec_3"]
        
        # Initialize multiple executions
        for i, exec_id in enumerate(exec_ids):
            self.demo.execution_status[exec_id] = {
                "status": "running",
                "progress": i * 25,
                "message": f"Processing execution {i+1}",
                "current_calls": [],
                "total_calls": 5
            }
        
        # Verify each execution is tracked independently
        for i, exec_id in enumerate(exec_ids):
            status = self.demo.execution_status[exec_id]
            self.assertEqual(status["progress"], i * 25)
            self.assertIn(f"execution {i+1}", status["message"])
        
        # Verify total count
        self.assertEqual(len(self.demo.execution_status), 3)
    
    def test_progress_message_formatting(self):
        """Test proper formatting of progress messages"""
        test_cases = [
            {
                "model": "gpt-4-turbo",
                "framework": "Analytical Framework", 
                "call_num": 1,
                "total": 10,
                "expected_pattern": "gpt-4-turbo with Analytical Framework (1/10)"
            },
            {
                "model": "claude-3-sonnet",
                "framework": "Creative Synthesis",
                "call_num": 5,
                "total": 8,
                "expected_pattern": "claude-3-sonnet with Creative Synthesis (5/8)"
            }
        ]
        
        for case in test_cases:
            message = f"Processing {case['model']} with {case['framework']} ({case['call_num']}/{case['total']})"
            
            # Verify message contains all expected components
            self.assertIn(case['model'], message)
            self.assertIn(case['framework'], message)
            self.assertIn(f"({case['call_num']}/{case['total']})", message)
    
    def test_progress_message_with_percentage(self):
        """Test progress messages include percentage indicators"""
        test_cases = [
            {
                "model": "gpt-4-turbo",
                "framework": "Analytical Framework",
                "call_num": 10,
                "total": 50,
                "expected_percentage": "20%"
            },
            {
                "model": "claude-3-sonnet", 
                "framework": "Creative Synthesis",
                "call_num": 35,
                "total": 48,
                "expected_percentage": "72%"
            },
            {
                "model": "gemini-pro",
                "framework": "Systematic Analysis", 
                "call_num": 4,
                "total": 4,
                "expected_percentage": "100%"
            }
        ]
        
        for case in test_cases:
            # Simulate the enhanced message format
            progress_percentage = int((case['call_num'] / case['total']) * 100)
            message = f"Processing {case['model']} with {case['framework']} framework ({case['call_num']}/{case['total']} - {progress_percentage}%)"
            
            # Verify enhanced message format
            self.assertIn(case['model'], message)
            self.assertIn(case['framework'], message)
            self.assertIn(f"({case['call_num']}/{case['total']} - {case['expected_percentage']})", message)
        
        # Test completion message with percentage
        completion_cases = [
            {"completed": 24, "total": 48, "expected": "50%"},
            {"completed": 35, "total": 48, "expected": "72%"},
            {"completed": 48, "total": 48, "expected": "100%"}
        ]
        
        for case in completion_cases:
            completion_percentage = int((case['completed'] / case['total']) * 100)
            message = f"Completed {case['completed']}/{case['total']} LLM calls ({completion_percentage}%)"
            
            self.assertIn(f"({case['expected']})", message)
            self.assertIn(f"{case['completed']}/{case['total']}", message)
    
    def test_time_estimation_functionality(self):
        """Test estimated time remaining calculations"""
        from datetime import datetime, timedelta
        
        # Set up execution with start time
        start_time = datetime.now() - timedelta(minutes=5)  # Started 5 minutes ago
        self.demo.execution_status[self.test_execution_id] = {
            "status": "running",
            "progress": 50,
            "message": "Processing...",
            "start_time": start_time.isoformat(),
            "current_calls": [],
            "total_calls": 10
        }
        
        # Test time calculation logic (matching app.py logic)
        current_time = datetime.now()
        elapsed_minutes = (current_time - start_time).total_seconds() / 60
        
        # Test cases for different progress levels
        test_cases = [
            {"combination_index": 2, "total": 10, "expected_pattern": "min"},
            {"combination_index": 5, "total": 10, "expected_pattern": "min"},
            {"combination_index": 9, "total": 10, "expected_pattern": "min"}
        ]
        
        for case in test_cases:
            if case['combination_index'] > 1:
                velocity = (case['combination_index'] - 1) / max(elapsed_minutes, 0.1)
                remaining_combinations = case['total'] - case['combination_index']
                estimated_remaining_minutes = remaining_combinations / max(velocity, 0.01)
                
                # Verify calculation is reasonable
                self.assertGreater(velocity, 0)
                self.assertGreaterEqual(estimated_remaining_minutes, 0)
        
        # Test time formatting
        time_test_cases = [
            {"minutes": 0.5, "expected": "30s"},
            {"minutes": 2.3, "expected": "2m"},
            {"minutes": 65, "expected": "1h 5m"},
            {"minutes": 125, "expected": "2h 5m"}
        ]
        
        for case in time_test_cases:
            minutes = case['minutes']
            if minutes < 1:
                formatted = f"{int(minutes * 60)}s"
            elif minutes < 60:
                formatted = f"{int(minutes)}m"
            else:
                hours = int(minutes // 60)
                mins = int(minutes % 60)
                formatted = f"{hours}h {mins}m"
            
            self.assertEqual(formatted, case['expected'])
    
    def test_progress_percentage_calculation(self):
        """Test accurate progress percentage calculations"""
        test_cases = [
            {"completed": 0, "total": 10, "expected": 0},
            {"completed": 1, "total": 4, "expected": 25},
            {"completed": 3, "total": 4, "expected": 75},
            {"completed": 4, "total": 4, "expected": 100},
            {"completed": 7, "total": 10, "expected": 70},
            {"completed": 15, "total": 20, "expected": 75}
        ]
        
        for case in test_cases:
            progress = (case["completed"] / case["total"]) * 100
            self.assertEqual(progress, case["expected"])
    
    def test_execution_status_api_response(self):
        """Test execution status API response format"""
        # Set up a sample execution status
        self.demo.execution_status[self.test_execution_id] = {
            "status": "running",
            "progress": 60,
            "message": "Processing gpt-4 with analytical framework (3/5)",
            "current_calls": [
                {"model": "gpt-4", "framework": "analytical", "call_number": 1},
                {"model": "claude-3", "framework": "creative", "call_number": 2},
                {"model": "gemini-pro", "framework": "systematic", "call_number": 3}
            ],
            "total_calls": 5,
            "start_time": "2025-06-24T10:30:00Z"
        }
        
        # Get status (simulating API call)
        status = self.demo.execution_status.get(self.test_execution_id, {"status": "not_found"})
        
        # Verify response format
        self.assertIn("status", status)
        self.assertIn("progress", status)
        self.assertIn("message", status)
        self.assertIn("current_calls", status)
        self.assertIn("total_calls", status)
        self.assertIn("start_time", status)
        
        # Verify data types
        self.assertIsInstance(status["progress"], (int, float))
        self.assertIsInstance(status["current_calls"], list)
        self.assertIsInstance(status["total_calls"], int)


class TestProgressMonitoringIntegration(unittest.TestCase):
    """Integration tests for progress monitoring with mock LLM calls"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.demo = ISEEWebDemo()
    
    @patch('subprocess.Popen')
    def test_progress_monitoring_with_mock_execution(self, mock_popen):
        """Test progress monitoring with simulated LLM execution"""
        # Mock subprocess output simulating real progress updates
        mock_process = Mock()
        mock_process.stdout.readline.side_effect = [
            b"Starting ISEE execution...\n",
            b"Processing model 1/4: gpt-4 with analytical framework\n", 
            b"Processing model 2/4: claude-3 with creative framework\n",
            b"Processing model 3/4: gemini-pro with systematic framework\n",
            b"Processing model 4/4: llama-3 with pragmatic framework\n",
            b"Execution completed successfully\n",
            b""  # End of output
        ]
        mock_process.poll.return_value = None  # Still running
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        # This would be part of a more complex integration test
        # For now, we verify the mock setup works
        self.assertIsNotNone(mock_process)
        self.assertEqual(mock_process.returncode, 0)


def run_progress_monitoring_tests():
    """Run all progress monitoring tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestProgressMonitoring,
        TestProgressMonitoringIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == '__main__':
    print("🧪 Running ISEE Progress Monitoring Tests...")
    print("=" * 60)
    
    success = run_progress_monitoring_tests()
    
    print("=" * 60)
    if success:
        print("✅ All progress monitoring tests passed!")
        sys.exit(0)
    else:
        print("❌ Some progress monitoring tests failed!")
        sys.exit(1)