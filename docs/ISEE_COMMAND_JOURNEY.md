# The Journey of a Command Through the ISEE Framework

This document provides a detailed walkthrough of what happens when you run a comprehensive command with the ISEE Meta Framework. We'll follow the journey of the query from submission to final output, explaining each step of the process from the perspective of the command itself.

## The Command

```bash
python main.py \
  --query "How might we automate a workflow for getting data from Discord channels and piping them into a vector database updated daily?" \
  --models 3 \
  --instructions 5 \
  --variations 4 \
  --domain "technology innovation" \
  --balanced-models \
  --config sample_config.json \
  --max-combinations 60 \
  --synthesize-method cross_pollination \
  --output-format markdown \
  --output-file "discord-piping-vector-db_results.md" \
  --save-state "discord-piping-vector-db_results_state.json"
```

## Step 1: Command Line Parsing and Initialization

When you execute me, I'm first processed by Python's `argparse` module in the `main()` function. Each of my flags becomes an attribute in the `args` object:

- My `--query` becomes `args.query` with the Discord automation text
- My `--models 3` becomes `args.models` with value 3 
- My `--instructions 5` becomes `args.instructions` with value 5
- And so on for all my parameters

Next, an `ISEEApplication` instance is created, loading the configuration from `sample_config.json`. This configuration includes:
- Three models: Claude 3.7 Sonnet, GPT-4 Turbo, and Claude 3 Opus
- Five instruction templates with different cognitive styles
- Domain definitions including "Technology Innovation"
- Scoring criteria for evaluating responses

## Step 2: Query Registration

I'm not just a plain text query - I'm transformed into a structured object. The framework:

1. Creates a unique ID for me using UUID (e.g., `query_12ab34cd`)
2. Wraps me in a `Query` object with that ID
3. Registers me with the `query_generator`
4. Prepares to create variations of me (specified by `--variations 4`)

## Step 3: Domain Selection

The framework searches for domains matching "technology innovation" and finds the matching domain object with:
- ID: `domain_tech`
- Name: "Technology Innovation"
- Description: "The field focused on developing and implementing new technologies to solve existing problems and create new possibilities."
- Keywords: ["technology", "innovation", "digital transformation", "emerging tech", "smart systems", "artificial intelligence", "IoT", "blockchain", "robotics"]

## Step 4: Generating Combinations

Now the framework uses the `generate_combinations()` method to create a diverse set of execution combinations:

1. **Query Variations**: The system creates 4 variations of my original query text using strategies like:
   - Adding constraints: "How might we automate a workflow for getting data from Discord channels and piping them into a vector database updated daily, with limited resources?"
   - Changing perspective: "How might we automate a workflow for getting data from Discord channels and piping them into a vector database updated daily, considering it from the perspective of end users?"
   - Adding context: "How might we automate a workflow for getting data from Discord channels and piping them into a vector database updated daily, in the context of rapid urbanization?"
   - Rephrasing: "What are effective ways to automate a workflow for getting data from Discord channels and piping them into a vector database updated daily?"

2. **Model Selection**: All 3 models specified in the config are selected:
   - Claude 3.7 Sonnet
   - GPT-4 Turbo
   - Claude 3 Opus

3. **Instruction Selection**: All 5 instruction templates are selected to provide cognitive diversity:
   - Analytical Framework - structured reasoning
   - Creative Framework - divergent thinking and novel ideation
   - Critical Framework - challenging assumptions
   - Integrative Framework - synthesizing diverse perspectives
   - Pragmatic Framework - focusing on implementation

4. **Balanced Distribution**: Since I included `--balanced-models`, combinations are created in a way that ensures each model gets an equal share of the workload. This distributes combinations evenly across all three models.

The system generates 60 combinations (5 instructions × 4 queries × 1 domain × 3 models) but will limit execution to the `--max-combinations 60` value.

## Step 5: Executing Combinations

For each combination, the system:

1. **Formats the instruction template** by inserting the domain description
2. **Combines the instruction with the query** to create a complete prompt
3. **Creates a model API client** using the appropriate provider (Anthropic for Claude models, OpenAI for GPT)
4. **Makes API calls** to each model with the formatted prompts
5. **Stores the results** including:
   - The response text
   - Metadata about the model and template used
   - Timing information

Since I requested 60 combinations, the system makes 60 separate API calls across the three models.

## Step 6: Evaluating Results

After gathering all responses, the system evaluates each one using the `ScoringFramework` with five criteria:

1. **Novelty** (25% weight): How original and innovative the ideas are
2. **Feasibility** (20% weight): How practical and implementable the ideas are
3. **Impact** (30% weight): The potential magnitude of positive change
4. **Comprehensiveness** (15% weight): How thoroughly the response addresses different aspects
5. **Specificity** (10% weight): The level of detail and concreteness

Each response gets scores on these criteria, which are combined into an overall weighted score.

## Step 7: Synthesizing Ideas

Since I specified `--synthesize-method cross_pollination`, the system:

1. Selects the top 10 highest-scoring responses based on overall score
2. Creates a synthesized idea that combines elements from all top responses
3. Documents the sources of each contribution, including which models provided which ideas
4. Creates metadata showing the contribution percentages from each model

The cross-pollination method specifically looks for complementary elements across different responses and combines them in novel ways, rather than clustering similar ideas together.

## Step 8: Formatting Output

The synthesized ideas are formatted as specified by `--output-format markdown` into a document with:

1. A title section for the synthesized idea
2. The description of how it was created
3. The key points extracted from the source responses
4. Metadata including:
   - Which models contributed
   - The synthesis method used
   - Source combinations
   - Average evaluation scores

## Step 9: Saving Results

Finally, two files are created:

1. **discord-piping-vector-db_results.md**: The formatted output document with the synthesized ideas
2. **discord-piping-vector-db_results_state.json**: A complete state file containing:
   - All combinations generated
   - All raw model responses
   - All evaluation scores
   - The synthesized ideas

The state file allows you to reload this exact state later without needing to make API calls again, letting you try different synthesis methods or output formats on the same data.

## Beyond the Command: The Power of Combinatorial Exploration

What makes the ISEE Framework powerful is not just that it calls multiple models, but that it systematically explores a combinatorial space of:

- Different query formulations
- Multiple cognitive frameworks (via different instruction templates)
- Diverse domain perspectives
- Various model architectures

By exploring this space and then evaluating and synthesizing the results, the framework can discover solutions that wouldn't emerge from any single model, prompt, or approach. The balanced model representation ensures that each model's unique strengths contribute equally to the exploration.

This comprehensive approach allows ISEE to generate more diverse, higher-quality ideas than would be possible with a traditional single-prompt approach.