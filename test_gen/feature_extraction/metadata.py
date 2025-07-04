"""
UI Metadata Resolution for rrweb Session Feature Extraction.

This module provides functions to resolve human-readable context for UI nodes,
including semantic attributes, DOM paths, and accessibility information that
can be used for behavior analysis and test generation.

Configuration:
    Uses default_dom_path_formatter from config module for DOM path formatting.
    Custom formatters can be passed to override the default behavior.

Extensibility:
    Custom DOM path formatters can be provided to modify how DOM paths are
    constructed and formatted. The formatter function should accept a list
    of path parts and return a formatted string.
"""

from typing import Dict, Any, Callable
from .models import UINode
from .config import default_dom_path_formatter


def resolve_node_metadata(
    node_id: int, 
    node_by_id: Dict[int, UINode],
    dom_path_formatter: Callable[[list], str] = default_dom_path_formatter
) -> Dict[str, Any]:
    """
    Given a node ID and the current virtual DOM map, return a metadata
    dict including human-readable context for the UI node.

    This function extracts semantic information from a DOM node that is useful
    for understanding user interactions and generating meaningful descriptions
    of user behavior.

    Args:
        node_id: The ID of the DOM node to resolve metadata for
        node_by_id: Dictionary mapping node IDs to UINode instances
        dom_path_formatter: Function to format DOM path parts into a string.
                           Defaults to default_dom_path_formatter from config.
                           Should accept a list of path parts and return a string.

    Returns:
        Dict containing:
        - tag: HTML tag name (e.g., "button", "input")
        - aria_label: Value of aria-label attribute or None
        - data_testid: Value of data-testid attribute or None
        - role: Value of role attribute or None
        - text: Text content of the node or None
        - dom_path: CSS-like selector path from root to node

    Raises:
        KeyError: If the node_id is not found in node_by_id

    Example:
        >>> metadata = resolve_node_metadata(42, node_by_id)
        >>> print(metadata['dom_path'])
        "html > body > div.container > button#submit"
    """
    if node_id not in node_by_id:
        raise KeyError(f"Node ID {node_id} not found in node_by_id")

    node = node_by_id[node_id]

    # Extract basic node information
    tag = node.tag
    text = node.text.strip() if node.text and node.text.strip() else None

    # Extract semantic attributes
    aria_label = node.attributes.get("aria-label")
    data_testid = node.attributes.get("data-testid")
    role = node.attributes.get("role")

    # Compute DOM path
    dom_path = _compute_dom_path(node, node_by_id, dom_path_formatter)

    return {
        "tag": tag,
        "aria_label": aria_label,
        "data_testid": data_testid,
        "role": role,
        "text": text,
        "dom_path": dom_path,
    }


def _compute_dom_path(node: UINode, node_by_id: Dict[int, UINode], formatter: Callable[[list], str]) -> str:
    """
    Compute a CSS-like selector path from root to the given node.

    Walks up the DOM tree from the given node to the root, building a path
    that includes tag names and identifying attributes like id and class.

    Args:
        node: The UINode to compute the path for
        node_by_id: Dictionary mapping node IDs to UINode instances
        formatter: Function to format the path parts into a string

    Returns:
        String representing the DOM path (e.g., "html > body > div.container > button#submit")
    """
    path_parts = []
    current_node = node

    while current_node is not None:
        # Build selector for current node
        selector = current_node.tag

        # Add ID if present
        node_id_attr = current_node.attributes.get("id")
        if node_id_attr:
            selector += f"#{node_id_attr}"

        # Add first class if present
        class_attr = current_node.attributes.get("class")
        if class_attr:
            # Take the first class name for simplicity
            first_class = class_attr.split()[0] if class_attr.split() else ""
            if first_class:
                selector += f".{first_class}"

        path_parts.insert(0, selector)

        # Move to parent
        if current_node.parent is not None:
            current_node = node_by_id.get(current_node.parent)
        else:
            current_node = None

    return formatter(path_parts)
