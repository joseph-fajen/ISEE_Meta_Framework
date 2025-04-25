# ISEE Meta-Framework Reporting Guide

The ISEE Meta-Framework provides a reporting system to generate detailed insights about your idea generation runs. This guide explains how to use the reporting features.

## Available Reports

The reporting system currently supports three types of reports:

1. **Run Summary Report**: A high-level overview of your run, including:
   - Run configuration details
   - Key statistics
   - Top synthesized ideas
   - Highest-scoring individual responses

2. **Combination Metadata Report**: Detailed information about each combination, including:
   - Model, instruction, and domain information
   - Response length
   - Evaluation scores

3. **CSV Data Exports**: Machine-readable data files for analysis in spreadsheet software:
   - `combinations.csv`: Detailed data for each combination generated
   - `ideas.csv`: Data about synthesized ideas and their sources
   - `model_performance.csv`: Aggregated statistics on model performance

## How to Generate Reports

To generate reports, add the `--generate-reports` flag to your command:

```bash
python main.py --config unified_config.json --query "Your query" --generate-reports
```

By default, reports are saved to the `data/output` directory in Markdown format.

### Report Format Options

You can choose the format for your text reports:

```bash
python main.py --config unified_config.json --query "Your query" --generate-reports --report-format markdown
```

Supported formats:
- `markdown`: Human-readable text format (default)
- `json`: Machine-readable data format

### Exporting Data as CSV

To export data as CSV files for analysis in spreadsheet software:

```bash
python main.py --config unified_config.json --query "Your query" --generate-reports --export-csv
```

This will generate CSV files that can be imported into Excel, Google Sheets, or data analysis tools.

### Custom Output Directory

You can specify a custom directory for saving reports:

```bash
python main.py --config unified_config.json --query "Your query" --generate-reports --output-directory reports/my_project
```

## CSV Data Export Details

### combinations.csv

Contains detailed information about each combination:

- `combination_id`: Unique identifier for the combination
- `model_id`: ID of the model used
- `model_name`: Human-readable name of the model
- `instruction_id`: ID of the instruction template used
- `domain_id`: ID of the domain used
- `query_id`: ID of the query used
- `executed`: Whether the combination was executed (True/False)
- `response_length`: Length of the response in characters
- `execution_time`: Time taken to execute the combination
- `overall_score`: Overall evaluation score
- Additional columns for individual evaluation criteria (novelty, feasibility, etc.)

### ideas.csv

Contains information about synthesized ideas:

- `idea_id`: Unique identifier for the idea
- `title`: Title of the idea
- `description`: Brief description of the idea
- `source_count`: Number of source combinations contributing to the idea
- `avg_score`: Average score of source combinations
- `contributing_models`: List of models that contributed to the idea
- `synthesis_method`: Method used to synthesize the idea

### model_performance.csv

Contains aggregated performance metrics for each model:

- `model_id`: ID of the model
- `model_name`: Human-readable name of the model
- `model_provider`: Provider of the model (OpenAI, Anthropic, etc.)
- `count`: Number of combinations executed with this model
- `avg_score`: Average score across all combinations
- `min_score`: Minimum score achieved
- `max_score`: Maximum score achieved
- `avg_response_length`: Average response length in characters
- `avg_execution_time`: Average execution time in seconds

## Report Samples

### Run Summary Report (Markdown)

The Run Summary Report includes:

```markdown
# ISEE Meta-Framework Run Summary

## Run Configuration
- **Query**: "How might we improve urban transportation in the next decade?"
- **Timestamp**: 2025-04-24 14:32:18
- **Sampling Method**: stratified
- **Max Combinations**: 36
- **Models Used**: 8
- **Instructions Used**: 10
- **Domains Used**: 3

## Run Statistics
- **Total Combinations**: 36
- **Executed Combinations**: 36
- **Average Response Length**: 3,842 characters
- **Min Score**: 0.347
- **Max Score**: 0.688
- **Average Score**: 0.512

## Top Synthesized Ideas
1. **Smart Infrastructure Integration** (Avg Score: 0.6425)
   - Primary Contributors: Claude 3 Opus (50%), GPT-4 Turbo (25%), Llama 3 8B (25%)
   - Key Points: Comprehensive approach to integrating smart technologies with existing infrastructure

2. **Sustainable Mobility Networks** (Avg Score: 0.587)
   - Primary Contributors: Claude 3.7 Sonnet (66.7%), Mixtral (33.3%)
   - Key Points: Focus on creating multi-modal, environmentally sustainable transportation options

## Top Individual Responses
1. **Claude 3 Opus with Systems Thinking Instruction** (Score: 0.688)
2. **GPT-4 Turbo with Integrative Framework** (Score: 0.654)
3. **Claude 3.7 Sonnet with Pragmatic Framework** (Score: 0.621)
```

### Combination Metadata Report (Markdown)

The Combination Metadata Report includes:

```markdown
# ISEE Meta-Framework Combination Metadata Report

This report provides metadata about all combinations generated and executed in this run.

## Combination Overview

- **Total Combinations**: 36
- **Executed Combinations**: 36
- **Evaluated Combinations**: 36

## Combination Details

| ID | Model | Instruction | Domain | Response Length | Score |
|---|---|---|---|---|---|
| model_claude_sonnet_ins_analytical_q_direct_domain_urban | Claude 3.7 Sonnet | Analytical | Urban | 4,231 | 0.587 |
| model_gpt4_ins_creative_q_constraint_domain_tech | GPT-4 Turbo | Creative | Tech | 3,876 | 0.612 |
| model_claude_opus_ins_critical_q_stakeholder_domain_policy | Claude 3 Opus | Critical | Policy | 5,102 | 0.598 |
```

## Using CSV Data for Analysis

The CSV exports are designed for analysis in spreadsheet software:

1. **Basic Analysis in Excel/Google Sheets**:
   - Sort and filter combinations by score
   - Create pivot tables to analyze model performance
   - Generate charts to visualize results

2. **Advanced Analysis with Python**:
   ```python
   import pandas as pd
   import matplotlib.pyplot as plt
   
   # Load the data
   combinations = pd.read_csv('combinations.csv')
   model_performance = pd.read_csv('model_performance.csv')
   
   # Compare model performance
   plt.figure(figsize=(10, 6))
   plt.bar(model_performance['model_name'], model_performance['avg_score'])
   plt.title('Average Score by Model')
   plt.xticks(rotation=45)
   plt.tight_layout()
   plt.savefig('model_comparison.png')
   ```

## Future Enhancements

The reporting system is in active development. Future versions may include:

1. Advanced response analysis with NLP
2. Visualization components directly in reports
3. Interactive web-based reports
4. Comparative analysis across multiple runs

## Technical Details

The reporting system is implemented in `reporting.py` and integrates with the main ISEE pipeline. Reports are generated after the complete pipeline execution and are saved alongside the main output file.

For developers: The reporting system follows a modular design that allows for easy extension with additional report types and formats. New report generators can be added by extending the `ReportingSystem` class.