"""
Data models for representing the DOM state, DOM mutations, & UI nodes
Designed to be built from rrweb data via extractors
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


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

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        """Create a UINode instance from a dictionary."""
        return UINode(
            id=data["id"],
            tag=data["tag"],
            attributes=data["attributes"],
            text=data["text"],
            parent=data["parent"],
        )
