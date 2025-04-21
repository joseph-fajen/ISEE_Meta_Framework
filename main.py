"""
Main Application for ISEE Framework

This module provides a simple command-line interface to interact with the
Idea Synthesis and Extraction Engine framework.
"""

import os
import json
import argparse
from typing import Dict, Any, List, Optional, Tuple
import time
import random

# Import modules
from model_api_integration import ModelAPIFactory, ModelAPIClient
from instruction_templates import TemplateLibrary, create_default_library, InstructionTemplate
from query_generator import QueryGenerator, create_default_queries, Query
from domain_manager import DomainManager, create_default_domains, Domain
from evaluation_scoring import ScoringFramework, create_default_framework

class ISEEApplication:
    """Main application class for the ISEE framework."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the ISEE application.
        
        Args:
            config_path: Optional path to a configuration file.
        """
        # Initialize components
        self.template_library = create_default_library()
        self.query_generator = QueryGenerator()
        self.domain_manager = DomainManager()
        self.scoring_framework = create_default_framework()
        
        # Add default data
        for query in create_default_queries():
            self.query_generator.add_base_query(query)
        
        for domain in create_default_domains():
            self.domain_manager.add_domain(domain)
        
        # Storage for results
        self.combinations = []
        self.results = {}
        self.evaluations = {}
        self.synthesized_ideas = {}
        
        # Model configuration and clients
        self.model_configs = {}
        self.model_clients = {}
        
        # Load configuration if provided
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Process configuration
        print(f"Loading configuration from {config_path}...")
        
        # Directory for data
        os.makedirs("data", exist_ok=True)
        
        # Load model configurations
        if "models" in config:
            for model_config in config["models"]:
                model_id = model_config.get("id")
                if model_id:
                    self.model_configs[model_id] = model_config
                    print(f"Loaded configuration for model: {model_id}")
        
        # Load instruction templates if provided
        if "instructions" in config:
            self.template_library = TemplateLibrary()
            for template_data in config["instructions"]:
                template = InstructionTemplate.from_dict(template_data)
                self.template_library.add_template(template)
            print(f"Loaded {len(config['instructions'])} instruction templates")
        
        # Load domains if provided
        if "domains" in config:
            self.domain_manager = DomainManager()
            for domain_data in config["domains"]:
                domain = Domain.from_dict(domain_data)
                self.domain_manager.add_domain(domain)
            print(f"Loaded {len(config['domains'])} domains")
        
        # Load queries if provided
        if "queries" in config:
            for query_data in config["queries"]:
                query = Query.from_dict(query_data)
                self.query_generator.add_base_query(query)
            print(f"Loaded {len(config['queries'])} queries")
    
    def save_state(self, state_path: str) -> None:
        """Save the current state to a file.
        
        Args:
            state_path: Path to save the state to.
        """
        state = {
            "combinations": self.combinations,
            "results": self.results,
            "evaluations": self.evaluations,
            "synthesized_ideas": self.synthesized_ideas
        }
        
        with open(state_path, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"State saved to {state_path}")
    
    def load_state(self, state_path: str) -> None:
        """Load state from a file.
        
        Args:
            state_path: Path to the state file.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        with open(state_path, 'r') as f:
            state = json.load(f)
        
        self.combinations = state.get("combinations", [])
        self.results = state.get("results", {})
        self.evaluations = state.get("evaluations", {})
        self.synthesized_ideas = state.get("synthesized_ideas", {})
        
        print(f"State loaded from {state_path}")
    
    def generate_combinations(
        self,
        query_id: str,
        domain_ids: Optional[List[str]] = None,
        model_count: int = 2,
        instruction_count: int = 3,
        query_variations: int = 2,
        balanced: bool = False
    ) -> List[Dict[str, Any]]:
        """Generate combinations of models, instructions, queries, and domains.
        
        Args:
            query_id: ID of the base query.
            domain_ids: Optional list of domain IDs. If None, all domains are used.
            model_count: Number of models to use.
            instruction_count: Number of instructions to use.
            query_variations: Number of query variations to generate.
            balanced: If True, ensure balanced representation of models in the final combinations.
            
        Returns:
            List of combination dictionaries.
            
        Raises:
            KeyError: If the query ID does not exist.
        """
        # Get the base query
        base_query = self.query_generator.get_query_by_id(query_id)
        if not base_query:
            raise KeyError(f"No query with ID '{query_id}' exists")
        
        # Generate query variations
        variations = self.query_generator.generate_variations(query_id, count=query_variations)
        all_queries = [base_query] + variations
        
        # Get domains
        if domain_ids:
            domains = [self.domain_manager.get_domain(did) for did in domain_ids]
        else:
            domains = self.domain_manager.list_domains()
        
        # Use model IDs from config, or create placeholder IDs if not available
        if self.model_configs:
            models = list(self.model_configs.keys())
            if model_count == len(models):
                # Use all available models
                pass
            elif model_count < len(models):
                # If we need fewer models than available, prioritize diversity
                # Instead of random sampling, we'll ensure we get a mix of different providers
                provider_models = {}
                for model_id in models:
                    if model_id in self.model_configs:
                        model_config = self.model_configs[model_id]
                        model_name = model_config.get("name", "")
                        # Determine provider
                        provider = model_config.get("provider", "")
                        if not provider:
                            if "claude" in model_name.lower():
                                provider = "anthropic"
                            elif "gpt" in model_name.lower():
                                provider = "openai"
                            elif any(keyword in model_name.lower() for keyword in 
                                     ["llama", "mixtral", "codellama", "phi3"]):
                                provider = "ollama"
                            else:
                                provider = "unknown"
                        # Group by provider
                        provider_models.setdefault(provider, []).append(model_id)
                
                # Select models to ensure diversity across providers
                selected_models = []
                # First, select one model from each provider
                for provider in provider_models:
                    if provider_models[provider] and len(selected_models) < model_count:
                        selected_models.append(provider_models[provider][0])
                
                # If we still need more models, add additional ones
                providers_cycle = list(provider_models.keys())
                idx = 0
                while len(selected_models) < model_count and idx < 100:  # avoid infinite loop
                    provider = providers_cycle[idx % len(providers_cycle)]
                    provider_list = provider_models[provider]
                    if len(provider_list) > 1:  # If there are more models from this provider
                        for model in provider_list[1:]:
                            if model not in selected_models and len(selected_models) < model_count:
                                selected_models.append(model)
                    idx += 1
                
                models = selected_models
        else:
            # Fall back to placeholder IDs
            models = [f"model_{i}" for i in range(1, model_count + 1)]
        
        # Get instructions
        all_templates = self.template_library.list_templates()
        if len(all_templates) > instruction_count:
            # Randomly select a subset of templates
            templates = random.sample(all_templates, instruction_count)
        else:
            templates = all_templates
        
        # Generate all combinations
        combinations = []
        
        if balanced:
            # Create combinations in a balanced way by interleaving models
            # First, create all possible template/query/domain combinations
            component_combinations = []
            for template in templates:
                for query in all_queries:
                    for domain in domains:
                        component_combinations.append((template, query, domain))
            
            # Then distribute these combinations across models in a balanced way
            while component_combinations and models:
                for model in models:
                    if not component_combinations:
                        break
                    
                    template, query, domain = component_combinations.pop(0)
                    combination_id = f"{model}_{template.id}_{query.id}_{domain.id}"
                    
                    combination = {
                        "id": combination_id,
                        "model": model,
                        "template": template.id,
                        "query": query.id,
                        "domain": domain.id
                    }
                    
                    combinations.append(combination)
        else:
            # Create combinations grouped by model (original behavior)
            for model in models:
                for template in templates:
                    for query in all_queries:
                        for domain in domains:
                            combination_id = f"{model}_{template.id}_{query.id}_{domain.id}"
                            
                            combination = {
                                "id": combination_id,
                                "model": model,
                                "template": template.id,
                                "query": query.id,
                                "domain": domain.id
                            }
                            
                            combinations.append(combination)
        
        # Store the combinations
        self.combinations = combinations
        
        print(f"Generated {len(combinations)} combinations")
        return combinations
    
    def _get_or_create_model_client(self, model_id: str) -> Optional[ModelAPIClient]:
        """Get or create a model API client.
        
        Args:
            model_id: ID of the model.
            
        Returns:
            ModelAPIClient instance or None if model configuration is not available.
        """
        # Return existing client if already created
        if model_id in self.model_clients:
            return self.model_clients[model_id]
        
        # Check if we have configuration for this model
        if model_id not in self.model_configs:
            print(f"Warning: No configuration found for model {model_id}")
            return None
        
        # Create a new client
        model_config = self.model_configs[model_id]
        model_name = model_config.get("name", "")
        
        try:
            # Determine provider from model name or explicit provider field
            provider = model_config.get("provider", "")
            if not provider:
                if "claude" in model_name.lower():
                    provider = "anthropic"
                elif "gpt" in model_name.lower():
                    provider = "openai"
                elif any(keyword in model_name.lower() for keyword in 
                        ["llama", "mixtral", "codellama", "phi3"]):
                    provider = "ollama"
                else:
                    print(f"Warning: Could not determine provider for model {model_id}")
                    return None
            
            print(f"Creating client for model {model_id} using provider: {provider}")
            
            # For Ollama models, check if Ollama is running and if the model is available
            if provider == "ollama":
                try:
                    # Create temporary client to check for model availability
                    temp_client = ModelAPIFactory.create_client("ollama")
                    available_models = temp_client.get_available_models()
                    model_param = model_config.get("parameters", {}).get("model")
                    
                    if not available_models:
                        print(f"Warning: No Ollama models found. Is Ollama running?")
                        print(f"Please ensure Ollama is installed and running on http://localhost:11434")
                        return None
                    
                    if model_param and model_param not in available_models:
                        print(f"Warning: Model {model_param} not found in Ollama. Available models: {', '.join(available_models)}")
                        print(f"Consider running 'ollama pull {model_param}' to download the model.")
                        return None
                except Exception as e:
                    print(f"Warning: Error checking Ollama availability: {str(e)}")
                    print("Please ensure Ollama is installed and running on http://localhost:11434")
            
            # Create the client
            client = ModelAPIFactory.create_client(provider)
            self.model_clients[model_id] = client
            return client
        
        except Exception as e:
            print(f"Error creating client for model {model_id}: {str(e)}")
            return None
    
    def execute_combinations(
        self,
        combinations: Optional[List[Dict[str, Any]]] = None,
        max_to_execute: Optional[int] = None,
        dry_run: bool = False,
        use_real_models: bool = True
    ) -> Dict[str, Any]:
        """Execute the generated combinations.
        
        Args:
            combinations: Optional list of combinations to execute. If None, uses stored combinations.
            max_to_execute: Optional maximum number of combinations to execute.
            dry_run: If True, just print what would be executed without actually executing.
            use_real_models: If True, uses real model API calls. If False, uses simulation.
            
        Returns:
            Dictionary mapping combination IDs to results.
        """
        combinations = combinations or self.combinations
        
        if max_to_execute and len(combinations) > max_to_execute:
            print(f"Limiting execution to {max_to_execute} out of {len(combinations)} combinations")
            combinations = combinations[:max_to_execute]
        
        if dry_run:
            print(f"Would execute {len(combinations)} combinations")
            for i, combo in enumerate(combinations[:5], 1):
                print(f"{i}. Combination: {combo['id']}")
                if i == 5 and len(combinations) > 5:
                    print(f"... and {len(combinations) - 5} more")
            return {}
        
        results = {}
        
        for i, combo in enumerate(combinations, 1):
            print(f"Executing combination {i}/{len(combinations)}: {combo['id']}")
            
            # Get the components
            template = self.template_library.get_template(combo["template"])
            query_obj = self.query_generator.get_query_by_id(combo["query"])
            domain = self.domain_manager.get_domain(combo["domain"])
            
            # Determine whether to use real API or simulation
            use_api = use_real_models and self.model_configs
            
            if use_api:
                # Use real model API
                result = self._generate_model_response(combo, template, query_obj, domain)
            else:
                # Use simulation
                result = self._simulate_model_response(combo, template, query_obj, domain)
            
            # Store the result
            results[combo["id"]] = result
            self.results[combo["id"]] = result
            
            # Add a small delay between requests to avoid rate limits
            time.sleep(0.2)
        
        print(f"Executed {len(results)} combinations")
        return results
    
    def _generate_model_response(
        self,
        combination: Dict[str, Any],
        template: Any,
        query: Query,
        domain: Domain
    ) -> Dict[str, Any]:
        """Generate a response using the actual model API.
        
        Args:
            combination: Combination dictionary.
            template: Instruction template.
            query: Query object.
            domain: Domain object.
            
        Returns:
            Result dictionary with API response.
        """
        # Format the instruction template
        formatted_instruction = template.format({
            "domain": domain.description,
            **query.variables
        })
        
        # Combine the instruction and query
        prompt = f"{formatted_instruction}\n\n{query.text}"
        
        # Get the model ID and client
        model_id = combination["model"]
        client = self._get_or_create_model_client(model_id)
        template_style = template.metadata.get("cognitive_style", "default")
        
        # Get model parameters from config
        model_params = {}
        if model_id in self.model_configs:
            model_config = self.model_configs[model_id]
            if "parameters" in model_config:
                model_params = model_config["parameters"].copy()
        
        response_text = ""
        start_time = time.time()
        
        try:
            if client:
                # Use the real API client
                print(f"Making real API call to {model_id}...")
                response_text = client.generate(prompt, model_params)
                print(f"Received response from {model_id} (length: {len(response_text)} chars)")
            else:
                # Fall back to simulation if client creation failed
                print(f"Warning: Using simulated response for {model_id} due to missing client")
                return self._simulate_model_response(combination, template, query, domain)
        
        except Exception as e:
            # Handle API errors gracefully
            error_message = str(e)
            print(f"Error calling API for {model_id}: {error_message}")
            response_text = f"Error generating response: {error_message}"
        
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            "combination_id": combination["id"],
            "prompt": prompt,
            "response": response_text,
            "metadata": {
                "model": model_id,
                "template_style": template_style,
                "timestamp": time.time(),
                "duration": duration
            }
        }
    
    def _simulate_model_response(
        self,
        combination: Dict[str, Any],
        template: Any,
        query: Query,
        domain: Domain
    ) -> Dict[str, Any]:
        """Simulate a model response for prototype purposes.
        
        Args:
            combination: Combination dictionary.
            template: Instruction template.
            query: Query object.
            domain: Domain object.
            
        Returns:
            Simulated result dictionary.
        """
        # Format the instruction template
        formatted_instruction = template.format({
            "domain": domain.description,
            **query.variables
        })
        
        # Combine the instruction and query
        prompt = f"{formatted_instruction}\n\n{query.text}"
        
        # For simulation purposes, generate a placeholder response
        model_name = combination["model"]
        template_style = template.metadata.get("cognitive_style", "default")
        
        # Generate a placeholder response based on the components
        response_parts = [
            f"This is a simulated response from {model_name} using the {template_style} approach.",
            f"Domain: {domain.name}",
            f"The query was: {query.text}",
            "Here are some ideas that address this challenge:",
        ]
        
        # Add some random "ideas" based on the domain keywords
        ideas = []
        for i in range(3):
            if domain.keywords:
                keyword = random.choice(domain.keywords)
                ideas.append(f"Idea {i+1}: A solution involving {keyword} that addresses the core challenge.")
            else:
                ideas.append(f"Idea {i+1}: A novel approach to solving this problem.")
        
        response_parts.extend(ideas)
        
        # Create a simulation of a conclusion
        response_parts.append(f"These ideas represent a {template_style} approach to the problem within the {domain.name} domain.")
        
        # Join the parts
        response_text = "\n\n".join(response_parts)
        
        return {
            "combination_id": combination["id"],
            "prompt": prompt,
            "response": response_text,
            "metadata": {
                "model": model_name,
                "template_style": template_style,
                "timestamp": time.time(),
                "simulated": True
            }
        }
    
    def evaluate_results(
        self, 
        results: Optional[Dict[str, Any]] = None,
        criteria: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, float]]:
        """Evaluate the results against the scoring criteria.
        
        Args:
            results: Optional dictionary of results to evaluate. If None, uses stored results.
            criteria: Optional list of criteria to evaluate against. If None, uses all criteria.
            
        Returns:
            Dictionary mapping combination IDs to evaluation scores.
        """
        results = results or self.results
        
        if not results:
            print("No results to evaluate")
            return {}
        
        evaluations = {}
        
        for combo_id, result in results.items():
            text = result["response"]
            
            # Score the text
            scores = self.scoring_framework.score_text(text)
            
            if criteria:
                # Filter to only the requested criteria
                scores = {k: v for k, v in scores.items() if k in criteria}
            
            # Calculate the overall score
            overall = self.scoring_framework.calculate_weighted_score(scores)
            scores["overall"] = overall
            
            # Store the scores
            evaluations[combo_id] = scores
            self.evaluations[combo_id] = scores
        
        print(f"Evaluated {len(evaluations)} results")
        return evaluations
    
    def get_top_results(
        self, 
        criterion: str = "overall", 
        n: int = 10
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Get the top N results based on a specific criterion.
        
        Args:
            criterion: The criterion to sort by.
            n: Number of top results to return.
            
        Returns:
            List of (result, score) tuples sorted by the criterion in descending order.
        """
        if not self.evaluations or not self.results:
            print("No evaluated results to rank")
            return []
        
        # Pair results with their scores
        scored_results = []
        for combo_id, evaluation in self.evaluations.items():
            if criterion in evaluation and combo_id in self.results:
                score = evaluation[criterion]
                result = self.results[combo_id]
                scored_results.append((result, score))
        
        # Sort by score in descending order
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        # Return the top N
        return scored_results[:n]
    
    def synthesize_ideas(
        self, 
        top_results: Optional[List[Tuple[Dict[str, Any], float]]] = None,
        method: str = "cluster_based"
    ) -> Dict[str, Any]:
        """Synthesize ideas from the top results.
        
        Args:
            top_results: Optional list of (result, score) tuples. If None, gets top results automatically.
            method: Method to use for synthesis (cluster_based, cross_pollination, etc.).
            
        Returns:
            Dictionary of synthesized ideas.
        """
        if top_results is None:
            top_results = self.get_top_results(n=10)
        
        if not top_results:
            print("No results to synthesize")
            return {}
        
        print(f"Synthesizing ideas from {len(top_results)} top results using {method} method")
        
        # In a real implementation, this would use sophisticated NLP techniques
        # For prototype purposes, we'll just create placeholder synthesized ideas
        synthesized = {}
        
        if method == "cluster_based":
            # Simulate clustering into 3 groups
            clusters = [
                top_results[:len(top_results)//3],
                top_results[len(top_results)//3:2*len(top_results)//3],
                top_results[2*len(top_results)//3:]
            ]
            
            for i, cluster in enumerate(clusters, 1):
                if not cluster:
                    continue
                
                # Create a synthesized idea from this cluster
                idea_id = f"synthesized_idea_{i}"
                
                # Extract information from the results in this cluster
                result_texts = [result["response"] for result, _ in cluster]
                combined_text = "\n\n".join(result_texts)
                
                # Group source combinations by model
                model_contributions = {}
                for result, _ in cluster:
                    model_id = result["metadata"]["model"]
                    model_contributions.setdefault(model_id, 0)
                    model_contributions[model_id] += 1
                
                # Calculate percentage contributions from each model
                total_contributions = sum(model_contributions.values())
                model_percentages = {model: (count / total_contributions) * 100 
                                     for model, count in model_contributions.items()}
                
                # In a real implementation, this would analyze and synthesize the texts
                # For prototype purposes, we'll just create a placeholder
                response_texts = [result["response"] for result, _ in cluster]
                
                # Use the first response's text if available, or create a summary
                if response_texts and len(response_texts[0]) > 0:
                    # Extract a title from the first response
                    lines = response_texts[0].split('\n')
                    title_candidate = next((line for line in lines if len(line) > 5 and len(line) < 80), f"Synthesized Idea {i}")
                    
                    synthesized_idea = {
                        "id": idea_id,
                        "title": title_candidate[:80],  # Use a portion of the first meaningful line as title
                        "description": f"This idea represents a synthesis of {len(cluster)} top-ranked responses.",
                        "source_combinations": [result["combination_id"] for result, _ in cluster],
                        "text": response_texts[0],  # Use the actual response text
                        "metadata": {
                            "method": method,
                            "cluster_id": i,
                            "cluster_size": len(cluster),
                            "average_score": sum(score for _, score in cluster) / len(cluster),
                            "model_contributions": model_contributions,
                            "model_percentages": model_percentages
                        }
                    }
                else:
                    # Fallback to placeholder if no response text is available
                    synthesized_idea = {
                        "id": idea_id,
                        "title": f"Synthesized Idea {i}",
                        "description": f"This idea represents a synthesis of {len(cluster)} top-ranked responses.",
                        "source_combinations": [result["combination_id"] for result, _ in cluster],
                        "text": f"Synthesized text would extract the common themes and innovative elements from cluster {i}.",
                        "metadata": {
                            "method": method,
                            "cluster_id": i,
                            "cluster_size": len(cluster),
                            "average_score": sum(score for _, score in cluster) / len(cluster),
                            "model_contributions": model_contributions,
                            "model_percentages": model_percentages
                        }
                    }
                
                synthesized[idea_id] = synthesized_idea
        
        elif method == "cross_pollination":
            # Simulate cross-pollination by combining elements from top results
            idea_id = "synthesized_idea_crossover"
            
            synthesized_idea = {
                "id": idea_id,
                "title": "Cross-Pollinated Innovation",
                "description": f"This idea combines elements from {len(top_results)} diverse top-ranked responses.",
                "source_combinations": [result["combination_id"] for result, _ in top_results],
                "text": "Cross-pollinated text would extract complementary elements from different responses and combine them in novel ways.",
                "metadata": {
                    "method": method,
                    "sources_count": len(top_results),
                    "average_score": sum(score for _, score in top_results) / len(top_results)
                }
            }
            
            synthesized[idea_id] = synthesized_idea
        
        else:
            print(f"Unknown synthesis method: {method}")
        
        # Store the synthesized ideas
        self.synthesized_ideas.update(synthesized)
        
        print(f"Synthesized {len(synthesized)} ideas")
        return synthesized
    
    def format_output(
        self, 
        ideas: Optional[Dict[str, Any]] = None, 
        format_type: str = "markdown"
    ) -> str:
        """Format the synthesized ideas for output.
        
        Args:
            ideas: Optional dictionary of ideas to format. If None, uses stored synthesized ideas.
            format_type: Output format type (markdown, json, etc.).
            
        Returns:
            Formatted output string.
        """
        ideas = ideas or self.synthesized_ideas
        
        if not ideas:
            return "No synthesized ideas to format"
        
        if format_type == "markdown":
            output = "# Synthesized Ideas\n\n"
            
            for idea_id, idea in ideas.items():
                output += f"## {idea['title']}\n\n"
                output += f"{idea['description']}\n\n"
                output += f"### Key Points\n\n"
                output += f"{idea['text']}\n\n"
                
                if "metadata" in idea:
                    output += "### Metadata\n\n"
                    
                    # Special handling for model contributions
                    if "model_contributions" in idea["metadata"]:
                        output += "#### Model Contributions\n\n"
                        model_contributions = idea["metadata"]["model_contributions"]
                        for model_id, count in model_contributions.items():
                            model_name = "Unknown"
                            if model_id in self.model_configs:
                                model_name = self.model_configs[model_id].get("name", model_id)
                            
                            percentage = idea["metadata"]["model_percentages"][model_id]
                            output += f"- **{model_name}**: {count} responses ({percentage:.1f}%)\n"
                        
                        output += "\n"
                        
                        # Remove these keys so we don't display them again in the general metadata
                        metadata_display = {k: v for k, v in idea["metadata"].items() 
                                           if k not in ["model_contributions", "model_percentages"]}
                    else:
                        metadata_display = idea["metadata"]
                    
                    # Display remaining metadata
                    output += "#### Additional Metadata\n\n"
                    for key, value in metadata_display.items():
                        output += f"- **{key}**: {value}\n"
                
                output += "\n---\n\n"
            
            return output
        
        elif format_type == "json":
            return json.dumps(ideas, indent=2)
        
        else:
            print(f"Unknown format type: {format_type}")
            return json.dumps(ideas, indent=2)
    
    def run_complete_pipeline(
        self,
        query_text: str,
        domain_name: Optional[str] = None,
        model_count: int = 2,
        instruction_count: int = 3,
        query_variations: int = 2,
        max_combinations: Optional[int] = 10,
        output_format: str = "markdown",
        use_real_models: bool = True,
        balanced_models: bool = False
    ) -> str:
        """Run the complete ISEE pipeline from query to synthesized ideas.
        
        Args:
            query_text: The input query text.
            domain_name: Optional domain name to focus on.
            model_count: Number of models to use.
            instruction_count: Number of instructions to use.
            query_variations: Number of query variations to generate.
            max_combinations: Maximum number of combinations to execute.
            output_format: Output format type.
            use_real_models: If True, uses real model API calls. If False, uses simulation.
            balanced_models: If True, ensure balanced representation of models in the combinations.
            
        Returns:
            Formatted output of synthesized ideas.
        """
        print(f"Running complete pipeline for query: {query_text}")
        
        # 1. Create a new query
        from uuid import uuid4
        query_id = f"query_{str(uuid4())[:8]}"
        query = Query(id=query_id, text=query_text)
        self.query_generator.add_base_query(query)
        
        # 2. Determine domains
        domain_ids = None
        if domain_name:
            matching_domains = self.domain_manager.search_domains(domain_name)
            if matching_domains:
                domain_ids = [domain.id for domain in matching_domains]
                print(f"Found {len(domain_ids)} matching domains for '{domain_name}'")
            else:
                print(f"No domains found matching '{domain_name}', using all domains")
        
        # 3. Generate combinations
        combinations = self.generate_combinations(
            query_id=query_id,
            domain_ids=domain_ids,
            model_count=model_count,
            instruction_count=instruction_count,
            query_variations=query_variations,
            balanced=balanced_models
        )
        
        # 4. Execute combinations
        results = self.execute_combinations(
            combinations=combinations,
            max_to_execute=max_combinations,
            use_real_models=use_real_models
        )
        
        # 5. Evaluate results
        evaluations = self.evaluate_results(results=results)
        
        # 6. Get top results
        top_results = self.get_top_results(n=min(10, len(evaluations)))
        
        # 7. Synthesize ideas
        synthesized = self.synthesize_ideas(top_results=top_results)
        
        # 8. Format output
        output = self.format_output(ideas=synthesized, format_type=output_format)
        
        print("Pipeline execution complete")
        return output


def main():
    """Main entry point for the application."""
    # Check if API keys are available
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    # Check Ollama availability
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
    if anthropic_key:
        api_status.append("Anthropic API key found")
    if openai_key:
        api_status.append("OpenAI API key found")
    if ollama_available:
        api_status.append(f"Ollama available with {len(ollama_models)} models")
    
    if api_status:
        print(f"API Status: {', '.join(api_status)}")
        print("Real model API calls can be used. Use --simulate to use simulation instead.")
        
        # Show Ollama models if available
        if ollama_available:
            print(f"\nAvailable Ollama models: {', '.join(ollama_models)}")
            
    else:
        print("API Status: No API providers found.")
        print("Options:")
        print("1. Create a .env file with ANTHROPIC_API_KEY and/or OPENAI_API_KEY")
        print("2. Install Ollama (https://ollama.com) and run 'ollama serve'")
        print("3. Use --simulate to run with simulation mode")
    print()
    
    parser = argparse.ArgumentParser(description="Idea Synthesis and Extraction Engine")
    
    # Main commands
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--save-state", help="Save application state to file")
    parser.add_argument("--load-state", help="Load application state from file")
    
    # Pipeline parameters
    parser.add_argument("--query", help="Input query text")
    parser.add_argument("--domain", help="Domain to focus on")
    parser.add_argument("--models", type=int, default=2, help="Number of models to use (set to a higher number to include more models)")
    parser.add_argument("--use-ollama", action="store_true", help="Include Ollama models in the model selection")
    parser.add_argument("--instructions", type=int, default=3, help="Number of instructions to use")
    parser.add_argument("--variations", type=int, default=2, help="Number of query variations to generate")
    parser.add_argument("--max-combinations", type=int, help="Maximum number of combinations to execute")
    parser.add_argument("--output-format", choices=["markdown", "json"], default="markdown", help="Output format")
    parser.add_argument("--output-file", help="Path to save the output to")
    parser.add_argument("--simulate", action="store_true", help="Use simulated responses instead of real model APIs")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be executed without actually running")
    parser.add_argument("--balanced-models", action="store_true", help="Ensure balanced representation of models in the executed combinations")
    parser.add_argument("--synthesize-method", choices=["cluster_based", "cross_pollination"], default="cluster_based", 
                        help="Method to use for synthesizing ideas (cluster_based or cross_pollination)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize the application
    app = ISEEApplication(config_path=args.config)
    
    # Load state if requested
    if args.load_state:
        app.load_state(args.load_state)
        
        # If synthesize-method is provided without a query, just synthesize from loaded state
        if args.synthesize_method and not args.query:
            top_results = app.get_top_results(n=10)
            if top_results:
                synthesized = app.synthesize_ideas(top_results=top_results, method=args.synthesize_method)
                output = app.format_output(ideas=synthesized, format_type=args.output_format)
                
                if args.output_file:
                    with open(args.output_file, 'w') as f:
                        f.write(output)
                    print(f"Output saved to {args.output_file}")
                else:
                    print("\nOutput:")
                    print("=" * 80)
                    print(output)
                    
                # Save state if requested
                if args.save_state:
                    app.save_state(args.save_state)
                    
                # Exit after synthesis
                return
    
    # Determine if we should use simulation mode
    use_simulation = args.simulate
    if not use_simulation and not (anthropic_key or openai_key):
        print("No API keys available. Forcing simulation mode.")
        use_simulation = True
    
    # Run pipeline if query is provided
    if args.query:
        # If dry run is specified, just print what would be executed
        if args.dry_run:
            combinations = app.generate_combinations(
                query_id=app.query_generator.list_base_queries()[0].id,
                model_count=args.models,
                instruction_count=args.instructions,
                query_variations=args.variations
            )
            app.execute_combinations(
                combinations=combinations,
                max_to_execute=args.max_combinations,
                dry_run=True
            )
        else:
            output = app.run_complete_pipeline(
                query_text=args.query,
                domain_name=args.domain,
                model_count=args.models,
                instruction_count=args.instructions,
                query_variations=args.variations,
                max_combinations=args.max_combinations,
                output_format=args.output_format,
                use_real_models=not use_simulation,
                balanced_models=args.balanced_models
            )
            
            # Apply custom synthesis method if specified
            if args.synthesize_method and args.synthesize_method != "cluster_based":
                print(f"Applying {args.synthesize_method} synthesis method...")
                top_results = app.get_top_results(n=10)
                if top_results:
                    synthesized = app.synthesize_ideas(top_results=top_results, method=args.synthesize_method)
                    output = app.format_output(ideas=synthesized, format_type=args.output_format)
        
        # Print or save the output if not a dry run
        if not args.dry_run:
            if args.output_file:
                with open(args.output_file, 'w') as f:
                    f.write(output)
                print(f"Output saved to {args.output_file}")
            else:
                print("\nOutput:")
                print("=" * 80)
                print(output)
    
    # Save state if requested
    if args.save_state:
        app.save_state(args.save_state)


if __name__ == "__main__":
    main()