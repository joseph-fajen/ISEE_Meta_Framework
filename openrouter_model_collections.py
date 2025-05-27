"""
OpenRouter Model Collections for ISEE Framework

This module provides curated, purpose-driven model collections that serve as the primary
model selection experience for users. Each collection is tailored to specific use cases
and provides intelligent defaults for maximum cognitive diversity.

Part of OpenRouter Integration - Stage 3: Purpose-Driven Collections
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from openrouter_categorization import (
    ProviderCategory, CapabilityCategory, CostTier, UseCase, OpenRouterCategorizer
)

@dataclass
class ModelCollection:
    """A curated collection of models for a specific purpose."""
    
    id: str
    name: str
    description: str
    icon: str
    purpose_alignment: str  # Purpose category ID this collection serves
    model_specs: List[Dict[str, Any]]  # Specifications for selecting models
    diversity_strategy: str  # How to ensure cognitive diversity
    cost_profile: str  # "budget", "balanced", "premium"
    expected_model_count: int  # Typical number of models in this collection
    fallback_specs: List[Dict[str, Any]]  # Fallback if preferred models unavailable
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "purpose_alignment": self.purpose_alignment,
            "model_specs": self.model_specs,
            "diversity_strategy": self.diversity_strategy,
            "cost_profile": self.cost_profile,
            "expected_model_count": self.expected_model_count,
            "fallback_specs": self.fallback_specs
        }

class OpenRouterModelCollections:
    """Manager for curated OpenRouter model collections."""
    
    def __init__(self):
        """Initialize with purpose-driven model collections."""
        self.collections: Dict[str, ModelCollection] = {}
        self.categorizer = OpenRouterCategorizer()
        self._load_default_collections()
    
    def _load_default_collections(self):
        """Load the default set of curated model collections."""
        
        # Quick Exploration Collection - Fast, diverse, cost-effective
        self.add_collection(ModelCollection(
            id="quick_exploration",
            name="Quick Explorer",
            description="Fast, cost-effective models optimized for rapid brainstorming and initial exploration",
            icon="🚀",
            purpose_alignment="quick_exploration",
            model_specs=[
                {
                    "providers": [ProviderCategory.ANTHROPIC],
                    "capabilities": [CapabilityCategory.FAST, CapabilityCategory.CREATIVE],
                    "cost_tiers": [CostTier.BUDGET, CostTier.STANDARD],
                    "min_quality_score": 7.0,
                    "preference": "claude-3-haiku"
                },
                {
                    "providers": [ProviderCategory.OPENAI],
                    "capabilities": [CapabilityCategory.FAST, CapabilityCategory.REASONING],
                    "cost_tiers": [CostTier.BUDGET, CostTier.STANDARD],
                    "min_quality_score": 7.0,
                    "preference": "gpt-3.5-turbo"
                }
            ],
            diversity_strategy="provider_and_capability",
            cost_profile="budget",
            expected_model_count=2,
            fallback_specs=[
                {
                    "providers": [ProviderCategory.META],
                    "capabilities": [CapabilityCategory.FAST],
                    "cost_tiers": [CostTier.FREE, CostTier.BUDGET]
                }
            ]
        ))
        
        # Deep Analysis Collection - Premium models for comprehensive exploration
        self.add_collection(ModelCollection(
            id="deep_analysis",
            name="Deep Analyzer",
            description="Premium flagship models for comprehensive research and detailed analysis",
            icon="🔬",
            purpose_alignment="deep_analysis",
            model_specs=[
                {
                    "providers": [ProviderCategory.ANTHROPIC],
                    "capabilities": [CapabilityCategory.REASONING, CapabilityCategory.ANALYSIS],
                    "cost_tiers": [CostTier.PREMIUM, CostTier.STANDARD],
                    "min_quality_score": 8.5,
                    "preference": "claude-3.5-sonnet"
                },
                {
                    "providers": [ProviderCategory.OPENAI],
                    "capabilities": [CapabilityCategory.REASONING, CapabilityCategory.ANALYSIS],
                    "cost_tiers": [CostTier.PREMIUM, CostTier.STANDARD],
                    "min_quality_score": 8.5,
                    "preference": "gpt-4"
                },
                {
                    "providers": [ProviderCategory.GOOGLE],
                    "capabilities": [CapabilityCategory.REASONING, CapabilityCategory.LARGE_CONTEXT],
                    "cost_tiers": [CostTier.PREMIUM, CostTier.STANDARD],
                    "min_quality_score": 8.0,
                    "preference": "gemini-pro"
                }
            ],
            diversity_strategy="maximum_provider_diversity",
            cost_profile="premium",
            expected_model_count=3,
            fallback_specs=[
                {
                    "providers": [ProviderCategory.MISTRAL],
                    "capabilities": [CapabilityCategory.REASONING],
                    "cost_tiers": [CostTier.STANDARD]
                }
            ]
        ))
        
        # Creative Innovation Collection - Models optimized for breakthrough thinking
        self.add_collection(ModelCollection(
            id="creative_innovation",
            name="Innovation Engine",
            description="Creative powerhouses for breakthrough ideas and novel solution generation",
            icon="💡",
            purpose_alignment="creative_innovation",
            model_specs=[
                {
                    "providers": [ProviderCategory.ANTHROPIC],
                    "capabilities": [CapabilityCategory.CREATIVE, CapabilityCategory.REASONING],
                    "cost_tiers": [CostTier.PREMIUM, CostTier.STANDARD],
                    "min_quality_score": 8.0,
                    "preference": "claude-3.5-sonnet"
                },
                {
                    "providers": [ProviderCategory.OPENAI],
                    "capabilities": [CapabilityCategory.CREATIVE, CapabilityCategory.CONVERSATIONAL],
                    "cost_tiers": [CostTier.PREMIUM, CostTier.STANDARD],
                    "min_quality_score": 8.0,
                    "preference": "gpt-4"
                },
                {
                    "providers": [ProviderCategory.META],
                    "capabilities": [CapabilityCategory.CREATIVE, CapabilityCategory.INSTRUCTION_FOLLOWING],
                    "cost_tiers": [CostTier.BUDGET, CostTier.STANDARD],
                    "min_quality_score": 7.5,
                    "preference": "llama-3"
                }
            ],
            diversity_strategy="creative_cognitive_diversity",
            cost_profile="balanced",
            expected_model_count=3,
            fallback_specs=[
                {
                    "providers": [ProviderCategory.MISTRAL],
                    "capabilities": [CapabilityCategory.CREATIVE],
                    "cost_tiers": [CostTier.STANDARD]
                }
            ]
        ))
        
        # Content Creation Collection - Specialized for writing and content generation
        self.add_collection(ModelCollection(
            id="content_creation",
            name="Content Creator",
            description="Specialized models for high-quality writing, content generation, and communication",
            icon="✍️",
            purpose_alignment="content_creation",
            model_specs=[
                {
                    "providers": [ProviderCategory.ANTHROPIC],
                    "capabilities": [CapabilityCategory.CREATIVE, CapabilityCategory.INSTRUCTION_FOLLOWING],
                    "cost_tiers": [CostTier.STANDARD, CostTier.PREMIUM],
                    "min_quality_score": 8.0,
                    "preference": "claude-3.5-sonnet"
                },
                {
                    "providers": [ProviderCategory.OPENAI],
                    "capabilities": [CapabilityCategory.CREATIVE, CapabilityCategory.CONVERSATIONAL],
                    "cost_tiers": [CostTier.STANDARD, CostTier.PREMIUM],
                    "min_quality_score": 7.5,
                    "preference": "gpt-4"
                }
            ],
            diversity_strategy="style_and_approach_diversity",
            cost_profile="balanced",
            expected_model_count=2,
            fallback_specs=[
                {
                    "providers": [ProviderCategory.COHERE],
                    "capabilities": [CapabilityCategory.CREATIVE],
                    "cost_tiers": [CostTier.STANDARD]
                }
            ]
        ))
        
        # Problem Solving Collection - Analytical and systematic thinking models
        self.add_collection(ModelCollection(
            id="problem_solving",
            name="Problem Solver",
            description="Analytical models specialized in structured problem-solving and systematic thinking",
            icon="🧩",
            purpose_alignment="problem_solving",
            model_specs=[
                {
                    "providers": [ProviderCategory.ANTHROPIC],
                    "capabilities": [CapabilityCategory.REASONING, CapabilityCategory.ANALYSIS],
                    "cost_tiers": [CostTier.STANDARD, CostTier.PREMIUM],
                    "min_quality_score": 8.0,
                    "preference": "claude-3.5-sonnet"
                },
                {
                    "providers": [ProviderCategory.OPENAI],
                    "capabilities": [CapabilityCategory.REASONING, CapabilityCategory.CODING],
                    "cost_tiers": [CostTier.STANDARD, CostTier.PREMIUM],
                    "min_quality_score": 8.0,
                    "preference": "gpt-4"
                },
                {
                    "providers": [ProviderCategory.GOOGLE],
                    "capabilities": [CapabilityCategory.ANALYSIS, CapabilityCategory.LARGE_CONTEXT],
                    "cost_tiers": [CostTier.STANDARD],
                    "min_quality_score": 7.5,
                    "preference": "gemini-pro"
                }
            ],
            diversity_strategy="analytical_approach_diversity",
            cost_profile="balanced",
            expected_model_count=3,
            fallback_specs=[
                {
                    "providers": [ProviderCategory.MISTRAL],
                    "capabilities": [CapabilityCategory.REASONING],
                    "cost_tiers": [CostTier.STANDARD]
                }
            ]
        ))
        
        # Learning Design Collection - Educational and instructional models
        self.add_collection(ModelCollection(
            id="learning_design",
            name="Learning Designer",
            description="Educational specialists for curriculum design, learning experiences, and instructional content",
            icon="🎓",
            purpose_alignment="learning_design",
            model_specs=[
                {
                    "providers": [ProviderCategory.ANTHROPIC],
                    "capabilities": [CapabilityCategory.INSTRUCTION_FOLLOWING, CapabilityCategory.CREATIVE],
                    "cost_tiers": [CostTier.STANDARD],
                    "min_quality_score": 8.0,
                    "preference": "claude-3.5-sonnet"
                },
                {
                    "providers": [ProviderCategory.OPENAI],
                    "capabilities": [CapabilityCategory.INSTRUCTION_FOLLOWING, CapabilityCategory.CONVERSATIONAL],
                    "cost_tiers": [CostTier.STANDARD],
                    "min_quality_score": 7.5,
                    "preference": "gpt-4"
                }
            ],
            diversity_strategy="pedagogical_approach_diversity",
            cost_profile="balanced",
            expected_model_count=2,
            fallback_specs=[
                {
                    "providers": [ProviderCategory.META],
                    "capabilities": [CapabilityCategory.INSTRUCTION_FOLLOWING],
                    "cost_tiers": [CostTier.BUDGET]
                }
            ]
        ))
        
        # Strategic Planning Collection - Long-term thinking and planning models
        self.add_collection(ModelCollection(
            id="strategic_planning",
            name="Strategic Planner",
            description="High-level strategic thinking models for long-term planning and organizational insights",
            icon="📊",
            purpose_alignment="strategic_planning",
            model_specs=[
                {
                    "providers": [ProviderCategory.ANTHROPIC],
                    "capabilities": [CapabilityCategory.REASONING, CapabilityCategory.ANALYSIS],
                    "cost_tiers": [CostTier.PREMIUM, CostTier.STANDARD],
                    "min_quality_score": 8.5,
                    "preference": "claude-3.5-sonnet"
                },
                {
                    "providers": [ProviderCategory.OPENAI],
                    "capabilities": [CapabilityCategory.REASONING, CapabilityCategory.ANALYSIS],
                    "cost_tiers": [CostTier.PREMIUM, CostTier.STANDARD],
                    "min_quality_score": 8.0,
                    "preference": "gpt-4"
                },
                {
                    "providers": [ProviderCategory.GOOGLE],
                    "capabilities": [CapabilityCategory.LARGE_CONTEXT, CapabilityCategory.ANALYSIS],
                    "cost_tiers": [CostTier.STANDARD],
                    "min_quality_score": 7.5,
                    "preference": "gemini-pro"
                }
            ],
            diversity_strategy="strategic_perspective_diversity",
            cost_profile="premium",
            expected_model_count=3,
            fallback_specs=[
                {
                    "providers": [ProviderCategory.MISTRAL],
                    "capabilities": [CapabilityCategory.REASONING],
                    "cost_tiers": [CostTier.STANDARD]
                }
            ]
        ))
        
        # Budget Optimizer Collection - Cost-effective but capable models
        self.add_collection(ModelCollection(
            id="budget_optimizer",
            name="Budget Optimizer",
            description="High-value models that maximize capability while minimizing cost",
            icon="💰",
            purpose_alignment="custom_exploration",
            model_specs=[
                {
                    "providers": [ProviderCategory.META],
                    "capabilities": [CapabilityCategory.REASONING, CapabilityCategory.CREATIVE],
                    "cost_tiers": [CostTier.FREE, CostTier.BUDGET],
                    "min_quality_score": 7.0,
                    "preference": "llama-3"
                },
                {
                    "providers": [ProviderCategory.ANTHROPIC],
                    "capabilities": [CapabilityCategory.FAST],
                    "cost_tiers": [CostTier.BUDGET],
                    "min_quality_score": 7.0,
                    "preference": "claude-3-haiku"
                },
                {
                    "providers": [ProviderCategory.MISTRAL],
                    "capabilities": [CapabilityCategory.REASONING],
                    "cost_tiers": [CostTier.BUDGET, CostTier.STANDARD],
                    "min_quality_score": 6.5,
                    "preference": "mistral-7b"
                }
            ],
            diversity_strategy="cost_optimized_diversity",
            cost_profile="budget",
            expected_model_count=3,
            fallback_specs=[
                {
                    "providers": [ProviderCategory.TOGETHER],
                    "cost_tiers": [CostTier.FREE, CostTier.BUDGET]
                }
            ]
        ))
    
    def add_collection(self, collection: ModelCollection):
        """Add a new model collection."""
        self.collections[collection.id] = collection
    
    def get_collection(self, collection_id: str) -> Optional[ModelCollection]:
        """Get a specific model collection by ID."""
        return self.collections.get(collection_id)
    
    def get_collections_for_purpose(self, purpose_id: str) -> List[ModelCollection]:
        """Get all collections that align with a specific purpose."""
        return [
            collection for collection in self.collections.values()
            if collection.purpose_alignment == purpose_id
        ]
    
    def get_all_collections(self) -> List[ModelCollection]:
        """Get all available model collections."""
        return list(self.collections.values())
    
    def get_collection_by_cost_profile(self, cost_profile: str) -> List[ModelCollection]:
        """Get collections filtered by cost profile."""
        return [
            collection for collection in self.collections.values()
            if collection.cost_profile == cost_profile
        ]
    
    def get_recommended_collection(self, purpose_id: str, cost_preference: str = "balanced") -> Optional[ModelCollection]:
        """Get the recommended collection for a purpose and cost preference."""
        purpose_collections = self.get_collections_for_purpose(purpose_id)
        
        if not purpose_collections:
            # Fallback to general collections
            if cost_preference == "budget":
                return self.get_collection("budget_optimizer")
            elif cost_preference == "premium":
                return self.get_collection("deep_analysis")
            else:
                return self.get_collection("creative_innovation")
        
        # Filter by cost preference
        filtered = [c for c in purpose_collections if c.cost_profile == cost_preference]
        if filtered:
            return filtered[0]
        
        # Return first available for purpose
        return purpose_collections[0]

def create_default_model_collections() -> OpenRouterModelCollections:
    """Create and return the default model collections manager."""
    return OpenRouterModelCollections()