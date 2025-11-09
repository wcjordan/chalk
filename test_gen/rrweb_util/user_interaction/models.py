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
        value: Input value, coordinates, or other action-specific data
        timestamp: When the interaction occurred (milliseconds)
    """

    action: str
    target_id: int
    value: Any
    timestamp: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "action": self.action,
            "target_id": self.target_id,
            "value": self.value,
            "timestamp": self.timestamp,
        }


@dataclass
class ScrollPattern:
    """
    Represents a scroll event paired with a subsequent DOM mutation.

    Captures scroll-triggered behaviors like lazy loading, infinite scroll,
    or content updates that occur in response to scrolling.

    Attributes:
        scroll_event: The original scroll event data
        mutation_event: The DOM mutation that followed the scroll
        delay_ms: Time between scroll and mutation (milliseconds)
    """

    scroll_event: Dict[str, Any]
    mutation_event: Dict[str, Any]
    delay_ms: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "scroll_event": self.scroll_event,
            "mutation_event": self.mutation_event,
            "delay_ms": self.delay_ms,
        }
