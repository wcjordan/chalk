"""
Basic Chunk Segmentation for rrweb session data.

This module provides functionality to segment interaction events into logical chunks
based on FullSnapshot boundaries. Chunks represent meaningful units of user activity
that can be processed independently for feature extraction.
"""

from typing import List

from rrweb_util import get_event_timestamp
from . import config


def _new_chunk(snapshot_before=None) -> dict:
    """
    Create a new empty chunk to hold interaction events and initial snapshot.

    Returns:
        An empty dictionary representing a new chunk of interaction events.
    """
    return {
        "interactions": [],
        "snapshot_before": snapshot_before,
    }


def segment_into_chunks(
    interactions: List[dict],
    snapshots: List[dict],
) -> List[List[dict]]:
    """
    Segment interaction events into chunks based on multiple boundary criteria.

    Takes sorted lists of interaction events (type == 3) and snapshot events (type == 2)
    and groups interactions into chunks. A new chunk is started when any of these
    conditions are met:
    1. An interaction's timestamp meets or exceeds the next FullSnapshot timestamp
    2. The time gap between consecutive interactions exceeds max_gap_ms
    3. The current chunk reaches max_events in size

    Args:
        interactions: List of interaction events (type == 3) sorted by timestamp
        snapshots: List of snapshot events (type == 2) sorted by timestamp

    Returns:
        List of chunks, where each chunk is a list of contiguous interaction events
        respecting all boundary conditions. If no snapshots exist, returns chunks
        based only on time gaps and size limits. If no interactions exist, returns
        an empty list.

    Example:
        interactions = [
            {"type": 3, "timestamp": 100, "data": {}},
            {"type": 3, "timestamp": 200, "data": {}},
            {"type": 3, "timestamp": 15000, "data": {}},  # Large time gap
        ]
        snapshots = [
            {"type": 2, "timestamp": 150, "data": {}},
        ]

        With max_gap_ms=10000, result: [
            [{"type": 3, "timestamp": 100, "data": {}}],  # Before snapshot
            [{"type": 3, "timestamp": 200, "data": {}}],  # Between snapshot and gap
            [{"type": 3, "timestamp": 15000, "data": {}}],  # After large gap
        ]
    """
    # Handle edge cases
    if not interactions:
        return []

    chunks = []
    current_chunk = _new_chunk()
    snapshot_iter = iter(snapshots)
    next_snapshot = next(snapshot_iter, None)
    last_timestamp = None

    for interaction in interactions:
        interaction_timestamp = get_event_timestamp(interaction)

        # Check if we need to start a new chunk due to snapshot boundary
        while next_snapshot and interaction_timestamp >= get_event_timestamp(
            next_snapshot
        ):
            # Finish current chunk if it has events
            if current_chunk["interactions"]:
                chunks.append(current_chunk)

            # Start a new chunk from the next snapshot
            current_chunk = _new_chunk(next_snapshot)

            # Reset timestamp so next interaction isn't compared against the prior chunk
            last_timestamp = None

            # Move to next snapshot
            next_snapshot = next(snapshot_iter, None)

        # Check if we need to start a new chunk due to time gap
        if (
            last_timestamp is not None
            and interaction_timestamp - last_timestamp > config.MAX_GAP_MS
        ):
            # Finish current chunk if it has events
            if current_chunk["interactions"]:
                chunks.append(current_chunk)
                current_chunk = _new_chunk()

        # Check if we need to start a new chunk due to size limit
        if len(current_chunk["interactions"]) >= config.MAX_EVENTS:
            # Finish current chunk
            chunks.append(current_chunk)
            current_chunk = _new_chunk()
            # Reset timestamp so next interaction isn't compared against the prior chunk
            last_timestamp = None

        # Add interaction to current chunk
        current_chunk["interactions"].append(interaction)
        last_timestamp = interaction_timestamp

    # Add final chunk if it has events
    if current_chunk["interactions"]:
        chunks.append(current_chunk)

    return chunks
