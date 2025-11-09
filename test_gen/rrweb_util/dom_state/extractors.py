"""
Extractors to convert rrweb events into dom state models.

This module contains functions to extract structured feature data from raw rrweb events,
including dom mutations and UI nodes.
"""

from typing import List

from rrweb_util import (
    is_dom_mutation_event,
    get_event_timestamp,
    get_event_data,
    get_tag_name,
)
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
        if not is_dom_mutation_event(event):
            continue

        timestamp = get_event_timestamp(event)
        data = get_event_data(event)

        # Extract different types of mutations
        mutations.extend(_extract_attribute_mutations(data, timestamp))
        mutations.extend(_extract_text_mutations(data, timestamp))
        mutations.extend(_extract_node_additions(data, timestamp))
        mutations.extend(_extract_node_removals(data, timestamp))

    return mutations


def _extract_attribute_mutations(data: dict, timestamp: int) -> List[DomMutation]:
    """Extract attribute change mutations from event data."""
    mutations = []
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
    return mutations


def _extract_text_mutations(data: dict, timestamp: int) -> List[DomMutation]:
    """Extract text content change mutations from event data."""
    mutations = []
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
    return mutations


def _extract_node_additions(data: dict, timestamp: int) -> List[DomMutation]:
    """Extract node addition mutations from event data."""
    mutations = []
    # pylint: disable=duplicate-code
    for add_record in data.get("adds", []):
        node_data = add_record.get("node", {})
        node_id = node_data.get("id")
        parent_id = add_record.get("parentId")

        if node_id is not None:
            tag = get_tag_name(node_data)
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
    return mutations


def _extract_node_removals(data: dict, timestamp: int) -> List[DomMutation]:
    """Extract node removal mutations from event data."""
    mutations = []
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
