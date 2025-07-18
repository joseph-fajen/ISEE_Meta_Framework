# Comprehensive ISEE Performance Analysis

Conduct a comprehensive analysis of recent ISEE query executions from the past 48 hours that haven't been analyzed yet, to identify optimization opportunities and improve the framework's core mission of cognitive diversity exploration.

## Command Features

**✨ Smart Analysis Modes:**
- **Single Run**: Deep analysis of one unanalyzed run (detailed file examination)
- **Detailed Batch**: Comprehensive analysis of 2-5 unanalyzed runs (comparative insights)
- **Summary Batch**: High-level analysis of 6+ unanalyzed runs (trend identification)

**🎯 Intelligent Run Detection:**
- Automatically finds runs from past 48 hours
- Excludes already-analyzed runs via index tracking
- Provides clear status reporting and run count

**📊 Comprehensive Coverage:**
- Model performance metrics and cost efficiency analysis
- Cognitive framework effectiveness and specialization patterns
- Database trends and historical performance context
- Cross-run comparative insights and optimization recommendations

**📁 Organized Reporting:**
- Structured analysis reports with metadata headers
- Searchable index.json for historical analysis tracking
- Batch CSV data collection for multi-run insights
- Helper scripts for analysis report discovery

## Instructions

This command performs a systematic analysis of ISEE's recent executions to derive actionable insights for continuous improvement and optimization of the framework's performance. It automatically detects unanalyzed runs from the past 48 hours and selects the appropriate analysis mode.

### Step 1: Identify Target Runs and Setup Analysis
```bash
# Setup analysis infrastructure
ANALYSIS_DATE=$(date +%Y%m%d_%H%M%S)
REPORTS_DIR="/Users/josephfajen/git/ISEE_Meta_Framework/data/analysis_reports"
INDEX_PATH="$REPORTS_DIR/index.json"

# Create analysis reports directory if it doesn't exist
mkdir -p "$REPORTS_DIR"

# Load existing analysis index to check what's already been analyzed
if [ -f "$INDEX_PATH" ]; then
    echo "Loading existing analysis index..."
    ANALYZED_RUNS=$(python3 -c "
import json
try:
    with open('$INDEX_PATH', 'r') as f:
        data = json.load(f)
    analyzed = [report.get('run_analyzed', '') for report in data.get('reports', [])]
    print(' '.join(analyzed))
except:
    print('')
")
else
    echo "No existing analysis index found. Creating new index."
    ANALYZED_RUNS=""
fi

# Find all runs from the past 48 hours
echo "Finding runs from the past 48 hours..."
RECENT_RUNS=$(find /Users/josephfajen/git/ISEE_Meta_Framework/data/output -name "run_*" -type d -newermt "48 hours ago" | sort -r)

# Filter out already analyzed runs
UNANALYZED_RUNS=""
for run_dir in $RECENT_RUNS; do
    run_id=$(basename "$run_dir")
    if [[ ! " $ANALYZED_RUNS " =~ " $run_id " ]]; then
        UNANALYZED_RUNS="$UNANALYZED_RUNS $run_dir"
    fi
done

# Trim leading space
UNANALYZED_RUNS=$(echo "$UNANALYZED_RUNS" | sed 's/^ *//')

echo "Recent runs found: $(echo $RECENT_RUNS | wc -w)"
echo "Already analyzed: $(echo $ANALYZED_RUNS | wc -w)"
echo "Unanalyzed runs to process: $(echo $UNANALYZED_RUNS | wc -w)"

if [ -z "$UNANALYZED_RUNS" ]; then
    echo "No unanalyzed runs found from the past 48 hours."
    echo "Most recent run: $(find /Users/josephfajen/git/ISEE_Meta_Framework/data/output -name "run_*" -type d | sort -r | head -1)"
    echo "Use force mode or analyze the most recent run even if already analyzed?"
    exit 0
fi

# Show runs to be analyzed
echo "Runs to be analyzed:"
for run_dir in $UNANALYZED_RUNS; do
    run_id=$(basename "$run_dir")
    run_date=$(echo "$run_id" | sed 's/run_//' | sed 's/_/ /' | head -c 17)
    echo "  - $run_id ($run_date)"
done

# Setup comprehensive analysis report path
BATCH_REPORT_PATH="$REPORTS_DIR/batch_analysis_${ANALYSIS_DATE}.md"
echo "Batch analysis report will be saved to: $BATCH_REPORT_PATH"
```

### Step 1.5: Analysis Mode Selection
Choose analysis approach based on number of runs to analyze:

```bash
# Count unanalyzed runs
RUN_COUNT=$(echo $UNANALYZED_RUNS | wc -w)

if [ "$RUN_COUNT" -eq 1 ]; then
    echo "Single run analysis mode"
    SINGLE_RUN_MODE=true
    LATEST_RUN=$(echo $UNANALYZED_RUNS | tr ' ' '\n' | head -1)
    RUN_ID=$(basename "$LATEST_RUN")
    REPORT_PATH="$REPORTS_DIR/analysis_${ANALYSIS_DATE}_${RUN_ID}.md"
elif [ "$RUN_COUNT" -le 5 ]; then
    echo "Detailed batch analysis mode (≤5 runs)"
    SINGLE_RUN_MODE=false
    DETAILED_BATCH=true
    REPORT_PATH="$BATCH_REPORT_PATH"
else
    echo "Summary batch analysis mode (>5 runs)"
    SINGLE_RUN_MODE=false
    DETAILED_BATCH=false
    REPORT_PATH="$BATCH_REPORT_PATH"
fi

echo "Analysis mode: $([[ $SINGLE_RUN_MODE == true ]] && echo "Single run" || ([[ $DETAILED_BATCH == true ]] && echo "Detailed batch" || echo "Summary batch"))"
echo "Report path: $REPORT_PATH"
```

### Step 2: Comprehensive File Analysis

**For single run mode**: Analyze ALL files in the target run directory.
**For batch mode**: Focus on key metrics and comparative analysis across runs.

**Core Result Files to Analyze:**
- `isee_result.md` - Main synthesis output and quality assessment
- `analysis.md` - Automated analysis and scoring breakdown  
- `run_summary.md` - Execution summary and key metrics
- `metadata.md` - Detailed combination metadata and execution details

**Performance Data Files:**
- `model_performance.csv` - Individual LLM performance metrics (scores, response times, success rates)
- `combinations.csv` - All framework×model×domain combinations executed
- `ideas.csv` - Individual response evaluations and scores

**Visual Analytics:**
- `model_comparison.png` - LLM performance visualization
- `domain_comparison.png` - Domain effectiveness analysis
- `instruction_comparison.png` - Cognitive framework performance  
- `scoring_components.png` - Score distribution analysis

**Additional Files:**
- `isee_report.html` - HTML report if generated
- `quality_assessment.md` - Quality analysis if available
- Any query-specific files or screenshots

### Step 2.5: Batch Analysis Data Collection
For multiple runs, collect comparative metrics:

```bash
if [ "$SINGLE_RUN_MODE" != true ]; then
    echo "Collecting batch analysis data..."
    
    # Create temporary CSV for batch metrics
    BATCH_CSV="/tmp/batch_analysis_${ANALYSIS_DATE}.csv"
    echo "run_id,query_summary,avg_score,top_model,top_score,worst_model,worst_score,total_models,execution_time,total_combinations,frameworks_used,domains_generated" > "$BATCH_CSV"
    
    # Process each run
    for run_dir in $UNANALYZED_RUNS; do
        run_id=$(basename "$run_dir")
        echo "Processing $run_id..."
        
        # Extract metrics from each run
        if [ -f "$run_dir/isee_result.md" ]; then
            query_summary=$(head -50 "$run_dir/isee_result.md" | grep -E "^#|Query|Topic" | head -1 | sed 's/^#* *//' | cut -c1-80 | tr ',' ';')
        else
            query_summary="Unknown"
        fi
        
        if [ -f "$run_dir/model_performance.csv" ]; then
            avg_score=$(awk -F',' 'NR>1 {sum+=$5; count++} END {if(count>0) printf "%.3f", sum/count; else print "0"}' "$run_dir/model_performance.csv")
            top_result=$(awk -F',' 'NR>1 {if($5>max){max=$5; name=$2}} END {print name ":" max}' "$run_dir/model_performance.csv")
            worst_result=$(awk -F',' 'NR>1 {if(min=="" || $5<min){min=$5; name=$2}} END {print name ":" min}' "$run_dir/model_performance.csv")
            total_models=$(awk -F',' 'NR>1' "$run_dir/model_performance.csv" | wc -l | tr -d ' ')
            
            top_model=$(echo "$top_result" | cut -d':' -f1)
            top_score=$(echo "$top_result" | cut -d':' -f2)
            worst_model=$(echo "$worst_result" | cut -d':' -f1)
            worst_score=$(echo "$worst_result" | cut -d':' -f2)
        else
            avg_score="0"
            top_model="unknown"
            top_score="0"
            worst_model="unknown"
            worst_score="0"
            total_models="0"
        fi
        
        if [ -f "$run_dir/combinations.csv" ]; then
            total_combinations=$(awk -F',' 'NR>1' "$run_dir/combinations.csv" | wc -l | tr -d ' ')
            frameworks_used=$(awk -F',' 'NR>1 {print $3}' "$run_dir/combinations.csv" | sort -u | wc -l | tr -d ' ')
            domains_generated=$(awk -F',' 'NR>1 {print $4}' "$run_dir/combinations.csv" | sort -u | wc -l | tr -d ' ')
        else
            total_combinations="0"
            frameworks_used="0" 
            domains_generated="0"
        fi
        
        if [ -f "$run_dir/run_summary.md" ]; then
            execution_time=$(grep -i "execution.*time\|duration\|elapsed" "$run_dir/run_summary.md" | head -1 | grep -o '[0-9]*\.?[0-9]*' | head -1)
            if [ -z "$execution_time" ]; then execution_time="0"; fi
        else
            execution_time="0"
        fi
        
        # Add to batch CSV
        echo "$run_id,$query_summary,$avg_score,$top_model,$top_score,$worst_model,$worst_score,$total_models,$execution_time,$total_combinations,$frameworks_used,$domains_generated" >> "$BATCH_CSV"
    done
    
    echo "Batch metrics collected in $BATCH_CSV"
    echo "Sample of collected data:"
    head -3 "$BATCH_CSV" | column -t -s ','
fi
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

### Step 9: Generate Analysis Report and Update Index

**Create the comprehensive analysis report:**

```bash
# Generate report based on analysis mode
if [ "$SINGLE_RUN_MODE" = true ]; then
    echo "Generating single run analysis report..."
    
    # Extract metadata for single run
    QUERY_SUMMARY=$(head -50 "$LATEST_RUN/isee_result.md" | grep -E "^#|Query|Topic" | head -1 | sed 's/^#* *//' | cut -c1-100)
    if [ -z "$QUERY_SUMMARY" ]; then
        QUERY_SUMMARY=$(basename "$LATEST_RUN" | sed 's/run_[0-9]*_[0-9]*_//' | tr '_' ' ')
    fi

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

    if [ -f "$LATEST_RUN/run_summary.md" ]; then
        EXECUTION_TIME=$(grep -i "execution.*time\|duration\|elapsed" "$LATEST_RUN/run_summary.md" | head -1 | grep -o '[0-9]*\.?[0-9]*' | head -1)
    else
        EXECUTION_TIME="unknown"
    fi

    # Single run report template
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

---

## Executive Summary
[Add your single run analysis findings here]

## Performance Analysis
[Add detailed performance breakdown for this specific run]

## Strategic Recommendations
[Add actionable recommendations based on this run]

## Learning Insights
[Add key insights for ISEE optimization from this run]

---
*Single run analysis generated by ISEE analyze-last-result command*
EOF

else
    echo "Generating batch analysis report..."
    
    # Batch analysis metadata
    BATCH_SUMMARY="$RUN_COUNT runs from past 48 hours"
    OVERALL_AVG=$(awk -F',' 'NR>1 {sum+=$3; count++} END {if(count>0) printf "%.3f", sum/count; else print "0"}' "$BATCH_CSV")
    BEST_RUN=$(awk -F',' 'NR>1 {if($3>max){max=$3; run=$1}} END {print run " (" max ")"}' "$BATCH_CSV")
    WORST_RUN=$(awk -F',' 'NR>1 {if(min=="" || $3<min){min=$3; run=$1}} END {print run " (" min ")"}' "$BATCH_CSV")
    TOTAL_RUNS="$RUN_COUNT"

    # Batch report template
    cat > "$REPORT_PATH" << EOF
# ISEE Performance Analysis Report - Batch Analysis

**Analysis Date**: $(date +"%Y-%m-%d %H:%M:%S")  
**Analysis Scope**: $BATCH_SUMMARY  
**Total Runs Analyzed**: $TOTAL_RUNS  
**Overall Average Score**: $OVERALL_AVG  
**Best Performing Run**: $BEST_RUN  
**Worst Performing Run**: $WORST_RUN  

---

## Executive Summary
[Add your batch analysis findings across all $RUN_COUNT runs]

## Comparative Performance Analysis
[Add trends and patterns across the analyzed runs]

### Run-by-Run Overview
EOF
    
    # Add run details to batch report
    echo "$(tail -n +2 "$BATCH_CSV")" | while IFS=',' read -r run_id query_summary avg_score top_model top_score worst_model worst_score total_models execution_time total_combinations frameworks_used domains_generated; do
        cat >> "$REPORT_PATH" << EOF

**$run_id**
- Query: $query_summary
- Score: $avg_score (Best: $top_model $top_score, Worst: $worst_model $worst_score)
- Models: $total_models | Combinations: $total_combinations | Time: ${execution_time}min
- Frameworks: $frameworks_used | Domains: $domains_generated
EOF
    done
    
    cat >> "$REPORT_PATH" << EOF

## Cross-Run Strategic Recommendations
[Add recommendations based on patterns across multiple runs]

## Batch Learning Insights
[Add insights from analyzing multiple runs together]

---
*Batch analysis of $RUN_COUNT runs generated by ISEE analyze-last-result command*
EOF

fi

echo "Analysis report template created at: $REPORT_PATH"
```

**Update the index.json file:**

```bash
# Create Python script to update index.json based on analysis mode
if [ "$SINGLE_RUN_MODE" = true ]; then
    echo "Updating index for single run analysis..."
    python3 << EOF
import json
from datetime import datetime

index_path = "$INDEX_PATH"
report_entry = {
    "analysis_date": "$(date +%Y-%m-%d)",
    "analysis_timestamp": "$ANALYSIS_DATE",
    "analysis_type": "single_run",
    "run_analyzed": "$RUN_ID",
    "query_summary": "$QUERY_SUMMARY",
    "avg_score": "$AVG_SCORE" if "$AVG_SCORE" != "unknown" else None,
    "top_performer": "$TOP_PERFORMER",
    "worst_performer": "$WORST_PERFORMER", 
    "total_models": int("$TOTAL_MODELS") if "$TOTAL_MODELS".isdigit() else None,
    "execution_time_minutes": float("$EXECUTION_TIME") if "$EXECUTION_TIME" != "unknown" and "$EXECUTION_TIME".replace('.','').replace('-','').isdigit() else None,
    "file_path": "$(basename "$REPORT_PATH")",
    "status": "template_created"
}

# Load existing index
try:
    with open(index_path, 'r') as f:
        index_data = json.load(f)
except FileNotFoundError:
    index_data = {"version": "1.0", "description": "ISEE analysis reports index", "reports": []}

# Add new report entry
index_data["reports"].insert(0, report_entry)
index_data["last_updated"] = datetime.now().isoformat()

# Save updated index
with open(index_path, 'w') as f:
    json.dump(index_data, f, indent=2)

print(f"Updated index.json with single run report entry")
print(f"Total reports indexed: {len(index_data['reports'])}")
EOF

else
    echo "Updating index for batch analysis..."
    python3 << EOF
import json
import csv
from datetime import datetime

index_path = "$INDEX_PATH"
batch_csv = "$BATCH_CSV"

# Read batch data
batch_runs = []
with open(batch_csv, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        batch_runs.append(row['run_id'])

report_entry = {
    "analysis_date": "$(date +%Y-%m-%d)",
    "analysis_timestamp": "$ANALYSIS_DATE",
    "analysis_type": "batch_analysis",
    "runs_analyzed": batch_runs,
    "run_count": $RUN_COUNT,
    "overall_avg_score": float("$OVERALL_AVG") if "$OVERALL_AVG" != "0" else None,
    "best_run": "$BEST_RUN",
    "worst_run": "$WORST_RUN",
    "analysis_scope": "Past 48 hours unanalyzed runs",
    "file_path": "$(basename "$REPORT_PATH")",
    "status": "template_created"
}

# Load existing index
try:
    with open(index_path, 'r') as f:
        index_data = json.load(f)
except FileNotFoundError:
    index_data = {"version": "1.0", "description": "ISEE analysis reports index", "reports": []}

# Add batch report entry
index_data["reports"].insert(0, report_entry)

# Also mark all individual runs as analyzed in batch
for run_id in batch_runs:
    individual_entry = {
        "analysis_date": "$(date +%Y-%m-%d)",
        "analysis_timestamp": "$ANALYSIS_DATE",
        "analysis_type": "batch_component",
        "run_analyzed": run_id,
        "batch_analysis_file": "$(basename "$REPORT_PATH")",
        "status": "analyzed_in_batch"
    }
    index_data["reports"].append(individual_entry)

index_data["last_updated"] = datetime.now().isoformat()

# Save updated index
with open(index_path, 'w') as f:
    json.dump(index_data, f, indent=2)

print(f"Updated index.json with batch analysis covering {len(batch_runs)} runs")
print(f"Total reports indexed: {len(index_data['reports'])}")
EOF

fi
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

**Final Steps:**

After completing your comprehensive analysis above, remember to:

1. **Fill in the analysis report** at `$REPORT_PATH` with your detailed findings
2. **Update the status** in index.json from "template_created" to "completed"  
3. **Add key findings and recommendations** to the index entry for better searchability

```bash
# Mark analysis as completed (run after finishing your analysis)
echo "Marking analysis as completed..."

python3 << EOF
import json
from datetime import datetime

index_path = "$INDEX_PATH"
with open(index_path, 'r') as f:
    index_data = json.load(f)

# Update the most recent report status (whether single or batch)
if index_data['reports']:
    most_recent = index_data['reports'][0]
    most_recent['status'] = 'completed'
    most_recent['analysis_completed_at'] = datetime.now().isoformat()
    
    # Add completion metadata
    if most_recent.get('analysis_type') == 'single_run':
        print(f"Marked single run analysis as completed: {most_recent.get('run_analyzed')}")
    elif most_recent.get('analysis_type') == 'batch_analysis':
        print(f"Marked batch analysis as completed: {most_recent.get('run_count')} runs")
    
    # Optionally add key findings summary
    # most_recent['key_findings'] = ["Finding 1", "Finding 2", ...]
    # most_recent['recommendations_count'] = X

with open(index_path, 'w') as f:
    json.dump(index_data, f, indent=2)

print("Analysis report marked as completed in index")
EOF

# Cleanup temporary files
if [ "$SINGLE_RUN_MODE" != true ] && [ -f "$BATCH_CSV" ]; then
    echo "Cleaning up temporary batch CSV: $BATCH_CSV"
    rm "$BATCH_CSV"
fi

echo ""
echo "=== ANALYSIS COMPLETE ==="
echo "Report: $REPORT_PATH"
echo "Mode: $([[ $SINGLE_RUN_MODE == true ]] && echo "Single run analysis" || echo "Batch analysis ($RUN_COUNT runs)")"
echo "Next: Fill in analysis findings and strategic recommendations"
echo ""
echo "Search existing reports: python3 $REPORTS_DIR/search_reports.py"
echo "View latest analysis: cat '$REPORT_PATH'"
```

## Usage Examples

**Basic usage** (analyzes unanalyzed runs from past 48 hours):
```bash
/analyze-last-result
```

**Force analyze most recent run** (even if already analyzed):
```bash
# Manually set latest run and force single mode
LATEST_RUN=$(find /Users/josephfajen/git/ISEE_Meta_Framework/data/output -name "run_*" -type d | sort -r | head -1)
UNANALYZED_RUNS="$LATEST_RUN"
# Then continue with analysis steps
```

**Search existing analyses**:
```bash
python3 /Users/josephfajen/git/ISEE_Meta_Framework/data/analysis_reports/search_reports.py
python3 /Users/josephfajen/git/ISEE_Meta_Framework/data/analysis_reports/search_reports.py query education
python3 /Users/josephfajen/git/ISEE_Meta_Framework/data/analysis_reports/search_reports.py low_score 0.3
```