"""
Event Classification for rrweb session data.

This module provides functionality to classify rrweb events into different categories
based on their type field. Events are separated into snapshots (full DOM captures),
interactions (incremental changes), and other event types for downstream processing.
"""

from typing import List, Tuple


def classify_events(events: List[dict]) -> Tuple[List[dict], List[dict], List[dict]]:
    """
    Classify rrweb events into snapshots, interactions, and others based on event type.

    Takes a sorted list of rrweb event dictionaries and separates them into three
    categories based on their 'type' field:
    - Snapshots: Full DOM snapshots (type == 2)
    - Interactions: Incremental changes (type == 3)
    - Others: All remaining event types (Meta, Custom, Plugin, etc.)

    Args:
        events: List of rrweb event dictionaries, typically sorted by timestamp

    Returns:
        Tuple containing three lists in order: (snapshots, interactions, others)

    Raises:
        KeyError: If any event is missing the required 'type' field
    """
    snapshots = []
    interactions = []
    others = []

    for event in events:
        # Access 'type' field - will raise KeyError if missing
        event_type = event["type"]

        if event_type == 2:
            # FullSnapshot events - complete DOM captures
            snapshots.append(event)
        elif event_type == 3:
            # IncrementalSnapshot events - DOM mutations, mouse moves, inputs, etc.
            interactions.append(event)
        else:
            # All other event types (Meta, Custom, Plugin, etc.)
            others.append(event)

    return snapshots, interactions, others
