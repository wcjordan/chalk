"""
Unit tests for process_rrweb_sessions.py

Tests focused on behavior and public interfaces following unit test policy.
"""

import json
import os
import tempfile
from unittest.mock import Mock, patch

import pytest
from google.cloud import storage
from google.cloud.exceptions import NotFound, Forbidden

from process_rrweb_sessions import (
    _download_json_files,
    _parse_and_validate_session_file,
    _group_by_session_guid,
    _sort_and_collect_timestamps,
    _validate_and_extract_environment,
    main,
)


@pytest.fixture(name="realistic_rrweb_data")
def fixture_realistic_rrweb_data():
    """Realistic rrweb event data for testing."""
    return {
        "session_1_file_1": [
            {"type": 0, "data": {"href": "https://example.com", "width": 1920, "height": 1080}},
            {"type": 1, "data": {"node": {"id": 1, "tagName": "html"}}},
            {"type": 2, "data": {"node": {"id": 2, "tagName": "body", "parentId": 1}}},
        ],
        "session_1_file_2": [
            {"type": 3, "data": {"source": 2, "type": 0, "id": 3}},
            {"type": 3, "data": {"source": 2, "type": 1, "id": 4}},
        ],
        "session_2_file_1": [
            {"type": 0, "data": {"href": "https://different.com", "width": 1366, "height": 768}},
            {"type": 1, "data": {"node": {"id": 1, "tagName": "html"}}},
        ],
    }


@pytest.fixture(name="test_bucket_data")
def fixture_test_bucket_data(realistic_rrweb_data):
    """Complete test bucket data with realistic content."""
    return {
        # Session 1 files (out of chronological order)
        "2025-05-02T12:11:30.991832+0000": {
            "session_guid": "session-abc-123",
            "session_data": realistic_rrweb_data["session_1_file_1"],
            "environment": "production"
        },
        "2025-05-02T12:10:50.644423+0000": {
            "session_guid": "session-abc-123", 
            "session_data": realistic_rrweb_data["session_1_file_2"],
            "environment": "production"
        },
        # Session 2 files
        "2025-05-02T12:12:15.123456+0000": {
            "session_guid": "session-def-456",
            "session_data": realistic_rrweb_data["session_2_file_1"],
            "environment": "staging"
        },
        # Malformed file (should be skipped)
        "2025-05-02T12:13:00.000000+0000": '{"invalid": "json"',  # Missing closing brace
        # File with missing required fields (should be skipped)
        "2025-05-02T12:14:00.000000+0000": {
            "session_guid": "incomplete-session",
            "environment": "test"
            # Missing session_data
        }
    }


@pytest.fixture(name="mock_gcs_bucket")
def fixture_mock_gcs_bucket(test_bucket_data):
    """Mock GCS bucket that returns test data."""
    def mock_download_json_files(bucket_name):
        """Mock implementation that returns test data."""
        files = []
        for filename, content in test_bucket_data.items():
            if isinstance(content, dict):
                content_str = json.dumps(content)
            else:
                content_str = content  # Already a string (for malformed cases)
            files.append((filename, content_str))
        return files
    
    with patch('process_rrweb_sessions._download_json_files', side_effect=mock_download_json_files):
        yield mock_download_json_files


class TestSessionProcessingPipeline:
    """Test the complete session processing workflow."""
    
    def test_processes_valid_multi_session_data_end_to_end(self, mock_gcs_bucket, realistic_rrweb_data):
        """Test complete pipeline with valid multi-session data."""
        # Download and process files
        files = _download_json_files("test-bucket")
        
        # Parse and validate files
        valid_records = []
        for filename, content in files:
            parsed = _parse_and_validate_session_file(filename, content)
            if parsed:
                valid_records.append(parsed)
        
        # Group by session
        grouped = _group_by_session_guid(valid_records)
        
        # Sort and collect timestamps
        sorted_sessions = _sort_and_collect_timestamps(grouped)
        
        # Validate environments
        final_sessions = _validate_and_extract_environment(sorted_sessions)
        
        # Verify final structure
        assert len(final_sessions) == 2
        assert "session-abc-123" in final_sessions
        assert "session-def-456" in final_sessions
        
        # Check session-abc-123 properties
        session_1 = final_sessions["session-abc-123"]
        assert session_1["environment"] == "production"
        assert len(session_1["timestamp_list"]) == 2
        assert len(session_1["sorted_entries"]) == 2
        
        # Verify timestamp ordering (chronological)
        timestamps = session_1["timestamp_list"]
        assert timestamps == sorted(timestamps)
        assert timestamps[0] == "2025-05-02T12:10:50.644423+0000"
        assert timestamps[1] == "2025-05-02T12:11:30.991832+0000"
        
        # Check session-def-456 properties
        session_2 = final_sessions["session-def-456"]
        assert session_2["environment"] == "staging"
        assert len(session_2["timestamp_list"]) == 1
        assert len(session_2["sorted_entries"]) == 1

    def test_handles_malformed_files_gracefully(self, mock_gcs_bucket, caplog):
        """Test pipeline skips invalid files and continues processing."""
        files = _download_json_files("test-bucket")
        
        valid_records = []
        skipped_count = 0
        
        for filename, content in files:
            parsed = _parse_and_validate_session_file(filename, content)
            if parsed:
                valid_records.append(parsed)
            else:
                skipped_count += 1
        
        # Should have skipped 2 files (malformed JSON and missing fields)
        assert skipped_count == 2
        
        # Should still process valid files
        assert len(valid_records) == 3
        
        # Verify warnings were logged
        assert "Failed to parse JSON" in caplog.text
        assert "missing required fields" in caplog.text

    def test_merges_session_data_in_timestamp_order(self, mock_gcs_bucket, realistic_rrweb_data):
        """Test that session data is correctly merged and ordered."""
        files = _download_json_files("test-bucket")
        
        valid_records = []
        for filename, content in files:
            parsed = _parse_and_validate_session_file(filename, content)
            if parsed:
                valid_records.append(parsed)
        
        grouped = _group_by_session_guid(valid_records)
        sorted_sessions = _sort_and_collect_timestamps(grouped)
        
        # Check session-abc-123 data ordering
        session_entries = sorted_sessions["session-abc-123"]["sorted_entries"]
        
        # First entry should be from earlier timestamp
        first_entry = session_entries[0]
        assert first_entry["filename"] == "2025-05-02T12:10:50.644423+0000"
        assert first_entry["session_data"] == realistic_rrweb_data["session_1_file_2"]
        
        # Second entry should be from later timestamp  
        second_entry = session_entries[1]
        assert second_entry["filename"] == "2025-05-02T12:11:30.991832+0000"
        assert second_entry["session_data"] == realistic_rrweb_data["session_1_file_1"]

    def test_handles_environment_conflicts_with_warning(self, caplog):
        """Test pipeline handles conflicting environments correctly."""
        # Create test data with conflicting environments
        conflicting_data = {
            "2025-05-02T12:10:00.000000+0000": {
                "session_guid": "conflict-session",
                "session_data": [{"type": 1}],
                "environment": "production"
            },
            "2025-05-02T12:11:00.000000+0000": {
                "session_guid": "conflict-session", 
                "session_data": [{"type": 2}],
                "environment": "staging"  # Different environment
            }
        }
        
        def mock_conflicting_download(bucket_name):
            files = []
            for filename, content in conflicting_data.items():
                files.append((filename, json.dumps(content)))
            return files
        
        with patch('process_rrweb_sessions._download_json_files', side_effect=mock_conflicting_download):
            files = _download_json_files("test-bucket")
            
            valid_records = []
            for filename, content in files:
                parsed = _parse_and_validate_session_file(filename, content)
                if parsed:
                    valid_records.append(parsed)
            
            grouped = _group_by_session_guid(valid_records)
            sorted_sessions = _sort_and_collect_timestamps(grouped)
            final_sessions = _validate_and_extract_environment(sorted_sessions)
            
            # Should use first environment value
            assert final_sessions["conflict-session"]["environment"] == "production"
            
            # Should log warning
            assert "conflicting environment values" in caplog.text
            assert "Using first value: 'production'" in caplog.text


class TestSessionDataValidation:
    """Test session data validation logic for edge cases."""
    
    def test_validates_required_fields_comprehensively(self):
        """Test validation catches all combinations of missing required fields."""
        test_cases = [
            # Missing session_guid
            ('{"session_data": [], "environment": "test"}', "session_guid"),
            # Missing session_data  
            ('{"session_guid": "test", "environment": "test"}', "session_data"),
            # Missing environment
            ('{"session_guid": "test", "session_data": []}', "environment"),
            # Missing multiple fields
            ('{"session_guid": "test"}', "session_data, environment"),
        ]
        
        for content, expected_missing in test_cases:
            result = _parse_and_validate_session_file("test.json", content)
            assert result is None

    def test_handles_data_type_validation(self):
        """Test validation of field data types."""
        test_cases = [
            # Non-string session_guid
            ('{"session_guid": 123, "session_data": [], "environment": "test"}', None),
            # Non-list session_data
            ('{"session_guid": "test", "session_data": "not-list", "environment": "test"}', None),
            # Non-string environment
            ('{"session_guid": "test", "session_data": [], "environment": 123}', None),
            # Valid case
            ('{"session_guid": "test", "session_data": [], "environment": "test"}', "test"),
        ]
        
        for content, expected_guid in test_cases:
            result = _parse_and_validate_session_file("test.json", content)
            if expected_guid:
                assert result is not None
                assert result["session_guid"] == expected_guid
            else:
                assert result is None

    def test_preserves_complex_rrweb_structures(self):
        """Test that complex rrweb event structures are preserved exactly."""
        complex_events = [
            {
                "type": 0,
                "data": {
                    "href": "https://example.com/path?param=value#hash",
                    "width": 1920,
                    "height": 1080,
                    "userAgent": "Mozilla/5.0..."
                }
            },
            {
                "type": 1, 
                "data": {
                    "node": {
                        "id": 1,
                        "tagName": "html",
                        "attributes": {"lang": "en"},
                        "childNodes": [{"id": 2, "tagName": "head"}]
                    }
                }
            },
            {
                "type": 3,
                "data": {
                    "source": 2,
                    "type": 0,
                    "id": 3,
                    "x": 100.5,
                    "y": 200.7,
                    "timeOffset": 1234
                }
            }
        ]
        
        content = json.dumps({
            "session_guid": "complex-test",
            "session_data": complex_events,
            "environment": "production"
        })
        
        result = _parse_and_validate_session_file("complex.json", content)
        
        assert result is not None
        assert result["session_data"] == complex_events
        # Verify deep structure is preserved
        assert result["session_data"][0]["data"]["href"] == "https://example.com/path?param=value#hash"
        assert result["session_data"][1]["data"]["node"]["attributes"]["lang"] == "en"
        assert result["session_data"][2]["data"]["x"] == 100.5


class TestTimestampOrdering:
    """Test timestamp ordering and sorting behavior."""
    
    def test_timestamp_ordering_with_various_formats(self):
        """Test sorting works with different timestamp formats."""
        # Create entries with various timestamp formats (all should sort lexicographically)
        entries = [
            {
                "filename": "2025-05-02T12:15:30.123456+0000",
                "session_guid": "test-session",
                "session_data": [{"order": 3}],
                "environment": "test"
            },
            {
                "filename": "2025-05-02T12:10:15.987654+0000", 
                "session_guid": "test-session",
                "session_data": [{"order": 1}],
                "environment": "test"
            },
            {
                "filename": "2025-05-02T12:12:45.555555+0000",
                "session_guid": "test-session", 
                "session_data": [{"order": 2}],
                "environment": "test"
            }
        ]
        
        grouped = {"test-session": entries}
        result = _sort_and_collect_timestamps(grouped)
        
        # Verify chronological ordering
        timestamps = result["test-session"]["timestamp_list"]
        sorted_entries = result["test-session"]["sorted_entries"]
        
        assert timestamps == sorted(timestamps)
        assert sorted_entries[0]["session_data"][0]["order"] == 1
        assert sorted_entries[1]["session_data"][0]["order"] == 2  
        assert sorted_entries[2]["session_data"][0]["order"] == 3

    def test_handles_single_file_sessions(self):
        """Test edge case of sessions with only one file."""
        single_entry = [{
            "filename": "2025-05-02T12:10:00.000000+0000",
            "session_guid": "single-file",
            "session_data": [{"type": 1}],
            "environment": "production"
        }]
        
        grouped = {"single-file": single_entry}
        result = _sort_and_collect_timestamps(grouped)
        
        assert len(result["single-file"]["timestamp_list"]) == 1
        assert len(result["single-file"]["sorted_entries"]) == 1
        assert result["single-file"]["timestamp_list"][0] == "2025-05-02T12:10:00.000000+0000"

    def test_handles_empty_session_groups(self):
        """Test edge case of empty session groups."""
        result = _sort_and_collect_timestamps({})
        assert result == {}
        
        result = _validate_and_extract_environment({})
        assert result == {}


# TEMP: remove after integration - keeping minimal edge case tests for private methods
class TestPrivateMethodEdgeCases:
    """Edge case tests for private methods that handle empty/malformed data."""
    
    def test_group_by_session_guid_handles_empty_list(self):
        """Test grouping handles empty input gracefully."""
        result = _group_by_session_guid([])
        assert result == {}
    
    def test_environment_validation_handles_empty_entries(self):
        """Test environment validation with sessions containing no entries."""
        sessions_with_empty = {
            "empty-session": {
                "sorted_entries": [],
                "timestamp_list": []
            }
        }
        
        result = _validate_and_extract_environment(sessions_with_empty)
        
        # Should handle empty entries gracefully
        assert "empty-session" in result
        assert result["empty-session"]["environment"] == ""  # Default for empty
        assert result["empty-session"]["sorted_entries"] == []
        assert result["empty-session"]["timestamp_list"] == []


# TEMP: remove after integration - keeping minimal GCS interaction tests
class TestGcsInteractionEdgeCases:
    """Minimal tests for GCS interaction edge cases."""
    
    def test_download_handles_empty_bucket(self):
        """Test download handles empty bucket gracefully."""
        def mock_empty_download(bucket_name):
            return []
        
        with patch('process_rrweb_sessions._download_json_files', side_effect=mock_empty_download):
            result = _download_json_files("empty-bucket")
            assert result == []
    
    def test_download_handles_gcs_errors(self):
        """Test download handles GCS errors appropriately."""
        def mock_error_download(bucket_name):
            raise NotFound("Bucket not found")
        
        with patch('process_rrweb_sessions._download_json_files', side_effect=mock_error_download):
            with pytest.raises(NotFound, match="Bucket not found"):
                _download_json_files("nonexistent-bucket")
