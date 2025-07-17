# ISEE Meta-Framework Reporting Guide

*Last updated: July 17, 2025*

The ISEE Meta-Framework provides a comprehensive reporting system to generate detailed insights about your idea generation runs. This guide explains how to use the reporting features.

## Available Reports and Analyses

The reporting system supports the following:

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

4. **Analysis Report**: Data-driven insights including:
   - Performance comparisons across models, domains, and instructions
   - Scoring component analysis
   - Top performers identification
   - Specific recommendations

5. **Visualizations**: Charts illustrating key findings:
   - Model performance comparison
   - Domain effectiveness
   - Instruction framework performance
   - Scoring component analysis

## Generating Reports and Analysis

### Basic Reports

To generate basic reports, add the `--generate-reports` flag to your command:

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

### Analyzing Results with Visualizations

To perform detailed analysis with automatically generated visualizations:

```bash
python main.py --config unified_config.json --query "Your query" --generate-reports --export-csv --analyze-results
```

This will:
1. Generate standard reports
2. Export data as CSV files
3. Analyze the data to produce insights
4. Generate visualization charts
5. Create an analysis report with recommendations

If you want to skip generating visualizations (e.g., in an environment without a display):

```bash
python main.py --config unified_config.json --query "Your query" --generate-reports --export-csv --analyze-results --no-visualizations
```

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

## Analysis Report

The analysis report provides data-driven insights about your run, organized into:

### Summary Statistics
Overview of combinations generated, execution statistics, and average scores.

### Model Performance
Comparison of models used, showing which models performed best for your query.

### Domain Performance
Analysis of how different domains performed, identifying the most productive domain contexts.

### Instruction Framework Performance
Comparison of cognitive frameworks, showing which instruction approaches were most effective.

### Scoring Component Analysis
Breakdown of scoring components (novelty, feasibility, etc.) to identify strengths and weaknesses.

### Top Performers
List of the best-performing models, domains, instructions, and combinations.

### Recommendations
Specific, actionable recommendations based on the data analysis.

## Visualizations

The analysis system automatically generates visualizations to help understand the results:

1. **Model Comparison Chart**: Bar chart comparing average scores across models
2. **Domain Comparison Chart**: Visual comparison of domain performance
3. **Instruction Comparison Chart**: Effectiveness of different instruction frameworks
4. **Scoring Component Chart**: Analysis of score distribution across components

These visualizations are saved as PNG files in the output directory.

## Using CSV Data for Advanced Analysis

The CSV exports enable more advanced analysis in external tools:

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

## Technical Details

The reporting and analysis system is implemented in three modules:

1. **reporting.py**: Generates reports and CSV exports
2. **analysis.py**: Performs data analysis and creates visualizations
3. **main.py integration**: Connects the reporting system to the ISEE pipeline

The system follows a modular design that allows for easy extension with additional report types and analysis capabilities.