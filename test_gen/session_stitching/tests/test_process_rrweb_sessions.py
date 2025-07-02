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
from google.cloud.exceptions import NotFound

from session_stitching.process_rrweb_sessions import (
    _initialize_gcs_client,
    _download_json_files,
    _parse_and_validate_session_file,
    _group_by_session_guid,
    _sort_and_collect_timestamps,
    _validate_and_extract_environment,
    _merge_session_data,
    _write_sessions_to_disk,
    process_rrweb_sessions,
)

SESSION_1_KEY = "session-abc-123"
SESSION_2_KEY = "session-def-456"


@pytest.fixture(name="sample_rrweb_data")
def fixture_sample_rrweb_data():
    """Sample rrweb event data for testing."""
    return {
        "session_1_file_1": [
            {
                "type": 0,
                "data": {"href": "https://example.com", "width": 1920, "height": 1080},
            },
            {"type": 1, "data": {"node": {"id": 1, "tagName": "html"}}},
            {"type": 2, "data": {"node": {"id": 2, "tagName": "body", "parentId": 1}}},
        ],
        "session_1_file_2": [
            {"type": 3, "data": {"source": 2, "type": 0, "id": 3}},
            {"type": 3, "data": {"source": 2, "type": 1, "id": 4}},
        ],
        "session_2_file_1": [
            {
                "type": 0,
                "data": {"href": "https://different.com", "width": 1366, "height": 768},
            },
            {"type": 1, "data": {"node": {"id": 1, "tagName": "html"}}},
        ],
    }


@pytest.fixture(name="sample_bucket_data")
def fixture_sample_bucket_data(sample_rrweb_data):
    """Complete test bucket data with sample content."""
    return {
        # Session 1 files (out of chronological order)
        "2025-05-02T12:11:30.991832+0000": {
            "session_guid": SESSION_1_KEY,
            "session_data": sample_rrweb_data["session_1_file_1"],
            "environment": "production",
        },
        "2025-05-02T12:10:50.644423+0000": {
            "session_guid": SESSION_1_KEY,
            "session_data": sample_rrweb_data["session_1_file_2"],
            "environment": "production",
        },
        # Session 2 files
        "2025-05-02T12:12:15.123456+0000": {
            "session_guid": SESSION_2_KEY,
            "session_data": sample_rrweb_data["session_2_file_1"],
            "environment": "staging",
        },
        # Malformed JSON (should be skipped)
        "2025-05-02T12:13:00.000000+0000": '{"invalid": "json"',  # Missing closing brace
        # Non dict (should be skipped)
        "2025-05-02T12:14:00.000000+0000": ["session_guid", "session_data"],  # List
        "2025-05-02T12:15:00.000000+0000": '"session_data"',  # String
        # File with missing required fields (should be skipped)
        "2025-05-02T12:16:00.000000+0000": {
            "session_guid": "incomplete-session",
            "environment": "test",
            # Missing session_data
        },
        # Non root files should be ignored
        "ignored/2025-05-02T12:17:00.000000+0000": {
            "session_guid": SESSION_2_KEY,
            "session_data": sample_rrweb_data["session_1_file_1"],
            "environment": "development",
        },
    }


@pytest.fixture(name="mock_client_class", autouse=True)
def fixture_mock_client_class(mock_gcs_client):
    """Mock class for GCS client to be used in tests."""
    with patch(
        "session_stitching.process_rrweb_sessions.storage.Client",
        return_value=mock_gcs_client,
    ) as client_class:
        yield client_class


@pytest.fixture(name="mock_gcs_client")
def fixture_mock_gcs_client(mock_bucket):
    """Mock GCS client for testing."""
    mock_gcs_client = Mock(spec=storage.Client)
    mock_gcs_client.bucket.return_value = mock_bucket
    return mock_gcs_client


@pytest.fixture(name="custom_mock_bucket")
def fixture_custom_mock_bucket():
    """Custom mock bucket factory to create buckets with specific data."""

    def get_mock_blob(blob_name, content):
        """Create a mock blob with specified name and content."""
        mock_blob = Mock(spec=storage.Blob)
        mock_blob.name = blob_name
        mock_blob.download_as_text.return_value = (
            json.dumps(content) if isinstance(content, dict) else content
        )
        return mock_blob

    def mock_blobs_from_items(bucket_data):
        mock_bucket = Mock(spec=storage.Bucket)

        mock_blobs = []
        for filename, content in bucket_data.items():
            mock_blob = get_mock_blob(filename, content)
            mock_blobs.append(mock_blob)

        def mock_get_blob(filename):
            """Mock method to return a blob by name."""
            for blob_name, blob_content in bucket_data.items():
                if blob_name == filename:
                    return get_mock_blob(blob_name, blob_content)
            return None

        mock_bucket.list_blobs.return_value = mock_blobs
        mock_bucket.blob.side_effect = mock_get_blob
        return mock_bucket

    return mock_blobs_from_items


@pytest.fixture(name="mock_bucket")
def fixture_mock_bucket(custom_mock_bucket, sample_bucket_data):
    """Mock GCS bucket that returns test data."""
    return custom_mock_bucket(sample_bucket_data)


@pytest.fixture(name="temp_output_dir")
def fixture_temp_output_dir():
    """Temporary output directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


class TestSessionProcessingPipeline:
    """Test the complete session processing workflow."""

    def test_process_rrweb_sessions_happy_path(self, caplog, temp_output_dir):
        """Test complete pipeline with valid multi-session data."""
        with caplog.at_level("INFO"):
            process_rrweb_sessions("mock_bucket_name", temp_output_dir)

        # Verify files were created with correct names
        sessions = [SESSION_1_KEY, SESSION_2_KEY]
        expected_filenames = [f"{session}.json" for session in sessions]
        actual_files = os.listdir(temp_output_dir)
        assert sorted(actual_files) == expected_filenames

        # Verify file contents
        for filename in expected_filenames:
            filepath = os.path.join(temp_output_dir, filename)
            assert os.path.exists(filepath)

            with open(filepath, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)

                assert "rrweb_data" in loaded_data
                assert "metadata" in loaded_data

                if filename == f"{SESSION_1_KEY}.json":
                    # Check SESSION_1 properties
                    assert loaded_data["session_guid"] == SESSION_1_KEY
                    assert loaded_data["metadata"]["environment"] == "production"
                    assert len(loaded_data["metadata"]["timestamp_list"]) == 2
                elif filename == f"{SESSION_2_KEY}.json":
                    # Check SESSION_2 properties
                    assert loaded_data["session_guid"] == SESSION_2_KEY
                    assert loaded_data["metadata"]["environment"] == "staging"
                    assert len(loaded_data["metadata"]["timestamp_list"]) == 1

        # Verify all statistics are logged
        assert "Total files downloaded from GCS: 7" in caplog.text
        assert "Files successfully parsed and validated: 3" in caplog.text
        assert "Files skipped due to errors: 4" in caplog.text
        assert "Total unique sessions processed: 2" in caplog.text
        assert "Sessions with environment conflicts: 0" in caplog.text
        assert "Session files successfully written to disk: 2" in caplog.text
        assert "SESSION PROCESSING SUMMARY" in caplog.text

    def test_process_rrweb_sessions_orders_cronologically(
        self, temp_output_dir, sample_rrweb_data
    ):
        """Test that session data is correctly merged and ordered."""
        process_rrweb_sessions("mock_bucket_name", temp_output_dir)

        filepath = os.path.join(temp_output_dir, f"{SESSION_1_KEY}.json")
        with open(filepath, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)

            # Verify timestamp ordering (chronological)
            timestamps = loaded_data["metadata"]["timestamp_list"]
            assert timestamps == sorted(timestamps)
            assert timestamps[0] == "2025-05-02T12:10:50.644423+0000"
            assert timestamps[1] == "2025-05-02T12:11:30.991832+0000"

            # Check merged rrweb_data ordering
            rrweb_data = loaded_data["rrweb_data"]

            # Should contain events from both files in chronological order
            # First file (earlier timestamp) events should come first
            expected_first_events = sample_rrweb_data["session_1_file_2"]
            expected_second_events = sample_rrweb_data["session_1_file_1"]

            # Verify the merged data contains all events in correct order
            file_split = len(expected_first_events)
            assert rrweb_data[:file_split] == expected_first_events
            assert rrweb_data[file_split:] == expected_second_events
            assert len(rrweb_data) == len(expected_first_events) + len(
                expected_second_events
            )

    def test_handles_malformed_files_gracefully(self, caplog, temp_output_dir):
        """Test pipeline skips invalid files and continues processing."""
        process_rrweb_sessions("mock_bucket_name", temp_output_dir)

        sessions = [SESSION_1_KEY, SESSION_2_KEY]
        expected_filenames = [f"{session}.json" for session in sessions]

        all_timestamps = []
        for filename in expected_filenames:
            filepath = os.path.join(temp_output_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
                all_timestamps.extend(loaded_data["metadata"]["timestamp_list"])

        # Verify that malformed JSON file and missing fields file are omitted
        assert (
            "2025-05-02T12:13:00.000000+0000" not in all_timestamps
        )  # Malformed JSON file should be skipped
        assert (
            "2025-05-02T12:14:00.000000+0000" not in all_timestamps
        )  # Missing fields file should be skipped

        # Should still process valid files
        assert len(all_timestamps) == 3

        # Verify warnings were logged
        assert "Failed to parse JSON in file" in caplog.text
        assert "Expecting ',' delimiter" in caplog.text
        assert "does not contain a JSON object (found str)" in caplog.text
        assert "missing required fields" in caplog.text

    def test_handles_environment_conflicts_with_warning(
        self, caplog, custom_mock_bucket, mock_gcs_client, temp_output_dir
    ):
        """Test pipeline handles conflicting environments correctly."""
        # Create test data with conflicting environments
        conflicting_data = {
            "2025-05-02T12:10:00.000000+0000": {
                "session_guid": "conflict-session",
                "session_data": [{"type": 1}],
                "environment": "production",
            },
            "2025-05-02T12:11:00.000000+0000": {
                "session_guid": "conflict-session",
                "session_data": [{"type": 2}],
                "environment": "staging",  # Different environment
            },
        }

        mock_bucket = custom_mock_bucket(conflicting_data)
        mock_gcs_client.bucket.return_value = mock_bucket

        process_rrweb_sessions("mock_bucket_name", temp_output_dir)

        # Should use first environment value
        filepath = os.path.join(temp_output_dir, "conflict-session.json")
        with open(filepath, "r", encoding="utf-8") as f:
            final_sessions = json.load(f)

            assert final_sessions["metadata"]["environment"] == "production"

        # Should log warning
        assert "conflicting environment values" in caplog.text
        assert "Using first value: 'production'" in caplog.text

    def test_handles_no_files(
        self, caplog, custom_mock_bucket, mock_gcs_client, temp_output_dir
    ):
        """Test pipeline handles no files correctly."""
        # Create test data with no files
        no_data = {}

        mock_bucket = custom_mock_bucket(no_data)
        mock_gcs_client.bucket.return_value = mock_bucket

        process_rrweb_sessions("mock_bucket_name", temp_output_dir)

        # Should not create any sessions
        assert os.listdir(temp_output_dir) == []

        # Should log warning
        assert "No files found" in caplog.text

    def test_writes_compact_json_format(self, temp_output_dir):
        """Test that JSON is written in compact format (no extra whitespace)."""
        process_rrweb_sessions("mock_bucket_name", temp_output_dir)

        sessions = [SESSION_1_KEY, SESSION_2_KEY]
        expected_filenames = [f"{session}.json" for session in sessions]

        # Verify file contents
        for filename in expected_filenames:
            filepath = os.path.join(temp_output_dir, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

                # Verify compact format (no extra whitespace or newlines)
                assert "\n" not in content
                assert "  " not in content  # No double spaces
                assert ": " not in content  # No space after colons
                assert ", " not in content  # No space after commas


class TestSessionDataValidation:
    """Test session data validation logic for edge cases."""

    def test_validates_required_fields_comprehensively(self):
        """Test validation catches all combinations of missing required fields."""
        test_cases = [
            # Missing session_guid
            '{"session_data": [], "environment": "test"}',
            # Missing session_data
            '{"session_guid": "test", "environment": "test"}',
            # Missing environment
            '{"session_guid": "test", "session_data": []}',
            # Missing multiple fields
            '{"session_guid": "test"}',
        ]

        for content in test_cases:
            result = _parse_and_validate_session_file("test.json", content)
            assert result is None

    def test_handles_data_type_validation(self):
        """Test validation of field data types."""
        test_cases = [
            # Non-string session_guid
            ('{"session_guid": 123, "session_data": [], "environment": "test"}', None),
            # Non-list session_data
            (
                '{"session_guid": "test", "session_data": "not-list", "environment": "test"}',
                None,
            ),
            # Non-string environment
            ('{"session_guid": "test", "session_data": [], "environment": 123}', None),
            # Valid case
            (
                '{"session_guid": "test", "session_data": [], "environment": "test"}',
                "test",
            ),
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
                    "userAgent": "Mozilla/5.0...",
                },
            },
            {
                "type": 1,
                "data": {
                    "node": {
                        "id": 1,
                        "tagName": "html",
                        "attributes": {"lang": "en"},
                        "childNodes": [{"id": 2, "tagName": "head"}],
                    }
                },
            },
            {
                "type": 3,
                "data": {
                    "source": 2,
                    "type": 0,
                    "id": 3,
                    "x": 100.5,
                    "y": 200.7,
                    "timeOffset": 1234,
                },
            },
        ]

        content = json.dumps(
            {
                "session_guid": "complex-test",
                "session_data": complex_events,
                "environment": "production",
            }
        )

        result = _parse_and_validate_session_file("complex.json", content)

        assert result is not None
        assert result["session_data"] == complex_events
        # Verify deep structure is preserved
        assert (
            result["session_data"][0]["data"]["href"]
            == "https://example.com/path?param=value#hash"
        )
        assert result["session_data"][1]["data"]["node"]["attributes"]["lang"] == "en"
        assert result["session_data"][2]["data"]["x"] == 100.5


# TEMP: remove after integration - keeping minimal tests specific to _sort_and_collect_timestamps
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
                "environment": "test",
            },
            {
                "filename": "2025-05-02T12:10:15.987654+0000",
                "session_guid": "test-session",
                "session_data": [{"order": 1}],
                "environment": "test",
            },
            {
                "filename": "2025-05-02T12:12:45.555555+0000",
                "session_guid": "test-session",
                "session_data": [{"order": 2}],
                "environment": "test",
            },
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
        single_entry = [
            {
                "filename": "2025-05-02T12:10:00.000000+0000",
                "session_guid": "single-file",
                "session_data": [{"type": 1}],
                "environment": "production",
            }
        ]

        grouped = {"single-file": single_entry}
        result = _sort_and_collect_timestamps(grouped)

        assert len(result["single-file"]["timestamp_list"]) == 1
        assert len(result["single-file"]["sorted_entries"]) == 1
        assert (
            result["single-file"]["timestamp_list"][0]
            == "2025-05-02T12:10:00.000000+0000"
        )


class TestPrivateMethodEdgeCases:
    """Edge case tests for private methods that handle empty/malformed data."""

    def test_group_by_session_guid_handles_empty_list(self):
        """Test grouping handles empty input gracefully."""
        result = _group_by_session_guid([])
        assert not result

    def test_environment_validation_handles_empty_entries(self):
        """Test environment validation with sessions containing no entries."""
        sessions_with_empty = {
            "empty-session": {"sorted_entries": [], "timestamp_list": []}
        }

        result, conflicts = _validate_and_extract_environment(sessions_with_empty)

        # Should handle empty entries gracefully
        assert "empty-session" in result
        assert result["empty-session"]["environment"] == ""  # Default for empty
        assert result["empty-session"]["sorted_entries"] == []
        assert result["empty-session"]["timestamp_list"] == []
        assert conflicts == 0

    def test_processing_handles_empty_session_groups(self):
        """Test edge case of empty session groups."""
        result = _sort_and_collect_timestamps({})
        assert not result

        result, conflicts = _validate_and_extract_environment({})
        assert not result
        assert conflicts == 0

    def test_merge_session_data_handles_empty_session_data(self):
        """Test edge case of empty session_data lists gracefully."""
        sessions = {
            "empty-session": {
                "sorted_entries": [
                    {
                        "filename": "2025-05-02T12:10:00.000000+0000",
                        "session_data": [],  # Empty session data
                        "environment": "test",
                    },
                    {
                        "filename": "2025-05-02T12:11:00.000000+0000",
                        "session_data": [{"type": 1}],  # Non-empty session data
                        "environment": "test",
                    },
                ],
                "timestamp_list": [
                    "2025-05-02T12:10:00.000000+0000",
                    "2025-05-02T12:11:00.000000+0000",
                ],
                "environment": "test",
            }
        }

        result = _merge_session_data(sessions)

        # Should handle empty lists gracefully
        rrweb_data = result["empty-session"]["rrweb_data"]
        assert len(rrweb_data) == 1  # Only the non-empty entry
        assert rrweb_data[0]["type"] == 1

    def test_merge_session_data_handles_empty_input(self):
        """Test merge handles empty sessions dictionary."""
        result = _merge_session_data({})
        assert not result

    def test_write_sessions_to_disk_handles_empty_sessions_dict(self, temp_output_dir):
        """Test that empty sessions dictionary is handled gracefully."""
        _write_sessions_to_disk({}, temp_output_dir)

        # Directory should exist but be empty
        assert os.path.exists(temp_output_dir)
        assert os.listdir(temp_output_dir) == []

    def test_write_sessions_to_disk_works_if_directory_exists_or_doesnt(
        self, temp_output_dir, sample_rrweb_data
    ):
        """Test that output directory is created if it doesn't exist and reused if it does."""
        sessions = {
            "test-session": {
                "session_guid": "test-session",
                "rrweb_data": sample_rrweb_data["session_1_file_1"],
                "metadata": {
                    "environment": "test",
                    "timestamp_list": ["2025-05-02T12:10:50.644423+0000"],
                },
            }
        }

        assert os.path.exists(temp_output_dir)

        _write_sessions_to_disk(sessions, temp_output_dir)

        # Verify file was written
        filepath = os.path.join(temp_output_dir, "test-session.json")
        assert os.path.exists(filepath)

        # Create a nested directory path that doesn't exist
        nested_output_dir = os.path.join(temp_output_dir, "nested", "output", "dir")
        assert not os.path.exists(nested_output_dir)

        _write_sessions_to_disk(sessions, nested_output_dir)

        # Verify directory was created
        assert os.path.exists(nested_output_dir)
        assert os.path.isdir(nested_output_dir)

        # Verify file was written
        filepath = os.path.join(nested_output_dir, "test-session.json")
        assert os.path.exists(filepath)


class TestGcsInteractionEdgeCases:
    """Minimal tests for GCS interaction edge cases."""

    def test_initialize_gcs_client_failure(self, mock_client_class):
        """Test GCS client initialization failure."""
        mock_client_class.side_effect = Exception("Authentication failed")

        with pytest.raises(Exception, match="Authentication failed"):
            _initialize_gcs_client()

    def test_download_handles_empty_bucket(self, mock_bucket):
        """Test download handles empty bucket gracefully."""
        mock_bucket.list_blobs.return_value = []

        result = _download_json_files("empty-bucket")
        assert not result

    def test_download_handles_gcs_errors(self, mock_gcs_client):
        """Test download handles GCS errors appropriately."""

        def mock_error_download(bucket_name):
            raise NotFound("Bucket not found")

        mock_gcs_client.bucket.side_effect = mock_error_download

        with pytest.raises(NotFound, match="Bucket not found"):
            _download_json_files("nonexistent-bucket")
