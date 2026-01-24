"""
Data models for representing the user interactions & scroll patterns
Designed to be built from rrweb data via extractors
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


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
                     fields like dom_path, all_descendant_text, nearest_ancestor_testid)
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

    # DOM Path and Element Identification Methods

    def get_dom_path(self) -> Optional[str]:
        """
        Get the full DOM path to the interacted element.

        Returns:
            CSS-like selector path (e.g., "html > body > div.container > button#submit")
            or None if not available
        """
        return self.target_node.get("dom_path")

    def get_data_testid(self) -> Optional[str]:
        """
        Get the data-testid attribute of the interacted element.

        Returns:
            The data-testid value or None if not present
        """
        return self.target_node.get("data_testid")

    def get_nearest_ancestor_testid(self) -> Optional[str]:
        """
        Get the data-testid of the nearest ancestor element that has one.

        Useful for contextualizing interactions on elements that don't have
        their own test IDs but are within a testable container.

        Returns:
            The ancestor's data-testid value or None if no ancestor has one
        """
        return self.target_node.get("nearest_ancestor_testid")

    def get_nearest_ancestor_testid_dom_path(self) -> Optional[str]:
        """
        Get the DOM path to the nearest ancestor element with a data-testid.

        Returns:
            The DOM path to the ancestor or None if no ancestor has a data-testid
        """
        return self.target_node.get("nearest_ancestor_testid_dom_path")

    # Text Content Extraction Methods

    def get_element_text(self) -> Optional[str]:
        """
        Get the direct text content of the interacted element (not including descendants).

        Returns:
            The text content or None if the element has no text
        """
        return self.target_node.get("text")

    def get_all_descendant_text(self) -> Optional[str]:
        """
        Get all text content from the element and its descendants, concatenated.

        This is useful for getting complete button labels or link text when the
        text is spread across nested elements (e.g., spans within a button).

        Returns:
            Space-separated concatenated text from element and all descendants,
            or None if no text content exists

        Example:
            For a button like:
            <button>
                <span>Submit</span>
                <span>Now</span>
            </button>

            Returns: "Submit Now"
        """
        return self.target_node.get("all_descendant_text")

    def get_aria_label(self) -> Optional[str]:
        """
        Get the aria-label attribute of the interacted element.

        Returns:
            The aria-label value or None if not present
        """
        return self.target_node.get("aria_label")

    def get_role(self) -> Optional[str]:
        """
        Get the ARIA role attribute of the interacted element.

        Returns:
            The role value or None if not present
        """
        return self.target_node.get("role")

    def get_tag(self) -> str:
        """
        Get the HTML tag name of the interacted element.

        Returns:
            The tag name (e.g., "button", "input", "div")
        """
        return self.target_node.get("tag", "")
