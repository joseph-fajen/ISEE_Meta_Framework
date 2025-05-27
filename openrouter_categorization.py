"""
OpenRouter Model Categorization System

This module provides intelligent categorization and filtering capabilities for OpenRouter's 300+ models.
It enables users to filter models by provider, capabilities, cost tiers, use cases, and more.

Part of OpenRouter Integration - Stage 1: Model Categorization
"""

from typing import Dict, Any, List, Optional, Set, Tuple
import re
from dataclasses import dataclass
from enum import Enum

class ProviderCategory(Enum):
    """Major AI model providers available through OpenRouter."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai" 
    GOOGLE = "google"
    META = "meta-llama"
    MISTRAL = "mistralai"
    COHERE = "cohere"
    AI21 = "ai21"
    TOGETHER = "togetherai"
    FIREWORKS = "fireworks"
    PERPLEXITY = "perplexityai"
    HUGGINGFACE = "huggingfaceh4"
    REPLICATE = "replicate"
    ANYSCALE = "anyscale"
    DEEPINFRA = "deepinfra"
    OTHER = "other"

class CapabilityCategory(Enum):
    """Model capabilities based on architecture and training."""
    REASONING = "reasoning"
    CREATIVE = "creative"
    CODING = "coding"
    ANALYSIS = "analysis"
    MULTIMODAL = "multimodal"
    LARGE_CONTEXT = "large_context"
    FAST = "fast"
    INSTRUCTION_FOLLOWING = "instruction_following"
    CONVERSATIONAL = "conversational"
    RAG_OPTIMIZED = "rag_optimized"

class CostTier(Enum):
    """Cost tiers based on pricing analysis."""
    FREE = "free"
    BUDGET = "budget"         # < $1 per 1M tokens
    STANDARD = "standard"     # $1-10 per 1M tokens  
    PREMIUM = "premium"       # $10-50 per 1M tokens
    PREMIUM_PLUS = "premium_plus"  # > $50 per 1M tokens

class UseCase(Enum):
    """Common use cases for ISEE framework."""
    CONTENT_CREATION = "content_creation"
    DEEP_ANALYSIS = "deep_analysis"
    QUICK_EXPLORATION = "quick_exploration"
    PROBLEM_SOLVING = "problem_solving"
    CREATIVE_INNOVATION = "creative_innovation"
    LEARNING_DESIGN = "learning_design"
    STRATEGIC_PLANNING = "strategic_planning"
    CODE_GENERATION = "code_generation"
    RESEARCH = "research"
    SYNTHESIS = "synthesis"

@dataclass
class ModelMetadata:
    """Rich metadata for a model including categorizations."""
    id: str
    name: str
    provider: ProviderCategory
    description: str
    capabilities: Set[CapabilityCategory]
    cost_tier: CostTier
    use_cases: Set[UseCase]
    context_length: int
    pricing: Dict[str, float]
    quality_score: float  # 1-10 subjective quality rating
    speed_tier: str       # "fast", "medium", "slow"
    architecture: str
    
class OpenRouterCategorizer:
    """Intelligent categorization system for OpenRouter models."""
    
    def __init__(self):
        """Initialize the categorization system with pattern matching rules."""
        self.provider_patterns = self._build_provider_patterns()
        self.capability_patterns = self._build_capability_patterns()
        self.use_case_mappings = self._build_use_case_mappings()
        
    def categorize_model(self, model_data: Dict[str, Any]) -> ModelMetadata:
        """Categorize a single model from OpenRouter API response.
        
        Args:
            model_data: Raw model data from OpenRouter API
            
        Returns:
            ModelMetadata with rich categorization information
        """
        model_id = model_data.get("id", "")
        model_name = model_data.get("name", "")
        description = model_data.get("description", "")
        
        # Extract provider from model ID
        provider = self._extract_provider(model_id)
        
        # Analyze capabilities from name, description, and metadata
        capabilities = self._analyze_capabilities(model_id, model_name, description, model_data)
        
        # Determine cost tier from pricing
        cost_tier = self._determine_cost_tier(model_data.get("pricing", {}))
        
        # Map to use cases based on capabilities and provider
        use_cases = self._map_use_cases(capabilities, provider)
        
        # Extract technical details
        context_length = model_data.get("context_length", 4096)
        pricing = self._normalize_pricing(model_data.get("pricing", {}))
        
        # Assign quality score based on provider and model tier
        quality_score = self._assign_quality_score(provider, model_id, model_name)
        
        # Determine speed tier
        speed_tier = self._determine_speed_tier(model_id, model_name, capabilities)
        
        return ModelMetadata(
            id=model_id,
            name=model_name,
            provider=provider,
            description=description,
            capabilities=capabilities,
            cost_tier=cost_tier,
            use_cases=use_cases,
            context_length=context_length,
            pricing=pricing,
            quality_score=quality_score,
            speed_tier=speed_tier,
            architecture=model_data.get("architecture", "unknown")
        )
    
    def filter_models(self, 
                     models: List[ModelMetadata],
                     providers: Optional[List[ProviderCategory]] = None,
                     capabilities: Optional[List[CapabilityCategory]] = None,
                     cost_tiers: Optional[List[CostTier]] = None,
                     use_cases: Optional[List[UseCase]] = None,
                     min_context_length: Optional[int] = None,
                     max_cost_per_million: Optional[float] = None,
                     min_quality_score: Optional[float] = None) -> List[ModelMetadata]:
        """Filter models based on multiple criteria.
        
        Args:
            models: List of categorized models
            providers: Filter by providers
            capabilities: Filter by required capabilities
            cost_tiers: Filter by cost tiers
            use_cases: Filter by use cases
            min_context_length: Minimum context window
            max_cost_per_million: Maximum cost per million tokens
            min_quality_score: Minimum quality score
            
        Returns:
            Filtered list of models
        """
        filtered = models
        
        if providers:
            filtered = [m for m in filtered if m.provider in providers]
            
        if capabilities:
            filtered = [m for m in filtered if any(cap in m.capabilities for cap in capabilities)]
            
        if cost_tiers:
            filtered = [m for m in filtered if m.cost_tier in cost_tiers]
            
        if use_cases:
            filtered = [m for m in filtered if any(uc in m.use_cases for uc in use_cases)]
            
        if min_context_length:
            filtered = [m for m in filtered if m.context_length >= min_context_length]
            
        if max_cost_per_million:
            filtered = [m for m in filtered 
                       if m.pricing.get("completion", float('inf')) <= max_cost_per_million]
            
        if min_quality_score:
            filtered = [m for m in filtered if m.quality_score >= min_quality_score]
            
        return filtered
    
    def get_recommended_models(self, 
                              use_case: UseCase,
                              budget_tier: CostTier = CostTier.STANDARD,
                              min_quality: float = 7.0,
                              diversity_providers: int = 3) -> List[ModelMetadata]:
        """Get recommended models for a specific use case with quality and diversity constraints.
        
        Args:
            use_case: Target use case
            budget_tier: Maximum cost tier
            min_quality: Minimum quality score
            diversity_providers: Number of different providers to include
            
        Returns:
            Recommended models list
        """
        # This would use a full model list, for now return empty
        # Will be implemented when integrated with OpenRouterClient
        return []
    
    def _build_provider_patterns(self) -> Dict[str, ProviderCategory]:
        """Build patterns to extract provider from model ID."""
        return {
            "anthropic/": ProviderCategory.ANTHROPIC,
            "openai/": ProviderCategory.OPENAI,
            "google/": ProviderCategory.GOOGLE,
            "meta-llama/": ProviderCategory.META,
            "mistralai/": ProviderCategory.MISTRAL,
            "cohere/": ProviderCategory.COHERE,
            "ai21/": ProviderCategory.AI21,
            "togetherai/": ProviderCategory.TOGETHER,
            "fireworks/": ProviderCategory.FIREWORKS,
            "perplexityai/": ProviderCategory.PERPLEXITY,
            "huggingfaceh4/": ProviderCategory.HUGGINGFACE,
            "replicate/": ProviderCategory.REPLICATE,
            "anyscale/": ProviderCategory.ANYSCALE,
            "deepinfra/": ProviderCategory.DEEPINFRA,
        }
    
    def _build_capability_patterns(self) -> Dict[str, Set[CapabilityCategory]]:
        """Build patterns to detect capabilities from model names/descriptions."""
        return {
            # Reasoning indicators
            "reasoning": {CapabilityCategory.REASONING, CapabilityCategory.ANALYSIS},
            "logic": {CapabilityCategory.REASONING},
            "analysis": {CapabilityCategory.ANALYSIS, CapabilityCategory.REASONING},
            "think": {CapabilityCategory.REASONING},
            
            # Creative indicators  
            "creative": {CapabilityCategory.CREATIVE},
            "art": {CapabilityCategory.CREATIVE, CapabilityCategory.MULTIMODAL},
            "story": {CapabilityCategory.CREATIVE},
            "writing": {CapabilityCategory.CREATIVE},
            
            # Coding indicators
            "code": {CapabilityCategory.CODING},
            "python": {CapabilityCategory.CODING},
            "programming": {CapabilityCategory.CODING},
            "codellama": {CapabilityCategory.CODING},
            
            # Speed indicators
            "turbo": {CapabilityCategory.FAST},
            "fast": {CapabilityCategory.FAST},
            "mini": {CapabilityCategory.FAST},
            "3.5": {CapabilityCategory.FAST},
            
            # Context indicators
            "32k": {CapabilityCategory.LARGE_CONTEXT},
            "128k": {CapabilityCategory.LARGE_CONTEXT},
            "200k": {CapabilityCategory.LARGE_CONTEXT},
            "long": {CapabilityCategory.LARGE_CONTEXT},
            
            # Multimodal indicators
            "vision": {CapabilityCategory.MULTIMODAL},
            "image": {CapabilityCategory.MULTIMODAL},
            "multimodal": {CapabilityCategory.MULTIMODAL},
            
            # RAG and instruction following
            "instruct": {CapabilityCategory.INSTRUCTION_FOLLOWING},
            "chat": {CapabilityCategory.CONVERSATIONAL, CapabilityCategory.INSTRUCTION_FOLLOWING},
            "command": {CapabilityCategory.RAG_OPTIMIZED, CapabilityCategory.INSTRUCTION_FOLLOWING},
        }
    
    def _build_use_case_mappings(self) -> Dict[CapabilityCategory, Set[UseCase]]:
        """Map capabilities to appropriate use cases."""
        return {
            CapabilityCategory.REASONING: {
                UseCase.DEEP_ANALYSIS, UseCase.PROBLEM_SOLVING, 
                UseCase.STRATEGIC_PLANNING, UseCase.RESEARCH
            },
            CapabilityCategory.CREATIVE: {
                UseCase.CONTENT_CREATION, UseCase.CREATIVE_INNOVATION,
                UseCase.LEARNING_DESIGN
            },
            CapabilityCategory.CODING: {
                UseCase.CODE_GENERATION, UseCase.PROBLEM_SOLVING
            },
            CapabilityCategory.ANALYSIS: {
                UseCase.DEEP_ANALYSIS, UseCase.RESEARCH, UseCase.SYNTHESIS
            },
            CapabilityCategory.FAST: {
                UseCase.QUICK_EXPLORATION, UseCase.CONTENT_CREATION
            },
            CapabilityCategory.LARGE_CONTEXT: {
                UseCase.DEEP_ANALYSIS, UseCase.SYNTHESIS, UseCase.RESEARCH
            },
            CapabilityCategory.RAG_OPTIMIZED: {
                UseCase.RESEARCH, UseCase.SYNTHESIS, UseCase.STRATEGIC_PLANNING
            }
        }
    
    def _extract_provider(self, model_id: str) -> ProviderCategory:
        """Extract provider from model ID."""
        for pattern, provider in self.provider_patterns.items():
            if model_id.startswith(pattern):
                return provider
        return ProviderCategory.OTHER
    
    def _analyze_capabilities(self, model_id: str, model_name: str, 
                            description: str, model_data: Dict[str, Any]) -> Set[CapabilityCategory]:
        """Analyze model capabilities from various data sources."""
        capabilities = set()
        
        # Combine text sources for analysis
        text_to_analyze = f"{model_id} {model_name} {description}".lower()
        
        # Pattern matching
        for pattern, caps in self.capability_patterns.items():
            if pattern in text_to_analyze:
                capabilities.update(caps)
        
        # Context length analysis
        context_length = model_data.get("context_length", 4096)
        if context_length >= 32000:
            capabilities.add(CapabilityCategory.LARGE_CONTEXT)
        
        # Provider-specific capabilities
        provider = self._extract_provider(model_id)
        if provider == ProviderCategory.ANTHROPIC:
            capabilities.update({CapabilityCategory.REASONING, CapabilityCategory.ANALYSIS})
        elif provider == ProviderCategory.OPENAI:
            capabilities.update({CapabilityCategory.REASONING, CapabilityCategory.INSTRUCTION_FOLLOWING})
        elif provider == ProviderCategory.COHERE:
            capabilities.add(CapabilityCategory.RAG_OPTIMIZED)
            
        return capabilities
    
    def _determine_cost_tier(self, pricing: Dict[str, Any]) -> CostTier:
        """Determine cost tier from pricing information."""
        if not pricing:
            return CostTier.BUDGET
            
        # Get completion pricing (most relevant for ISEE usage)
        completion_cost_raw = pricing.get("completion", 0)
        
        # Convert to float if it's a string
        try:
            if isinstance(completion_cost_raw, str):
                # Remove currency symbols and convert
                clean_value = re.sub(r'[^\d.]', '', completion_cost_raw)
                completion_cost = float(clean_value) if clean_value else 0.0
            else:
                completion_cost = float(completion_cost_raw) if completion_cost_raw else 0.0
        except (ValueError, TypeError):
            completion_cost = 0.0
        
        if completion_cost == 0:
            return CostTier.FREE
        elif completion_cost < 1:
            return CostTier.BUDGET
        elif completion_cost < 10:
            return CostTier.STANDARD
        elif completion_cost < 50:
            return CostTier.PREMIUM
        else:
            return CostTier.PREMIUM_PLUS
    
    def _map_use_cases(self, capabilities: Set[CapabilityCategory], 
                      provider: ProviderCategory) -> Set[UseCase]:
        """Map capabilities to relevant use cases."""
        use_cases = set()
        
        for capability in capabilities:
            if capability in self.use_case_mappings:
                use_cases.update(self.use_case_mappings[capability])
        
        # Default use cases for all models
        use_cases.add(UseCase.QUICK_EXPLORATION)
        
        return use_cases
    
    def _normalize_pricing(self, pricing: Dict[str, Any]) -> Dict[str, float]:
        """Normalize pricing to consistent format (per million tokens)."""
        normalized = {}
        
        # Convert string prices to floats and normalize units
        for key, value in pricing.items():
            try:
                if isinstance(value, str):
                    # Remove currency symbols and convert
                    clean_value = re.sub(r'[^\d.]', '', value)
                    normalized[key] = float(clean_value) if clean_value else 0.0
                else:
                    normalized[key] = float(value) if value else 0.0
            except (ValueError, TypeError):
                normalized[key] = 0.0
                
        return normalized
    
    def _assign_quality_score(self, provider: ProviderCategory, 
                            model_id: str, model_name: str) -> float:
        """Assign subjective quality score based on known model performance."""
        
        # Provider-based base scores
        provider_scores = {
            ProviderCategory.ANTHROPIC: 9.0,
            ProviderCategory.OPENAI: 8.5,
            ProviderCategory.GOOGLE: 8.0,
            ProviderCategory.META: 7.5,
            ProviderCategory.MISTRAL: 7.5,
            ProviderCategory.COHERE: 7.0,
            ProviderCategory.AI21: 7.0,
            ProviderCategory.OTHER: 6.0,
        }
        
        base_score = provider_scores.get(provider, 6.0)
        
        # Model-specific adjustments
        model_text = f"{model_id} {model_name}".lower()
        
        if "opus" in model_text:
            return min(10.0, base_score + 1.0)
        elif "4-turbo" in model_text or "4o" in model_text:
            return min(10.0, base_score + 0.5)
        elif "sonnet" in model_text or "gpt-4" in model_text:
            return base_score
        elif "3.5" in model_text or "mini" in model_text:
            return max(1.0, base_score - 1.0)
        
        return base_score
    
    def _determine_speed_tier(self, model_id: str, model_name: str, 
                            capabilities: Set[CapabilityCategory]) -> str:
        """Determine speed tier based on model characteristics."""
        model_text = f"{model_id} {model_name}".lower()
        
        if (CapabilityCategory.FAST in capabilities or 
            "turbo" in model_text or "3.5" in model_text or "mini" in model_text):
            return "fast"
        elif "opus" in model_text or "4o" in model_text:
            return "medium"
        else:
            return "medium"

# Factory function for easy integration
def create_openrouter_categorizer() -> OpenRouterCategorizer:
    """Create and return an OpenRouter categorization instance."""
    return OpenRouterCategorizer()