"""
Noise-Filtering Framework for rrweb session data.

This module provides functionality to identify and remove low-signal events from
rrweb chunks, including mousemove noise, micro-scrolls, trivial DOM mutations,
and duplicate events. This helps focus downstream processing on meaningful
user interactions.
"""

from typing import List, Set, Tuple


def is_low_signal(event: dict, micro_scroll_threshold: int = 20) -> bool:
    """
    Returns True if the event should be dropped as low-signal noise.

    Identifies events that carry little meaningful information about user behavior,
    such as cursor-only movements, tiny scrolls, and trivial DOM changes.

    Args:
        event: rrweb event dictionary with 'type', 'timestamp', and 'data' fields
        micro_scroll_threshold: Minimum scroll distance in pixels to be considered
                               meaningful (default: 20px)

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
    # Only filter IncrementalSnapshot events (type == 3)
    if event.get("type") != 3:
        return False

    data = event.get("data", {})
    source = data.get("source")

    # Drop mousemove events (source == 1)
    if source == 1:
        return True

    # Drop micro-scrolls (source == 3 with small delta)
    if source == 3:
        # Check for scroll distance in x or y direction
        x_delta = abs(data.get("x", 0))
        y_delta = abs(data.get("y", 0))

        # If both deltas are below threshold, consider it a micro-scroll
        if x_delta < micro_scroll_threshold and y_delta < micro_scroll_threshold:
            return True

    # Drop trivial DOM mutations (source == 0)
    if source == 0:
        # Check for trivial mutations - this is a simplified heuristic
        # In practice, this would need more sophisticated analysis
        adds = data.get("adds", [])
        removes = data.get("removes", [])
        texts = data.get("texts", [])
        attributes = data.get("attributes", [])

        # If no significant changes, consider it trivial
        if not adds and not removes and not texts and not attributes:
            return True

        # If only minor attribute changes (like style updates), consider trivial
        if not adds and not removes and not texts and len(attributes) == 1:
            attr_change = attributes[0]
            # Simple heuristic: single style attribute changes are often trivial
            if attr_change.get("attributes", {}).get("style"):
                return True

    return False


def clean_chunk(events: List[dict], micro_scroll_threshold: int = 20) -> List[dict]:
    """
    Removes low-signal and duplicate events from a chunk.

    Applies noise filtering to remove events that don't contribute meaningful
    information about user behavior, and deduplicates identical events to
    reduce redundancy.

    Args:
        events: List of rrweb event dictionaries to clean
        micro_scroll_threshold: Minimum scroll distance in pixels to be
                                considered meaningful (default: 20px)

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
        if is_low_signal(event, micro_scroll_threshold):
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
