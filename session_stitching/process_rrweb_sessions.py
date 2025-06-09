#!/usr/bin/env python3
"""
Process rrweb session data from Google Cloud Storage.

This script downloads JSON files from a GCS bucket, groups them by session_guid,
merges the session data, and outputs consolidated session files.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Tuple, Any

from google.cloud import storage


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _initialize_gcs_client() -> storage.Client:
    """
    Initialize GCS client using Application Default Credentials.

    Returns:
        storage.Client: Authenticated GCS client
    """
    client = storage.Client()
    logger.info("Successfully initialized GCS client")
    return client


def _list_json_files(client: storage.Client, bucket_name: str) -> List[str]:
    """
    List all .json files in the specified GCS bucket (flat structure only).

    Args:
        client: Authenticated GCS client
        bucket_name: Name of the GCS bucket

    Returns:
        List[str]: List of JSON filenames
    """
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs()

    json_files = []
    for blob in blobs:
        # Only include files in root (no subdirectories)
        if "/" not in blob.name:
            json_files.append(blob.name)

    logger.info("Found %d JSON files in bucket '%s'", len(json_files), bucket_name)
    return json_files


def _download_file_content(
    client: storage.Client, bucket_name: str, filename: str
) -> str:
    """
    Download the content of a single file from GCS.

    Args:
        client: Authenticated GCS client
        bucket_name: Name of the GCS bucket
        filename: Name of the file to download

    Returns:
        str: File content as string
    """
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    content = blob.download_as_text()
    logger.debug("Successfully downloaded file: %s", filename)
    return content


def _parse_and_validate_session_file(
    filename: str, content: str
) -> Optional[Dict[str, Any]]:
    """
    Parse and validate a single session JSON file.

    Args:
        filename: Name of the file being parsed
        content: String content of the JSON file

    Returns:
        Optional[Dict[str, Any]]: Dictionary with filename, session_guid, session_data,
                                  and environment if valid, None if invalid
    """
    try:
        # Attempt to parse JSON content
        data = json.loads(content)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning("Failed to parse JSON in file '%s': %s", filename, str(e))
        return None

    # Validate that parsed object is a dictionary
    if not isinstance(data, dict):
        logger.warning(
            "File '%s' does not contain a JSON object (found %s)",
            filename,
            type(data).__name__,
        )
        return None

    return _parse_and_validate_session_file_content(filename, data)


def _parse_and_validate_session_file_content(
    filename: str, data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Validate the content of a session file.
    Args:
        filename: Name of the file being validated
        data: Parsed JSON data as a dictionary
    Returns:
        Optional[Dict[str, Any]]: Dictionary with filename, session_guid, session_data,
                                  and environment if valid, None if invalid
    """
    # Check for required fields
    required_fields = ["session_guid", "session_data", "environment"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        logger.warning(
            "File '%s' missing required fields: %s", filename, ", ".join(missing_fields)
        )
        return None

    # Validate field types
    session_guid = data["session_guid"]
    session_data = data["session_data"]
    environment = data["environment"]

    # session_guid must be a non-empty string
    if not isinstance(session_guid, str) or not session_guid.strip():
        logger.warning(
            "File '%s' has invalid session_guid: must be non-empty string", filename
        )
        return None

    # session_data must be a list
    if not isinstance(session_data, list):
        logger.warning(
            "File '%s' has invalid session_data: must be a list (found %s)",
            filename,
            type(session_data).__name__,
        )
        return None

    # environment must be a non-empty string
    if not isinstance(environment, str) or not environment.strip():
        logger.warning(
            "File '%s' has invalid environment: must be non-empty string (found %s)",
            filename,
            type(environment).__name__,
        )
        return None

    # Return validated data
    return {
        "filename": filename,
        "session_guid": session_guid,
        "session_data": session_data,
        "environment": environment,
    }


def _group_by_session_guid(
    records: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group validated session records by session_guid.

    Args:
        records: List of validated session record dictionaries

    Returns:
        Dict[str, List[Dict[str, Any]]]: Dictionary where keys are session_guid strings
                                         and values are lists of records for that session
    """
    grouped_sessions = {}

    for record in records:
        session_guid = record["session_guid"]

        if session_guid not in grouped_sessions:
            grouped_sessions[session_guid] = []

        grouped_sessions[session_guid].append(record)

    logger.info(
        "Grouped %d records into %d sessions", len(records), len(grouped_sessions)
    )

    # Log number of files per session
    for session_guid, session_records in grouped_sessions.items():
        logger.info("Session '%s': %d files", session_guid, len(session_records))

    return grouped_sessions


def _sort_and_collect_timestamps(
    grouped_sessions: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Dict[str, Any]]:
    """
    Sort session entries by filename and collect timestamps.

    Args:
        grouped_sessions: Dictionary mapping session_guid to list of session records

    Returns:
        Dict[str, Dict[str, Any]]: Dictionary with session_guid as keys and values containing:
                                   - sorted_entries: list of records sorted by filename
                                   - timestamp_list: list of timestamps extracted from filenames
    """
    sorted_sessions = {}

    for session_guid, session_records in grouped_sessions.items():
        # Sort entries by filename (lexicographically, assuming timestamp-based filenames)
        sorted_entries = sorted(session_records, key=lambda record: record["filename"])

        # Extract timestamps from sorted filenames
        timestamp_list = [record["filename"] for record in sorted_entries]

        sorted_sessions[session_guid] = {
            "sorted_entries": sorted_entries,
            "timestamp_list": timestamp_list,
        }

        logger.info(
            "Session '%s': sorted %d entries by timestamp",
            session_guid,
            len(sorted_entries),
        )

    logger.info("Sorted and collected timestamps for %d sessions", len(sorted_sessions))
    return sorted_sessions


def _validate_and_extract_environment(
    sessions: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """
    Validate and deduplicate environment values per session.

    Args:
        sessions: Dictionary mapping session_guid to session data containing
                 sorted_entries and timestamp_list

    Returns:
        Dict[str, Dict[str, Any]]: Dictionary with session_guid as keys and values containing:
                                   - sorted_entries: preserved from input
                                   - timestamp_list: preserved from input
                                   - environment: deduplicated and validated environment value
    """
    validated_sessions = {}

    for session_guid, session_data in sessions.items():
        sorted_entries = session_data["sorted_entries"]
        timestamp_list = session_data["timestamp_list"]

        # Extract all environment values from entries
        environment_values = [entry["environment"] for entry in sorted_entries]

        # Get unique environment values
        unique_environments = list(set(environment_values))

        # Use the first environment value as canonical
        canonical_environment = environment_values[0] if environment_values else ""

        # Log warning if multiple distinct environment values found
        if len(unique_environments) > 1:
            logger.warning(
                "Session '%s' has conflicting environment values: %s. Using first value: '%s'",
                session_guid,
                unique_environments,
                canonical_environment,
            )

        validated_sessions[session_guid] = {
            "sorted_entries": sorted_entries,
            "timestamp_list": timestamp_list,
            "environment": canonical_environment,
        }

        logger.debug(
            "Session '%s': validated environment as '%s'",
            session_guid,
            canonical_environment,
        )

    logger.info(
        "Validated and extracted environment for %d sessions", len(validated_sessions)
    )
    return validated_sessions


def _download_json_files(bucket_name: str) -> List[Tuple[str, str]]:
    """
    Download all JSON files from the specified GCS bucket.

    Args:
        bucket_name: Name of the GCS bucket

    Returns:
        List[Tuple[str, str]]: List of (filename, file_content) pairs
    """
    client = _initialize_gcs_client()
    json_files = _list_json_files(client, bucket_name)

    file_contents = []
    for filename in json_files:
        content = _download_file_content(client, bucket_name, filename)
        file_contents.append((filename, content))

    logger.info("Successfully downloaded %d files", len(file_contents))
    return file_contents


def _merge_session_data(
    sessions: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """
    Merge session_data arrays from sorted session entries into final output format.

    Args:
        sessions: Dictionary mapping session_guid to session data containing:
                 - sorted_entries: list of validated and chronologically ordered records
                 - timestamp_list: list of timestamps for the session
                 - environment: canonical environment string for the session

    Returns:
        Dict[str, Dict[str, Any]]: Dictionary with session_guid as keys and values containing:
                                   - session_guid: the session identifier
                                   - rrweb_data: merged list of rrweb events
                                   - metadata: dict with environment and timestamp_list
    """
    merged_sessions = {}

    for session_guid, session_data in sessions.items():
        sorted_entries = session_data["sorted_entries"]
        timestamp_list = session_data["timestamp_list"]
        environment = session_data["environment"]

        # Merge all session_data arrays in chronological order
        rrweb_data = []
        for entry in sorted_entries:
            rrweb_data.extend(entry["session_data"])

        # Create final session structure
        merged_sessions[session_guid] = {
            "session_guid": session_guid,
            "rrweb_data": rrweb_data,
            "metadata": {
                "environment": environment,
                "timestamp_list": timestamp_list,
            },
        }

        logger.info(
            "Session '%s': merged %d events from %d files",
            session_guid,
            len(rrweb_data),
            len(sorted_entries),
        )

    logger.info("Merged session data for %d sessions", len(merged_sessions))
    return merged_sessions


def write_sessions_to_disk(
    sessions: Dict[str, Dict[str, Any]], output_dir: str
) -> None:
    """
    Write session objects to disk as compact JSON files.

    Args:
        sessions: Dictionary mapping session_guid to session objects containing:
                 - session_guid: the session identifier
                 - rrweb_data: merged list of rrweb events
                 - metadata: dict with environment and timestamp_list
        output_dir: Directory path where session files should be written

    Each session is written to <output_dir>/<session_guid>.json in compact format.
    The output directory is created if it doesn't exist.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    logger.info("Created output directory: %s", output_dir)

    for session_guid, session_data in sessions.items():
        # Create filename from session_guid
        filename = f"{session_guid}.json"
        filepath = os.path.join(output_dir, filename)

        # Write session data as compact JSON (no whitespace, no indentation)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(session_data, f, separators=(",", ":"), ensure_ascii=False)

        logger.info("Wrote session '%s' to %s", session_guid, filepath)

    logger.info("Successfully wrote %d sessions to %s", len(sessions), output_dir)


def process_rrweb_sessions(bucket_name: str) -> Dict[str, Dict[str, Any]]:
    """
    Main function for processing rrweb session data.
    This function orchestrates the downloading, parsing, grouping, sorting,
    validating, and merging of session files from a GCS bucket.

    Args:
        bucket_name: Name of the GCS bucket containing rrweb session JSON files

    Returns:
        Dict[str, Dict[str, Any]]: Dictionary mapping session_guid to final session objects
    """
    # Download all JSON files
    files = _download_json_files(bucket_name)
    logger.info("Number of JSON files found: %d", len(files))

    # Verification: print first 100 characters of first file content
    parsed_files = []
    if not files:
        logger.warning("No files found")

    # Parse and validate each session file
    parsed_files = [
        _parse_and_validate_session_file(filename, content)
        for filename, content in files
    ]
    parsed_files = [entry for entry in parsed_files if entry is not None]

    # Group by session_guid
    grouped_sessions = _group_by_session_guid(parsed_files)
    logger.info("Number of grouped sessions: %d", len(grouped_sessions))

    # Sort by timestamp
    sorted_sessions = _sort_and_collect_timestamps(grouped_sessions)
    logger.info("Number of sorted sessions: %d", len(sorted_sessions))

    # Validate each session has the same environment
    validated_sessions = _validate_and_extract_environment(sorted_sessions)
    logger.info("Number of validated sessions: %d", len(validated_sessions))

    # Merge session data arrays
    final_sessions = _merge_session_data(validated_sessions)
    logger.info("Number of final sessions: %d", len(final_sessions))

    return final_sessions


if __name__ == "__main__":
    EXAMPLE_BUCKET = "example-bucket-name"
    session_output = process_rrweb_sessions(EXAMPLE_BUCKET)
    logger.info("Output: %s", session_output)
