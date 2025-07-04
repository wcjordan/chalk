"""
Scroll-Pattern Detection for rrweb Session Feature Extraction.

This module provides functionality to detect scroll events that trigger DOM mutations
within a specified time window. This is useful for identifying lazy loading behaviors,
infinite scroll implementations, and other scroll-triggered content updates.

The detection algorithm pairs each scroll event with the next DOM mutation that occurs
within the maximum reaction time window. This helps identify responsive UI behaviors
where scrolling triggers content changes, such as:
- Lazy loading of images or content
- Infinite scroll pagination
- Dynamic content updates based on viewport position
- Progressive disclosure patterns

Configuration:
    Uses DEFAULT_SCROLL_REACTION_MS from config module.
    All parameters can be overridden via function arguments.

Usage:
    from .config import DEFAULT_SCROLL_REACTION_MS
    patterns = detect_scroll_patterns(events)
    for pattern in patterns:
        print(f"Scroll at {pattern.scroll_event['timestamp']} triggered mutation after {pattern.delay_ms}ms")
"""

from typing import List
from .models import ScrollPattern
from . import config


def detect_scroll_patterns(
    events: List[dict],
) -> List[ScrollPattern]:
    """
    Identifies scroll events followed by DOM mutations within a time window.

    This function processes rrweb events to find scroll events (type == 3, data.source == 3)
    that are followed by DOM mutation events (type == 3, data.source == 0) within a
    specified time window. This is useful for detecting scroll-triggered behaviors like
    lazy loading, infinite scroll, and dynamic content updates.

    Args:
        events: List of rrweb events to analyze

    Returns:
        List of ScrollPattern objects representing scroll→mutation pairs, ordered
        chronologically by scroll event timestamp. Each pattern contains:
        - scroll_event: The original scroll event data
        - mutation_event: The DOM mutation that followed the scroll
        - delay_ms: Time between scroll and mutation in milliseconds

    Note:
        Each scroll event matches at most one mutation event (the first one within
        the time window). After a match is found, the search continues from the
        next scroll event. Events that are not scroll or mutation events are ignored.
    """
    if not events:
        return []

    patterns = []
    scroll_events = _filter_scroll_events(events)
    mutation_events = _filter_mutation_events(events)

    if not scroll_events or not mutation_events:
        return []

    # Use a pointer to track position in mutation events to avoid re-scanning
    mutation_index = 0

    for scroll_event in scroll_events:
        scroll_ts = scroll_event.get("timestamp", 0)

        # Look for the next mutation event within the time window
        while mutation_index < len(mutation_events):
            mutation_event = mutation_events[mutation_index]
            mutation_ts = mutation_event.get("timestamp", 0)

            # If mutation is before scroll, skip it
            if mutation_ts <= scroll_ts:
                mutation_index += 1
                continue

            # If mutation is within the reaction window, create a pattern
            delay_ms = mutation_ts - scroll_ts
            if delay_ms <= config.DEFAULT_SCROLL_REACTION_MS:
                pattern = ScrollPattern(
                    scroll_event=scroll_event,
                    mutation_event=mutation_event,
                    delay_ms=delay_ms,
                )
                patterns.append(pattern)
                mutation_index += 1  # Move past this mutation for next scroll
                break

            # If mutation is beyond the window, no match for this scroll
            break

    return patterns


def _filter_scroll_events(events: List[dict]) -> List[dict]:
    """
    Filter events to only include scroll events.

    Args:
        events: List of rrweb events to filter

    Returns:
        List of events where type == 3 and data.source == 3, sorted by timestamp
    """
    scroll_events = [
        event
        for event in events
        if event.get("type") == 3 and event.get("data", {}).get("source") == 3
    ]
    # Sort by timestamp to ensure chronological processing
    scroll_events.sort(key=lambda e: e.get("timestamp", 0))
    return scroll_events


def _filter_mutation_events(events: List[dict]) -> List[dict]:
    """
    Filter events to only include DOM mutation events.

    Args:
        events: List of rrweb events to filter

    Returns:
        List of events where type == 3 and data.source == 0, sorted by timestamp
    """
    mutation_events = [
        event
        for event in events
        if event.get("type") == 3 and event.get("data", {}).get("source") == 0
    ]
    # Sort by timestamp to ensure chronological processing
    mutation_events.sort(key=lambda e: e.get("timestamp", 0))
    return mutation_events
