# ISEE Meta Framework

**The Idea Synthesis and Extraction Engine • Systematic Multi-Perspective Research Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)](https://flask.palletsprojects.com/)

---

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/joseph-fajen/ISEE_Meta_Framework.git
cd ISEE_Meta_Framework
pip install -r requirements.txt

# 2. Configure API access
cp .env.template .env
# Edit .env with your OpenRouter API key

# 3. Start the server
./scripts/dev-server.sh start

# 4. Open browser
open http://localhost:5001/isee-ui
```

**That's it!** The ISEE web interface is now running with 300+ AI models and 10 cognitive frameworks ready for systematic multi-perspective research.

---

## 📖 What is ISEE?

ISEE transforms how we approach complex research by moving beyond single-perspective AI interactions to **systematic cognitive exploration**. Instead of asking one AI model for one answer, ISEE orchestrates multiple AI models through diverse cognitive frameworks to reveal breakthrough insights hiding in the spaces between different ways of thinking.

### The Core Innovation

**Traditional AI**: Ask a question → Get an answer → Accept cognitive limitations  
**ISEE**: Ask a question → **Systematically explore 60 perspectives** → Discover insights you couldn't anticipate

### Why Cognitive Diversity Matters

Complex problems resist simple solutions. The most transformative breakthroughs often emerge from the intersection of contradictory perspectives. ISEE provides **intellectual insurance against the cognitive limitations of homogeneous analysis**—whether single-model or consensus-based approaches.

---

## 🎯 How ISEE Works

### The Architecture

**🧠 14 Heterogeneous AI Models**  
Each chosen for distinct reasoning capabilities and knowledge synthesis patterns

**🔍 10 Cognitive Framework Lenses**  
From analytical rigor to contrarian deconstruction, ensuring comprehensive perspective coverage

**📊 Dynamic Knowledge Domain Mapping**  
Real-time identification of relevant expertise areas based on query complexity

**⚡ Automated Perspective Synthesis**  
Cluster-based organization revealing complementary, contradictory, and emergent insights

### The Process

1. **Enter your query**: Simply type your research question or complex problem
2. **Click "ANALYZE WITH ISEE"**: That's it - no configuration needed
3. **Watch real-time progress**: See live indicators as ISEE systematically explores 60 perspectives across models and frameworks
4. **Review comprehensive results**: Access organized insights, scoring, and visual reports
5. **Download or view**: Multiple format options for your complete analysis

---

## 🎨 Web Interface Features

### Modern, Intuitive Design
- **Professional academic aesthetic** optimized for research contexts
- **Real-time progress tracking** with cognitive framework indicators
- **Ultra-simplified interface**: Just enter query and click analyze
- **14 LLMs configured automatically** for targeted exploration

### Comprehensive Analysis Standard
- **60 systematic calls** across models and frameworks automatically
- **~15 minutes** processing time for maximum cognitive diversity
- **Real-time indicators** show progress across all frameworks and models
- **True multi-perspective exploration** beyond single-model limitations

### Advanced Features
- **300+ AI models** via OpenRouter integration
- **Dynamic domain generation** based on query context
- **Multiple result formats** with instant viewing and download options
- **Professional report generation** with academic styling

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- OpenRouter API key (manages 300+ models with single key)
- Git

### Step-by-Step Installation

```bash
# 1. Clone the repository
git clone https://github.com/joseph-fajen/ISEE_Meta_Framework.git
cd ISEE_Meta_Framework

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.template .env
```

### Configure API Access

Edit `.env` file:
```bash
OPENROUTER_API_KEY=your_openrouter_key_here
```

**Get your OpenRouter API key**: [https://openrouter.ai/keys](https://openrouter.ai/keys)

### Launch ISEE

```bash
# Professional server management (recommended)
./scripts/dev-server.sh start

# Or direct Python execution
python app.py
```

**Access the interface**: http://localhost:5001/isee-ui

---

## 📋 Usage Guide

### Basic Usage

1. **Open ISEE**: Navigate to http://localhost:5001/isee-ui
2. **Enter your query**: Type your research question or complex problem
3. **Click "ANALYZE WITH ISEE"**: No configuration needed - the system automatically runs 60 comprehensive calls
4. **Watch real-time progress**: See live indicators showing progress across all cognitive frameworks and models
5. **Review results**: Explore organized insights and download comprehensive reports in multiple formats

### Advanced Features

**Carefully Curated LLM Portfolio**:
- Pre-selected set of high-performance models optimized for cognitive diversity
- Automatically balanced across different reasoning capabilities and knowledge synthesis patterns
- No user configuration needed - optimal model selection handled automatically

**Comprehensive Cognitive Framework Coverage**:
- Analytical, Creative, Critical, Integrative, Pragmatic
- First Principles, Systems, Contrarian, Historical, Futurist
- Each framework reveals different aspects of your query across all selected models

**Server Management**:
```bash
./scripts/dev-server.sh start    # Start server
./scripts/dev-server.sh status   # Check status and recent logs
./scripts/dev-server.sh restart  # Restart server (useful after updates)
./scripts/dev-server.sh logs     # Follow real-time logs
./scripts/dev-server.sh stop     # Stop server
```

---

## 🔧 Configuration

### Core Configuration Files

- **`openrouter_config.json`**: Primary configuration designed for simple setup using a single OpenRouter API key. While OpenRouter provides access to a large number of LLMs, ISEE uses a carefully selected set optimized for cognitive diversity so users don't need to think about which models to use
- **`.env`**: Environment variables and API keys

### Available Scripts

ISEE includes comprehensive development scripts for server management and utilities:

- **`scripts/dev-server.sh`**: Complete server lifecycle management (start, stop, restart, status, logs)
- **`scripts/check-ports.sh`**: Port conflict detection and resolution
- **`scripts/kill-port.sh`**: Kill processes on specific ports
- **`scripts/kill-dev-ports.sh`**: Clean up development ports
- **`scripts/dev-aliases.sh`**: Convenient command aliases for faster workflows
- **`scripts/install-aliases.sh`**: Install development aliases system-wide

### Logging

- **`isee-ui.log`**: Application logs and debugging information
- **`dev-server.log`**: Server management logs
- All logs excluded from git via `.gitignore`

---

## 🎯 Who Should Use ISEE?

### Researchers & Academics
Exploring multifaceted problems requiring assumption-challenging and perspective synthesis

### Strategic Decision-Makers
Professionals whose choices require comprehensive analysis of unintended consequences and alternative frameworks

### Innovation Architects
Boundary-pushers seeking breakthrough insights that emerge from cognitive collision rather than linear thinking

---

## 💡 Example Use Cases

### Research Questions
*"How could blockchain governance models evolve to systematically incorporate insights from classical music ensemble leadership—where conductors, concertmasters, and section leaders create dynamic decision-making hierarchies that balance individual expression with collective precision?"*

### Strategic Innovation  
*"What would emerge if we designed smart contract development education programs inspired by conservatory training methods—combining technical rigor with artistic intuition, peer mentorship traditions, and performance-under-pressure experiences that classical musicians develop?"*

### Cross-Domain Synthesis
*"How might sustainable ecosystem management practices inform the design of stake pool operator communities, where long-term thinking, resource stewardship, and symbiotic relationships create resilient networks that adapt to environmental changes while maintaining core stability?"*

Each query reveals insights across multiple cognitive clusters, ensuring comprehensive understanding beyond single-perspective limitations.

---

## 🔍 Technical Architecture

### Core Python Capabilities

**🎯 Primary Controllers:**
- **`main.py`** (2,304 lines) - Core execution engine and CLI orchestration
- **`app.py`** (2,304 lines) - Flask web interface with REST API endpoints

**🤖 AI Integration Layer:**
- **`model_api_integration.py`** (931 lines) - Unified gateway to 300+ AI models across 5 providers
- **`openrouter_rankings_service.py`** (413 lines) - Dynamic model ranking and caching

**🧠 Cognitive Diversity Engine:**
- **`cognitive_framework_visualizer.py`** (373 lines) - Manages 10 cognitive frameworks (Analytical, Creative, Critical, etc.)
- **`domain_manager.py`** (410 lines) - Knowledge domain contextualization

**📊 Intelligence & Analytics:**
- **`reporting.py`** (1,056 lines) - Result synthesis and comprehensive report generation
- **`cost_estimation.py`** (747 lines) - Real-time cost/time estimation
- **`performance_tracker.py`** (413 lines) - SQLite-based performance monitoring

### Data Flow

```
Query → Cost Estimation → Framework Selection → Domain Context → 
Model Execution → Real-time Monitoring → Result Evaluation → 
Synthesis & Reporting → Performance Tracking
```

### Key Technical Innovations

🔬 **Cognitive Diversity**: 10 distinct thinking frameworks ensure comprehensive analysis beyond single-perspective limitations

🌐 **Unified Model Access**: Single interface to 300+ models via OpenRouter with graceful fallback mechanisms

💰 **Economic Intelligence**: Transparent cost management and real-time estimation before execution

🎨 **Academic Design**: Professional interface optimized for research contexts with scholarly aesthetics

📈 **Continuous Learning**: Performance analytics and model ranking drive systematic optimization

**Total Core Codebase**: ~11,000 lines with 9 dependencies, designed for both accessibility and sophisticated multi-perspective research

---

## 🚀 Development

### Development Workflow

```bash
# Start development server
./scripts/dev-server.sh start

# View real-time logs
./scripts/dev-server.sh logs

# Check system status
./scripts/dev-server.sh status

# Stop server
./scripts/dev-server.sh stop
```

### Repository Structure

```
ISEE_Meta_Framework/
├── isee-ui.html              # Primary web interface
├── app.py                    # Flask backend server
├── main.py                   # Core ISEE logic
├── requirements.txt          # Python dependencies
├── scripts/                  # Development tools
├── content/                  # Documentation
├── data/                     # Output and tracking
├── prompts/                  # Template library
└── archive/                  # Historical versions
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly using the web interface
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🏗️ Built By

**Joseph Fajen** - Senior Technical Writer at IOHK  
Developed using Claude Code through months of architectural contemplation, seeking to democratize multi-perspective research methodology.

---

## 🌟 Philosophy

ISEE represents a fundamental shift from **information retrieval** to **perspective archaeology**—systematically excavating the full cognitive territory surrounding complex questions. It's designed for moments when you need more than expert responses or agreement—when you need to discover perspectives you couldn't formulate, assumptions you didn't know you held, and possibilities hiding in intellectual blind spots.

**Try ISEE. Explore systematically. Discover what cognitive diversity reveals.**

---

*Ready to move beyond single-perspective limitations? Start your systematic multi-perspective research journey today.*