#!/usr/bin/env python3
"""
Test Suite for Dashboard Parameter Standardization Phase 2

This test suite validates the Phase 2 parameter editors:
- Domain parameter editor with category filtering
- Models parameter editor with OpenRouter collections
- Unified parameter editors (sampling_method, max_combinations, output_format)
- Enhanced parameter editor framework integration
- Dashboard controller integration

Part of UX Enhancement Roadmap - Dashboard Parameter Standardization Phase 2
"""

import sys
import pytest
from io import StringIO
from unittest.mock import Mock, patch, MagicMock
from rich.console import Console

# Test framework components
try:
    from domain_parameter_editor import DomainParameterEditor
    from models_parameter_editor import ModelsParameterEditor
    from unified_parameter_editor import (
        SamplingMethodParameterEditor, 
        MaxCombinationsParameterEditor,
        OutputFormatParameterEditor,
        create_unified_parameter_editor
    )
    from enhanced_parameter_editor import ParameterEditorFactory, ParameterItem, SelectionMode
    EDITORS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Parameter editors not available: {e}")
    EDITORS_AVAILABLE = False


class MockParameter:
    """Mock parameter with value attribute"""
    def __init__(self, value):
        self.value = value

class MockDashboardState:
    """Mock dashboard state for testing"""
    
    def __init__(self):
        self.parameters = {
            "domain": MockParameter("Technology Innovation"),
            "models": MockParameter(3),
            "sampling_method": MockParameter("random"),
            "max_combinations": MockParameter(12),
            "output_format": MockParameter("json"),
            "openrouter_filters": MockParameter(""),
            "config_file": MockParameter("unified_config.json"),
            "use_ollama": MockParameter(False),
            "balanced_models": MockParameter(False)
        }
    
    def get(self, key, default=None):
        return self.parameters.get(key, default)


def capture_console_output(func, *args, **kwargs):
    """Capture Rich console output for testing"""
    output = StringIO()
    console = Console(file=output, width=80)
    
    try:
        result = func(console, *args, **kwargs)
        return result, output.getvalue()
    except Exception as e:
        return None, f"Error: {e}"


class TestDomainParameterEditor:
    """Test suite for Domain Parameter Editor"""
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_domain_editor_initialization(self):
        """Test domain editor initializes correctly"""
        console = Console()
        dashboard_state = MockDashboardState()
        
        editor = DomainParameterEditor(console, dashboard_state)
        
        assert editor.parameter_name == "domain"
        assert editor.current_value == "Technology Innovation"
        assert editor.selection_mode == SelectionMode.HYBRID
        assert editor.show_help_on_start == True
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_domain_categories_loading(self):
        """Test domain categories are loaded correctly"""
        console = Console()
        dashboard_state = MockDashboardState()
        editor = DomainParameterEditor(console, dashboard_state)
        
        items = editor.load_items()
        
        # Should have items from multiple categories
        assert len(items) > 0
        
        # Check category diversity
        categories = set(item.metadata.get("category") for item in items)
        assert len(categories) >= 8  # Should have at least 8 different categories
        
        # Check required categories exist
        category_names = [cat["name"] for cat in editor.domain_categories.values()]
        assert "Innovation & Technology" in category_names
        assert "Business & Strategy" in category_names
        assert "Education & Learning" in category_names
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_domain_display_table(self):
        """Test domain display table generation"""
        def run_test(console):
            dashboard_state = MockDashboardState()
            editor = DomainParameterEditor(console, dashboard_state)
            editor.items = editor.load_items()
            
            table = editor.get_display_table()
            return table
        
        result, output = capture_console_output(run_test)
        
        assert result is not None
        assert "Available Domain Categories" in str(result.title)
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_domain_validation(self):
        """Test domain selection validation"""
        console = Console()
        dashboard_state = MockDashboardState()
        editor = DomainParameterEditor(console, dashboard_state)
        editor.items = editor.load_items()
        
        # Valid numeric selection
        assert editor.validate_selection("1") == True
        assert editor.validate_selection(str(len(editor.items))) == True
        
        # Valid custom domain
        assert editor.validate_selection("Custom Domain") == True
        assert editor.validate_selection("Advanced Robotics") == True
        
        # Invalid selections
        assert editor.validate_selection("") == False
        assert editor.validate_selection("0") == False
        assert editor.validate_selection(str(len(editor.items) + 1)) == False


class TestModelsParameterEditor:
    """Test suite for Models Parameter Editor"""
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_models_editor_initialization(self):
        """Test models editor initializes correctly"""
        console = Console()
        dashboard_state = MockDashboardState()
        
        editor = ModelsParameterEditor(console, dashboard_state)
        
        assert editor.parameter_name == "models"
        assert editor.current_value == 3
        assert editor.selection_mode == SelectionMode.HYBRID
        assert editor.show_help_on_start == True
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_models_types_loading(self):
        """Test different model types are loaded"""
        console = Console()
        dashboard_state = MockDashboardState()
        editor = ModelsParameterEditor(console, dashboard_state)
        
        items = editor.load_items()
        
        # Should have items from different model types
        assert len(items) > 0
        
        # Check model type diversity
        types = set(item.metadata.get("type") for item in items)
        expected_types = ["openrouter_collection", "individual_openrouter", "traditional_api", "local_ollama"]
        
        # Should have at least some of the expected types
        assert len(types.intersection(expected_types)) >= 2
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_models_display_table(self):
        """Test models display table generation"""
        def run_test(console):
            dashboard_state = MockDashboardState()
            editor = ModelsParameterEditor(console, dashboard_state)
            editor.items = editor.load_items()
            
            table = editor.get_display_table()
            return table
        
        result, output = capture_console_output(run_test)
        
        assert result is not None
        assert "Available Model Selection Options" in str(result.title)
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_models_cost_estimation(self):
        """Test model cost estimation"""
        console = Console()
        dashboard_state = MockDashboardState()
        editor = ModelsParameterEditor(console, dashboard_state)
        
        # Test known models
        cost = editor._estimate_model_cost("openai/gpt-4o-mini")
        assert cost == "$0.15"
        
        cost = editor._estimate_model_cost("anthropic/claude-3.7-sonnet")
        assert cost == "$3.00"
        
        # Test unknown model (should have default)
        cost = editor._estimate_model_cost("unknown/model")
        assert cost == "$0.50"
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_models_quality_estimation(self):
        """Test model quality estimation"""
        console = Console()
        dashboard_state = MockDashboardState()
        editor = ModelsParameterEditor(console, dashboard_state)
        
        # Test known models
        quality = editor._estimate_model_quality("anthropic/claude-sonnet-4")
        assert quality == 9.7
        
        quality = editor._estimate_model_quality("openai/gpt-4o-mini")
        assert quality == 8.5
        
        # Test unknown model (should have default)
        quality = editor._estimate_model_quality("unknown/model")
        assert quality == 7.0


class TestUnifiedParameterEditors:
    """Test suite for Unified Parameter Editors"""
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_sampling_method_editor(self):
        """Test sampling method parameter editor"""
        console = Console()
        dashboard_state = MockDashboardState()
        
        editor = SamplingMethodParameterEditor(console, dashboard_state)
        
        assert editor.parameter_name == "sampling_method"
        assert editor.current_value == "random"
        assert editor.selection_mode == SelectionMode.SINGLE
        
        # Test loading sampling methods
        items = editor.load_items()
        assert len(items) == 4  # random, stratified, systematic, adaptive
        
        # Check method IDs
        method_ids = [item.id for item in items]
        assert "random" in method_ids
        assert "stratified" in method_ids
        assert "systematic" in method_ids
        assert "adaptive" in method_ids
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_max_combinations_editor(self):
        """Test max combinations parameter editor"""
        console = Console()
        dashboard_state = MockDashboardState()
        
        editor = MaxCombinationsParameterEditor(console, dashboard_state)
        
        assert editor.parameter_name == "max_combinations"
        assert editor.current_value == 12
        assert editor.selection_mode == SelectionMode.HYBRID
        
        # Test loading resource profiles
        items = editor.load_items()
        assert len(items) == 5  # quick, standard, comprehensive, extensive, research
        
        # Check profiles exist
        profile_ids = [item.metadata.get("profile_type") for item in items]
        assert "quick" in profile_ids
        assert "standard" in profile_ids
        assert "comprehensive" in profile_ids
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_output_format_editor(self):
        """Test output format parameter editor"""
        console = Console()
        dashboard_state = MockDashboardState()
        
        editor = OutputFormatParameterEditor(console, dashboard_state)
        
        assert editor.parameter_name == "output_format"
        assert editor.current_value == "json"
        assert editor.selection_mode == SelectionMode.SINGLE
        
        # Test loading output formats
        items = editor.load_items()
        assert len(items) == 5  # json, yaml, text, csv, markdown
        
        # Check format IDs
        format_ids = [item.id for item in items]
        assert "json" in format_ids
        assert "yaml" in format_ids
        assert "text" in format_ids
        assert "csv" in format_ids
        assert "markdown" in format_ids
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_unified_editor_factory(self):
        """Test unified parameter editor factory"""
        console = Console()
        dashboard_state = MockDashboardState()
        
        # Test valid parameter types
        sampling_editor = create_unified_parameter_editor("sampling_method", console, dashboard_state)
        assert isinstance(sampling_editor, SamplingMethodParameterEditor)
        
        combinations_editor = create_unified_parameter_editor("max_combinations", console, dashboard_state)
        assert isinstance(combinations_editor, MaxCombinationsParameterEditor)
        
        format_editor = create_unified_parameter_editor("output_format", console, dashboard_state)
        assert isinstance(format_editor, OutputFormatParameterEditor)
        
        # Test invalid parameter type
        invalid_editor = create_unified_parameter_editor("invalid_param", console, dashboard_state)
        assert invalid_editor is None


class TestParameterEditorFactory:
    """Test suite for Enhanced Parameter Editor Factory"""
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_factory_domain_creation(self):
        """Test factory creates domain editor correctly"""
        console = Console()
        dashboard_state = MockDashboardState()
        
        editor = ParameterEditorFactory.create_editor("domain", console, dashboard_state)
        assert isinstance(editor, DomainParameterEditor)
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_factory_models_creation(self):
        """Test factory creates models editor correctly"""
        console = Console()
        dashboard_state = MockDashboardState()
        
        editor = ParameterEditorFactory.create_editor("models", console, dashboard_state)
        assert isinstance(editor, ModelsParameterEditor)
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_factory_unified_creation(self):
        """Test factory creates unified editors correctly"""
        console = Console()
        dashboard_state = MockDashboardState()
        
        # Test sampling method
        editor = ParameterEditorFactory.create_editor("sampling_method", console, dashboard_state)
        assert isinstance(editor, SamplingMethodParameterEditor)
        
        # Test max combinations
        editor = ParameterEditorFactory.create_editor("max_combinations", console, dashboard_state)
        assert isinstance(editor, MaxCombinationsParameterEditor)
        
        # Test output format
        editor = ParameterEditorFactory.create_editor("output_format", console, dashboard_state)
        assert isinstance(editor, OutputFormatParameterEditor)
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_factory_invalid_parameter(self):
        """Test factory handles invalid parameters correctly"""
        console = Console()
        dashboard_state = MockDashboardState()
        
        with pytest.raises(ValueError, match="No enhanced editor available"):
            ParameterEditorFactory.create_editor("invalid_parameter", console, dashboard_state)


class TestParameterEditorIntegration:
    """Test suite for parameter editor integration with dashboard"""
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_domain_editor_integration(self):
        """Test domain editor integrates with dashboard state"""
        console = Console()
        dashboard_state = MockDashboardState()
        
        editor = DomainParameterEditor(console, dashboard_state)
        editor.items = editor.load_items()
        
        # Test applying selection
        if len(editor.items) > 0:
            editor.apply_selection(1)
            # Check that dashboard state was updated
            assert dashboard_state.parameters["domain"].value == editor.items[0].name
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_models_editor_integration(self):
        """Test models editor integrates with dashboard state"""
        console = Console()
        dashboard_state = MockDashboardState()
        
        editor = ModelsParameterEditor(console, dashboard_state)
        editor.items = editor.load_items()
        
        # Test applying numeric selection (model count)
        # Since the editor might treat 5 as an item selection if there are 5+ items,
        # let's use a higher number to ensure it's treated as model count
        test_count = max(10, len(editor.items) + 1)
        editor.apply_selection(test_count)
        assert dashboard_state.parameters["models"].value == test_count
    
    @pytest.mark.skipif(not EDITORS_AVAILABLE, reason="Parameter editors not available")
    def test_sampling_method_integration(self):
        """Test sampling method editor integrates with dashboard state"""
        console = Console()
        dashboard_state = MockDashboardState()
        
        editor = SamplingMethodParameterEditor(console, dashboard_state)
        editor.items = editor.load_items()
        
        # Test applying selection
        editor.apply_selection(2)  # Should be stratified
        assert dashboard_state.parameters["sampling_method"].value == "stratified"


def run_comprehensive_test():
    """Run comprehensive test suite for Phase 2 parameter editors"""
    print("🧪 Dashboard Parameter Standardization Phase 2 - Test Suite")
    print("=" * 70)
    
    if not EDITORS_AVAILABLE:
        print("❌ Parameter editors not available - skipping tests")
        return False
    
    # Test categories
    test_categories = [
        ("Domain Parameter Editor", TestDomainParameterEditor),
        ("Models Parameter Editor", TestModelsParameterEditor), 
        ("Unified Parameter Editors", TestUnifiedParameterEditors),
        ("Parameter Editor Factory", TestParameterEditorFactory),
        ("Integration Tests", TestParameterEditorIntegration)
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for category_name, test_class in test_categories:
        print(f"\n📋 {category_name}")
        print("-" * 50)
        
        # Get test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for test_method_name in test_methods:
            total_tests += 1
            test_instance = test_class()
            test_method = getattr(test_instance, test_method_name)
            
            try:
                test_method()
                print(f"  ✅ {test_method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"  ❌ {test_method_name}: {str(e)}")
    
    # Summary
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Phase 2 parameter editors working correctly.")
        return True
    else:
        print(f"⚠️ {total_tests - passed_tests} tests failed. Review implementation.")
        return False


def test_framework_components():
    """Test framework components are working"""
    print("🔧 Testing Framework Components")
    print("-" * 40)
    
    # Test ParameterItem
    try:
        item = ParameterItem("test_id", "Test Item", "Test description")
        assert item.id == "test_id"
        assert item.name == "Test Item"
        print("  ✅ ParameterItem class working")
    except Exception as e:
        print(f"  ❌ ParameterItem class error: {e}")
        return False
    
    # Test SelectionMode
    try:
        assert SelectionMode.SINGLE == "single"
        assert SelectionMode.MULTIPLE == "multiple"
        assert SelectionMode.HYBRID == "hybrid"
        print("  ✅ SelectionMode enum working")
    except Exception as e:
        print(f"  ❌ SelectionMode enum error: {e}")
        return False
    
    print("  🎉 Framework components working correctly")
    return True


if __name__ == "__main__":
    print("🚀 Starting Dashboard Parameter Standardization Phase 2 Tests")
    print("=" * 70)
    
    # Test framework first
    if not test_framework_components():
        print("💥 Framework component tests failed - aborting")
        sys.exit(1)
    
    # Run comprehensive tests
    success = run_comprehensive_test()
    
    if success:
        print("\n✅ Phase 2 Implementation Successfully Validated!")
        print("🎯 Ready for integration and user testing")
        sys.exit(0)
    else:
        print("\n❌ Phase 2 Implementation Issues Detected")
        print("🔧 Review and fix issues before proceeding")
        sys.exit(1)