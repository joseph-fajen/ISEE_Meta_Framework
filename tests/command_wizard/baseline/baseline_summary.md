# Command Wizard Baseline Metrics Summary

## API Detection

### no_apis

- Any API detected: False
- Simulation forced: True

### anthropic_only

- Any API detected: True
- Simulation forced: False

### all_apis

- Any API detected: True
- Simulation forced: False

### ollama_only

- Any API detected: False
- Simulation forced: False

## Domain Loading

- Total domains: 15
- Domain names: Urban Planning, Education, Healthcare, Sustainability, Technology Innovation, Technical Documentation, Knowledge Management, Content Strategy, AI-Assisted Writing, Developer Documentation, Instructional Design, E-learning Design, Learning Experience Design, Corporate Training, Assessment Design

## Template Selection

- Total templates: 10
- Template names: Analytical Framework, Creative Framework, Critical Framework, Integrative Framework, Pragmatic Framework, First Principles Framework, Systems Thinking Framework, Contrarian Framework, Historical Framework, Future-Oriented Framework
- Specific template support: False

## Command Construction

### minimal

- Command: `python main.py --config unified_config.json --query "How might we improve urban transportation?" --models 2 --instructions 3 --variations 2 --sampling-method exhaustive --output-format markdown`
- Parameter count: 19

### complex

- Command: `python main.py --config unified_config.json --query "How might we improve user's experience with "smart home" devices?" --domain "technology" --models 3 --use-ollama --balanced-models --instructions 4 --variations 3 --max-combinations 36 --sampling-method stratified --synthesize-method cross_pollination --output-format json --output-file "results.json" --generate-reports --analyze-results --simulate --save-state "test_state.json"`
- Parameter count: 38

## Command Validation

### default

- Valid: True
- Message: Command is valid

## Parameter Mapping

- Total wizard parameters: 18
- Total main.py parameters: 28
- Match percentage: 27.8%

### Missing in main.py


### Missing in wizard

- config (text)
- domain_config (text)
- output_directory (text)
- report_format (text)
- export_csv (text)
- no_visualizations (text)
- quick (text)
- full (text)
- list_domains (text)
- help (text)

### Type mismatches

- models: Wizard integer vs Main text
- use_ollama: Wizard boolean vs Main text
- balanced_models: Wizard boolean vs Main text
- instructions: Wizard integer vs Main text
- variations: Wizard integer vs Main text
- max_combinations: Wizard integer vs Main text
- sampling_method: Wizard choice vs Main text
- synthesize_method: Wizard choice vs Main text
- output_format: Wizard choice vs Main text
- generate_reports: Wizard boolean vs Main text
- analyze_results: Wizard boolean vs Main text
- simulate: Wizard boolean vs Main text
- dry_run: Wizard boolean vs Main text

## Compatibility

- Command: `python main.py --config unified_config.json --query "How might we improve urban transportation?" --models 2 --instructions 3 --variations 2 --sampling-method exhaustive --output-format markdown --simulate --dry-run`
- Valid: True
- Message: Command is valid
