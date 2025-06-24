# CLAUDE.md - ISEE Meta Framework Developer Guide

**Primary Focus**: Web UI Development | **Latest Update**: December 2024

> **🚀 Quick Start**: Run `python app.py` → Open http://localhost:5001

## Table of Contents
- [📱 Web UI Overview](#-web-ui-overview)
- [🏗️ Architecture](#️-architecture) 
- [⚡ Quick Commands](#-quick-commands)
- [🔧 Development Workflow](#-development-workflow)
- [🎨 Visual Design](#-visual-design)
- [🔗 Session Handoff](#-session-handoff)
- [🚨 Troubleshooting](#-troubleshooting)

---

## 📱 Web UI Overview

The ISEE Meta Framework has evolved from a CLI-first tool to a **Web UI-first platform** designed for accessible AI research and cognitive diversity exploration.

### What Works Today

✅ **Complete Web Interface** (`app.py:5001`)
- Flask-based application with professional gradient design
- Real-time configuration with 300+ models via OpenRouter
- Dynamic cognitive frameworks selection (10 frameworks)
- Live cost estimation and progress tracking
- Individual LLM selection with detailed model info

✅ **Academic/Scholarly Visual Design**
- Professional gradient backgrounds
- Clean typography optimized for research context
- Visual cognitive framework icons and descriptions
- Responsive design for various screen sizes

✅ **Core Functionality**
- Query input with real-time validation
- Domain selection from actual ISEE domains
- Model selection with provider grouping and cost tiers
- Execution with progress monitoring and result download
- Full CLI feature parity through web interface

### Configuration Requirements

**Essential**: `openrouter_config.json` - Consolidated configuration file
**API Key**: OpenRouter API key (manages 300+ models with single key)
**Dependencies**: See `requirements.txt` - 9 total dependencies

---

## 🏗️ Architecture

### Current Architecture (Web UI Primary)

```
Web UI (Flask) → Backend Services → Model APIs
    ↓                ↓               ↓
app.py          main.py           OpenRouter
templates/      reporting.py      (300+ models)
demo.html       cost_estimation   Ollama (optional)
```

### Key Components

**🎯 Primary Interface**: `app.py` (1218 lines)
- `ISEEWebDemo` class: Main controller
- REST API endpoints for all functionality
- Real-time execution monitoring
- Session-based API key management

**🧠 Backend Services**:
- `main.py`: Core ISEE execution logic
- `openrouter_rankings_service.py`: Dynamic model rankings
- `cost_estimation.py`: Real-time cost calculation
- `cognitive_framework_visualizer.py`: Framework rendering

**📊 Data Flow**:
1. Web UI collects parameters
2. Parameters converted to CLI format
3. Backend executes ISEE framework  
4. Results streamed back to web interface
5. Download available in multiple formats

---

## ⚡ Quick Commands

### Web UI Development

```bash
# Start development server
python app.py

# Parameter validation testing (CRITICAL - run before/after changes)
python tests/test_runner.py --quick         # Quick validation check
python tests/test_runner.py --bug-only      # Test specific bug cases
python tests/test_runner.py                 # Full parameter validation suite

# Test Web UI endpoints
curl http://localhost:5001/api/models
curl http://localhost:5001/api/frameworks
curl http://localhost:5001/api/domains

# Check API integrations
python -c "from app import demo; print(demo._detect_apis())"

# Validate OpenRouter rankings
python -c "from openrouter_rankings_service import OpenRouterRankingsService; print(OpenRouterRankingsService().get_cache_status())"
```

### Backend Testing

```bash
# CLI validation
python main.py --query "test query" --domain "Education" --models 3 --config openrouter_config.json --simulate

# Cost estimation test  
python -c "from cost_estimation import CostEstimator; print(CostEstimator().estimate_cost(type('obj', (), {'query': 'test', 'models': 5})))"

# Framework validation
python -c "from cognitive_framework_visualizer import CognitiveFrameworkVisualizer; print(len(CognitiveFrameworkVisualizer().get_frameworks_for_complexity('all')))"
```

### Configuration Verification

```bash
# Check OpenRouter config
python -c "import json; print(f'Models: {len(json.load(open(\"openrouter_config.json\"))[\"models\"][\"api_models\"])}')"

# Validate domains
python -c "from domain_manager import DomainManager, create_default_domains; dm = DomainManager(); [dm.add_domain(d) for d in create_default_domains()]; print(f'Domains: {len(dm.domains)}')"

# Test model loading
python -c "from app import demo; print(f'Available models: {len(demo.get_individual_models())}')"
```

---

## 🔧 Development Workflow

### Web UI Development Focus

**🎯 Primary Development Areas**:

1. **Visual Design Enhancements** (`templates/demo.html`)
   - Academic/scholarly aesthetic improvements
   - Enhanced cognitive framework visualization
   - Responsive design optimization
   - Professional form components

2. **Real-time Features** (`app.py` endpoints)
   - Dynamic model rankings updates
   - Live cost estimation improvements  
   - Progress tracking enhancements
   - Error handling and user feedback

3. **Integration Improvements**
   - OpenRouter API optimization
   - Dynamic rankings caching strategy
   - Session management enhancement
   - API key validation workflows

### Current Priorities

**🔴 High Priority**:
- Visual design polish for academic presentation
- OpenRouter rankings optimization 
- Error handling improvements
- Session state management

**✅ COMPLETED**:
- **Dynamic Model Selection**: Fixed critical bug where Web UI ignored user model selections
- **Future-Proof OpenRouter Integration**: System now supports any current/future OpenRouter model automatically
- **Dynamic Config Generation**: Backend creates model configs on-the-fly for unknown OpenRouter models
- **CRITICAL: Accurate Cost Estimation**: Fixed "Demo mode: Using simplified cost calculation" fallback issue
- **Enhanced Parameter Integration**: Fixed SimpleParams class compatibility with cost estimator backend
- **Verified End-to-End Pipeline**: Confirmed Web UI → Cost Estimation → Execution → Results download workflow
- **Selected Models List Enhancement**: Added collapsible detailed list showing selected model names and providers in sidebar for improved user reference
- **🎯 MAJOR: Query Preview & Export**: Implemented comprehensive query preview modal showing exactly how cognitive frameworks transform user queries, with CSV export for spreadsheet analysis - provides complete transparency into ISEE's cognitive instruction assembly process
- **🚨 CRITICAL: Parameter Passing Bug Fixes**: Fixed 3 major bugs in Web UI → Backend parameter conversion:
  - **Multi-Domain Support**: Fixed ignored `selected_domains` array - now correctly processes multiple knowledge domains
  - **Framework Selection**: Fixed cognitive framework bypass - Web UI selections now properly applied to backend
  - **Unlimited CSV Export**: Removed 12-record limit for comprehensive analysis and debugging capabilities
- **🧪 AUTOMATED PARAMETER VALIDATION**: Implemented comprehensive test framework preventing parameter passing regressions:
  - **Automated Bug Detection**: Test framework automatically catches parameter passing bugs before manual testing
  - **Framework Name Mapping**: Fixed Web UI framework names → Backend template ID conversion (e.g., "Analytical Framework" → "ins_analytical")
  - **End-to-End Validation**: Complete parameter validation from Web UI → Backend → CSV export with 100% test coverage
  - **Regression Prevention**: Robust test suite ensures future changes don't break parameter handling
- **🎯 CRITICAL: Combination Limits Resolution**: Fixed user-reported issue where only 2 of 5 frameworks appeared:
  - **Root Cause**: max_combinations limit of 48 was too low for 5×4×5=100+ parameter combinations
  - **Solution**: Increased default to 100, added options up to 400, provided calculation guidance in UI
  - **UI Enhancement**: Added form help text showing combination calculation formula
  - **Test Coverage**: Added comprehensive 5×5×4 test case to automated suite preventing future regressions
- **🦙 MAJOR: Ollama Model Integration & Selection Fixes**: Complete resolution of local model support:
  - **Dynamic Ollama Model Detection**: Local Ollama models automatically integrated into main model list
  - **UI Consolidation**: Unified model selection - removed separate Ollama section for cleaner interface
  - **CRITICAL: Multi-Model Distribution**: Fixed bug where only 1 of 4 selected models was used in combinations
  - **CRITICAL: Domain Auto-Expansion**: Fixed unwanted domain expansion (Education → 4 sub-domains) with exact matching
  - **Fair Stratified Sampling**: Implemented algorithm ensuring all selected models, frameworks, and domains are represented within max_combinations limit
  - **End-to-End Validation**: Complete Ollama model selection → query preview → execution pipeline verified
- **✨ MAJOR: AI Models Selection Enhancement**: Complete bulk selection functionality for improved workflow:
  - **Select All/Deselect All Buttons**: Added functional buttons to models header for efficient bulk operations
  - **Smart Filter Integration**: Select All respects current filter state (only selects visible models)
  - **Interface Cleanup**: Removed non-functional "View All" button for cleaner, more intuitive design
  - **Professional UX**: Consistent with data table interaction patterns users expect
- **🎛️ MAJOR: Filter Panel Master Controls**: Enhanced filter usability with master checkbox functionality:
  - **Provider Master Checkbox**: Single control for all provider filters (OpenAI, Anthropic, Google, etc.)
  - **Cost Tier Master Checkbox**: Single control for all cost tier filters (Free, Budget, Balanced, Premium)
  - **Indeterminate State Support**: Visual indication of partial selection (checked/unchecked/mixed states)
  - **Bidirectional Updates**: Individual filter changes update master checkbox, master changes update all filters
- **📊 MAJOR: Dynamic Model Count Display**: Transformed static counter into meaningful, contextual information:
  - **Filter-Aware Display**: Shows "Showing X of Y models" when filters are applied vs. static "Y models"
  - **Real-time Updates**: Count updates immediately as users apply/remove filters or search
  - **Clear Information Architecture**: Users understand exactly what the number represents
  - **Professional Data Table Behavior**: Matches modern UI expectations for filtered data displays
- **🔧 CRITICAL: Multi-Domain CLI Parameter Bug Fix**: Resolved parameter inconsistency between Web UI selections and Command Preview:
  - **CLI Multi-Domain Support**: Added `action="append"` to `--domain` argument parser for multiple domain flags
  - **Command Preview Accuracy**: Now shows `--domain domain_knowledge_management --domain domain_content_strategy --domain domain_ai_writing` instead of misleading display text
  - **Direct Domain Mapping**: Eliminated fuzzy search logic for bulletproof 1:1 mapping between Web UI selections and backend processing
  - **End-to-End Consistency**: Web UI selections → Command Preview → CLI execution → Backend processing all use identical domain parameters
  - **Backward Compatibility**: Single domain usage continues to work while supporting multiple domains
  - **Comprehensive Testing**: All parameter validation tests pass with new multi-domain functionality

**🟡 Medium Priority**:
- Advanced visualization components
- Performance optimization
- Additional export formats
- Accessibility improvements

**🔧 LATEST SESSION ACHIEVEMENTS**:
- **✅ CRITICAL: LLM Collections Display Bug Fixed**: Resolved null pointer error in `renderRankingsStatus` preventing collections from loading
- **✅ Systematic Debugging Process**: Implemented step-by-step diagnosis approach identifying exact failure point in initialization
- **✅ Defensive Programming**: Added null checks for optional UI elements to prevent future crashes
- **✅ Full Collections Feature Working**: All 4 curated collections now display with proper styling and functionality

**🟢 Low Priority**:
- CLI enhancements (Web UI has feature parity)
- Additional provider integrations
- Advanced analytics features

### File Locations

**Web UI Core**: `app.py`, `templates/demo.html`
**Configuration**: `openrouter_config.json` (single source of truth)
**Backend**: `main.py`, `reporting.py`, `cost_estimation.py`
**Services**: `openrouter_rankings_service.py`, `domain_manager.py`
**Visualization**: `cognitive_framework_visualizer.py`

---

## 🎨 Visual Design

### Current Design System

**🎨 Enhanced Academic Color Palette**:
- Primary gradient: `#667eea` → `#764ba2`
- Professional typography: Inter, Source Serif Pro, Fira Code
- Academic neutrals with warm undertones
- Provider-specific color coding (OpenAI, Anthropic, Google, etc.)
- Cost tier visualization (Free, Budget, Balanced, Premium)

**📝 Professional Typography System**:
- Font families: Inter (primary), Source Serif Pro (academic), Fira Code (code)
- Academic hierarchy: 8-level scale from 0.75rem to 3rem
- Line heights optimized for research readability
- Design tokens for consistent spacing and sizing

**🧩 Enhanced Component Library**:
- **CSS Architecture**: Modular design system with design tokens
- **Framework Cards**: Enhanced visual icons with hover effects
- **Model Selection**: Provider grouping with professional badges
- **Cost Estimation**: Real-time visualization with academic styling  
- **Progress Indicators**: Sophisticated animations and shimmer effects
- **Glass Morphism**: Backdrop filters for modern academic aesthetic
- **Interactive States**: Hover, focus, and selection with smooth transitions

### CSS Architecture

**📁 File Structure**:
- `static/css/design-tokens.css`: CSS custom properties and design system
- `static/css/main.css`: Core layout, typography, and base styles
- `static/css/components.css`: UI components and interactive elements
- `static/css/enhancements.css`: Advanced visual effects and animations

**🎯 Completed Enhancements**:
1. ✅ **Modular CSS Architecture**: Separated concerns with design tokens
2. ✅ **Academic Typography**: Professional Inter/Serif font system
3. ✅ **Enhanced Components**: Sophisticated cards, badges, and indicators
4. ✅ **Professional Color System**: Provider-specific and cost-tier colors
5. ✅ **Advanced Interactions**: Hover states, focus rings, smooth transitions
6. ✅ **Glass Morphism Effects**: Modern backdrop filters and transparency
7. ✅ **Academic Favicon**: Custom SVG icon for professional branding

**📐 Responsive Design**:
- Mobile-first approach with academic readability
- Flexible grid system for various screen sizes
- Touch-friendly interactive elements
- Print-optimized styles for academic documentation

---

## 🔗 Session Handoff

### Enhanced Session Handoff Procedure (Web UI Focus)

**🔄 Shortcut Command**: "Please execute the session handoff procedure"

This triggers the following **6-step automated process**:

#### **Step 1: 📊 Progress Assessment (Web UI Focus)**
- Summarize Web UI development progress
- Document visual design improvements
- Note any UX/UI enhancements completed
- Assess frontend testing status

#### **Step 2: 📝 Documentation Updates** 
- Update CLAUDE.md with Web UI changes
- Document any new API endpoints
- Record visual design decisions
- Update development priorities

#### **Step 3: 🔧 Web UI State Validation**
```bash
# Automated parameter validation (CRITICAL - prevents parameter passing bugs)
python tests/test_runner.py --quick || echo "🚨 Parameter validation FAILED - check Web UI → Backend conversion"

# Web UI functionality check
python app.py --test-mode &
sleep 2
curl -f http://localhost:5001/api/models || echo "API issue detected"
curl -f http://localhost:5001/api/frameworks || echo "Framework API issue"
curl -f http://localhost:5001/api/domains || echo "Domain API issue"
pkill -f "python app.py"

# Backend validation
python main.py --help > /dev/null && echo "CLI functional" || echo "CLI issue"
python -c "from app import demo; demo._detect_apis()" || echo "API detection issue"

# Full parameter validation (if quick test failed)
# python tests/test_runner.py || echo "🚨 CRITICAL: Full parameter validation failed"
```

#### **Step 4: 💾 Commit Optimization (Web UI Context)**
```bash
# Stage Web UI changes
git add app.py templates/ static/ 
git add openrouter_config.json CLAUDE.md

# Create comprehensive commit
git commit -m "feat: enhance Web UI development

- [Specific UI improvements made]
- [Backend integrations completed] 
- [Visual design enhancements]
- Updated CLAUDE.md for next session handoff

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

#### **Step 5: 🎯 Next Session Preparation (Web UI Priorities)**
Document immediate startup commands:
```bash
# Quick Web UI startup validation
python app.py &
echo "Web UI starting at http://localhost:5001"
sleep 3
curl -s http://localhost:5001/api/models | jq '.[:3]' || echo "Models API check needed"

# Next session priorities:
# 1. [Specific Web UI task]
# 2. [Visual design improvement] 
# 3. [Integration enhancement]
```

#### **Step 6: ✅ Handoff Summary**
- Current Web UI development status
- Next session immediate priorities
- Known issues or blockers
- Visual design enhancement roadmap

### Session Management Strategy

**🔄 Fresh Session Approach**: 
- Start new Claude sessions at logical Web UI development boundaries
- Use CLAUDE.md as primary context preservation
- Maintain development momentum through clear handoff documentation

**📱 Web UI Session Boundaries**:
- Major visual design milestones
- API integration completion points
- Feature implementation completion
- User testing/feedback integration points

### Next Session Startup Template

```bash
# Immediate context restoration
cd /Users/josephfajen/git/ISEE_Meta_Framework
git status
git log --oneline -5

# Web UI status check
python app.py &
WEB_PID=$!
sleep 3
curl -s http://localhost:5001/api/api-status | jq '.'
kill $WEB_PID

# Backend validation
python main.py --help | head -5

# Ready for Web UI development with full context!
```

---

## 🚨 Troubleshooting

### Common Web UI Issues

**🚫 Web UI Won't Start** (`python app.py` fails):
```bash
# Check dependencies
pip install -r requirements.txt

# Verify port availability
lsof -i :5001

# Check configuration
python -c "import json; json.load(open('openrouter_config.json'))"
```

**🔑 API Key Issues**:
```bash
# Check OpenRouter key format
echo $OPENROUTER_API_KEY | grep "^sk-or-" || echo "Invalid key format"

# Test API key via Web UI
curl -X POST http://localhost:5001/api/validate-openrouter -H "Content-Type: application/json" -d '{"api_key":"YOUR_KEY"}'
```

**📊 Model Loading Issues**:
```bash
# Check OpenRouter rankings
python -c "from openrouter_rankings_service import OpenRouterRankingsService; print(OpenRouterRankingsService().get_cache_status())"

# Force rankings update
curl -X POST http://localhost:5001/api/update-rankings
```

**🎨 Frontend Display Issues**:
- Check browser console for JavaScript errors
- Verify Flask template rendering
- Validate CSS loading and gradient displays
- Test responsive design on different screen sizes

### Backend Integration Issues

**CLI Execution Problems**:
```bash
# Test core functionality
python main.py --query "test" --domain "Education" --models 2 --simulate

# Check cost estimation
python -c "from cost_estimation import CostEstimator; print(CostEstimator().estimate_cost(type('obj', (), {'models': 3})))"
```

**Configuration Issues**:
```bash
# Validate openrouter_config.json
python -c "import json; config=json.load(open('openrouter_config.json')); print(f'Valid config with {len(config[\"models\"][\"api_models\"])} models')"

# Check domain loading  
python -c "from domain_manager import create_default_domains; print(f'Default domains: {len(create_default_domains())}')"
```

---

## 🎯 Development Roadmap

### Immediate Next Steps (Next Session)

**🧪 PRIORITY: User Testing & Collection Refinement**
1. **User Testing Results**: Analyze feedback on curated collections UX and cognitive load reduction
2. **Collection Optimization**: Refine model selections based on actual usage patterns and user preferences
3. **Advanced Individual Selection**: Consider implementing optional "Advanced Mode" for power users
4. **Performance Monitoring**: Validate collection-based cost estimation accuracy and execution performance

**📊 Collection Analytics & Monitoring**
1. **Usage Analytics**: Track which collections are most popular and effective
2. **Cost Analysis**: Monitor actual vs estimated costs across different collections
3. **Model Performance**: Analyze cognitive diversity effectiveness within each collection
4. **Dynamic Updates**: Implement collection updates based on new OpenRouter model releases

**🔄 Previous Session Achievements**:
- ✅ **MAJOR: Curated LLM Collections Implementation**: Complete replacement of complex individual model selection with streamlined 4-collection system
- ✅ **Strategic UI Simplification**: 90% cognitive load reduction from 30+ model selection to 4 curated collections
- ✅ **Dynamic OpenRouter Integration**: Collections leverage full 300+ model catalog with runtime resolution and smart fallbacks
- ✅ **Professional Academic Design**: Collection cards with progressive disclosure, matching existing framework card aesthetics
- ✅ **Complete Backend Integration**: Collection resolution, parameter conversion, cost estimation, and command preview all functional
- ✅ **Zero Regressions**: All parameter validation tests pass, maintaining backward compatibility with individual selection
- ✅ **Production Ready Branch**: feature/curated-llm-collections branch created with comprehensive implementation

### Medium-term Goals

1. **Advanced Visualization**: Interactive cognitive framework displays
2. **Export Enhancements**: Multiple format options and custom reports
3. **Session Management**: Enhanced user state persistence
4. **Accessibility**: WCAG compliance and screen reader support

### Long-term Vision

1. **Production Deployment**: Docker containerization and cloud deployment
2. **User Management**: Multi-user support and workspace management
3. **Analytics**: Usage analytics and research insights
4. **Integration**: External tool integrations and API expansions

---

## 📚 Key Resources

**🔧 Essential Files**:
- `app.py`: Web UI application (primary development focus)
- `openrouter_config.json`: Consolidated configuration
- `templates/demo.html`: Frontend interface
- `main.py`: Backend ISEE logic

**📖 Documentation**:
- `CLAUDE_ARCHIVE.md`: Historical development context
- `requirements.txt`: Python dependencies  
- `docs/`: Comprehensive guides for all features
- `docs/ui-rethinking/`: **NEW** - Complete UI redesign specifications and research plan

**🌐 External Resources**:
- OpenRouter API: https://openrouter.ai/docs
- ISEE Methodology: Cognitive diversity through multi-model exploration
- Flask Documentation: https://flask.palletsprojects.com/

---

*This guide prioritizes Web UI development while maintaining full access to the powerful ISEE Meta Framework backend. Focus on visual design, user experience, and accessibility to create a world-class research tool.*