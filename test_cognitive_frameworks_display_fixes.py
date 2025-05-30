#!/usr/bin/env python3
"""
Test Cognitive Frameworks Display Fixes

Tests the fixes for:
1. Adding number column (1-10) to cognitive frameworks table
2. Ensuring proper spacing between Integrative and Pragmatic frameworks
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch
from io import StringIO

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from cognitive_framework_visualizer import CognitiveFrameworkVisualizer
    from rich.console import Console
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

class TestCognitiveFrameworksDisplayFixes(unittest.TestCase):
    """Test cases for cognitive frameworks display fixes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.console = Console(file=StringIO(), width=120)
        self.visualizer = CognitiveFrameworkVisualizer(self.console)
    
    def test_frameworks_overview_has_number_column(self):
        """Test that the frameworks overview table includes a number column."""
        # Capture output
        output_buffer = StringIO()
        test_console = Console(file=output_buffer, width=120)
        test_visualizer = CognitiveFrameworkVisualizer(test_console)
        
        # Display the frameworks overview
        test_visualizer.display_frameworks_overview()
        
        # Get the output
        output = output_buffer.getvalue()
        
        # Check that the table includes a number column header
        self.assertIn("#", output)
        
        # Check that numbers 1-10 appear in the output (for the 10 frameworks)
        for i in range(1, 11):
            self.assertIn(str(i), output)
    
    def test_integrative_and_pragmatic_are_separate(self):
        """Test that Integrative and Pragmatic frameworks appear as separate items."""
        # Get all frameworks
        frameworks = self.visualizer.template_library.list_templates()
        
        # Find Integrative and Pragmatic frameworks
        integrative_found = False
        pragmatic_found = False
        
        for framework in frameworks:
            if "integrative" in framework.id.lower():
                integrative_found = True
            if "pragmatic" in framework.id.lower():
                pragmatic_found = True
        
        # Both should be found as separate frameworks
        self.assertTrue(integrative_found, "Integrative framework should be found")
        self.assertTrue(pragmatic_found, "Pragmatic framework should be found")
        
        # They should have different IDs
        integrative = self.visualizer.template_library.get_template("ins_integrative")
        pragmatic = self.visualizer.template_library.get_template("ins_pragmatic")
        
        self.assertNotEqual(integrative.id, pragmatic.id)
        self.assertNotEqual(integrative.name, pragmatic.name)
    
    def test_frameworks_have_unique_icons(self):
        """Test that Integrative and Pragmatic have different icons."""
        integrative_icon = self.visualizer.framework_icons.get("ins_integrative")
        pragmatic_icon = self.visualizer.framework_icons.get("ins_pragmatic")
        
        self.assertIsNotNone(integrative_icon)
        self.assertIsNotNone(pragmatic_icon)
        self.assertNotEqual(integrative_icon, pragmatic_icon)
        
        # Verify the specific icons
        self.assertEqual(integrative_icon, "🔗")
        self.assertEqual(pragmatic_icon, "🔧")
    
    def test_framework_numbering_consistency(self):
        """Test that framework numbering is consistent and sequential."""
        # Capture output for all frameworks
        output_buffer = StringIO()
        test_console = Console(file=output_buffer, width=120)
        test_visualizer = CognitiveFrameworkVisualizer(test_console)
        
        # Display frameworks overview
        test_visualizer.display_frameworks_overview()
        
        # Get the output
        output = output_buffer.getvalue()
        
        # Count frameworks in the library
        frameworks_count = len(test_visualizer.template_library.list_templates())
        
        # Check that we have numbers 1 through frameworks_count
        for i in range(1, frameworks_count + 1):
            self.assertIn(f" {i} ", output, f"Number {i} should appear in the table")
    
    def test_complexity_level_filtering_includes_numbers(self):
        """Test that complexity level filtering still includes numbers."""
        # Test basic level
        output_buffer = StringIO()
        test_console = Console(file=output_buffer, width=120)
        test_visualizer = CognitiveFrameworkVisualizer(test_console)
        
        test_visualizer.display_frameworks_overview(complexity_level="basic")
        output = output_buffer.getvalue()
        
        # Should have numbers for basic frameworks
        self.assertIn("#", output)  # Header should be there
        
        # Basic level should have at least 1, 2, 3 (for the basic frameworks)
        basic_frameworks = test_visualizer.complexity_levels.get("basic", [])
        for i in range(1, len(basic_frameworks) + 1):
            self.assertIn(str(i), output)
    
    def test_table_structure_with_number_column(self):
        """Test that the table structure includes the number column correctly."""
        # Check that the number column is added correctly
        output_buffer = StringIO()
        test_console = Console(file=output_buffer, width=120)
        test_visualizer = CognitiveFrameworkVisualizer(test_console)
        
        test_visualizer.display_frameworks_overview()
        output = output_buffer.getvalue()
        
        # Check for the expected columns in order
        self.assertIn("#", output)
        self.assertIn("Framework", output)
        self.assertIn("Cognitive Style", output)
        self.assertIn("Strength", output)
        self.assertIn("Best For", output)
    
    def test_visual_demo_output(self):
        """Demo test to visually inspect the output."""
        print("\n" + "="*80)
        print("VISUAL DEMO: Enhanced Cognitive Frameworks Table")
        print("="*80)
        
        # Create a real console for visual output
        demo_console = Console()
        demo_visualizer = CognitiveFrameworkVisualizer(demo_console)
        
        print("\n1. All Frameworks with Numbers:")
        demo_visualizer.display_frameworks_overview()
        
        print("\n2. Basic Level Frameworks:")
        demo_visualizer.display_frameworks_overview(complexity_level="basic")
        
        print("\n3. Advanced Level Frameworks:")
        demo_visualizer.display_frameworks_overview(complexity_level="advanced")
        
        print("\n" + "="*80)
        print("END VISUAL DEMO")
        print("="*80)

if __name__ == "__main__":
    print("Running Cognitive Frameworks Display Fixes Tests...")
    unittest.main(verbosity=2)