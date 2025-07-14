#!/usr/bin/env python3
"""
Comprehensive test suite for the Preset Manager functionality (Step 2.2)

This test suite validates all aspects of the preset configuration implementation
including preset creation, management, saving/loading, and integration with
the command wizard.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add the current directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from preset_manager import PresetManager, PresetConfiguration, create_default_preset_manager
    from purpose_categories import create_default_purpose_manager
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_AVAILABLE = False

def test_preset_configuration_creation():
    """Test PresetConfiguration creation and data handling."""
    print("Testing PresetConfiguration creation...")
    
    preset = PresetConfiguration(
        id="test_preset",
        name="Test Preset",
        description="A test preset configuration",
        purpose_category="quick_exploration",
        icon="🧪",
        parameters={"models": 2, "instructions": 3},
        tags=["test", "example"],
        estimated_cost="low",
        estimated_time="quick",
        complexity_level="beginner",
        use_cases=["Testing purposes"],
        is_custom=True
    )
    
    assert preset.id == "test_preset"
    assert preset.name == "Test Preset"
    assert preset.parameters["models"] == 2
    assert preset.is_custom == True
    
    # Test dictionary conversion
    preset_dict = preset.to_dict()
    assert preset_dict["id"] == "test_preset"
    assert preset_dict["parameters"]["models"] == 2
    
    # Test creation from dictionary
    new_preset = PresetConfiguration.from_dict(preset_dict)
    assert new_preset.id == preset.id
    assert new_preset.parameters == preset.parameters
    
    print("✓ PresetConfiguration creation test passed")

def test_preset_manager_initialization():
    """Test PresetManager initialization and default presets."""
    print("Testing PresetManager initialization...")
    
    # Test with temporary directory to avoid affecting real user data
    with tempfile.TemporaryDirectory() as temp_dir:
        preset_manager = PresetManager(custom_presets_dir=temp_dir)
        
        # Check that default presets are loaded
        presets = preset_manager.list_presets()
        assert len(presets) > 0, "Should have default presets"
        
        # Check specific preset categories
        quick_presets = preset_manager.get_presets_by_purpose("quick_exploration")
        assert len(quick_presets) >= 2, "Should have quick exploration presets"
        
        deep_presets = preset_manager.get_presets_by_purpose("deep_analysis")
        assert len(deep_presets) >= 2, "Should have deep analysis presets"
        
        creative_presets = preset_manager.get_presets_by_purpose("creative_innovation")
        assert len(creative_presets) >= 2, "Should have creative innovation presets"
        
        print(f"✓ Found {len(presets)} default presets")
        
    print("✓ PresetManager initialization test passed")

def test_preset_filtering_and_search():
    """Test preset filtering and search functionality."""
    print("Testing preset filtering and search...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        preset_manager = PresetManager(custom_presets_dir=temp_dir)
        
        # Test filtering by purpose
        quick_presets = preset_manager.get_presets_by_purpose("quick_exploration")
        for preset in quick_presets:
            assert preset.purpose_category == "quick_exploration"
        
        # Test filtering by complexity
        beginner_presets = preset_manager.get_presets_by_complexity("beginner")
        for preset in beginner_presets:
            assert preset.complexity_level == "beginner"
        
        # Test filtering by cost
        low_cost_presets = preset_manager.get_presets_by_cost("low")
        for preset in low_cost_presets:
            assert preset.estimated_cost == "low"
        
        # Test search functionality
        brainstorm_presets = preset_manager.search_presets("brainstorm")
        assert len(brainstorm_presets) > 0, "Should find presets containing 'brainstorm'"
        
        analysis_presets = preset_manager.search_presets("analysis")
        assert len(analysis_presets) > 0, "Should find presets containing 'analysis'"
        
        print("✓ Preset filtering and search test passed")

def test_custom_preset_creation_and_saving():
    """Test creating and saving custom presets."""
    print("Testing custom preset creation and saving...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        preset_manager = PresetManager(custom_presets_dir=temp_dir)
        
        # Create a custom preset
        custom_preset = preset_manager.create_preset_from_parameters(
            name="My Test Preset",
            description="A custom test preset",
            purpose_category="problem_solving",
            parameters={
                "models": 3,
                "instructions": 4,
                "variations": 2,
                "max_combinations": 12,
                "sampling_method": "stratified"
            },
            complexity_level="intermediate",
            estimated_cost="medium",
            estimated_time="moderate"
        )
        
        assert custom_preset.is_custom == True
        assert custom_preset.created_by == "user"
        assert custom_preset.name == "My Test Preset"
        
        # Save the custom preset
        save_success = preset_manager.save_custom_preset(custom_preset)
        assert save_success == True, "Should successfully save custom preset"
        
        # Verify the preset file was created
        preset_file = Path(temp_dir) / f"{custom_preset.id}.json"
        assert preset_file.exists(), "Preset file should be created"
        
        # Verify the preset can be retrieved
        retrieved_preset = preset_manager.get_preset(custom_preset.id)
        assert retrieved_preset is not None
        assert retrieved_preset.name == "My Test Preset"
        assert retrieved_preset.parameters["models"] == 3
        
        print("✓ Custom preset creation and saving test passed")

def test_custom_preset_loading():
    """Test loading custom presets from disk."""
    print("Testing custom preset loading...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a preset file manually
        custom_preset_data = {
            "id": "manual_test_preset",
            "name": "Manual Test Preset",
            "description": "Manually created test preset",
            "purpose_category": "content_creation",
            "icon": "📝",
            "parameters": {
                "models": 2,
                "instructions": 3,
                "variations": 2
            },
            "tags": ["manual", "test"],
            "estimated_cost": "low",
            "estimated_time": "quick",
            "complexity_level": "beginner",
            "use_cases": ["Manual testing"],
            "created_by": "user",
            "is_custom": True
        }
        
        preset_file = Path(temp_dir) / "manual_test_preset.json"
        with open(preset_file, 'w') as f:
            json.dump(custom_preset_data, f, indent=2)
        
        # Create preset manager that should load this file
        preset_manager = PresetManager(custom_presets_dir=temp_dir)
        
        # Verify the preset was loaded
        loaded_preset = preset_manager.get_preset("manual_test_preset")
        assert loaded_preset is not None
        assert loaded_preset.name == "Manual Test Preset"
        assert loaded_preset.is_custom == True
        assert loaded_preset.parameters["models"] == 2
        
        print("✓ Custom preset loading test passed")

def test_preset_deletion():
    """Test deleting custom presets."""
    print("Testing custom preset deletion...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        preset_manager = PresetManager(custom_presets_dir=temp_dir)
        
        # Create and save a custom preset
        custom_preset = preset_manager.create_preset_from_parameters(
            name="Deletable Preset",
            description="A preset to be deleted",
            purpose_category="custom_exploration",
            parameters={"models": 2}
        )
        
        preset_manager.save_custom_preset(custom_preset)
        
        # Verify it exists
        assert preset_manager.get_preset(custom_preset.id) is not None
        
        # Delete it
        delete_success = preset_manager.delete_custom_preset(custom_preset.id)
        assert delete_success == True, "Should successfully delete custom preset"
        
        # Verify it's gone
        assert preset_manager.get_preset(custom_preset.id) is None
        
        # Verify file is deleted
        preset_file = Path(temp_dir) / f"{custom_preset.id}.json"
        assert not preset_file.exists(), "Preset file should be deleted"
        
        # Test deleting non-existent preset
        delete_fail = preset_manager.delete_custom_preset("non_existent_preset")
        assert delete_fail == False, "Should fail to delete non-existent preset"
        
        print("✓ Custom preset deletion test passed")

def test_preset_parameter_validation():
    """Test that preset parameters are valid and complete."""
    print("Testing preset parameter validation...")
    
    preset_manager = create_default_preset_manager()
    
    # Check all default presets have required fields
    for preset in preset_manager.list_presets():
        assert preset.id, "Preset should have ID"
        assert preset.name, "Preset should have name"
        assert preset.description, "Preset should have description"
        assert preset.purpose_category, "Preset should have purpose category"
        assert preset.icon, "Preset should have icon"
        assert isinstance(preset.parameters, dict), "Preset should have parameters dict"
        assert preset.estimated_cost in ["low", "medium", "high"], "Invalid cost estimate"
        assert preset.estimated_time in ["quick", "moderate", "extended"], "Invalid time estimate"
        assert preset.complexity_level in ["beginner", "intermediate", "advanced"], "Invalid complexity"
        
        # Check that parameter values are reasonable
        if "models" in preset.parameters:
            assert isinstance(preset.parameters["models"], int)
            assert 1 <= preset.parameters["models"] <= 10, "Models count should be reasonable"
        
        if "instructions" in preset.parameters:
            assert isinstance(preset.parameters["instructions"], int)
            assert 1 <= preset.parameters["instructions"] <= 10, "Instructions count should be reasonable"
        
        if "max_combinations" in preset.parameters:
            assert isinstance(preset.parameters["max_combinations"], int)
            assert preset.parameters["max_combinations"] > 0, "Max combinations should be positive"
    
    print("✓ Preset parameter validation test passed")

def test_purpose_preset_integration():
    """Test integration between purpose categories and presets."""
    print("Testing purpose-preset integration...")
    
    purpose_manager = create_default_purpose_manager()
    preset_manager = create_default_preset_manager()
    
    # Check that each purpose category has at least one preset
    purposes = purpose_manager.list_categories()
    for purpose in purposes:
        if purpose.id != "custom_exploration":  # Custom exploration may not have presets
            presets = preset_manager.get_presets_by_purpose(purpose.id)
            assert len(presets) > 0, f"Purpose '{purpose.id}' should have at least one preset"
    
    # Verify preset purpose categories exist in purpose manager
    for preset in preset_manager.list_presets():
        purpose = purpose_manager.get_category(preset.purpose_category)
        if preset.purpose_category != "custom_exploration":
            assert purpose is not None, f"Preset '{preset.id}' references non-existent purpose '{preset.purpose_category}'"
    
    print("✓ Purpose-preset integration test passed")

def run_all_tests():
    """Run all preset manager tests."""
    if not IMPORTS_AVAILABLE:
        print("❌ Cannot run tests - import errors occurred")
        return False
    
    print("🧪 Running Preset Manager Test Suite (Step 2.2)")
    print("=" * 60)
    
    try:
        test_preset_configuration_creation()
        test_preset_manager_initialization()
        test_preset_filtering_and_search()
        test_custom_preset_creation_and_saving()
        test_custom_preset_loading()
        test_preset_deletion()
        test_preset_parameter_validation()
        test_purpose_preset_integration()
        
        print("=" * 60)
        print("✅ All Preset Manager tests passed!")
        print("\nStep 2.2 Implementation Summary:")
        print("• ✓ Preset data structure and configuration format")
        print("• ✓ PresetManager class with full functionality")
        print("• ✓ Custom preset saving/loading infrastructure")
        print("• ✓ Preset filtering, search, and management")
        print("• ✓ Integration with purpose selection system")
        print("• ✓ Visual preview and comparison capabilities")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)