# ISEE Configuration Guide

This guide explains how to configure the ISEE framework using the configuration file.

## Configuration File Structure

The configuration file is a JSON file with the following main sections:

1. **models**: Defines the AI models to use for idea generation
2. **instructions**: Defines the instruction templates for cognitive diversity
3. **queries**: Defines base queries to use (optional, can also be provided via command line)
4. **domains**: Defines application domains to contextualize the queries
5. **scoring_criteria**: Defines the criteria for evaluating generated ideas
6. **evaluation_settings**: Configures the evaluation process
7. **extraction_settings**: Configures the idea extraction and synthesis process

## Unified Configuration Approach

The ISEE framework now includes a unified configuration approach with `unified_config.json`, which organizes models by provider type:

```json
"models": {
  "api_models": [
    {
      "id": "model_claude_sonnet",
      "name": "Claude 3.7 Sonnet",
      "provider": "anthropic",
      "requires": "ANTHROPIC_API_KEY",
      ...
    }
  ],
  "ollama_models": [
    {
      "id": "ollama_codellama",
      "name": "CodeLlama 7B Instruct",
      "provider": "ollama",
      "requires": "ollama",
      ...
    }
  ]
}
```

The system will:
- Automatically detect which models you can use based on available API keys and Ollama installation
- Seamlessly combine all models from different sections
- Provide a consistent experience with all cognitive frameworks regardless of model provider

## Models Configuration

The `models` section defines the AI models to use:

```json
"models": [
  {
    "id": "model_1",
    "name": "Claude 3.7 Sonnet",
    "provider": "anthropic",  // Optional, can be inferred from name
    "parameters": {
      "max_tokens": 4096,
      "temperature": 0.7,
      "top_p": 0.95
    }
  },
  {
    "id": "model_2",
    "name": "GPT-4 Turbo",
    "provider": "openai",  // Optional, can be inferred from name
    "parameters": {
      "max_tokens": 4000,
      "temperature": 0.8,
      "top_p": 1.0
    }
  }
]
```

- **id**: Unique identifier for the model (used in combinations)
- **name**: Human-readable name (used to infer provider if not specified)
- **provider**: The API provider ("anthropic", "openai", or "ollama")
- **requires**: Optional field indicating what's needed for this model to run
- **parameters**: Model-specific parameters

The system will automatically determine the provider from the model name if not specified:
- Names containing "claude" will use Anthropic
- Names containing "gpt" will use OpenAI
- Names containing "llama", "mixtral", "phi3", etc. will use Ollama

## Instructions Configuration

The `instructions` section defines the instruction templates:

```json
"instructions": [
  {
    "id": "ins_analytical",
    "name": "Analytical Framework",
    "template": "You are an expert analyst specializing in {domain}. Approach the following question with careful analysis, systematic thinking, and evidence-based reasoning. Consider multiple perspectives, identify potential challenges, and evaluate trade-offs. Focus on creating a structured, logical response.",
    "metadata": {
      "cognitive_style": "analytical",
      "strength": "structured reasoning"
    }
  }
]
```

- **id**: Unique identifier for the template
- **name**: Human-readable name
- **template**: The instruction template with placeholders
- **metadata**: Additional information about the template

## Available Cognitive Frameworks

The ISEE framework includes 10 cognitive frameworks:

1. **Analytical**: Structured reasoning and evidence-based analysis
2. **Creative**: Novel ideation and unconventional thinking
3. **Critical**: Challenging assumptions and identifying flaws
4. **Integrative**: Synthesizing diverse perspectives
5. **Pragmatic**: Practical implementation and feasibility focus
6. **First Principles**: Breaking problems down to fundamental truths
7. **Systems Thinking**: Considering interconnected components and feedback loops
8. **Contrarian**: Taking positions opposite to conventional wisdom
9. **Historical**: Examining precedents and learning from past experiences
10. **Future-Oriented**: Considering long-term trends and emerging paradigms

## Usage with Command Line

To use a configuration file:

```bash
python main.py --config unified_config.json --query "Your query" --max-combinations 10
```

You can override specific settings from the config file using command-line arguments:

```bash
python main.py --config unified_config.json --query "Your query" --models 2 --instructions 3
```

## Creating Your Own Configuration

To create your own configuration:

1. Copy the `unified_config.json` file
2. Modify the model settings to match your API access
3. Add your own instruction templates if needed
4. Define domains relevant to your project
5. Adjust scoring criteria weights to match your priorities

Save the file and use it with the `--config` argument.

## Configuration Tips

- **Models**: Use lower temperature (0.3-0.5) for more focused, deterministic responses and higher temperature (0.7-1.0) for more creative, diverse outputs
- **Instructions**: Use the full range of cognitive frameworks to maximize diversity of thinking
- **Domains**: Add relevant keywords to domains to help contextualize the responses
- **Scoring**: Adjust weights to prioritize different aspects (novelty, feasibility, impact, etc.)

## Example Minimal Configuration

Here's a minimal configuration example:

```json
{
  "models": {
    "api_models": [
      {
        "id": "claude",
        "name": "Claude 3 Sonnet",
        "provider": "anthropic",
        "requires": "ANTHROPIC_API_KEY",
        "parameters": {
          "temperature": 0.7
        }
      }
    ],
    "ollama_models": [
      {
        "id": "ollama_llama3",
        "name": "Llama 3 8B",
        "provider": "ollama",
        "requires": "ollama",
        "parameters": {
          "model": "llama3:8b",
          "temperature": 0.7
        }
      }
    ]
  },
  "instructions": [
    {
      "id": "creative",
      "name": "Creative Approach",
      "template": "You are a creative thinker focusing on {domain}. Generate innovative ideas for: "
    },
    {
      "id": "practical",
      "name": "Practical Approach",
      "template": "You are a pragmatic problem-solver focusing on {domain}. Suggest practical solutions for: "
    }
  ],
  "domains": [
    {
      "id": "technology",
      "name": "Technology",
      "description": "Digital and technological solutions and innovations",
      "keywords": ["software", "hardware", "digital", "automation", "AI"]
    }
  ]
}
```

This minimal configuration defines models from both API and Ollama providers, two instruction approaches, and one domain, which is sufficient to start exploring the combinatorial space.