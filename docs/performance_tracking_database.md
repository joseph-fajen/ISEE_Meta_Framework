# ISEE Performance Tracking Database

## Overview

The ISEE Meta Framework includes a sophisticated **SQLite-based performance tracking system** that automatically captures, analyzes, and provides insights from every test execution. This system transforms your individual test runs into institutional knowledge for data-driven collection optimization decisions.

## 🚀 Quick Start

The system works **completely automatically** with Web UI tests:

1. **Run any test** via the Web UI
2. **Database automatically captures** all performance data
3. **Analysis tools immediately available** for insights

No manual intervention required!

## 🗄️ Database Architecture

### Core Tables

The performance database (`data/performance_tracking.db`) contains four main tables:

#### **test_runs**
Master record of each test execution
- `run_id`: Unique identifier (timestamp-based)
- `collection_name`: Which LLM collection was used
- `query_text`: The actual query executed
- `total_combinations`: Number of LLM calls made
- `avg_score`: Overall quality score
- `execution_time`: How long the test took
- `frameworks_used`: Cognitive frameworks applied
- `domains_used`: Knowledge domains involved

#### **model_performance** 
Individual model metrics within each test
- `model_id`: Unique model identifier
- `model_name`: Human-readable model name
- `model_provider`: OpenAI, Google, Anthropic, etc.
- `avg_score`: Model's quality performance
- `avg_execution_time`: Speed metrics
- `avg_response_length`: Content richness
- `success_rate`: Reliability metrics

#### **performance_issues**
Automatically detected problems
- `issue_type`: poor_quality, slow_execution, short_responses
- `issue_description`: Specific details about the problem
- `severity`: high, medium, low
- `model_id`: Which model has the issue

#### **framework_performance**
Cognitive framework effectiveness (future enhancement)

## 📊 Analysis Tools

### Command Line Interface

#### **Basic Performance Summary**
```bash
# View all collections comparison
python performance_analysis.py --compare

# Output shows:
# - Test run counts
# - Average scores
# - Speed metrics
# - Issue counts
```

#### **Model Performance Ranking**
```bash
# Rank models within a specific collection
python performance_analysis.py --models "Premium Diversity"

# See all models across collections
python performance_analysis.py --models
```

#### **Provider Analysis**
```bash
# Compare performance by provider (OpenAI vs Google vs Anthropic, etc.)
python performance_analysis.py --providers
```

#### **Issue Detection**
```bash
# View all performance issues
python performance_tracker.py --issues

# View only high-severity issues
python performance_analysis.py --recommend "Collection Name"
```

#### **Comprehensive Reports**
```bash
# Generate full optimization report for a collection
python performance_analysis.py --report "Reliable Exploration"

# Output includes:
# - Collection overview
# - Model rankings
# - Replacement recommendations
# - Provider analysis
```

### Manual Database Ingestion (if needed)

For CLI-only tests, manually ingest results:
```bash
python performance_tracker.py --ingest data/output/run_YYYYMMDD_HHMMSS --collection "Collection Name"
```

## 🎯 Practical Usage Scenarios

### **1. Collection Optimization**

**Goal**: Improve a collection's performance

```bash
# 1. Identify underperforming collection
python performance_analysis.py --compare

# 2. Get detailed breakdown
python performance_analysis.py --report "Reliable Exploration"

# 3. Review recommendations
python performance_analysis.py --recommend "Reliable Exploration"
```

**Example Output**:
```
⚠️  Models with high-severity issues in Reliable Exploration:
  🚨 GPT-3.5 Turbo (OpenRouter) (openrouter)
     Issues: poor_quality,short_responses
     Performance: Score 0.269, Speed 0.5s
     💡 Recommendation: Consider replacement
```

### **2. Model Replacement Decisions**

**Scenario**: Replace underperforming models

```bash
# Find problematic models
python performance_analysis.py --recommend "Premium Diversity"

# Check provider alternatives
python performance_analysis.py --providers

# Validate trends over time
python performance_analysis.py --models "Premium Diversity"
```

### **3. Performance Trend Analysis**

**Goal**: Track model performance over time

```bash
# View model trends (shows performance across multiple tests)
python performance_tracker.py --trends "x-ai/grok-3"

# Compare collections over time
python performance_analysis.py --compare
```

### **4. Cost vs Performance Optimization**

**Scenario**: Balance cost efficiency with quality

1. **Identify cost tiers** in your collections
2. **Analyze performance by tier** using provider analysis
3. **Find sweet spots** where cost-effective models deliver good quality
4. **Replace expensive underperformers** with budget alternatives

### **5. Quality Assurance**

**Goal**: Ensure consistent performance standards

```bash
# Regular quality checks
python performance_tracker.py --issues

# Set up alerts for severe issues
python performance_analysis.py --recommend "Collection Name" | grep "🚨"
```

## 📈 Advanced Usage

### **SQL Queries**

For custom analysis, directly query the SQLite database:

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/performance_tracking.db')

# Custom query example: Find fastest models by provider
query = '''
    SELECT model_provider, model_name, 
           AVG(avg_execution_time_seconds) as avg_speed,
           AVG(avg_score) as avg_quality
    FROM model_performance 
    GROUP BY model_provider, model_name
    ORDER BY avg_speed ASC
'''

df = pd.read_sql_query(query, conn)
print(df)
```

### **Performance Monitoring Automation**

Set up regular performance monitoring:

```bash
# Weekly performance review script
#!/bin/bash
echo "=== Weekly ISEE Performance Report ==="
python performance_analysis.py --compare
echo ""
python performance_tracker.py --issues
```

### **Data Export**

Export performance data for external analysis:

```python
from performance_tracker import PerformanceTracker

tracker = PerformanceTracker()

# Export to CSV
collection_summary = tracker.get_collection_performance_summary()
collection_summary.to_csv('collection_performance.csv', index=False)

model_trends = tracker.get_model_trends(days=30)
model_trends.to_csv('model_trends.csv', index=False)
```

## 🔧 Troubleshooting

### **Common Issues**

#### **Database Not Updated**
- **Web UI Tests**: Should auto-update (check completion message for 🗄️)
- **CLI Tests**: Requires manual ingestion
- **Error in logs**: Check `isee_web_demo.log` for ingestion errors

#### **Missing Collection Names**
```bash
# Check if collection was properly detected
python performance_tracker.py --summary

# Manually fix collection name
sqlite3 data/performance_tracking.db
UPDATE test_runs SET collection_name = 'Correct Name' WHERE run_id = 'run_YYYYMMDD_HHMMSS';
```

#### **Performance Issues Not Detected**
- Issues are automatically detected based on thresholds:
  - **Poor Quality**: Score < 0.3
  - **Slow Execution**: Time > 60 seconds  
  - **Short Responses**: Length < 100 characters
- Adjust thresholds in `performance_tracker.py` if needed

### **Database Maintenance**

#### **Backup Database**
```bash
cp data/performance_tracking.db data/performance_tracking_backup.db
```

#### **Reset Database**
```bash
rm data/performance_tracking.db
python performance_tracker.py --summary  # Recreates empty database
```

#### **Migrate Old Test Results**
```bash
# Ingest historical test results
for dir in data/output/run_*; do
    python performance_tracker.py --ingest "$dir" --collection "Historical"
done
```

## 📊 Interpreting Results

### **Performance Scores**

- **0.5+**: Excellent performance
- **0.4-0.5**: Good performance
- **0.3-0.4**: Acceptable performance  
- **Below 0.3**: Poor performance (flagged for replacement)

### **Execution Times**

- **0-20s**: Fast (good for interactive use)
- **20-40s**: Moderate (acceptable for research)
- **40-60s**: Slow (consider optimization)
- **60s+**: Very slow (flagged as issue)

### **Response Lengths**

- **5000+ chars**: Rich, detailed responses
- **1000-5000 chars**: Good depth
- **500-1000 chars**: Adequate
- **Below 500 chars**: Potentially insufficient (flagged if <100)

## 🚀 Future Enhancements

The performance tracking system is designed for extensibility:

### **Planned Features**
- **Cost tracking**: Actual API costs per model/test
- **Framework effectiveness**: Cognitive framework performance analysis
- **Query similarity**: Group similar queries for trend analysis
- **Automated alerts**: Email/Slack notifications for performance issues
- **Web dashboard**: Visual performance tracking in the Web UI
- **Predictive modeling**: Suggest optimal model combinations

### **Integration Opportunities**
- **CI/CD integration**: Automated performance regression testing
- **A/B testing**: Compare model configurations systematically
- **Production monitoring**: Track performance in live deployments
- **Research collaboration**: Share performance insights across teams

## 📚 Related Documentation

- [`CLAUDE.md`](../CLAUDE.md) - Main development guide
- [`llm_collections.json`](../llm_collections.json) - Collection definitions
- [`performance_tracker.py`](../performance_tracker.py) - Core tracking implementation
- [`performance_analysis.py`](../performance_analysis.py) - Analysis tools

---

## 🎯 Getting Started Checklist

- [ ] Run a test via Web UI and confirm auto-capture works
- [ ] Try `python performance_analysis.py --compare`
- [ ] Review any detected issues with `python performance_tracker.py --issues`
- [ ] Generate your first optimization report
- [ ] Set up regular performance monitoring routine

**The performance tracking system transforms your ISEE testing from isolated experiments into systematic research with institutional memory and data-driven optimization capabilities.**