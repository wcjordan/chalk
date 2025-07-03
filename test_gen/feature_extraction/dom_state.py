"""
Virtual DOM State Management for rrweb Session Feature Extraction.

This module handles the initialization and maintenance of a virtual DOM state
from rrweb snapshot and mutation events. It creates the initial DOM tree from
FullSnapshot events and maintains the evolving DOM based on incremental snapshots
through mutation tracking.
"""

from typing import Dict, List
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
            id=node_id, tag=tag, attributes=attributes, text=text, parent=parent_id
        )

        node_by_id[node_id] = ui_node

        # Recursively process child nodes
        child_nodes = node_data.get("childNodes", [])
        for child in child_nodes:
            traverse_node(child, node_id)

    # Start traversal from root
    traverse_node(root_node)

    return node_by_id


def apply_mutations(node_by_id: Dict[int, UINode], mutation_events: List[dict]) -> None:
    """
    Applies a sequence of rrweb mutation events to update the in-memory DOM state in place.

    This function processes mutation events (type == 3, source == 0) and updates
    the virtual DOM state by handling node additions, removals, attribute changes,
    and text content modifications.

    Args:
        node_by_id: Dictionary mapping node IDs to UINode instances (modified in place)
        mutation_events: List of rrweb mutation events to apply

    Note:
        This function modifies node_by_id in place. Mutation entries that reference
        nonexistent node IDs are safely ignored without raising errors.
    """
    for event in mutation_events:
        # Only process mutation events
        if event.get("type") != 3 or event.get("data", {}).get("source") != 0:
            continue

        data = event.get("data", {})

        # Handle node additions
        adds = data.get("adds", [])
        for add_record in adds:
            node_data = add_record.get("node", {})
            node_id = node_data.get("id")
            parent_id = add_record.get("parentId")

            if node_id is not None:
                tag = node_data.get("tagName", node_data.get("type", ""))
                attributes = node_data.get("attributes", {})
                text = node_data.get("textContent", "")

                ui_node = UINode(
                    id=node_id,
                    tag=tag,
                    attributes=attributes,
                    text=text,
                    parent=parent_id,
                )
                node_by_id[node_id] = ui_node

        # Handle node removals
        removes = data.get("removes", [])
        for remove_record in removes:
            node_id = remove_record.get("id")
            if node_id is not None and node_id in node_by_id:
                del node_by_id[node_id]

        # Handle attribute changes
        attributes = data.get("attributes", [])
        for attr_record in attributes:
            node_id = attr_record.get("id")
            if node_id is not None and node_id in node_by_id:
                new_attributes = attr_record.get("attributes", {})
                node_by_id[node_id].attributes.update(new_attributes)

        # Handle text changes
        texts = data.get("texts", [])
        for text_record in texts:
            node_id = text_record.get("id")
            if node_id is not None and node_id in node_by_id:
                new_text = text_record.get("value", "")
                node_by_id[node_id].text = new_text
