#!/bin/bash
# Make this file executable with: chmod +x run_examples.sh
# ISEE Framework Example Runner
# This script runs a series of example queries through the ISEE framework

# Create necessary directories if they don't exist
mkdir -p data/results
mkdir -p data/state
mkdir -p data/output

# Function to run an example
run_example() {
  query="$1"
  domain="$2"
  output_name="$3"
  
  echo "Running query: $query"
  echo "Domain: $domain"
  echo "Output: $output_name"
  echo "--------------------------------"
  
  # Run the query
  python main.py \
    --query "$query" \
    --domain "$domain" \
    --models 2 \
    --instructions 3 \
    --variations 2 \
    --max-combinations 10 \
    --output-format markdown \
    --output-file "data/output/${output_name}.md" \
    --save-state "data/state/${output_name}.json"
  
  echo "--------------------------------"
  echo "Results saved to data/output/${output_name}.md"
  echo "State saved to data/state/${output_name}.json"
  echo ""
}

# Function to view results
view_results() {
  output_name="$1"
  
  echo "Viewing results for: $output_name"
  echo "--------------------------------"
  
  # Run the viewer in summary mode
  python result_viewer.py \
    --state "data/state/${output_name}.json" \
    --summary
  
  echo "--------------------------------"
  echo "To explore interactively: python result_viewer.py --state data/state/${output_name}.json --interactive"
  echo ""
}

# Example 1: Urban Transportation
run_example "How might we improve urban transportation in the next decade?" "Urban Planning" "urban_transportation"
view_results "urban_transportation"

# Example 2: Education Innovation
run_example "How might we redesign education systems to better prepare students for future challenges?" "Education" "education_innovation"
view_results "education_innovation"

# Example 3: Sustainable Energy
run_example "How might we accelerate the transition to sustainable energy sources?" "Sustainability" "sustainable_energy"
view_results "sustainable_energy"

# Example 4: Healthcare Access
run_example "How might we make healthcare more accessible and affordable for everyone?" "Healthcare" "healthcare_access"
view_results "healthcare_access"

# Example 5: Technology Innovation
run_example "How might we use artificial intelligence to solve real-world problems?" "Technology Innovation" "ai_solutions"
view_results "ai_solutions"

echo "All examples completed!"
echo "To explore any example interactively, use:"
echo "python result_viewer.py --state data/state/EXAMPLE_NAME.json --interactive"
