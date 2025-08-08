# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is ISEE?

The Idea Synthesis and Extraction Engine (ISEE) is a systematic multi-perspective research platform that orchestrates 300+ AI models through diverse cognitive frameworks to discover breakthrough insights. Instead of single AI interactions, ISEE runs 60 comprehensive calls across 14 AI models and 10 cognitive frameworks to reveal perspectives hiding in the spaces between different ways of thinking.

## Development Commands

### Server Management
```bash
# Start development server (recommended)
./scripts/dev-server.sh start

# Check server status and recent logs
./scripts/dev-server.sh status

# View real-time logs
./scripts/dev-server.sh logs

# Restart server (after code changes)
./scripts/dev-server.sh restart

# Stop server
./scripts/dev-server.sh stop

# Alternative: Direct Python execution
python app.py
```

**Primary Interface**: http://localhost:5001/isee-ui (Web UI - recommended)

### Latest Features (August 2025)
- **Live API Calls Visualization**: Real-time display of individual combinations during execution
- **Enhanced Progress Monitoring**: Shows "LLM + Cognitive Framework + Knowledge Domain" per API call
- **Parallel Execution Support**: Visual feedback works seamlessly with 2.5-minute parallel processing
- **Professional UI**: Card-based active calls grid with animations and status indicators
- **COMPLETELY OVERHAULED Scoring System**: Revolutionary evaluation_scoring.py eliminates template failures and buzzword dominance
- **Template Failure Auto-Disqualification**: Automatically detects and disqualifies placeholder responses (score 0.05)
- **Enhanced Buzzword Penalty Engine**: Penalizes undefined jargon with -0.60 max penalty for technical audience focus
- **Quality Gates**: 5-tier filtering system prevents low-quality AI content from reaching final findings
- **Technical Audience Optimization**: Actionability (20%), Specificity (25%) weights prioritize implementable solutions

### Common Development Tasks

**Testing Core ISEE Logic:**
```bash
# Quick CLI analysis (testing)
python main.py --query "Your test question" --models 3 --config openrouter_config.json

# Full comprehensive analysis (production)
python main.py --query "Your research question" --models 14 --config openrouter_config.json --generate-reports
```

**Dependency Management:**
```bash
pip install -r requirements.txt
```

**Environment Setup:**
```bash
cp .env.template .env
# Edit .env with OPENROUTER_API_KEY=your_key_here
```

**Port Debugging:**
```bash
# Check if port 5001 is occupied
./scripts/check-ports.sh

# Kill processes on port 5001
./scripts/kill-port.sh 5001

# Clean all dev ports
./scripts/kill-dev-ports.sh
```

## Architecture Overview

### Core Application Files

**Primary Controllers:**
- `main.py` (2,304 lines) - Core ISEE execution engine and CLI orchestration
- `app.py` (2,304 lines) - Flask web interface with REST API endpoints

**AI Integration Layer:**
- `model_api_integration.py` (931 lines) - Unified gateway to 300+ AI models across 5 providers
- `openrouter_rankings_service.py` (413 lines) - Dynamic model ranking and caching system (legacy, no longer used, no longer needed)

**Cognitive Diversity Engine:**
- `cognitive_framework_visualizer.py` (373 lines) - Manages 11 cognitive frameworks (Analytical, Creative, Critical, Systems, etc.)
- `instruction_templates.py` - Template library for cognitive framework prompts
- `domain_manager.py` (410 lines) - Knowledge domain contextualization. Knowledge domains are dynamically generated based on the the user query provided for each run

**Intelligence & Analytics:**
- `reporting.py` (1,056 lines) - Result synthesis and comprehensive report generation
- `evaluation_scoring.py` (1,204 lines) - OVERHAULED scoring system with template failure detection, buzzword penalties, and technical audience optimization
- `cost_estimation.py` (747 lines) - Real-time cost/time estimation before execution
- `performance_tracker.py` (413 lines) - SQLite-based performance monitoring system

### Data Flow Architecture

```
Query Input → Cost Estimation → Framework Selection → Domain Context → 
Model Execution (60 calls) → Real-time Monitoring → Result Evaluation → 
Synthesis & Reporting → Performance Tracking → Analysis Reports
```

### Key Directories

**Configuration:**
- `openrouter_config.json` - Primary AI model configuration (300+ models via single API key)
- `.env` - Environment variables and API keys

**Data Storage:**
- `data/output/YYYY-MM/weekX/run_YYYYMMDD_HHMMSS/` - Organized run results
- `data/analysis_reports/` - Generated analysis reports with search capabilities  
- `data/performance_tracking.db` - SQLite database for performance analytics

**Development Tools:**
- `scripts/` - Development server management and utilities
- `tests/` - Test harnesses and validation scripts
- `archive/` - Legacy components and historical versions

**Web Interface:**
- `isee-ui.html` - Primary web interface
- `static/css/` - Styling and design tokens
- `static/js/` - Frontend JavaScript
- `templates/` - Additional HTML templates

## Key Technical Concepts

### Cognitive Diversity System
ISEE uses 10 distinct cognitive frameworks to ensure comprehensive analysis:
- **Analytical** (🔍) - Systematic problem breakdown
- **Creative** (💡) - Novel solution generation  
- **Critical** (⚖️) - Rigorous evaluation and challenges
- **Integrative** (🔗) - Cross-domain synthesis
- **Pragmatic** (🔧) - Implementation-focused analysis
- **First Principles** (🧱) - Fundamental assumptions examination
- **Systems** (🌐) - Holistic interconnection analysis
- **Contrarian** (🔄) - Alternative perspective generation
- **Historical** (📚) - Past patterns and lessons
- **Futurist** (🚀) - Forward-looking implications

### Model Distribution Strategy
- **14 Heterogeneous AI Models** chosen for distinct reasoning capabilities
- **Balanced Distribution** ensures equal model contribution (prevents dominance)
- **Provider Diversity**: Claude, GPT-4, Gemini, Llama, and 300+ others via OpenRouter
- **Graceful Fallback** mechanisms for API failures

### Quality Assurance System
**Multi-Criteria Scoring Framework:**
- Impact (30%) - Transformative potential and scale
- Novelty (25%) - Innovation and breakthrough thinking  
- Feasibility (20%) - Practical implementation considerations
- Comprehensiveness (15%) - Depth and multi-perspective coverage
- Specificity (10%) - Concrete details and precision

## Development Workflow

### Making Changes
1. **Start development server**: `./scripts/dev-server.sh start`
2. **Make code changes** in relevant files
3. **Test via web interface**: http://localhost:5001/isee-ui
4. **Monitor logs**: `./scripts/dev-server.sh logs` 
5. **Restart if needed**: `./scripts/dev-server.sh restart`

### Testing ISEE Logic
1. **Quick test**: Use CLI with `--models 3` for faster testing
2. **Full analysis**: Use Web UI for complete 60-call comprehensive analysis
3. **Monitor execution**: Real-time progress indicators show framework/model activity
4. **Review results**: Check `data/output/` for generated reports

### Performance Analysis
The system includes built-in performance tracking and self-analysis capabilities:
- **SQLite database**: Tracks all runs, performance metrics, API costs
- **Analysis reports**: Generated automatically for performance optimization
- **Model rankings**: Dynamic ranking system for model selection optimization

## Output Structure

### Primary Result Files
- `isee_result.md` - Primary comprehensive analysis (main deliverable)
- `queries_detailed_YYYYMMDD_HHMMSS.csv` - Complete query transparency log
- `model_performance.csv` - Performance metrics by model
- `combinations.csv` - All executed combinations with timing data

### Results Access Methods
1. **Web UI Quick View**: "📄 View Analysis (Quick)" button
2. **Complete Package Download**: "📥 Download Complete Package" button  
3. **Direct File Access**: `data/output/run_YYYYMMDD_HHMMSS/` directory

## Configuration Notes

### OpenRouter Integration (Recommended)
- **Single API Key**: Access 300+ models from all major providers
- **Unified Billing**: One account for Claude, GPT-4, Gemini, Llama, etc.
- **Pre-configured Collections**: Carefully curated model portfolios for cognitive diversity

### Environment Variables
```bash
OPENROUTER_API_KEY=your_openrouter_key_here
# Optional individual provider keys:
# ANTHROPIC_API_KEY=your_anthropic_key
# OPENAI_API_KEY=your_openai_key  
# GOOGLE_API_KEY=your_google_key
```

### Execution Settings
- **Standard Analysis**: 60 calls (~15 minutes, ~$4.80)
- **Quick Testing**: 20-30 calls (~5 minutes, ~$1.60)
- **Comprehensive Research**: 60+ calls with custom parameters

## Troubleshooting

### Common Issues
- **Port 5001 occupied**: Use `./scripts/kill-port.sh 5001` or `./scripts/check-ports.sh`
- **API key errors**: Verify OpenRouter key at https://openrouter.ai/keys
- **Memory issues**: 60-call analysis requires adequate system resources
- **Slow first execution**: Model caching improves subsequent performance

### Debugging Tools
- **Real-time logs**: `./scripts/dev-server.sh logs`
- **Server status**: `./scripts/dev-server.sh status`
- **Error detection**: Built-in `api_error_detector.py` system
- **Performance tracking**: Check `data/performance_tracking.db`

## Key Design Principles

### Cognitive Diversity Over Consensus
ISEE is designed to reveal contradictory and complementary perspectives rather than seeking agreement. The goal is intellectual insurance against single-perspective limitations.

### High-Performance Parallel Execution
Advanced AsyncIO-based parallel execution system delivers 10x performance improvements. 66-call comprehensive analyses complete in 3-5 minutes vs 30+ minutes with intelligent rate limiting across all major AI providers.

### Economic Intelligence
Transparent cost management with real-time estimation before execution. Users know exactly what each analysis will cost before running.

### Academic Rigor
Professional interface optimized for research contexts with scholarly aesthetics and comprehensive documentation.

### Systematic Exploration
Every analysis runs the same comprehensive 60-call framework to ensure reliable cognitive diversity and prevent cherry-picking results.

## Development Dependencies

Core dependencies from `requirements.txt`:
```
requests>=2.28.0          # HTTP client
anthropic>=0.5.0          # Claude API
openai>=1.0.0            # OpenAI API  
flask>=2.3.0             # Web framework
rich>=13.0.0             # CLI formatting
pandas>=1.5.0            # Data analysis
matplotlib>=3.6.0        # Visualization
aiohttp>=3.8.0           # Async HTTP
tiktoken>=0.5.0          # Token counting
psutil>=5.9.0            # System monitoring
```

## File Organization

The codebase follows a modular architecture with clear separation of concerns:
- **Core Logic**: `main.py` orchestrates the entire ISEE process
- **Web Interface**: `app.py` provides Flask-based web demo  
- **AI Integration**: `model_api_integration.py` handles all AI model communications
- **Analysis Tools**: Separate modules for scoring, reporting, and performance tracking
- **Historical Data**: Comprehensive archiving in `data/output/` with organized folder structure

Total Core Codebase: ~11,000 lines across 9 key modules, designed for both accessibility and sophisticated multi-perspective research capabilities.