# ISEE Framework Quick Start Guide

This guide provides a quick overview of how to get started with the Idea Synthesis and Extraction Engine prototype.

## Setup

1. **Environment setup**
   ```bash
   # Create and activate a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **API Keys**
   
   Set up your API keys to use real model APIs. There are two ways to do this:
   
   **Option 1:** Using environment variables:
   ```bash
   # Set environment variables for API keys
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   export OPENAI_API_KEY="your-openai-api-key"
   ```
   
   **Option 2:** Using a .env file (recommended for development):
   ```bash
   # Copy the template file
   cp .env.template .env
   
   # Edit the .env file with your API keys
   nano .env  # or use any text editor
   ```
   
   **IMPORTANT NOTE**: In addition to setting up API keys, you **must** also use the `--config` parameter with a valid configuration file (like sample_config.json) to use real API calls. Without a configuration file, the system will fall back to simulation mode even when API keys are present.
   
   If you don't have API keys, the system will automatically use simulation mode.

## Understanding the ISEE Approach

### Traditional vs. ISEE Approach

| Traditional AI Approach | ISEE Approach |
|------------------------|---------------|
| Single prompt | Dozens/hundreds of combinations |
| One cognitive style | Multiple cognitive frameworks |
| Fixed context | Various domains and perspectives |
| Manual evaluation | Systematic scoring and ranking |
| One-off generation | Persistent state across sessions |
| Linear exploration | Combinatorial exploration |

## Running Your First Idea Generation Session

Try a simple run to see the framework in action:

```bash
python main.py --query "How might we improve remote work collaboration?" --max-combinations 6 --config sample_config.json
```

> **IMPORTANT**: The `--config` parameter is required to use real API calls. Without it, the system will use simulation mode even if API keys are configured.

This will:
- Create a base query
- Generate variations of the query
- Create combinations with different models, instructions, and domains
- Execute these combinations (using real API calls if keys are available and config is provided, or simulation otherwise)
- Evaluate the results
- Synthesize ideas from the top results
- Display the output

## Exploring Different Domains

To focus on a specific domain:

```bash
python main.py --query "How might we design more sustainable packaging?" --domain "Sustainability" --max-combinations 8 --config sample_config.json
```

## Saving Results

Save the output to a file:

```bash
python main.py --query "How can we make cities more livable?" --output-file "livable_cities_ideas.md" --config sample_config.json
```

## Maximizing Diversity

### Model Diversity

To maximize diversity across different AI models and ensure balanced model representation:

```bash
python main.py \
  --query "How might we reimagine public education?" \
  --models 3 \
  --instructions 3 \
  --variations 2 \
  --max-combinations 18 \
  --balanced-models \
  --config sample_config.json
```

The `--balanced-models` flag ensures that combinations are distributed evenly across all models, preventing any single model from dominating the results. This is especially valuable for:

- Preventing bias from a single model's perspective
- Capturing unique insights from different model architectures
- Comparing how different models approach the same problem
- Ensuring diversity in the synthesized ideas

### Cognitive Diversity

To increase the diversity of thinking approaches:

```bash
python main.py \
  --query "How might we reimagine public education?" \
  --models 3 \
  --instructions 5 \
  --variations 4 \
  --max-combinations 20 \
  --config sample_config.json
```

## Saving and Loading State

One of the most powerful features of the ISEE framework is the ability to save and load the complete state of your session, preserving all combinations, API responses, evaluations, and synthesized ideas:

```bash
# Run a session and save the state
python main.py --query "How might we reduce food waste?" --save-state "food_waste_state.json" --config sample_config.json

# Later, even after restarting your computer, load the state and continue working
python main.py --load-state "food_waste_state.json" --output-file "food_waste_ideas.md"
```

The state file contains everything needed to restore your session exactly as it was, including all API responses. This means:

- You can shut down your computer and pick up where you left off days or weeks later
- You can avoid making the same API calls again, saving time and API costs
- You can try different synthesis approaches on the same data
- You can share your work with colleagues by sharing the state file

For example, to load a state file and try a different output format:

```bash
python main.py --load-state "food_waste_state.json" --output-format json
```

Note: When loading an existing state file, the `--config` parameter is not required for subsequent operations, as the model configurations are stored in the state.

## Customizing Output Format

Choose between markdown and JSON output formats:

```bash
# Get output in JSON format
python main.py --query "How can we improve healthcare access?" --output-format json --config sample_config.json

# Get output in Markdown format (default)
python main.py --query "How can we improve healthcare access?" --output-format markdown --config sample_config.json
```

## Extending the Framework

The modular design allows for easy extension:

1. **Add new instruction templates**
   - Edit `instruction_templates.py` to add new cognitive frameworks

2. **Add new domains**
   - Edit `domain_manager.py` to add new application domains

3. **Use configuration file for models**
   - Create a custom configuration file based on `sample_config.json`
   - Update model settings, parameters, and API endpoints as needed

4. **Enhance evaluation criteria**
   - Modify `evaluation_scoring.py` to add more sophisticated scoring methods

## Directory Structure

Create the following directories for data storage:

```bash
mkdir -p data/results data/state data/output
```

## Example Workflow

Here's a complete workflow example with balanced model representation:

```bash
# 1. Run a query with multiple variations and balanced model representation
python main.py \
  --query "How might we reduce carbon emissions in urban areas?" \
  --variations 3 \
  --models 3 \
  --instructions 3 \
  --max-combinations 18 \
  --balanced-models \
  --save-state "data/state/carbon_emissions.json" \
  --config sample_config.json \
  --output-file "data/output/carbon_emissions.md"

# 2. Examine the results (note the model contributions section in the metadata)
cat data/output/carbon_emissions.md

# 3. Run another related query, maintaining balanced representation
python main.py \
  --query "How can we increase adoption of renewable energy?" \
  --domain "Sustainability" \
  --models 3 \
  --balanced-models \
  --max-combinations 18 \
  --load-state "data/state/carbon_emissions.json" \
  --save-state "data/state/energy_transition.json" \
  --output-file "data/output/renewable_energy.md"

# 4. Combine insights for a comprehensive approach
python main.py \
  --load-state "data/state/energy_transition.json" \
  --output-file "data/output/sustainability_roadmap.md"
```

The balanced model representation ensures that each model contributes equally to the exploration, and the metadata in the output file shows exactly how each model contributed to each synthesized idea.

## Troubleshooting

- **Module not found errors**: Ensure you've activated your virtual environment and installed all requirements
- **API errors**: Check your API keys and connection if using real API integration
- **Simulated responses despite API keys**: Make sure to include the `--config sample_config.json` parameter, which is required for real API calls
- **Memory issues**: Reduce the number of combinations with `--max-combinations` for large runs
- **Data persistence**: Use `--save-state` frequently to avoid losing work

## Using Configuration Files

Try using the sample configuration file for more control:

```bash
python main.py --config sample_config.json --query "How might we improve education?" --max-combinations 10
```

The configuration file allows you to:
- Define specific models and their parameters
- Configure custom instruction templates
- Set up domains with relevant keywords
- Adjust scoring criteria weights

## Controlling API Usage

Control how the system uses APIs:

```bash
# Force simulation mode even if API keys are available
python main.py --query "Your query" --simulate

# Preview what would be executed without making API calls
python main.py --query "Your query" --dry-run
```

## Next Steps

Once you're comfortable with the basic operation:

1. **Maximize Model Diversity**: Always use the `--balanced-models` flag with multiple models to ensure diverse perspectives
2. Try different domains and queries to explore the framework's versatility
3. Experiment with different instruction combinations to find what works best for your use cases
4. Create your own configuration file with preferred models and parameters
5. Add custom evaluation criteria specific to your domain
6. Develop your own synthesis methods to extract the most value from the generated ideas
7. **Analyze Model Contributions**: Examine the model contribution metadata to understand how different models influence different types of ideas

*For detailed, step-by-step example use cases demonstrating the full power of ISEE, see [EXAMPLE_USE_CASES.md](EXAMPLE_USE_CASES.md)*
