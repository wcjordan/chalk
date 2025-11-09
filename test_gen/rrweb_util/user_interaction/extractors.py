"""
Extractors to convert rrweb events into user interaction models.

This module contains functions to extract structured feature data from raw rrweb events,
including user interactions and scroll patterns.
"""

from typing import List

from rrweb_util import (
    is_incremental_snapshot,
    is_mouse_interaction_event,
    is_input_event,
    is_scroll_event,
    get_event_timestamp,
    get_event_data,
    get_target_id,
    get_mouse_coordinates,
)
from .models import UserInteraction


def extract_user_interactions(events: List[dict]) -> List[UserInteraction]:
    """
    From a list of rrweb events, return structured UserInteraction records
    for click, input, and scroll actions.

    This function processes rrweb events and extracts user interactions including
    mouse clicks, input changes, and scroll events. Only events with type == 3
    (IncrementalSnapshot) are considered, and specific data.source values map to
    different interaction types:
    - source == 2: Mouse interactions (click, dblclick)
    - source == 5: Input events (text changes, checkboxes)
    - source == 3: Scroll events

    Args:
        events: List of rrweb events to process

    Returns:
        List of UserInteraction objects representing user actions, preserving
        the original event order

    Note:
        Events with other source values or missing required fields are ignored.
        The function preserves event order in the returned list.
    """
    interactions = []

    for event in events:
        # Only process IncrementalSnapshot events
        if not is_incremental_snapshot(event):
            continue

        timestamp = get_event_timestamp(event)

        if is_mouse_interaction_event(event):
            # Mouse interactions (click, dblclick)
            interaction = _extract_click_interaction(event, timestamp)
            if interaction:
                interactions.append(interaction)
        elif is_input_event(event):
            # Input events (text changes, checkboxes)
            interaction = _extract_input_interaction(event, timestamp)
            if interaction:
                interactions.append(interaction)
        elif is_scroll_event(event):
            # Scroll events
            interaction = _extract_scroll_interaction(event, timestamp)
            if interaction:
                interactions.append(interaction)

    return interactions


def _extract_click_interaction(event: dict, timestamp: int) -> UserInteraction:
    """Extract click interaction from mouse event data."""
    target_id = get_target_id(event)
    if target_id is not None:
        x, y = get_mouse_coordinates(event)
        return UserInteraction(
            action="click",
            target_id=target_id,
            value={"x": x, "y": y},
            timestamp=timestamp,
        )
    return None


def _extract_input_interaction(event: dict, timestamp: int) -> UserInteraction:
    """Extract input interaction from input event data."""
    target_id = get_target_id(event)
    if target_id is not None:
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
            value=value,
            timestamp=timestamp,
        )
    return None


def _extract_scroll_interaction(event: dict, timestamp: int) -> UserInteraction:
    """Extract scroll interaction from scroll event data."""
    target_id = get_target_id(event)
    if target_id is not None:
        data = get_event_data(event)
        x = data.get("x", 0)
        y = data.get("y", 0)
        return UserInteraction(
            action="scroll",
            target_id=target_id,
            value={"x": x, "y": y},
            timestamp=timestamp,
        )
    return None
