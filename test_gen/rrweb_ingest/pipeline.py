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

import logging
import os
from typing import Generator, List

from rrweb_ingest.loader import load_events
from rrweb_ingest.classifier import classify_events
from rrweb_ingest.filter import clean_chunk
from rrweb_ingest.normalizer import normalize_chunk
from rrweb_ingest.models import Chunk

logger = logging.getLogger(__name__)


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

    # Load and validate events from JSON file
    events = load_events(filepath)

    # # Classify events into categories
    # snapshots, interactions, _ = classify_events(events)

    # Filter noise and duplicates
    cleaned_events = clean_chunk(events)

    # Skip empty chunks after cleaning
    if not cleaned_events:
        return None

    # Normalize into Chunk object
    return normalize_chunk(cleaned_events, session_id)


def iterate_sessions(
    session_dir: str, max_sessions: int = None
) -> Generator[List[Chunk], None, None]:
    """
    Generator function to iterate through all rrweb session files in a directory and ingest them.

    This function scans the specified directory for rrweb JSON files, ingests
    each session using the ingest_session function, and yields all
    normalized chunks from all sessions.

    Args:
        session_dir: Directory containing rrweb session JSON files
        max_sessions: Optional limit on number of sessions to process

    Returns:
        Generator yielding all normalized Chunk objects from processed sessions.
    """
    sessions_handled = 0
    session_files = sorted([f for f in os.listdir(session_dir) if f.endswith(".json")])

    for filename in session_files:
        if max_sessions is not None and sessions_handled >= max_sessions:
            break

        session_id = filename.split(".")[0]
        filepath = os.path.join(session_dir, filename)
        try:
            yield ingest_session(session_id, filepath)
            sessions_handled += 1
        except Exception as e:
            logger.error("Error processing %s: %s", filename, e)
            raise
