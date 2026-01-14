"""
End-to-End Ingest Pipeline for rrweb session data.

This module provides the main entry point for processing rrweb session recordings.
It orchestrates the complete pipeline from raw JSON loading through user interaction extraction.
"""

from collections import defaultdict
import logging
from pathlib import Path
from pprint import pformat
from typing import Generator, List, Optional

from rrweb_ingest.loader import load_events
from rrweb_ingest.filter import is_low_signal
from rrweb_util import EventType
from rrweb_util.helpers import is_dom_mutation_event
from rrweb_util.dom_state.dom_state_helpers import apply_mutation, init_dom_state
from rrweb_util.user_interaction.extractors import extract_user_interactions


logger = logging.getLogger(__name__)


def ingest_session(
    session_id: str,
    filepath: Path,
) -> dict:
    """
    Load, filter, and extract user interactions from an rrweb session.

    This is the main entry point for processing rrweb session recordings. It takes
    a raw JSON file and transforms it through the complete preprocessing pipeline
    to produce a list of the user interactions from the session ready for rules matching.

    Args:
        session_id: Unique identifier for this session, used in chunk IDs
        filepath: Path to the rrweb JSON session file to process

    Returns:
        Dict w/ the session_id and user_interactions list.
        User interactions are ordered by their original event timestamps.

    Raises:
        FileNotFoundError: If the specified filepath does not exist
        JSONDecodeError: If the file contains invalid JSON syntax
        ValueError: If the JSON structure is invalid or session_id is empty
        KeyError: If events are missing required fields

    Examples:
        >>> session_data = ingest_session(
        ...     "user_session_123",
        ...     "/path/to/session.json",
        ... )
        >>> session_data['session_id']
        'user_session_123'
        >>> len(session_data['user_interactions'])
        3
    """
    # Validate session_id
    if not session_id:
        raise ValueError("session_id cannot be empty")

    # Load and validate events from JSON file
    events = load_events(filepath)

    # Walk user interaction & DOM state changes to extract events we want to pass to rule matcher
    # - If user interaction, extract that event and any relevant DOM details on the elements being interacted with
    # - If DOM state change, update our concept of the DOMs current state
    # At the end, return a list UI interactions in the session
    dom_state = None
    user_interactions = []
    for event in events:
        event_type = event["type"]

        if event_type == EventType.FULL_SNAPSHOT:
            # FullSnapshot event - initialize DOM state
            dom_state = init_dom_state(event)

        elif event_type == EventType.INCREMENTAL_SNAPSHOT:
            # IncrementalSnapshot event
            # - apply mutations to DOM state
            # - extract user interactions
            if dom_state is None:
                raise ValueError(
                    "IncrementalSnapshot event encountered before FullSnapshot"
                )

            if is_dom_mutation_event(event):
                apply_mutation(dom_state, event)
            elif not is_low_signal(event):
                user_interactions.extend(extract_user_interactions(dom_state, event))

    # Skip empty chunks after cleaning
    if not user_interactions:
        return None

    return {
        # TODO include the environment from the session metadata
        # "environment": session['metadata']['environment']
        "user_interactions": user_interactions,
        "session_id": session_id,
    }


def iterate_sessions(
    session_dir: Path, max_sessions: int = None
) -> Generator[List[Optional[dict]], None, None]:
    """
    Generator function to iterate through all rrweb session files in a directory and ingest them.

    This function scans the specified directory for rrweb JSON files, ingests
    each session using the ingest_session function, and yields user interactions processed from sessions.

    Args:
        session_dir: Directory containing rrweb session JSON files
        max_sessions: Optional limit on number of sessions to process

    Returns:
        Generator yielding processed sessions.
    """
    sessions_handled = 0
    session_files = sorted([f for f in session_dir.iterdir() if f.suffix == ".json"])

    for filepath in session_files:
        if max_sessions is not None and sessions_handled >= max_sessions:
            break


        try:
            yield ingest_session(filepath.stem, filepath)
            sessions_handled += 1
        except Exception as e:
            logger.error("Error processing %s: %s", filepath, e)
            raise


def process_sessions(
    session_dir: Path, output_dir: Path, max_sessions: int = None
) -> dict:
    """
    Process rrweb sessions from a directory and save extracted user interactions to output directory.

    This function iterates through rrweb session files, processes them to extract user interactions,
    and saves the results to the specified output directory.

    Args:
        session_dir: Directory containing rrweb session JSON files
        output_dir: Directory where processed session data will be saved
        max_sessions: Optional limit on number of sessions to process
    Returns:
        Dictionary containing processing statistics:
        - sessions_processed: Number of session files processed
        - sessions_saved: Number of session files successfully saved to output
        - total_features: Aggregate counts of each feature type
        - errors: List of any errors encountered during processing
    """
    # Initialize statistics tracking
    stats = {
        "sessions_processed": 0,
        "sessions_saved": 0,
        "total_interactions": defaultdict(int),
    }

    session_generator = iterate_sessions(session_dir, max_sessions)
    for session in session_generator:
        stats["sessions_processed"] += 1

        if session is None:
            logger.debug("Session yielded no user interactions and was skipped")
            continue

        logger.debug("Processed session: %s", session["session_id"])
        logger.debug("Extracted %d user interactions", len(session["user_interactions"]))
        logger.debug(pformat(session["user_interactions"]))

        # Update stats
        for interaction in session["user_interactions"]:
            stats["total_interactions"][interaction.action] += 1

        # TODO save the session data to output_dir as JSON file

    return stats
