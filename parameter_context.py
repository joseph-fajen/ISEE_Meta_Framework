"""
Parameter Context Module for ISEE Framework

This module provides comprehensive parameter context, relationships, examples, 
and impact tracking for the ISEE Command Wizard.

Part of the UX Enhancement Roadmap - Step 1.2: Parameter Context Improvements
"""

from typing import Dict, Any, List, Optional, Tuple, Union
import json
import os
from pathlib import Path

# Parameter Categories for organization and progressive disclosure
PARAMETER_CATEGORIES = {
    "basic": {
        "name": "Basic Parameters",
        "description": "Core parameters that define the essential aspects of your ISEE run",
        "parameters": ["query", "domain", "models", "instructions", "variations"]
    },
    "sampling": {
        "name": "Sampling Control",
        "description": "Parameters that control how combinations are selected and limited",
        "parameters": ["sampling_method", "max_combinations", "quick", "full"]
    },
    "models": {
        "name": "Model Selection",
        "description": "Parameters that control which models are used and how",
        "parameters": ["balanced_models", "use_ollama", "openrouter_filters", "simulate"]
    },
    "output": {
        "name": "Output Options",
        "description": "Parameters that control what is generated from the results",
        "parameters": ["output_format", "output_file", "generate_reports", "analyze_results", 
                      "report_format", "export_csv", "no_visualizations"]
    },
    "advanced": {
        "name": "Advanced Options",
        "description": "Parameters for fine-tuning and specialized use cases",
        "parameters": ["save_state", "load_state", "synthesize_method", "instruction_templates", 
                      "domain_config", "dry_run"]
    }
}

# Define the comprehensive parameter context database
PARAMETER_CONTEXT = {
    "query": {
        "short": "The text query to send to models",
        "long": "This is the primary input text that will be sent to all selected models. It should clearly describe the problem or request for which you want to evaluate model responses.",
        "impact": "The quality and specificity of your query directly affects the relevance of model responses.",
        "examples": [
            "How to improve urban mobility?", 
            "Design an eco-friendly packaging solution", 
            "Explain quantum computing to a 10-year-old"
        ],
        "detailed_examples": [
            {
                "value": "How to improve urban mobility?",
                "explanation": "A straightforward query that will generate a range of solution approaches across different domains like technology, urban planning, and policy."
            },
            {
                "value": "Generate 5 innovative solutions for sustainable urban transportation",
                "explanation": "A more specific query that constrains both the number of solutions (5) and the domain focus (sustainable transportation), which will produce more focused results."
            }
        ],
        "related": ["domain"],
        "cross_impacts": [
            {
                "parameter": "variations",
                "impact": "More variations will create slight rewording of your query, which helps test the robustness of model responses to different phrasings."
            },
            {
                "parameter": "models",
                "impact": "Different models may interpret your query differently, especially if it contains ambiguous terms."
            }
        ],
        "category": "basic",
        "required": True
    },
    "domain": {
        "short": "Problem domain to focus models on",
        "long": "Specifies the knowledge domain that models should consider when responding. This helps direct model responses toward a specific field or context.",
        "impact": "Choosing the right domain improves response relevance by providing appropriate context. Models can leverage domain-specific knowledge to generate better responses.",
        "examples": ["Technology", "Education", "Healthcare"],
        "detailed_examples": [
            {
                "value": "Technology Innovation",
                "explanation": "This domain will focus responses on technological solutions, emphasizing innovations, trends, and emerging technologies."
            },
            {
                "value": "Sustainable Development",
                "explanation": "This domain directs models to consider environmental sustainability, resource management, and long-term ecological impacts."
            }
        ],
        "related": ["query", "domain_config"],
        "cross_impacts": [
            {
                "parameter": "domain_config",
                "impact": "If you specify a custom domain configuration file, it will provide additional domain-specific context beyond the basic domain setting."
            }
        ],
        "category": "basic",
        "required": False
    },
    "models": {
        "short": "Number of different models to use",
        "long": "Determines how many different AI models will process your query. Using multiple models allows you to compare responses across different architectures and capabilities.",
        "impact": "More models provide greater diversity of responses but increase API costs and execution time. Each model adds a multiplier to your total combinations.",
        "examples": ["2", "3", "5"],
        "detailed_examples": [
            {
                "value": "1",
                "explanation": "The minimum setting - uses just one model. Fastest and cheapest option, but provides no comparative insights across different models."
            },
            {
                "value": "3",
                "explanation": "A balanced option that provides good model diversity while keeping combinations manageable. With 3 models, 3 instructions, and 2 variations, you'd have 18 combinations."
            }
        ],
        "related": ["balanced_models", "use_ollama", "simulate"],
        "cross_impacts": [
            {
                "parameter": "balanced_models",
                "impact": "When enabled, the system will select models from different providers to maximize cognitive diversity."
            },
            {
                "parameter": "variations",
                "impact": "The total number of combinations is models × instructions × variations. Increasing models will multiply your combinations by the number of instruction templates."
            },
            {
                "parameter": "instructions",
                "impact": "The total number of combinations is models × instructions × variations. Increasing models will multiply your combinations by the number of instructions."
            }
        ],
        "category": "basic",
        "required": False,
        "warning_threshold": 5,
        "warning_message": "Using a high number of models will significantly increase both API costs and execution time. Consider using 2-3 models for most use cases."
    },
    "instructions": {
        "short": "Number of different instruction prompts to use",
        "long": "Determines how many different instruction templates will be used to frame your query. Different instruction templates encourage different response styles and perspectives.",
        "impact": "More instruction templates lead to greater cognitive diversity in responses but increase the total number of combinations and execution time.",
        "examples": ["3", "5", "10"],
        "detailed_examples": [
            {
                "value": "2",
                "explanation": "A minimal setting that provides some cognitive diversity while keeping combinations low. With 2 models, 2 instructions, and 2 variations, you'd have 8 combinations."
            },
            {
                "value": "5",
                "explanation": "A higher setting that explores more cognitive approaches. With 2 models, 5 instructions, and 2 variations, you'd have 20 combinations, providing a good exploration of the possibility space."
            }
        ],
        "related": ["instruction_templates", "variations"],
        "cross_impacts": [
            {
                "parameter": "instruction_templates",
                "impact": "If you specify explicit instruction templates, the instructions count is ignored in favor of your specific selections."
            },
            {
                "parameter": "variations",
                "impact": "The total number of combinations is models × instructions × variations. Increasing instructions will multiply your combinations by the number of variations."
            },
            {
                "parameter": "models",
                "impact": "The total number of combinations is models × instructions × variations. Increasing instructions will multiply your combinations by the number of models."
            }
        ],
        "category": "basic",
        "required": False,
        "warning_threshold": 10,
        "warning_message": "Using a high number of instruction templates will significantly increase the total number of combinations. Consider using 3-5 templates for most use cases."
    },
    "variations": {
        "short": "Number of query variations to generate",
        "long": "Creates multiple variations of your base query to test how slight wording changes affect model responses. Helps identify response sensitivity to query phrasing.",
        "impact": "More variations increase the robustness of your evaluation but multiply the total number of combinations, increasing costs and execution time.",
        "examples": ["2", "3", "5"],
        "detailed_examples": [
            {
                "value": "1",
                "explanation": "No variations - only the exact query you provided will be used. This minimizes combinations but doesn't test for response sensitivity to wording."
            },
            {
                "value": "3",
                "explanation": "Creates three slightly different phrasings of your query. With 2 models and 3 instructions, this would yield 18 combinations, providing good robustness testing."
            }
        ],
        "related": ["instructions", "models"],
        "cross_impacts": [
            {
                "parameter": "models",
                "impact": "The total number of combinations is models × instructions × variations. Increasing variations will multiply your combinations by the number of models."
            },
            {
                "parameter": "instructions",
                "impact": "The total number of combinations is models × instructions × variations. Increasing variations will multiply your combinations by the number of instructions."
            }
        ],
        "category": "basic",
        "required": False,
        "warning_threshold": 4,
        "warning_message": "Using more than 3 variations multiplies combinations significantly. For most cases, 2-3 variations provide sufficient robustness testing."
    },
    "max_combinations": {
        "short": "Maximum number of combinations to execute",
        "long": "Limits the total number of query-model-instruction combinations that will be executed. Helps control execution time and API costs.",
        "impact": "Lower values reduce cost and time but might not provide a representative sample of all possible combinations.",
        "examples": ["36", "50", "100"],
        "detailed_examples": [
            {
                "value": "36",
                "explanation": "A balanced setting that provides good coverage without excessive costs. Often used with stratified sampling to ensure representative distribution."
            },
            {
                "value": "12",
                "explanation": "A lower setting focused on efficiency. Useful for quick explorations or when using expensive models. Best paired with stratified sampling."
            }
        ],
        "related": ["sampling_method", "quick", "full"],
        "cross_impacts": [
            {
                "parameter": "sampling_method",
                "impact": "When using 'exhaustive' sampling, max_combinations has no effect. With 'random' or 'stratified' sampling, it limits the total combinations executed."
            },
            {
                "parameter": "quick",
                "impact": "The 'quick' preset automatically sets max_combinations to 36 with stratified sampling."
            },
            {
                "parameter": "full",
                "impact": "The 'full' preset ignores max_combinations and runs all possible combinations."
            }
        ],
        "category": "sampling",
        "required": False
    },
    "sampling_method": {
        "short": "Method for sampling combinations",
        "long": "Determines how combinations are selected when not running exhaustively. Options are 'exhaustive' (all combinations), 'stratified' (balanced representation), or 'random' (random selection).",
        "impact": "Stratified sampling provides good coverage with fewer combinations. Random sampling is faster but less systematic.",
        "examples": ["exhaustive", "stratified", "random"],
        "detailed_examples": [
            {
                "value": "exhaustive",
                "explanation": "Runs every possible combination. This is the most thorough approach but can be expensive and time-consuming for large combination spaces."
            },
            {
                "value": "stratified",
                "explanation": "Selects a representative subset of combinations, ensuring balance across models, instructions, and variations. This provides good coverage with fewer combinations."
            },
            {
                "value": "random",
                "explanation": "Randomly selects combinations up to the max_combinations limit. Faster but may not provide balanced representation across parameters."
            }
        ],
        "related": ["max_combinations", "quick", "full"],
        "cross_impacts": [
            {
                "parameter": "max_combinations",
                "impact": "When using 'random' or 'stratified' sampling, max_combinations determines how many combinations are executed."
            },
            {
                "parameter": "models",
                "impact": "With stratified sampling, increasing models may require more combinations to maintain representative coverage."
            },
            {
                "parameter": "instructions",
                "impact": "With stratified sampling, increasing instructions may require more combinations to maintain representative coverage."
            }
        ],
        "category": "sampling",
        "required": False
    },
    "use_ollama": {
        "short": "Include Ollama local models",
        "long": "When enabled, includes locally-running Ollama models in the evaluation. Requires Ollama to be installed and running on your system.",
        "impact": "Allows comparison between cloud API models and open-source models running locally, but requires Ollama setup.",
        "examples": ["True", "False"],
        "detailed_examples": [
            {
                "value": "True",
                "explanation": "Includes Ollama models in your evaluation, allowing comparison between cloud API models and locally-running open source models. Requires Ollama to be installed and running."
            },
            {
                "value": "False",
                "explanation": "Only uses cloud API models (OpenAI, Anthropic, etc.). This is simpler but doesn't provide comparison with open-source models."
            }
        ],
        "related": ["models", "balanced_models"],
        "cross_impacts": [
            {
                "parameter": "balanced_models",
                "impact": "When both enabled, ensures representation from both cloud API models and Ollama models."
            },
            {
                "parameter": "models",
                "impact": "When enabled, increases the pool of available models to include Ollama models."
            }
        ],
        "category": "models",
        "required": False
    },
    "balanced_models": {
        "short": "Balance models across providers",
        "long": "Ensures that model combinations are evenly distributed across different providers (OpenAI, Anthropic, etc.). Helps prevent bias toward any single provider.",
        "impact": "Provides more balanced results but may limit flexibility in model selection.",
        "examples": ["True", "False"],
        "detailed_examples": [
            {
                "value": "True",
                "explanation": "When enabled, the system will select models from different providers to maximize cognitive diversity. For example, with 3 models, it might select one from OpenAI, one from Anthropic, and one from Google."
            },
            {
                "value": "False",
                "explanation": "Models are selected based on detection order, which may result in multiple models from the same provider."
            }
        ],
        "related": ["models", "use_ollama"],
        "cross_impacts": [
            {
                "parameter": "use_ollama",
                "impact": "When both enabled, ensures representation from both cloud API models and Ollama models."
            },
            {
                "parameter": "models",
                "impact": "With balanced_models enabled, the system attempts to select models from different providers up to the models count."
            }
        ],
        "category": "models",
        "required": False
    },
    "openrouter_filters": {
        "short": "Filter OpenRouter models by criteria",
        "long": "Configure filters to select specific types of models from the 300+ available OpenRouter models. Filter by provider (Anthropic, OpenAI, Google, etc.), capabilities (reasoning, coding, fast, etc.), or cost tiers (free, budget, premium, etc.).",
        "impact": "Helps narrow down the vast selection of OpenRouter models to those that match your specific requirements for cost, capabilities, or provider preferences.",
        "examples": ["provider filters", "capability filters", "cost tier filters"],
        "detailed_examples": [
            {
                "value": "Provider filtering",
                "explanation": "Select models only from specific providers like Anthropic, OpenAI, or Google to compare performance across preferred providers."
            },
            {
                "value": "Capability filtering", 
                "explanation": "Filter models by capabilities such as reasoning, coding, or large context windows to match your specific task requirements."
            },
            {
                "value": "Cost tier filtering",
                "explanation": "Limit selection to specific cost tiers (free, budget, premium) to control API costs while maintaining quality."
            }
        ],
        "related": ["models", "balanced_models"],
        "cross_impacts": [
            {
                "parameter": "models",
                "impact": "The filtered OpenRouter models will be included in the total model count selection."
            },
            {
                "parameter": "balanced_models",
                "impact": "When enabled with OpenRouter filters, ensures diversity across both filtered OpenRouter models and other providers."
            }
        ],
        "category": "models",
        "required": False
    },
    "output_format": {
        "short": "Format for result output",
        "long": "Determines the format of the output files generated by the ISEE framework. Markdown is human-readable, while JSON is better for programmatic processing.",
        "impact": "Choose markdown for readability or JSON for further automated processing.",
        "examples": ["markdown", "json", "text"],
        "detailed_examples": [
            {
                "value": "markdown",
                "explanation": "Creates human-readable Markdown files with formatted text, headings, and lists. Best for direct reading and sharing of results."
            },
            {
                "value": "json",
                "explanation": "Outputs structured JSON data that can be easily parsed and processed by other applications. Best for programmatic use of results."
            },
            {
                "value": "text",
                "explanation": "Simple plain text output without formatting. Most basic option but less readable for complex results."
            }
        ],
        "related": ["output_file", "generate_reports"],
        "cross_impacts": [
            {
                "parameter": "generate_reports",
                "impact": "When reports are generated, they will use this format unless report_format is specified separately."
            }
        ],
        "category": "output",
        "required": False
    },
    "output_file": {
        "short": "Path to save output results",
        "long": "Specifies where the output file will be saved. If not provided, a default path in the data/output directory will be used.",
        "impact": "Allows organizing outputs in specific locations for easier management.",
        "examples": ["results.md", "output/my_evaluation.json"],
        "detailed_examples": [
            {
                "value": "results.md",
                "explanation": "Saves results to a file named 'results.md' in the current directory. The file extension should match your chosen output_format."
            },
            {
                "value": "data/output/project_name/results.json",
                "explanation": "Saves results to a specific subdirectory structure, which is useful for organizing multiple evaluations."
            }
        ],
        "related": ["output_format"],
        "cross_impacts": [],
        "category": "output",
        "required": False
    },
    "simulate": {
        "short": "Simulate responses without API calls",
        "long": "Runs the evaluation with simulated model responses instead of making actual API calls. Useful for testing workflow or when API keys are not available.",
        "impact": "Eliminates API costs but provides only placeholder responses for testing purposes.",
        "examples": ["True", "False"],
        "detailed_examples": [
            {
                "value": "True",
                "explanation": "No actual API calls will be made. The system will generate placeholder responses for testing the workflow without incurring costs."
            },
            {
                "value": "False",
                "explanation": "Normal operation - makes real API calls to the selected models, incurring costs based on usage."
            }
        ],
        "related": ["dry_run"],
        "cross_impacts": [
            {
                "parameter": "dry_run",
                "impact": "Both simulate and dry_run prevent actual API calls, but dry_run doesn't generate any responses at all."
            }
        ],
        "category": "models",
        "required": False
    },
    "dry_run": {
        "short": "Show what would run without executing",
        "long": "Shows which combinations would be executed without actually running them. Useful for validating your configuration before committing to a full run.",
        "impact": "Allows validation of settings without spending time or API credits.",
        "examples": ["True", "False"],
        "detailed_examples": [
            {
                "value": "True",
                "explanation": "The system will show you exactly which combinations would be executed, but won't make any API calls or generate responses. Useful for previewing what will happen."
            },
            {
                "value": "False",
                "explanation": "Normal operation - executes the selected combinations."
            }
        ],
        "related": ["simulate"],
        "cross_impacts": [
            {
                "parameter": "simulate",
                "impact": "Both simulate and dry_run prevent actual API calls, but simulate still generates placeholder responses."
            }
        ],
        "category": "advanced",
        "required": False
    },
    "generate_reports": {
        "short": "Generate summary reports",
        "long": "Creates detailed summary reports of the evaluation results, including model comparisons, statistical analyses, and key findings.",
        "impact": "Provides valuable insights but adds processing time at the end of execution.",
        "examples": ["True", "False"],
        "detailed_examples": [
            {
                "value": "True",
                "explanation": "After completing all model runs, the system will analyze the results and generate summary reports with comparisons and insights."
            },
            {
                "value": "False",
                "explanation": "Only raw model responses will be saved, without additional analysis or aggregation."
            }
        ],
        "related": ["analyze_results", "report_format", "export_csv"],
        "cross_impacts": [
            {
                "parameter": "analyze_results",
                "impact": "analyze_results requires generate_reports to be enabled. If generate_reports is False, analyze_results will have no effect."
            },
            {
                "parameter": "report_format",
                "impact": "The report_format parameter only applies when generate_reports is enabled."
            },
            {
                "parameter": "export_csv",
                "impact": "The export_csv parameter only applies when generate_reports is enabled."
            }
        ],
        "category": "output",
        "required": False
    },
    "analyze_results": {
        "short": "Analyze results with visualizations",
        "long": "Performs in-depth analysis of results and generates visualizations like charts and graphs. Requires generate_reports to be enabled.",
        "impact": "Helps identify patterns and insights but adds significant processing time.",
        "examples": ["True", "False"],
        "detailed_examples": [
            {
                "value": "True",
                "explanation": "In addition to summary reports, the system will generate visualizations and charts to help identify patterns and insights in the results."
            },
            {
                "value": "False",
                "explanation": "Summary reports will be text-only, without visualizations."
            }
        ],
        "related": ["generate_reports", "no_visualizations"],
        "cross_impacts": [
            {
                "parameter": "generate_reports",
                "impact": "analyze_results requires generate_reports to be enabled. If generate_reports is False, analyze_results will have no effect."
            },
            {
                "parameter": "no_visualizations",
                "impact": "If no_visualizations is True, it will override analyze_results and prevent chart generation."
            }
        ],
        "category": "output",
        "required": False,
        "dependencies": [
            {
                "parameter": "generate_reports",
                "required_value": True,
                "message": "analyze_results requires generate_reports to be enabled"
            }
        ]
    },
    "save_state": {
        "short": "Save state to a file",
        "long": "Saves the current state of the evaluation to a file that can be loaded later. Useful for long-running evaluations that might need to be paused.",
        "impact": "Enables resuming interrupted runs but adds overhead for state management.",
        "examples": ["my_evaluation_state.json"],
        "detailed_examples": [
            {
                "value": "state/project_evaluation.json",
                "explanation": "Saves the complete state of the evaluation to this file, including all configurations, completed combinations, and partial results."
            }
        ],
        "related": ["load_state"],
        "cross_impacts": [],
        "category": "advanced",
        "required": False
    },
    "load_state": {
        "short": "Load state from a file",
        "long": "Loads a previously saved state to continue an evaluation. Useful for resuming interrupted runs or building upon previous results.",
        "impact": "Allows continuing previous runs without starting over.",
        "examples": ["my_evaluation_state.json"],
        "detailed_examples": [
            {
                "value": "state/project_evaluation.json",
                "explanation": "Loads a previously saved state file, restoring all configurations and allowing you to continue where you left off."
            }
        ],
        "related": ["save_state"],
        "cross_impacts": [],
        "category": "advanced",
        "required": False
    },
    "synthesize_method": {
        "short": "Method for synthesizing results",
        "long": "Determines how model responses are combined and synthesized into final insights. 'cluster_based' groups similar responses, while 'cross_pollination' combines elements from different responses.",
        "impact": "Different methods produce different types of synthesized insights.",
        "examples": ["cluster_based", "cross_pollination"],
        "detailed_examples": [
            {
                "value": "cluster_based",
                "explanation": "Groups similar responses together and identifies common themes and insights within each cluster. Best for identifying consensus and divergence in responses."
            },
            {
                "value": "cross_pollination",
                "explanation": "Combines elements from different responses to create novel insights that aren't present in any single response. More creative but may be less coherent."
            }
        ],
        "related": ["analyze_results", "generate_reports"],
        "cross_impacts": [],
        "category": "advanced",
        "required": False
    },
    "quick": {
        "short": "Run in quick mode with stratified sampling",
        "long": "Preset that runs with stratified sampling and 36 combinations for a quicker evaluation. Good balance between thoroughness and speed.",
        "impact": "Significantly reduces execution time while maintaining reasonable coverage.",
        "examples": ["True", "False"],
        "detailed_examples": [
            {
                "value": "True",
                "explanation": "Automatically configures stratified sampling with 36 combinations. This provides a good balance of coverage and efficiency for most evaluations."
            }
        ],
        "related": ["full", "sampling_method", "max_combinations"],
        "cross_impacts": [
            {
                "parameter": "full",
                "impact": "The quick and full parameters are mutually exclusive. If both are set, full takes precedence."
            },
            {
                "parameter": "sampling_method",
                "impact": "Setting quick=True automatically sets sampling_method to 'stratified' regardless of what was specified."
            },
            {
                "parameter": "max_combinations",
                "impact": "Setting quick=True automatically sets max_combinations to 36 regardless of what was specified."
            }
        ],
        "category": "sampling",
        "required": False
    },
    "full": {
        "short": "Run in full mode with exhaustive combinations",
        "long": "Preset that runs all possible combinations for the most thorough evaluation. May take significant time and API credits.",
        "impact": "Provides the most comprehensive results but maximizes execution time and costs.",
        "examples": ["True", "False"],
        "detailed_examples": [
            {
                "value": "True",
                "explanation": "Automatically configures exhaustive sampling with no combination limit. This provides the most thorough coverage but may be expensive and time-consuming for large parameter values."
            }
        ],
        "related": ["quick", "sampling_method", "max_combinations"],
        "cross_impacts": [
            {
                "parameter": "quick",
                "impact": "The quick and full parameters are mutually exclusive. If both are set, full takes precedence."
            },
            {
                "parameter": "sampling_method",
                "impact": "Setting full=True automatically sets sampling_method to 'exhaustive' regardless of what was specified."
            },
            {
                "parameter": "max_combinations",
                "impact": "Setting full=True effectively ignores any max_combinations setting, as all possible combinations will be executed."
            }
        ],
        "category": "sampling",
        "required": False,
        "warning_threshold": True,
        "warning_message": "Full mode runs all possible combinations without limits. This can be expensive and time-consuming when using many models, instructions, or variations."
    },
    "instruction_templates": {
        "short": "Specific instruction templates to use",
        "long": "Instead of randomly selecting templates, this allows specifying exactly which templates to use by their ID. Provides precise control over the instruction diversity.",
        "impact": "Allows targeted evaluation with specific instruction styles.",
        "examples": ["creative_thinking,critical_analysis,empathetic_response"],
        "detailed_examples": [
            {
                "value": "creative_thinking,critical_analysis",
                "explanation": "Uses only these two specific instruction templates. This overrides the 'instructions' count parameter and provides precise control over which cognitive approaches are used."
            },
            {
                "value": "first_principles,steelman,opposing_perspectives",
                "explanation": "Selects three templates focused on analytical and critical thinking approaches, providing targeted cognitive diversity."
            }
        ],
        "related": ["instructions"],
        "cross_impacts": [
            {
                "parameter": "instructions",
                "impact": "When instruction_templates is specified, it overrides the instructions count parameter."
            }
        ],
        "category": "advanced",
        "required": False
    },
    "report_format": {
        "short": "Format for generated reports",
        "long": "Specifies the format for summary reports. Only applies when generate_reports is enabled.",
        "impact": "Choose markdown for human readability or JSON for programmatic analysis.",
        "examples": ["markdown", "json"],
        "detailed_examples": [
            {
                "value": "markdown",
                "explanation": "Generates reports in Markdown format, which is easy to read and share. Best for human consumption."
            },
            {
                "value": "json",
                "explanation": "Generates reports in JSON format, which is structured for machine processing. Best for further programmatic analysis."
            }
        ],
        "related": ["generate_reports", "export_csv"],
        "cross_impacts": [],
        "category": "output",
        "required": False,
        "dependencies": [
            {
                "parameter": "generate_reports",
                "required_value": True,
                "message": "report_format only applies when generate_reports is enabled"
            }
        ]
    },
    "export_csv": {
        "short": "Export data as CSV for analysis",
        "long": "Exports evaluation data in CSV format for further analysis in spreadsheet software or data analysis tools. Only applies when generate_reports is enabled.",
        "impact": "Facilitates deeper custom analysis in external tools.",
        "examples": ["True", "False"],
        "detailed_examples": [
            {
                "value": "True",
                "explanation": "In addition to regular reports, the system will export structured data in CSV format for use in tools like Excel, Google Sheets, or R."
            }
        ],
        "related": ["generate_reports", "analyze_results"],
        "cross_impacts": [],
        "category": "output",
        "required": False,
        "dependencies": [
            {
                "parameter": "generate_reports",
                "required_value": True,
                "message": "export_csv only applies when generate_reports is enabled"
            }
        ]
    },
    "no_visualizations": {
        "short": "Skip generating visualization charts",
        "long": "Disables the generation of visualization charts during analysis. Only applies when analyze_results is enabled.",
        "impact": "Speeds up analysis but loses visual insights from charts and graphs.",
        "examples": ["True", "False"],
        "detailed_examples": [
            {
                "value": "True",
                "explanation": "Prevents the generation of charts and graphs during analysis, which can speed up processing and reduce complexity in the output."
            }
        ],
        "related": ["analyze_results"],
        "cross_impacts": [
            {
                "parameter": "analyze_results",
                "impact": "no_visualizations only has an effect when analyze_results is enabled."
            }
        ],
        "category": "output",
        "required": False,
        "dependencies": [
            {
                "parameter": "analyze_results",
                "required_value": True,
                "message": "no_visualizations only applies when analyze_results is enabled"
            }
        ]
    },
    "domain_config": {
        "short": "Domain-specific configuration file",
        "long": "Path to a configuration file containing domain-specific settings for the evaluation.",
        "impact": "Allows tailoring the evaluation to specific domains with specialized settings.",
        "examples": ["tech_writing_domains.json", "learning_design_domains.json"],
        "detailed_examples": [
            {
                "value": "tech_writing_domains.json",
                "explanation": "Loads specialized domains and settings for technical writing evaluations, including specialized instruction templates and evaluation criteria."
            },
            {
                "value": "learning_design_domains.json",
                "explanation": "Loads specialized domains for educational and learning design contexts, providing relevant templates and evaluation approaches."
            }
        ],
        "related": ["domain"],
        "cross_impacts": [],
        "category": "advanced",
        "required": False
    }
}


class ParameterContext:
    """Provides comprehensive parameter context, examples, and relationship tracking."""
    
    def __init__(self):
        """Initialize the parameter context manager."""
        self.context_db = PARAMETER_CONTEXT
        self.categories = PARAMETER_CATEGORIES
    
    def get_parameter_context(self, param_name: str) -> Dict[str, Any]:
        """Get the full context for a specific parameter.
        
        Args:
            param_name: The parameter name (with underscores, not dashes)
            
        Returns:
            Dictionary with the parameter context or empty dict if not found
        """
        # Clean up parameter name (replace dashes with underscores)
        clean_param = param_name.replace("-", "_")
        
        if clean_param in self.context_db:
            return self.context_db[clean_param]
        
        return {}
    
    def get_parameter_examples(self, param_name: str) -> List[str]:
        """Get the list of examples for a parameter.
        
        Args:
            param_name: The parameter name (with underscores, not dashes)
            
        Returns:
            List of example strings
        """
        context = self.get_parameter_context(param_name)
        return context.get("examples", [])
    
    def get_detailed_example(self, param_name: str, index: int = 0) -> Dict[str, str]:
        """Get a detailed example with explanation for a parameter.
        
        Args:
            param_name: The parameter name (with underscores, not dashes)
            index: The index of the example to retrieve (defaults to the first one)
            
        Returns:
            Dictionary with example value and explanation, or empty dict if not found
        """
        context = self.get_parameter_context(param_name)
        detailed_examples = context.get("detailed_examples", [])
        
        if not detailed_examples or index >= len(detailed_examples):
            return {}
        
        return detailed_examples[index]
    
    def get_cross_parameter_impacts(self, param_name: str) -> List[Dict[str, str]]:
        """Get the cross-parameter impacts for a parameter.
        
        Args:
            param_name: The parameter name (with underscores, not dashes)
            
        Returns:
            List of impact dictionaries with parameter and impact description
        """
        context = self.get_parameter_context(param_name)
        return context.get("cross_impacts", [])
    
    def get_related_parameters(self, param_name: str) -> List[str]:
        """Get the list of related parameters.
        
        Args:
            param_name: The parameter name (with underscores, not dashes)
            
        Returns:
            List of related parameter names
        """
        context = self.get_parameter_context(param_name)
        return context.get("related", [])
    
    def get_parameter_warning(self, param_name: str, value: Any) -> Optional[str]:
        """Get a warning message for a parameter value if applicable.
        
        Args:
            param_name: The parameter name (with underscores, not dashes)
            value: The value to check against thresholds
            
        Returns:
            Warning message or None if no warning
        """
        context = self.get_parameter_context(param_name)
        
        # Check if there's a warning threshold
        if "warning_threshold" not in context:
            return None
        
        threshold = context["warning_threshold"]
        warning = context.get("warning_message")
        
        # Boolean threshold (warn if True)
        if isinstance(threshold, bool) and threshold and value:
            return warning
        
        # Numeric threshold (warn if value >= threshold)
        if isinstance(threshold, (int, float)) and isinstance(value, (int, float)):
            if value >= threshold:
                return warning
        
        return None
    
    def check_parameter_dependencies(self, param_name: str, all_params: Dict[str, Any]) -> List[str]:
        """Check if dependencies for a parameter are satisfied.
        
        Args:
            param_name: The parameter name (with underscores, not dashes)
            all_params: Dictionary of all parameter values
            
        Returns:
            List of dependency warning messages, empty if all dependencies are satisfied
        """
        context = self.get_parameter_context(param_name)
        dependencies = context.get("dependencies", [])
        
        if not dependencies:
            return []
        
        warnings = []
        for dep in dependencies:
            required_param = dep.get("parameter")
            required_value = dep.get("required_value")
            message = dep.get("message", f"Requires {required_param}={required_value}")
            
            # Skip if the dependent parameter isn't set or has a falsy value
            if not all_params.get(param_name):
                continue
                
            # Check if the dependency is satisfied
            if required_param not in all_params or all_params[required_param] != required_value:
                warnings.append(message)
        
        return warnings
    
    def get_all_parameter_names(self) -> List[str]:
        """Get a list of all parameter names.
        
        Returns:
            List of all parameter names
        """
        return list(self.context_db.keys())
    
    def get_parameters_by_category(self, category_name: str) -> List[str]:
        """Get a list of parameters in a specific category.
        
        Args:
            category_name: The category name
            
        Returns:
            List of parameter names in that category
        """
        if category_name not in self.categories:
            return []
        
        return self.categories[category_name].get("parameters", [])
    
    def get_all_categories(self) -> List[Dict[str, Any]]:
        """Get a list of all categories with their metadata.
        
        Returns:
            List of category dictionaries
        """
        result = []
        for cat_id, cat_info in self.categories.items():
            result.append({
                "id": cat_id,
                "name": cat_info.get("name", cat_id),
                "description": cat_info.get("description", ""),
                "parameters": cat_info.get("parameters", [])
            })
        return result
    
    def calculate_combinations(self, params: Dict[str, Any]) -> int:
        """Calculate the total number of combinations based on parameter values.
        
        Args:
            params: Dictionary of parameter values
            
        Returns:
            Total number of combinations
        """
        # Extract key parameters
        models_count = params.get("models", 2)
        
        # If instruction_templates is specified, it overrides instructions count
        if params.get("instruction_templates"):
            templates = params["instruction_templates"].split(",")
            instructions_count = len(templates)
        else:
            instructions_count = params.get("instructions", 3)
            
        variations_count = params.get("variations", 2)
        max_combinations = params.get("max_combinations")
        
        # Calculate the total possible combinations
        total_combinations = models_count * instructions_count * variations_count
        
        # Check for quick/full presets
        if params.get("full", False):
            return total_combinations
            
        if params.get("quick", False):
            return min(total_combinations, 36)
        
        # If max_combinations is set, use that as the limit
        if max_combinations is not None and max_combinations > 0:
            return min(total_combinations, max_combinations)
        
        # For 'exhaustive' sampling, use all combinations
        # For other sampling methods, limit if needed
        if params.get("sampling_method") == "exhaustive":
            return total_combinations
        else:
            # Default to 50 combinations for random/stratified sampling if not specified
            default_max = 50
            return min(total_combinations, max_combinations or default_max)
    
    def get_combination_impact(self, params: Dict[str, Any]) -> str:
        """Get a description of the impact of the current combination count.
        
        Args:
            params: Dictionary of parameter values
            
        Returns:
            Impact description string
        """
        combinations = self.calculate_combinations(params)
        
        if combinations <= 8:
            return f"{combinations} combinations - Very quick execution with minimal cost"
        elif combinations <= 24:
            return f"{combinations} combinations - Quick execution with moderate cost"
        elif combinations <= 48:
            return f"{combinations} combinations - Moderate execution time and cost"
        elif combinations <= 100:
            return f"{combinations} combinations - Longer execution time with higher cost"
        else:
            return f"{combinations} combinations - Extended execution time with significant cost"