# Query Visibility Enhancement Summary

## Overview

Added comprehensive query visibility features to the ISEE Framework, providing unprecedented transparency into the complete queries being sent to LLMs. This enhancement addresses the user's request for visibility into how queries are constructed and executed.

## New Command-Line Flags

### 1. `--query-preview-only`
- **Purpose**: Show representative complete queries WITHOUT executing them
- **Use Case**: Understanding query construction, debugging, research
- **Output**: 8 sample queries with detailed component breakdown
- **Example**: `python main.py --query "Your question" --query-preview-only`

### 2. `--verbose-queries`
- **Purpose**: Show 3 sample complete queries at execution start, then proceed normally
- **Use Case**: Development, testing, moderate visibility
- **Output**: Initial query samples + normal execution progress
- **Example**: `python main.py --query "Your question" --verbose-queries`

### 3. `--show-all-queries`
- **Purpose**: Show complete query for EVERY combination (very verbose)
- **Use Case**: Deep debugging, complete transparency
- **Output**: Full query details for each of the 90+ combinations
- **Example**: `python main.py --query "Your question" --show-all-queries --max-combinations 5`

## Enhanced Visibility Features

### Query Component Breakdown
Each query preview shows:
- **Combination ID**: Unique identifier for the specific combination
- **Model**: Which AI model will receive the query
- **Template**: Instruction template name and cognitive style
- **Query**: The user's query (truncated if long)
- **Domain**: Domain context being applied
- **Template Style**: Cognitive framework approach (integrative, analytical, etc.)

### Complete Query Display
Shows the actual prompt sent to LLMs including:
- **Formatted instruction template** with domain context
- **Complete user query** as it will be processed
- **Character and word count** for sizing analysis
- **Visual formatting** with clear boundaries

### Execution Integration
- **Query sampling** during verbose execution
- **Progressive disclosure** (first 3 combinations detailed, then standard)
- **Abbreviated display** for long queries (smart truncation)
- **Performance stats** (character/word counts)

## Technical Implementation

### New Methods in ISEEApplication

#### `show_query_preview(combinations, sample_count, show_breakdown)`
- Displays representative sample queries from combinations
- Shows detailed component breakdown
- Formats complete prompts with visual boundaries
- Provides query statistics

#### `show_verbose_execution(combinations, show_every_nth)`
- Enhanced execution with selective query details
- Shows queries for first 3, last 2, and every nth combination
- Maintains performance while providing visibility

### Enhanced `execute_combinations()` Method
- Added `verbose_queries` and `show_all_queries` parameters
- Integrated query sampling at execution start
- Enhanced execution logging with query details
- Smart formatting for different verbosity levels

### Integration Points
- **Command-line argument parsing** for new flags
- **Pipeline integration** passing flags through execution chain
- **Dashboard compatibility** (future integration ready)
- **Error handling** for missing components

## Example Output Formats

### Query Preview Mode
```
🔍 SAMPLE QUERY 1/8
────────────────────────────────────────────────────────────
📋 QUERY COMPONENTS:
  • Combination ID: model_1_ins_integrative_query_f835c9a9_domain_technology
  • Model: gpt-4o-mini
  • Template: Integrative Synthesis (integrative)
  • Query: What are the specific challenges technical writers will face...
  • Domain: Technology Innovation
  • Template Style: integrative

🤖 COMPLETE QUERY SENT TO LLM:
────────────────────────────────────────
You are an expert in Technology Innovation with deep
understanding of current trends, emerging technologies,
and innovation patterns. Apply integrative thinking to
synthesize diverse perspectives and find creative
connections across different domains.

What are the specific challenges technical writers
will face when transitioning from linear Markdown
documentation to atomic content creation?
────────────────────────────────────────
📊 Query Stats: 412 characters, 67 words
```

### Verbose Queries Mode
```
🔍 QUERY SAMPLE: Showing 3 representative complete queries from 90 combinations

📋 Sample 1 - model_1_ins_integrative_query_f835c9a9_domain_technology:
  Model: gpt-4o-mini | Template: Integrative Synthesis | Domain: Technology Innovation
  Complete Query (412 chars):
  ┌─────────────────────────────────────────
  │ You are an expert in Technology Innovation...
  │ ...atomic content creation?
  └─────────────────────────────────────────

⚡ Starting execution of all 90 combinations...

Executing combination 1/90: model_1_ins_integrative_query_f835c9a9_domain_urban_planning
Executing combination 2/90: model_1_ins_integrative_query_f835c9a9_domain_education
...
```

### Show All Queries Mode
```
Executing combination 1/90: model_1_ins_integrative_query_f835c9a9_domain_urban_planning
  ┌─ Model: gpt-4o-mini | Template: Integrative Synthesis | Domain: Urban Planning
  ├─ Complete Query (398 chars):
  │   You are an expert in Urban Planning with deep understanding...
  │   ...atomic content creation?
  └─

Executing combination 2/90: model_1_ins_integrative_query_f835c9a9_domain_education
  ┌─ Model: gpt-4o-mini | Template: Integrative Synthesis | Domain: Education
  ├─ Complete Query (387 chars):
  │   You are an expert in Education with deep understanding...
  │   ...atomic content creation?
  └─
```

## Benefits

### For Users
- **Complete transparency** into LLM interactions
- **Understanding** of how ISEE constructs prompts
- **Debugging capability** for unexpected results
- **Research insights** into query construction patterns
- **Optimization guidance** for instruction templates

### For Developers
- **Debugging tool** for template development
- **Validation system** for query generation
- **Performance analysis** (query length, complexity)
- **Integration testing** support
- **Documentation** of actual usage patterns

## Usage Scenarios

### Research & Development
```bash
python main.py --query "Your research question" --query-preview-only
```
Perfect for understanding query construction before execution commitment.

### Focused Debugging
```bash
python main.py --query "Your question" --verbose-queries --max-combinations 10
```
Balanced visibility with execution for development and testing.

### Deep Inspection
```bash
python main.py --query "Your question" --show-all-queries --max-combinations 5
```
Complete transparency for debugging specific issues.

### Dashboard Integration
The query preview functionality is ready for integration with the configuration dashboard, enabling visual query inspection through the interactive interface.

## Performance Considerations

- **Minimal overhead** for standard execution (no flags)
- **Smart sampling** reduces output volume in verbose mode
- **Efficient formatting** with truncation for long queries
- **Memory conscious** - doesn't store unnecessary query copies
- **Terminal friendly** - respects line length and readability

## Future Extensions

1. **Query export** - Save sample queries to files
2. **Template analysis** - Compare query patterns across templates
3. **Domain impact analysis** - Show how domains change query content
4. **Interactive selection** - Let users choose which queries to see
5. **Statistical analysis** - Query length, complexity metrics
6. **A/B testing support** - Compare query variations

## Testing

The enhancement has been tested with:
- ✅ Query preview mode (--query-preview-only)
- ✅ Verbose queries mode (--verbose-queries)
- ✅ Show all queries mode (--show-all-queries)
- ✅ Integration with existing flags (--max-combinations, --simulate)
- ✅ Various query lengths and complexities
- ✅ Different domain and template combinations
- ✅ Error handling for missing components

## Files Modified

- `main.py` - Added new command-line flags, methods, and integration
- Enhanced `ISEEApplication` class with query visibility capabilities
- Updated `execute_combinations()` method with verbose options
- Modified `run_complete_pipeline()` to pass through visibility flags

## Breaking Changes

None. All new functionality is opt-in through command-line flags.

## Backward Compatibility

100% maintained. Existing commands work exactly as before.

---

*This enhancement provides the query visibility you requested, allowing you to see exactly what complete queries are being sent to the LLMs and understand how ISEE constructs its comprehensive prompts.*