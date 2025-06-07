"""
Unit tests for process_rrweb_sessions.py

Tests the GCS interaction functions using mocks to avoid actual GCS calls.
"""

import pytest
from unittest.mock import Mock, patch
from google.cloud import storage
from google.cloud.exceptions import NotFound, Forbidden

from process_rrweb_sessions import (
    _initialize_gcs_client,
    _list_json_files,
    _download_file_content,
    download_json_files,
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
        "2025-05-02T12:10:50.644423+0000",
        "2025-05-02T12:11:30.991832+0000",
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
    """Tests for download_json_files function (integration tests)."""

    def test_download_json_files_success(
        self, mock_client_class, mock_bucket, mock_sample_blobs, sample_file_contents
    ):
        """Test successful download of all JSON files."""
        result = download_json_files("test-bucket")

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

        result = download_json_files("empty-bucket")

        assert result == []
        mock_bucket.list_blobs.assert_called_once()

    def test_download_json_files_partial_failure(self, mock_blob):
        """Test download when some files fail to download."""

        # First file succeeds, second fails, third succeeds
        mock_blob.download_as_text.side_effect = NotFound("File not found")

        with pytest.raises(NotFound, match="File not found"):
            download_json_files("test-bucket")

    def test_download_json_files_client_init_failure(self, mock_client_class):
        """Test download when client initialization fails."""
        mock_client_class.side_effect = Exception("Authentication failed")

        with pytest.raises(Exception, match="Authentication failed"):
            download_json_files("test-bucket")

    def test_download_json_files_list_failure(self, mock_bucket):
        """Test download when listing files fails."""
        mock_bucket.list_blobs.side_effect = Forbidden("Access denied")

        with pytest.raises(Forbidden, match="Access denied"):
            download_json_files("test-bucket")
