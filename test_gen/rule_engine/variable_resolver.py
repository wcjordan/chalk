"""
Variable resolution module for extracting values from matched events and nodes.

This module provides functionality to extract variable values from UserInteraction
events and UINode objects based on path expressions defined in rules.
"""

from typing import Dict, Any
from feature_extraction.models import UserInteraction, UINode


def extract_variables(
    variable_map: Dict[str, str],
    event: UserInteraction,
    node: UINode
) -> Dict[str, Any]:
    """
    Extract variables from matched event and node based on path expressions.
    
    Args:
        variable_map: Dictionary mapping variable names to source paths
                     (e.g., {"input_value": "event.value", "placeholder": "node.attributes.placeholder"})
        event: The matched UserInteraction object
        node: The matched UINode object
    
    Returns:
        Dictionary mapping variable names to their resolved values.
        Returns None for variables whose paths cannot be resolved.
    
    Examples:
        >>> variable_map = {
        ...     "input_value": "event.value",
        ...     "placeholder": "node.attributes.placeholder",
        ...     "node_text": "node.text"
        ... }
        >>> result = extract_variables(variable_map, event, node)
        >>> # Returns: {"input_value": "cats", "placeholder": "Search...", "node_text": "Search field"}
    """
    result = {}
    
    for variable_name, path in variable_map.items():
        resolved_value = _resolve_path(path, event, node)
        result[variable_name] = resolved_value
    
    return result


def _resolve_path(path: str, event: UserInteraction, node: UINode) -> Any:
    """
    Resolve a dotted path expression to extract a value from event or node.
    
    Args:
        path: Dotted path expression (e.g., "event.value", "node.text", "node.attributes.placeholder")
        event: The UserInteraction object
        node: The UINode object
    
    Returns:
        The resolved value, or None if the path cannot be resolved.
    """
    path_parts = path.split('.')
    
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
        except (AttributeError, KeyError, TypeError):
            return None
    
    return current_obj