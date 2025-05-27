"""
Preset Manager Module for ISEE Framework

This module provides preset configuration management to build upon the purpose selection
foundation. Presets offer refined parameter configurations within purpose categories,
giving users more specific options while maintaining ease of use.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
import json
import os
from pathlib import Path

@dataclass
class PresetConfiguration:
    """Represents a preset configuration with specific parameter values."""
    
    id: str
    name: str
    description: str
    purpose_category: str  # Links to purpose category ID
    icon: str  # Unicode icon or emoji
    parameters: Dict[str, Any]  # Complete parameter configuration
    tags: List[str] = field(default_factory=list)  # Searchable tags
    estimated_cost: str = "medium"  # "low", "medium", "high"
    estimated_time: str = "moderate"  # "quick", "moderate", "extended"
    complexity_level: str = "intermediate"  # "beginner", "intermediate", "advanced"
    use_cases: List[str] = field(default_factory=list)  # Specific use case examples
    created_by: str = "system"  # "system" or "user"
    is_custom: bool = False  # True for user-created presets
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "purpose_category": self.purpose_category,
            "icon": self.icon,
            "parameters": self.parameters,
            "tags": self.tags,
            "estimated_cost": self.estimated_cost,
            "estimated_time": self.estimated_time,
            "complexity_level": self.complexity_level,
            "use_cases": self.use_cases,
            "created_by": self.created_by,
            "is_custom": self.is_custom
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PresetConfiguration':
        """Create from dictionary representation."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            purpose_category=data["purpose_category"],
            icon=data["icon"],
            parameters=data["parameters"],
            tags=data.get("tags", []),
            estimated_cost=data.get("estimated_cost", "medium"),
            estimated_time=data.get("estimated_time", "moderate"),
            complexity_level=data.get("complexity_level", "intermediate"),
            use_cases=data.get("use_cases", []),
            created_by=data.get("created_by", "system"),
            is_custom=data.get("is_custom", False)
        )


class PresetManager:
    """Manages preset configurations for the ISEE Command Wizard."""
    
    def __init__(self, custom_presets_dir: Optional[str] = None):
        """
        Initialize the preset manager.
        
        Args:
            custom_presets_dir: Directory to store custom user presets
        """
        self.presets: Dict[str, PresetConfiguration] = {}
        self.custom_presets_dir = custom_presets_dir or os.path.join(
            os.path.expanduser("~"), ".isee", "presets"
        )
        
        # Ensure custom presets directory exists
        Path(self.custom_presets_dir).mkdir(parents=True, exist_ok=True)
        
        # Load system presets and user presets
        self._load_system_presets()
        self._load_custom_presets()
    
    def _load_system_presets(self):
        """Load built-in system presets for each purpose category."""
        
        # Quick Exploration Presets
        self.add_preset(PresetConfiguration(
            id="quick_brainstorm",
            name="Quick Brainstorm",
            description="Rapid idea generation with minimal setup - perfect for getting started quickly",
            purpose_category="quick_exploration",
            icon="⚡",
            parameters={
                "models": 2,
                "instructions": 2,
                "variations": 1,
                "max_combinations": 4,
                "sampling_method": "random"
            },
            tags=["fast", "simple", "brainstorm", "ideation"],
            estimated_cost="low",
            estimated_time="quick",
            complexity_level="beginner",
            use_cases=[
                "Initial brainstorming sessions",
                "Quick feasibility checks", 
                "Rapid prototype concepts"
            ]
        ))
        
        self.add_preset(PresetConfiguration(
            id="exploration_plus",
            name="Exploration Plus",
            description="Enhanced exploration with more cognitive diversity while staying efficient",
            purpose_category="quick_exploration",
            icon="🚀",
            parameters={
                "models": 3,
                "instructions": 3,
                "variations": 2,
                "max_combinations": 8,
                "sampling_method": "stratified"
            },
            tags=["enhanced", "diverse", "efficient"],
            estimated_cost="medium",
            estimated_time="moderate",
            complexity_level="intermediate",
            use_cases=[
                "Market opportunity scanning",
                "Feature ideation workshops",
                "Creative problem solving"
            ]
        ))
        
        # Deep Analysis Presets
        self.add_preset(PresetConfiguration(
            id="comprehensive_analysis",
            name="Comprehensive Analysis",
            description="Thorough analysis using maximum cognitive diversity for deep insights",
            purpose_category="deep_analysis",
            icon="🔬",
            parameters={
                "models": 4,
                "instructions": 5,
                "variations": 2,
                "max_combinations": 20,
                "sampling_method": "stratified",
                "balanced_models": True
            },
            tags=["thorough", "comprehensive", "research", "analysis"],
            estimated_cost="high",
            estimated_time="extended",
            complexity_level="advanced",
            use_cases=[
                "Strategic planning initiatives",
                "Market research projects",
                "Technology assessment studies"
            ]
        ))
        
        self.add_preset(PresetConfiguration(
            id="focused_deep_dive",
            name="Focused Deep Dive",
            description="Intensive analysis with controlled scope for specific research questions",
            purpose_category="deep_analysis",
            icon="🎯",
            parameters={
                "models": 3,
                "instructions": 4,
                "variations": 2,
                "max_combinations": 12,
                "sampling_method": "stratified"
            },
            tags=["focused", "intensive", "specific", "controlled"],
            estimated_cost="medium",
            estimated_time="moderate",
            complexity_level="intermediate",
            use_cases=[
                "Specific problem analysis",
                "Competitor deep dives",
                "Technology evaluation"
            ]
        ))
        
        # Creative Innovation Presets
        self.add_preset(PresetConfiguration(
            id="breakthrough_innovation",
            name="Breakthrough Innovation",
            description="Maximum creativity with balanced cognitive approaches for revolutionary ideas",
            purpose_category="creative_innovation",
            icon="💡",
            parameters={
                "models": 4,
                "instructions": 5,
                "variations": 3,
                "max_combinations": 30,
                "sampling_method": "balanced",
                "balanced_models": True
            },
            tags=["creative", "breakthrough", "revolutionary", "innovation"],
            estimated_cost="high",
            estimated_time="extended",
            complexity_level="advanced",
            use_cases=[
                "Disruptive product concepts",
                "Next-generation service design",
                "Blue ocean strategy development"
            ]
        ))
        
        self.add_preset(PresetConfiguration(
            id="creative_exploration",
            name="Creative Exploration",
            description="Balanced creativity with manageable complexity for innovative solutions",
            purpose_category="creative_innovation",
            icon="🌟",
            parameters={
                "models": 3,
                "instructions": 4,
                "variations": 2,
                "max_combinations": 16,
                "sampling_method": "balanced"
            },
            tags=["creative", "balanced", "manageable", "innovative"],
            estimated_cost="medium",
            estimated_time="moderate",
            complexity_level="intermediate",
            use_cases=[
                "Product feature innovation",
                "Process improvement ideas",
                "Customer experience enhancement"
            ]
        ))
        
        # Content Creation Presets
        self.add_preset(PresetConfiguration(
            id="content_variety",
            name="Content Variety",
            description="Multiple content perspectives with efficient parameter settings",
            purpose_category="content_creation",
            icon="📝",
            parameters={
                "models": 2,
                "instructions": 3,
                "variations": 2,
                "max_combinations": 8,
                "sampling_method": "random"
            },
            tags=["content", "variety", "efficient", "writing"],
            estimated_cost="medium",
            estimated_time="moderate",
            complexity_level="beginner",
            use_cases=[
                "Blog post angle generation",
                "Marketing copy variations",
                "Training material development"
            ]
        ))
        
        # Problem Solving Presets
        self.add_preset(PresetConfiguration(
            id="systematic_solving",
            name="Systematic Problem Solving",
            description="Structured approach using diverse methodologies for comprehensive solutions",
            purpose_category="problem_solving",
            icon="🔧",
            parameters={
                "models": 3,
                "instructions": 4,
                "variations": 2,
                "max_combinations": 16,
                "sampling_method": "stratified"
            },
            tags=["systematic", "structured", "methodical", "solutions"],
            estimated_cost="medium",
            estimated_time="moderate",
            complexity_level="intermediate",
            use_cases=[
                "Operational problem solving",
                "Technical challenge resolution",
                "Process optimization"
            ]
        ))
        
        # Learning Design Presets
        self.add_preset(PresetConfiguration(
            id="instructional_design",
            name="Instructional Design",
            description="Educational approach with multiple pedagogical perspectives",
            purpose_category="learning_design",
            icon="🎓",
            parameters={
                "models": 3,
                "instructions": 4,
                "variations": 2,
                "max_combinations": 16,
                "sampling_method": "stratified"
            },
            tags=["education", "pedagogy", "learning", "instruction"],
            estimated_cost="medium",
            estimated_time="moderate",
            complexity_level="intermediate",
            use_cases=[
                "Course curriculum design",
                "Learning pathway development",
                "Assessment strategy creation"
            ]
        ))
        
        # Strategic Planning Presets
        self.add_preset(PresetConfiguration(
            id="strategic_comprehensive",
            name="Strategic Comprehensive",
            description="Long-term strategic thinking with maximum cognitive diversity",
            purpose_category="strategic_planning",
            icon="🎯",
            parameters={
                "models": 4,
                "instructions": 5,
                "variations": 3,
                "max_combinations": 24,
                "sampling_method": "stratified",
                "balanced_models": True
            },
            tags=["strategic", "long-term", "comprehensive", "planning"],
            estimated_cost="high",
            estimated_time="extended",
            complexity_level="advanced",
            use_cases=[
                "5-year strategic planning",
                "Market entry strategies",
                "Transformation roadmaps"
            ]
        ))
        
        # OpenRouter Integration Presets (OpenRouter Integration Stage 2)
        self.add_preset(PresetConfiguration(
            id="openrouter_provider_diversity",
            name="OpenRouter Provider Diversity",
            description="Leverage OpenRouter's 300+ models across multiple providers for maximum cognitive diversity",
            purpose_category="deep_analysis",
            icon="🌐",
            parameters={
                "models": 5,
                "instructions": 4,
                "variations": 2,
                "max_combinations": 20,
                "sampling_method": "stratified",
                "balanced_models": True,
                "openrouter_filters": {
                    "providers": ["anthropic", "openai", "google", "meta-llama", "mistralai"],
                    "capabilities": ["reasoning", "analysis", "large_context"]
                }
            },
            tags=["openrouter", "diversity", "multi-provider", "comprehensive"],
            estimated_cost="medium",
            estimated_time="moderate",
            complexity_level="intermediate",
            use_cases=[
                "Cross-provider model comparison",
                "Maximum cognitive diversity analysis",
                "Provider-agnostic research"
            ]
        ))
        
        self.add_preset(PresetConfiguration(
            id="openrouter_coding_focused",
            name="OpenRouter Coding Models",
            description="Specialized coding models from OpenRouter for software development tasks",
            purpose_category="problem_solving",
            icon="💻",
            parameters={
                "models": 3,
                "instructions": 3,
                "variations": 2,
                "max_combinations": 12,
                "sampling_method": "stratified",
                "openrouter_filters": {
                    "capabilities": ["coding", "reasoning"],
                    "cost_tiers": ["budget", "standard", "premium"]
                }
            },
            tags=["openrouter", "coding", "development", "programming"],
            estimated_cost="medium",
            estimated_time="moderate",
            complexity_level="intermediate",
            use_cases=[
                "Code architecture decisions",
                "Algorithm optimization strategies",
                "Development best practices"
            ]
        ))
        
        self.add_preset(PresetConfiguration(
            id="openrouter_budget_optimizer",
            name="OpenRouter Budget Optimizer",
            description="Cost-effective analysis using OpenRouter's budget-tier models without sacrificing quality",
            purpose_category="quick_exploration",
            icon="💰",
            parameters={
                "models": 4,
                "instructions": 3,
                "variations": 2,
                "max_combinations": 12,
                "sampling_method": "stratified",
                "openrouter_filters": {
                    "cost_tiers": ["free", "budget"],
                    "capabilities": ["reasoning", "fast"]
                }
            },
            tags=["openrouter", "budget", "cost-effective", "efficient"],
            estimated_cost="low",
            estimated_time="quick",
            complexity_level="beginner",
            use_cases=[
                "Budget-conscious research",
                "High-volume analysis tasks",
                "Educational projects"
            ]
        ))
        
        self.add_preset(PresetConfiguration(
            id="openrouter_premium_flagship",
            name="OpenRouter Premium Flagship",
            description="Top-tier models from OpenRouter for highest quality analysis and insights",
            purpose_category="strategic_planning",
            icon="⭐",
            parameters={
                "models": 3,
                "instructions": 5,
                "variations": 2,
                "max_combinations": 15,
                "sampling_method": "stratified",
                "balanced_models": True,
                "openrouter_filters": {
                    "cost_tiers": ["premium", "premium_plus"],
                    "capabilities": ["reasoning", "analysis", "large_context"],
                    "providers": ["anthropic", "openai", "google"]
                }
            },
            tags=["openrouter", "premium", "flagship", "high-quality"],
            estimated_cost="high",
            estimated_time="extended",
            complexity_level="advanced",
            use_cases=[
                "Critical business decisions",
                "High-stakes strategic planning",
                "Executive-level analysis"
            ]
        ))
    
    def _load_custom_presets(self):
        """Load user-created custom presets from the custom presets directory."""
        preset_files = Path(self.custom_presets_dir).glob("*.json")
        
        for preset_file in preset_files:
            try:
                with open(preset_file, 'r') as f:
                    data = json.load(f)
                preset = PresetConfiguration.from_dict(data)
                preset.is_custom = True
                self.add_preset(preset)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # Skip invalid preset files
                print(f"Warning: Could not load preset from {preset_file}: {e}")
    
    def add_preset(self, preset: PresetConfiguration):
        """Add a preset configuration to the manager."""
        self.presets[preset.id] = preset
    
    def get_preset(self, preset_id: str) -> Optional[PresetConfiguration]:
        """Get a specific preset by ID."""
        return self.presets.get(preset_id)
    
    def list_presets(self) -> List[PresetConfiguration]:
        """Get all preset configurations."""
        return list(self.presets.values())
    
    def get_presets_by_purpose(self, purpose_category: str) -> List[PresetConfiguration]:
        """Get presets filtered by purpose category."""
        return [preset for preset in self.presets.values() 
                if preset.purpose_category == purpose_category]
    
    def get_presets_by_complexity(self, complexity_level: str) -> List[PresetConfiguration]:
        """Get presets filtered by complexity level."""
        return [preset for preset in self.presets.values() 
                if preset.complexity_level == complexity_level]
    
    def get_presets_by_cost(self, cost_level: str) -> List[PresetConfiguration]:
        """Get presets filtered by estimated cost."""
        return [preset for preset in self.presets.values() 
                if preset.estimated_cost == cost_level]
    
    def search_presets(self, query: str) -> List[PresetConfiguration]:
        """Search presets by name, description, tags, or use cases."""
        query_lower = query.lower()
        matches = []
        
        for preset in self.presets.values():
            # Check name and description
            if (query_lower in preset.name.lower() or 
                query_lower in preset.description.lower()):
                matches.append(preset)
                continue
            
            # Check tags
            for tag in preset.tags:
                if query_lower in tag.lower():
                    matches.append(preset)
                    break
            else:
                # Check use cases if no tag match
                for use_case in preset.use_cases:
                    if query_lower in use_case.lower():
                        matches.append(preset)
                        break
        
        return matches
    
    def save_custom_preset(self, preset: PresetConfiguration) -> bool:
        """
        Save a custom preset to the user's preset directory.
        
        Args:
            preset: The preset configuration to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not preset.is_custom:
            preset.is_custom = True
            preset.created_by = "user"
        
        try:
            preset_file = Path(self.custom_presets_dir) / f"{preset.id}.json"
            with open(preset_file, 'w') as f:
                json.dump(preset.to_dict(), f, indent=2)
            
            # Add to our in-memory collection
            self.add_preset(preset)
            return True
        except Exception as e:
            print(f"Error saving preset {preset.id}: {e}")
            return False
    
    def delete_custom_preset(self, preset_id: str) -> bool:
        """
        Delete a custom preset.
        
        Args:
            preset_id: ID of the preset to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        preset = self.get_preset(preset_id)
        if not preset or not preset.is_custom:
            return False
        
        try:
            preset_file = Path(self.custom_presets_dir) / f"{preset_id}.json"
            if preset_file.exists():
                preset_file.unlink()
            
            # Remove from in-memory collection
            del self.presets[preset_id]
            return True
        except Exception as e:
            print(f"Error deleting preset {preset_id}: {e}")
            return False
    
    def create_preset_from_parameters(self, 
                                    name: str, 
                                    description: str,
                                    purpose_category: str,
                                    parameters: Dict[str, Any],
                                    **kwargs) -> PresetConfiguration:
        """
        Create a new custom preset from current parameters.
        
        Args:
            name: Name for the preset
            description: Description of the preset
            purpose_category: Purpose category this preset belongs to
            parameters: Parameter configuration
            **kwargs: Additional preset properties
            
        Returns:
            The created preset configuration
        """
        preset_id = name.lower().replace(" ", "_").replace("-", "_")
        
        # Ensure unique ID
        counter = 1
        original_id = preset_id
        while preset_id in self.presets:
            preset_id = f"{original_id}_{counter}"
            counter += 1
        
        preset = PresetConfiguration(
            id=preset_id,
            name=name,
            description=description,
            purpose_category=purpose_category,
            parameters=parameters.copy(),
            icon=kwargs.get("icon", "⚙️"),
            tags=kwargs.get("tags", []),
            estimated_cost=kwargs.get("estimated_cost", "medium"),
            estimated_time=kwargs.get("estimated_time", "moderate"),
            complexity_level=kwargs.get("complexity_level", "intermediate"),
            use_cases=kwargs.get("use_cases", []),
            is_custom=True,
            created_by="user"
        )
        
        return preset


def create_default_preset_manager() -> PresetManager:
    """Create a preset manager with default system presets."""
    return PresetManager()


# For testing and development
if __name__ == "__main__":
    manager = create_default_preset_manager()
    
    print("Available Preset Configurations:")
    for purpose in ["quick_exploration", "deep_analysis", "creative_innovation"]:
        presets = manager.get_presets_by_purpose(purpose)
        if presets:
            print(f"\n{purpose.replace('_', ' ').title()}:")
            for preset in presets:
                print(f"  {preset.icon} {preset.name}")
                print(f"    {preset.description}")
                print(f"    Cost: {preset.estimated_cost}, Time: {preset.estimated_time}")
                print(f"    Parameters: {preset.parameters}")