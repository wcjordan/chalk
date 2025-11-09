"""
Data models for representing the DOM state, DOM mutations, & UI nodes
Designed to be built from rrweb data via extractors
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class DomMutation:
    """
    Captures a DOM mutation event with its type, target, and timing.

    Represents changes to the DOM structure including node additions/removals,
    attribute changes, and text content modifications.

    Attributes:
        mutation_type: Type of mutation ("add", "remove", "attribute", "text")
        target_id: ID of the DOM node that was mutated
        details: Mutation-specific data (new attributes, text content, etc.)
        timestamp: When the mutation occurred (milliseconds)
    """

    mutation_type: str
    target_id: int
    details: Dict[str, Any]
    timestamp: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "mutation_type": self.mutation_type,
            "target_id": self.target_id,
            "details": self.details,
            "timestamp": self.timestamp,
        }


@dataclass
class UINode:
    """
    Represents a DOM node with its metadata and hierarchy information.

    Captures the essential properties of a DOM element including its structure,
    attributes, content, and position in the DOM tree.

    Attributes:
        id: Unique identifier for the DOM node
        tag: HTML tag name (e.g., "button", "input", "div")
        attributes: Dictionary of HTML attributes
        text: Text content of the node
        parent: ID of the parent node, or None for root
    """

    id: int
    tag: str
    attributes: Dict[str, str]
    text: str
    parent: Optional[int]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "tag": self.tag,
            "attributes": self.attributes,
            "text": self.text,
            "parent": self.parent,
        }
