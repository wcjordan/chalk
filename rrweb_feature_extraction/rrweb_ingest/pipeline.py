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
"""
import os
from collections import defaultdict
import sys
from typing import List

from rrweb_ingest.loader import load_events
from rrweb_ingest.classifier import classify_events
from rrweb_ingest.segmenter import segment_into_chunks
from rrweb_ingest.filter import clean_chunk
from rrweb_ingest.normalizer import normalize_chunk
from rrweb_ingest.models import Chunk


def ingest_session(
    session_id: str,
    filepath: str,
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
        ... )
        >>> len(chunks)
        3
        >>> chunks[0].chunk_id
        'user_session_123-chunk000'
        >>> chunks[0].metadata['num_events']
        45
    """
    # Validate session_id
    if not session_id:
        raise ValueError("session_id cannot be empty")

    # Step 1: Load and validate events from JSON file
    events = load_events(filepath)

    # Step 2: Classify events into categories
    snapshots, interactions, _ = classify_events(events)

    # Step 3: Segment interactions into raw chunks
    raw_chunks = segment_into_chunks(interactions, snapshots)

    # Step 4 & 5: Clean and normalize each chunk
    normalized_chunks = []
    for chunk_index, raw_chunk in enumerate(raw_chunks):
        # Filter noise and duplicates
        cleaned_events = clean_chunk(raw_chunk)

        # Skip empty chunks after cleaning
        if not cleaned_events:
            continue

        # Normalize into Chunk object
        chunk = normalize_chunk(cleaned_events, session_id, chunk_index)
        normalized_chunks.append(chunk)

    return normalized_chunks


if __name__ == "__main__":
    session_path = "../session_stitching/output_sessions"
    chunk_sizes = defaultdict(int)
    for filename in os.listdir(session_path):
        if filename.endswith(".json"):
            session_id = filename.split(".")[0]
            filepath = os.path.join(session_path, filename)
            try:
                chunks = ingest_session(session_id, filepath)
                chunk_sizes[len(chunks)] += 1
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    print("Chunk size distribution:")
    for size, count in sorted(chunk_sizes.items()):
        print(f"{size} events: {count} sessions")
    print(f"Total sessions processed: {sum(chunk_sizes.values())}")
