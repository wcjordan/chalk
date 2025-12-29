"""
Noise-Filtering Framework for rrweb session data.

This module provides functionality to identify and remove low-signal events from
rrweb chunks, including mousemove noise & scrolling. This helps focus downstream
processing on meaningful user interactions.
"""

from rrweb_util import (
    is_incremental_snapshot,
    is_mouse_move_event,
    is_scroll_event,
)


def is_low_signal(event: dict) -> bool:
    """
    Returns True if the event should be dropped as low-signal noise.

    Identifies events that carry little meaningful information about user behavior,
    such as cursor-only movements & scrolling.

    Args:
        event: rrweb event dictionary with 'type', 'timestamp', and 'data' fields

    Returns:
        True if the event should be filtered out as noise, False if it should be kept

    Examples:
        >>> # Mousemove event (noise)
        >>> event = {"type": 3, "data": {"source": 1}, "timestamp": 1000}
        >>> is_low_signal(event)
        True

        >>> # Scroll event (noise)
        >>> event = {"type": 3, "data": {"source": 3, "y": 10}, "timestamp": 1000}
        >>> is_low_signal(event)
        True
    """
    # Only filter IncrementalSnapshot events
    if not is_incremental_snapshot(event):
        return False

    # Drop mousemove events & scroll events
    return is_mouse_move_event(event) or is_scroll_event(event)
