"""
Virtual DOM State Management for rrweb Session Feature Extraction.

This module handles the initialization and maintenance of a virtual DOM state
from rrweb snapshot and mutation events. It creates the initial DOM tree from
FullSnapshot events and provides utilities for tracking DOM changes over time.
"""

from typing import Dict
from .models import UINode


def init_dom_state(full_snapshot_event: dict) -> Dict[int, UINode]:
    """
    Given a FullSnapshot rrweb event, builds and returns a node_by_id map.
    
    The full_snapshot_event is an rrweb event with type == 2 and data.node
    containing the entire DOM tree. This function traverses the snapshot
    payload and creates UINode instances for each DOM node.
    
    Args:
        full_snapshot_event: rrweb event with type == 2 containing DOM snapshot
        
    Returns:
        Dict mapping node IDs to UINode instances
        
    Raises:
        ValueError: If the event is not a valid FullSnapshot event
    """
    if full_snapshot_event.get("type") != 2:
        raise ValueError("Event must be a FullSnapshot event (type == 2)")
    
    if "data" not in full_snapshot_event or "node" not in full_snapshot_event["data"]:
        raise ValueError("FullSnapshot event must contain data.node")
    
    node_by_id = {}
    root_node = full_snapshot_event["data"]["node"]
    
    def traverse_node(node_data, parent_id=None):
        """Recursively traverse the DOM tree and create UINode instances."""
        node_id = node_data.get("id")
        if node_id is None:
            return
        
        # Extract node properties
        tag = node_data.get("tagName", node_data.get("type", ""))
        attributes = node_data.get("attributes", {})
        text = node_data.get("textContent", "")
        
        # Create UINode instance
        ui_node = UINode(
            id=node_id,
            tag=tag,
            attributes=attributes,
            text=text,
            parent=parent_id
        )
        
        node_by_id[node_id] = ui_node
        
        # Recursively process child nodes
        child_nodes = node_data.get("childNodes", [])
        for child in child_nodes:
            traverse_node(child, node_id)
    
    # Start traversal from root
    traverse_node(root_node)
    
    return node_by_id
