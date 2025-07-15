# Comprehensive ISEE Performance Analysis

Conduct a comprehensive analysis of the most recent ISEE query execution to identify optimization opportunities and improve the framework's core mission of cognitive diversity exploration.

## Instructions

This command performs a systematic analysis of ISEE's latest execution to derive actionable insights for continuous improvement and optimization of the framework's performance.

### Step 1: Identify Most Recent Run and Setup Analysis
```bash
# Find the most recent run directory
LATEST_RUN=$(find /Users/josephfajen/git/ISEE_Meta_Framework/data/output -name "run_*" -type d | sort -r | head -1)
echo "Analyzing run: $LATEST_RUN"

# Setup analysis report path and metadata
ANALYSIS_DATE=$(date +%Y%m%d_%H%M%S)
RUN_ID=$(basename "$LATEST_RUN")
REPORT_PATH="/Users/josephfajen/git/ISEE_Meta_Framework/data/analysis_reports/analysis_${ANALYSIS_DATE}_${RUN_ID}.md"
INDEX_PATH="/Users/josephfajen/git/ISEE_Meta_Framework/data/analysis_reports/index.json"

echo "Analysis report will be saved to: $REPORT_PATH"
```

### Step 2: Comprehensive File Analysis
Analyze ALL files in the most recent run directory to extract complete performance insights:

**Core Result Files:**
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
# Extract key metadata for indexing
echo "Extracting metadata from run files..."

# Get query summary from isee_result.md
QUERY_SUMMARY=$(head -50 "$LATEST_RUN/isee_result.md" | grep -E "^#|Query|Topic" | head -1 | sed 's/^#* *//' | cut -c1-100)
if [ -z "$QUERY_SUMMARY" ]; then
    QUERY_SUMMARY=$(basename "$LATEST_RUN" | sed 's/run_[0-9]*_[0-9]*_//' | tr '_' ' ')
fi

# Get performance metrics from model_performance.csv or analysis.md
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

# Get execution time from run_summary.md or metadata.md
if [ -f "$LATEST_RUN/run_summary.md" ]; then
    EXECUTION_TIME=$(grep -i "execution.*time\|duration\|elapsed" "$LATEST_RUN/run_summary.md" | head -1 | grep -o '[0-9]*\.?[0-9]*' | head -1)
else
    EXECUTION_TIME="unknown"
fi

echo "Metadata extracted:"
echo "  Query: $QUERY_SUMMARY"
echo "  Avg Score: $AVG_SCORE"
echo "  Top Performer: $TOP_PERFORMER"
echo "  Execution Time: ${EXECUTION_TIME} minutes"
```

**Start the analysis report with metadata header:**

```bash
cat > "$REPORT_PATH" << EOF
# Comprehensive ISEE Performance Analysis Report

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
[Add your analysis findings here]

## Performance Analysis
[Add detailed performance breakdown here]

## Strategic Recommendations
[Add actionable recommendations here]

## Learning Insights
[Add key insights for ISEE optimization here]

---
*Report generated by ISEE analyze-last-result command*
EOF

echo "Analysis report template created at: $REPORT_PATH"
```

**Update the index.json file:**

```bash
# Create Python script to update index.json
python3 << EOF
import json
import os
from datetime import datetime

index_path = "$INDEX_PATH"
report_entry = {
    "analysis_date": "$(date +%Y-%m-%d)",
    "analysis_timestamp": "$ANALYSIS_DATE",
    "run_analyzed": "$RUN_ID",
    "query_summary": "$QUERY_SUMMARY",
    "avg_score": "$AVG_SCORE" if "$AVG_SCORE" != "unknown" else None,
    "top_performer": "$TOP_PERFORMER",
    "worst_performer": "$WORST_PERFORMER", 
    "total_models": int("$TOTAL_MODELS") if "$TOTAL_MODELS".isdigit() else None,
    "execution_time_minutes": float("$EXECUTION_TIME") if "$EXECUTION_TIME" != "unknown" and "$EXECUTION_TIME".replace('.','').isdigit() else None,
    "file_path": "analysis_${ANALYSIS_DATE}_${RUN_ID}.md",
    "status": "template_created"
}

# Load existing index
try:
    with open(index_path, 'r') as f:
        index_data = json.load(f)
except FileNotFoundError:
    index_data = {"version": "1.0", "description": "ISEE analysis reports index", "reports": []}

# Add new report entry
index_data["reports"].insert(0, report_entry)  # Add to beginning for newest first
index_data["last_updated"] = datetime.now().isoformat()

# Save updated index
with open(index_path, 'w') as f:
    json.dump(index_data, f, indent=2)

print(f"Updated index.json with new report entry")
print(f"Total reports indexed: {len(index_data['reports'])}")
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

**Final Steps:**

After completing your comprehensive analysis above, remember to:

1. **Fill in the analysis report** at `$REPORT_PATH` with your detailed findings
2. **Update the status** in index.json from "template_created" to "completed"
3. **Add key findings and recommendations** to the index entry for better searchability

```bash
# Mark analysis as completed (run after finishing your analysis)
python3 << EOF
import json

index_path = "$INDEX_PATH"
with open(index_path, 'r') as f:
    index_data = json.load(f)

# Update the most recent report status
if index_data['reports']:
    index_data['reports'][0]['status'] = 'completed'
    index_data['reports'][0]['analysis_completed_at'] = "$(date --iso-8601=seconds)"
    
    # Optionally add key findings summary
    # index_data['reports'][0]['key_findings'] = ["Finding 1", "Finding 2", ...]
    # index_data['reports'][0]['recommendations_count'] = X

with open(index_path, 'w') as f:
    json.dump(index_data, f, indent=2)

print("Report marked as completed in index")
EOF
```