# ISEE Single Run Performance Analysis

Conduct a comprehensive analysis of a specific ISEE query execution to identify optimization opportunities and improve the framework's core mission of cognitive diversity exploration.

## Command Purpose

**🎯 Focused Analysis:**
- Deep analysis of one user-specified run (detailed file examination)
- Comprehensive performance breakdown and insights
- Strategic recommendations for system optimization

**📊 Comprehensive Coverage:**
- Model performance metrics and cost efficiency analysis
- Cognitive framework effectiveness and specialization patterns
- Synthesis quality assessment and strategic insights
- Actionable recommendations for immediate improvements

**📁 Structured Reporting:**
- Professional analysis reports with metadata headers
- Searchable index.json for historical tracking
- Integration with existing analysis report system

## Instructions

This command performs a systematic analysis of a specific ISEE execution run to derive actionable insights for continuous improvement. **The user must specify the exact run folder name and location** (e.g., "run_20250723_070134" in data/output).

### Step 1: Setup Analysis Infrastructure and Validate Target Run

**Prerequisites**: User must specify the exact run folder name (e.g., "run_20250723_070134")

```bash
# Setup analysis infrastructure
ANALYSIS_DATE=$(date +%Y%m%d_%H%M%S)
REPORTS_DIR="/Users/josephfajen/git/ISEE_Meta_Framework/data/analysis_reports"
INDEX_PATH="$REPORTS_DIR/index.json"

# Create analysis reports directory if it doesn't exist
mkdir -p "$REPORTS_DIR"

# User specifies the target run (example: run_20250723_070134)
# This should be provided by the user in their request
TARGET_RUN_ID="USER_SPECIFIED_RUN_ID"  # Replace with actual run ID from user
TARGET_RUN_PATH="/Users/josephfajen/git/ISEE_Meta_Framework/data/output/$TARGET_RUN_ID"

# Validate the specified run exists
if [ ! -d "$TARGET_RUN_PATH" ]; then
    echo "❌ Error: Run directory not found: $TARGET_RUN_PATH"
    echo ""
    echo "Available recent runs:"
    find /Users/josephfajen/git/ISEE_Meta_Framework/data/output -name "run_*" -type d | sort -r | head -10 || echo "No runs found"
    exit 1
fi

echo "🎯 Analyzing single run: $TARGET_RUN_ID"
echo "📁 Run directory: $TARGET_RUN_PATH"
echo "📊 Analysis timestamp: $ANALYSIS_DATE"

# Check if run has been analyzed before
PREVIOUSLY_ANALYZED=false
if [ -f "$INDEX_PATH" ]; then
    ANALYZED_CHECK=$(python3 -c "
import json
try:
    with open('$INDEX_PATH', 'r') as f:
        data = json.load(f)
    analyzed_runs = [report.get('run_analyzed', '') for report in data.get('reports', [])]
    print('yes' if '$TARGET_RUN_ID' in analyzed_runs else 'no')
except:
    print('no')
")
    if [ "$ANALYZED_CHECK" = "yes" ]; then
        PREVIOUSLY_ANALYZED=true
        echo "⚠️  Note: This run has been analyzed before (will create new analysis)"
    fi
fi

# Setup single run analysis paths
RUN_ID="$TARGET_RUN_ID"
LATEST_RUN="$TARGET_RUN_PATH"
REPORT_PATH="$REPORTS_DIR/analysis_${ANALYSIS_DATE}_${RUN_ID}.md"

echo "📝 Analysis report will be saved to: $REPORT_PATH"
```

### Step 2: Comprehensive Single Run File Analysis

Analyze ALL files in the specified run directory to extract comprehensive insights.

**🎯 Core Result Files to Analyze:**
- `isee_result.md` - Main synthesis output and quality assessment
- `analysis.md` - Automated analysis and scoring breakdown  
- `run_summary.md` - Execution summary and key metrics
- `metadata.md` - Detailed combination metadata and execution details

**📊 Performance Data Files:**
- `model_performance.csv` - Individual LLM performance metrics (scores, response times, success rates)
- `combinations.csv` - All framework×model×domain combinations executed
- `ideas.csv` - Individual response evaluations and scores

**📈 Visual Analytics:**
- `model_comparison.png` - LLM performance visualization
- `domain_comparison.png` - Domain effectiveness analysis
- `instruction_comparison.png` - Cognitive framework performance  
- `scoring_components.png` - Score distribution analysis

**📋 Additional Files:**
- `isee_report.html` - HTML report if generated
- `quality_assessment.md` - Quality analysis if available
- Any query-specific files or screenshots

### Step 2.5: Extract Key Metrics from Target Run

```bash
echo "📊 Extracting metrics from $TARGET_RUN_ID..."

# Extract query summary
if [ -f "$LATEST_RUN/isee_result.md" ]; then
    QUERY_SUMMARY=$(head -50 "$LATEST_RUN/isee_result.md" | grep -E "^#|Query|Topic" | head -1 | sed 's/^#* *//' | cut -c1-120)
    if [ -z "$QUERY_SUMMARY" ]; then
        QUERY_SUMMARY=$(basename "$LATEST_RUN" | sed 's/run_[0-9]*_[0-9]*_//' | tr '_' ' ')
    fi
else
    QUERY_SUMMARY="Query file not found"
fi

# Extract performance metrics
if [ -f "$LATEST_RUN/model_performance.csv" ]; then
    AVG_SCORE=$(awk -F',' 'NR>1 {sum+=$5; count++} END {if(count>0) printf "%.3f", sum/count}' "$LATEST_RUN/model_performance.csv")
    TOP_PERFORMER=$(awk -F',' 'NR>1 {if($5>max){max=$5; name=$2}} END {print name " (" max ")"}' "$LATEST_RUN/model_performance.csv")
    WORST_PERFORMER=$(awk -F',' 'NR>1 {if(min=="" || $5<min){min=$5; name=$2}} END {print name " (" min ")"}' "$LATEST_RUN/model_performance.csv")
    TOTAL_MODELS=$(awk -F',' 'NR>1' "$LATEST_RUN/model_performance.csv" | wc -l | tr -d ' ')
else
    AVG_SCORE="unknown"
    TOP_PERFORMER="unknown"
    WORST_PERFORMER="unknown"
    TOTAL_MODELS="unknown"
fi

# Extract execution metrics
if [ -f "$LATEST_RUN/run_summary.md" ]; then
    EXECUTION_TIME=$(grep -i "execution.*time\|duration\|elapsed" "$LATEST_RUN/run_summary.md" | head -1 | grep -o '[0-9]*\.?[0-9]*' | head -1)
    if [ -z "$EXECUTION_TIME" ]; then EXECUTION_TIME="unknown"; fi
else
    EXECUTION_TIME="unknown"
fi

# Extract combination metrics
if [ -f "$LATEST_RUN/combinations.csv" ]; then
    TOTAL_COMBINATIONS=$(awk -F',' 'NR>1' "$LATEST_RUN/combinations.csv" | wc -l | tr -d ' ')
    FRAMEWORKS_USED=$(awk -F',' 'NR>1 {print $3}' "$LATEST_RUN/combinations.csv" | sort -u | wc -l | tr -d ' ')
    DOMAINS_GENERATED=$(awk -F',' 'NR>1 {print $4}' "$LATEST_RUN/combinations.csv" | sort -u | wc -l | tr -d ' ')
else
    TOTAL_COMBINATIONS="unknown"
    FRAMEWORKS_USED="unknown"
    DOMAINS_GENERATED="unknown"
fi

# Extract synthesis quality metrics
if [ -f "$LATEST_RUN/ideas.csv" ]; then
    SYNTHESIS_IDEAS=$(awk -F',' 'NR>1' "$LATEST_RUN/ideas.csv" | wc -l | tr -d ' ')
else
    SYNTHESIS_IDEAS="unknown"
fi

echo "✅ Metrics extracted:"
echo "   Query: $QUERY_SUMMARY"
echo "   Average Score: $AVG_SCORE"
echo "   Top Performer: $TOP_PERFORMER"
echo "   Worst Performer: $WORST_PERFORMER"
echo "   Total Models: $TOTAL_MODELS"
echo "   Execution Time: ${EXECUTION_TIME} minutes"
echo "   Total Combinations: $TOTAL_COMBINATIONS"
echo "   Frameworks Used: $FRAMEWORKS_USED"
echo "   Domains Generated: $DOMAINS_GENERATED"
echo "   Synthesis Ideas: $SYNTHESIS_IDEAS"
```

### Step 3: Database Performance Analysis
Examine the performance tracking database for trends and historical context:

```bash
# Query recent performance trends
sqlite3 /Users/josephfajen/git/ISEE_Meta_Framework/data/performance_tracking.db "
SELECT run_id, avg_score, total_combinations, total_execution_time_seconds 
FROM test_runs 
ORDER BY timestamp DESC 
LIMIT 10;"

# Identify consistently poor-performing models
sqlite3 /Users/josephfajen/git/ISEE_Meta_Framework/data/performance_tracking.db "
SELECT model_name, AVG(avg_score) as overall_avg, COUNT(*) as run_count
FROM model_performance 
GROUP BY model_name 
HAVING run_count >= 3
ORDER BY overall_avg ASC;"

# Check for API/execution issues
sqlite3 /Users/josephfajen/git/ISEE_Meta_Framework/data/performance_tracking.db "
SELECT * FROM performance_issues 
WHERE detected_at >= date('now', '-7 days')
ORDER BY severity DESC;"
```

### Step 4: Log File Analysis
Examine system logs for operational issues and API performance:

```bash
# Check for recent errors or warnings
tail -50 /Users/josephfajen/git/ISEE_Meta_Framework/dev-server.log
tail -50 /Users/josephfajen/git/ISEE_Meta_Framework/isee-ui.log

# Look for API timeout or failure patterns
grep -i "error\|timeout\|failed" /Users/josephfajen/git/ISEE_Meta_Framework/*.log
```

### Step 5: Configuration and Model Analysis
Review current model configuration for optimization opportunities:

```bash
# Analyze current model collection
python -c "
import json
with open('/Users/josephfajen/git/ISEE_Meta_Framework/openrouter_config.json', 'r') as f:
    config = json.load(f)
    models = config['models']['api_models']
    print(f'Total configured models: {len(models)}')
    
    # Group by provider and cost tier
    providers = {}
    cost_tiers = {}
    for model in models:
        provider = model.get('provider', 'unknown')
        cost_tier = model.get('cost_tier', 'unknown')
        providers[provider] = providers.get(provider, 0) + 1
        cost_tiers[cost_tier] = cost_tiers.get(cost_tier, 0) + 1
    
    print('Providers:', providers)
    print('Cost tiers:', cost_tiers)
"
```

### Step 6: Comprehensive Performance Assessment

**Analyze the following aspects for optimization insights:**

#### 6.1 Model Performance Analysis
- **Top Performers**: Identify models with consistently high scores (>0.5)
- **Poor Performers**: Flag models with low scores (<0.3) or high failure rates
- **Cost Efficiency**: Analyze score-to-cost ratios for budget optimization
- **Speed Analysis**: Identify slow models impacting user experience
- **API Reliability**: Check for timeout patterns or API issues

#### 6.2 Cognitive Framework Effectiveness
- **Framework Specialization**: Which frameworks excel in specific domains?
- **Framework Balance**: Are all cognitive frameworks being utilized effectively?
- **Instruction Quality**: Are certain cognitive approaches consistently underperforming?
- **Domain Synergy**: Which framework×domain combinations produce best results?

#### 6.3 Domain Performance Analysis
- **Dynamic Domain Quality**: How well are AI-generated domains performing?
- **Domain Diversity**: Is the system generating sufficiently diverse knowledge areas?
- **Cross-Domain Synthesis**: Quality of interdisciplinary connections
- **Domain Specialization**: Which domains consistently produce high-quality outputs?

#### 6.4 System Optimization Opportunities
- **Resource Allocation**: Optimal distribution of calls across models/frameworks
- **Execution Efficiency**: Identify bottlenecks in processing pipeline
- **Quality vs. Speed**: Balance between thorough analysis and execution time
- **Cost Optimization**: Reduce expenses while maintaining quality

### Step 7: Strategic Recommendations

Based on the comprehensive analysis, provide specific, actionable recommendations:

#### 7.1 Immediate Actions (Next Session)
- **Model Replacements**: Specific underperforming models to remove/replace
- **Configuration Adjustments**: Parameter tuning for better performance
- **Bug Fixes**: Critical issues requiring immediate attention

#### 7.2 Short-term Optimizations (1-2 weeks)
- **Model Portfolio Refinement**: Curated collections optimization
- **Framework Balancing**: Adjustments to cognitive diversity distribution
- **Performance Monitoring**: Enhanced tracking and alerting

#### 7.3 Long-term Strategic Improvements (1-3 months)
- **Architecture Enhancements**: System-level optimizations
- **Quality Assurance**: Automated quality monitoring and feedback loops
- **User Experience**: Interface and workflow improvements

### Step 8: Learning and Knowledge Extraction

**Focus on ISEE's Core Mission Improvement:**

#### 8.1 Cognitive Diversity Insights
- Are we achieving genuine cognitive diversity or falling into patterns?
- Which combinations produce truly novel and valuable insights?
- How can we enhance the breadth and depth of perspectives?

#### 8.2 Quality Enhancement Learnings
- What factors consistently correlate with high-quality outputs?
- How can we improve synthesis quality and coherence?
- What makes certain model×framework combinations exceptionally effective?

#### 8.3 Scalability and Efficiency Learnings
- How can we maintain quality while reducing execution time and cost?
- What are the optimal parameters for different query types and complexities?
- How can we better predict and optimize resource allocation?

#### 8.4 User Value Optimization
- Which outputs provide the most actionable insights for users?
- How can we improve the practical utility of ISEE analyses?
- What presentation formats maximize comprehension and engagement?

## Expected Outcome

A comprehensive analysis report containing:

1. **Performance Summary**: Overview of latest run quality and key metrics
2. **Model Analysis**: Detailed breakdown of LLM performance with specific recommendations
3. **Framework Effectiveness**: Cognitive diversity assessment and optimization suggestions
4. **System Health**: Operational status, issues, and maintenance needs
5. **Strategic Recommendations**: Prioritized action items for immediate and future improvements
6. **Learning Insights**: Key findings about optimizing ISEE's core mission and effectiveness
7. **Trend Analysis**: Historical performance patterns and trajectory assessment

This analysis should provide clear, data-driven guidance for continuously improving ISEE's ability to generate high-quality, cognitively diverse insights that advance its mission of exploring complex problems through multiple analytical lenses.

### Step 7: Generate Analysis Report and Update Index

**Create the comprehensive single run analysis report:**

```bash
echo "📝 Generating single run analysis report..."

# Create comprehensive analysis report template
cat > "$REPORT_PATH" << EOF
# ISEE Performance Analysis Report - Single Run

**Analysis Date**: $(date +"%Y-%m-%d %H:%M:%S")  
**Run Analyzed**: $RUN_ID  
**Query Summary**: $QUERY_SUMMARY  
**Average Score**: $AVG_SCORE  
**Top Performer**: $TOP_PERFORMER  
**Worst Performer**: $WORST_PERFORMER  
**Total Models**: $TOTAL_MODELS  
**Execution Time**: ${EXECUTION_TIME} minutes  
**Total Combinations**: $TOTAL_COMBINATIONS  
**Frameworks Used**: $FRAMEWORKS_USED  
**Domains Generated**: $DOMAINS_GENERATED  
**Synthesis Ideas**: $SYNTHESIS_IDEAS  

---

## Executive Summary

[Add your comprehensive single run analysis findings here]

**Key Performance Highlights:**
- System performance assessment and overall quality
- Critical successes and areas for improvement
- Strategic implications for ISEE optimization

## Performance Analysis

### Model Performance Breakdown
[Add detailed breakdown of LLM performance with specific insights]

**🏆 Top Performers:**
- [Analysis of best-performing models]

**⚠️ Underperformers:**
- [Analysis of poor-performing models requiring attention]

### Cognitive Framework Effectiveness
[Add framework performance analysis]

**🎯 Most Effective Frameworks:**
- [Framework specialization insights]

### Domain Performance Analysis
[Add domain generation and performance insights]

### Scoring Component Analysis
[Add breakdown of scoring components: feasibility, specificity, comprehensiveness, impact, novelty]

## Quality Assessment of Synthesized Ideas
[Add analysis of the synthesis quality and key findings]

## Strategic Recommendations

### Immediate Actions (Next Session)
- [Critical model issues requiring immediate attention]
- [Configuration adjustments needed]
- [Priority optimizations]

### Short-term Optimizations (1-2 weeks)
- [Performance monitoring improvements]
- [System refinements]

### Long-term Strategic Improvements (1-3 months)
- [Architecture enhancements]
- [Quality optimization initiatives]

## Learning Insights

### Cognitive Diversity Excellence
- [Assessment of cognitive diversity achievement]

### Performance Predictability Patterns
- [Model and framework performance patterns identified]

### System Optimization Insights
- [Key learnings for system improvement]

## Key Performance Metrics Summary

**🎯 Run Health**: [Assessment]  
**🏆 Top Model**: [Best performer with score]  
**🔬 Synthesis Quality**: [Assessment of synthesis output]  
**⚡ Execution Efficiency**: [Runtime and efficiency assessment]  
**⚖️ System Balance**: [Framework and domain distribution assessment]  

**🎯 Priority Focus**: [Key areas requiring attention]

---

*Single run analysis generated by ISEE analyze-last-result command*  
*Report covers comprehensive performance analysis for optimization and strategic planning*
EOF

echo "✅ Analysis report template created at: $REPORT_PATH"
echo ""
echo "📋 Next Steps:"
echo "1. Fill in the comprehensive analysis findings in the report"
echo "2. Review and analyze all files in the run directory"
echo "3. Complete the strategic recommendations section"
echo "4. Update the index when analysis is complete"
```

### Step 8: Update Analysis Index

**Update the index.json file with the new analysis:**

```bash
echo "📋 Updating analysis index..."

# Create Python script to update index.json for single run analysis
python3 << EOF
import json
from datetime import datetime

index_path = "$INDEX_PATH"

# Create report entry with all extracted metrics
report_entry = {
    "analysis_date": "$(date +%Y-%m-%d)",
    "analysis_timestamp": "$ANALYSIS_DATE",
    "analysis_type": "single_run",
    "run_analyzed": "$RUN_ID",
    "query_summary": "$QUERY_SUMMARY",
    "avg_score": float("$AVG_SCORE") if "$AVG_SCORE" != "unknown" and "$AVG_SCORE".replace('.','').replace('-','').isdigit() else None,
    "top_performer": "$TOP_PERFORMER",
    "worst_performer": "$WORST_PERFORMER",
    "total_models": int("$TOTAL_MODELS") if "$TOTAL_MODELS".isdigit() else None,
    "execution_time_minutes": float("$EXECUTION_TIME") if "$EXECUTION_TIME" != "unknown" and "$EXECUTION_TIME".replace('.','').replace('-','').isdigit() else None,
    "total_combinations": int("$TOTAL_COMBINATIONS") if "$TOTAL_COMBINATIONS".isdigit() else None,
    "frameworks_used": int("$FRAMEWORKS_USED") if "$FRAMEWORKS_USED".isdigit() else None,
    "domains_generated": int("$DOMAINS_GENERATED") if "$DOMAINS_GENERATED".isdigit() else None,
    "synthesis_ideas": int("$SYNTHESIS_IDEAS") if "$SYNTHESIS_IDEAS".isdigit() else None,
    "previously_analyzed": $PREVIOUSLY_ANALYZED,
    "file_path": "$(basename "$REPORT_PATH")",
    "status": "template_created"
}

# Load existing index
try:
    with open(index_path, 'r') as f:
        index_data = json.load(f)
except FileNotFoundError:
    index_data = {
        "version": "1.0", 
        "created": "$(date +%Y-%m-%d)",
        "description": "ISEE single run analysis reports index", 
        "reports": []
    }

# Add new report entry to the beginning
index_data["reports"].insert(0, report_entry)
index_data["last_updated"] = datetime.now().isoformat()

# Save updated index
with open(index_path, 'w') as f:
    json.dump(index_data, f, indent=2)

print(f"✅ Updated index.json with single run analysis entry")
print(f"📊 Total reports indexed: {len(index_data['reports'])}")
print(f"🔍 Run: $RUN_ID")
print(f"📁 Report file: $(basename "$REPORT_PATH")")
EOF
```

**Index Search Helper Functions:**

```bash
# Add these helper functions for searching the index
echo "Creating search helper functions..."

cat > "/Users/josephfajen/git/ISEE_Meta_Framework/data/analysis_reports/search_reports.py" << 'EOF'
#!/usr/bin/env python3
import json
import sys
from datetime import datetime

def search_reports(query=None, min_score=None, max_score=None, model_name=None, days_back=None):
    """Search analysis reports by various criteria"""
    try:
        with open('/Users/josephfajen/git/ISEE_Meta_Framework/data/analysis_reports/index.json', 'r') as f:
            index_data = json.load(f)
    except FileNotFoundError:
        print("No index.json found")
        return []
    
    results = []
    for report in index_data.get('reports', []):
        # Query text search
        if query and query.lower() not in report.get('query_summary', '').lower():
            continue
            
        # Score filtering
        if min_score and (not report.get('avg_score') or float(report['avg_score']) < min_score):
            continue
        if max_score and (not report.get('avg_score') or float(report['avg_score']) > max_score):
            continue
            
        # Model name search
        if model_name and (model_name.lower() not in report.get('top_performer', '').lower() and 
                          model_name.lower() not in report.get('worst_performer', '').lower()):
            continue
            
        # Date filtering
        if days_back:
            report_date = datetime.fromisoformat(report['analysis_date'])
            if (datetime.now() - report_date).days > days_back:
                continue
                
        results.append(report)
    
    return results

def print_results(results):
    """Print search results in a formatted way"""
    if not results:
        print("No reports found matching criteria")
        return
        
    print(f"\nFound {len(results)} reports:")
    print("-" * 80)
    for report in results:
        print(f"Date: {report['analysis_date']}")
        print(f"Run: {report['run_analyzed']}")
        print(f"Query: {report['query_summary'][:60]}...")
        print(f"Score: {report.get('avg_score', 'N/A')} | Top: {report.get('top_performer', 'N/A')}")
        print(f"File: {report['file_path']}")
        print("-" * 40)

if __name__ == "__main__":
    # Command line interface
    if len(sys.argv) == 1:
        # Show recent reports
        results = search_reports(days_back=30)
        print("Recent reports (last 30 days):")
        print_results(results)
    elif sys.argv[1] == "query" and len(sys.argv) > 2:
        results = search_reports(query=" ".join(sys.argv[2:]))
        print_results(results)
    elif sys.argv[1] == "low_score":
        threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.4
        results = search_reports(max_score=threshold)
        print(f"Reports with score <= {threshold}:")
        print_results(results)
    elif sys.argv[1] == "model" and len(sys.argv) > 2:
        results = search_reports(model_name=" ".join(sys.argv[2:]))
        print_results(results)
    else:
        print("Usage:")
        print("  python3 search_reports.py                    # Recent reports")
        print("  python3 search_reports.py query <text>       # Search by query text")
        print("  python3 search_reports.py low_score [0.4]    # Reports with low scores")
        print("  python3 search_reports.py model <name>       # Reports mentioning model")
EOF

chmod +x "/Users/josephfajen/git/ISEE_Meta_Framework/data/analysis_reports/search_reports.py"

echo "Search helper created. Usage examples:"
echo "  python3 data/analysis_reports/search_reports.py"
echo "  python3 data/analysis_reports/search_reports.py query education"
echo "  python3 data/analysis_reports/search_reports.py low_score 0.3"
echo "  python3 data/analysis_reports/search_reports.py model deepseek"
```

### Step 9: Complete Analysis and Finalize Report

**After completing your comprehensive analysis, finalize the report:**

```bash
# Mark analysis as completed (run after finishing your detailed analysis)
echo "🏁 Finalizing analysis report..."

python3 << EOF
import json
from datetime import datetime

index_path = "$INDEX_PATH"
with open(index_path, 'r') as f:
    index_data = json.load(f)

# Update the most recent report status
if index_data['reports']:
    most_recent = index_data['reports'][0]
    most_recent['status'] = 'completed'
    most_recent['analysis_completed_at'] = datetime.now().isoformat()
    
    print(f"✅ Marked single run analysis as completed: {most_recent.get('run_analyzed')}")
    
    # Add completion metadata (optional - add after analysis)
    # most_recent['key_insights'] = ["Insight 1", "Insight 2", ...]
    # most_recent['recommendations'] = ["Rec 1", "Rec 2", ...]
    # most_recent['critical_findings'] = ["Finding 1", "Finding 2", ...]

with open(index_path, 'w') as f:
    json.dump(index_data, f, indent=2)

print("📋 Analysis report marked as completed in index")
EOF

echo ""
echo "🎉 === ANALYSIS COMPLETE ==="
echo "📁 Report: $REPORT_PATH"
echo "🎯 Run Analyzed: $RUN_ID"
echo "📊 Query: $QUERY_SUMMARY"
echo "⭐ Score: $AVG_SCORE"
echo ""
echo "🔍 Search existing reports: python3 $REPORTS_DIR/search_reports.py"
echo "📖 View analysis: cat '$REPORT_PATH'"
echo "🗂️  Browse reports: ls -la $REPORTS_DIR/analysis_*.md"
```

## Usage Instructions

**📋 How to Use This Command:**

1. **Identify the run you want to analyze** by checking available runs:
   ```bash
   ls data/output/ | grep run_ | sort -r | head -10
   ```

2. **Specify the exact run folder name** when requesting analysis (e.g., "run_20250723_070134")

3. **Follow the step-by-step analysis process** outlined above:
   - Setup analysis infrastructure
   - Extract metrics from the target run
   - Perform comprehensive file analysis
   - Review database trends and system health
   - Generate strategic recommendations
   - Create and finalize the analysis report

**📊 Example Usage:**
```bash
# User specifies: "Please analyze run_20250723_070134"
# Replace USER_SPECIFIED_RUN_ID with: run_20250723_070134
# Then follow all steps in sequence
```

**🔍 Search and Discovery:**
```bash
# View recent analysis reports
python3 data/analysis_reports/search_reports.py

# Search by query content
python3 data/analysis_reports/search_reports.py query "video mining"

# Find low-performing runs
python3 data/analysis_reports/search_reports.py low_score 0.4

# Search by model performance
python3 data/analysis_reports/search_reports.py model "grok"
```

**📁 Report Management:**
- All reports are saved in `data/analysis_reports/`
- Index maintained in `data/analysis_reports/index.json`
- Reports follow naming convention: `analysis_YYYYMMDD_HHMMSS_run_ID.md`
- Search functionality available through `search_reports.py`