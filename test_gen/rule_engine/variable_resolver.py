"""
Variable resolution module for extracting values from matched events and nodes.

This module provides functionality to extract variable values from UserInteraction
events and UINode objects based on path expressions defined in rules.
"""

import logging
import re
from typing import Any, Dict, List, Optional
from rrweb_util.user_interaction.models import UserInteraction
from rrweb_util.dom_state.models import UINode
from rule_engine.utils import query_node_text

logger = logging.getLogger("test_gen.rule_engine")


def extract_variables(
    variable_map: Dict[str, str],
    event: UserInteraction,
    all_nodes: List[UINode] = None,
) -> Dict[str, Any]:
    """
    Extract variables from matched event and node based on path expressions.

    Args:
        variable_map: Dictionary mapping variable names to source paths
                      (e.g., {"input_value": "event.value", "placeholder": "node.attributes.placeholder"})
        event: The matched UserInteraction object
        all_nodes: Optional list of all UINodes for CSS-style queries (required for node.query() expressions)

    Returns:
        Dictionary mapping variable names to their resolved values.
        Returns None for variables whose paths cannot be resolved.

    Examples:
        >>> variable_map = {
        ...     "input_value": "event.value",
        ...     "placeholder": "node.attributes.placeholder",
        ...     "node_text": "node.text",
        ...     "child_label": "node.query('div > span').text"
        ... }
        >>> result = extract_variables(variable_map, event, all_nodes)
        >>> # Returns: {
        ...     "input_value": "cats",
        ...     "placeholder": "Search...",
        ...     "node_text": "Search field",
        ...     "child_label": "Label text"
        ... }
    """
    result = {}
    node = UINode.from_dict(event.target_node)

    for variable_name, path in variable_map.items():
        # Check if this is a node.query().text expression
        if _is_query_expression(path):
            resolved_value = _resolve_query_expression(path, node, all_nodes)
        else:
            resolved_value = _resolve_path(path, event, node)

        # Log extraction failures
        if resolved_value is None:
            logger.debug(
                "Variable extraction failed for '%s': path '%s' not found",
                variable_name,
                path,
            )

        result[variable_name] = resolved_value

    return result


def _resolve_path(path: str, event: UserInteraction, node: UINode) -> Any:
    """
    Private helper function to resolve a dotted path expression to extract a value from event or node.

    This function returns None if the path cannot be resolved, specifically if an AttributeError,
    KeyError, or TypeError is encountered during resolution.

    Args:
        path: Dotted path expression (e.g., "event.value", "node.text", "node.attributes.placeholder",
              "event.target_node.dom_path")
        event: The UserInteraction object
        node: The UINode object

    Returns:
        The resolved value, or None if the path cannot be resolved.
    """
    path_parts = path.split(".")

    if len(path_parts) < 2:
        return None

    root = path_parts[0]
    remaining_parts = path_parts[1:]

    # Determine the root object
    if root == "event":
        current_obj = event
    elif root == "node":
        current_obj = node
    else:
        return None

    # Traverse the path
    for part in remaining_parts:
        try:
            if hasattr(current_obj, part):
                current_obj = getattr(current_obj, part)
            elif isinstance(current_obj, dict) and part in current_obj:
                current_obj = current_obj[part]
            else:
                return None
        except (AttributeError, KeyError, TypeError) as e:
            logger.debug("Failed to resolve path '%s' at part '%s': %s", path, part, e)
            return None

    return current_obj


def _is_query_expression(path: str) -> bool:
    """
    Check if a path expression is a node.query().text pattern.

    Args:
        path: The path expression to check

    Returns:
        True if this is a node.query().text expression, False otherwise
    """
    # Pattern: node.query("selector").text or node.query('selector').text
    pattern = r'^node\.query\(["\']([^"\']+)["\']\)\.text$'
    return bool(re.match(pattern, path))


def _resolve_query_expression(
    path: str, node: UINode, all_nodes: List[UINode]
) -> Optional[str]:
    """
    Resolve a node.query().text expression by extracting the selector and querying the DOM.

    Args:
        path: The query expression (e.g., 'node.query("div > span").text')
        node: The root node to search from
        all_nodes: List of all nodes for building the tree structure

    Returns:
        The text content of the matching node, or None if no match found or invalid expression
    """
    if not all_nodes:
        logger.debug(
            "Cannot resolve query expression '%s': all_nodes is required", path
        )
        return None

    # Extract the selector from the expression
    pattern = r'^node\.query\(["\']([^"\']+)["\']\)\.text$'
    match = re.match(pattern, path)

    if not match:
        logger.debug("Invalid query expression format: '%s'", path)
        return None

    selector = match.group(1)

    return query_node_text(node, all_nodes, selector)
