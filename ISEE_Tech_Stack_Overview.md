# ISEE Tech Stack Overview

## **Core Architecture**

**Frontend:**

- **Static HTML/CSS/JavaScript**: `isee-ui.html` - Self-contained single-page application

- **Responsive Design**: Professional charcoal/copper gradient theme optimized for research context

- **Real-time Updates**: AJAX-based communication with Flask backend

- **Access Method**: Served at `http://localhost:5001/isee-ui` (requires Flask server)

**Backend:**

- **Python Flask**: Web server on port 5001 (`app.py`)

- **Core Logic**: `main.py` - ISEE execution engine and CLI interface

- **Model Configuration**: Static model selection - 12 models hand-curated in `openrouter_config.json`

- **Cost Analysis**: `cost_estimation.py` - Real-time pricing calculations (not currently in the implementation but could be)

- **Visualization**: `cognitive_framework_visualizer.py` - Framework rendering system

## **External Integrations**

**LLM Providers:**

- **Primary**: OpenRouter API (300+ models with single API key)

- **Models**: 12 strategically hand-selected models across providers (OpenAI, Anthropic, Google, etc.)

- **Legacy**: `openrouter_rankings_service.py` exists but dynamic ranking no longer used

- **Fallback**: Ollama support for local model execution (optional)

**Data Storage:**

- **Configuration**: JSON-based configuration files (`openrouter_config.json`)

- **Results**: Markdown and JSON output formats

- **Performance**: SQLite database for execution tracking (`data/performance_tracking.db`)

## **Development Infrastructure**

**Dependencies:**

- **Core**: Flask, requests, python-dotenv (see `requirements.txt` - 9 total dependencies)

- **Minimal footprint**: No heavy ML libraries or complex databases required

**Development Tools:**

- **Scripts**: `/scripts/` directory with server management utilities

  - `dev-server.sh`: Main development server management

  - `kill-port.sh`, `check-ports.sh`: Port management utilities

- **Testing**: `tests/test_runner.py` - Parameter validation and bug testing

**Deployment:**

- **Local Development**: Python development server

- **Production Ready**: Standard Flask deployment patterns supported

- **Security**: All processing local, API calls only to enterprise-approved LLM providers

## **Key Technical Features**

**Multi-Model Orchestration:**

- **Exhaustive Matrix Generation**: Creates Cartesian product of all possible combinations (Models × Frameworks × Domains)

- **Potential Scale**: With 12 models, 11 frameworks, 3 domains = 396 total possible combinations

- **Stratified Sampling**: System samples 66 combinations using framework-balanced selection to ensure representation across all dimensions

- **Pre-Execution Randomization**: Selected 66 combinations shuffled before execution for diverse processing order

- **Sequential Execution**: Each combination executes with predetermined Model + Framework + Domain (real-time UI indicators reflect these components)

- **Test Mode**: Quick validation with 11 combinations (reduced scope for testing)

- Dynamic query variation using LLM-powered analysis

- **Execution Flow**: Deterministic sampling → random shuffling → sequential processing (not dynamic selection during runtime)

**Enterprise Integration:**

- API key management through environment variables

- No proprietary data storage - results exported to standard formats

- Compatible with existing enterprise AI licensing agreements

**Performance:**

- Concurrent execution capability

- Real-time progress tracking and cost estimation

- Typical execution time: 15-25 minutes for full 66-call analysis