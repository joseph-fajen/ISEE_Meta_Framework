# ISEE Command Construction Wizard Specification

## Overview

This document specifies the design and flow for a command construction wizard and conversational agent that will help users create properly formatted ISEE commands with minimal friction. The goal is to remove technical barriers while preserving access to the full power of the ISEE framework.

## API and Model Availability Detection

The wizard should automatically detect available APIs and local models:

1. **API Key Detection**
   - Check for environment variables (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`)
   - Check for API keys in `.env` file (via dotenv if installed)
   - Disable unavailable options or mark them as requiring setup

2. **Ollama Detection**
   - Check if Ollama is running locally (http://localhost:11434)
   - Query available models via Ollama API, with fallback to CLI
   - Provide guidance for installing missing models (`ollama pull model_name`)

3. **Provider Selection Logic**
   - If no APIs are available, automatically select simulation mode
   - If only certain providers are available, prioritize those
   - If user selects unavailable providers, show setup instructions

4. **Simulation Fallback**
   - Always offer simulation mode as an option
   - Clearly indicate when simulation mode is being used
   - Explain limitations of simulation mode

## Design Principles

1. **Progressive Disclosure** - Present options in order of importance, revealing complexity only as needed
2. **Natural Language Interface** - Allow users to express needs conversationally
3. **Guaranteed Correctness** - Ensure all constructed commands are syntactically correct
4. **Contextual Help** - Provide explanations of options as they are being selected
5. **Parameter Relationships** - Highlight how different parameters interact and affect results
6. **Transparent Translation** - Show users how their requirements map to command parameters

## Command Construction Wizard

### Wizard Flow

The wizard should follow a logical progression from essential to optional elements:

#### 1. Project Initialization

```
[ ] Create a new project
[ ] Continue existing project

[If continuing]
    Select project state file: [Dropdown of state files in data/state/]
```

#### 2. Query Definition

```
What innovation challenge would you like to explore?
[Text input field]

Which domain best describes this challenge? [Dropdown + Search]
[  ] Urban Planning
[  ] Healthcare
[  ] Education
[  ] Technology Innovation
[  ] Sustainability
...
[  ] Other (specify)
```

#### 3. Model Selection

```
Which AI models would you like to use?

[Cloud Models]
[ ] Anthropic Claude (requires API key)
[ ] OpenAI GPT-4 (requires API key)
[ ] Google Gemini (requires API key)

[Local Models]
[ ] Ollama Models (requires local installation)
    [ ] LLaMA 3 8B
    [ ] CodeLLaMA 7B
    [ ] Mixtral
    [ ] Phi-3 Mini

How many different models should be included?
[Slider: 1-7, Default: 2]

[ ] Ensure balanced representation of models
```

#### 4. Cognitive Diversity

```
How many different cognitive approaches (instruction templates) should be used?
[Slider: 1-10, Default: 3]

[ ] Analytical (logical, systematic)
[ ] Creative (imaginative, divergent)
[ ] Critical (evaluative, challenging)
[ ] Integrative (synthesizing perspectives)
[ ] Pragmatic (implementation-focused)
[ ] First Principles (fundamental analysis)
[ ] Systems Thinking (holistic ecosystem view)
[ ] Contrarian (challenging conventional wisdom)
[ ] Historical (pattern recognition from past)
[ ] Futurist (anticipating long-term trends)

How many variations of your query should be generated?
[Slider: 1-5, Default: 2]
```

#### 5. Execution Parameters

```
How many combinations would you like to execute?
[Slider with cost estimate display]

Sampling method:
( ) Exhaustive (all possible combinations - default)
( ) Stratified (balanced representation across dimensions)
( ) Adaptive (learns and adjusts based on early results)

Synthesis method:
( ) Cluster-based (groups similar ideas)
( ) Cross-pollination (combines diverse perspectives)
```

#### 6. Output Preferences

```
Output format:
( ) Markdown (human-readable)
( ) JSON (machine-processable)

Save output as:
[Filename input] [Browse...]

Advanced output options:
[ ] Generate detailed reports
[ ] Export data as CSV for analysis
[ ] Perform automatic analysis with visualizations
```

#### 7. Execution Mode

```
How would you like to run this command?

( ) Normal execution (uses API calls as configured)
( ) Simulation mode (no API calls)
( ) Dry run (preview only)

[ ] Save state for later continuation
```

#### 8. Command Preview

```
Based on your selections, the following command will be executed:

python main.py --query "How might we improve urban transportation?" --domain "Urban Planning" --models 3 --instructions 4 --variations 2 --max-combinations 15 --sampling-method adaptive --balanced-models --output-file "transportation_ideas.md" --generate-reports --analyze-results

[Edit Command] [Copy Command] [Execute]
```

### Progressive Help System

Throughout the wizard, contextual help should be available:

- **Tooltips** - Brief explanations on hover
- **Info panels** - More detailed explanations when clicking (?)
- **Cost estimator** - Dynamic calculation of API costs based on selections
- **Time estimator** - Approximate execution time based on selections
- **Conflict detector** - Warnings when incompatible options are selected

## Conversational Agent Interface

The conversational agent provides a natural language alternative to the structured wizard, following a similar logical flow but in dialogue form.

### Agent Interview Flow

#### 1. Initial Greeting and Project Context

```
Agent: "Welcome to the ISEE framework! Would you like to start a new innovation project or continue an existing one?"

User: "Start a new project."

Agent: "Great! I'll help you set up your innovation exploration."
```

#### 2. Problem Exploration

```
Agent: "What innovation challenge or question would you like to explore today?"

User: "I'm trying to figure out how to make transportation more sustainable in urban areas."

Agent: "That sounds like an urban planning challenge focused on sustainability. Would you say that's accurate, or is it more about environmental science or technology innovation?"

User: "Urban planning is right, but with elements of environmental science too."

Agent: "I'll categorize this primarily as 'Urban Planning' with cross-domain elements. This will help ensure we get the most relevant cognitive frameworks."
```

#### 3. Resource and Scope Definition

```
Agent: "How extensively would you like to explore this question? We can do a quick exploration with a few AI models, or a more comprehensive analysis with multiple models and approaches."

User: "I'd like a fairly comprehensive analysis, but I'm concerned about costs."

Agent: "I understand. Let me ask about your available AI resources first. Do you have access to Claude, GPT, or Gemini through API keys? Or would you prefer to use local Ollama models?"

User: "I have Claude and GPT keys, but not Gemini."

Agent: "Great. For a balanced exploration that manages costs, I'd recommend using 3 models (2 from Claude, 1 from GPT) with 3 different cognitive approaches and 2 query variations. This would result in approximately 18 combinations. Would that work for you?"

User: "That sounds good."
```

#### 4. Output Preferences

```
Agent: "How would you like to receive the results? I can prepare a markdown report, JSON data, or include additional analysis and visualizations."

User: "I'd like a readable report with some visualizations."

Agent: "I'll set up a markdown report with analysis visualizations. Would you like to save the state of this project so you can continue or modify it later?"

User: "Yes, that would be helpful."

Agent: "What would you like to name this project?"

User: "Sustainable Urban Transit 2025"
```

#### 5. Command Construction and Confirmation

```
Agent: "Based on our conversation, I've constructed the following command:

python main.py --config unified_config.json --query "How might we make transportation more sustainable in urban areas?" --domain "Urban Planning" --models 3 --instructions 3 --variations 2 --max-combinations 18 --balanced-models --output-file "sustainable_urban_transit_2025.md" --generate-reports --analyze-results --export-csv --save-state "sustainable_urban_transit_2025.json"

This will:
- Use 3 models (selected based on available providers)
- Apply 3 different cognitive approaches
- Create 2 variations of your query
- Execute up to 18 total combinations
- Generate a markdown report with visualizations and CSV data exports
- Save the state for future continuation

Does this look correct, or would you like to adjust anything?"

User: "That looks perfect. Let's run it."

Agent: "Great! I'm executing the command now. This may take 5-10 minutes to complete based on current system load. I'll notify you when it's finished."
```

### Agent Capabilities

The agent should be able to:

1. **Translate natural language** - Convert user statements into parameter values
2. **Detect ambiguity** - Ask clarifying questions when user intent is unclear
3. **Suggest appropriate values** - Recommend parameter settings based on context
4. **Explain tradeoffs** - Clarify how different choices affect results and resources
5. **Handle corrections** - Allow users to revise earlier choices
6. **Learn preferences** - Remember user preferences for future sessions
7. **Detect environment** - Check for available API keys and local models
8. **Validate commands** - Ensure constructed commands are valid before execution

## Implementation Considerations

### Technical Architecture

1. **Form-Based Wizard**
   - Web-based interface with responsive design
   - Client-side validation for immediate feedback
   - Parameter dependency management to avoid conflicts

2. **Conversational Agent**
   - LLM-powered interface with structured dialogue flow
   - Semantic parsing to extract parameter values from natural language
   - State tracking to maintain context throughout the conversation
   - Command validation before execution

### Integration with ISEE Framework

Both interfaces should:

1. **Validate command syntax** against the ISEE parameter schema
2. **Check environment** for available resources (API keys, local models)
3. **Estimate resource usage** before execution
4. **Provide real-time feedback** during command execution
5. **Handle errors gracefully** with clear explanations
6. **Record command history** for easy reuse and modification
7. **Support parameter presets** for common use cases

### User Experience Optimizations

1. **Command Templates Library**
   ```
   [Quick Exploration] [Comprehensive Analysis] [Cross-Model Comparison] [Domain-Specific Deep Dive]
   ```

2. **Parameter Groups**
   ```
   [Basic] [Models] [Cognitive Diversity] [Execution] [Output] [Advanced]
   ```

3. **Presets for Different User Types**
   ```
   [Novice] [Intermediate] [Expert] [Developer]
   ```

4. **Smart Defaults**
   - Automatically adjust related parameters when one parameter changes
   - Suggest optimal values based on query complexity and available resources

## Conclusion

The command construction wizard and conversational agent described in this specification will significantly reduce the friction in using the ISEE framework. By guiding users through a logical progression of choices, these interfaces ensure that the powerful capabilities of ISEE are accessible without requiring deep technical knowledge of command syntax.

The implementation should prioritize correctness, clarity, and contextual guidance while maintaining access to the full range of ISEE capabilities. This approach aligns perfectly with the overall goal of the ISEE Meta-Framework: systematizing innovation while removing barriers to creativity and exploration.
