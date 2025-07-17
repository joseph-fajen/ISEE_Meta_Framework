# ISEE Configuration Guide

*Last updated: July 17, 2025*

This guide explains how to configure the ISEE Meta Framework in the current OpenRouter era. The configuration has been streamlined for the Web UI-first approach while maintaining CLI flexibility.

## Quick Setup (Recommended)

### OpenRouter Configuration (Single API Key for 300+ Models)

The simplest and most powerful configuration uses OpenRouter:

1. **Get OpenRouter API Key**: Visit https://openrouter.ai/keys
2. **Set Environment Variable**:
   ```bash
   export OPENROUTER_API_KEY="your-key-here"
   ```
3. **Use Default Configuration**: The system automatically uses `openrouter_config.json`

**Done!** You now have access to 300+ models from all major providers with a single key.

## Current Configuration Architecture

### Primary Configuration: `openrouter_config.json`

This is the main configuration file that provides:
- **300+ AI Models**: Claude, GPT-4, Gemini, Llama, Mistral, and many more
- **Single API Key**: One OpenRouter key for all models
- **Unified Billing**: Consolidated costs across all providers
- **Automatic Updates**: New models added regularly

### Configuration Structure

```json
{
  "models": {
    "api_models": [
      {
        "id": "anthropic/claude-3.5-sonnet",
        "name": "Claude 3.5 Sonnet",
        "provider": "openrouter",
        "context_length": 200000,
        "cost_per_1k_tokens": {
          "input": 0.003,
          "output": 0.015
        }
      }
    ]
  },
  "cognitive_frameworks": [
    {
      "id": "analytical",
      "name": "Analytical Framework",
      "description": "Structured reasoning and evidence-based analysis",
      "template": "You are an expert analyst..."
    }
  ],
  "domains": [
    {
      "id": "education",
      "name": "Education", 
      "description": "Educational systems, learning, and pedagogy"
    }
  ]
}
```

## Web UI Configuration

### API Key Management

**In Web UI**:
1. Click "🔑 Set API Key" button
2. Enter your OpenRouter API key
3. System validates and stores for session

**Environment Variable** (preferred for development):
```bash
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"
```

### Model Selection

**Curated Collections** (recommended):
- **Flagship Models**: Top performers from each provider
- **Creative Models**: Optimized for creative and innovative thinking
- **Analytical Models**: Best for structured analysis and reasoning
- **Balanced Collection**: Well-rounded mix of capabilities

**Individual Models**: Select specific models for targeted analysis

## Advanced Configuration

### Custom Model Collections

You can create custom collections by modifying `openrouter_config.json`:

```json
{
  "model_collections": {
    "research_collection": {
      "name": "Research Collection",
      "description": "Optimized for academic research",
      "models": [
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4-turbo",
        "google/gemini-2.5-pro",
        "meta-llama/llama-3.1-70b-instruct"
      ]
    }
  }
}
```

### Cognitive Framework Customization

Add or modify cognitive frameworks:

```json
{
  "cognitive_frameworks": [
    {
      "id": "domain_expert",
      "name": "Domain Expert Framework",
      "description": "Deep expertise in specific fields",
      "template": "You are a world-renowned expert in {domain} with 20+ years of experience. Your expertise includes cutting-edge research, practical implementation, and industry best practices. Approach this question with the depth and nuance that comes from deep domain mastery:",
      "complexity": "advanced"
    }
  ]
}
```

### Custom Domain Configuration

Define specialized domains for your use case:

```json
{
  "domains": [
    {
      "id": "biotech_research",
      "name": "Biotechnology Research",
      "description": "Biotechnology, genomics, and life sciences research",
      "keywords": ["biotech", "genomics", "CRISPR", "synthetic biology", "bioinformatics"],
      "context": "cutting-edge biotechnology research and development"
    }
  ]
}
```

## Configuration Files Overview

### Current Active Configurations

| File | Purpose | Status |
|------|---------|---------|
| `openrouter_config.json` | **Primary** - 300+ models via OpenRouter | ✅ Current |
| `unified_config.json` | Legacy unified configuration | 📦 Archived |
| `sample_config.json` | Legacy sample configuration | 📦 Archived |

### Migration from Legacy Configurations

If you have old configuration files, use this migration path:

```bash
# Old approach (deprecated)
python main.py --config unified_config.json --query "..."

# New approach (recommended)  
python main.py --config openrouter_config.json --query "..."

# Or simply (uses openrouter_config.json by default)
python main.py --query "..."
```

## CLI Configuration Usage

### Basic CLI Usage

```bash
# Use default OpenRouter configuration
python main.py --query "Your research question"

# Specify configuration explicitly
python main.py --config openrouter_config.json --query "Your question"

# Override number of models/frameworks
python main.py --query "Your question" --models 5 --frameworks 3
```

### Advanced CLI Configuration

```bash
# Custom analysis depth with specific parameters
python main.py \
  --query "How can we improve sustainable energy adoption?" \
  --models 6 --frameworks 4 --domains 3 \
  --max-combinations 72 \
  --config openrouter_config.json \
  --output-file sustainable_energy_analysis.md

# Generate comprehensive reports
python main.py \
  --query "Your question" \
  --config openrouter_config.json \
  --generate-reports --export-csv --analyze-results
```

## Cost Management

### Understanding Costs

OpenRouter provides transparent, competitive pricing:

- **Claude 3.5 Sonnet**: $3.00 per 1M input tokens
- **GPT-4 Turbo**: $10.00 per 1M input tokens  
- **Gemini 2.5 Pro**: $1.25 per 1M input tokens
- **Llama 3.1 70B**: $0.88 per 1M input tokens

### Cost Estimation

The Web UI provides real-time cost estimates:
- **Balanced Analysis** (30 calls): ~$2.40
- **Deep Analysis** (45 calls): ~$3.60
- **Comprehensive Analysis** (60 calls): ~$4.80

### Cost Control

```bash
# Limit maximum cost
python main.py --query "Your question" --max-cost 5.00

# Preview costs without execution
python main.py --query "Your question" --dry-run

# Use cost-effective models only
python main.py --query "Your question" --cost-tier low
```

## Performance Optimization

### Model Performance Rankings

ISEE automatically tracks and uses model performance data:

```json
{
  "model_rankings": {
    "overall_performance": [
      "anthropic/claude-3.5-sonnet",
      "openai/gpt-4-turbo", 
      "google/gemini-2.5-pro"
    ],
    "cost_effectiveness": [
      "google/gemini-2.5-pro",
      "meta-llama/llama-3.1-70b-instruct",
      "anthropic/claude-3.5-sonnet"
    ]
  }
}
```

### Dynamic Rankings

The system updates model rankings based on:
- **Quality scores**: Multi-criteria evaluation results
- **Cost efficiency**: Performance per dollar spent
- **Reliability**: Success rate and error frequency
- **Speed**: Response time and throughput

## Environment Configuration

### Required Environment Variables

```bash
# Primary (required)
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"

# Optional - for specific providers
export ANTHROPIC_API_KEY="your-anthropic-key"    # Direct Anthropic access
export OPENAI_API_KEY="your-openai-key"          # Direct OpenAI access
export GOOGLE_API_KEY="your-google-key"          # Direct Google access
```

### Configuration File Locations

```bash
# Primary configuration (auto-detected)
./openrouter_config.json

# Custom configurations
./configs/my_custom_config.json
./configs/research_config.json
./configs/production_config.json
```

## Troubleshooting Configuration

### Common Issues

**API Key Problems**:
```bash
# Verify API key is set
echo $OPENROUTER_API_KEY

# Test API key validity
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  https://openrouter.ai/api/v1/models
```

**Configuration File Issues**:
```bash
# Validate JSON syntax
python -m json.tool openrouter_config.json

# Check configuration loading
python -c "import json; print(json.load(open('openrouter_config.json'))['models']['api_models'][0]['name'])"
```

**Model Access Issues**:
```bash
# List available models
python main.py --list-models

# Test specific model
python main.py --query "test" --models 1 --simulate
```

### Configuration Validation

```bash
# Validate complete configuration
python -c "
from app import demo
print(f'API Detection: {demo._detect_apis()}')
print(f'Available Models: {len(demo.get_individual_models())}')
print(f'Frameworks: {len(demo.cognitive_framework_visualizer.get_frameworks_for_complexity(\"all\"))}')
"
```

## Best Practices

### For Web UI Users
1. **Use OpenRouter**: Single key for maximum model access
2. **Start with Balanced**: 30-call analysis for most use cases
3. **Monitor costs**: Check real-time estimates before execution
4. **Save results**: Download markdown and HTML reports

### For CLI Users  
1. **Use default config**: `openrouter_config.json` is optimized
2. **Export data**: Always use `--export-csv` for analysis
3. **Save state**: Use `--save-state` for expensive runs
4. **Generate reports**: Include `--generate-reports --analyze-results`

### For Researchers
1. **Document configuration**: Save custom configs with descriptive names
2. **Track model performance**: Monitor which models work best for your domain
3. **Use comprehensive analysis**: 60-call runs for publication-quality research
4. **Maintain reproducibility**: Fixed configurations for comparable results

---

## Quick Reference

### Essential Commands

```bash
# Web UI (recommended)
./scripts/dev-server.sh start
# Then visit: http://localhost:5001/isee-ui

# CLI Quick Start
python main.py --query "Your research question"

# CLI Advanced
python main.py --query "Your question" --models 5 --frameworks 4 \
  --generate-reports --export-csv --output-file results.md
```

### Key Files
- **`openrouter_config.json`**: Primary configuration (300+ models)
- **`.env`**: Environment variables (API keys)
- **`docs/configuration/`**: Advanced configuration guides

### Support
- **Configuration issues**: Check `docs/advanced/` for troubleshooting
- **API problems**: Verify keys at https://openrouter.ai/keys  
- **Model questions**: Use `--list-models` to see available options

*The ISEE Meta Framework configuration has evolved to prioritize simplicity and power through OpenRouter integration while maintaining flexibility for advanced use cases.*