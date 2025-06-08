"""
Unit tests for process_rrweb_sessions.py

Tests the GCS interaction functions using mocks to avoid actual GCS calls.
"""

import json
from unittest.mock import Mock, patch

import pytest
from google.cloud import storage
from google.cloud.exceptions import NotFound, Forbidden

from process_rrweb_sessions import (
    _initialize_gcs_client,
    _list_json_files,
    _download_file_content,
    _download_json_files,
    _parse_and_validate_session_file,
    _group_by_session_guid,
    _sort_and_collect_timestamps,
)


@pytest.fixture(name="mock_client_class", autouse=True)
def fixture_mock_client_class(mock_gcs_client):
    """Mock class for GCS client to be used in tests."""
    with patch(
        "process_rrweb_sessions.storage.Client", return_value=mock_gcs_client
    ) as client_class:
        yield client_class


@pytest.fixture(name="mock_gcs_client")
def fixture_mock_gcs_client(mock_bucket):
    """Mock GCS client for testing."""
    mock_gcs_client = Mock(spec=storage.Client)
    mock_gcs_client.bucket.return_value = mock_bucket
    return mock_gcs_client


@pytest.fixture(name="mock_bucket")
def fixture_mock_bucket(mock_blob):
    """Mock GCS bucket for testing."""
    mock_bucket = Mock(spec=storage.Bucket)
    mock_bucket.list_blobs.return_value = [mock_blob]
    mock_bucket.blob.return_value = mock_blob
    return mock_bucket


@pytest.fixture(name="mock_blob")
def fixture_mock_blob(sample_json_files, sample_file_contents):
    """Mock GCS blob for testing."""
    mock_blob = Mock(spec=storage.Blob)
    mock_blob.name = sample_json_files[0]
    mock_blob.download_as_text.return_value = sample_file_contents[0]
    return mock_blob


@pytest.fixture(name="sample_json_files")
def fixture_sample_json_files():
    """Sample JSON filenames for testing."""
    return [
        "2025-05-02T12:11:30.991832+0000",
        "2025-05-02T12:10:50.644423+0000",
        "2025-05-02T12:12:15.123456+0000",
    ]


@pytest.fixture(name="sample_file_contents")
def fixture_sample_file_contents():
    """Sample file contents for testing."""
    return [
        '{"session_guid": "abc-123", "session_data": [{"type": 1}], "environment": "production"}',
        '{"session_guid": "abc-123", "session_data": [{"type": 2}], "environment": "production"}',
        '{"session_guid": "def-456", "session_data": [{"type": 3}], "environment": "staging"}',
    ]


@pytest.fixture(name="mock_sample_blobs")
def fixture_mock_sample_blobs(mock_bucket, sample_json_files, sample_file_contents):
    """Mock blobs representing JSON files in bucket."""
    blobs = []
    for filename, content in zip(sample_json_files, sample_file_contents):
        blob = Mock()
        blob.name = filename
        blob.download_as_text.return_value = content
        blobs.append(blob)
    mock_bucket.list_blobs.return_value = blobs
    mock_bucket.blob.side_effect = blobs
    return blobs


@pytest.fixture(name="sample_validated_records")
def fixture_sample_validated_records(sample_json_files, sample_file_contents):
    """Sample validated records for testing."""
    records = []
    for filename, content in zip(sample_json_files, sample_file_contents):
        record = json.loads(content)
        record["filename"] = filename
        records.append(record)
    return records


@pytest.fixture(name="sample_grouped_sessions")
def fixture_sample_grouped_sessions(sample_validated_records):
    """Sample grouped sessions for testing."""
    return _group_by_session_guid(sample_validated_records)


class TestInitializeGcsClient:
    """Tests for _initialize_gcs_client function."""

    def test_initialize_gcs_client_success(self, mock_client_class, mock_gcs_client):
        """Test successful GCS client initialization."""
        result = _initialize_gcs_client()

        mock_client_class.assert_called_once()
        assert result == mock_gcs_client

    def test_initialize_gcs_client_failure(self, mock_client_class):
        """Test GCS client initialization failure."""
        mock_client_class.side_effect = Exception("Authentication failed")

        with pytest.raises(Exception, match="Authentication failed"):
            _initialize_gcs_client()


class TestListJsonFiles:
    """Tests for _list_json_files function."""

    def test_list_json_files_success(
        self, mock_gcs_client, mock_bucket, mock_sample_blobs, sample_json_files
    ):
        """Test successful listing of JSON files."""

        result = _list_json_files(mock_gcs_client, "test-bucket")

        # Should only return JSON files in root directory
        assert result == sample_json_files
        mock_gcs_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.list_blobs.assert_called_once()

    def test_list_json_files_empty_bucket(self, mock_gcs_client, mock_bucket):
        """Test listing files from empty bucket."""
        mock_bucket.list_blobs.return_value = []

        result = _list_json_files(mock_gcs_client, "empty-bucket")

        #  pylint: disable=use-implicit-booleaness-not-comparison
        assert result == []
        mock_gcs_client.bucket.assert_called_once_with("empty-bucket")

    def test_list_json_files_bucket_not_found(self, mock_gcs_client):
        """Test listing files when bucket doesn't exist."""
        mock_gcs_client.bucket.side_effect = NotFound("Bucket not found")

        with pytest.raises(NotFound, match="Bucket not found"):
            _list_json_files(mock_gcs_client, "nonexistent-bucket")

    def test_list_json_files_permission_denied(self, mock_gcs_client):
        """Test listing files when access is denied."""
        mock_gcs_client.bucket.side_effect = Forbidden("Access denied")

        with pytest.raises(Forbidden, match="Access denied"):
            _list_json_files(mock_gcs_client, "forbidden-bucket")

    def test_list_json_files_with_special_characters(
        self, mock_gcs_client, mock_bucket
    ):
        """Test listing files with special characters in names."""
        special_blobs = []
        # File with spaces
        blob1 = Mock()
        blob1.name = "file with spaces.json"
        special_blobs.append(blob1)

        # File with unicode characters
        blob2 = Mock()
        blob2.name = "файл.json"
        special_blobs.append(blob2)

        # File with special characters
        blob3 = Mock()
        blob3.name = "file-with_special.chars.json"
        special_blobs.append(blob3)

        mock_bucket.list_blobs.return_value = special_blobs

        result = _list_json_files(mock_gcs_client, "special-bucket")

        expected = [
            "file with spaces.json",
            "файл.json",
            "file-with_special.chars.json",
        ]
        assert result == expected


class TestDownloadFileContent:
    """Tests for _download_file_content function."""

    def test_download_file_content_success(
        self, mock_gcs_client, mock_bucket, mock_blob
    ):
        """Test successful file download."""
        mock_blob.download_as_text.return_value = "test file content"

        result = _download_file_content(mock_gcs_client, "test-bucket", "test.json")

        assert result == "test file content"
        mock_gcs_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("test.json")
        mock_blob.download_as_text.assert_called_once()

    def test_download_file_content_file_not_found(self, mock_gcs_client, mock_blob):
        """Test downloading non-existent file."""
        mock_blob.download_as_text.side_effect = NotFound("File not found")

        with pytest.raises(NotFound, match="File not found"):
            _download_file_content(mock_gcs_client, "test-bucket", "nonexistent.json")

    def test_download_file_content_permission_denied(self, mock_gcs_client, mock_blob):
        """Test downloading file with insufficient permissions."""
        mock_blob.download_as_text.side_effect = Forbidden("Access denied")

        with pytest.raises(Forbidden, match="Access denied"):
            _download_file_content(mock_gcs_client, "test-bucket", "forbidden.json")

    def test_download_file_content_empty_file(self, mock_gcs_client, mock_blob):
        """Test downloading empty file."""
        mock_blob.download_as_text.return_value = ""

        result = _download_file_content(mock_gcs_client, "test-bucket", "empty.json")

        assert result == ""

    def test_download_file_content_large_file(self, mock_gcs_client, mock_blob):
        """Test downloading large file."""
        large_content = "x" * 10000  # 10KB of content
        mock_blob.download_as_text.return_value = large_content

        result = _download_file_content(mock_gcs_client, "test-bucket", "large.json")

        assert result == large_content
        assert len(result) == 10000

    def test_download_file_with_unicode_content(self, mock_gcs_client, mock_blob):
        """Test downloading file with unicode content."""
        unicode_content = '{"message": "Hello 世界", "emoji": "🌍"}'
        mock_blob.download_as_text.return_value = unicode_content

        result = _download_file_content(mock_gcs_client, "test-bucket", "unicode.json")

        assert result == unicode_content


class TestDownloadJsonFiles:
    """Tests for _download_json_files function (integration tests)."""

    def test_download_json_files_success(
        self, mock_client_class, mock_bucket, mock_sample_blobs, sample_file_contents
    ):
        """Test successful download of all JSON files."""
        result = _download_json_files("test-bucket")

        expected = list(
            zip([blob.name for blob in mock_sample_blobs], sample_file_contents)
        )
        assert result == expected

        mock_client_class.assert_called_once()
        mock_bucket.list_blobs.assert_called_once()
        for blob in mock_sample_blobs:
            assert blob.download_as_text.call_count == 1

    def test_download_json_files_empty_bucket(self, mock_bucket):
        """Test download from empty bucket."""
        mock_bucket.list_blobs.return_value = []

        result = _download_json_files("empty-bucket")

        assert result == []
        mock_bucket.list_blobs.assert_called_once()

    def test_download_json_files_partial_failure(self, mock_blob):
        """Test download when some files fail to download."""

        # First file succeeds, second fails, third succeeds
        mock_blob.download_as_text.side_effect = NotFound("File not found")

        with pytest.raises(NotFound, match="File not found"):
            _download_json_files("test-bucket")

    def test_download_json_files_client_init_failure(self, mock_client_class):
        """Test download when client initialization fails."""
        mock_client_class.side_effect = Exception("Authentication failed")

        with pytest.raises(Exception, match="Authentication failed"):
            _download_json_files("test-bucket")

    def test_download_json_files_list_failure(self, mock_bucket):
        """Test download when listing files fails."""
        mock_bucket.list_blobs.side_effect = Forbidden("Access denied")

        with pytest.raises(Forbidden, match="Access denied"):
            _download_json_files("test-bucket")


class TestParseAndValidateSessionFile:
    """Tests for parse_and_validate_session_file function."""

    def test_valid_json_input(self):
        """Test parsing valid JSON input returns expected dictionary."""
        filename = "test.json"
        content = '{"session_guid": "abc-123", "session_data": [{"type": 1}], "environment": "production"}'

        result = _parse_and_validate_session_file(filename, content)

        assert result is not None
        assert result["filename"] == filename
        assert result["session_guid"] == "abc-123"
        assert result["session_data"] == [{"type": 1}]
        assert result["environment"] == "production"

    def test_malformed_json_input(self, caplog):
        """Test malformed JSON input logs warning and returns None."""
        filename = "malformed.json"
        # Missing closing brace
        content = '{"session_guid": "abc-123", "session_data": [{"type": 1}], "environment": "production"'

        result = _parse_and_validate_session_file(filename, content)

        assert result is None
        assert "Failed to parse JSON in file 'malformed.json'" in caplog.text

    def test_non_json_object_input(self, caplog):
        """Test JSON input that is not an object logs warning and returns None."""
        filename = "array.json"
        content = '[{"session_guid": "abc-123"}]'  # Array instead of object

        result = _parse_and_validate_session_file(filename, content)

        assert result is None
        assert "does not contain a JSON object (found list)" in caplog.text

    def test_missing_session_guid_field(self, caplog):
        """Test JSON missing session_guid field logs warning and returns None."""
        filename = "missing_guid.json"
        content = '{"session_data": [{"type": 1}], "environment": "production"}'

        result = _parse_and_validate_session_file(filename, content)

        assert result is None
        assert "missing required fields: session_guid" in caplog.text

    def test_missing_session_data_field(self, caplog):
        """Test JSON missing session_data field logs warning and returns None."""
        filename = "missing_data.json"
        content = '{"session_guid": "abc-123", "environment": "production"}'

        result = _parse_and_validate_session_file(filename, content)

        assert result is None
        assert "missing required fields: session_data" in caplog.text

    def test_missing_environment_field(self, caplog):
        """Test JSON missing environment field logs warning and returns None."""
        filename = "missing_env.json"
        content = '{"session_guid": "abc-123", "session_data": [{"type": 1}]}'

        result = _parse_and_validate_session_file(filename, content)

        assert result is None
        assert "missing required fields: environment" in caplog.text

    def test_missing_multiple_fields(self, caplog):
        """Test JSON missing multiple fields logs warning and returns None."""
        filename = "missing_multiple.json"
        content = '{"session_guid": "abc-123"}'

        result = _parse_and_validate_session_file(filename, content)

        assert result is None
        assert "missing required fields: session_data, environment" in caplog.text

    def test_empty_session_guid(self, caplog):
        """Test empty session_guid logs warning and returns None."""
        filename = "empty_guid.json"
        content = '{"session_guid": "", "session_data": [{"type": 1}], "environment": "production"}'

        result = _parse_and_validate_session_file(filename, content)

        assert result is None
        assert "has invalid session_guid: must be non-empty string" in caplog.text

    def test_whitespace_only_session_guid(self, caplog):
        """Test whitespace-only session_guid logs warning and returns None."""
        filename = "whitespace_guid.json"
        content = '{"session_guid": "   ", "session_data": [{"type": 1}], "environment": "production"}'

        result = _parse_and_validate_session_file(filename, content)

        assert result is None
        assert "has invalid session_guid: must be non-empty string" in caplog.text

    def test_non_string_session_guid(self, caplog):
        """Test non-string session_guid logs warning and returns None."""
        filename = "numeric_guid.json"
        content = '{"session_guid": 123, "session_data": [{"type": 1}], "environment": "production"}'

        result = _parse_and_validate_session_file(filename, content)

        assert result is None
        assert "has invalid session_guid: must be non-empty string" in caplog.text

    def test_non_list_session_data(self, caplog):
        """Test non-list session_data logs warning and returns None."""
        filename = "string_data.json"
        content = '{"session_guid": "abc-123", "session_data": "not a list", "environment": "production"}'

        result = _parse_and_validate_session_file(filename, content)

        assert result is None
        assert "has invalid session_data: must be a list (found str)" in caplog.text

    def test_non_string_environment(self, caplog):
        """Test non-string environment logs warning and returns None."""
        filename = "numeric_env.json"
        content = '{"session_guid": "abc-123", "session_data": [{"type": 1}], "environment": 123}'

        result = _parse_and_validate_session_file(filename, content)

        assert result is None
        assert (
            "has invalid environment: must be non-empty string (found int)"
            in caplog.text
        )

    def test_empty_session_data_list(self):
        """Test empty session_data list is valid."""
        filename = "empty_data.json"
        content = '{"session_guid": "abc-123", "session_data": [], "environment": "production"}'

        result = _parse_and_validate_session_file(filename, content)

        assert result is not None
        assert result["session_data"] == []

    def test_empty_environment_string(self):
        """Test empty environment string is valid."""
        filename = "empty_env.json"
        content = '{"session_guid": "abc-123", "session_data": [{"type": 1}], "environment": ""}'

        result = _parse_and_validate_session_file(filename, content)

        assert result is None

    def test_complex_session_data(self):
        """Test complex session_data structure is preserved."""
        filename = "complex.json"
        complex_data = [
            {"type": 1, "data": {"href": "https://example.com"}},
            {"type": 2, "data": {"node": {"id": 1, "tagName": "div"}}},
            {"type": 3, "data": {"source": 0, "texts": [], "attributes": []}},
        ]
        data_str = json.dumps(complex_data)
        content = f'{{"session_guid": "abc-123", "session_data": {data_str}, "environment": "production"}}'

        result = _parse_and_validate_session_file(filename, content)

        assert result is not None
        assert result["session_data"] == complex_data

    def test_unicode_content(self):
        """Test file with unicode content is handled correctly."""
        filename = "unicode.json"
        content = '{"session_guid": "测试-123", "session_data": [{"message": "Hello 世界"}], "environment": "测试环境"}'

        result = _parse_and_validate_session_file(filename, content)

        assert result is not None
        assert result["session_guid"] == "测试-123"
        assert result["environment"] == "测试环境"
        assert result["session_data"] == [{"message": "Hello 世界"}]

    def test_extra_fields_are_ignored(self):
        """Test that extra fields in JSON are ignored."""
        filename = "extra_fields.json"
        content = (
            '{"session_guid": "abc-123", "session_data": [{"type": 1}], "environment": "production", '
            '"extra_field": "ignored", "timestamp": 1234567890}'
        )

        result = _parse_and_validate_session_file(filename, content)

        assert result is not None
        assert "extra_field" not in result
        assert "timestamp" not in result
        assert (
            len(result) == 4
        )  # Only filename, session_guid, session_data, environment


class TestGroupBySessionGuid:
    """Tests for group_by_session_guid function."""

    def test_group_single_session(self, sample_validated_records):
        """Test grouping records from a single session."""
        records = [
            record
            for record in sample_validated_records
            if record["session_guid"] == "abc-123"
        ]

        result = _group_by_session_guid(records)

        assert len(result) == 1
        assert "abc-123" in result
        assert len(result["abc-123"]) == 2

        # Check that grouping maintains order and filenames.
        assert result["abc-123"][0]["filename"] == "2025-05-02T12:11:30.991832+0000"
        assert result["abc-123"][1]["filename"] == "2025-05-02T12:10:50.644423+0000"

    def test_group_multiple_sessions(self, sample_validated_records):
        """Test grouping records from multiple sessions."""
        result = _group_by_session_guid(sample_validated_records)

        assert len(result) == 2
        assert "abc-123" in result
        assert "def-456" in result
        assert len(result["abc-123"]) == 2
        assert len(result["def-456"]) == 1

    def test_group_empty_list(self):
        """Test grouping empty list of records."""
        records = []

        result = _group_by_session_guid(records)

        assert len(result) == 0
        assert result == {}

    def test_group_preserves_record_structure(self, sample_validated_records):
        """Test that grouping preserves the complete record structure."""
        records = [sample_validated_records[0]]

        result = _group_by_session_guid(records)

        grouped_record = result["abc-123"][0]
        assert grouped_record["filename"] == "2025-05-02T12:11:30.991832+0000"
        assert grouped_record["session_guid"] == "abc-123"
        assert grouped_record["session_data"] == [{"type": 1}]
        assert grouped_record["environment"] == "production"

    def test_group_with_unicode_session_guids(self, sample_validated_records):
        """Test grouping with unicode session_guid values."""
        sample_validated_records[0]["session_guid"] = "测试-123"
        sample_validated_records[1]["session_guid"] = "测试-123"

        result = _group_by_session_guid(sample_validated_records)

        assert len(result) == 2
        assert "测试-123" in result
        assert len(result["测试-123"]) == 2

    def test_group_large_number_of_sessions(self):
        """Test grouping with a large number of different sessions."""
        records = []
        num_sessions = 100
        files_per_session = 3

        for i in range(num_sessions):
            session_guid = f"session-{i:03d}"
            for j in range(files_per_session):
                records.append(
                    {
                        "filename": f"file_{i}_{j}.json",
                        "session_guid": session_guid,
                        "session_data": [{"type": j}],
                        "environment": "production",
                    }
                )

        result = _group_by_session_guid(records)

        assert len(result) == num_sessions
        for i in range(num_sessions):
            session_guid = f"session-{i:03d}"
            assert session_guid in result
            assert len(result[session_guid]) == files_per_session


class TestSortAndCollectTimestamps:
    """Tests for _sort_and_collect_timestamps function."""

    def test_sort_single_session_in_order(self, sample_grouped_sessions):
        """Test sorting a single session with files already in order."""
        result = _sort_and_collect_timestamps(sample_grouped_sessions)

        assert len(result) == 2
        assert "abc-123" in result
        assert "def-456" in result

        session_data = result["abc-123"]
        assert "sorted_entries" in session_data
        assert "timestamp_list" in session_data

        # Check sorted entries
        sorted_entries = session_data["sorted_entries"]
        assert len(sorted_entries) == 2

        # Check that first entry (after sorting) has all original fields
        first_entry = sorted_entries[0]
        assert first_entry["filename"] == "2025-05-02T12:10:50.644423+0000"
        assert first_entry["session_guid"] == "abc-123"
        assert first_entry["session_data"] == [{"type": 2}]
        assert first_entry["environment"] == "production"

        # Check that second entry (after sorting) has all original fields
        second_entry = sorted_entries[1]
        assert second_entry["filename"] == "2025-05-02T12:11:30.991832+0000"
        assert second_entry["session_guid"] == "abc-123"
        assert second_entry["session_data"] == [{"type": 1}]
        assert second_entry["environment"] == "production"

        # Check timestamp list
        timestamp_list = session_data["timestamp_list"]
        assert timestamp_list == [
            "2025-05-02T12:10:50.644423+0000",
            "2025-05-02T12:11:30.991832+0000",
        ]

    def test_sort_empty_sessions_dict(self):
        """Test sorting with empty sessions dictionary."""
        grouped_sessions = {}

        result = _sort_and_collect_timestamps(grouped_sessions)

        assert len(result) == 0
        assert result == {}

    def test_sort_large_number_of_entries(self):
        """Test sorting with a large number of entries in a single session."""
        entries = []
        num_entries = 100

        # Create entries with timestamps in reverse order
        for i in range(num_entries - 1, -1, -1):
            timestamp = f"2025-05-02T12:{i:02d}:00.000000+0000"
            entries.append(
                {
                    "filename": timestamp,
                    "session_guid": "large-session",
                    "session_data": [{"type": i}],
                    "environment": "production",
                }
            )

        grouped_sessions = {"large-session": entries}

        result = _sort_and_collect_timestamps(grouped_sessions)

        timestamp_list = result["large-session"]["timestamp_list"]
        sorted_entries = result["large-session"]["sorted_entries"]

        # Verify correct number of entries
        assert len(timestamp_list) == num_entries
        assert len(sorted_entries) == num_entries

        # Verify entries are sorted correctly
        for i in range(num_entries):
            expected_timestamp = f"2025-05-02T12:{i:02d}:00.000000+0000"
            assert timestamp_list[i] == expected_timestamp
            assert sorted_entries[i]["filename"] == expected_timestamp
            assert sorted_entries[i]["session_data"] == [{"type": i}]
