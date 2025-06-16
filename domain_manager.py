"""
Domain Manager Module for ISEE Framework

This module provides functionality for managing different application domains
that can be used to contextualize query generation and idea evaluation.
"""

import json
from typing import Dict, Any, List, Optional, Set
from uuid import uuid4

class Domain:
    """Represents a specific application domain."""
    
    def __init__(
        self, 
        id: str, 
        name: str, 
        description: str, 
        keywords: Optional[List[str]] = None
    ):
        """Initialize a domain.
        
        Args:
            id: Unique identifier for the domain.
            name: Human-readable name for the domain.
            description: Description of the domain.
            keywords: Optional list of keywords associated with the domain.
        """
        self.id = id
        self.name = name
        self.description = description
        self.keywords = keywords or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary representation.
        
        Returns:
            Dictionary representation of the domain.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "keywords": self.keywords
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Domain':
        """Create a domain from a dictionary representation.
        
        Args:
            data: Dictionary representation of the domain.
            
        Returns:
            A new Domain instance.
        """
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            keywords=data.get("keywords", [])
        )


class DomainManager:
    """Manages a collection of application domains."""
    
    def __init__(self):
        """Initialize an empty domain manager."""
        self.domains: Dict[str, Domain] = {}
    
    def add_domain(self, domain: Domain) -> None:
        """Add a domain to the manager.
        
        Args:
            domain: The domain to add.
            
        Raises:
            ValueError: If a domain with the same ID already exists.
        """
        if domain.id in self.domains:
            raise ValueError(f"Domain with ID '{domain.id}' already exists")
        
        self.domains[domain.id] = domain
    
    def get_domain(self, domain_id: str) -> Domain:
        """Get a domain by ID.
        
        Args:
            domain_id: The ID of the domain to get.
            
        Returns:
            The requested domain.
            
        Raises:
            KeyError: If no domain with the given ID exists.
        """
        if domain_id not in self.domains:
            raise KeyError(f"No domain with ID '{domain_id}' exists")
        
        return self.domains[domain_id]
    
    def list_domains(self) -> List[Domain]:
        """List all domains.
        
        Returns:
            List of all domains.
        """
        return list(self.domains.values())
    
    def search_domains(self, query: str) -> List[Domain]:
        """Search domains by name, description, or keywords.
        
        Args:
            query: The search query.
            
        Returns:
            List of matching domains.
        """
        query = query.lower()
        matches = []
        
        for domain in self.domains.values():
            # Check name
            if query in domain.name.lower():
                matches.append(domain)
                continue
            
            # Check description
            if query in domain.description.lower():
                matches.append(domain)
                continue
            
            # Check keywords
            if any(query in keyword.lower() for keyword in domain.keywords):
                matches.append(domain)
                continue
        
        return matches
    
    def load_from_file(self, file_path: str) -> None:
        """Load domains from a JSON file.
        
        Args:
            file_path: Path to the JSON file containing domains.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
            KeyError: If the file does not contain a 'domains' key.
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        domains_data = data.get('domains')
        if not domains_data:
            raise KeyError("File does not contain 'domains' key")
        
        for domain_data in domains_data:
            domain = Domain.from_dict(domain_data)
            self.add_domain(domain)
    
    def save_to_file(self, file_path: str) -> None:
        """Save domains to a JSON file.
        
        Args:
            file_path: Path to save the domains to.
        """
        domains_data = [domain.to_dict() for domain in self.domains.values()]
        data = {'domains': domains_data}
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_domain(
        self, 
        name: str, 
        description: str, 
        keywords: Optional[List[str]] = None,
        id: Optional[str] = None
    ) -> Domain:
        """Create and add a new domain.
        
        Args:
            name: Name of the domain.
            description: Description of the domain.
            keywords: Optional list of keywords.
            id: Optional ID (generated if not provided).
            
        Returns:
            The created domain.
            
        Raises:
            ValueError: If a domain with the same ID already exists.
        """
        # Generate ID if not provided
        if id is None:
            # Create a slug from the name
            slug = name.lower().replace(' ', '_')
            id = f"domain_{slug}_{str(uuid4())[:8]}"
        
        # Create the domain
        domain = Domain(
            id=id,
            name=name,
            description=description,
            keywords=keywords
        )
        
        # Add it to the manager
        self.add_domain(domain)
        
        return domain
    
    def delete_domain(self, domain_id: str) -> bool:
        """Delete a domain by ID.
        
        Args:
            domain_id: ID of the domain to delete.
            
        Returns:
            True if the domain was deleted, False if it didn't exist.
        """
        if domain_id in self.domains:
            del self.domains[domain_id]
            return True
        
        return False
    
    def get_related_domains(self, domain_id: str, min_matches: int = 2) -> List[Domain]:
        """Get domains related to the given domain based on keyword overlap.
        
        Args:
            domain_id: ID of the domain to find related domains for.
            min_matches: Minimum number of matching keywords required.
            
        Returns:
            List of related domains.
            
        Raises:
            KeyError: If no domain with the given ID exists.
        """
        if domain_id not in self.domains:
            raise KeyError(f"No domain with ID '{domain_id}' exists")
        
        source_domain = self.domains[domain_id]
        related = []
        
        # Skip if the source domain has no keywords
        if not source_domain.keywords:
            return []
        
        source_keywords = set(k.lower() for k in source_domain.keywords)
        
        for other_id, other_domain in self.domains.items():
            if other_id == domain_id:
                continue
            
            other_keywords = set(k.lower() for k in other_domain.keywords)
            matches = source_keywords.intersection(other_keywords)
            
            if len(matches) >= min_matches:
                related.append(other_domain)
        
        return related


def create_default_domains() -> List[Domain]:
    """Create a set of default domains.
    
    Returns:
        List of default domains.
    """
    defaults = [
        # Core Domains
        Domain(
            id="domain_urban_planning",
            name="Urban Planning",
            description="The interdisciplinary field concerned with the development of urban areas, including transportation systems, land use, and public spaces.",
            keywords=["urban planning", "city development", "urban design", "transportation", "mobility", "land use", "zoning", "public spaces", "infrastructure"]
        ),
        Domain(
            id="domain_education",
            name="Education",
            description="The field focused on teaching and learning processes, educational systems, and pedagogy across various age groups and contexts.",
            keywords=["education", "learning", "teaching", "pedagogy", "curriculum", "schools", "universities", "educational technology", "e-learning"]
        ),
        Domain(
            id="domain_healthcare",
            name="Healthcare",
            description="The organized provision of medical care to individuals or communities, including prevention, diagnosis, treatment, and management of illness.",
            keywords=["healthcare", "medicine", "public health", "medical care", "wellness", "disease prevention", "telehealth", "health systems", "patient care"]
        ),
        Domain(
            id="domain_sustainability",
            name="Sustainability",
            description="The study and practice of meeting human needs without compromising the ability of future generations to meet their own needs.",
            keywords=["sustainability", "environment", "climate change", "renewable energy", "conservation", "green technology", "circular economy", "eco-friendly"]
        ),
        Domain(
            id="domain_technology",
            name="Technology Innovation",
            description="The field focused on developing and implementing new technologies to solve existing problems and create new possibilities.",
            keywords=["technology", "innovation", "digital transformation", "emerging tech", "smart systems", "artificial intelligence", "IoT", "blockchain", "robotics"]
        ),
        
        # Technical Writing Domains
        Domain(
            id="domain_technical_writing",
            name="Technical Documentation",
            description="The creation of clear, accurate, and useful documentation for complex technical subjects, processes, and products.",
            keywords=["technical writing", "documentation", "user manuals", "API docs", "technical communication", "software documentation", "process documentation"]
        ),
        Domain(
            id="domain_knowledge_management",
            name="Knowledge Management",
            description="The systematic approach to capturing, developing, sharing, and effectively using organizational knowledge and information.",
            keywords=["knowledge management", "information systems", "knowledge base", "wiki", "documentation systems", "organizational learning", "knowledge sharing"]
        ),
        Domain(
            id="domain_content_strategy",
            name="Content Strategy",
            description="The planning, development, and management of content across various platforms and channels to achieve business objectives.",
            keywords=["content strategy", "content marketing", "content planning", "editorial strategy", "content management", "digital content", "content governance"]
        ),
        Domain(
            id="domain_ai_writing",
            name="AI-Assisted Writing",
            description="The integration of artificial intelligence tools and techniques to enhance writing processes, creativity, and productivity.",
            keywords=["AI writing", "automated writing", "writing assistance", "content generation", "natural language processing", "writing tools", "AI content"]
        ),
        Domain(
            id="domain_developer_docs",
            name="Developer Documentation",
            description="The creation and maintenance of technical documentation specifically for software developers, including APIs, SDKs, and code examples.",
            keywords=["developer documentation", "API documentation", "code examples", "SDK documentation", "programming guides", "technical reference", "developer experience"]
        ),
        
        # Learning Design Domains
        Domain(
            id="domain_instructional_design",
            name="Instructional Design",
            description="The systematic design of educational experiences and materials to facilitate effective learning and skill development.",
            keywords=["instructional design", "learning design", "curriculum development", "educational design", "training materials", "learning objectives", "assessment design"]
        ),
        Domain(
            id="domain_elearning",
            name="E-learning Design",
            description="The design and development of digital learning experiences, including online courses, interactive modules, and educational technology.",
            keywords=["e-learning", "online learning", "digital education", "LMS", "educational technology", "interactive learning", "distance learning"]
        ),
        Domain(
            id="domain_learning_experience",
            name="Learning Experience Design",
            description="The holistic approach to designing meaningful, effective, and engaging learning experiences that consider learner needs and contexts.",
            keywords=["learning experience design", "learner-centered design", "user experience", "learning journey", "educational UX", "learner engagement", "experience design"]
        ),
        Domain(
            id="domain_corporate_training",
            name="Corporate Training",
            description="The development and delivery of professional development programs and training initiatives within organizational contexts.",
            keywords=["corporate training", "professional development", "workplace learning", "employee training", "skill development", "organizational learning", "training programs"]
        ),
        Domain(
            id="domain_assessment_design",
            name="Assessment Design",
            description="The creation of effective assessment methods and tools to measure learning outcomes, skills, and competencies.",
            keywords=["assessment design", "evaluation", "testing", "learning assessment", "formative assessment", "summative assessment", "competency assessment"]
        )
    ]
    
    return defaults


# Example usage
if __name__ == "__main__":
    # Create a domain manager
    manager = DomainManager()
    
    # Add default domains
    for domain in create_default_domains():
        manager.add_domain(domain)
    
    # Print all domains
    print(f"Available domains ({len(manager.domains)}):")
    for domain in manager.list_domains():
        print(f"- {domain.name} ({domain.id})")
        print(f"  Description: {domain.description}")
        print(f"  Keywords: {', '.join(domain.keywords)}")
        print()
    
    # Search for domains
    search_term = "technology"
    results = manager.search_domains(search_term)
    print(f"Search results for '{search_term}':")
    for domain in results:
        print(f"- {domain.name}")
    
    # Get related domains
    related = manager.get_related_domains("domain_urban_planning")
    print("\nDomains related to Urban Planning:")
    for domain in related:
        print(f"- {domain.name}")
    
    # Save to a file
    import os
    os.makedirs("data", exist_ok=True)
    manager.save_to_file("data/domains.json")
    print("\nDomains saved to data/domains.json")
