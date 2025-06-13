"""
JSON Loader & Sorter for rrweb session data.

This module provides functionality to load, validate, and sort rrweb session recordings
from JSON files. It ensures that the data conforms to the expected schema and is properly
ordered by timestamp for downstream processing.
"""

import json
from typing import List


def load_events(filepath: str) -> List[dict]:
    """
    Load an rrweb session file, validate its structure, and return sorted events.
    
    Opens the file at the specified path, parses it as JSON, validates that it contains
    a list of properly structured rrweb events, and returns them sorted by timestamp
    in ascending order.
    
    Args:
        filepath: Path to the JSON file containing rrweb session data
        
    Returns:
        List of event dictionaries sorted by timestamp in ascending order
        
    Raises:
        FileNotFoundError: If the specified file does not exist
        JSONDecodeError: If the file contains invalid JSON syntax
        ValueError: If the JSON structure is invalid (not a list, or events missing
                   required fields 'type', 'timestamp', or 'data')
    """
    # Open and parse the JSON file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Session file not found: {filepath}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in file {filepath}: {e.msg}", e.doc, e.pos)
    
    # Validate that the top-level structure is a list
    if not isinstance(raw_data, list):
        raise ValueError("Session must be JSON array")
    
    # Validate each event has required fields
    required_fields = {"type", "timestamp", "data"}
    for i, event in enumerate(raw_data):
        if not isinstance(event, dict):
            raise ValueError(f"Event at index {i} must be an object, got {type(event).__name__}")
        
        missing_fields = required_fields - set(event.keys())
        if missing_fields:
            raise ValueError(f"Event at index {i} missing required fields: {missing_fields}")
    
    # Sort events by timestamp in ascending order
    return sorted(raw_data, key=lambda event: event["timestamp"])
