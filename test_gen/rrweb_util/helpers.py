"""
Shared utility functions for rrweb event processing across all modules.
"""

from typing import Optional, Dict, Any, Tuple
from .constants import EventType, IncrementalSource, NODE_TYPE_TO_TAG_MAP


# Event type checking
def is_full_snapshot(event: Dict[str, Any]) -> bool:
    """Check if event is a FullSnapshot."""
    return event.get("type") == EventType.FULL_SNAPSHOT


def is_incremental_snapshot(event: Dict[str, Any]) -> bool:
    """Check if event is an IncrementalSnapshot."""
    return event.get("type") == EventType.INCREMENTAL_SNAPSHOT


def get_incremental_source(event: Dict[str, Any]) -> Optional[int]:
    """Get the source type from an incremental snapshot event."""
    if not is_incremental_snapshot(event):
        return None
    return event.get("data", {}).get("source")


# Specific event type checking
def is_mouse_move_event(event: Dict[str, Any]) -> bool:
    """Check if event is a mouse move."""
    return get_incremental_source(event) == IncrementalSource.MOUSE_MOVE


def is_mouse_interaction_event(event: Dict[str, Any]) -> bool:
    """Check if event is a mouse click/interaction."""
    return get_incremental_source(event) == IncrementalSource.MOUSE_INTERACTION


def is_scroll_event(event: Dict[str, Any]) -> bool:
    """Check if event is a scroll."""
    return get_incremental_source(event) == IncrementalSource.SCROLL


def is_input_event(event: Dict[str, Any]) -> bool:
    """Check if event is an input."""
    return get_incremental_source(event) == IncrementalSource.INPUT


def is_dom_mutation_event(event: Dict[str, Any]) -> bool:
    """Check if event is a DOM mutation."""
    return get_incremental_source(event) == IncrementalSource.MUTATION


# Data extraction helpers
def get_event_timestamp(event: Dict[str, Any]) -> int:
    """Safely get timestamp from event."""
    return event.get("timestamp", 0)


def get_event_data(event: Dict[str, Any]) -> Dict[str, Any]:
    """Safely get data from event."""
    return event.get("data", {})


def get_target_id(event: Dict[str, Any]) -> Optional[int]:
    """Get target element ID from interaction event."""
    return get_event_data(event).get("id")


def get_mouse_coordinates(event: Dict[str, Any]) -> Tuple[int, int]:
    """Get x, y coordinates from mouse event."""
    data = get_event_data(event)
    return data.get("x", 0), data.get("y", 0)


def get_scroll_delta(event: Dict[str, Any]) -> Tuple[int, int]:
    """Get x, y scroll deltas from scroll event."""
    data = get_event_data(event)
    return data.get("x", 0), data.get("y", 0)


# DOM node helpers
def get_tag_name(node_data: Dict[str, Any]) -> str:
    """Get the tag name for a given node data dictionary."""
    return node_data.get(
        "tagName", NODE_TYPE_TO_TAG_MAP.get(node_data.get("type"), "unknown")
    )


def extract_interaction_details(event: Dict[str, Any]) -> Dict[str, Any]:
    """Extract common interaction details from event."""
    data = get_event_data(event)
    details = {}

    # Mouse coordinates
    if "x" in data and "y" in data:
        details["coordinates"] = {"x": data["x"], "y": data["y"]}

    # Input values
    if "text" in data:
        details["text"] = data["text"]
    if "isChecked" in data:
        details["checked"] = data["isChecked"]

    # Target information
    if "id" in data:
        details["target_id"] = data["id"]

    return details
