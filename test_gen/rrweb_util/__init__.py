"""
Shared utilities for rrweb event processing.
"""

from .constants import EventType, IncrementalSource, MouseInteractionType, NodeType
from .helpers import (
    is_full_snapshot,
    is_incremental_snapshot,
    get_incremental_source,
    is_mouse_move_event,
    is_mouse_interaction_event,
    is_scroll_event,
    is_input_event,
    is_dom_mutation_event,
    get_event_timestamp,
    get_event_data,
    get_target_id,
    get_mouse_coordinates,
    get_tag_name,
    extract_interaction_details,
)

__all__ = [
    # Constants
    "EventType",
    "IncrementalSource",
    "MouseInteractionType",
    "NodeType",
    # Helpers
    "is_full_snapshot",
    "is_incremental_snapshot",
    "get_incremental_source",
    "is_mouse_move_event",
    "is_mouse_interaction_event",
    "is_scroll_event",
    "is_input_event",
    "is_dom_mutation_event",
    "get_event_timestamp",
    "get_event_data",
    "get_target_id",
    "get_mouse_coordinates",
    "get_tag_name",
    "extract_interaction_details",
]
