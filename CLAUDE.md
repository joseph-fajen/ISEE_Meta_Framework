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

### Latest Features (January 2025)
- **🔥 DUAL API PROVIDER SYSTEM**: Complete implementation enabling seamless switching between OpenRouter and Globant Enterprise AI with intelligent hybrid mode and automatic fallback
- **🏢 Enterprise AI Integration**: Full Globant Enterprise AI support with enhanced security, compliance features, and curated model portfolio
- **⚡ Hybrid Provider Mode**: Intelligent provider selection based on performance metrics, health monitoring, and cost optimization
- **💰 Cross-Provider Cost Analysis**: Real-time cost comparison and optimization recommendations across API providers
- **🔄 Automatic Failover**: Seamless provider switching on failures with health-based selection and performance tracking
- **🎛️ Professional Provider UI**: Clean three-card provider selection interface with real-time status indicators
- **📊 Provider Health Monitoring**: Live tracking of API performance, success rates, and response times
- **Query Enhancement System**: AI-powered query optimization with 15-25% score improvements using validated patterns
- **Auto-Apply Enhancement UX**: One-click enhancement selection with optional auto-apply for streamlined workflow
- **Prominent Enhancement UI**: Visually striking green gradient apply button with icons and animations
- **Enhancement Effectiveness Tracking**: SQLite-based analytics system tracks query improvement success rates
- **Parallel Processing Optimization**: 4-minute full analysis (66 calls) and 1-minute validation (11 calls)
- **Cost-Optimized Execution**: 90% cost reduction - $0.50 for full analysis, $0.07 for validation
- **Live API Calls Visualization**: Real-time display of individual combinations during execution
- **Enhanced Progress Monitoring**: Shows "LLM + Cognitive Framework + Knowledge Domain" per API call
- **Professional UI**: Card-based active calls grid with animations and status indicators
- **COMPLETELY OVERHAULED Scoring System**: Revolutionary evaluation_scoring.py eliminates template failures and buzzword dominance
- **Template Failure Auto-Disqualification**: Automatically detects and disqualifies placeholder responses (score 0.05)
- **Enhanced Buzzword Penalty Engine**: Penalizes undefined jargon with -0.60 max penalty for technical audience focus
- **Quality Gates**: 5-tier filtering system prevents low-quality AI content from reaching final findings
- **Technical Audience Optimization**: Actionability (20%), Specificity (25%) weights prioritize implementable solutions
- **Rank-Based Raw Response Files**: Automatic renaming of raw response files with rank prefixes (01_, 02_, etc.) based on evaluation scores for easy identification and sharing of top-performing responses
- **Enhanced Visual Illumination System**: Fixed parallel execution visual display to accurately reflect true cognitive diversity with improved model/framework matching and duplicate prevention
- **Cognitive Diversity Explorer**: Revolutionary platform with pixel-perfect design alignment - seamlessly integrated UI for exploring all 66 raw responses with professional enterprise aesthetics and enhanced metadata filtering
- **Hybrid Smart Curation System**: Complete research annotation platform with stars, tags, notes, favorites, and reviewed tracking
- **Run-Specific Storage**: Isolated annotation storage per query run for clean research workflow
- **Advanced Export**: "Download My Analysis Notes" with comprehensive JSON export including run metadata
- **Remote Deployment Compatibility**: Enhanced error handling and robust subprocess execution for seamless remote deployment

### Common Development Tasks

**Testing Core ISEE Logic:**
```bash
# Quick CLI analysis (testing) - with provider selection
python main.py --query "Your test question" --models 3 --provider openrouter

# Full comprehensive analysis with Globant Enterprise AI
python main.py --query "Your research question" --models 14 --provider globant --generate-reports

# Intelligent hybrid mode with automatic provider selection
python main.py --query "Your research question" --models 14 --provider hybrid --generate-reports

# Legacy usage (still supported - defaults to OpenRouter)
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

### Strategic Analysis & Planning Documents

**DSPy Integration Research:**
- `docs/dspy_integration_analysis.md` - Comprehensive analysis of DSPy framework integration potential for ISEE response synthesis optimization. Includes detailed evaluation of query optimization vs. response synthesis use cases, 5 implementation approaches with code examples, risk assessment, and phased implementation strategy.

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

### Globant Enterprise AI Integration
- **132 AI Models**: Enterprise-grade model portfolio with enhanced security
- **API Documentation Sources**:
  - **GitHub Repository**: https://github.com/genexuslabs/saia-ingest
  - **Official Wiki**: https://wiki.genexus.com/enterprise-ai/wiki?20
- **API Configuration**:
  - Base URL: `https://api.saia.ai`
  - Endpoint: `/chat/completions` (not `/v1/chat/completions`)
  - Authentication: Bearer token with API key
  - Model Format: `provider/model` (e.g., `anthropic/claude-3-5-haiku-20241022`)

### Environment Variables
```bash
OPENROUTER_API_KEY=your_openrouter_key_here

# Globant Enterprise AI (alternative provider)
GLOBANT_API_KEY=your_globant_api_key_here
GLOBANT_ORG_ID=your_organization_id
GLOBANT_BASE_URL=https://api.saia.ai

# Optional individual provider keys:
# ANTHROPIC_API_KEY=your_anthropic_key
# OPENAI_API_KEY=your_openai_key  
# GOOGLE_API_KEY=your_google_key
```

### Execution Settings
- **Standard Analysis**: 66 calls (~4 minutes, ~$0.50)
- **Quick Testing**: 11 calls (~1 minute, ~$0.07)
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

## 🧠 Cognitive Diversity Explorer - ✅ FULLY INTEGRATED & DESIGN ALIGNED

**Revolutionary platform that transforms ISEE from "smart synthesis tool" to "cognitive diversity exploration platform" - NOW SEAMLESSLY INTEGRATED INTO MAIN WEB UI WITH PIXEL-PERFECT DESIGN CONSISTENCY**

### 🎨 Enterprise Design System Alignment (August 2025)
- **Sophisticated Color Palette**: Migrated from bright purple/blue to professional amber/slate enterprise scheme
- **Typography Excellence**: Enhanced with SF Pro Display font stack and improved hierarchy
- **Premium Card Design**: Glass morphism effects with backdrop filters and sophisticated shadow systems
- **Consistent Spacing**: Professional padding/margin scale matching main ISEE UI exactly
- **Interactive Polish**: Enhanced hover states, focus treatments, and accessibility features
- **Visual Cohesion**: Both interfaces now provide identical professional appearance

### What is the Cognitive Diversity Explorer?

The Cognitive Diversity Explorer provides transparent access to all 66 unique AI thinking approaches from any ISEE analysis run. Instead of only seeing the final synthesis, users can explore, filter, compare, and discover insights across all raw responses with rich metadata and interactive tools.

### 🚀 **INTEGRATED ACCESS - NEW PRIMARY METHOD**

**The Cognitive Diversity Explorer is now seamlessly integrated into the main ISEE web interface!**

```bash
# 1. Run ISEE analysis through main web UI
http://localhost:5001/isee-ui

# 2. After analysis completion, click the third result option:
#    📄 View Analysis (Quick) | 📥 Download Package | 🧠 Explore Cognitive Diversity

# 3. Explorer opens automatically with all 66 responses loaded and ready to explore!
```

### 🛠️ **Alternative Launch Methods (for direct access)**

```bash
# Direct launch for any existing run
python launch_cognitive_explorer.py data/output/run_YYYYMMDD_HHMMSS

# CLI exploration and analysis
python cognitive_diversity_browser.py data/output/run_YYYYMMDD_HHMMSS/cognitive_diversity_index.json
```

### Core Components

**Files Created:**
- `cognitive_diversity_metadata_schema.json` - Complete 40+ field metadata specification
- `cognitive_diversity_extractor.py` - Metadata extraction and indexing system
- `cognitive_diversity_browser.py` - Interactive CLI exploration tool
- `cognitive_diversity_web.html` - Rich web interface template
- `launch_cognitive_explorer.py` - Web server and data integration
- `COGNITIVE_DIVERSITY_README.md` - Complete documentation and usage guide

### Enhanced Metadata Schema (40+ Fields)

**Core Metadata:**
- Performance scores (overall, feasibility, impact, novelty, etc.)
- Cognitive framework and thinking style analysis
- Model provider specializations and execution metrics

**Cognitive Analysis:**
- Framework specialization (what each approach does uniquely well)
- Thinking style (analytical, creative, contrarian, systematic, etc.)
- Innovation approach (incremental, disruptive, paradigm_shift, synthesis)
- Contrarian elements (ways responses challenge conventional thinking)

**Content Analysis:**
- Key concepts (extracted technologies, methodologies, frameworks)
- Approach categories (implementation, strategy, research, comparison)
- Success metrics (specific measurable criteria mentioned)
- Tone characteristics (formal, practical, innovative, ambitious)

**Discoverability:**
- Search keywords for enhanced discoverability
- Cognitive clusters (groupings of similar thinking approaches)
- Similarity relationships (related, contrasting, complementary responses)

### Key Use Cases

**🔍 Research & Discovery:**
- Study cognitive diversity patterns in AI responses
- Find alternative approaches to implementation challenges
- Discover breakthrough ideas that scored lower initially

**🎭 Framework Deep Dive:**
- Compare how different cognitive frameworks approach the same problem
- Identify framework specializations and optimal use cases
- Discover framework combinations that complement each other

**🤖 Model Specialization Analysis:**
- Explore how different AI models excel at different cognitive approaches
- Find model-framework combinations that produce exceptional results
- Identify model biases and blind spots

**🔄 Contrarian Perspective Discovery:**
- Find responses that challenge conventional wisdom
- Explore minority viewpoints that didn't make the synthesis
- Identify alternative approaches dismissed by mainstream thinking

### Web Interface Features

**Multi-Dimensional Filtering:**
- Score-based: Filter by performance tiers or score ranges
- Cognitive: Filter by frameworks, thinking styles, innovation approaches
- Technical: Filter by model providers, domains, complexity levels
- Content: Search by concepts, technologies, keywords

**Interactive Response Cards:**
- Performance metrics visualization
- Cognitive framework and model badges  
- Key concepts and approach categories
- Content preview and expandable details
- Similarity and relationship indicators

**Discovery Modes:**
- Cognitive Diversity Mapping (visual clustering of thinking approaches)
- Performance Analysis (score vs innovation plotting)
- Framework Effectiveness (systematic framework comparison)
- Contrarian Exploration (alternative viewpoint discovery)

### Integration with Main ISEE Workflow

The Cognitive Diversity Explorer seamlessly integrates with the main ISEE workflow:

1. **Run ISEE Analysis**: Generate 66 responses with standard ISEE process
2. **Extract Metadata**: `python cognitive_diversity_extractor.py <run_directory>`
3. **Explore Diversity**: Launch web or CLI tools to explore all perspectives
4. **Discover Insights**: Find hidden gems and alternative approaches
5. **Inform Decisions**: Use cognitive diversity insights for better research outcomes

### Competitive Advantage

This transforms ISEE into something **unprecedented in the AI space**:
- **No other AI system** offers transparent access to 66 different thinking approaches
- **Unique value proposition**: From "smart AI answers" to "cognitive diversity exploration"
- **Defensible differentiation**: Complex to replicate, high switching costs
- **Research platform**: Valuable for academic and enterprise research applications

### Development Status

**Current Status:** Fully operational and battle-tested
- ✅ Complete metadata extraction system
- ✅ Interactive web interface with real-time data serving
- ✅ CLI tools for programmatic analysis
- ✅ Comprehensive documentation and examples
- ✅ Integration with existing ISEE workflow

**Next Development Phase:**
- Semantic search and similarity clustering
- Advanced visualization with D3.js cognitive mapping
- User contribution systems for community-driven insights
- Direct integration with main ISEE UI for seamless workflow

## Git Branch Management & Development Workflow

### Current Repository Structure (August 2025)

**Main Development Branch (`main`)**
- **Status**: Clean, with major UI enhancements completed (August 2025)
- **Latest Updates**: Enhanced user instructions and dramatically improved combinatorial visualization for parallel execution
- **UI Improvements**: Professional 6-step user workflow guide and restored visual richness of 66 unique combinations
- **Visual System**: Enhanced parallel execution choreography with real-time combination tracking and connection effects
- **Purpose**: Stable development branch for core ISEE framework enhancements
- **Next Session**: Ready for further optimization or new feature development

**Pipeline Research Branch (`feature/raw-response-analysis-to-csv-pipeline`)**
- **Status**: Complete preservation of experimental pipeline work
- **Content**: 87 files, 11,823+ insertions covering CSV generation and raw response analysis
- **Components**: 
  - Hybrid ensemble analysis integration with Claude Sonnet 4
  - Automated CSV generation from AI responses
  - Pipeline testing and debugging scripts (62+ test files)
  - Raw response analysis and structured data extraction
  - Enhanced error handling and production reliability features
- **Purpose**: Experimental line exploring structured data extraction from ISEE responses
- **Access**: `git checkout feature/raw-response-analysis-to-csv-pipeline`

### Branch Management Best Practices

**For Main ISEE Development:**
```bash
# Ensure you're on main and up-to-date
git checkout main
git status  # Should show "working tree clean"

# Start new feature development
git checkout -b feature/your-new-feature
# ... make changes ...
git commit -m "your changes"
```

**For Pipeline Research Continuation:**
```bash
# Switch to pipeline branch to continue CSV/analysis work
git checkout feature/raw-response-analysis-to-csv-pipeline

# Verify all pipeline work is present
ls data/pipeline_results/  # Should show CSV files
ls scripts/*pipeline*      # Should show pipeline scripts
```

**For Session Handoffs:**
- Main branch always clean and GitHub-synchronized
- Experimental work preserved in feature branches
- Comprehensive commit messages with session context
- CLAUDE.md updated to reflect current development state