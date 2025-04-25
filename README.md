# Idea Synthesis and Extraction Engine (ISEE)

## Project Overview

The Idea Synthesis and Extraction Engine is a meta-framework for innovation that systematically leverages AI to generate, evaluate, and extract high-value concepts across any domain. Rather than using AI in a single-prompt manner, this framework creates a deliberate combinatorial approach that maximizes the exploration of possibility space before filtering for the most promising ideas.

### A New Paradigm for AI-Powered Innovation

ISEE represents a fundamentally different approach to using AI for innovation:

- **Beyond Single Prompts**: Instead of relying on individual prompts, ISEE systematically explores combinations of models, cognitive frameworks, queries, and domains
- **Maximizing Cognitive Diversity**: By employing multiple instruction templates that embody different thinking styles, ISEE accesses a wider range of approaches than a single human could generate
- **From Volume to Value**: ISEE doesn't just generate content—it evaluates, ranks, and synthesizes the outputs to extract the most valuable concepts
- **Persistent Exploration**: With state saving capabilities, teams can build cumulative knowledge across sessions and collaborate on complex innovation challenges

*For a deeper understanding of why ISEE matters and how it differs from traditional AI approaches, see [WHY_ISEE.md](docs/WHY_ISEE.md)*

*For concrete examples of how to use ISEE for different innovation challenges, see [EXAMPLE_USE_CASES.md](docs/EXAMPLE_USE_CASES.md)*

## Repository Contents

This repository contains the following files:

- `README.md` - This file providing an overview of the project
- `main.py` - The main application for running the ISEE pipeline
- `model_api_integration.py` - Module for integrating with AI model APIs
- `instruction_templates.py` - Module for managing instruction templates
- `query_generator.py` - Module for generating query variations
- `domain_manager.py` - Module for managing application domains
- `evaluation_scoring.py` - Module for evaluating and scoring generated ideas
- `reporting.py` - Module for generating detailed reports and CSV exports
- `analysis.py` - Module for analyzing results and creating visualizations
- `sample_config.json` - Sample configuration file
- `gemini_test_config.json` - Configuration file for Google Gemini 2.5 Pro integration
- `requirements.txt` - Package dependencies
- `workflow_diagram.svg` - Visual representation of the ISEE system architecture
- `docs/` - Directory containing all documentation files:
  - `QUICKSTART.md` - Quick start guide to get up and running
  - `SYSTEM_OVERVIEW.md` - Overview of the ISEE system architecture
  - `CONFIG_GUIDE.md` - Guide for configuring the ISEE framework
  - `DOMAIN_CONFIG_GUIDE.md` - Guide for using domain-specific configurations
  - `REPORTING_GUIDE.md` - Documentation for reporting and analysis features
  - `DRY_RUN_GUIDE.md` - Comprehensive guide for testing with dry run mode
  - `EXAMPLE_USE_CASES.md` - Detailed examples of using ISEE for innovation
  - `WHY_ISEE.md` - Explanation of the ISEE concept and benefits
  - `DATA_STRUCTURE.md` - Details about the data structures used in ISEE
  - `RESULT_VIEWER_GUIDE.md` - Guide for viewing and interpreting results
  - `ISEE_COMMAND_JOURNEY.md` - Detailed explanation of a command's execution through ISEE

## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up API keys for the models you want to use:
   - For Claude: Set the `ANTHROPIC_API_KEY` environment variable
   - For OpenAI: Set the `OPENAI_API_KEY` environment variable

## Usage

### Basic Usage

Run the complete pipeline with a single query:

```bash
python main.py --query "How might we improve urban transportation in the next decade?" --domain "Urban Planning" --max-combinations 10
```

This will:
1. Create a new query based on the input text
2. Generate variations of the query
3. Generate combinations of models, instructions, queries, and domains
4. Execute the combinations (using real API calls if API keys are available)
5. Evaluate the results
6. Synthesize ideas from the top results
7. Format and display the output

### API Integration

The system supports real API calls to Anthropic (Claude), OpenAI models, Google Gemini, and now Ollama local models. 

### Using Cloud Models (Anthropic, OpenAI & Google Gemini)

1. Set up API keys by either:

   **Option 1:** Using environment variables:
   ```bash
   # For Anthropic Claude models
   export ANTHROPIC_API_KEY=your_api_key_here
   
   # For OpenAI GPT models
   export OPENAI_API_KEY=your_api_key_here
   
   # For Google Gemini models
   export GOOGLE_API_KEY=your_api_key_here
   ```
   
   **Option 2:** Using a .env file (recommended for development):
   ```bash
   # Copy the template file
   cp .env.template .env
   
   # Edit the .env file with your API keys
   nano .env  # or use any text editor
   ```

### Using Local Models with Ollama

The framework now supports using local models via [Ollama](https://ollama.com). This is especially useful for:
- Working offline without internet access
- Avoiding API costs and rate limits
- Using models not available via API
- Privacy-sensitive applications

To use Ollama models:

1. Install Ollama from https://ollama.com
2. Start the Ollama service: `ollama serve`
3. Download the models you want to use:
   ```bash
   ollama pull codellama:7b-instruct
   ollama pull mixtral:latest
   ollama pull phi3:mini
   ollama pull llama3:8b
   ```
4. Use the unified configuration:
   ```bash
   python main.py --config unified_config.json --query "Your query here"
   ```

The system will automatically detect your available models and use only those you have access to. For example:
- If you have only Ollama installed, it will use only Ollama models
- If you have API keys, it will use both API models and Ollama models if available
- If you have no models available, it will run in simulation mode

### Enhanced Cognitive Diversity with Multiple Model Architectures

One of the most powerful aspects of the ISEE framework is its ability to leverage diverse model architectures to generate richer, more innovative ideas. With the addition of Ollama models and Google Gemini, this diversity is significantly expanded:

**Model Architecture Diversity**
- **Claude Models**: Known for careful, nuanced reasoning and instruction-following
- **GPT Models**: Offer strong creative generation and detailed domain knowledge
- **Gemini 2.5 Pro**: Google's multimodal model with strong reasoning capabilities
- **CodeLlama**: Specialized for structured, computational thinking with code expertise
- **Mixtral**: Employs a mixture-of-experts architecture for versatile reasoning
- **Phi-3**: Optimized for efficient reasoning in a compact model size
- **Llama 3**: Brings Meta's latest approach to knowledge representation

**Cognitive Benefits:**
- Each model family has unique training data distributions and internal architectures
- Different reasoning patterns emerge when combining cloud and local models
- Knowledge gaps in one model family can be complemented by strengths in others
- Self-correction and evaluation improve with truly diverse model perspectives

When running all models together (cloud + local), the system can synthesize ideas from significantly more dissimilar systems, increasing the likelihood of discovering novel patterns or connections that would be missed with a more homogeneous model population.

### Running the Framework

Configure models in a configuration file:

- `unified_config.json` (recommended) - Comprehensive config with all models and all cognitive frameworks
- `sample_config.json` - Original config with mixed model providers
- `ollama_config.json` - Legacy Ollama-only config (now updated with all cognitive frameworks)
- `gemini_test_config.json` - Config for testing with Google Gemini 2.5 Pro

Run with the unified config file:
```bash
python main.py --config unified_config.json --query "Your query here"
```

You can force simulation mode even if APIs or Ollama are available by using the `--simulate` flag.

### Command-Line Options

```
usage: main.py [-h] [--config CONFIG] [--save-state SAVE_STATE] [--load-state LOAD_STATE] [--domain-config DOMAIN_CONFIG]
               [--query QUERY] [--domain DOMAIN] [--models MODELS] [--use-ollama] [--instructions INSTRUCTIONS]
               [--variations VARIATIONS] [--max-combinations MAX_COMBINATIONS] [--sampling-method {exhaustive,stratified,adaptive}]
               [--output-format {markdown,json}] [--output-file OUTPUT_FILE] [--output-directory OUTPUT_DIRECTORY]
               [--simulate] [--dry-run] [--balanced-models] [--synthesize-method {cluster_based,cross_pollination}]
               [--generate-reports] [--report-format {markdown,json}] [--export-csv] [--analyze-results] [--no-visualizations]
               [--quick] [--full] [--list-domains]

Idea Synthesis and Extraction Engine

options:
  -h, --help            show this help message and exit
  --config CONFIG       Path to configuration file
  --save-state SAVE_STATE
                        Save application state to file
  --load-state LOAD_STATE
                        Load application state from file
  --domain-config DOMAIN_CONFIG
                        Path to a domain-specific configuration file
  --query QUERY         Input query text
  --domain DOMAIN       Domain to focus on
  --models MODELS       Number of models to use (set to a higher number to include more models)
  --use-ollama          Include Ollama models in the model selection
  --instructions INSTRUCTIONS
                        Number of instructions to use
  --variations VARIATIONS
                        Number of query variations to generate
  --max-combinations MAX_COMBINATIONS
                        Maximum number of combinations to execute
  --sampling-method {exhaustive,stratified,adaptive}
                        Method to use for sampling combinations
  --output-format {markdown,json}
                        Output format
  --output-file OUTPUT_FILE
                        Path to save the output to
  --output-directory OUTPUT_DIRECTORY
                        Directory to save reports to
  --simulate            Use simulated responses instead of real model APIs
  --dry-run             Print what would be executed without actually running
  --balanced-models     Ensure balanced representation of models in the executed combinations
  --synthesize-method {cluster_based,cross_pollination}
                        Method to use for synthesizing ideas
  --generate-reports    Generate detailed reports
  --report-format {markdown,json}
                        Format for generated reports
  --export-csv          Export data as CSV files for analysis
  --analyze-results     Perform analysis of results with visualizations
  --no-visualizations   Skip generating visualization charts during analysis
  --quick               Run in quick mode (stratified sampling with 36 combinations)
  --full                Run in full mode (exhaustive combinations)
  --list-domains        List all available domains and exit
```

### Examples

**Maximizing Model Diversity Across All Providers (Recommended Approach):**

```bash
python main.py \
  --config sample_config.json \
  --query "How can we create high impact AI workflows for technical documentation in a decentralized organization?" \
  --domain "Technology Innovation" \
  --models 7 \
  --use-ollama \
  --instructions 3 \
  --variations 1 \
  --max-combinations 21 \
  --balanced-models \
  --output-file ai_documentation_comprehensive.md
```

This command maximizes cognitive diversity by:
- Using all 7 available models (Claude models, GPT models, and Ollama models)
- Combining cloud and local models for maximum architectural diversity
- Evenly distributing the models across all combinations
- Including 3 different cognitive styles (e.g., analytical, creative, critical)
- Using query variations to explore different aspects of the problem
- Using the `--balanced-models` flag to ensure fair representation
- Tracking model contributions in the output metadata

The resulting synthesis draws from models with fundamentally different architectures, training data, and reasoning patterns - creating a truly comprehensive exploration of the problem space.

**Generate ideas for education innovation using real models:**

```bash
python main.py --config sample_config.json --query "How might we redesign education systems to better prepare students for future challenges?" --domain "Education" --models 2 --instructions 5 --variations 3 --max-combinations 15 --output-file "education_ideas.md"
```

**Generate ideas for healthcare improvement using simulation mode:**

```bash
python main.py --query "How can we make healthcare more accessible and affordable for everyone?" --domain "Healthcare" --models 2 --instructions 3 --variations 2 --output-format json --output-file "healthcare_ideas.json" --simulate
```

**Using local Ollama models for software development ideas:**

```bash
python main.py --config ollama_config.json --query "How can we improve the developer experience for complex codebases?" --domain "Technology Innovation" --models 4 --instructions 2 --variations 2 --output-file "dev_experience_ideas.md" --balanced-models
```

**Combining cloud models with Ollama models:**

```bash
python main.py --config sample_config.json --query "How can we design more energy-efficient homes?" --use-ollama --models 4 --balanced-models --output-file "sustainable_home_ideas.md"
```

**Preview what combinations would be executed without actually running them:**

```bash
python main.py --query "How might we improve urban transportation?" --domain "Urban Planning" --dry-run
```

### File Organization and Output Management

The framework now uses a consistent directory structure for all outputs:

- `/data/output/` - All generated outputs (markdown and JSON files)
- `/data/state/` - State files for saving/restoring framework state

All outputs are automatically saved to the appropriate directories with timestamped filenames.
See [data/README_OUTPUTS.md](data/README_OUTPUTS.md) for detailed information.

### Saving and Loading State

You can save the state of the application to continue work later:

```bash
python main.py --query "How might we improve urban transportation?" --save-state "transportation_state.json"
```

This will automatically save the state to `data/state/transportation_state.json`.

Then load it in a subsequent run:

```bash
python main.py --load-state "transportation_state.json"
```

The framework will automatically look for the state file in `data/state/` and save the output to `data/output/` with a timestamped filename.

## Core Components

The ISEE framework consists of four main layers:

1. **Input Layer** - Manages the diversity of models, instructions, queries, and domains
2. **Orchestration Layer** - Handles the generation and execution of combinations
3. **Evaluation Layer** - Analyzes and scores the generated results
4. **Extraction Layer** - Synthesizes and refines the most promising ideas

## Advanced Features

### Domain Configuration

The framework now supports domain-specific configuration files allowing you to customize domains for different scenarios:

```bash
python main.py --config unified_config.json --domain-config tech_writing_domains.json --query "Your query" --list-domains
```

This enables you to create tailored domain sets for specific fields such as technical writing, healthcare, education, etc. For details, see [DOMAIN_CONFIG_GUIDE.md](docs/DOMAIN_CONFIG_GUIDE.md).

### Reporting and Analysis

The framework includes a comprehensive reporting system:

```bash
python main.py --config unified_config.json --query "Your query" --generate-reports --export-csv --analyze-results
```

This will:
- Generate standard text reports (run summary, metadata)
- Export data as CSV files for external analysis
- Perform automatic data analysis with insights and recommendations
- Create visualization charts showing performance across models, domains, and instructions

For complete reporting documentation, see [REPORTING_GUIDE.md](docs/REPORTING_GUIDE.md).

### Dry Run Mode

Test your configuration and sampling parameters without making API calls:

```bash
python main.py --config unified_config.json --query "Your query" --dry-run
```

This preview mode shows what would be executed, helping you optimize your pipeline before committing to API costs. See [DRY_RUN_GUIDE.md](docs/DRY_RUN_GUIDE.md) for details.

## Development Roadmap

1. ✅ Integrate with real model APIs
2. ✅ Add support for local models via Ollama
3. ✅ Implement domain-specific configuration
4. ✅ Add comprehensive reporting and analysis
5. ✅ Create data exports for external analysis
6. ✅ Add Google Gemini 2.5 Pro API integration
7. Implement more sophisticated evaluation algorithms
8. Add advanced clustering and pattern detection for better synthesis
9. Develop a web-based user interface
10. Add collaborative features for team-based innovation
11. Implement feedback loops to improve the quality of generated ideas
12. Add proper database integration for state management
13. Implement parallel execution for better performance

## Implementation Status

The current implementation is a working prototype that demonstrates the conceptual framework. Current features:

- ✅ Real model API integration with Anthropic (Claude), OpenAI, Google Gemini, and Ollama
- ✅ Support for local models via Ollama for offline/private use
- ✅ Configuration-based model setup with fallback to simulation
- ✅ Flexible query generation with multiple variation strategies
- ✅ Diverse instruction templates for cognitive approach variation
- ✅ Domain-specific contextualization with customizable domain sets
- ✅ Basic evaluation using heuristic-based scoring
- ✅ Simple idea synthesis and extraction
- ✅ Model diversity maximization with balanced representation
- ✅ Enhanced metadata tracking of model contributions
- ✅ Comprehensive reporting with Markdown and JSON formats
- ✅ CSV data exports for external analysis
- ✅ Automated results analysis with visualizations
- ✅ Data-driven recommendations based on performance patterns

Items still in development:

- Evaluation is based on simple heuristics that could be enhanced with more sophisticated analysis
- Idea synthesis could be improved with more advanced NLP techniques
- Pattern recognition and clustering for better synthesis are planned
- A web-based user interface is on the roadmap
- Proper database integration for state management would improve scalability

## Contributors

This project is based on the ISEE meta-framework concept developed by Joseph Fajen. 
Ongoing software development is a collaborative effort between Joseph Fajen, Claude Code, and Claude Desktop.

## License

This project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).  
You are free to use, modify, and distribute this software, provided you include proper attribution to the original author, Joseph Fajen, and retain the license terms.
