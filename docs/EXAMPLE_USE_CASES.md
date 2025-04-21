# ISEE Framework Example Use Cases

This document provides detailed example use cases for the ISEE framework, each showcasing different aspects of the system. Follow these examples to understand the framework's capabilities and how it can be applied to various innovation challenges.

> **NEW**: All examples now include the `--balanced-models` flag to ensure optimal model diversity and prevent any single model from dominating the results. This feature distributes combinations evenly across all models and tracks their contributions in the synthesized output.

## Prerequisites

Before running any of the examples in this document, make sure to create the necessary directory structure for saving states and outputs:

```bash
# Create the required directory structure
mkdir -p data/state data/output
```

All example commands in this document assume this directory structure exists. If you encounter a `FileNotFoundError` when running any command, it's likely because these directories haven't been created yet.

## Use Case 1: Product Innovation - Reimagining Smart Home Interfaces

### Scenario
You're a product designer tasked with developing next-generation interfaces for smart home systems. You want to move beyond screen-based and voice-based interactions to create more intuitive and seamless user experiences.

### Command

```bash
python main.py \
  --config sample_config.json \
  --query "How might we create more intuitive and seamless interfaces for smart home systems beyond screens and voice?" \
  --models 3 \
  --instructions 3 \
  --variations 3 \
  --max-combinations 27 \
  --balanced-models \
  --save-state "data/state/smart_home_interfaces.json" \
  --output-file "data/output/smart_home_interfaces.md"
```

### What This Does

This command:
1. Creates 3 variations of your base query, exploring different perspectives
2. Uses all 3 models from your configuration with balanced representation
3. Applies 3 different cognitive frameworks (analytical, creative, critical, etc.)
4. Generates 27 combinations (3 models × 3 instructions × 3 query variations)
5. Ensures even distribution across all models with the `--balanced-models` flag
6. Saves the full state for future reference
7. Outputs the synthesized ideas to a markdown file with model contribution metrics

### How to Build Upon Results

After reviewing the initial output, pay special attention to the model contribution metrics to see which models contributed most to each synthesized idea.

1. **Explore specific aspects**: Focus on promising ideas from the initial run:

```bash
python main.py \
  --load-state "data/state/smart_home_interfaces.json" \
  --query "How might we use ambient environmental cues as interfaces for smart homes?" \
  --models 3 \
  --balanced-models \
  --max-combinations 15 \
  --save-state "data/state/ambient_interfaces.json"
```

2. **Try different synthesis methods and analyze model contributions**:

```bash
python main.py \
  --load-state "data/state/smart_home_interfaces.json" \
  --synthesize-method "cross_pollination" \
  --output-file "data/output/cross_pollinated_interfaces.md"
```

3. **Examine model contribution differences**:

Review the "Model Contributions" section in the metadata of each synthesized idea to see which models influenced different types of ideas. This can reveal strengths of different AI architectures in various aspects of interface design.

## Use Case 2: Addressing Climate Change in Urban Environments

### Scenario
You're working with a city planning department to develop innovative strategies for making urban areas more resilient to climate change while improving quality of life for residents.

### Command

```bash
python main.py \
  --config sample_config.json \
  --query "How might we transform urban environments to address climate change while improving quality of life?" \
  --domain "Urban Planning" \
  --models 3 \
  --instructions 5 \
  --variations 2 \
  --max-combinations 30 \
  --balanced-models \
  --save-state "data/state/climate_resilient_cities.json" \
  --output-file "data/output/climate_resilient_cities.md"
```

### What This Does

This command:
1. Focuses on the "Urban Planning" domain for relevant context
2. Uses all 3 AI models with balanced representation
3. Applies 5 different cognitive frameworks to maximize diversity of thinking
4. Creates 2 variations of the query to explore different angles
5. Generates up to 30 combinations while ensuring even model distribution
6. Uses the `--balanced-models` flag to prevent any single model from dominating
7. Saves the state and outputs the results to a markdown file with model contribution analytics

### How to Build Upon Results

After the initial exploration:

1. **Add constraints to make ideas more practical while maintaining model diversity**:

```bash
python main.py \
  --load-state "data/state/climate_resilient_cities.json" \
  --query "How might we transform urban environments to address climate change while improving quality of life, with limited budgets and minimal disruption to existing infrastructure?" \
  --models 3 \
  --balanced-models \
  --max-combinations 18 \
  --save-state "data/state/practical_climate_solutions.json"
```

2. **Export detailed ideas with model contribution data for further analysis**:

```bash
python main.py \
  --load-state "data/state/climate_resilient_cities.json" \
  --output-format json \
  --output-file "data/output/climate_solutions_detailed.json"
```

3. **Analyze which models excel at different aspects of urban planning**:

Examine the model contribution metrics in each cluster to determine if certain models are better at generating:
- Technically feasible solutions
- Innovative breakthrough concepts
- Practical implementation approaches
- Holistic ecosystem thinking

## Use Case 3: Reinventing Technical Documentation with AI

### Scenario
You're a technical documentation team lead trying to revolutionize how your company creates, maintains, and delivers documentation using AI technologies.

### Command

First preview the combinations with a dry run:

```bash
python main.py \
  --config sample_config.json \
  --query "How might we reinvent technical documentation processes and deliverables using AI?" \
  --models 3 \
  --instructions 3 \
  --variations 2 \
  --max-combinations 18 \
  --balanced-models \
  --dry-run
```

Then run the actual command with balanced model distribution:

```bash
python main.py \
  --config sample_config.json \
  --query "How might we reinvent technical documentation processes and deliverables using AI?" \
  --models 3 \
  --instructions 3 \
  --variations 2 \
  --max-combinations 18 \
  --balanced-models \
  --save-state "data/state/ai_documentation.json" \
  --output-file "data/output/ai_documentation.md"
```

### What This Does

This command:
1. Uses all 3 models with equal representation for diverse AI perspectives
2. Applies 3 different cognitive frameworks across all models
3. Creates 2 variations of the query
4. Generates 18 combinations evenly distributed across models (3 models × 3 instructions × 2 variations)
5. Uses the `--balanced-models` flag to ensure each model contributes equally
6. First previews what would run (with dry-run) to verify balanced distribution
7. Then executes with model balance, saves the state and results with model contribution analytics

### How to Build Upon Results

To maximize the value from this exploration:

1. **Evaluate the top results individually and examine model contributions**:

```bash
python result_viewer.py --state "data/state/ai_documentation.json" --interactive
```

In the interactive viewer, pay attention to which models contributed to each idea cluster. This helps identify model strengths for documentation tasks.

2. **Create a focused follow-up session with balanced model representation**:

```bash
python main.py \
  --query "How might we implement real-time collaborative editing in technical documentation with AI assistance?" \
  --models 3 \
  --instructions 2 \
  --variations 2 \
  --max-combinations 12 \
  --balanced-models \
  --save-state "data/state/collaborative_documentation.json"
```

3. **Combine insights from both sessions and analyze model contribution patterns**:

```bash
# Export both state files to markdown with model contribution data
python main.py --load-state "data/state/ai_documentation.json" --output-file "data/output/general_ai_doc.md"
python main.py --load-state "data/state/collaborative_documentation.json" --output-file "data/output/collaborative_ai_doc.md"

# Review model contribution sections in both outputs to identify:
# - Which models excel at different aspects of documentation
# - If patterns emerge across both exploration sessions
# - How model strengths align with different documentation needs
```

## Tips for Creating Your Own Use Cases

1. **Start with a clear, open-ended question** that defines your innovation challenge
2. **Always use the `--balanced-models` flag** to ensure optimal model diversity
3. **Create the necessary directory structure** before running commands:
   ```bash
   mkdir -p data/state data/output
   ```
4. **Adjust parameters based on your needs**:
   - More `--variations` for exploring different perspectives
   - More `--instructions` for diverse cognitive approaches
   - Use `--models 3` to include all available AI models
   - Set `--max-combinations` appropriately to ensure all models are included

5. **Calculate the right combination count** using this formula:
   - Total combinations = models × instructions × variations × domains
   - Ensure `--max-combinations` is at least equal to this number

6. **Use domain constraints** to focus on specific contexts
7. **Save state files** to build cumulative knowledge
8. **Use the Result Viewer** to dive deeper into specific outputs
9. **Analyze model contribution data** to understand model strengths
10. **Follow promising threads** with targeted follow-up queries
11. **Experiment with different synthesis methods** to extract maximum value

## Advanced Example: Multi-Stage Innovation Process with Model Diversity

For complex innovation challenges, consider a multi-stage process that maintains model diversity throughout:

```bash
# Stage 1: Broad exploration with balanced model representation
python main.py \
  --config sample_config.json \
  --query "How might we revolutionize remote work collaboration?" \
  --models 3 \
  --instructions 3 \
  --variations 3 \
  --max-combinations 27 \
  --balanced-models \
  --save-state "data/state/remote_work_stage1.json" \
  --output-file "data/output/remote_work_stage1.md"

# Stage 2: Focus on promising themes, analyzing model contributions
# (after reviewing Stage 1 results and model contribution metrics)
python main.py \
  --query "How might we create immersive virtual collaboration spaces that preserve non-verbal communication?" \
  --load-state "data/state/remote_work_stage1.json" \
  --models 3 \
  --balanced-models \
  --max-combinations 18 \
  --save-state "data/state/remote_work_stage2.json" \
  --output-file "data/output/remote_work_stage2.md"

# Stage 3: Add constraints for practical implementation, maintaining model diversity
python main.py \
  --query "How might we create immersive virtual collaboration spaces that work on standard hardware and low-bandwidth connections?" \
  --load-state "data/state/remote_work_stage2.json" \
  --models 3 \
  --balanced-models \
  --max-combinations 18 \
  --save-state "data/state/remote_work_stage3.json" \
  --output-file "data/output/practical_virtual_collaboration.md"
```

This multi-stage approach demonstrates how ISEE can support an entire innovation process from initial exploration to practical implementation while maintaining cognitive diversity through balanced model contributions at each stage.

## Analyzing Model Contributions

After running multiple sessions, examine the model contribution metadata to identify patterns:

1. **Model strengths in different domains**: Which models excel at technical, creative, or practical aspects?
2. **Evolution of contributions**: Do certain models become more/less influential as the process narrows?
3. **Complementary capabilities**: Which model combinations produce the most powerful synthesized ideas?
4. **Thought style alignment**: Do certain models align better with specific cognitive frameworks?

This analysis can help you optimize future innovation sessions by strategically leveraging each model's unique strengths.