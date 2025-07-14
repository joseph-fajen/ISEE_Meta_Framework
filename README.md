# ISEE Meta Framework

**The Idea Synthesis and Extraction Engine • Systematic Multi-Perspective Research Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)](https://flask.palletsprojects.com/)

---

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/your-username/ISEE_Meta_Framework.git
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

**🧠 10 Heterogeneous AI Models**  
Each chosen for distinct reasoning capabilities and knowledge synthesis patterns

**🔍 10 Cognitive Framework Lenses**  
From analytical rigor to contrarian deconstruction, ensuring comprehensive perspective coverage

**📊 Dynamic Knowledge Domain Mapping**  
Real-time identification of relevant expertise areas based on query complexity

**⚡ Automated Perspective Synthesis**  
Cluster-based organization revealing complementary, contradictory, and emergent insights

### The Process

1. **Query Input**: Enter your research question or complex problem
2. **Framework Selection**: Choose cognitive approaches (or use Smart Auto-Pilot)
3. **Model Orchestration**: ISEE systematically explores your question across models and frameworks
4. **Insight Synthesis**: Results are organized into coherent clusters revealing different perspectives
5. **Comprehensive Output**: Download complete analysis with insights, scoring, and visual reports

---

## 🎨 Web Interface Features

### Modern, Intuitive Design
- **Professional academic aesthetic** optimized for research contexts
- **Real-time progress tracking** with cognitive framework indicators
- **Smart Auto-Pilot mode** for effortless comprehensive analysis
- **Individual model selection** for targeted exploration

### Comprehensive Analysis Standard
- **60 systematic calls** across models and frameworks
- **~15 minutes** processing time for maximum cognitive diversity
- **True multi-perspective exploration** beyond single-model limitations

### Advanced Configuration
- **300+ AI models** via OpenRouter integration
- **Flexible analysis depth**: 30, 45, or 60 LLM calls
- **Dynamic domain generation** based on query context
- **Real-time cost estimation** and progress monitoring

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- OpenRouter API key (manages 300+ models with single key)
- Git

### Step-by-Step Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/ISEE_Meta_Framework.git
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
3. **Choose analysis depth**: 30 (Balanced), 45 (Deep), or 60 (Comprehensive) calls
4. **Select mode**: 
   - **Smart Auto-Pilot**: Automatic framework selection
   - **Individual Selection**: Choose specific models and frameworks
5. **Start analysis**: Click "Start Analysis" and watch real-time progress
6. **Review results**: Explore organized insights and download comprehensive reports

### Advanced Features

**Individual Model Selection**:
- Access 300+ models organized by provider and capability
- Mix and match models for specific research needs
- Real-time cost estimation for budget planning

**Cognitive Framework Customization**:
- Analytical, Creative, Critical, Integrative, Pragmatic
- First Principles, Systems, Contrarian, Historical, Futurist
- Each framework reveals different aspects of your query

**Professional Server Management**:
```bash
./scripts/dev-server.sh start    # Start server
./scripts/dev-server.sh status   # Check status
./scripts/dev-server.sh logs     # View logs
./scripts/dev-server.sh stop     # Stop server
```

---

## 🔧 Configuration

### Core Configuration Files

- **`openrouter_config.json`**: AI model definitions and collections
- **`unified_config.json`**: System-wide configuration
- **`.env`**: Environment variables and API keys

### Server Scripts

ISEE includes professional development scripts for robust server management:

- **`scripts/dev-server.sh`**: Complete server lifecycle management
- **`scripts/check-ports.sh`**: Port conflict detection and resolution
- **`scripts/dev-aliases.sh`**: Convenient command aliases

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
*"How might we redesign urban transportation systems to optimize for both environmental sustainability and social equity?"*

### Strategic Planning
*"What are the unintended consequences of implementing AI-driven hiring processes across different cultural contexts?"*

### Innovation Exploration
*"What would happen if we approached scientific literacy through orchestral performances designed to help audiences emotionally experience scientific principles?"*

Each query reveals insights across multiple cognitive clusters, ensuring comprehensive understanding beyond single-perspective limitations.

---

## 🔍 Technical Architecture

### Backend Components
- **Flask web server** with RESTful API endpoints
- **OpenRouter integration** for 300+ AI model access
- **Dynamic model ranking** and performance tracking
- **Automated report generation** with HTML output

### Frontend Features
- **Self-contained HTML interface** with modern CSS/JavaScript
- **Real-time progress monitoring** with framework indicators
- **Responsive design** optimized for research workflows
- **Professional typography** and academic aesthetics

### Data Management
- **SQLite performance tracking** for model optimization
- **Configurable output formats** (JSON, Markdown, HTML)
- **Persistent logging** for debugging and analysis
- **Session-based state management**

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