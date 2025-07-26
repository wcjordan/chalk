"""
Chunk Normalization for rrweb session data.

This module provides functionality to convert cleaned lists of rrweb events
into normalized Chunk objects with standardized metadata and identifiers.
The normalization process ensures consistent structure for downstream processing.
"""

from typing import List, Dict, Any
from .models import Chunk


def normalize_chunk(
    raw_events: List[Dict[str, Any]],
    session_id: str,
    chunk_index: int,
    snapshot_before: dict,
) -> Chunk:
    """
    Builds a Chunk object from a list of cleaned events.

    Takes a list of cleaned rrweb event dictionaries and wraps them in a
    normalized Chunk object with computed metadata and a standardized identifier.
    This provides a consistent interface for downstream feature extraction and
    analysis components.

    Args:
        raw_events: List of cleaned rrweb event dictionaries. Each event must
                   have at least a 'timestamp' field. Events should be sorted
                   by timestamp.
        session_id: Identifier for the session this chunk belongs to. Used to
                   generate the chunk_id.
        chunk_index: Zero-based index of this chunk within the session. Used to
                    generate the chunk_id with zero-padding.
        snapshot_before: Snapshot data with the initial DOM state before this chunk.

    Returns:
        Chunk object with populated fields:
        - chunk_id: Formatted as "{session_id}-chunk{chunk_index:03d}"
        - start_time: Timestamp of first event
        - end_time: Timestamp of last event
        - events: Copy of the input events list
        - metadata: Dictionary containing num_events and duration_ms

    Raises:
        ValueError: If raw_events is empty, session_id is empty, or chunk_index
                   is negative
        KeyError: If any event is missing the required 'timestamp' field

    Examples:
        >>> events = [
        ...     {"type": 3, "timestamp": 1000, "data": {"source": 2}},
        ...     {"type": 3, "timestamp": 1500, "data": {"source": 3}},
        ... ]
        >>> chunk = normalize_chunk(events, "session_abc", 0)
        >>> chunk.chunk_id
        'session_abc-chunk000'
        >>> chunk.start_time
        1000
        >>> chunk.end_time
        1500
        >>> chunk.metadata['duration_ms']
        500
    """
    # Validate inputs
    if not raw_events:
        raise ValueError("Cannot create chunk from empty event list")

    if not session_id:
        raise ValueError("session_id cannot be empty")

    if chunk_index < 0:
        raise ValueError("chunk_index must be non-negative")

    # Validate that all events have timestamps
    for i, event in enumerate(raw_events):
        if "timestamp" not in event:
            raise KeyError(f"Event at index {i} missing required 'timestamp' field")

    # Extract timestamps
    timestamps = [event["timestamp"] for event in raw_events]
    start_time = min(timestamps)
    end_time = max(timestamps)

    # Generate chunk ID with zero-padded index
    chunk_id = f"{session_id}-chunk{chunk_index:03d}"

    # Calculate metadata
    num_events = len(raw_events)
    duration_ms = end_time - start_time

    metadata = {
        "num_events": num_events,
        "duration_ms": duration_ms,
        "snapshot_before": snapshot_before,
    }

    # Create and return the Chunk object
    return Chunk(
        chunk_id=chunk_id,
        start_time=start_time,
        end_time=end_time,
        events=raw_events.copy(),  # Create a copy to avoid mutation
        metadata=metadata,
    )
