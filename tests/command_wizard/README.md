# ISEE Command Wizard Test Framework

This directory contains a comprehensive test framework for the ISEE Command Construction Wizard. The framework is designed to validate the functionality of the wizard and ensure it correctly aligns with the core functionality of the ISEE framework.

## Overview

The test framework implements Phase 1 of the roadmap outlined in the [ISEE Command Wizard Assessment and Roadmap](../../specs/ISEE_Command_Wizard_Assessment_and_Roadmap.md) document. It provides a systematic approach to testing the wizard's functionality and establishing baseline metrics.

## Components

The test framework consists of the following components:

- **Test Harness**: A utility class for testing the Command Wizard with simulated inputs and mocked dependencies.
- **API Detection Tests**: Tests for the wizard's ability to detect and handle different API configurations.
- **Domain Loading Tests**: Tests for the wizard's ability to load domain configurations from files.
- **Template Selection Tests**: Tests for the wizard's template selection functionality.
- **Command Construction Tests**: Tests for the wizard's ability to construct valid commands.
- **Baseline Metrics**: Utilities for establishing baseline functionality metrics.
- **Test Runner**: A script for running all tests or specific tests.

## Usage

### Running All Tests

To run all tests, use the following command:

```bash
python tests/command_wizard/run_tests.py
```

### Running Specific Tests

To run specific tests, specify the test category or test name:

```bash
python tests/command_wizard/run_tests.py --tests api
```

or

```bash
python tests/command_wizard/run_tests.py --tests test_no_apis_available
```

### Listing Available Tests

To list all available tests:

```bash
python tests/command_wizard/run_tests.py --list
```

### Generating Baseline Metrics

To generate baseline metrics for the Command Wizard:

```bash
python tests/command_wizard/baseline_metrics.py
```

This will create a JSON file with detailed metrics and a Markdown summary in the `tests/command_wizard/baseline` directory.

## Test Categories

### API Detection Tests

These tests validate the wizard's ability to detect and handle different API configurations:

- No API keys available
- Only Anthropic API key available
- All API keys available
- Only Ollama available

### Domain Loading Tests

These tests validate the wizard's ability to load domain configurations:

- Loading default domains
- Loading domains from tech_writing_domains.json
- Loading domains from learning_design_domains.json
- Handling malformed domain files

### Template Selection Tests

These tests validate the wizard's template selection functionality:

- Selecting all templates
- Selecting specific templates
- Verifying template count affects combinations

### Command Construction Tests

These tests validate the wizard's ability to construct valid commands:

- Simple query with no special characters
- Complex query with special characters
- Command with all available parameters
- Automatic inclusion of unified config if available
- Handling of specific template selections

## Baseline Metrics

The baseline metrics module establishes baseline functionality metrics for the Command Wizard, including:

- API detection capabilities
- Domain loading capabilities
- Template selection capabilities
- Command construction capabilities
- Command validation
- Parameter mapping between wizard and main.py
- Compatibility between wizard and main.py

## Future Work

This test framework is just the beginning. Future phases of the roadmap include:

- **Phase 2**: Core Functionality Alignment
- **Phase 3**: Feature Completion
- **Phase 4**: User Experience Improvements
- **Phase 5**: Documentation and Training

## Contributing

When adding new tests or modifying existing ones, please ensure:

1. The tests are isolated and do not depend on external state
2. The tests use the test harness for consistent testing
3. The tests are documented with clear descriptions
4. The baseline metrics are updated if necessary