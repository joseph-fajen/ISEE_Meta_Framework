# ISEE Meta Framework - Quick Start Guide

*Last updated: July 17, 2025*

Welcome to the ISEE Meta Framework - a Web UI-first platform for comprehensive AI research and cognitive diversity exploration. This guide will get you up and running in minutes.

## Getting Started (Web UI - Recommended)

### 1. Setup and Launch

```bash
# Clone and setup
git clone [repository-url]
cd ISEE_Meta_Framework

# Install dependencies
pip install -r requirements.txt

# Start the Web UI server
./scripts/dev-server.sh start
```

### 2. Access the Interface

Open your browser to: **http://localhost:5001/isee-ui**

You'll see the modern ISEE Web Interface with a sophisticated charcoal and copper design.

### 3. Configure Your API Key

**Essential**: You need an OpenRouter API key to access 300+ AI models with a single key.

**In the Web UI**:
1. Click the "🔑 Set API Key" button in the top right
2. Enter your OpenRouter API key
3. The system will automatically validate and save it for your session

**Alternative - Environment Variable**:
```bash
export OPENROUTER_API_KEY="your-openrouter-api-key-here"
```

### 4. Your First Analysis

1. **Enter your research question** in the query box (default shows JWST example)
2. **Select analysis depth**: Balanced (30 calls), Deep (45 calls), or Comprehensive (60 calls)
3. **Choose cognitive frameworks**: Select from 10 different thinking approaches
4. **Pick knowledge domains**: Choose relevant expertise areas
5. **Click "🚀 Generate Analysis"**

**Example first query**:
```
How can we design an innovative educational program that integrates 
classical music appreciation, mindfulness meditation, and literary 
exploration for learners aged 5 to 95?
```

### 5. Monitor Progress and View Results

- **Real-time indicators**: Watch as different models and frameworks activate
- **Live progress tracking**: See cost estimates and completion status
- **Download results**: Get your comprehensive analysis as markdown
- **View HTML reports**: Professional formatted reports with rich styling

## Understanding ISEE's Approach

### Built-in Intelligence and Optimization

**ISEE doesn't just run queries - it learns and improves from every execution:**

🧠 **Automatic Performance Tracking**: Every query execution is analyzed and stored in a performance database  
📊 **Self-Analysis Capabilities**: Built-in system to identify optimization opportunities  
🎯 **Data-Driven Recommendations**: Strategic guidance for improving quality and reducing costs  
🔄 **Continuous Improvement**: System gets smarter and more efficient with use  

**Example: After running several analyses, ISEE might discover:**
- "Remove Model X (poor performance: 0.254 avg) → gain 15% quality improvement"
- "Rebalance cost tiers → save 20% budget while maintaining quality"  
- "Focus on Models Y and Z → they consistently deliver 0.5+ scores"

*Learn more: [Analysis and Optimization Guide](/docs/advanced/ANALYSIS_AND_OPTIMIZATION.md)*

### Traditional vs. ISEE Method

| Traditional AI Approach | ISEE Meta Framework |
|------------------------|-------------------|
| Single AI model response | 30-60 diverse AI responses |
| One thinking style | 10 cognitive frameworks |
| Fixed perspective | Multiple knowledge domains |
| Manual evaluation | Systematic scoring & ranking |
| Simple output | Synthesized high-quality insights |

### What Makes ISEE Unique

✅ **Cognitive Diversity**: Combines Analytical, Creative, Critical, Systems Thinking, and 6 other frameworks  
✅ **Provider Diversity**: Access to Claude, GPT-4, Gemini, Llama, and 300+ other models  
✅ **Systematic Synthesis**: Research-grade scoring and cluster-based idea combination  
✅ **Complete Transparency**: Full attribution showing which models contributed what  
✅ **Real-time Experience**: Live progress indicators and immediate results  

## Web UI Features

### Analysis Configuration
- **Flexible depth control**: 30/45/60 LLM calls based on your needs
- **Dynamic model selection**: Individual model choice or curated collections
- **Real-time cost estimation**: Know costs before execution
- **Framework customization**: Select specific cognitive approaches

### Live Execution Monitoring
- **Model indicators**: Light up as each AI model responds
- **Framework tracking**: See which cognitive approaches are active
- **Progress visualization**: Real-time completion status
- **Cost tracking**: Live updates of analysis costs

### Results and Export
- **Markdown download**: Clean, formatted analysis results
- **HTML reports**: Professional presentation-ready reports
- **Model attribution**: Complete transparency of contributions
- **Quality metrics**: Scoring and synthesis information

## Advanced Usage (CLI)

For power users, the CLI remains available with full feature parity:

```bash
# Quick CLI analysis
python main.py --query "Your research question" \
  --models 5 --config openrouter_config.json \
  --output-file results.md

# Advanced CLI with custom parameters
python main.py --query "Your question" \
  --models 3 --frameworks 4 --domains 3 \
  --max-combinations 36 --config openrouter_config.json \
  --generate-reports --export-csv
```

## Configuration Guide

### OpenRouter Setup (Recommended)
- **Single API Key**: Access 300+ models from all major providers
- **Unified Billing**: One account for Claude, GPT-4, Gemini, Llama, and more
- **Cost Efficiency**: Competitive pricing across all model providers
- **Simple Management**: No need to manage multiple API keys

### Alternative Provider Setup
You can also use individual provider API keys:
```bash
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-key"
```

## Example Workflows

### Research Workflow
1. **Start with Balanced Analysis** (30 calls, ~$2.40, 3-5 minutes)
2. **Review initial insights** in downloaded markdown file
3. **Generate HTML report** for professional presentation
4. **Iterate with Deep Analysis** (45 calls) if needed

### Academic Research
1. **Use Comprehensive Analysis** (60 calls, ~$4.80, 8-12 minutes)
2. **Export CSV data** for statistical analysis
3. **Generate multiple report formats** for different audiences
4. **Maintain research trail** with session documentation

### Strategic Planning
1. **Define clear research question** with specific scope
2. **Select relevant knowledge domains** for your industry
3. **Use balanced cognitive frameworks** for comprehensive coverage
4. **Generate executive-ready HTML reports** for stakeholder presentations

## Understanding Results

### Synthesized Ideas Structure
- **3 High-Quality Ideas**: Representing different thematic approaches
- **Model Attribution**: Which AI models contributed to each idea
- **Quality Scores**: Based on Impact, Novelty, Feasibility, Comprehensiveness, Specificity
- **Source Traceability**: Links back to original model responses

### Quality Metrics
- **Overall Score**: Weighted combination of 5 criteria
- **Impact (30%)**: Transformative potential and scale
- **Novelty (25%)**: Innovation and breakthrough thinking
- **Feasibility (20%)**: Practical implementation considerations
- **Comprehensiveness (15%)**: Depth and multi-perspective coverage
- **Specificity (10%)**: Concrete details and precision

## Troubleshooting

### Common Issues
- **Server won't start**: Check if port 5001 is available: `lsof -i :5001`
- **API key errors**: Verify your OpenRouter key at https://openrouter.ai/keys
- **Slow responses**: Normal for first-time model calls; subsequent calls are faster
- **Memory issues**: Reduce analysis depth from Comprehensive to Balanced

### Getting Help
- **Documentation**: Browse `/docs/` folder for detailed guides
- **Examples**: Check `/docs/getting-started/EXAMPLE_USE_CASES.md`
- **Configuration**: See `/docs/configuration/` for advanced setup

## Next Steps

### Immediate Actions
1. **Complete your first analysis** using the Web UI
2. **Experiment with different frameworks** to see how thinking styles affect results
3. **Try various analysis depths** to understand the quality/cost tradeoffs
4. **Generate HTML reports** for professional presentation

### Advanced Exploration
1. **Learn the CLI** for batch processing and automation
2. **Discover self-analysis**: Use `/analyze-last-result` to optimize system performance
3. **Explore custom configurations** for specialized use cases
4. **Analyze CSV exports** for statistical insights
5. **Integrate with research workflows** for systematic use

### Contributing and Customization
1. **Review core algorithms** in `/docs/advanced/` for methodology understanding
2. **Customize cognitive frameworks** for domain-specific applications
3. **Extend reporting capabilities** with custom templates
4. **Contribute improvements** to the open-source project

---

## What's Next?

- **Try it now**: Start with the Web UI at http://localhost:5001/isee-ui
- **Learn more**: Read [Why ISEE?](WHY_ISEE.md) for the philosophical foundation
- **See examples**: Browse [Example Use Cases](EXAMPLE_USE_CASES.md) for inspiration
- **Go deeper**: Explore [Advanced Features](/docs/advanced/) for power user capabilities

*The ISEE Meta Framework transforms how we approach complex research questions by systematically combining the cognitive diversity of multiple AI models with proven research methodologies. Start exploring today!*