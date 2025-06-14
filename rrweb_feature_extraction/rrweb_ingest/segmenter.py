"""
Basic Chunk Segmentation for rrweb session data.

This module provides functionality to segment interaction events into logical chunks
based on FullSnapshot boundaries. Chunks represent meaningful units of user activity
that can be processed independently for feature extraction.
"""

from typing import List


def segment_into_chunks(
    interactions: List[dict], snapshots: List[dict]
) -> List[List[dict]]:
    """
    Segment interaction events into chunks based on FullSnapshot boundaries.

    Takes sorted lists of interaction events (type == 3) and snapshot events (type == 2)
    and groups interactions into chunks. A new chunk is started whenever an interaction's
    timestamp meets or exceeds the next FullSnapshot timestamp.

    Args:
        interactions: List of interaction events (type == 3) sorted by timestamp
        snapshots: List of snapshot events (type == 2) sorted by timestamp

    Returns:
        List of chunks, where each chunk is a list of contiguous interaction events
        between snapshot boundaries. If no snapshots exist, returns a single chunk
        containing all interactions. If no interactions exist, returns an empty list.

    Example:
        interactions = [
            {"type": 3, "timestamp": 100, "data": {}},
            {"type": 3, "timestamp": 200, "data": {}},
            {"type": 3, "timestamp": 400, "data": {}},
        ]
        snapshots = [
            {"type": 2, "timestamp": 150, "data": {}},
            {"type": 2, "timestamp": 350, "data": {}},
        ]

        Result: [
            [{"type": 3, "timestamp": 100, "data": {}}],  # Before first snapshot
            [{"type": 3, "timestamp": 200, "data": {}}],  # Between snapshots
            [{"type": 3, "timestamp": 400, "data": {}}],  # After last snapshot
        ]
    """
    # Handle edge cases
    if not interactions:
        return []

    if not snapshots:
        return [interactions]

    chunks = []
    current_chunk = []
    snapshot_iter = iter(snapshots)
    next_snapshot = next(snapshot_iter, None)

    for interaction in interactions:
        interaction_timestamp = interaction["timestamp"]

        # Check if we need to start a new chunk due to snapshot boundary
        while next_snapshot and interaction_timestamp >= next_snapshot["timestamp"]:
            # Finish current chunk if it has events
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = []

            # Move to next snapshot
            next_snapshot = next(snapshot_iter, None)

        # Add interaction to current chunk
        current_chunk.append(interaction)

    # Add final chunk if it has events
    if current_chunk:
        chunks.append(current_chunk)

    return chunks
