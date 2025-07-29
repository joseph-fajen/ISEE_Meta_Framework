"""
Instruction Templates Module for ISEE Framework

This module provides a library of instruction templates that can be used to diversify
the cognitive approaches applied to a given problem.
"""

from typing import Dict, Any, List, Optional
import json
import os

class InstructionTemplate:
    """Represents a system prompt or instruction framework."""
    
    def __init__(self, id: str, name: str, template: str, metadata: Optional[Dict[str, Any]] = None):
        """Initialize an instruction template.
        
        Args:
            id: Unique identifier for the template.
            name: Human-readable name for the template.
            template: The template string with placeholders for variables.
            metadata: Optional metadata about the template, such as cognitive style.
        """
        self.id = id
        self.name = name
        self.template = template
        self.metadata = metadata or {}
    
    def format(self, variables: Dict[str, Any]) -> str:
        """Format the template with the provided variables.
        
        Args:
            variables: Dictionary of variables to substitute into the template.
            
        Returns:
            The formatted template string.
        """
        try:
            return self.template.format(**variables)
        except KeyError as e:
            missing_key = str(e).strip("'")
            raise ValueError(f"Missing required variable '{missing_key}' for template '{self.name}'")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the template to a dictionary representation.
        
        Returns:
            Dictionary representation of the template.
        """
        return {
            "id": self.id,
            "name": self.name,
            "template": self.template,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InstructionTemplate':
        """Create a template from a dictionary representation.
        
        Args:
            data: Dictionary representation of the template.
            
        Returns:
            A new InstructionTemplate instance.
        """
        return cls(
            id=data["id"],
            name=data["name"],
            template=data["template"],
            metadata=data.get("metadata", {})
        )


class TemplateLibrary:
    """Manages a collection of instruction templates."""
    
    def __init__(self):
        """Initialize an empty template library."""
        self.templates: Dict[str, InstructionTemplate] = {}
    
    def add_template(self, template: InstructionTemplate) -> None:
        """Add a template to the library.
        
        Args:
            template: The template to add.
            
        Raises:
            ValueError: If a template with the same ID already exists.
        """
        if template.id in self.templates:
            raise ValueError(f"Template with ID '{template.id}' already exists")
        
        self.templates[template.id] = template
    
    def get_template(self, template_id: str) -> InstructionTemplate:
        """Get a template by ID.
        
        Args:
            template_id: The ID of the template to get.
            
        Returns:
            The requested template.
            
        Raises:
            KeyError: If no template with the given ID exists.
        """
        if template_id not in self.templates:
            raise KeyError(f"No template with ID '{template_id}' exists")
        
        return self.templates[template_id]
    
    def list_templates(self) -> List[InstructionTemplate]:
        """List all templates in the library.
        
        Returns:
            List of all templates.
        """
        return list(self.templates.values())
    
    def filter_templates(self, metadata_key: str, metadata_value: Any) -> List[InstructionTemplate]:
        """Filter templates by metadata.
        
        Args:
            metadata_key: The metadata key to filter on.
            metadata_value: The value the metadata key should have.
            
        Returns:
            List of templates matching the filter.
        """
        return [
            template for template in self.templates.values()
            if template.metadata.get(metadata_key) == metadata_value
        ]
    
    def load_from_file(self, file_path: str) -> None:
        """Load templates from a JSON file.
        
        Args:
            file_path: Path to the JSON file containing templates.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
            KeyError: If the file does not contain a 'templates' key.
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        templates_data = data.get("templates") or data.get("instructions")
        if not templates_data:
            raise KeyError("File does not contain 'templates' or 'instructions' key")
        
        for template_data in templates_data:
            template = InstructionTemplate.from_dict(template_data)
            self.add_template(template)
    
    def save_to_file(self, file_path: str) -> None:
        """Save templates to a JSON file.
        
        Args:
            file_path: Path to save the templates to.
        """
        templates_data = [template.to_dict() for template in self.templates.values()]
        data = {"templates": templates_data}
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)


# Default templates library
def create_default_library() -> TemplateLibrary:
    """Create a library with default instruction templates.
    
    Returns:
        A template library populated with default templates.
    """
    library = TemplateLibrary()
    
    # Analytical Framework
    analytical = InstructionTemplate(
        id="ins_analytical",
        name="Analytical Framework",
        template=(
            "You are an expert analyst specializing in {domain}. Approach the following "
            "question with careful analysis, systematic thinking, and evidence-based reasoning. "
            "Consider multiple perspectives, identify potential challenges, and evaluate trade-offs. "
            "Focus on creating a structured, logical response."
        ),
        metadata={
            "cognitive_style": "analytical",
            "strength": "structured reasoning"
        }
    )
    library.add_template(analytical)
    
    # Creative Framework - Enhanced for Radical Innovation
    creative = InstructionTemplate(
        id="ins_creative",
        name="Creative Framework",
        template=(
            "You are a radical creative innovator specializing in {domain}. Challenge every "
            "assumption about how things should work in this field. Ask 'What if we didn't need "
            "[current solution]?' Design solutions that would make existing approaches completely "
            "obsolete. Focus on breakthrough thinking that creates entirely new categories of "
            "solutions. Combine unexpected elements from other fields to reimagine {domain} from scratch."
        ),
        metadata={
            "cognitive_style": "divergent",
            "strength": "paradigm-shifting innovation",
            "innovation_focus": True
        }
    )
    library.add_template(creative)
    
    # Critical Framework
    critical = InstructionTemplate(
        id="ins_critical",
        name="Critical Framework",
        template=(
            "You are a critical thinker specializing in {domain}. Approach the following "
            "question by challenging assumptions, identifying potential flaws, and considering counterarguments. "
            "Focus on rigorously evaluating ideas rather than accepting them at face value. "
            "Identify hidden constraints, unstated assumptions, and potential negative consequences."
        ),
        metadata={
            "cognitive_style": "critical",
            "strength": "assumption challenging"
        }
    )
    library.add_template(critical)
    
    # Integrative Framework
    integrative = InstructionTemplate(
        id="ins_integrative",
        name="Integrative Framework",
        template=(
            "You are an expert in integrative thinking specializing in {domain}. Approach the following "
            "question by synthesizing diverse perspectives, reconciling apparent contradictions, and creating holistic solutions. "
            "Focus on finding the connections between different disciplines and frameworks. "
            "Consider how various stakeholders might contribute to a comprehensive solution."
        ),
        metadata={
            "cognitive_style": "integrative",
            "strength": "synthesis"
        }
    )
    library.add_template(integrative)
    
    # Pragmatic Framework
    pragmatic = InstructionTemplate(
        id="ins_pragmatic",
        name="Pragmatic Framework",
        template=(
            "You are a pragmatic problem-solver specializing in {domain}. Approach the following "
            "question with a focus on practical implementation, resource constraints, and real-world feasibility. "
            "Focus on creating solutions that can be readily applied and that address immediate needs. "
            "Consider ease of adoption, cost-effectiveness, and scalability."
        ),
        metadata={
            "cognitive_style": "pragmatic",
            "strength": "implementation focus"
        }
    )
    library.add_template(pragmatic)
    
    # First Principles Framework - Enhanced for Breakthrough Innovation
    first_principles = InstructionTemplate(
        id="ins_first_principles",
        name="First Principles Framework",
        template=(
            "You are a radical first principles innovator specializing in {domain}. Break the "
            "challenge down to its most basic elements, then recombine these elements in ways "
            "never attempted before. Ignore all existing solution patterns and build something "
            "completely new from the fundamentals. Question why things exist in their current "
            "form and design from the ground up as if the field were being invented today."
        ),
        metadata={
            "cognitive_style": "reductive",
            "strength": "ground-up innovation",
            "innovation_focus": True
        }
    )
    library.add_template(first_principles)
    
    # Systems Thinking Framework
    systems_thinking = InstructionTemplate(
        id="ins_systems",
        name="Systems Thinking Framework",
        template=(
            "You are a systems thinker specializing in {domain}. Approach the following "
            "question by considering the whole ecosystem of interrelated components. "
            "Focus on identifying feedback loops, emergent properties, and non-linear relationships. "
            "Consider how interventions in one part of the system might affect other parts, "
            "both immediately and over time."
        ),
        metadata={
            "cognitive_style": "systems",
            "strength": "holistic analysis"
        }
    )
    library.add_template(systems_thinking)
    
    # Contrarian Framework - Enhanced for Assumption-Breaking
    contrarian = InstructionTemplate(
        id="ins_contrarian",
        name="Contrarian Framework",
        template=(
            "You are a radical contrarian innovator specializing in {domain}. Identify the 3 most "
            "fundamental assumptions everyone makes about this field. Now design solutions that "
            "prove these assumptions completely wrong. What would {domain} look like if the opposite "
            "of conventional wisdom were true? Challenge not just approaches, but the underlying "
            "premises that define the entire problem space."
        ),
        metadata={
            "cognitive_style": "contrarian",
            "strength": "assumption demolition",
            "innovation_focus": True
        }
    )
    library.add_template(contrarian)
    
    # Historical Framework
    historical = InstructionTemplate(
        id="ins_historical",
        name="Historical Framework",
        template=(
            "You are a historical analyst specializing in {domain}. Approach the following "
            "question by examining relevant historical precedents and patterns. "
            "Consider how similar challenges have been addressed in the past, what succeeded, "
            "what failed, and why. Extract lessons and principles that might apply to the current situation."
        ),
        metadata={
            "cognitive_style": "historical",
            "strength": "pattern recognition"
        }
    )
    library.add_template(historical)
    
    # Future-Oriented Framework
    futurist = InstructionTemplate(
        id="ins_futurist",
        name="Future-Oriented Framework",
        template=(
            "You are a futurist specializing in {domain}. Approach the following "
            "question by considering long-term trends, emerging technologies, and potential "
            "paradigm shifts. Focus on anticipating how the context might change over time "
            "and creating solutions that remain relevant or adapt to evolving conditions."
        ),
        metadata={
            "cognitive_style": "futurist",
            "strength": "trend extrapolation"
        }
    )
    library.add_template(futurist)
    
    # Disruption Framework - New 11th Framework for Maximum Innovation
    disruption = InstructionTemplate(
        id="ins_disruption",
        name="Disruption Framework",
        template=(
            "You are a strategic innovation expert specializing in {domain}. Identify promising "
            "alternative approaches that could significantly improve upon current solutions. Focus "
            "on breakthrough innovations that challenge conventional thinking while remaining "
            "implementable in the current market environment. What emerging technologies, changing "
            "behaviors, or new business models could create 2-5x improvements?"
        ),
        metadata={
            "cognitive_style": "disruptive",
            "strength": "industry transformation",
            "innovation_focus": True
        }
    )
    library.add_template(disruption)
    
    return library


# Example usage
if __name__ == "__main__":
    # Create a default library
    library = create_default_library()
    
    # Print all available templates
    print(f"Available templates ({len(library.templates)}):")
    for template in library.list_templates():
        print(f"- {template.name} ({template.id})")
        print(f"  Cognitive Style: {template.metadata.get('cognitive_style', 'N/A')}")
        print(f"  Strength: {template.metadata.get('strength', 'N/A')}")
        print()
    
    # Example of using a template
    domain = "artificial intelligence ethics"
    template = library.get_template("ins_analytical")
    formatted = template.format({"domain": domain})
    
    print("Example formatted template:")
    print(formatted)
    
    # Save templates to file
    os.makedirs("data", exist_ok=True)
    library.save_to_file("data/instruction_templates.json")
    print("\nTemplates saved to data/instruction_templates.json")
