"""
Event extractors for the Session Chunking & Feature Extraction module.

This module contains functions to extract structured feature data from raw rrweb events,
including DOM mutations, user interactions, and timing delays.
"""

from typing import List
from .models import DomMutation


def extract_dom_mutations(events: List[dict]) -> List[DomMutation]:
    """
    From a list of rrweb events, return structured DomMutation records
    for all mutation events (source == 0).

    This function processes rrweb events and extracts DOM mutations including
    node additions, removals, attribute changes, and text content modifications.
    Only events with type == 3 and data.source == 0 are considered mutation events.

    Args:
        events: List of rrweb events to process

    Returns:
        List of DomMutation objects representing all DOM changes, preserving
        the original event order

    Note:
        Events with empty mutation data (no adds, removes, attributes, or texts)
        will not produce any DomMutation entries.
    """
    mutations = []

    for event in events:
        # Only process mutation events
        if event.get("type") != 3:
            continue

        data = event.get("data", {})
        if data.get("source") != 0:
            continue

        timestamp = event.get("timestamp", 0)

        # Extract attribute changes
        for attr_change in data.get("attributes", []):
            node_id = attr_change.get("id")
            if node_id is not None:
                attributes = attr_change.get("attributes", {})
                mutation = DomMutation(
                    mutation_type="attribute",
                    target_id=node_id,
                    details={"attributes": attributes},
                    timestamp=timestamp,
                )
                mutations.append(mutation)

        # Extract text changes
        for text_change in data.get("texts", []):
            node_id = text_change.get("id")
            if node_id is not None:
                text_value = text_change.get("value", "")
                mutation = DomMutation(
                    mutation_type="text",
                    target_id=node_id,
                    details={"text": text_value},
                    timestamp=timestamp,
                )
                mutations.append(mutation)

        # Extract node additions
        for add_record in data.get("adds", []):
            node_data = add_record.get("node", {})
            node_id = node_data.get("id")
            parent_id = add_record.get("parentId")

            if node_id is not None:
                tag = node_data.get("tagName", node_data.get("type", ""))
                attributes = node_data.get("attributes", {})
                text = node_data.get("textContent", "")

                mutation = DomMutation(
                    mutation_type="add",
                    target_id=node_id,
                    details={
                        "parent_id": parent_id,
                        "tag": tag,
                        "attributes": attributes,
                        "text": text,
                    },
                    timestamp=timestamp,
                )
                mutations.append(mutation)

        # Extract node removals
        for remove_record in data.get("removes", []):
            node_id = remove_record.get("id")
            if node_id is not None:
                mutation = DomMutation(
                    mutation_type="remove",
                    target_id=node_id,
                    details={},
                    timestamp=timestamp,
                )
                mutations.append(mutation)

    return mutations
