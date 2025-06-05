#!/usr/bin/env python3
"""
Test Enhanced Parameter Editors

Tests the new enhanced parameter editor framework to ensure:
- Framework components work correctly
- Integration with dashboard controller functions
- Rich displays and special commands operate properly
"""

import sys
from rich.console import Console
from unittest.mock import Mock

def test_framework_imports():
    """Test that all framework components import correctly"""
    try:
        from enhanced_parameter_editor import EnhancedParameterEditor, ParameterItem, SelectionMode
        from query_parameter_editor import QueryParameterEditor
        from variations_parameter_editor import VariationsParameterEditor
        print("✅ All enhanced parameter editor components imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_parameter_item_creation():
    """Test ParameterItem creation and metadata handling"""
    try:
        from enhanced_parameter_editor import ParameterItem
        
        item = ParameterItem(
            id="test_1",
            name="Test Item",
            description="A test parameter item",
            metadata={"category": "test", "score": 8}
        )
        
        assert item.id == "test_1"
        assert item.name == "Test Item"
        assert item.description == "A test parameter item"
        assert item.metadata["category"] == "test"
        assert item.metadata["score"] == 8
        
        print("✅ ParameterItem creation and metadata handling works correctly")
        return True
    except Exception as e:
        print(f"❌ ParameterItem test failed: {e}")
        return False

def test_query_editor_initialization():
    """Test QueryParameterEditor initialization"""
    try:
        from query_parameter_editor import QueryParameterEditor
        
        console = Console()
        mock_dashboard_state = Mock()
        mock_dashboard_state.parameters = {"query": {"value": "test query"}}
        
        editor = QueryParameterEditor(console, mock_dashboard_state)
        
        assert editor.parameter_name == "query"
        assert editor.current_value == "test query"
        assert len(editor.query_categories) > 0
        
        print("✅ QueryParameterEditor initialization works correctly")
        return True
    except Exception as e:
        print(f"❌ QueryParameterEditor test failed: {e}")
        return False

def test_variations_editor_initialization():
    """Test VariationsParameterEditor initialization"""
    try:
        from variations_parameter_editor import VariationsParameterEditor
        
        console = Console()
        mock_dashboard_state = Mock()
        mock_dashboard_state.parameters = {"variations": {"value": 3}}
        
        editor = VariationsParameterEditor(console, mock_dashboard_state)
        
        assert editor.parameter_name == "variations"
        assert editor.current_value == 3
        assert len(editor.variation_configs) == 5  # Should have 5 predefined configurations
        
        print("✅ VariationsParameterEditor initialization works correctly")
        return True
    except Exception as e:
        print(f"❌ VariationsParameterEditor test failed: {e}")
        return False

def test_query_categories_and_examples():
    """Test query categories contain appropriate examples"""
    try:
        from query_parameter_editor import QueryParameterEditor
        
        console = Console()
        mock_dashboard_state = Mock()
        mock_dashboard_state.parameters = {"query": {"value": ""}}
        
        editor = QueryParameterEditor(console, mock_dashboard_state)
        
        # Test category structure
        expected_categories = ["Innovation & Creativity", "Problem Solving", "Strategic Planning", 
                             "Technology & Innovation", "Learning & Development"]
        
        for category in expected_categories:
            assert category in editor.query_categories, f"Missing category: {category}"
            assert len(editor.query_categories[category]) >= 3, f"Too few examples in {category}"
        
        print("✅ Query categories and examples are properly structured")
        return True
    except Exception as e:
        print(f"❌ Query categories test failed: {e}")
        return False

def test_variations_configurations():
    """Test variations configurations are properly defined"""
    try:
        from variations_parameter_editor import VariationsParameterEditor
        
        console = Console()
        mock_dashboard_state = Mock()
        mock_dashboard_state.parameters = {"variations": {"value": 2}}
        
        editor = VariationsParameterEditor(console, mock_dashboard_state)
        
        # Test configuration structure
        for config in editor.variation_configs:
            required_fields = ["count", "name", "description", "use_case", "quality_score", 
                             "exploration_score", "cost_multiplier", "time_multiplier", "recommended_for"]
            
            for field in required_fields:
                assert field in config, f"Missing field {field} in variation config"
            
            # Test value ranges
            assert 1 <= config["count"] <= 5, f"Invalid count: {config['count']}"
            assert 1 <= config["quality_score"] <= 10, f"Invalid quality score: {config['quality_score']}"
            assert 1 <= config["exploration_score"] <= 10, f"Invalid exploration score: {config['exploration_score']}"
        
        print("✅ Variations configurations are properly structured")
        return True
    except Exception as e:
        print(f"❌ Variations configurations test failed: {e}")
        return False

def test_selection_mode_types():
    """Test SelectionMode enum values"""
    try:
        from enhanced_parameter_editor import SelectionMode
        
        expected_modes = ["single", "multiple", "count", "hybrid"]
        actual_modes = [SelectionMode.SINGLE, SelectionMode.MULTIPLE, SelectionMode.COUNT_BASED, SelectionMode.HYBRID]
        
        for mode in actual_modes:
            assert mode in expected_modes, f"Unexpected selection mode: {mode}"
        
        print("✅ SelectionMode types are properly defined")
        return True
    except Exception as e:
        print(f"❌ SelectionMode test failed: {e}")
        return False

def test_dashboard_integration():
    """Test that enhanced editors integrate with dashboard controller"""
    try:
        # Mock the dashboard state
        mock_dashboard_state = Mock()
        mock_dashboard_state.parameters = {
            "query": {"value": "test query"},
            "variations": {"value": 2}
        }
        mock_dashboard_state.update_parameter = Mock()
        
        console = Console()
        
        # Test query editor integration
        from query_parameter_editor import QueryParameterEditor
        query_editor = QueryParameterEditor(console, mock_dashboard_state)
        items = query_editor.load_items()
        assert len(items) > 0, "Query editor should load example items"
        
        # Test variations editor integration  
        from variations_parameter_editor import VariationsParameterEditor
        variations_editor = VariationsParameterEditor(console, mock_dashboard_state)
        items = variations_editor.load_items()
        assert len(items) == 5, "Variations editor should load 5 configurations"
        
        print("✅ Enhanced editors integrate properly with dashboard state")
        return True
    except Exception as e:
        print(f"❌ Dashboard integration test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("🧪 Testing Enhanced Parameter Editor Framework")
    print("=" * 50)
    
    tests = [
        test_framework_imports,
        test_parameter_item_creation,
        test_query_editor_initialization,
        test_variations_editor_initialization,
        test_query_categories_and_examples,
        test_variations_configurations,
        test_selection_mode_types,
        test_dashboard_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Enhanced parameter editor framework is ready.")
        return True
    else:
        print(f"⚠️ {failed} tests failed. Please review and fix issues.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)