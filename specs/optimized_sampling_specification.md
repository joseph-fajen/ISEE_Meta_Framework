# Specification Document: ISEE Framework Optimization

## Executive Summary

This document outlines a plan to optimize the Idea Synthesis and Extraction Engine (ISEE) framework by reducing the computational and time requirements while maintaining the quality and diversity of generated ideas. The current implementation requires hundreds of API calls, resulting in extended run times (up to 3 hours for 210 calls). We propose implementing a more efficient combination selection algorithm that can deliver comparable results with approximately 36 API calls.

## Problem Statement

The current exhaustive approach to combination generation in the ISEE framework is computationally expensive and time-consuming. Running all possible combinations of models, instructions, queries, and domains can require hundreds of API calls, leading to:

1. Extended run times (approximately 3 hours on an M1 MacBook Pro)
2. Higher API costs for commercial models
3. Potential rate limiting issues
4. Reduced iterations for experimentation

## Proposed Solution

We recommend implementing a three-phase approach to optimize the combination selection process:

### Phase 1: Stratified Random Sampling (Base Implementation)

Implement a stratified random sampling algorithm that ensures representation across all key dimensions while drastically reducing total combinations.

**Key Features:**
- Guarantees each model, instruction type, and domain appears at least once
- Maintains randomness to explore different combinations
- Configurable maximum combination limit
- Simple implementation with immediate benefits

### Phase 2: Adaptive Sequential Sampling (Enhancement)

Enhance the framework with an adaptive approach that learns from initial results and focuses remaining resources on promising areas.

**Key Features:**
- Two-stage execution process
- Initial diverse sampling (50% of budget)
- Analysis of initial results to identify high-performing combinations
- Focused exploration of variations on top performers for remaining budget
- Optimizes resource allocation based on real-time performance

### Phase 3: Historical Performance Database (Future Work)

Develop a performance tracking system to guide future combination selection based on historical data.

**Key Features:**
- Database to track performance of combinations across runs
- Model-quality weighted sampling based on historical performance
- Continuous improvement of sampling strategy over time
- Balance between exploration of new combinations and exploitation of known high performers

## Technical Implementation Details

### Phase 1: Stratified Random Sampling

```python
def stratified_random_sampling(models, instructions, queries, domains, max_combinations=36):
    # Ensure representation across all key dimensions
    combinations = []
    
    # 1. First, ensure each model is represented
    for model in models:
        instruction = random.choice(instructions)
        query = random.choice(queries)
        domain = random.choice(domains)
        combinations.append((model, instruction, query, domain))
    
    # 2. Then ensure each instruction is represented
    for instruction in instructions:
        if len(combinations) >= max_combinations:
            break
        if not any(i == instruction for _, i, _, _ in combinations):
            model = random.choice(models)
            query = random.choice(queries)
            domain = random.choice(domains)
            combinations.append((model, instruction, query, domain))
    
    # 3. Ensure each domain is represented
    for domain in domains:
        if len(combinations) >= max_combinations:
            break
        if not any(d == domain for _, _, _, d in combinations):
            model = random.choice(models)
            instruction = random.choice(instructions)
            query = random.choice(queries)
            combinations.append((model, instruction, query, domain))
    
    # 4. Add random combinations until reaching max_combinations
    remaining_slots = max_combinations - len(combinations)
    for _ in range(remaining_slots):
        model = random.choice(models)
        instruction = random.choice(instructions)
        query = random.choice(queries)
        domain = random.choice(domains)
        combinations.append((model, instruction, query, domain))
    
    return combinations
```

### Phase 2: Adaptive Sequential Sampling

```python
def adaptive_sequential_sampling(models, instructions, queries, domains, max_combinations=36):
    # Phase 1: Initial diverse sampling (around 50% of budget)
    initial_count = max_combinations // 2
    initial_combinations = stratified_random_sampling(
        models, instructions, queries, domains, max_combinations=initial_count
    )
    
    # Run these combinations and get results
    results = run_combinations(initial_combinations)
    
    # Phase 2: Analyze results to determine promising areas
    performance = defaultdict(float)
    for combo, score in zip(initial_combinations, results):
        model, instruction, _, _ = combo
        performance[(model, instruction)] += score
    
    # Select top performing combinations
    top_combos = sorted(performance.items(), key=lambda x: x[1], reverse=True)[:4]
    top_models_instructions = [combo[0] for combo in top_combos]
    
    # Phase 3: Explore variations on top performers for remaining budget
    remaining_count = max_combinations - initial_count
    additional_combinations = []
    
    for model, instruction in top_models_instructions:
        # Explore different queries and domains with this model+instruction
        for _ in range(remaining_count // len(top_models_instructions)):
            query = random.choice(queries)
            domain = random.choice(domains)
            additional_combinations.append((model, instruction, query, domain))
    
    return initial_combinations + additional_combinations
```

### Phase 3: Historical Performance Database

```python
class PerformanceTracker:
    def __init__(self, db_path="performance_history.db"):
        self.db_path = db_path
        self._initialize_db()
        
    def _initialize_db(self):
        # Create SQLite database with appropriate schema
        # Tables for models, instructions, combinations, and performance metrics
        pass
        
    def record_performance(self, combination, score):
        # Record performance of a combination in the database
        pass
        
    def get_model_weights(self):
        # Calculate performance weights for models based on historical data
        pass
        
    def get_instruction_weights(self):
        # Calculate performance weights for instructions based on historical data
        pass
        
    def get_top_combinations(self, limit=10):
        # Get top performing combinations
        pass
```

## Implementation Plan

### Phase 1 (1-2 Weeks)
1. Implement the stratified random sampling algorithm
2. Add configuration option to set maximum combinations
3. Integrate with current pipeline
4. Test with various combination sizes (18, 36, 54)
5. Compare results with exhaustive approach

### Phase 2 (2-3 Weeks)
1. Implement the adaptive sequential sampling algorithm
2. Refactor pipeline to support two-stage execution
3. Add analysis logic for initial results
4. Implement strategy for selecting additional combinations
5. Test effectiveness compared to Phase 1

### Phase 3 (3-4 Weeks)
1. Design and implement performance tracking database
2. Add logging for combination performance
3. Implement model-quality weighted sampling
4. Create analysis tools for historical performance
5. Test long-term improvement in idea quality

## Success Metrics

1. **Efficiency**: Reduce run time by at least 80% compared to exhaustive approach
2. **Quality Preservation**: Maintain at least 90% of the idea quality compared to exhaustive approach
3. **Diversity**: Ensure representation of all models, instruction types, and domains
4. **User Experience**: Improve iteration speed for researchers using the framework

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Quality degradation with fewer combinations | High | Conduct comparative analysis between exhaustive and optimized approaches; allow users to adjust combination count based on quality needs |
| Selection bias toward certain combinations | Medium | Implement diversity constraints; periodically include random combinations to explore new areas |
| Complexity of adaptive algorithm | Medium | Start with simpler stratified approach; add adaptive features incrementally |
| Database overhead for small projects | Low | Make historical tracking optional; provide simple file-based storage for small projects |

## Future Considerations

1. **Machine Learning Optimization**: Train a model to predict which combinations will yield high-quality ideas
2. **User Interface**: Develop visualization tools for combination selection and performance
3. **API Cost Optimization**: Implement budget-aware selection that considers API costs for different models
4. **Parallel Execution**: Support parallel API calls to further reduce runtime

## Appendix: Command-Line Interface Updates

```bash
# Current command
python main.py --config unified_config.json --query "What services..." --models 7 --instructions 10 --variations 3 --max-combinations 210 --balanced-models --synthesize-method cluster_based

# Proposed command with new options
python main.py --config unified_config.json --query "What services..." --sampling-method stratified --max-combinations 36 --balanced-models --synthesize-method cluster_based

# Future adaptive sampling command
python main.py --config unified_config.json --query "What services..." --sampling-method adaptive --max-combinations 36 --adaptive-ratio 0.5 --use-history --synthesize-method cluster_based
```

This specification provides a clear roadmap for optimizing the ISEE framework's combination selection process while maintaining its core value proposition of diverse, high-quality idea synthesis.
