"""
Data models for representing the user interactions & scroll patterns
Designed to be built from rrweb data via extractors
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class UserInteraction:
    """
    Captures a user interaction event with its action and context.

    Represents direct user actions like clicks, input changes, and scrolling
    with their associated DOM targets and values.

    Attributes:
        action: Type of interaction ("click", "input", "scroll")
        target_id: ID of the DOM node that was interacted with
        target_node: Resolved UINode metadata for the target_id (includes pre-computed
                     fields like dom_path, all_descendant_text, nearest_ancestor_testid,
                     nearest_ancestor_testid_dom_path, text, aria_label, data_testid, role, tag)
        value: Input value, coordinates, or other action-specific data
        timestamp: When the interaction occurred (milliseconds)
    """

    action: str
    target_id: int
    target_node: Dict[str, Any]
    value: Any
    timestamp: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "action": self.action,
            "target_id": self.target_id,
            "target_node": self.target_node,
            "value": self.value,
            "timestamp": self.timestamp,
        }
