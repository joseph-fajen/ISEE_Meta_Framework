# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ISEE Meta Framework Overview

The Idea Synthesis and Extraction Engine (ISEE) is a meta-framework for innovation that systematically leverages AI to generate, evaluate, and extract high-value concepts across any domain. Rather than using AI in a single-prompt manner, this framework creates a deliberate combinatorial approach that maximizes the exploration of possibility space before filtering for the most promising ideas.

### Key Components

- **Input Layer** (`query_generator.py`, `instruction_templates.py`, `domain_manager.py`) - Manages input diversity
- **Orchestration Layer** (`main.py`, `model_api_integration.py`) - Handles combinations and execution
- **Evaluation Layer** (`evaluation_scoring.py`) - Analyzes and scores results
- **Extraction Layer** (in `main.py`) - Synthesizes and refines ideas
- **Command Wizard** (`command_wizard.py`) - Interactive UI for command generation

### Current Development Focus

The current development focus is on implementing the UX Enhancement Roadmap detailed in `specs/Command-Wizard-Integrated-UX-Enhancement-Dev-Roadmap.md`. This roadmap outlines a comprehensive plan for enhancing the user experience of the Command Wizard.

**Immediate Priority - Step 1.1: Cost and Time Estimation** (from the roadmap):
- Developing algorithms to estimate API costs based on parameter selections
- Creating execution time estimation based on combination count and model selection
- Implementing warning systems for potentially expensive operations
- Adding visual indicators showing how parameter changes affect costs
- Displaying estimated costs alongside parameter selection options

## Common Commands

### Environment Setup

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the ISEE Framework

```bash
# Basic run with simulation mode (no API keys required)
python main.py --query "Your query here" --simulate

# Run with real API integration (requires API keys)
python main.py --config sample_config.json --query "Your query here"

# Run with max model diversity (balanced representation)
python main.py --config unified_config.json --query "Your query" --models 3 --balanced-models

# Run with dry-run mode to preview without executing
python main.py --query "Your query" --dry-run
```

### Specifying Parameters

```bash
# Set domain focus
python main.py --query "Your query" --domain "Technology Innovation"

# Control model count
python main.py --query "Your query" --models 3

# Set instruction templates count
python main.py --query "Your query" --instructions 4

# Set variation count
python main.py --query "Your query" --variations 2

# Limit combinations
python main.py --query "Your query" --max-combinations 12

# Control sampling method
python main.py --query "Your query" --sampling-method stratified
```

### Running the Command Wizard

```bash
# Run the interactive command wizard
python command_wizard.py
```

### Testing

```bash
# Run instruction templates test
python test_instruction_templates.py

# Run command wizard test
python test_command_wizard.py

# Run command wizard test harness
python tests/command_wizard/test_harness.py

# Run phase1 tests
python tests/command_wizard/run_phase1.py

# Run all tests
python tests/command_wizard/run_tests.py
```

## Code Architecture

The ISEE Meta Framework architecture is designed around these key principles:

1. **Modularity** - Components are separated with clear boundaries
2. **Extensibility** - Easy to add new models, templates, domains, and evaluation criteria
3. **Configurability** - Extensive control through command-line options and config files
4. **Persistence** - State can be saved and restored across sessions

The framework uses a layered approach:
- The Input Layer manages the diversity of inputs
- The Orchestration Layer creates and executes combinations
- The Evaluation Layer scores the results
- The Extraction Layer synthesizes the most promising ideas

## Development Guidelines

### Implementation Principles from the UX Enhancement Roadmap

When making changes to the codebase, especially for the Command Wizard UX Enhancement, follow these principles:

1. **Incremental Integration**: Build on existing code rather than replacing it
2. **Feature Flagging**: Implement new features behind toggles for safe deployment
3. **Comprehensive Testing**: Maintain and extend test coverage for all changes
4. **Backward Compatibility**: Ensure existing commands and workflows continue to function
5. **Code Isolation**: Minimize modifications to core functionality when adding UX enhancements
6. **Documentation**: Update documentation alongside code changes
7. **User Feedback**: Incorporate feedback loops into the implementation process

### Risk Mitigation Strategy

For implementation safety:

1. **Branch-Based Development**
   - Create feature branches for each step
   - Integrate only after passing all tests
   - Maintain main branch stability

2. **Feature Flags**
   - Implement new features behind toggles
   - Allow enabling/disabling new capabilities
   - Support fallback to previous behavior

3. **Progressive Testing**
   - Test each component individually
   - Perform integration testing between steps

### Adding New Models

Extend the `model_api_integration.py` file to add new model providers or integrate with additional models.

### Adding New Instructions

Edit `instruction_templates.py` to add new cognitive frameworks/instruction templates.

### Adding New Domains

Edit `domain_manager.py` or create a custom domain configuration JSON file.

### Improving Evaluation

Enhance `evaluation_scoring.py` with more sophisticated scoring algorithms.

### Configuration Files

The system uses several configuration files:
- `unified_config.json` - Comprehensive config with all models
- `sample_config.json` - Original config with mixed model providers
- `ollama_config.json` - Ollama-only config
- `gemini_test_config.json` - Config for testing with Google Gemini 2.5 Pro

### API Integration

The framework supports these model APIs:
- Anthropic Claude (via `ANTHROPIC_API_KEY`)
- OpenAI models (via `OPENAI_API_KEY`)
- Google Gemini (via `GOOGLE_API_KEY`) 
- Local Ollama models

## UI Enhancements with Command Wizard

The Command Wizard (`command_wizard.py`) provides an interactive UI to construct ISEE commands. Key features:

1. Automatic API detection
2. Step-by-step guidance through parameters
3. Command preview and explanation
4. Clipboard integration
5. Direct execution option

When working on Command Wizard, be aware of these design principles:
- Progressive disclosure of options
- Helpful defaults for beginners
- Clear explanations of complex options
- Error handling and validation

## Important Notes

- **API Keys**: The framework requires API keys for real model integration (Anthropic, OpenAI, Google)
- **Simulation Mode**: Use `--simulate` to run without API keys
- **Dry Run Mode**: Use `--dry-run` to preview execution without running
- **State Management**: Use `--save-state` and `--load-state` for persistence
- **Balanced Models**: Use `--balanced-models` for maximum cognitive diversity

## UX Enhancement Roadmap

The UX Enhancement Roadmap (see `specs/Command-Wizard-Integrated-UX-Enhancement-Dev-Roadmap.md`) outlines a comprehensive plan for improving the Command Wizard interface while maintaining the power and flexibility of the framework. The roadmap is divided into five phases:

1. **Phase 1: Cost Awareness and Foundational Improvements**
   - Step 1.1: Cost and Time Estimation (Current Focus)
   - Step 1.2: Parameter Context Improvements
   - Step 1.3: Command Preview Enhancements

2. **Phase 2: Purpose-First Approach and Presets**
   - Step 2.1: Purpose Selection Foundation
   - Step 2.2: Preset Configuration Implementation
   - Step 2.3: Progressive Disclosure Pattern

3. **Phase 3: Visual Understanding Enhancements**
   - Step 3.1: Cognitive Frameworks Visualization
   - Step 3.2: Simple Configuration Dashboard
   - Step 3.3: Combination Explorer (Prototype)

4. **Phase 4: Interaction and Feedback Refinements**
   - Step 4.1: Interactive Cost/Quality Slider
   - Step 4.2: Real-time Validation Enhancements
   - Step 4.3: Enhanced Progress and Result Visualization

5. **Phase 5: Integration and Final Enhancements**
   - Step 5.1: Purpose-Preset-Parameter Integration
   - Step 5.2: Advanced Combination Explorer
   - Step 5.3: Complete Documentation and Help System

When working on the roadmap implementation, focus on the immediate priorities while maintaining awareness of how your changes will fit into the overall vision.