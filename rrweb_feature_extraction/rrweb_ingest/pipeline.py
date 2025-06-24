"""
End-to-End Ingest Pipeline for rrweb session data.

This module provides the main entry point for processing rrweb session recordings.
It orchestrates the complete pipeline from raw JSON loading through chunk normalization,
integrating all preprocessing components into a single cohesive workflow.

The pipeline performs the following steps:
1. Load and validate raw rrweb JSON data
2. Classify events into snapshots, interactions, and others
3. Segment interactions into logical chunks based on boundaries and limits
4. Filter out noise and duplicate events from each chunk
5. Normalize chunks into standardized objects with metadata

Parameters can be configured to control chunking behavior:
- max_gap_ms: Maximum time gap between events before starting new chunk
- max_events: Maximum number of events per chunk
- micro_scroll_threshold: Minimum scroll distance to be considered meaningful
"""

from typing import List, Callable, Optional

from . import config
from .loader import load_events
from .classifier import classify_events
from .segmenter import segment_into_chunks
from .filter import clean_chunk
from .normalizer import normalize_chunk
from .models import Chunk


def ingest_session(
    session_id: str,
    filepath: str,
    *,
    max_gap_ms: int = None,
    max_events: int = None,
    micro_scroll_threshold: int = None,
    custom_filters: Optional[List[Callable[[dict], bool]]] = None,
) -> List[Chunk]:
    """
    Load, classify, segment, filter, and normalize an rrweb session into Chunks.

    This is the main entry point for processing rrweb session recordings. It takes
    a raw JSON file and transforms it through the complete preprocessing pipeline
    to produce a list of normalized, cleaned chunks ready for feature extraction.

    The pipeline integrates all preprocessing components:
    1. Loads and validates the JSON session file
    2. Classifies events by type (snapshots vs interactions vs others)
    3. Segments interactions into chunks based on multiple criteria
    4. Filters noise and duplicates from each chunk
    5. Normalizes chunks with metadata and standardized identifiers

    Args:
        session_id: Unique identifier for this session, used in chunk IDs
        filepath: Path to the rrweb JSON session file to process
        max_gap_ms: Maximum time gap in milliseconds between consecutive
                   interactions before starting a new chunk (default: from config.MAX_GAP_MS)
        max_events: Maximum number of events per chunk before starting a new
                   chunk (default: from config.MAX_EVENTS)
        micro_scroll_threshold: Minimum scroll distance in pixels to be
                               considered meaningful (default: from config.MICRO_SCROLL_THRESHOLD)
        custom_filters: Optional list of additional filter functions for noise detection
                       (default: from config.DEFAULT_CUSTOM_FILTERS)

    Returns:
        List of normalized Chunk objects, each containing cleaned events and
        metadata. Chunks are ordered by their temporal sequence in the session.

    Raises:
        FileNotFoundError: If the specified filepath does not exist
        JSONDecodeError: If the file contains invalid JSON syntax
        ValueError: If the JSON structure is invalid or session_id is empty
        KeyError: If events are missing required fields

    Examples:
        >>> chunks = ingest_session(
        ...     "user_session_123",
        ...     "/path/to/session.json",
        ...     max_gap_ms=5000,
        ...     max_events=500
        ... )
        >>> len(chunks)
        3
        >>> chunks[0].chunk_id
        'user_session_123-chunk000'
        >>> chunks[0].metadata['num_events']
        45
    """
    # Apply configuration defaults if not provided
    if max_gap_ms is None:
        max_gap_ms = config.MAX_GAP_MS
    if max_events is None:
        max_events = config.MAX_EVENTS
    if micro_scroll_threshold is None:
        micro_scroll_threshold = config.MICRO_SCROLL_THRESHOLD
    if custom_filters is None:
        custom_filters = config.DEFAULT_CUSTOM_FILTERS.copy()

    # Validate session_id
    if not session_id:
        raise ValueError("session_id cannot be empty")

    # Step 1: Load and validate events from JSON file
    events = load_events(filepath)

    # Step 2: Classify events into categories
    snapshots, interactions, _ = classify_events(events)

    # Step 3: Segment interactions into raw chunks
    raw_chunks = segment_into_chunks(
        interactions, snapshots, max_gap_ms=max_gap_ms, max_events=max_events
    )

    # Step 4 & 5: Clean and normalize each chunk
    normalized_chunks = []
    for chunk_index, raw_chunk in enumerate(raw_chunks):
        # Filter noise and duplicates
        cleaned_events = clean_chunk(raw_chunk, micro_scroll_threshold, custom_filters)

        # Skip empty chunks after cleaning
        if not cleaned_events:
            continue

        # Normalize into Chunk object
        chunk = normalize_chunk(cleaned_events, session_id, chunk_index)
        normalized_chunks.append(chunk)

    return normalized_chunks
