#!/usr/bin/env python3
"""
Process rrweb session data from Google Cloud Storage.

This script downloads JSON files from a GCS bucket, groups them by session_guid,
merges the session data, and outputs consolidated session files.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any

from google.cloud import storage


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
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
    except json.JSONDecodeError as e:
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


def group_by_session_guid(records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
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
    
    logger.info("Grouped %d records into %d sessions", len(records), len(grouped_sessions))
    
    # Log number of files per session
    for session_guid, session_records in grouped_sessions.items():
        logger.info("Session '%s': %d files", session_guid, len(session_records))
    
    return grouped_sessions


def download_json_files(bucket_name: str) -> List[Tuple[str, str]]:
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


def _test_group_by_session_guid():
    """
    Test function for group_by_session_guid with sample data.
    """
    # Create test records with 2 different session_guid values
    test_records = [
        {
            "filename": "2025-05-02T12:10:50.644423+0000_2374",
            "session_guid": "abc-123",
            "session_data": [{"type": 1, "data": "event1"}],
            "environment": "production"
        },
        {
            "filename": "2025-05-02T12:11:30.991832+0000_2375",
            "session_guid": "abc-123",
            "session_data": [{"type": 2, "data": "event2"}],
            "environment": "production"
        },
        {
            "filename": "2025-05-02T12:12:15.123456+0000_2376",
            "session_guid": "def-456",
            "session_data": [{"type": 3, "data": "event3"}],
            "environment": "staging"
        },
        {
            "filename": "2025-05-02T12:13:45.789012+0000_2377",
            "session_guid": "abc-123",
            "session_data": [{"type": 4, "data": "event4"}],
            "environment": "production"
        },
        {
            "filename": "2025-05-02T12:14:20.456789+0000_2378",
            "session_guid": "def-456",
            "session_data": [{"type": 5, "data": "event5"}],
            "environment": "staging"
        }
    ]
    
    # Group the records
    grouped = group_by_session_guid(test_records)
    
    # Verification: print number of sessions and files in each group
    print(f"Number of sessions: {len(grouped)}")
    
    for session_guid, records in grouped.items():
        print(f"Session '{session_guid}': {len(records)} files")
        for record in records:
            print(f"  - {record['filename']}")
    
    # Verify all records are present and grouped correctly
    total_records = sum(len(records) for records in grouped.values())
    assert total_records == len(test_records), f"Expected {len(test_records)} records, got {total_records}"
    
    # Verify specific groupings
    assert len(grouped["abc-123"]) == 3, f"Expected 3 records for abc-123, got {len(grouped['abc-123'])}"
    assert len(grouped["def-456"]) == 2, f"Expected 2 records for def-456, got {len(grouped['def-456'])}"
    
    # Verify record structure is preserved
    for session_guid, records in grouped.items():
        for record in records:
            assert "filename" in record
            assert "session_guid" in record
            assert "session_data" in record
            assert "environment" in record
            assert record["session_guid"] == session_guid
    
    print("✓ All grouping tests passed!")
    return grouped


def main():
    """
    Main function demonstrating usage with example-bucket.
    """
    bucket_name = "example-bucket"

    # Download all JSON files
    files = download_json_files(bucket_name)

    # Verification: print number of JSON files found
    print(f"Number of JSON files found: {len(files)}")

    # Verification: print first 100 characters of first file content
    if files:
        first_filename, first_content = files[0]
        print(f"First file: {first_filename}")
        print(f"First 100 characters: {first_content[:100]}")

        # Demonstrate parsing and validation
        parsed_result = _parse_and_validate_session_file(first_filename, first_content)
        if parsed_result:
            print(
                f"Successfully parsed file with session_guid: {parsed_result['session_guid']}"
            )
        else:
            print("Failed to parse first file")
    else:
        print("No files found")
    
    print("\n" + "="*50)
    print("Testing group_by_session_guid function:")
    print("="*50)
    _test_group_by_session_guid()


if __name__ == "__main__":
    main()
