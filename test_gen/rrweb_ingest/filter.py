"""
Noise-Filtering Framework for rrweb session data.

This module provides functionality to identify and remove low-signal events from
rrweb chunks, including mousemove noise, micro-scrolls, trivial DOM mutations,
and duplicate events. This helps focus downstream processing on meaningful
user interactions.
"""

from typing import List, Set, Tuple
from . import config
from rrweb_util import (
    is_incremental_snapshot,
    is_mouse_move_event,
    is_scroll_event,
    is_dom_mutation_event,
    get_scroll_delta,
)


def is_low_signal(event: dict) -> bool:
    """
    Returns True if the event should be dropped as low-signal noise.

    Identifies events that carry little meaningful information about user behavior,
    such as cursor-only movements, tiny scrolls, and trivial DOM changes.

    Args:
        event: rrweb event dictionary with 'type', 'timestamp', and 'data' fields

    Returns:
        True if the event should be filtered out as noise, False if it should be kept

    Examples:
        >>> # Mousemove event (noise)
        >>> event = {"type": 3, "data": {"source": 1}, "timestamp": 1000}
        >>> is_low_signal(event)
        True

        >>> # Significant scroll (keep)
        >>> event = {"type": 3, "data": {"source": 3, "y": 50}, "timestamp": 1000}
        >>> is_low_signal(event)
        False

        >>> # Micro-scroll (noise)
        >>> event = {"type": 3, "data": {"source": 3, "y": 10}, "timestamp": 1000}
        >>> is_low_signal(event)
        True
    """
    # Only filter IncrementalSnapshot events
    if not is_incremental_snapshot(event):
        return False

    # Drop mousemove events
    if is_mouse_move_event(event):
        return True

    # Drop micro-scrolls with small delta
    if is_scroll_event(event):
        x_delta, y_delta = get_scroll_delta(event)
        # If both deltas are below threshold, consider it a micro-scroll
        if (
            abs(x_delta) < config.MICRO_SCROLL_THRESHOLD
            and abs(y_delta) < config.MICRO_SCROLL_THRESHOLD
        ):
            return True

    # Drop trivial DOM mutations
    if is_dom_mutation_event(event):
        data = event.get("data", {})
        # Check for trivial mutations - this is a simplified heuristic
        # In practice, this would need more sophisticated analysis
        adds = data.get("adds", [])
        removes = data.get("removes", [])
        texts = data.get("texts", [])
        attributes = data.get("attributes", [])

        # If no significant changes, consider it trivial
        if (
            config.FILTER_EMPTY_MUTATIONS
            and not adds
            and not removes
            and not texts
            and not attributes
        ):
            return True

        # If only minor attribute changes (like style updates), consider trivial
        if (
            config.FILTER_STYLE_ONLY_MUTATIONS
            and not adds
            and not removes
            and not texts
            and len(attributes) == 1
        ):
            attr_change = attributes[0]
            # Simple heuristic: single style attribute changes are often trivial
            if attr_change.get("attributes", {}).get("style"):
                return True

    return False


def clean_chunk(
    events: List[dict],
) -> List[dict]:
    """
    Removes low-signal and duplicate events from a chunk.

    Applies noise filtering to remove events that don't contribute meaningful
    information about user behavior, and deduplicates identical events to
    reduce redundancy.

    Args:
        events: List of rrweb event dictionaries to clean

    Returns:
        List of cleaned events with noise and duplicates removed, preserving
        the original order of remaining events

    Examples:
        >>> events = [
        ...     {"type": 3, "data": {"source": 1}, "timestamp": 1000},  # mousemove (noise)
        ...     {"type": 3, "data": {"source": 2, "id": 5}, "timestamp": 2000},  # click
        ...     {"type": 3, "data": {"source": 2, "id": 5}, "timestamp": 2000},  # duplicate
        ... ]
        >>> clean_chunk(events)
        [{"type": 3, "data": {"source": 2, "id": 5}, "timestamp": 2000}]
    """
    if not events:
        return []

    cleaned = []
    seen_signatures: Set[Tuple] = set()

    for event in events:
        # Skip low-signal events
        if is_low_signal(event):
            continue

        # Apply custom filters
        if any(custom_filter(event) for custom_filter in config.DEFAULT_CUSTOM_FILTERS):
            continue

        # Create a signature for deduplication
        # Use type, source, timestamp, and target id if available
        event_type = event.get("type")
        data = event.get("data", {})
        source = data.get("source")
        timestamp = event.get("timestamp")
        target_id = data.get("id")  # Target element ID for interactions

        signature = (event_type, source, timestamp, target_id)

        # Skip if we've seen this exact event before
        if signature in seen_signatures:
            continue

        seen_signatures.add(signature)
        cleaned.append(event)

    return cleaned
