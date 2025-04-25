# ISEE Meta-Framework Reporting Guide

The ISEE Meta-Framework provides a reporting system to generate detailed insights about your idea generation runs. This guide explains how to use the reporting features.

## Available Reports

The reporting system currently supports two basic report types:

1. **Run Summary Report**: A high-level overview of your run, including:
   - Run configuration details
   - Key statistics
   - Top synthesized ideas
   - Highest-scoring individual responses

2. **Combination Metadata Report**: Detailed information about each combination, including:
   - Model, instruction, and domain information
   - Response length
   - Evaluation scores

## How to Generate Reports

To generate reports, add the `--generate-reports` flag to your command:

```bash
python main.py --config unified_config.json --query "Your query" --generate-reports
```

By default, reports are saved to the `data/output` directory in Markdown format.

### Report Format Options

You can choose the format for your reports:

```bash
python main.py --config unified_config.json --query "Your query" --generate-reports --report-format markdown
```

Supported formats:
- `markdown`: Human-readable text format (default)
- `json`: Machine-readable data format

### Custom Output Directory

You can specify a custom directory for saving reports:

```bash
python main.py --config unified_config.json --query "Your query" --generate-reports --output-directory reports/my_project
```

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

## Future Enhancements

The reporting system is in active development. Future versions will include:

1. Advanced response analysis with NLP
2. Performance analytics reports
3. Synthesis process analysis
4. CSV data exports for external analysis
5. Visualization components

## Technical Details

The reporting system is implemented in `reporting.py` and integrates with the main ISEE pipeline. Reports are generated after the complete pipeline execution and are saved alongside the main output file.

For developers: The reporting system follows a modular design that allows for easy extension with additional report types and formats. New report generators can be added by extending the `ReportingSystem` class.