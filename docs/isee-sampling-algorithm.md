# ISEE Sampling Algorithm: Fair Stratified Selection

## Overview

When users select parameters that could generate hundreds or even thousands of potential LLM combinations, ISEE employs a sophisticated **Fair Stratified Sampling Algorithm** to select a representative subset while maximizing cognitive diversity. This document explains how ISEE intelligently chooses which combinations to execute from the vast possibility space.

## The Sampling Challenge

### Example Scenario
- **User Selection**: 5 models × 4 frameworks × 6 variations × 4 domains = **480 potential combinations**
- **Computational Limit**: `max_combinations = 48`
- **Challenge**: Which 48 combinations should ISEE execute to maximize insight diversity?

### Naive Approaches (What ISEE Doesn't Do)
❌ **Simple Random Sampling**: Could result in 35 Analytical + 10 Creative + 3 Critical + 0 Systems  
❌ **First-N Selection**: Would only use combinations from early frameworks  
❌ **Round-Robin**: Doesn't account for uneven parameter distributions  

## ISEE's Two-Stage Solution

### Stage 1: Exhaustive Generation

**Location**: `main.py`, function `generate_combinations()` (lines 392-407)

ISEE first generates **all possible combinations** to understand the complete search space:

```python
# Exhaustive combination generation
all_combinations = []
for template in templates:          # Cognitive frameworks
    for domain in domains:          # Knowledge domains  
        for query in all_queries:   # Query variations
            for model in models:    # LLM models
                combination = {
                    "id": f"{model}_{template.id}_{query.id}_{domain.id}",
                    "model": model,
                    "template": template.id,
                    "query": query.id,
                    "domain": domain.id,
                    "metadata": {
                        "framework_name": template.name,
                        "domain_name": domain.name,
                        "query_type": query.type
                    }
                }
                all_combinations.append(combination)
```

**Result**: Complete enumeration of the possibility space (e.g., 480 combinations)

### Stage 2: Fair Stratified Sampling

**Location**: `main.py`, function `generate_combinations()` (lines 409-443)

When combinations exceed the limit, ISEE applies **cognitive framework-first stratification**:

```python
if len(all_combinations) > max_combinations:
    import random
    random.seed(42)  # Ensures reproducible results
    
    # PRIMARY STRATIFICATION: Group by cognitive framework
    framework_groups = {}
    for combo in all_combinations:
        framework_id = combo['template']
        framework_groups.setdefault(framework_id, []).append(combo)
    
    # EQUAL ALLOCATION: Calculate combinations per framework
    combinations_per_framework = max_combinations // len(frameworks)
    remainder = max_combinations % len(frameworks)
    
    selected_combinations = []
    
    # FAIR DISTRIBUTION: Ensure each framework is represented
    for i, (framework_id, framework_combos) in enumerate(framework_groups.items()):
        # Distribute remainder fairly across frameworks
        framework_limit = combinations_per_framework + (1 if i < remainder else 0)
        
        if len(framework_combos) <= framework_limit:
            # Use all combinations if fewer than limit
            selected_combinations.extend(framework_combos)
        else:
            # RANDOM SAMPLING: Within framework, randomly select
            sampled = random.sample(framework_combos, framework_limit)
            selected_combinations.extend(sampled)
    
    return selected_combinations
```

## Algorithm Features

### 1. Cognitive Diversity Prioritization

**Framework-First Stratification**:
- Primary grouping by cognitive framework ensures each thinking style is represented
- Equal allocation across frameworks prevents dominance by any single approach
- Remainder distribution ensures perfect utilization of the combination budget

**Example Distribution** (48 combinations, 4 frameworks):
```
Analytical Framework:   12 combinations (guaranteed)
Creative Framework:     12 combinations (guaranteed)
Critical Framework:     12 combinations (guaranteed)
Systems Framework:      12 combinations (guaranteed)
Total:                  48 combinations (perfect utilization)
```

### 2. Fair Random Sampling

**Within-Framework Selection**:
- After framework allocation, random sampling ensures fair representation of models, domains, and query variations
- **Fixed random seed (42)** provides reproducible results
- Same input parameters always generate the same representative sample

**Sampling Logic**:
```python
# Within each framework group
for framework_combos in framework_groups.values():
    # Randomly select from: models × domains × query_variations
    # Ensures no bias toward specific models or domains
    sampled = random.sample(framework_combos, framework_limit)
```

### 3. Scalable Efficiency

**Adaptive Limits**:
- **Web UI Default**: 24 combinations (quick exploration)
- **CLI Standard**: 48 combinations (balanced analysis)
- **Comprehensive**: 100+ combinations (deep research)
- **Maximum**: 400+ combinations (exhaustive analysis)

**Hardware-Aware Guardrails**:
```python
# From main.py lines 1303-1467
class ISEEGuardrails:
    DEVICE_LIMITS = {
        "laptop": {"max_combinations": 100},
        "workstation": {"max_combinations": 500}
    }
```

## Model Provider Diversity

**Location**: `main.py`, function `generate_combinations()` (lines 314-355)

ISEE also ensures diversity across AI model providers:

```python
# Prioritize diversity across providers
provider_models = {}
for model_id in selected_models:
    provider = determine_provider(model_config)  # anthropic, openai, google, etc.
    provider_models.setdefault(provider, []).append(model_id)

# Ensure representation from each provider
selected_models_list = []
# First pass: select one model from each provider
for provider in provider_models:
    if len(selected_models_list) < model_count:
        selected_models_list.append(provider_models[provider][0])

# Second pass: cycle through providers for additional models
# Prevents single provider from dominating the model selection
```

## Real-World Example

### Input Parameters
- **Models**: 5 selected (Claude, GPT-4, Gemini, Llama, Mistral)
- **Frameworks**: 4 selected (Analytical, Creative, Critical, Systems)
- **Query Variations**: 3 (Original, Rephrased, Context-Enhanced)
- **Domains**: 4 selected (Education, Technology, Strategy, Innovation)
- **Total Combinations**: 5 × 4 × 3 × 4 = **240 combinations**
- **Limit**: `max_combinations = 48`

### Sampling Process

1. **Exhaustive Generation**: Create all 240 combinations
2. **Framework Stratification**: Group into 4 framework buckets of 60 combinations each
3. **Equal Allocation**: 48 ÷ 4 = 12 combinations per framework
4. **Random Selection**: From each framework's 60 combinations, randomly select 12
5. **Result**: 48 combinations with guaranteed cognitive diversity

### Final Distribution
```
Analytical Framework:   12 combinations (models/domains/variations randomized)
Creative Framework:     12 combinations (models/domains/variations randomized)  
Critical Framework:     12 combinations (models/domains/variations randomized)
Systems Framework:      12 combinations (models/domains/variations randomized)
```

## Key Benefits

### ✅ Guaranteed Cognitive Coverage
- **Every selected framework** appears in the final sample
- No risk of missing entire thinking approaches
- Balanced perspective across all cognitive styles

### ✅ Fair Model Representation  
- Random sampling within frameworks ensures all models can appear
- Provider diversity prevents single vendor dominance
- Equal opportunity for each selected model

### ✅ Reproducible Results
- **Fixed random seed** ensures identical sampling for same inputs
- Enables reliable testing, debugging, and result comparison
- Consistent behavior across different execution environments

### ✅ Scalable Efficiency
- Same algorithm works from 12 to 400+ combinations
- Linear scaling with framework count
- Efficient memory usage through streaming generation

### ✅ Research Integrity
- **Stratified sampling** is a gold-standard statistical method
- Maintains scientific rigor in combination selection
- Provides defensible methodology for research applications

## Manager Explanation

**The Research Director Analogy**:

*"ISEE acts like a research director assembling a diverse expert panel for a study. Instead of randomly picking researchers (which might accidentally select 35 from Psychology and 0 from Sociology), ISEE ensures equal representation from each department (cognitive framework), then randomly selects specific experts within each department.*

*This guarantees we get balanced perspectives from all thinking styles while staying within our budget constraints. The result is a systematically diverse team that explores the problem space comprehensively rather than accidentally focusing on just one approach."*

## Technical Implementation

### Core Files
| Component | File | Key Functions |
|-----------|------|---------------|
| Combination Generation | `main.py` | `generate_combinations()` (lines 203-449) |
| Stratified Sampling | `main.py` | Framework grouping and allocation logic |
| Provider Diversity | `main.py` | Model selection with provider balancing |
| Guardrails | `main.py` | `ISEEGuardrails` class (lines 1303-1467) |
| Web UI Integration | `app.py` | Parameter conversion and limit management |

### Configuration Points
- `max_combinations`: Primary sampling limit
- `random.seed(42)`: Reproducibility control  
- Framework selection: Determines stratification groups
- Model selection: Influences within-group diversity

## Conclusion

ISEE's Fair Stratified Sampling Algorithm ensures that computational constraints don't compromise cognitive diversity. By prioritizing framework representation and applying fair random sampling within cognitive groups, ISEE delivers systematically diverse insights that would be difficult to achieve through simple random selection or naive filtering approaches.

This approach reflects ISEE's core philosophy: **cognitive diversity over raw coverage** - it's better to have balanced perspectives from 48 carefully selected combinations than random perspectives from 48 accidentally similar ones.