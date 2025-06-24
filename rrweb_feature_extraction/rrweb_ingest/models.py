"""
Data models for rrweb session processing.

This module defines the core data structures used throughout the rrweb ingestion
pipeline, including the Chunk model that represents a normalized segment of
user interaction events.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Chunk:
    """
    Represents a normalized chunk of rrweb interaction events.

    A chunk is a logical grouping of related user interaction events that occurred
    within a specific time window. Chunks are created by segmenting the raw event
    stream based on various criteria like FullSnapshot boundaries, time gaps,
    and size limits.

    Attributes:
        chunk_id: Unique identifier for the chunk in format "{session_id}-chunk{index:03d}"
        start_time: Timestamp of the first event in the chunk (milliseconds since epoch)
        end_time: Timestamp of the last event in the chunk (milliseconds since epoch)
        events: List of cleaned rrweb event dictionaries in this chunk
        metadata: Additional information about the chunk including:
                 - num_events: Number of events in the chunk
                 - duration_ms: Duration of the chunk in milliseconds (end_time - start_time)
                 - snapshot_before: Optional FullSnapshot event that preceded this chunk
    """

    chunk_id: str
    start_time: int
    end_time: int
    events: List[Dict[str, Any]]
    metadata: Dict[str, Any]

    def __post_init__(self):
        """Validate chunk data after initialization."""
        if not self.chunk_id:
            raise ValueError("chunk_id cannot be empty")

        if self.start_time < 0:
            raise ValueError("start_time must be non-negative")

        if self.end_time < self.start_time:
            raise ValueError("end_time must be >= start_time")

        if not isinstance(self.events, list):
            raise ValueError("events must be a list")

        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")
