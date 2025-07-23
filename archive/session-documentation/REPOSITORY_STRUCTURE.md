# ISEE Meta Framework - Repository Structure

## Overview
This document describes the final repository structure after the comprehensive cleanup and refactoring for public release.

## 🎯 Core Working Files

### Frontend & Backend
- **`isee-ui.html`** - Primary web UI entry point (self-contained)
- **`app.py`** - Flask backend API server (1218 lines)
- **`main.py`** - Core ISEE execution logic

### Essential Core Modules
- **`analysis.py`** - Result analysis and processing
- **`cognitive_framework_visualizer.py`** - Framework visualization
- **`cost_estimation.py`** - Real-time cost calculation
- **`domain_manager.py`** - Knowledge domain management
- **`evaluation_scoring.py`** - Scoring framework
- **`instruction_templates.py`** - Template management
- **`model_api_integration.py`** - API integration layer
- **`openrouter_categorization.py`** - Model categorization
- **`openrouter_model_collections.py`** - Model collection management
- **`openrouter_rankings_service.py`** - Dynamic model rankings
- **`performance_tracker.py`** - Performance monitoring
- **`query_generator.py`** - Query generation
- **`report_generator.py`** - HTML report generation
- **`reporting.py`** - Core reporting functionality

## 📋 Configuration Files

### Essential Configuration
- **`requirements.txt`** - Python dependencies (9 total)
- **`unified_config.json`** - Main configuration
- **`openrouter_config.json`** - OpenRouter API configuration
- **`.env.template`** - Environment variable template
- **`.gitignore`** - Git ignore rules (updated)

### Supporting Configuration
- **`CLAUDE.md`** - Active working document
- **`Dockerfile`** - Container configuration
- **`docker-compose.yml`** - Docker compose setup
- **`run_examples.sh`** - Example commands

## 📁 Data & Resources

### Data Directory (`data/`)
- **`performance_tracking.db`** - SQLite performance database
- **`rankings_cache.json`** - Cached model rankings
- **`output/`** - Generated results and reports
- **`state/`** - Application state files

### Content & Resources
- **`content/`** - Static content files
- **`prompts/`** - Prompt templates
- **`templates/`** - HTML templates
- **`static/`** - CSS, JS, and assets
- **`scripts/`** - Development scripts

## 📚 Documentation

### Primary Documentation
- **`README.md`** - Main project documentation
- **`LICENSE`** - Project license

### Planning Documentation (`planning-docs/`)
- **`architecture/`** - System architecture documents
- **`demo-guides/`** - Demo setup guides
- **`development-notes/`** - Development session notes
- **`session-notes/`** - Session handoff information
- **`strategy/`** - Strategic planning documents

### Technical Documentation (`docs/`)
- **`QUICKSTART.md`** - Quick start guide
- **`SYSTEM_OVERVIEW.md`** - System overview
- **`WHY_ISEE.md`** - Project rationale
- **`specs/`** - Technical specifications
- **`ui-rethinking/`** - UI design specifications

## 📦 Archived Code (`archive/`)

### Legacy Development Phases
- **`cli-phase/`** - Original CLI implementation
  - `command_wizard.py*` - Command wizard iterations
  - `isee_prototype_pseudocode.py` - Early prototypes
  
- **`rich-cli-phase/`** - Rich CLI interface components
  - `configuration_dashboard.py` - Interactive dashboard
  - `*_parameter_editor.py` - Parameter editing components
  - `unified_parameter_editor.py` - Unified editor
  
- **`web-demo-phase/`** - Early web demo attempts
  - `enhanced_test.html` - Previous web interface
  - `demo_individual_model_selection.py` - Demo scripts
  - `performance_analysis.py` - Analysis tools
  
- **`tests-archive/`** - All test and debug files
  - `test_*.py` - 50+ test files
  - `debug_*.py` - Debug scripts
  - `analyze_dependencies.py` - Dependency analysis tools
  
- **`backup-files/`** - Backup and broken files
  - `unified_config_backup.json` - Configuration backups
  - `*.backup*` - File backups

## 🔧 Supporting Files

### Development Tools
- **`tests/`** - Current test infrastructure
- **`specs/`** - Technical specifications
- **`temp-for-reference-ollama_prompting_tool_v1/`** - Reference implementation

### Additional Resources
- **`fabric-outputs/`** - Fabric analysis outputs
- **`LLM-analysis-Simon-Willison_July-2025/`** - YouTube analysis
- **`*.json`** - Various configuration files

## 📊 File Statistics

### Before Cleanup
- **84 Python files** in root directory
- **Multiple backup files** and broken iterations
- **50+ test files** cluttering root directory

### After Cleanup
- **18 essential Python files** in root directory
- **67 files archived** by development phase
- **Clean, organized structure** ready for public release

## 🚀 System Status

### Working System Components
- ✅ **Web UI**: `isee-ui.html` loads and functions
- ✅ **Backend**: `app.py` imports and runs successfully
- ✅ **Core Logic**: `main.py` imports without errors
- ✅ **All Dependencies**: Essential modules available
- ✅ **Configuration**: All config files present

### Archive Success
- ✅ **67 files archived** without breaking system
- ✅ **Legacy imports removed** from active code
- ✅ **Clean directory structure** achieved
- ✅ **Git history preserved** in backup branch

## 💡 Key Achievements

1. **Dependency Analysis**: Identified 18 essential vs 67 archivable files
2. **Phase-Based Organization**: Logical archive structure by development phase
3. **Import Cleanup**: Removed legacy dependencies from active code
4. **System Validation**: Confirmed working system post-cleanup
5. **Documentation**: Complete structural documentation
6. **Git Safety**: Pre-cleanup backup branch created

## 🔄 Future Maintenance

The repository is now organized for:
- **Easy public sharing** with clean structure
- **Future development** with clear core files
- **Historical reference** through organized archives
- **Dependency management** with minimal essential files
- **Performance optimization** with reduced file count

This structure supports the transition from development repository to production-ready public codebase while preserving all historical development work in organized archives.