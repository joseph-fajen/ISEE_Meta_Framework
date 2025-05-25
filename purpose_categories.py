"""
Purpose Categories Module for ISEE Framework

This module provides purpose-based categorization to shift the Command Wizard
from a parameter-focused to purpose-focused interface. Users select their 
purpose first, which then suggests appropriate parameter configurations.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
import json

@dataclass
class PurposeCategory:
    """Represents a purpose category with associated parameter recommendations."""
    
    id: str
    name: str
    description: str
    icon: str  # Unicode icon or emoji
    examples: List[str]  # Example use cases
    recommended_params: Dict[str, Any]  # Default parameter values
    required_expertise: str  # "beginner", "intermediate", "advanced"
    estimated_cost: str  # "low", "medium", "high"
    typical_runtime: str  # "quick", "moderate", "extended"
    domains: List[str]  # Suggested domain IDs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "examples": self.examples,
            "recommended_params": self.recommended_params,
            "required_expertise": self.required_expertise,
            "estimated_cost": self.estimated_cost,
            "typical_runtime": self.typical_runtime,
            "domains": self.domains
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PurposeCategory':
        """Create from dictionary representation."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            icon=data["icon"],
            examples=data["examples"],
            recommended_params=data["recommended_params"],
            required_expertise=data["required_expertise"],
            estimated_cost=data["estimated_cost"],
            typical_runtime=data["typical_runtime"],
            domains=data["domains"]
        )


class PurposeManager:
    """Manages purpose categories and their parameter mappings."""
    
    def __init__(self):
        """Initialize with default purpose categories."""
        self.categories: Dict[str, PurposeCategory] = {}
        self._load_default_categories()
    
    def _load_default_categories(self):
        """Load the default set of purpose categories."""
        
        # Quick Exploration - For rapid ideation and brainstorming
        self.add_category(PurposeCategory(
            id="quick_exploration",
            name="Quick Exploration",
            description="Rapid brainstorming and initial idea generation for immediate insights",
            icon="🚀",
            examples=[
                "Generate 10 creative marketing campaign ideas",
                "Brainstorm potential product features",
                "Quick competitive analysis angles"
            ],
            recommended_params={
                "models": 2,
                "instructions": 2,
                "variations": 1,
                "max_combinations": 4,
                "sampling_method": "random"
            },
            required_expertise="beginner",
            estimated_cost="low",
            typical_runtime="quick",
            domains=["domain_general"]
        ))
        
        # Deep Analysis - For comprehensive research and analysis
        self.add_category(PurposeCategory(
            id="deep_analysis",
            name="Deep Analysis",
            description="Comprehensive exploration using diverse cognitive approaches for thorough insights",
            icon="🔬",
            examples=[
                "Analyze market opportunities from multiple perspectives",
                "Comprehensive strategic planning review",
                "Multi-angle problem diagnosis"
            ],
            recommended_params={
                "models": 4,
                "instructions": 5,
                "variations": 2,
                "max_combinations": 20,
                "sampling_method": "stratified"
            },
            required_expertise="intermediate",
            estimated_cost="high",
            typical_runtime="extended",
            domains=["domain_business_strategy", "domain_research"]
        ))
        
        # Creative Innovation - For breakthrough thinking and novel solutions
        self.add_category(PurposeCategory(
            id="creative_innovation",
            name="Creative Innovation",
            description="Maximum cognitive diversity for breakthrough ideas and novel solutions",
            icon="💡",
            examples=[
                "Design revolutionary product concepts",
                "Create disruptive business models",
                "Develop innovative learning experiences"
            ],
            recommended_params={
                "models": 3,
                "instructions": 4,
                "variations": 3,
                "max_combinations": 24,
                "sampling_method": "balanced",
                "balanced_models": True
            },
            required_expertise="intermediate",
            estimated_cost="high",
            typical_runtime="extended",
            domains=["domain_innovation", "domain_creative_thinking"]
        ))
        
        # Problem Solving - For systematic solution development
        self.add_category(PurposeCategory(
            id="problem_solving",
            name="Problem Solving",
            description="Structured approach to analyzing problems and developing practical solutions",
            icon="🔧",
            examples=[
                "Troubleshoot complex operational issues",
                "Design solutions for user experience problems",
                "Develop technical implementation strategies"
            ],
            recommended_params={
                "models": 3,
                "instructions": 3,
                "variations": 2,
                "max_combinations": 12,
                "sampling_method": "stratified"
            },
            required_expertise="intermediate",
            estimated_cost="medium",
            typical_runtime="moderate",
            domains=["domain_engineering", "domain_systems_thinking"]
        ))
        
        # Content Creation - For writing and content development
        self.add_category(PurposeCategory(
            id="content_creation",
            name="Content Creation",
            description="Generate diverse content approaches and writing perspectives",
            icon="📝",
            examples=[
                "Develop multiple article angles",
                "Create varied training materials",
                "Generate content for different audiences"
            ],
            recommended_params={
                "models": 2,
                "instructions": 3,
                "variations": 2,
                "max_combinations": 8,
                "sampling_method": "random"
            },
            required_expertise="beginner",
            estimated_cost="medium",
            typical_runtime="moderate",
            domains=["domain_technical_writing", "domain_content_strategy"]
        ))
        
        # Learning Design - For educational and training purposes
        self.add_category(PurposeCategory(
            id="learning_design",
            name="Learning Design",
            description="Educational approach focused on learning outcomes and instructional methods",
            icon="🎓",
            examples=[
                "Design course curriculum from multiple pedagogical angles",
                "Create assessment strategies",
                "Develop learning experience frameworks"
            ],
            recommended_params={
                "models": 3,
                "instructions": 4,
                "variations": 2,
                "max_combinations": 16,
                "sampling_method": "stratified"
            },
            required_expertise="intermediate",
            estimated_cost="medium",
            typical_runtime="moderate",
            domains=["domain_instructional_design", "domain_elearning", "domain_learning_experience"]
        ))
        
        # Strategic Planning - For long-term thinking and planning
        self.add_category(PurposeCategory(
            id="strategic_planning",
            name="Strategic Planning",
            description="Long-term perspective and strategic thinking across multiple timeframes and scenarios",
            icon="🎯",
            examples=[
                "Develop 5-year technology roadmaps",
                "Create market entry strategies",
                "Design organizational transformation plans"
            ],
            recommended_params={
                "models": 4,
                "instructions": 4,
                "variations": 2,
                "max_combinations": 20,
                "sampling_method": "stratified",
                "balanced_models": True
            },
            required_expertise="advanced",
            estimated_cost="high",
            typical_runtime="extended",
            domains=["domain_business_strategy", "domain_systems_thinking"]
        ))
        
        # Custom Exploration - For advanced users who want full control
        self.add_category(PurposeCategory(
            id="custom_exploration",
            name="Custom Exploration",
            description="Full parameter control for advanced users with specific requirements",
            icon="⚙️",
            examples=[
                "Specific research methodology requirements",
                "Custom cognitive framework combinations",
                "Specialized domain-specific analysis"
            ],
            recommended_params={
                # No defaults - user will set all parameters
            },
            required_expertise="advanced",
            estimated_cost="variable",
            typical_runtime="variable",
            domains=[]  # User will select
        ))
    
    def add_category(self, category: PurposeCategory):
        """Add a purpose category to the manager."""
        self.categories[category.id] = category
    
    def get_category(self, category_id: str) -> Optional[PurposeCategory]:
        """Get a specific purpose category by ID."""
        return self.categories.get(category_id)
    
    def list_categories(self) -> List[PurposeCategory]:
        """Get all purpose categories."""
        return list(self.categories.values())
    
    def get_categories_by_expertise(self, expertise: str) -> List[PurposeCategory]:
        """Get categories filtered by required expertise level."""
        return [cat for cat in self.categories.values() 
                if cat.required_expertise == expertise]
    
    def get_categories_by_cost(self, cost: str) -> List[PurposeCategory]:
        """Get categories filtered by estimated cost."""
        return [cat for cat in self.categories.values() 
                if cat.estimated_cost == cost]
    
    def search_categories(self, query: str) -> List[PurposeCategory]:
        """Search categories by name, description, or examples."""
        query_lower = query.lower()
        matches = []
        
        for category in self.categories.values():
            # Check name and description
            if (query_lower in category.name.lower() or 
                query_lower in category.description.lower()):
                matches.append(category)
                continue
            
            # Check examples
            for example in category.examples:
                if query_lower in example.lower():
                    matches.append(category)
                    break
        
        return matches
    
    def save_to_file(self, filepath: str):
        """Save purpose categories to a JSON file."""
        data = {
            "purpose_categories": [cat.to_dict() for cat in self.categories.values()]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filepath: str):
        """Load purpose categories from a JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.categories = {}
        for cat_data in data["purpose_categories"]:
            category = PurposeCategory.from_dict(cat_data)
            self.add_category(category)


def create_default_purpose_manager() -> PurposeManager:
    """Create a purpose manager with default categories."""
    return PurposeManager()


# For testing and development
if __name__ == "__main__":
    manager = create_default_purpose_manager()
    
    print("Available Purpose Categories:")
    for category in manager.list_categories():
        print(f"\n{category.icon} {category.name}")
        print(f"  {category.description}")
        print(f"  Expertise: {category.required_expertise}")
        print(f"  Cost: {category.estimated_cost}, Runtime: {category.typical_runtime}")
        print(f"  Examples: {category.examples[0]}...")