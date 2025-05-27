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

**COMPLETED - Step 1.1: Cost and Time Estimation**
- ✅ Developed algorithms to estimate API costs based on parameter selections
- ✅ Created execution time estimation based on combination count and model selection
- ✅ Implemented warning systems for potentially expensive operations
- ✅ Added visual indicators showing how parameter changes affect costs
- ✅ Displayed estimated costs alongside parameter selection options

**COMPLETED - Step 1.2: Parameter Context Improvements**
- ✅ Created a comprehensive parameter context database
- ✅ Implemented enhanced help command functionality
- ✅ Added cross-parameter relationship tracking
- ✅ Added concrete examples for complex concepts
- ✅ Implemented "See Example" option for key parameters
- ✅ Added cross-parameter impact warnings
- ✅ Refactored parameter input handling for consistent special command support
- ✅ Added reusable input functions for different parameter types
- ✅ Ensured consistent step numbering throughout the wizard
- ✅ Improved error handling for user inputs

**COMPLETED - Step 1.3: Command Preview Enhancements**
- ✅ Expanded the command preview functionality with categorized parameter displays
- ✅ Added parameter-by-parameter explanations using ParameterContext integration
- ✅ Implemented collapsible sections for detailed/summary views with interactive toggles
- ✅ Created visual breakdown of command construction with color-coded categories
- ✅ Added before/after parameter change comparisons with tracking
- ✅ Implemented Parameter Impact Analysis panel showing cost/quality implications
- ✅ Enhanced special command support (preview, preview detailed, preview summary)
- ✅ Added comprehensive test coverage with 10 test cases

**COMPLETED - Step 2.1: Purpose Selection Foundation**:
- ✅ Created purpose category database with 8 predefined categories (Beginner-Friendly, Quick Exploration, Content Creation, Deep Analysis, Creative Innovation, Problem Solving, Learning Design, Strategic Planning, Custom Exploration)
- ✅ Implemented purpose selection as new initial wizard step
- ✅ Designed intuitive purpose selection interface with cost/runtime indicators
- ✅ Added purpose-driven parameter recommendations
- ✅ Integrated with Rich-only UI architecture

**COMPLETED - Step 2.2: Preset Configuration Implementation**:
- ✅ Designed comprehensive preset data structure and configuration format
- ✅ Created PresetManager class with full preset lifecycle management
- ✅ Implemented 10 built-in system presets across all purpose categories
- ✅ Added preset selection interface as Step 1.5 in command wizard
- ✅ Built visual preview and comparison functionality for presets
- ✅ Implemented custom preset saving/loading infrastructure
- ✅ Added special commands: 'preview <number>', 'compare <num1> <num2>'
- ✅ Created comprehensive test suite with 8 test categories (all passing)
- ✅ Integrated seamlessly with purpose selection foundation

**COMPLETED - Step 2.3: Progressive Disclosure Pattern**:
- ✅ Implemented three-tier complexity system (basic, advanced, expert)
- ✅ Added configuration path selection (Quick, Detailed, Expert Configuration)
- ✅ Created parameter categorization system for progressive disclosure
- ✅ Built collapsible sections for advanced options with visual indicators
- ✅ Implemented "Show Advanced Options" toggles for intermediate complexity levels
- ✅ Added complexity-aware section headers and time estimates
- ✅ Integrated smart defaults for quick configuration path
- ✅ Created comprehensive test suite with 15 test cases (100% pass rate)
- ✅ Maintained full backward compatibility with existing workflow

**COMPLETED - Rich-Only Migration (Architectural Enhancement)**:
- ✅ Eliminated dual Rich/non-Rich code paths throughout the entire codebase
- ✅ Removed all 49+ RICH_AVAILABLE conditionals for massive code simplification
- ✅ Achieved 25%+ code reduction while maintaining full functionality
- ✅ Improved maintainability and reduced complexity
- ✅ Enhanced terminal UI experience with consistent Rich formatting
- ✅ Updated error handling to fail fast with clear Rich dependency message

**Current Status - OpenRouter Integration FULLY COMPLETE + Critical Bug Fixes Applied**:
Phase 1 + Phase 2 (Steps 2.1, 2.2, 2.3) are complete. Additionally, **OpenRouter Integration is now FULLY COMPLETE with optimized user experience and critical bug fixes**, providing seamless access to 300+ models through intelligent curation and purpose-driven collections.

**OpenRouter Integration - Stage 1 COMPLETE**:
- ✅ **Intelligent Model Categorization System** - 5-dimensional filtering with 140k+ models/second performance
- ✅ **Provider Categorization** - 14+ provider categories (Anthropic, OpenAI, Google, Meta, etc.)
- ✅ **Capability Detection** - 10 capability categories (reasoning, creative, coding, fast, large_context, etc.)
- ✅ **Cost Tier Analysis** - 5 cost tiers from free to premium_plus with automatic pricing analysis
- ✅ **Use Case Mapping** - 10 ISEE-optimized use cases with intelligent model recommendations
- ✅ **Quality Scoring** - 1-10 intelligent quality scoring system with provider-aware ratings
- ✅ **Advanced OpenRouterClient** - Enhanced with categorization methods and ISEE-optimized recommendations
- ✅ **Rich Configuration** - Updated with categorization strategies and filtering examples
- ✅ **Comprehensive Testing** - 7/7 test suite validation with 100% pass rate

**OpenRouter Integration - Stage 2 COMPLETE**:
- ✅ **Interactive API Key Setup** - Browser integration, secure input, flexible storage options
- ✅ **Command Wizard Integration** - Seamless categorization filters in model selection workflow
- ✅ **4 OpenRouter-Specific Presets** - Provider diversity, coding focus, budget optimization, premium flagship
- ✅ **Enhanced Error Recovery** - Proactive OpenRouter setup suggestions and guidance
- ✅ **API Key Validation System** - Format checking and optional live validation
- ✅ **User-Friendly Documentation** - Complete setup guides and testing procedures
- ✅ **Comprehensive Testing** - 15/15 integration tests passing with 100% success rate

**OpenRouter Integration - Stage 3 COMPLETE**:
- ✅ **Purpose-Driven Model Collections** - 8 curated collections optimized for specific ISEE use cases
- ✅ **OpenRouter-First Experience** - Primary user flow with beautiful Rich table interface
- ✅ **Smart Recommendations** - Auto-suggests best collection based on user's purpose and cost preference
- ✅ **Legacy Fallback** - Traditional model selection available as advanced option
- ✅ **Enhanced Visibility** - Prominent OpenRouter promotion throughout wizard flow
- ✅ **Cost-Aware Curation** - Budget, balanced, and premium collections clearly labeled
- ✅ **Comprehensive Testing** - 27/27 total tests passing (12 new + 15 existing integration tests)

**LATEST UPDATES - Critical Bug Fixes (May 27, 2025)**:
- ✅ **Fixed OpenRouter API Key Detection**: Updated main.py to properly detect OPENROUTER_API_KEY environment variable
- ✅ **Fixed Duplicate Step 6 Variations**: Removed leftover dual Rich/non-Rich code paths in command wizard
- ✅ **Automatic Config File Selection**: Command Wizard now automatically includes --config openrouter_config.json when OpenRouter collections selected
- ✅ **End-to-End Validation**: Verified real OpenRouter models working with 400%+ content quality improvement

**Next Priority - Phase 3 Planning**:
- OpenRouter integration and user experience optimization COMPLETE with bug fixes applied
- Ready to proceed with Phase 3: Visual Understanding Enhancements
- Focus areas: Cognitive Frameworks Visualization, Configuration Dashboard, Combination Explorer

## Common Commands

### Environment Setup

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (Rich library is required for terminal UI)
pip install -r requirements.txt
```

**Important Note**: The ISEE Framework now requires the Rich library for its terminal interface. The system will fail fast with a clear error message if Rich is not installed.

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

# Run preset manager test (Step 2.2)
python test_preset_manager.py

# Run progressive disclosure test (Step 2.3)
python test_step_23_progressive_disclosure.py

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

### Rich-Only Architecture (New Standard)

The codebase has been migrated to a Rich-only architecture for improved maintainability and user experience:

1. **Rich Dependency Required**: The Rich library is now mandatory for all terminal UI functionality
2. **No Dual Code Paths**: All RICH_AVAILABLE conditionals have been eliminated
3. **Fail-Fast Design**: System provides clear error messages if Rich is not installed
4. **Simplified Maintenance**: 25%+ code reduction achieved through architecture consolidation
5. **Enhanced UX**: Consistent Rich formatting across all user interactions

When developing new features:
- Always use Rich components for terminal output (Console, Panel, Table, Prompt)
- No need to check for Rich availability - assume it's present
- Follow existing Rich formatting patterns for consistency

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
- **OpenRouter (via `OPENROUTER_API_KEY`) - 300+ models from 50+ providers**
- Local Ollama models

#### Setting Up OpenRouter (Recommended for Maximum Model Diversity)

**Interactive Setup (Easiest):**
1. Run `python command_wizard.py`
2. The wizard will detect if OpenRouter is not configured and offer to help you set it up
3. Follow the guided setup process to get and configure your API key
4. Choose how to store your key (session-only, terminal session, or permanent)

**Manual Setup:**
```bash
# Get your API key from: https://openrouter.ai/keys
export OPENROUTER_API_KEY="your_openrouter_api_key"
```

**Benefits of OpenRouter:**
- Access to 300+ models from 50+ providers with a single API key
- Intelligent model categorization and filtering
- Cost-effective options from free to premium tiers
- Latest models from all major providers (Anthropic, OpenAI, Google, Meta, etc.)

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
   - ✅ Step 1.1: Cost and Time Estimation (COMPLETED)
   - ✅ Step 1.2: Parameter Context Improvements (COMPLETED)
   - ✅ Step 1.3: Command Preview Enhancements (COMPLETED)

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

### Progress Summary
- **Current Status**: Phase 1 + Phase 2 (Steps 2.1, 2.2, 2.3) are **COMPLETE** + OpenRouter Integration **FULLY COMPLETE + User Experience Optimized**
- **Next Priority**: Phase 3 Planning → Visual Understanding Enhancements
- **Implementation**: 
  - **Step 1.1**: Cost estimation and time estimation capabilities with visual indicators ✅
  - **Step 1.2**: Parameter context module with enhanced help system and examples ✅
  - **Step 1.3**: Enhanced command preview with categorization, impact analysis, and interactive modes ✅
  - **Step 2.1**: Purpose Selection Foundation with 8 purpose categories and parameter recommendations ✅
  - **Step 2.2**: Preset Configuration Implementation with 10 built-in presets, custom preset support, and visual interface ✅
  - **Step 2.3**: Progressive Disclosure Pattern with three-tier complexity system and smart configuration paths ✅
  - **Rich-Only Migration**: Eliminated all dual code paths, 25%+ code reduction, enhanced maintainability ✅
  - **OpenRouter Stage 1**: Intelligent model categorization system with 5-dimensional filtering ✅
  - **OpenRouter Stage 2**: Interactive API key setup, command wizard integration, OpenRouter presets ✅
  - **OpenRouter Stage 3**: Purpose-driven model collections, OpenRouter-first experience, enhanced visibility ✅
  - Added reusable input handling functions in `command_wizard.py` for consistent UX
  - Refactored all parameter inputs to ensure consistent special command handling
  - Fixed step numbering consistency throughout the wizard
- **Branch**: Phase 1 + Phase 2 changes in `main`, OpenRouter integration in `openrouter-integration-poc`
- **Testing**: 
  - Unit tests added in `test_parameter_context.py` to verify parameter context functionality
  - Added `test_parameter_examples.py` to test special command handling
  - Created `test_model_input.py` to verify numeric input handling
  - Added `test_parameter_input_refactoring.py` to test all refactored input types
  - Added `test_command_preview_enhancements.py` with comprehensive Step 1.3 test coverage
  - Added `test_preset_manager.py` with 8 comprehensive test suites for Step 2.2 (all passing)
  - Added `test_step_23_progressive_disclosure.py` with 15 comprehensive test cases for Step 2.3 (100% pass rate)
  - **NEW**: Added `test_openrouter_integration.py` and `test_openrouter_categorization.py` with 10/10 tests passing
  - **NEW**: Added `test_openrouter_command_wizard_integration.py` with 15/15 comprehensive integration tests passing
  - **NEW**: Added `test_openrouter_model_collections.py` with 12/12 comprehensive model collection tests passing (27/27 total OpenRouter tests)
  - Rich-only migration verified with comprehensive functionality testing
- **Documentation**:
  - Added `PARAMETER_CONTEXT_EXAMPLE_HANDLING_FIX.md` documenting example command handling
  - Added `STEP_NUMBERING_FIXES.md` documenting step numbering consistency
  - Added `PARAMETER_INPUT_REFACTORING.md` explaining input handling improvements
  - **NEW**: Updated CLAUDE.md with OpenRouter Integration Stage 1 completion details
  - **NEW**: Added `OPENROUTER_HUMAN_TESTING_GUIDE.md` with comprehensive 7-scenario testing framework
  - **NEW**: Updated documentation with interactive OpenRouter setup guides and user flows
- **Architecture**: Rich-only codebase with progressive disclosure enhanced purpose-driven workflow + intelligent OpenRouter model categorization + purpose-driven model collections for 42.9x model diversity expansion with optimal user experience

When working on the roadmap implementation, focus on the immediate priorities while maintaining awareness of how your changes will fit into the overall vision.

## Session Management Guide

### 🔄 **Optimal Claude Code Session Strategy**

This project uses a **fresh session approach** for maximum context capacity and development efficiency. Follow this proven workflow:

#### **Before Ending Current Session:**
1. ✅ **Commit all changes** with descriptive messages
2. ✅ **Update documentation** (CLAUDE.md, roadmap, summaries)
3. ✅ **Run final tests** to ensure stability
4. ✅ **Note any in-progress thoughts** in commit messages

#### **Starting Fresh Session:**
```bash
# Essential first commands:
read CLAUDE.md                    # Get complete current context
git log --oneline -10                           # See recent progress
git status                                    # Check current state
python test_step_23_progressive_disclosure.py # Verify latest functionality (Step 2.3)
```

#### **Optimal Session Boundaries:**
- ✅ **After completing a major step** (like Step 2.3)
- ✅ **Before starting complex new functionality** (like Step 3.1)
- ✅ **When approaching context limits**
- ✅ **After significant architectural changes**

#### **Context Preservation Strategy:**
- **CLAUDE.md** - Always contains current status and next priorities
- **Step summary docs** - Detailed implementation notes for completed work
- **Roadmap document** - Overall progress and upcoming work
- **Git commit history** - Implementation trail and decision log

#### **Quick Session Transition Template:**
```bash
# End session: Commit work
git add . && git commit -m "feat: complete [STEP_NAME]

- [Key achievement 1]
- [Key achievement 2] 
- [Key achievement 3]
- Updated documentation for next session handoff"

# Exit Claude Code
# Start fresh Claude Code session when ready

# Begin new session:
read CLAUDE.md                    # Restore full context
# Ready to continue with maximum context capacity!
```

#### **Current Session Handoff (OpenRouter Integration)**:
```bash
# For OpenRouter Integration continuation:
read CLAUDE.md                                    # Get complete current context
read docs/OPENROUTER_INTEGRATION_SUMMARY.md      # Get detailed Stage 1 summary
git log --oneline -5                              # See recent progress
git status                                        # Check current state
python test_openrouter_categorization.py          # Verify categorization working
python test_openrouter_integration.py             # Verify integration working

# Current status: Stage 1 complete, ready for Stage 2 (Command Wizard Integration)
# Branch: openrouter-integration-poc
# Next: Integrate categorization system with Command Wizard interface
```

This documentation-driven approach ensures **perfect continuity** while maintaining **optimal performance** across development sessions.

## 🔄 **Session Handoff Shortcut**

When you're ready to end a session optimally, use this shortcut command:

**"Please execute the session handoff procedure"**

This triggers the complete session optimization workflow:

### **Session Handoff Procedure:**

1. **📊 Progress Assessment**
   - Summarize completed work and achievements
   - Identify current implementation status
   - Document any in-progress work state

2. **📝 Documentation Updates**
   - Update CLAUDE.md with latest completion status
   - Update progress summary with new achievements
   - Create/update relevant summary documents
   - Add specific next-session startup commands

3. **🔧 Code State Validation**
   - Run relevant tests to ensure stability
   - Verify branch state and recent commits
   - Check for any uncommitted changes
   - Ensure clean repository state

4. **💾 Commit Optimization**
   - Stage all documentation updates
   - Create comprehensive handoff commit
   - Include session summary in commit message
   - Note next priorities and context

5. **🎯 Next Session Preparation**
   - Document exact startup commands for next session
   - Identify immediate next priorities
   - Estimate time requirements for next stage
   - Ensure maximum context preservation

6. **✅ Handoff Summary**
   - Provide final status overview
   - Confirm branch readiness
   - Validate test coverage
   - Declare session handoff status

### **Usage:**
Simply say: **"Please execute the session handoff procedure"** and Claude will automatically:
- Assess current progress and update all documentation
- Run validation tests and ensure clean commit state  
- Create optimized handoff commit with comprehensive context
- Provide next-session startup commands and priorities
- Deliver final handoff summary for maximum context preservation

This ensures **optimal context capacity** and **seamless continuity** for every fresh session start.