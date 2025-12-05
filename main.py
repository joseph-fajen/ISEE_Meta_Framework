"""
Main CLI Entry Point for ISEE Framework

This module provides a command-line interface to interact with the
Idea Synthesis and Extraction Engine framework.

The core engine logic has been extracted to isee_engine.py for direct
import by web applications (Phase 3 of refactoring).
"""

import os
import json
import argparse
import sys
from datetime import datetime

# Import core engine from extracted module
from isee_engine import (
    ISEEApplication,
    ISEEGuardrails,
    ExecutionParams,
    get_week_of_month,
    normalize_framework_name,
    normalize_model_display_name,
)

# Import supporting modules
from domain_manager import DomainManager, Domain
from query_generator import Query
from reporting import generate_reports
from analysis import analyze_results


def generate_metadata_header(args, app, execution_start_time, execution_end_time=None, combinations=None):
    """Generate comprehensive metadata header for result files."""

    # Determine query display based on whether enhancement was used
    if hasattr(args, 'original_query') and hasattr(args, 'enhancement_type'):
        # Enhancement was used
        header_lines = [
            "# Query Information",
            "",
            f"**Enhanced Query** ({args.enhancement_type}):",
            args.query if args.query else "No query specified",
            "",
            "**Original Query:**",
            args.original_query,
            "",
            f"**Enhancement Rationale:** {args.enhancement_rationale}",
            "",
            "# Parameters",
        ]
    else:
        # No enhancement used
        header_lines = [
            "# Query Information",
            "",
            args.query if args.query else "No query specified",
            "",
            "# Parameters",
        ]

    # Continue with common header elements
    header_lines.extend([
        "",
        "## Cognitive Frameworks",
        ""
    ])

    # Extract selected frameworks from args
    if hasattr(args, 'instruction_templates') and args.instruction_templates:
        template_ids = [t.strip() for t in args.instruction_templates.split(',')]
        framework_names = []
        framework_mapping = {
            "ins_analytical": "Analytical",
            "ins_creative": "Creative",
            "ins_critical": "Critical",
            "ins_integrative": "Integrative",
            "ins_pragmatic": "Pragmatic",
            "ins_first_principles": "First Principles",
            "ins_systems": "Systems",
            "ins_contrarian": "Contrarian",
            "ins_historical": "Historical",
            "ins_futurist": "Future-Oriented"
        }
        for template_id in template_ids:
            framework_names.append(f"- {framework_mapping.get(template_id, template_id)}")
        header_lines.append("\n".join(framework_names))
    else:
        header_lines.append(f"Count: {args.instructions if args.instructions else 'Default'}")

    header_lines.extend([
        "",
        "## LLMs",
        ""
    ])

    # Extract selected models
    if hasattr(args, 'selected_models') and args.selected_models:
        selected_models = [m.strip() for m in args.selected_models.split(',')]
        model_names = []
        for model_id in selected_models:
            if model_id in app.model_configs:
                model_name = app.model_configs[model_id].get("name", model_id)
                model_names.append(f"- {model_name}")
            else:
                model_names.append(f"- {model_id}")
        header_lines.append("\n".join(model_names))
    else:
        header_lines.append(f"Count: {args.models if args.models else 'Default'}")

    header_lines.extend([
        "",
        "## Knowledge Domains",
        ""
    ])

    # Extract domains (both static and dynamic)
    domain_names = []

    # Add static domains from args.domain
    if hasattr(args, 'domain') and args.domain:
        for domain_id in args.domain:
            if domain_id.startswith('dynamic:'):
                # Handle dynamic domains that might be in the static domain list
                dynamic_name = domain_id.replace('dynamic:', '')
                domain_names.append(f"- {dynamic_name} (Dynamic)")
            elif domain_id.startswith('domain_'):
                # Convert static domain ID to readable name with better formatting
                name = domain_id.replace('domain_', '').replace('_', ' ')
                # Handle special cases and proper capitalization
                name_parts = name.split()
                formatted_parts = []
                for part in name_parts:
                    if part.lower() in ['ai', 'ml', 'it', 'ux', 'ui', 'api', 'iot']:
                        formatted_parts.append(part.upper())
                    elif part.lower() in ['and', 'or', 'of', 'in', 'on', 'at', 'to', 'for']:
                        formatted_parts.append(part.lower())
                    else:
                        formatted_parts.append(part.capitalize())
                name = ' '.join(formatted_parts)
                domain_names.append(f"- {name}")
            else:
                domain_names.append(f"- {domain_id}")

    # Add dynamic domains from args.dynamic_domain
    if hasattr(args, 'dynamic_domain') and args.dynamic_domain:
        for dynamic_domain in args.dynamic_domain:
            domain_names.append(f"- {dynamic_domain} (Dynamic)")

    # Output the domain list
    if domain_names:
        header_lines.append("\n".join(domain_names))
    else:
        header_lines.append("Default domain selection")

    # Format execution settings with better structure
    # Use actual number of combinations executed instead of misleading variations parameter
    if combinations:
        actual_combinations = len(combinations)
    elif hasattr(app, 'results') and app.results:
        actual_combinations = len(app.results)
    else:
        actual_combinations = 0
    max_combinations = args.max_combinations if args.max_combinations else 'Unlimited'
    output_format = args.output_format.title() if args.output_format else 'Markdown'

    # Determine analysis depth based on actual combinations executed
    if actual_combinations <= 20:
        depth_label = "Quick Exploration"
    elif actual_combinations <= 45:
        depth_label = "Balanced Analysis"
    else:
        depth_label = "Deep Analysis"

    # Determine combination scope
    if isinstance(max_combinations, int):
        if max_combinations <= 30:
            scope_label = "Quick"
        elif max_combinations <= 60:
            scope_label = "Balanced"
        else:
            scope_label = "Comprehensive"
    else:
        scope_label = "Unlimited"

    header_lines.extend([
        "",
        "## Execution Settings",
        "",
        f"- **Analysis Depth**: {actual_combinations} LLM calls ({depth_label})",
        f"- **Output Format**: {output_format}",
        ""
    ])

    # Add execution status
    if execution_end_time:
        duration = int((execution_end_time - execution_start_time).total_seconds())
        status_line = f"**Execution completed successfully!**  \nDuration: {duration} seconds"
        if hasattr(args, 'output_file') and args.output_file:
            result_filename = os.path.basename(args.output_file)
            status_line += f"  \nResults file: {result_filename}"
    else:
        status_line = "**Execution in progress...**"

    header_lines.extend([
        status_line,
        ""
    ])

    # Add separator
    header_lines.extend([
        "---",
        "",
        ""
    ])

    return "\n".join(header_lines)


def update_latest_symlink(run_output_dir: str) -> None:
    """Update the 'latest' symlink to point to the most recent run directory.

    Args:
        run_output_dir: Path to the completed run directory
    """
    try:
        # Get the output base directory
        output_base = os.path.join("data", "output")
        latest_link = os.path.join(output_base, "latest")

        # Convert run_output_dir to relative path from output directory
        if run_output_dir.startswith(output_base):
            # Handle both organized (monthly/weekly) and flat structures
            relative_path = os.path.relpath(run_output_dir, output_base)
        else:
            # Fallback: use just the run folder name
            relative_path = os.path.basename(run_output_dir)

        # Remove existing symlink if it exists
        if os.path.islink(latest_link):
            os.unlink(latest_link)
        elif os.path.exists(latest_link):
            # Handle case where 'latest' is a regular directory/file
            if os.path.isdir(latest_link):
                os.rmdir(latest_link)
            else:
                os.remove(latest_link)

        # Create new symlink
        os.symlink(relative_path, latest_link)
        print(f"Updated 'latest' symlink to point to: {relative_path}")

    except Exception as e:
        print(f"Warning: Could not update 'latest' symlink: {e}")
        # Don't fail the whole run if symlink update fails


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Idea Synthesis and Extraction Engine")

    # Main commands
    parser.add_argument("--config", default="globant_enterprise_config.json",
                        help="Path to configuration file (default: globant_enterprise_config.json)")
    parser.add_argument("--save-state", help="Save application state to file")
    parser.add_argument("--load-state", help="Load application state from file")
    parser.add_argument("--domain-config", help="Path to a domain-specific configuration file")

    # Pipeline parameters
    parser.add_argument("--query", help="Input query text")
    parser.add_argument("--domain", action="append", help="Domain to focus on (can be used multiple times)")
    parser.add_argument("--dynamic-domain", action="append", help="Dynamic domain name (bypasses validation, can be used multiple times)")
    parser.add_argument("--models", type=int, default=2, help="Number of models to use (set to a higher number to include more models)")
    parser.add_argument("--selected-models", type=str, help="Comma-separated list of specific model IDs to use (overrides --models count)")
    parser.add_argument("--use-ollama", action="store_true", help="Include Ollama models in the model selection (automatic when using unified_config.json)")
    parser.add_argument("--instructions", type=int, default=3, help="Number of instructions to use")
    parser.add_argument("--instruction-templates", help="Comma-separated list of specific template IDs to use (overrides --instructions count)")
    parser.add_argument("--variations", type=int, default=2, help="Number of query variations to generate")
    parser.add_argument("--max-combinations", type=int, help="Maximum number of combinations to execute")
    # Sampling method removed - ISEE now uses exhaustive sampling with balanced models for maximum diversity
    parser.add_argument("--output-format", choices=["markdown", "json"], default="markdown", help="Output format")
    parser.add_argument("--output-file", help="Path to save the output to")
    parser.add_argument("--output-directory", help="Directory to save reports to")
    parser.add_argument("--simulate", action="store_true", help="Use simulated responses instead of real model APIs")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be executed without actually running")
    # Balanced models is now enabled by default for maximum diversity - no longer needs to be specified
    parser.add_argument("--synthesize-method", choices=["cluster_based", "cross_pollination"], default="cluster_based",
                        help="Method to use for synthesizing ideas (cluster_based or cross_pollination)")
    parser.add_argument("--generate-reports", action="store_true", help="Generate detailed reports")
    parser.add_argument("--report-format", choices=["markdown", "json"], default="markdown", help="Format for generated reports")
    parser.add_argument("--export-csv", action="store_true", help="Export data as CSV files for analysis")
    parser.add_argument("--no-rank-files", action="store_true", help="Skip renaming raw response files with rank prefixes (useful for programmatic processing)")
    parser.add_argument("--analyze-results", action="store_true", help="Perform analysis of results with visualizations")
    parser.add_argument("--no-visualizations", action="store_true", help="Skip generating visualization charts during analysis")
    # Add simple preset flag options
    parser.add_argument("--quick", action="store_true", help="Run in quick mode (exhaustive sampling with 36 combinations limit)")
    parser.add_argument("--full", action="store_true", help="Run in full mode (exhaustive combinations)")
    parser.add_argument("--list-domains", action="store_true", help="List all available domains and exit")
    parser.add_argument("--expert-mode", action="store_true", help="Bypass guardrail limits (use with caution)")
    parser.add_argument("--force", action="store_true", help="Force execution despite guardrail warnings")
    parser.add_argument("--verbose-queries", action="store_true", help="Show sample complete queries being sent to LLMs")
    parser.add_argument("--show-all-queries", action="store_true", help="Show complete query for every combination (very verbose)")
    parser.add_argument("--query-preview-only", action="store_true", help="Show representative queries without executing")
    parser.add_argument("--enhance-query", action="store_true", help="Show enhanced versions of the input query based on proven patterns")
    parser.add_argument("--json-progress", action="store_true", help="Output structured JSON progress information for Web UI parsing")
    parser.add_argument("--parallel", action="store_true", default=True,
                        help="Use parallel execution for faster processing (default: enabled)")
    parser.add_argument("--sequential", action="store_true", help="Force sequential execution (disables parallel)")
    parser.add_argument("--max-workers", type=int, default=8, help="Maximum concurrent workers for parallel execution")
    parser.add_argument("--provider", choices=["globant", "openrouter"], default="globant",
                        help="API provider to use (globant is primary, openrouter for legacy)")

    # Parse arguments
    args = parser.parse_args()

    # Check for enhancement information from Web UI (passed via environment variables)
    if os.getenv('ISEE_ORIGINAL_QUERY') and os.getenv('ISEE_ENHANCEMENT_TYPE'):
        args.original_query = os.getenv('ISEE_ORIGINAL_QUERY')
        args.enhancement_type = os.getenv('ISEE_ENHANCEMENT_TYPE')
        args.enhancement_rationale = os.getenv('ISEE_ENHANCEMENT_RATIONALE', '')

    # Check if we should list domains and exit
    if args.list_domains:
        # We need to initialize the application first to load domains
        app = ISEEApplication(config_path=args.config, output_directory=args.output_directory)

        # Load domain-specific config if provided
        if args.domain_config and os.path.exists(args.domain_config):
            try:
                with open(args.domain_config, 'r') as f:
                    domain_data = json.load(f)
                    if "domains" in domain_data:
                        # Create a new domain manager to replace the existing one
                        app.domain_manager = DomainManager()
                        for domain_info in domain_data["domains"]:
                            domain = Domain.from_dict(domain_info)
                            app.domain_manager.add_domain(domain)
            except Exception as e:
                print(f"Error loading domain config: {str(e)}")

        # Print all domains
        print("\nAvailable Domains:")
        print("=================")
        for domain in app.domain_manager.list_domains():
            print(f"ID: {domain.id}")
            print(f"Name: {domain.name}")
            print(f"Description: {domain.description}")
            print(f"Keywords: {', '.join(domain.keywords)}")
            print()

        # Exit after listing domains
        sys.exit(0)

    # Check if API keys are available
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    globant_key = os.environ.get("GLOBANT_API_KEY")

    # Check API and Ollama availability
    ollama_available = False
    ollama_models = []
    try:
        from model_api_integration import ModelAPIFactory
        ollama_client = ModelAPIFactory.create_client("ollama")
        ollama_models = ollama_client.get_available_models()
        if ollama_models:
            ollama_available = True
    except Exception:
        # Silently fail if Ollama check fails
        pass

    # Show API status
    api_status = []
    if globant_key:
        api_status.append("Globant Enterprise AI ready (15 strategic models)")
    if anthropic_key:
        api_status.append("Anthropic API key found")
    if openai_key:
        api_status.append("OpenAI API key found")
    if openrouter_key:
        api_status.append("OpenRouter API key found (legacy)")
    if ollama_available:
        api_status.append(f"Ollama available with {len(ollama_models)} models")

    if api_status:
        print(f"API Status: {', '.join(api_status)}")
        print("Real model API calls can be used. Use --simulate to use simulation instead.")

        # Show Ollama models if available
        if ollama_available:
            print(f"\nAvailable Ollama models: {', '.join(ollama_models)}")

        # Check for unified_config.json and suggest it if available
        if os.path.exists("unified_config.json") and not args.config:
            print("\nUNIFIED CONFIG DETECTED: For best results with your available models, consider using:")
            print("python main.py --config unified_config.json --query \"Your query here\"")
            if ollama_available and not (anthropic_key or openai_key or openrouter_key):
                print("This configuration will automatically use only Ollama models since no API keys are present.")

    else:
        print("API Status: No API providers found.")
        print("Options:")
        print("1. Create a .env file with ANTHROPIC_API_KEY, OPENAI_API_KEY, and/or OPENROUTER_API_KEY")
        print("2. Install Ollama (https://ollama.com) and run 'ollama serve'")
        print("3. Use --simulate to run with simulation mode")
        print("4. Run 'python command_wizard.py' for interactive OpenRouter setup")
    print()

    # Initialize the application
    app = ISEEApplication(config_path=args.config, output_directory=args.output_directory)

    # Set provider mode from CLI argument
    app.set_provider_mode(args.provider)

    # Set rank files flag
    app.skip_rank_files = args.no_rank_files

    # Process specific template IDs if provided
    if args.instruction_templates:
        # Split comma-separated string into list of template IDs
        app.specific_template_ids = [template_id.strip() for template_id in args.instruction_templates.split(',')]
        print(f"Using specific instruction templates: {', '.join(app.specific_template_ids)}")

    # Process specific model IDs if provided
    selected_models = None
    if args.selected_models:
        # Split comma-separated string into list of model IDs
        selected_models = [model_id.strip() for model_id in args.selected_models.split(',')]
        print(f"Using specific models: {', '.join(selected_models)}")

    # Load domain-specific config if provided
    if args.domain_config and os.path.exists(args.domain_config):
        try:
            with open(args.domain_config, 'r') as f:
                domain_data = json.load(f)
                if "domains" in domain_data:
                    # Create a new domain manager to replace the existing one
                    app.domain_manager = DomainManager()
                    for domain_info in domain_data["domains"]:
                        domain = Domain.from_dict(domain_info)
                        app.domain_manager.add_domain(domain)
                    print(f"Loaded {len(domain_data['domains'])} domains from {args.domain_config}")
        except Exception as e:
            print(f"Error loading domain config: {str(e)}")

    # Load state if requested
    if args.load_state:
        app.load_state(args.load_state)

        # If synthesize-method is provided without a query, just synthesize from loaded state
        if args.synthesize_method and not args.query:
            top_results = app.get_top_results(n=10)
            if top_results:
                synthesized = app.synthesize_ideas(top_results=top_results, method=args.synthesize_method)
                output = app.format_output(ideas=synthesized, format_type=args.output_format)

                # Determine output path - either user-specified or auto-generated in run-specific directory
                output_path = args.output_file
                if not output_path:
                    # Use .md extension instead of .markdown for better compatibility
                    extension = "md" if args.output_format == "markdown" else args.output_format
                    filename = f"isee_result.{extension}"
                    # Use the run-specific output directory
                    output_path = os.path.join(app.run_output_dir, filename)

                # If user specified a filename without a path, put it in the run directory
                elif not os.path.dirname(output_path):
                    output_path = os.path.join(app.run_output_dir, output_path)

                # Write the output
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w') as f:
                    f.write(output)
                print(f"Output saved to {output_path}")

                # Also print a preview if not redirected
                if not args.output_file:
                    preview_lines = output.split('\n')[:20]  # First 20 lines as preview
                    print("\nOutput Preview:")
                    print("=" * 80)
                    print('\n'.join(preview_lines))
                    if len(output.split('\n')) > 20:
                        print("...")
                        print(f"Full output available in {output_path}")

                # Save state if requested
                if args.save_state:
                    app.save_state(args.save_state)

                # Exit after synthesis
                return

    # Determine if we should use simulation mode
    use_simulation = args.simulate
    if not use_simulation and not (globant_key or anthropic_key or openai_key or openrouter_key or ollama_available):
        print("No API keys available. Forcing simulation mode.")
        use_simulation = True

    # Apply quick and full presets
    if args.quick:
        if not args.max_combinations:
            args.max_combinations = 36
    # Full mode now just removes max_combinations limit

    # Get config settings if available
    max_combinations = args.max_combinations

    # Command line args override config settings
    if hasattr(app, 'execution_settings'):
        # Use config settings if command line args not provided
        if not args.max_combinations and 'max_combinations' in app.execution_settings:
            max_combinations = app.execution_settings['max_combinations']
            if max_combinations:
                print(f"Using max combinations from config: {max_combinations}")

    # Set sensible default based on model count if no limit specified
    if not max_combinations and not args.full:
        # Default: models × 11 (one per framework + 1 extra for diversity)
        max_combinations = args.models * 11
        print(f"Using default max combinations: {max_combinations} ({args.models} models × 11)")

    # Handle query enhancement if requested
    if args.enhance_query and args.query:
        from query_enhancement import get_enhancement_service
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich import box

        console = Console()

        console.print("\n[bold blue]✨ Query Enhancement System[/bold blue]")
        console.print(f"[dim]Original query:[/dim] {args.query}")

        try:
            enhancement_service = get_enhancement_service()
            result = enhancement_service.enhance_query(args.query)

            # Display analysis
            console.print(f"\n[green]Enhancement Analysis (processed in {result.processing_time_ms:.1f}ms):[/green]")
            console.print(Panel(result.enhancement_analysis, box=box.ROUNDED))

            # Create table for enhanced versions
            table = Table(title="Enhanced Query Versions", box=box.ROUNDED)
            table.add_column("Type", style="cyan", width=20)
            table.add_column("Expected Improvement", style="green", width=18)
            table.add_column("Confidence", style="yellow", width=12)
            table.add_column("Enhanced Query", style="white", width=80)

            for i, enhancement in enumerate(result.enhanced_versions):
                table.add_row(
                    enhancement.type.value,
                    enhancement.expected_quality_improvement,
                    f"{enhancement.confidence_score:.0%}",
                    enhancement.query[:300] + ("..." if len(enhancement.query) > 300 else "")
                )

            console.print("\n")
            console.print(table)

            # Show detailed versions
            for i, enhancement in enumerate(result.enhanced_versions):
                console.print(f"\n[bold cyan]Option {i+1}: {enhancement.type.value}[/bold cyan]")
                console.print(f"[green]{enhancement.expected_quality_improvement}[/green] | [yellow]{enhancement.confidence_score:.0%} confidence[/yellow]")
                console.print(Panel(enhancement.query, title="Enhanced Query", box=box.MINIMAL))
                console.print(f"[dim]Rationale: {enhancement.rationale}[/dim]")

            # Ask user to select an enhancement
            console.print(f"\n[bold]Would you like to use one of these enhanced versions?[/bold]")
            console.print("[dim]Enter the option number (1-{}) to use that enhancement, or press Enter to keep original:[/dim]".format(len(result.enhanced_versions)))

            choice = input().strip()

            if choice.isdigit():
                choice_num = int(choice) - 1
                if 0 <= choice_num < len(result.enhanced_versions):
                    selected_enhancement = result.enhanced_versions[choice_num]
                    args.query = selected_enhancement.query
                    console.print(f"[green]✅ Using {selected_enhancement.type.value} enhancement[/green]")
                    console.print(f"[dim]Updated query:[/dim] {args.query[:100]}{'...' if len(args.query) > 100 else ''}")
                else:
                    console.print("[yellow]Invalid selection. Using original query.[/yellow]")
            else:
                console.print("[blue]Using original query.[/blue]")

            # Update analytics
            analytics = enhancement_service.get_analytics()
            console.print(f"\n[dim]Enhancement Analytics: {analytics['total_enhancements']} queries enhanced, avg processing time: {analytics['average_processing_time']:.1f}ms[/dim]")

            # Store enhancement information for reporting
            if choice.isdigit() and 0 <= int(choice) - 1 < len(result.enhanced_versions):
                selected_enhancement = result.enhanced_versions[int(choice) - 1]
                args.original_query = result.original  # Store original for reporting
                args.enhancement_type = selected_enhancement.type.value
                args.enhancement_rationale = selected_enhancement.rationale

        except Exception as e:
            console.print(f"[red]Enhancement failed: {e}[/red]")
            console.print("[yellow]Continuing with original query...[/yellow]")

        console.print("\n" + "="*80 + "\n")

    # Run pipeline if query is provided
    if args.query:
        # GUARDRAIL VALIDATION - Check limits before execution
        if not args.expert_mode:
            validation_result = ISEEGuardrails.validate_command_limits(args)

            # Print device info and estimates
            print(f"\n🖥️  Device Type: {validation_result['device_type'].title()}")
            print(f"📊 Estimated: {validation_result['estimated_combinations']:,} combinations, "
                  f"${validation_result['estimated_cost']:.2f} cost, "
                  f"{validation_result['estimated_time_minutes']:.1f} min")

            # Handle HARD LIMITS (blocking errors)
            if validation_result['errors']:
                print("\n🚫 COMMAND REJECTED - Exceeds safety limits:")
                for error in validation_result['errors']:
                    print(f"   {error}")

                ISEEGuardrails.print_optimization_suggestions(validation_result, args)

                print("🔧 To bypass these limits, add --expert-mode (use with caution)")
                print("   Example: python main.py --expert-mode [your command]")
                sys.exit(1)

            # Handle WARNINGS (informational)
            if validation_result['warnings']:
                print("\n⚠️  PERFORMANCE WARNINGS:")
                for warning in validation_result['warnings']:
                    print(f"   {warning}")

                if not args.force:
                    ISEEGuardrails.print_optimization_suggestions(validation_result, args)
                    print("🚀 To proceed anyway, add --force")
                    print("   Example: python main.py --force [your command]")
                    sys.exit(1)

            print("✅ Command within safety limits\n")
        else:
            print("🔥 EXPERT MODE: Guardrails bypassed\n")

        # If dry run is specified, just print what would be executed
        if args.dry_run:
            # Handle multiple domains for dry run using direct mapping
            domain_ids = None
            if args.domain:
                domain_ids = []
                for domain_name in args.domain:
                    # Direct domain ID validation
                    if domain_name.startswith('domain_'):
                        if domain_name in app.domain_manager.domains:
                            domain_ids.append(domain_name)
                            print(f"Using domain ID: {domain_name}")
                        else:
                            print(f"Error: Invalid domain ID '{domain_name}'")
                            sys.exit(1)
                    else:
                        # Domain name provided - find exact match
                        all_domains = app.domain_manager.list_domains()
                        exact_matches = [d for d in all_domains if d.name.lower() == domain_name.lower()]
                        if exact_matches:
                            domain_ids.append(exact_matches[0].id)
                            print(f"Found exact match for '{domain_name}' -> {exact_matches[0].id}")
                        else:
                            print(f"Error: No exact match found for domain '{domain_name}'")
                            sys.exit(1)

            combinations = app.generate_combinations(
                query_id=app.query_generator.list_base_queries()[0].id,
                domain_ids=domain_ids,
                model_count=args.models,
                instruction_count=args.instructions,
                query_variations=args.variations,
                # exhaustive + balanced is now the default
                max_combinations=max_combinations,
                selected_models=selected_models
            )
            app.execute_combinations(
                combinations=combinations,
                max_to_execute=max_combinations,
                dry_run=True
            )
        else:
            # Handle query preview mode
            if args.query_preview_only:
                print("🔍 QUERY PREVIEW MODE: Generating combinations and showing representative queries")

                # Handle multiple domains for query preview using direct mapping
                domain_ids = None
                if args.domain:
                    domain_ids = []
                    for domain_name in args.domain:
                        # Direct domain ID validation
                        if domain_name.startswith('domain_'):
                            if domain_name in app.domain_manager.domains:
                                domain_ids.append(domain_name)
                                print(f"Using domain ID: {domain_name}")
                            else:
                                print(f"Error: Invalid domain ID '{domain_name}'")
                                sys.exit(1)
                        else:
                            # Domain name provided - find exact match
                            all_domains = app.domain_manager.list_domains()
                            exact_matches = [d for d in all_domains if d.name.lower() == domain_name.lower()]
                            if exact_matches:
                                domain_ids.append(exact_matches[0].id)
                                print(f"Found exact match for '{domain_name}' -> {exact_matches[0].id}")
                            else:
                                print(f"Error: No exact match found for domain '{domain_name}'")
                                sys.exit(1)

                # Generate combinations without executing
                combinations = app.generate_combinations(
                    query_id=app.query_generator.list_base_queries()[0].id,
                    domain_ids=domain_ids,
                    model_count=args.models,
                    instruction_count=args.instructions,
                    query_variations=args.variations,
                    max_combinations=max_combinations,
                    selected_models=selected_models
                )

                # Show query preview
                app.show_query_preview(combinations=combinations, sample_count=8, show_breakdown=True)
                return

            # Process instruction templates parameter if provided
            specific_templates = None
            if args.instruction_templates:
                specific_templates = [template_id.strip() for template_id in args.instruction_templates.split(',')]

            # Track execution timing for metadata
            execution_start_time = datetime.now()

            # Handle --sequential flag overriding parallel
            use_parallel = args.parallel and not getattr(args, 'sequential', False)
            if use_parallel:
                print("🚀 Parallel execution enabled")
            else:
                print("⚡ Sequential execution mode")

            output = app.run_complete_pipeline(
                query_text=args.query,
                domain_names=args.domain,
                dynamic_domain_names=args.dynamic_domain,
                model_count=args.models,
                instruction_count=args.instructions,
                query_variations=args.variations,
                max_combinations=max_combinations,
                output_format=args.output_format,
                use_real_models=not use_simulation,
                # exhaustive + balanced models is now the default
                specific_template_ids=specific_templates,
                verbose_queries=args.verbose_queries,
                show_all_queries=args.show_all_queries,
                selected_models=selected_models,
                json_progress=args.json_progress,
                parallel=use_parallel,
                max_workers=args.max_workers
            )

            execution_end_time = datetime.now()

            # Apply custom synthesis method if specified
            if args.synthesize_method and args.synthesize_method != "cluster_based":
                print(f"Applying {args.synthesize_method} synthesis method...")
                top_results = app.get_top_results(n=10)
                if top_results:
                    synthesized = app.synthesize_ideas(top_results=top_results, method=args.synthesize_method)
                    output = app.format_output(ideas=synthesized, format_type=args.output_format)

        # Print or save the output if not a dry run
        if not args.dry_run:
            # Determine output path - either user-specified or auto-generated in run-specific directory
            output_path = args.output_file
            if not output_path:
                # Use .md extension instead of .markdown for better compatibility
                extension = "md" if args.output_format == "markdown" else args.output_format
                filename = f"isee_result.{extension}"
                # Use the run-specific output directory
                output_path = os.path.join(app.run_output_dir, filename)

            # If user specified a filename without a path, put it in the run directory
            elif not os.path.dirname(output_path):
                output_path = os.path.join(app.run_output_dir, output_path)

            # Generate metadata header and combine with output
            metadata_header = generate_metadata_header(args, app, execution_start_time, execution_end_time)
            combined_output = metadata_header + output

            # Write the output with metadata header
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(combined_output)
            print(f"Output saved to {output_path}")

            # Also print a preview if not redirected
            if not args.output_file:
                preview_lines = combined_output.split('\n')[:20]  # First 20 lines as preview
                print("\nOutput Preview:")
                print("=" * 80)
                print('\n'.join(preview_lines))
                if len(combined_output.split('\n')) > 20:
                    print("...")
                    print(f"Full output available in {output_path}")

            # Generate additional reports if requested
            if args.generate_reports:
                print("\nGenerating detailed reports...")
                report_files = generate_reports(
                    app=app,
                    args=args,
                    query=args.query,
                    combinations=app.combinations,
                    results=app.results,
                    evaluations=app.evaluations,
                    synthesized_ideas=app.synthesized_ideas,
                    run_output_dir=app.run_output_dir
                )

                print("Reports generated:")
                for report_name, file_path in report_files.items():
                    print(f"- {report_name.capitalize()} report: {file_path}")

                # Perform analysis if requested
                if args.analyze_results:
                    print("\nAnalyzing results...")
                    # Prefer app's run directory if available
                    output_directory = app.run_output_dir if hasattr(app, 'run_output_dir') else (args.output_directory if args.output_directory else "data/output")
                    generate_visualizations = not args.no_visualizations

                    # CSV files are now directly in the run directory, no timestamp needed
                    analysis_report, visualization_files = analyze_results(
                        data_directory=output_directory,
                        output_directory=output_directory,
                        output_format=args.report_format,
                        run_timestamp=None,  # Not needed with new directory structure
                        generate_visualizations=generate_visualizations
                    )

                    # Save analysis report with simple name in run directory
                    # Always use .md extension for markdown files for consistency
                    extension = "md" if args.report_format == "markdown" else args.report_format
                    analysis_filename = f"analysis.{extension}"
                    analysis_path = os.path.join(output_directory, analysis_filename)

                    with open(analysis_path, 'w') as f:
                        f.write(analysis_report)

                    print(f"Analysis report saved to: {analysis_path}")

                    if visualization_files:
                        print("Visualizations generated:")
                        for viz_file in visualization_files:
                            print(f"- {viz_file}")

    # Save state if requested
    if args.save_state:
        app.save_state(args.save_state)

    # Update 'latest' symlink to point to this run
    if hasattr(app, 'run_output_dir') and app.run_output_dir:
        update_latest_symlink(app.run_output_dir)


if __name__ == "__main__":
    main()
