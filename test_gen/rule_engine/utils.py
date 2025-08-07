"""
Utility functions for rule-based variable extraction system.

This module provides helper functions for DOM traversal and CSS-style
node queries to support enhanced variable extraction.
"""

import re
from typing import List, Optional
from feature_extraction.models import UINode


def query_node_text(
    root_node: UINode,
    all_nodes: List[UINode],
    selector: str
) -> Optional[str]:
    """
    Search for a descendant node using simple CSS-style selectors and return its text.
    
    This function supports basic tag-based selectors and direct child relationships
    using the '>' operator. It searches the subtree under root_node for the first
    matching descendant and returns the text content of that node.
    
    Args:
        root_node: The UINode to search within
        all_nodes: List of all UINodes to build the tree structure
        selector: Simple CSS selector (e.g., "span", "div > span")
                 Only supports tag names and direct child operator '>'
    
    Returns:
        The text content of the first matching node, or None if no match found
        
    Examples:
        >>> query_node_text(root, all_nodes, "span")  # Find any span descendant
        >>> query_node_text(root, all_nodes, "div > span")  # Find span that is direct child of div
    """
    if not selector or not selector.strip():
        return None
        
    # Parse selector - split on '>' to handle direct child relationships
    selector_parts = [part.strip() for part in selector.split('>')]
    if not selector_parts or not all(part for part in selector_parts):
        return None
    
    # Build a map of node ID to UINode for efficient lookup
    node_map = {node.id: node for node in all_nodes}
    
    # Build children map for tree traversal
    children_map = {}
    for node in all_nodes:
        if node.parent is not None:
            if node.parent not in children_map:
                children_map[node.parent] = []
            children_map[node.parent].append(node)
    
    # Start search from root_node
    current_candidates = [root_node]
    
    # Process each selector part
    for i, tag in enumerate(selector_parts):
        if not current_candidates:
            break
            
        next_candidates = []
        
        for candidate in current_candidates:
            if i == 0:
                # For the first selector part, search all descendants
                descendants = _get_all_descendants(candidate, children_map)
            else:
                # For subsequent parts (after '>'), search only direct children
                descendants = children_map.get(candidate.id, [])
            
            # Filter descendants by tag name
            matching_descendants = [
                desc for desc in descendants 
                if desc.tag.lower() == tag.lower()
            ]
            
            next_candidates.extend(matching_descendants)
        
        current_candidates = next_candidates
    
    # Return text of first match
    if current_candidates:
        return current_candidates[0].text
    
    return None


def _get_all_descendants(node: UINode, children_map: dict) -> List[UINode]:
    """
    Get all descendant nodes (children, grandchildren, etc.) of a given node.
    
    Args:
        node: The parent node to get descendants for
        children_map: Dictionary mapping parent ID to list of child nodes
        
    Returns:
        List of all descendant UINodes
    """
    descendants = []
    
    # Get direct children
    direct_children = children_map.get(node.id, [])
    descendants.extend(direct_children)
    
    # Recursively get descendants of each child
    for child in direct_children:
        descendants.extend(_get_all_descendants(child, children_map))
    
    return descendants