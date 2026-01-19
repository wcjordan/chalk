"""
Extractors to convert rrweb events into user interaction models.

This module contains functions to extract structured feature data from raw rrweb events,
including user interactions and scroll patterns.
"""

from typing import List

from rrweb_util.dom_state.node_metadata import resolve_node_metadata
from rrweb_util.helpers import (
    is_incremental_snapshot,
    is_drag_event,
    is_mouse_interaction_event,
    is_input_event,
    get_event_timestamp,
    get_event_data,
    get_target_id,
    get_mouse_coordinates,
)
from .models import UserInteraction


def extract_user_interactions(dom_state: dict, event: dict) -> List[UserInteraction]:
    """
    From a rrweb event, return structured UserInteraction records
    for click and input actions.

    This function processes a rrweb event and extracts user interactions including
    mouse clicks and input changes. Only events with type == 3
    (IncrementalSnapshot) are considered, and specific data.source values map to
    different interaction types:
    - source == 2: Mouse interactions (click, dblclick)
    - source == 5: Input events (text changes, checkboxes)

    Args:
        dom_state: Current DOM state mapping node IDs to UINode metadata
        event: A single rrweb event to process

    Returns:
        List of UserInteraction objects representing user actions, preserving
        the original event order

    Note:
        Events with other source values or missing required fields are ignored.
        The function preserves event order in the returned list.
    """
    interactions = []

    # Only process IncrementalSnapshot events
    if not is_incremental_snapshot(event):
        return []

    timestamp = get_event_timestamp(event)

    if is_mouse_interaction_event(event):
        # Mouse interactions (click, dblclick)
        interaction = _extract_click_interaction(dom_state, event, timestamp)
        if interaction:
            interactions.append(interaction)
    elif is_input_event(event):
        # Input events (text changes, checkboxes)
        interaction = _extract_input_interaction(dom_state, event, timestamp)
        if interaction:
            interactions.append(interaction)
    elif is_drag_event(event):
        # Drag event
        # TODO: Implement drag interaction extraction
        pass
    else:
        raise ValueError(f"Unknown event type for interaction extraction: {event}")

    return interactions


def _extract_click_interaction(
    dom_state: dict, event: dict, timestamp: int
) -> UserInteraction:
    """Extract click interaction from mouse event data."""
    target_id = get_target_id(event)
    if target_id is not None:
        target_node = resolve_node_metadata(target_id, dom_state)
        x, y = get_mouse_coordinates(event)
        return UserInteraction(
            action="click",
            target_id=target_id,
            target_node=target_node,
            value={"x": x, "y": y},
            timestamp=timestamp,
        )
    return None


def _extract_input_interaction(
    dom_state: dict, event: dict, timestamp: int
) -> UserInteraction:
    """Extract input interaction from input event data."""
    target_id = get_target_id(event)
    if target_id is not None:
        target_node = resolve_node_metadata(target_id, dom_state)
        data = get_event_data(event)
        # Input events can have either 'text' or 'isChecked' fields
        value = {}
        if "text" in data:
            value["value"] = data["text"]
        if "isChecked" in data:
            value["checked"] = data["isChecked"]

        return UserInteraction(
            action="input",
            target_id=target_id,
            target_node=target_node,
            value=value,
            timestamp=timestamp,
        )
    return None
