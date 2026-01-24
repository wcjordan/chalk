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

from typing import Dict, Any, List, Optional, Tuple
from rrweb_util.dom_state import config
from .models import UINode


def resolve_node_metadata(
    node_id: int,
    node_by_id: Dict[int, UINode],
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

    Returns:
        Dict containing:
        - tag: HTML tag name (e.g., "button", "input")
        - aria_label: Value of aria-label attribute or None
        - data_testid: Value of data-testid attribute or None
        - role: Value of role attribute or None
        - text: Text content of the node or None
        - dom_path: CSS-like selector path from root to node
        - all_descendant_text: Concatenated text from all descendants (space-separated)
        - nearest_ancestor_testid: data-testid of nearest ancestor with one, or None
        - nearest_ancestor_testid_dom_path: DOM path to nearest ancestor with testid, or None

    Raises:
        KeyError: If the node_id is not found in node_by_id

    Example:
        >>> metadata = resolve_node_metadata(42, node_by_id)
        >>> print(metadata['dom_path'])
        "html > body > div.container > button#submit"
        >>> print(metadata['all_descendant_text'])
        "Submit Now"
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
    dom_path = _compute_dom_path(node, node_by_id)

    # Compute all descendant text
    all_descendant_text = _get_all_descendant_text(node, node_by_id)

    # Find nearest ancestor with data-testid
    ancestor_testid, ancestor_dom_path = _find_nearest_ancestor_with_testid(
        node, node_by_id
    )

    # TODO should this return the UINode directly and should this logic live in its to_dict method?
    return {
        "tag": tag,
        "aria_label": aria_label,
        "data_testid": data_testid,
        "role": role,
        "text": text,
        "dom_path": dom_path,
        "all_descendant_text": all_descendant_text,
        "nearest_ancestor_testid": ancestor_testid,
        "nearest_ancestor_testid_dom_path": ancestor_dom_path,
    }


def _compute_dom_path(node: UINode, node_by_id: Dict[int, UINode]) -> str:
    """
    Compute a CSS-like selector path from root to the given node.

    Walks up the DOM tree from the given node to the root, building a path
    that includes tag names and identifying attributes like id and class.

    Args:
        node: The UINode to compute the path for
        node_by_id: Dictionary mapping node IDs to UINode instances

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

    return config.default_dom_path_formatter(path_parts)


def _get_all_descendant_text(
    node: UINode, node_by_id: Dict[int, UINode]
) -> Optional[str]:
    """
    Collect and concatenate all text content from a node and its descendants.

    Performs a depth-first traversal of the DOM tree starting from the given node,
    collecting text content from the node itself and all its descendants. Text is
    concatenated with spaces and stripped of extra whitespace.

    Args:
        node: The root UINode to collect text from
        node_by_id: Dictionary mapping node IDs to UINode instances

    Returns:
        Concatenated text from node and all descendants (space-separated and stripped),
        or None if no text content is found

    Example:
        For a button with nested spans:
        <button id="123">
            <span>Submit</span>
            <span>Now</span>
        </button>

        >>> _get_all_descendant_text(button_node, node_by_id)
        "Submit Now"
    """

    # Recursive function to collect text from node and descendants
    def collect_text(current_node: UINode) -> List[str]:
        texts = []

        # Add current node's text if it exists
        if current_node.text and current_node.text.strip():
            texts.append(current_node.text.strip())

        # Recursively collect text from children using node.children
        for child_id in current_node.children:
            child_node = node_by_id.get(child_id)
            if child_node is not None:  # Defensive - child should exist
                texts.extend(collect_text(child_node))

        return texts

    all_texts = collect_text(node)
    if not all_texts:
        return None

    # Join all text pieces with spaces and clean up extra whitespace
    combined = " ".join(all_texts)
    # Normalize whitespace (replace multiple spaces with single space)
    normalized = " ".join(combined.split())

    return normalized if normalized else None


def _find_nearest_ancestor_with_testid(
    node: UINode, node_by_id: Dict[int, UINode]
) -> Tuple[Optional[str], Optional[str]]:
    """
    Find the nearest ancestor node that has a data-testid attribute.

    Walks up the DOM tree from the given node to find the first parent or ancestor
    that has a data-testid attribute defined. This is useful for contextualizing
    interactions on elements that don't have their own test IDs.

    Args:
        node: The UINode to start searching from
        node_by_id: Dictionary mapping node IDs to UINode instances

    Returns:
        Tuple of (data-testid value, dom_path to ancestor) if found, or (None, None)
        if no ancestor with data-testid exists

    Example:
        <div data-testid="user-profile">
            <div class="header">
                <button id="123">Edit</button>  <!-- clicking this button -->
            </div>
        </div>

        >>> testid, path = _find_nearest_ancestor_with_testid(button_node, node_by_id)
        >>> testid
        "user-profile"
        >>> path
        "html > body > div[data-testid='user-profile']"
    """
    # Start from the parent (not the node itself, since we want ancestor)
    if node.parent is None:
        return None, None

    current_node = node_by_id.get(node.parent)

    # Walk up the tree until we find a data-testid or reach the root
    while current_node is not None:
        testid = current_node.attributes.get("data-testid")
        if testid:
            # Found an ancestor with data-testid
            ancestor_dom_path = _compute_dom_path(current_node, node_by_id)
            return testid, ancestor_dom_path

        # Move to parent
        if current_node.parent is not None:
            current_node = node_by_id.get(current_node.parent)
        else:
            current_node = None

    return None, None
