#!/usr/bin/env python3
"""
Comprehensive test suite for Cognitive Framework Visualizer

Tests the visualization functionality for Step 3.1: Cognitive Frameworks Visualization
Part of UX Enhancement Roadmap implementation.
"""

import sys
import io
from contextlib import redirect_stdout
from rich.console import Console
from cognitive_framework_visualizer import CognitiveFrameworkVisualizer, create_framework_visualizer
from instruction_templates import create_default_library

class TestCognitiveFrameworkVisualizer:
    """Test suite for cognitive framework visualization functionality."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.console = Console(file=io.StringIO(), width=80)
        self.visualizer = create_framework_visualizer(self.console)
        self.template_library = create_default_library()
        self.tests_passed = 0
        self.tests_failed = 0
        
    def run_all_tests(self):
        """Run all test cases."""
        print("🧠 Testing Cognitive Framework Visualizer (Step 3.1)")
        print("=" * 60)
        
        # Core functionality tests
        self.test_visualizer_initialization()
        self.test_framework_icons_mapping()
        self.test_complexity_level_filtering()
        self.test_frameworks_overview_display()
        self.test_framework_detail_display()
        self.test_framework_comparison()
        self.test_cognitive_diversity_explanation()
        self.test_example_query_demonstrations()
        
        # Integration tests
        self.test_progressive_disclosure_integration()
        self.test_special_commands_support()
        self.test_error_handling()
        self.test_fallback_behavior()
        
        # Print results
        print("\n" + "=" * 60)
        total_tests = self.tests_passed + self.tests_failed
        print(f"📊 Test Results: {self.tests_passed}/{total_tests} passed")
        
        if self.tests_failed == 0:
            print("✅ All tests passed! Cognitive Framework Visualizer is ready.")
            return True
        else:
            print(f"❌ {self.tests_failed} tests failed. Please review implementation.")
            return False
    
    def test_visualizer_initialization(self):
        """Test 1: Visualizer initialization and basic properties."""
        try:
            # Test basic initialization
            visualizer = CognitiveFrameworkVisualizer()
            assert visualizer is not None, "Visualizer should initialize"
            assert visualizer.console is not None, "Console should be initialized"
            assert visualizer.template_library is not None, "Template library should be loaded"
            
            # Test framework icons mapping
            assert len(visualizer.framework_icons) == 10, "Should have 10 framework icons"
            assert "ins_analytical" in visualizer.framework_icons, "Should have analytical framework icon"
            assert "ins_creative" in visualizer.framework_icons, "Should have creative framework icon"
            
            # Test complexity levels
            assert len(visualizer.complexity_levels) == 3, "Should have 3 complexity levels"
            assert "basic" in visualizer.complexity_levels, "Should have basic complexity level"
            assert "advanced" in visualizer.complexity_levels, "Should have advanced complexity level"
            assert "expert" in visualizer.complexity_levels, "Should have expert complexity level"
            
            # Test example queries
            assert len(visualizer.example_queries) == 10, "Should have examples for all 10 frameworks"
            
            self._test_passed("Visualizer initialization")
            
        except Exception as e:
            self._test_failed("Visualizer initialization", str(e))
    
    def test_framework_icons_mapping(self):
        """Test 2: Framework icon mapping completeness and consistency."""
        try:
            # Get all templates from library
            templates = self.template_library.list_templates()
            template_ids = [t.id for t in templates]
            
            # Check that all templates have icons
            for template_id in template_ids:
                assert template_id in self.visualizer.framework_icons, f"Missing icon for {template_id}"
            
            # Check that all icons are unique
            icons = list(self.visualizer.framework_icons.values())
            assert len(icons) == len(set(icons)), "All framework icons should be unique"
            
            # Check specific icon assignments
            expected_icons = {
                "ins_analytical": "🔍",
                "ins_creative": "💡",
                "ins_critical": "⚖️",
                "ins_integrative": "🔗",
                "ins_pragmatic": "🔧"
            }
            
            for framework_id, expected_icon in expected_icons.items():
                actual_icon = self.visualizer.framework_icons.get(framework_id)
                assert actual_icon == expected_icon, f"Wrong icon for {framework_id}: got {actual_icon}, expected {expected_icon}"
            
            self._test_passed("Framework icons mapping")
            
        except Exception as e:
            self._test_failed("Framework icons mapping", str(e))
    
    def test_complexity_level_filtering(self):
        """Test 3: Complexity level filtering functionality."""
        try:
            # Test basic level frameworks
            basic_frameworks = self.visualizer.get_frameworks_for_complexity("basic")
            assert len(basic_frameworks) == 3, "Basic level should have 3 frameworks"
            
            # Test advanced level frameworks
            advanced_frameworks = self.visualizer.get_frameworks_for_complexity("advanced")
            assert len(advanced_frameworks) == 4, "Advanced level should have 4 frameworks"
            
            # Test expert level frameworks
            expert_frameworks = self.visualizer.get_frameworks_for_complexity("expert")
            assert len(expert_frameworks) == 3, "Expert level should have 3 frameworks"
            
            # Test that total adds up to all frameworks
            total_frameworks = len(basic_frameworks) + len(advanced_frameworks) + len(expert_frameworks)
            all_templates = len(self.template_library.list_templates())
            assert total_frameworks == all_templates, "Sum of complexity levels should equal total frameworks"
            
            # Test framework IDs are correctly categorized
            basic_ids = [fw[0] for fw in basic_frameworks]
            assert "ins_analytical" in basic_ids, "Analytical should be in basic level"
            assert "ins_creative" in basic_ids, "Creative should be in basic level"
            assert "ins_pragmatic" in basic_ids, "Pragmatic should be in basic level"
            
            self._test_passed("Complexity level filtering")
            
        except Exception as e:
            self._test_failed("Complexity level filtering", str(e))
    
    def test_frameworks_overview_display(self):
        """Test 4: Frameworks overview display functionality."""
        try:
            # Capture output for different complexity levels
            test_console = Console(file=io.StringIO(), width=80)
            test_visualizer = CognitiveFrameworkVisualizer(test_console)
            
            # Test basic overview
            test_visualizer.display_frameworks_overview("basic")
            basic_output = test_console.file.getvalue()
            assert "Cognitive Frameworks" in basic_output, "Should display frameworks title"
            assert "Basic Level" in basic_output, "Should show basic level indication"
            
            # Reset console
            test_console.file.seek(0)
            test_console.file.truncate(0)
            
            # Test advanced overview
            test_visualizer.display_frameworks_overview("advanced")
            advanced_output = test_console.file.getvalue()
            assert "Advanced Level" in advanced_output, "Should show advanced level indication"
            
            # Reset console
            test_console.file.seek(0)
            test_console.file.truncate(0)
            
            # Test all frameworks overview
            test_visualizer.display_frameworks_overview("all")
            all_output = test_console.file.getvalue()
            assert "🧠 Cognitive Frameworks" in all_output, "Should display all frameworks title"
            
            self._test_passed("Frameworks overview display")
            
        except Exception as e:
            self._test_failed("Frameworks overview display", str(e))
    
    def test_framework_detail_display(self):
        """Test 5: Individual framework detail display."""
        try:
            test_console = Console(file=io.StringIO(), width=80)
            test_visualizer = CognitiveFrameworkVisualizer(test_console)
            
            # Test valid framework detail
            test_visualizer.display_framework_detail("ins_analytical")
            output = test_console.file.getvalue()
            assert "Analytical Framework" in output, "Should display framework name"
            assert "Cognitive Style" in output, "Should show cognitive style"
            assert "Core Strength" in output, "Should show core strength"
            assert "Example Application" in output, "Should show example"
            
            # Reset console
            test_console.file.seek(0)
            test_console.file.truncate(0)
            
            # Test invalid framework ID
            test_visualizer.display_framework_detail("invalid_framework")
            error_output = test_console.file.getvalue()
            assert "not found" in error_output, "Should show error for invalid framework"
            
            self._test_passed("Framework detail display")
            
        except Exception as e:
            self._test_failed("Framework detail display", str(e))
    
    def test_framework_comparison(self):
        """Test 6: Framework comparison functionality."""
        try:
            test_console = Console(file=io.StringIO(), width=80)
            test_visualizer = CognitiveFrameworkVisualizer(test_console)
            
            # Test valid framework comparison
            test_visualizer.display_framework_comparison("ins_analytical", "ins_creative")
            output = test_console.file.getvalue()
            assert "Framework Comparison" in output, "Should display comparison title"
            assert "Analytical Framework" in output, "Should show first framework"
            assert "Creative Framework" in output, "Should show second framework"
            assert ("Cognitive Style" in output or "Cognitive" in output), "Should compare cognitive styles"
            assert "Best When" in output, "Should show when to use each"
            
            # Reset console
            test_console.file.seek(0)
            test_console.file.truncate(0)
            
            # Test invalid framework comparison
            test_visualizer.display_framework_comparison("invalid1", "invalid2")
            error_output = test_console.file.getvalue()
            assert "not found" in error_output, "Should show error for invalid frameworks"
            
            self._test_passed("Framework comparison")
            
        except Exception as e:
            self._test_failed("Framework comparison", str(e))
    
    def test_cognitive_diversity_explanation(self):
        """Test 7: Cognitive diversity explanation display."""
        try:
            test_console = Console(file=io.StringIO(), width=80)
            test_visualizer = CognitiveFrameworkVisualizer(test_console)
            
            test_visualizer.display_cognitive_diversity_explanation()
            output = test_console.file.getvalue()
            
            assert "Cognitive Diversity in AI Innovation" in output, "Should display title"
            assert "cognitive diversity" in output, "Should explain cognitive diversity concept"
            assert "How It Works" in output, "Should explain how it works"
            assert "Example" in output, "Should provide example"
            assert "Result" in output, "Should show result"
            
            self._test_passed("Cognitive diversity explanation")
            
        except Exception as e:
            self._test_failed("Cognitive diversity explanation", str(e))
    
    def test_example_query_demonstrations(self):
        """Test 8: Example query demonstrations for each framework."""
        try:
            # Check that all frameworks have example queries
            templates = self.template_library.list_templates()
            
            for template in templates:
                assert template.id in self.visualizer.example_queries, f"Missing example for {template.id}"
                
                example = self.visualizer.example_queries[template.id]
                assert "query" in example, f"Missing query in example for {template.id}"
                assert "approach" in example, f"Missing approach in example for {template.id}"
                assert len(example["query"]) > 0, f"Empty query for {template.id}"
                assert len(example["approach"]) > 0, f"Empty approach for {template.id}"
            
            # Test that examples use consistent query
            first_query = list(self.visualizer.example_queries.values())[0]["query"]
            for example in self.visualizer.example_queries.values():
                assert example["query"] == first_query, "All examples should use same query for comparison"
            
            # Test that approaches are different
            approaches = [ex["approach"] for ex in self.visualizer.example_queries.values()]
            assert len(approaches) == len(set(approaches)), "All framework approaches should be unique"
            
            self._test_passed("Example query demonstrations")
            
        except Exception as e:
            self._test_failed("Example query demonstrations", str(e))
    
    def test_progressive_disclosure_integration(self):
        """Test 9: Integration with progressive disclosure pattern."""
        try:
            # Test that complexity levels map to correct frameworks
            complexity_mapping = {
                "basic": ["ins_analytical", "ins_creative", "ins_pragmatic"],
                "advanced": ["ins_critical", "ins_integrative", "ins_systems", "ins_historical"],
                "expert": ["ins_first_principles", "ins_contrarian", "ins_futurist"]
            }
            
            for level, expected_ids in complexity_mapping.items():
                actual_frameworks = self.visualizer.get_frameworks_for_complexity(level)
                actual_ids = [fw[0] for fw in actual_frameworks]
                
                for expected_id in expected_ids:
                    assert expected_id in actual_ids, f"{expected_id} should be in {level} level"
            
            # Test that display names include icons
            basic_frameworks = self.visualizer.get_frameworks_for_complexity("basic")
            for framework_id, display_name in basic_frameworks:
                expected_icon = self.visualizer.framework_icons[framework_id]
                assert expected_icon in display_name, f"Display name should include icon for {framework_id}"
            
            self._test_passed("Progressive disclosure integration")
            
        except Exception as e:
            self._test_failed("Progressive disclosure integration", str(e))
    
    def test_special_commands_support(self):
        """Test 10: Special commands functionality for enhanced interaction."""
        try:
            # Test that framework visualizer supports the needed methods for special commands
            assert hasattr(self.visualizer, 'display_framework_detail'), "Should support preview command"
            assert hasattr(self.visualizer, 'display_framework_comparison'), "Should support compare command"
            assert hasattr(self.visualizer, 'display_frameworks_overview'), "Should support list command"
            
            # Test that methods work with valid inputs
            test_console = Console(file=io.StringIO(), width=80)
            test_visualizer = CognitiveFrameworkVisualizer(test_console)
            
            # Test preview functionality
            test_visualizer.display_framework_detail("ins_analytical")
            output1 = test_console.file.getvalue()
            assert len(output1) > 0, "Preview should generate output"
            
            # Reset and test compare functionality
            test_console.file.seek(0)
            test_console.file.truncate(0)
            test_visualizer.display_framework_comparison("ins_analytical", "ins_creative")
            output2 = test_console.file.getvalue()
            assert len(output2) > 0, "Compare should generate output"
            
            self._test_passed("Special commands support")
            
        except Exception as e:
            self._test_failed("Special commands support", str(e))
    
    def test_error_handling(self):
        """Test 11: Error handling for invalid inputs."""
        try:
            test_console = Console(file=io.StringIO(), width=80)
            test_visualizer = CognitiveFrameworkVisualizer(test_console)
            
            # Test invalid framework ID in detail view
            test_visualizer.display_framework_detail("nonexistent_framework")
            output1 = test_console.file.getvalue()
            assert "not found" in output1.lower(), "Should handle invalid framework ID gracefully"
            
            # Reset console
            test_console.file.seek(0)
            test_console.file.truncate(0)
            
            # Test invalid complexity level
            frameworks = test_visualizer.get_frameworks_for_complexity("invalid_level")
            assert frameworks == [], "Should return empty list for invalid complexity level"
            
            # Test invalid framework comparison
            test_visualizer.display_framework_comparison("invalid1", "ins_analytical")
            output2 = test_console.file.getvalue()
            assert "not found" in output2.lower(), "Should handle invalid framework comparison gracefully"
            
            self._test_passed("Error handling")
            
        except Exception as e:
            self._test_failed("Error handling", str(e))
    
    def test_fallback_behavior(self):
        """Test 12: Fallback behavior when visualizer is not available."""
        try:
            # Test create_framework_visualizer function
            visualizer1 = create_framework_visualizer()
            assert visualizer1 is not None, "Should create visualizer without console"
            
            visualizer2 = create_framework_visualizer(self.console)
            assert visualizer2 is not None, "Should create visualizer with console"
            assert visualizer2.console == self.console, "Should use provided console"
            
            # Test that visualizer works without custom console
            assert visualizer1.console is not None, "Should have default console"
            
            self._test_passed("Fallback behavior")
            
        except Exception as e:
            self._test_failed("Fallback behavior", str(e))
    
    def _test_passed(self, test_name):
        """Record a passed test."""
        print(f"✅ {test_name}")
        self.tests_passed += 1
    
    def _test_failed(self, test_name, error):
        """Record a failed test."""
        print(f"❌ {test_name}: {error}")
        self.tests_failed += 1


def main():
    """Run the test suite."""
    print("Starting Cognitive Framework Visualizer Test Suite...")
    print("Testing Step 3.1: Cognitive Frameworks Visualization\n")
    
    try:
        # Import check
        from cognitive_framework_visualizer import CognitiveFrameworkVisualizer
        print("✅ Successfully imported CognitiveFrameworkVisualizer")
        
        # Run tests
        test_suite = TestCognitiveFrameworkVisualizer()
        success = test_suite.run_all_tests()
        
        if success:
            print("\n🎉 Step 3.1: Cognitive Frameworks Visualization is fully implemented and tested!")
            print("Ready for integration with Command Wizard.")
            return 0
        else:
            print("\n⚠️  Some tests failed. Please review and fix issues before proceeding.")
            return 1
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure cognitive_framework_visualizer.py is in the current directory.")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())