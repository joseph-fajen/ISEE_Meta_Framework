# ISEE Framework Refactoring Plan

**Created**: December 2025
**Goal**: Simplify codebase for web-first architecture with Globant as primary provider

## Executive Summary

Refactor ISEE from a CLI-first application with web wrapper to a clean web-first architecture. Consolidate to Globant Enterprise as the primary LLM provider, eliminating dual-provider complexity.

## Current State

### Architecture Issues
1. **Subprocess Pattern**: `app.py` spawns `main.py` as subprocess instead of importing directly
2. **Dual Provider Complexity**: OpenRouter and Globant have different model name formats
3. **Visualization Bugs**: Framework/model/domain tracking has race conditions and state issues
4. **Code Duplication**: ~150 lines of parameter translation between CLI and web

### File Sizes (Before)
| File | Lines | Purpose |
|------|-------|---------|
| main.py | 3,185 | CLI engine + core logic |
| app.py | 3,111 | Flask web server |
| isee-ui.html | 4,558 | Web interface |
| model_api_integration.py | 1,245 | All provider clients |
| provider_manager.py | 362 | Dual-provider switching |
| **Total Core** | **12,461** | |

## Target State

### Architecture Goals
1. **Web-first**: Direct module imports, no subprocess
2. **Single Provider**: Globant Enterprise as primary (OpenRouter can be added later if needed)
3. **Clear Visualization**: Each API call shows Model + Framework + Domain clearly
4. **Simplified Codebase**: ~50% reduction in core code

### Estimated File Sizes (After)
| File | Lines | Change |
|------|-------|--------|
| isee_engine.py (new) | ~1,200 | Extract from main.py |
| app.py | ~1,500 | -52% |
| isee-ui.html | ~3,000 | -35% |
| providers/globant.py | ~300 | Focused provider |
| main.py | ~500 | CLI wrapper only |
| **Total Core** | **~6,500** | **-48%** |

---

## Refactoring Phases

### Phase 1: Fix Visualization Bug (Immediate)
**Goal**: Fix the buggy display of cognitive lens + knowledge domain + LLM combinations

**Issues Identified**:
1. `illuminatedCombinations` Set in isee-ui.html never resets between runs
2. Framework name matching uses 8 different strategies (fragile)
3. Race condition between `current_calls` and `active_parallel_calls` in app.py

**Files to Modify**:
- `isee-ui.html` - Reset state on execution start, simplify matching
- `app.py` - Fix race condition in call tracking
- `main.py` - Ensure consistent naming in progress events

**Success Criteria**:
- Each combination lights up exactly once
- Model, Framework, and Domain display correctly
- No duplicates or missed combinations

---

### Phase 2: Consolidate to Globant Provider
**Goal**: Remove OpenRouter code, simplify to single provider

**Changes**:
1. Remove `OpenRouterClient` class from model_api_integration.py
2. Remove or simplify `provider_manager.py` (no longer need fallback logic)
3. Update config to use `globant_enterprise_config.json` as sole source
4. Remove provider selection UI from isee-ui.html
5. Update CLAUDE.md documentation

**Files to Modify**:
- `model_api_integration.py` - Remove OpenRouter client (~300 lines)
- `provider_manager.py` - Remove or drastically simplify (~250 lines)
- `openrouter_config.json` - Archive (not delete, for future reference)
- `isee-ui.html` - Remove provider selection cards
- `app.py` - Remove provider switching logic

**Success Criteria**:
- All API calls go through Globant
- No references to OpenRouter in active code paths
- Configuration simplified to single file

---

### Phase 3: Extract ISEEEngine Module
**Goal**: Create importable engine module from main.py

**New File**: `isee_engine.py`

**Extract from main.py**:
- `ISEEApplication` class core methods
- `ParallelExecutionEngine` class
- Combination generation logic
- Result evaluation logic
- Synthesis logic

**Keep in main.py**:
- CLI argument parsing
- Entry point for CLI usage
- Thin wrapper that instantiates ISEEEngine

**New Structure**:
```python
# isee_engine.py
class ExecutionParams:
    """Unified parameters for both CLI and web"""
    query: str
    models: list[str]
    frameworks: list[str]
    domains: list[str]
    # ...

class ISEEEngine:
    def __init__(self, params: ExecutionParams):
        pass

    async def execute(self) -> AsyncIterator[CombinationResult]:
        """Yields progress for each combination"""
        pass

    def get_combinations(self) -> list[Combination]:
        """Returns all combinations that will be executed"""
        pass
```

**Success Criteria**:
- `ISEEEngine` can be imported and used directly
- Same logic works for both CLI and web
- No parameter translation needed

---

### Phase 4: Eliminate Subprocess Pattern
**Goal**: app.py imports ISEEEngine directly instead of spawning subprocess

**Current Flow**:
```
Web UI → app.py → subprocess(main.py) → stdout JSON → app.py → Web UI
```

**Target Flow**:
```
Web UI → app.py → ISEEEngine.execute() → Web UI
```

**Changes**:
1. Remove `subprocess.Popen` calls from app.py
2. Import and instantiate `ISEEEngine` directly
3. Use async iteration for progress streaming
4. Remove JSON stdout parsing logic

**Files to Modify**:
- `app.py` - Major refactor of execution logic

**Success Criteria**:
- No subprocess spawning
- Direct async progress streaming
- Cleaner error handling (no stdout parsing)

---

### Phase 5: Simplify UI Visualization
**Goal**: Clean, clear display of Model × Framework × Domain combinations

**Visualization Approach**:
- Show execution as a clear matrix/grid
- Each cell = one combination
- Real-time status updates (pending → active → complete)
- Click any cell to see that response

**UI Simplifications**:
- Remove provider selection (Globant only)
- Remove advanced configuration options (use sensible defaults)
- Focus on: Query → Execute → Results

**Files to Modify**:
- `isee-ui.html` - Simplify JavaScript, improve visualization

---

## Implementation Order

1. **Phase 1** first - fixes immediate user-facing bug
2. **Phase 2** second - reduces complexity for subsequent phases
3. **Phase 3** third - creates clean foundation
4. **Phase 4** fourth - eliminates architectural debt
5. **Phase 5** last - polish and UX improvements

Each phase should be a separate commit with working code.

---

## Risk Mitigation

### Preserving Functionality
- Keep `archive/` directory for reference
- Archive (don't delete) OpenRouter config
- Maintain ability to run existing analyses

### Rollback Strategy
- Each phase is a separate commit
- Can revert individual phases if issues arise
- Branch-based development allows easy comparison

### Testing Approach
- Test each phase with real Globant API calls
- Verify visualization works for full 66-combination run
- Check that existing result files remain accessible

---

## Future Considerations

### If OpenRouter Needed Later
- Provider interface already defined
- Can add `providers/openrouter.py` without touching core engine
- Config system supports multiple provider files

### CLI Deprecation Path
- Phase 3 keeps CLI working via thin wrapper
- Can fully remove CLI in future if web-only desired
- main.py becomes optional entry point

---

## Success Metrics

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Core code lines | 12,461 | ~6,500 | -48% |
| Provider files | 2 configs + manager | 1 config | -67% |
| Visualization bugs | Multiple | 0 | Fixed |
| Time to understand codebase | High | Medium | Reduced |
| Subprocess calls | Yes | No | Eliminated |
