"""
Dynamic Query Variation Module for ISEE Framework

This module provides intelligent, context-sensitive query variation generation
using LLM analysis to replace static template-based approaches.
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from uuid import uuid4
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class QueryAnalysis:
    """Results from LLM-based query analysis."""
    complexity_level: str  # 'simple', 'moderate', 'complex', 'highly_structured'
    topic_domain: str
    tone: str  # 'academic', 'practical', 'creative', 'technical'
    structure_type: str  # 'open_ended', 'specific_research', 'structured_inquiry'
    key_concepts: List[str]
    should_vary: bool  # Whether variations are recommended
    protective_mode: bool  # Whether to use minimal/careful variations
    confidence: float  # Analysis confidence (0.0-1.0)

@dataclass
class QueryVariation:
    """A generated query variation with metadata."""
    id: str
    text: str
    strategy: str  # 'perspective_shift', 'scope_variation', 'protective'
    confidence: float
    analysis_used: QueryAnalysis

class DynamicQueryVariator:
    """
    Intelligent query variation generator using LLM analysis.
    
    Replaces static template-based approach with context-sensitive
    variation generation that respects query complexity and structure.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the dynamic query variator.
        
        Args:
            api_key: OpenRouter API key. If None, reads from environment.
        """
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.analysis_model = "anthropic/claude-3.5-haiku"  # Fast, cost-efficient
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        if not self.api_key:
            logger.warning("No OpenRouter API key found. Variations will fall back to original query.")
    
    def analyze_query(self, query_text: str) -> QueryAnalysis:
        """
        Analyze query using LLM to determine complexity, domain, and variation approach.
        
        Args:
            query_text: The query to analyze
            
        Returns:
            QueryAnalysis with recommendations for variation approach
        """
        if not self.api_key:
            return self._fallback_analysis(query_text)
        
        analysis_prompt = f"""Analyze this query for intelligent variation generation:

QUERY: "{query_text}"

Provide analysis in this exact JSON format:
{{
    "complexity_level": "simple|moderate|complex|highly_structured",
    "topic_domain": "brief domain description",
    "tone": "academic|practical|creative|technical",
    "structure_type": "open_ended|specific_research|structured_inquiry",
    "key_concepts": ["concept1", "concept2", "concept3"],
    "should_vary": true/false,
    "protective_mode": true/false,
    "confidence": 0.0-1.0
}}

Guidelines:
- simple: Basic questions, straightforward language
- moderate: Some specificity but flexible structure  
- complex: Multiple components, careful phrasing
- highly_structured: Precise language, specific methodology, formal research

- should_vary: false for highly structured or sensitive queries
- protective_mode: true for complex queries that need minimal changes
- confidence: how certain you are about the analysis

Focus on preserving the user's intent and careful wording."""

        try:
            response = self._call_llm(analysis_prompt, max_tokens=500, temperature=0.1)
            analysis_data = json.loads(response)
            
            return QueryAnalysis(
                complexity_level=analysis_data.get('complexity_level', 'moderate'),
                topic_domain=analysis_data.get('topic_domain', 'general'),
                tone=analysis_data.get('tone', 'practical'),
                structure_type=analysis_data.get('structure_type', 'open_ended'),
                key_concepts=analysis_data.get('key_concepts', []),
                should_vary=analysis_data.get('should_vary', True),
                protective_mode=analysis_data.get('protective_mode', False),
                confidence=analysis_data.get('confidence', 0.7)
            )
            
        except Exception as e:
            logger.warning(f"Query analysis failed: {e}. Using fallback analysis.")
            return self._fallback_analysis(query_text)
    
    def generate_variations(self, query_text: str, max_variations: int = 2) -> List[QueryVariation]:
        """
        Generate intelligent, context-sensitive query variations.
        
        Args:
            query_text: Original query text
            max_variations: Maximum number of variations to generate
            
        Returns:
            List of QueryVariation objects
        """
        # First analyze the query
        analysis = self.analyze_query(query_text)
        
        # If analysis recommends no variations, return empty list
        if not analysis.should_vary:
            logger.info(f"Analysis recommends no variations for query: {query_text[:50]}...")
            return []
        
        variations = []
        
        # Generate variations based on analysis
        if analysis.protective_mode:
            # Use minimal, careful variations for complex queries
            variations.extend(self._generate_protective_variations(query_text, analysis, max_variations))
        else:
            # Use full variation strategies for simpler queries
            strategies = ['perspective_shift', 'scope_variation'][:max_variations]
            
            for strategy in strategies:
                try:
                    variation = self._generate_variation_by_strategy(query_text, analysis, strategy)
                    if variation:
                        variations.append(variation)
                except Exception as e:
                    logger.warning(f"Variation generation failed for strategy {strategy}: {e}")
                    continue
        
        return variations[:max_variations]
    
    def _generate_variation_by_strategy(self, query_text: str, analysis: QueryAnalysis, strategy: str) -> Optional[QueryVariation]:
        """Generate a single variation using specified strategy."""
        if not self.api_key:
            return None
        
        if strategy == 'perspective_shift':
            return self._generate_perspective_variation(query_text, analysis)
        elif strategy == 'scope_variation':
            return self._generate_scope_variation(query_text, analysis)
        else:
            logger.warning(f"Unknown strategy: {strategy}")
            return None
    
    def _generate_perspective_variation(self, query_text: str, analysis: QueryAnalysis) -> Optional[QueryVariation]:
        """Generate a perspective shift variation."""
        perspective_prompt = f"""Create a thoughtful perspective variation of this query:

ORIGINAL: "{query_text}"
DOMAIN: {analysis.topic_domain}
TONE: {analysis.tone}
KEY CONCEPTS: {', '.join(analysis.key_concepts)}

Generate ONE perspective shift variation that:
1. Maintains the core question and intent
2. Shifts to a relevant stakeholder or contextual viewpoint
3. Uses natural, flowing language (not template-like)
4. Stays relevant to the domain: {analysis.topic_domain}
5. Avoids generic phrases like "rural communities" or "aging populations" unless directly relevant

Respond with just the variation text, no explanation."""

        try:
            variation_text = self._call_llm(perspective_prompt, max_tokens=200, temperature=0.3)
            
            return QueryVariation(
                id=f"perspective_{str(uuid4())[:8]}",
                text=variation_text.strip(),
                strategy='perspective_shift',
                confidence=0.8,
                analysis_used=analysis
            )
        except Exception as e:
            logger.warning(f"Perspective variation generation failed: {e}")
            return None
    
    def _generate_scope_variation(self, query_text: str, analysis: QueryAnalysis) -> Optional[QueryVariation]:
        """Generate a scope adjustment variation."""
        scope_prompt = f"""Create a thoughtful scope variation of this query:

ORIGINAL: "{query_text}"
DOMAIN: {analysis.topic_domain}
COMPLEXITY: {analysis.complexity_level}
KEY CONCEPTS: {', '.join(analysis.key_concepts)}

Generate ONE scope variation that:
1. Maintains the core question and intent
2. Intelligently adjusts focus (narrow specific aspect OR broaden context)
3. Uses natural, flowing language
4. Stays highly relevant to: {analysis.topic_domain}
5. Avoids generic contexts unless directly relevant to the topic

Respond with just the variation text, no explanation."""

        try:
            variation_text = self._call_llm(scope_prompt, max_tokens=200, temperature=0.3)
            
            return QueryVariation(
                id=f"scope_{str(uuid4())[:8]}",
                text=variation_text.strip(),
                strategy='scope_variation',
                confidence=0.8,
                analysis_used=analysis
            )
        except Exception as e:
            logger.warning(f"Scope variation generation failed: {e}")
            return None
    
    def _generate_protective_variations(self, query_text: str, analysis: QueryAnalysis, max_variations: int) -> List[QueryVariation]:
        """Generate minimal, careful variations for complex/structured queries."""
        if not self.api_key:
            return []
        
        protective_prompt = f"""Create minimal, careful variations of this complex query:

ORIGINAL: "{query_text}"
COMPLEXITY: {analysis.complexity_level}
STRUCTURE: {analysis.structure_type}

Generate {max_variations} very careful variations that:
1. Preserve the exact intent and methodology
2. Make only subtle adjustments to phrasing
3. Maintain all specific terminology
4. Keep the same level of precision
5. Do NOT change the fundamental approach or scope

Format as JSON array: ["variation1", "variation2"]
Respond with just the JSON, no explanation."""

        try:
            response = self._call_llm(protective_prompt, max_tokens=300, temperature=0.1)
            variation_texts = json.loads(response)
            
            variations = []
            for i, text in enumerate(variation_texts[:max_variations]):
                variations.append(QueryVariation(
                    id=f"protective_{i}_{str(uuid4())[:8]}",
                    text=text.strip(),
                    strategy='protective',
                    confidence=0.9,
                    analysis_used=analysis
                ))
            
            return variations
            
        except Exception as e:
            logger.warning(f"Protective variation generation failed: {e}")
            return []
    
    def _call_llm(self, prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> str:
        """Make a call to the LLM via OpenRouter."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.analysis_model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "timeout": 30  # Prevent long waits
        }
        
        response = requests.post(self.base_url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def _fallback_analysis(self, query_text: str) -> QueryAnalysis:
        """Provide fallback analysis when LLM is unavailable."""
        # Simple heuristic-based analysis
        word_count = len(query_text.split())
        has_technical_terms = any(term in query_text.lower() for term in 
                                ['methodology', 'framework', 'implementation', 'systematic', 'comprehensive'])
        has_specific_domains = any(domain in query_text.lower() for domain in 
                                 ['blockchain', 'quantum', 'neural', 'algorithm', 'protocol'])
        
        if word_count > 30 or has_technical_terms:
            complexity = 'complex'
            protective = True
            should_vary = False
        elif word_count > 15 or has_specific_domains:
            complexity = 'moderate'
            protective = False
            should_vary = True
        else:
            complexity = 'simple'
            protective = False
            should_vary = True
        
        return QueryAnalysis(
            complexity_level=complexity,
            topic_domain='general',
            tone='practical',
            structure_type='open_ended',
            key_concepts=[],
            should_vary=should_vary,
            protective_mode=protective,
            confidence=0.5
        )

# Factory function for backwards compatibility with existing query_generator.py
def create_dynamic_variator() -> DynamicQueryVariator:
    """Create a dynamic query variator instance."""
    return DynamicQueryVariator()

# Test function for development and validation
def test_variation_system():
    """Test the dynamic variation system with sample queries."""
    variator = DynamicQueryVariator()
    
    test_queries = [
        "How might we improve urban transportation?",
        "What are the implications of implementing a comprehensive blockchain-based formal verification methodology for smart contract security auditing?",
        "How can we make education more engaging for children?",
        "What strategies should we employ to systematically integrate quantum computing protocols with existing cybersecurity frameworks while maintaining backwards compatibility?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"TESTING: {query}")
        print(f"{'='*60}")
        
        analysis = variator.analyze_query(query)
        print(f"Analysis: {analysis}")
        
        variations = variator.generate_variations(query, max_variations=2)
        print(f"\nGenerated {len(variations)} variations:")
        for i, var in enumerate(variations, 1):
            print(f"{i}. {var.text}")
            print(f"   Strategy: {var.strategy}, Confidence: {var.confidence}")

if __name__ == "__main__":
    test_variation_system()