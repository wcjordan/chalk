"""
Unit tests for the JSON loader module.

Tests the load_events function to ensure it properly loads, validates, and sorts
rrweb session data from JSON files.
"""

import json
import pytest
import tempfile
import os
from rrweb_ingest.loader import load_events


class TestLoadEvents:
    """Test cases for the load_events function."""
    
    def test_load_valid_session_sorted(self):
        """Test loading a well-formed JSON session and verify sorting."""
        # Create test data with events out of timestamp order
        test_events = [
            {"type": 2, "timestamp": 1000, "data": {"source": 0}},
            {"type": 3, "timestamp": 500, "data": {"source": 1}},
            {"type": 3, "timestamp": 1500, "data": {"source": 2}},
            {"type": 1, "timestamp": 750, "data": {"source": 3}}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_events, f)
            temp_path = f.name
        
        try:
            result = load_events(temp_path)
            
            # Verify all events are present
            assert len(result) == 4
            
            # Verify events are sorted by timestamp
            timestamps = [event["timestamp"] for event in result]
            assert timestamps == [500, 750, 1000, 1500]
            
            # Verify event content is preserved
            assert result[0]["type"] == 3  # timestamp 500
            assert result[1]["type"] == 1  # timestamp 750
            assert result[2]["type"] == 2  # timestamp 1000
            assert result[3]["type"] == 3  # timestamp 1500
            
        finally:
            os.unlink(temp_path)
    
    def test_file_not_found(self):
        """Test that FileNotFoundError is raised for non-existent files."""
        with pytest.raises(FileNotFoundError, match="Session file not found"):
            load_events("/nonexistent/path/file.json")
    
    def test_malformed_json(self):
        """Test that JSONDecodeError is raised for invalid JSON syntax."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json syntax}')  # Missing quotes around 'json'
            temp_path = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError, match="Invalid JSON"):
                load_events(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_non_list_top_level(self):
        """Test that ValueError is raised when top-level JSON is not a list."""
        test_data = {"type": 2, "timestamp": 1000, "data": {}}  # Object instead of array
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Session must be JSON array"):
                load_events(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_missing_type_field(self):
        """Test that ValueError is raised when an event is missing 'type' field."""
        test_events = [
            {"timestamp": 1000, "data": {}}  # Missing 'type'
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_events, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="missing required fields.*type"):
                load_events(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_missing_timestamp_field(self):
        """Test that ValueError is raised when an event is missing 'timestamp' field."""
        test_events = [
            {"type": 2, "data": {}}  # Missing 'timestamp'
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_events, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="missing required fields.*timestamp"):
                load_events(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_missing_data_field(self):
        """Test that ValueError is raised when an event is missing 'data' field."""
        test_events = [
            {"type": 2, "timestamp": 1000}  # Missing 'data'
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_events, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="missing required fields.*data"):
                load_events(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_missing_multiple_fields(self):
        """Test that ValueError is raised when an event is missing multiple required fields."""
        test_events = [
            {"type": 2}  # Missing 'timestamp' and 'data'
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_events, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="missing required fields"):
                load_events(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_non_dict_event(self):
        """Test that ValueError is raised when an event is not a dictionary."""
        test_events = [
            "not a dictionary"  # String instead of object
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_events, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Event at index 0 must be an object"):
                load_events(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_empty_list(self):
        """Test that an empty list is handled correctly."""
        test_events = []
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_events, f)
            temp_path = f.name
        
        try:
            result = load_events(temp_path)
            assert result == []
        finally:
            os.unlink(temp_path)
    
    def test_single_event(self):
        """Test that a single event is handled correctly."""
        test_events = [
            {"type": 2, "timestamp": 1000, "data": {"source": 0}}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_events, f)
            temp_path = f.name
        
        try:
            result = load_events(temp_path)
            assert len(result) == 1
            assert result[0] == test_events[0]
        finally:
            os.unlink(temp_path)
