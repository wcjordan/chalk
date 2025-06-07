"""
Unit tests for process_rrweb_sessions.py

Tests the GCS interaction functions using mocks to avoid actual GCS calls.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from google.cloud import storage
from google.cloud.exceptions import NotFound, Forbidden

from process_rrweb_sessions import (
    _initialize_gcs_client,
    _list_json_files,
    _download_file_content,
    download_json_files,
)


@pytest.fixture
def mock_gcs_client():
    """Mock GCS client for testing."""
    return Mock(spec=storage.Client)


@pytest.fixture
def mock_bucket():
    """Mock GCS bucket for testing."""
    return Mock(spec=storage.Bucket)


@pytest.fixture
def mock_blob():
    """Mock GCS blob for testing."""
    return Mock(spec=storage.Blob)


@pytest.fixture
def sample_json_files():
    """Sample JSON filenames for testing."""
    return [
        "2025-05-02T12:10:50.644423+0000.json",
        "2025-05-02T12:11:30.991832+0000.json",
        "2025-05-02T12:12:15.123456+0000.json",
    ]


@pytest.fixture
def sample_file_contents():
    """Sample file contents for testing."""
    return [
        '{"session_guid": "abc-123", "session_data": [{"type": 1}], "environment": "production"}',
        '{"session_guid": "abc-123", "session_data": [{"type": 2}], "environment": "production"}',
        '{"session_guid": "def-456", "session_data": [{"type": 3}], "environment": "staging"}',
    ]


@pytest.fixture
def mixed_files_in_bucket():
    """Mock blobs representing mixed file types in bucket."""
    blobs = []
    
    # JSON files in root
    json_blob1 = Mock()
    json_blob1.name = "2025-05-02T12:10:50.644423+0000.json"
    blobs.append(json_blob1)
    
    json_blob2 = Mock()
    json_blob2.name = "2025-05-02T12:11:30.991832+0000.json"
    blobs.append(json_blob2)
    
    # Non-JSON file in root (should be ignored)
    txt_blob = Mock()
    txt_blob.name = "readme.txt"
    blobs.append(txt_blob)
    
    # JSON file in subdirectory (should be ignored)
    subdir_blob = Mock()
    subdir_blob.name = "subdir/2025-05-02T12:12:15.123456+0000.json"
    blobs.append(subdir_blob)
    
    return blobs


class TestInitializeGcsClient:
    """Tests for _initialize_gcs_client function."""
    
    @patch('process_rrweb_sessions.storage.Client')
    def test_initialize_gcs_client_success(self, mock_client_class):
        """Test successful GCS client initialization."""
        mock_client_instance = Mock(spec=storage.Client)
        mock_client_class.return_value = mock_client_instance
        
        result = _initialize_gcs_client()
        
        mock_client_class.assert_called_once()
        assert result == mock_client_instance
    
    @patch('process_rrweb_sessions.storage.Client')
    def test_initialize_gcs_client_failure(self, mock_client_class):
        """Test GCS client initialization failure."""
        mock_client_class.side_effect = Exception("Authentication failed")
        
        with pytest.raises(Exception, match="Authentication failed"):
            _initialize_gcs_client()


class TestListJsonFiles:
    """Tests for _list_json_files function."""
    
    def test_list_json_files_success(self, mock_gcs_client, mock_bucket, mixed_files_in_bucket):
        """Test successful listing of JSON files."""
        mock_gcs_client.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = mixed_files_in_bucket
        
        result = _list_json_files(mock_gcs_client, "test-bucket")
        
        # Should only return JSON files in root directory
        expected = [
            "2025-05-02T12:10:50.644423+0000.json",
            "2025-05-02T12:11:30.991832+0000.json"
        ]
        assert result == expected
        mock_gcs_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.list_blobs.assert_called_once()
    
    def test_list_json_files_empty_bucket(self, mock_gcs_client, mock_bucket):
        """Test listing files from empty bucket."""
        mock_gcs_client.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = []
        
        result = _list_json_files(mock_gcs_client, "empty-bucket")
        
        assert result == []
        mock_gcs_client.bucket.assert_called_once_with("empty-bucket")
    
    def test_list_json_files_no_json_files(self, mock_gcs_client, mock_bucket):
        """Test listing files when no JSON files exist."""
        mock_gcs_client.bucket.return_value = mock_bucket
        
        # Create blobs with non-JSON files
        non_json_blobs = []
        txt_blob = Mock()
        txt_blob.name = "readme.txt"
        non_json_blobs.append(txt_blob)
        
        csv_blob = Mock()
        csv_blob.name = "data.csv"
        non_json_blobs.append(csv_blob)
        
        mock_bucket.list_blobs.return_value = non_json_blobs
        
        result = _list_json_files(mock_gcs_client, "no-json-bucket")
        
        assert result == []
    
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


class TestDownloadFileContent:
    """Tests for _download_file_content function."""
    
    def test_download_file_content_success(self, mock_gcs_client, mock_bucket, mock_blob):
        """Test successful file download."""
        mock_gcs_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.download_as_text.return_value = "test file content"
        
        result = _download_file_content(mock_gcs_client, "test-bucket", "test.json")
        
        assert result == "test file content"
        mock_gcs_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("test.json")
        mock_blob.download_as_text.assert_called_once()
    
    def test_download_file_content_file_not_found(self, mock_gcs_client, mock_bucket, mock_blob):
        """Test downloading non-existent file."""
        mock_gcs_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.download_as_text.side_effect = NotFound("File not found")
        
        with pytest.raises(NotFound, match="File not found"):
            _download_file_content(mock_gcs_client, "test-bucket", "nonexistent.json")
    
    def test_download_file_content_permission_denied(self, mock_gcs_client, mock_bucket, mock_blob):
        """Test downloading file with insufficient permissions."""
        mock_gcs_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.download_as_text.side_effect = Forbidden("Access denied")
        
        with pytest.raises(Forbidden, match="Access denied"):
            _download_file_content(mock_gcs_client, "test-bucket", "forbidden.json")
    
    def test_download_file_content_empty_file(self, mock_gcs_client, mock_bucket, mock_blob):
        """Test downloading empty file."""
        mock_gcs_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.download_as_text.return_value = ""
        
        result = _download_file_content(mock_gcs_client, "test-bucket", "empty.json")
        
        assert result == ""
    
    def test_download_file_content_large_file(self, mock_gcs_client, mock_bucket, mock_blob):
        """Test downloading large file."""
        mock_gcs_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        large_content = "x" * 10000  # 10KB of content
        mock_blob.download_as_text.return_value = large_content
        
        result = _download_file_content(mock_gcs_client, "test-bucket", "large.json")
        
        assert result == large_content
        assert len(result) == 10000


class TestDownloadJsonFiles:
    """Tests for download_json_files function (integration tests)."""
    
    @patch('process_rrweb_sessions._initialize_gcs_client')
    @patch('process_rrweb_sessions._list_json_files')
    @patch('process_rrweb_sessions._download_file_content')
    def test_download_json_files_success(self, mock_download, mock_list, mock_init, 
                                       sample_json_files, sample_file_contents):
        """Test successful download of all JSON files."""
        mock_client = Mock(spec=storage.Client)
        mock_init.return_value = mock_client
        mock_list.return_value = sample_json_files
        mock_download.side_effect = sample_file_contents
        
        result = download_json_files("test-bucket")
        
        expected = list(zip(sample_json_files, sample_file_contents))
        assert result == expected
        
        mock_init.assert_called_once()
        mock_list.assert_called_once_with(mock_client, "test-bucket")
        assert mock_download.call_count == len(sample_json_files)
    
    @patch('process_rrweb_sessions._initialize_gcs_client')
    @patch('process_rrweb_sessions._list_json_files')
    def test_download_json_files_empty_bucket(self, mock_list, mock_init):
        """Test download from empty bucket."""
        mock_client = Mock(spec=storage.Client)
        mock_init.return_value = mock_client
        mock_list.return_value = []
        
        result = download_json_files("empty-bucket")
        
        assert result == []
        mock_init.assert_called_once()
        mock_list.assert_called_once_with(mock_client, "empty-bucket")
    
    @patch('process_rrweb_sessions._initialize_gcs_client')
    @patch('process_rrweb_sessions._list_json_files')
    @patch('process_rrweb_sessions._download_file_content')
    def test_download_json_files_partial_failure(self, mock_download, mock_list, mock_init):
        """Test download when some files fail to download."""
        mock_client = Mock(spec=storage.Client)
        mock_init.return_value = mock_client
        mock_list.return_value = ["file1.json", "file2.json", "file3.json"]
        
        # First file succeeds, second fails, third succeeds
        mock_download.side_effect = [
            "content1",
            NotFound("File not found"),
            "content3"
        ]
        
        with pytest.raises(NotFound, match="File not found"):
            download_json_files("test-bucket")
    
    @patch('process_rrweb_sessions._initialize_gcs_client')
    def test_download_json_files_client_init_failure(self, mock_init):
        """Test download when client initialization fails."""
        mock_init.side_effect = Exception("Authentication failed")
        
        with pytest.raises(Exception, match="Authentication failed"):
            download_json_files("test-bucket")
    
    @patch('process_rrweb_sessions._initialize_gcs_client')
    @patch('process_rrweb_sessions._list_json_files')
    def test_download_json_files_list_failure(self, mock_list, mock_init):
        """Test download when listing files fails."""
        mock_client = Mock(spec=storage.Client)
        mock_init.return_value = mock_client
        mock_list.side_effect = Forbidden("Access denied")
        
        with pytest.raises(Forbidden, match="Access denied"):
            download_json_files("test-bucket")


class TestEdgeCases:
    """Tests for edge cases and error conditions."""
    
    def test_list_json_files_with_special_characters(self, mock_gcs_client, mock_bucket):
        """Test listing files with special characters in names."""
        mock_gcs_client.bucket.return_value = mock_bucket
        
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
            "file-with_special.chars.json"
        ]
        assert result == expected
    
    def test_download_file_with_unicode_content(self, mock_gcs_client, mock_bucket, mock_blob):
        """Test downloading file with unicode content."""
        mock_gcs_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        unicode_content = '{"message": "Hello 世界", "emoji": "🌍"}'
        mock_blob.download_as_text.return_value = unicode_content
        
        result = _download_file_content(mock_gcs_client, "test-bucket", "unicode.json")
        
        assert result == unicode_content
    
    def test_list_json_files_case_sensitivity(self, mock_gcs_client, mock_bucket):
        """Test that file extension matching is case sensitive."""
        mock_gcs_client.bucket.return_value = mock_bucket
        
        case_blobs = []
        # Lowercase .json (should be included)
        blob1 = Mock()
        blob1.name = "file1.json"
        case_blobs.append(blob1)
        
        # Uppercase .JSON (should be excluded)
        blob2 = Mock()
        blob2.name = "file2.JSON"
        case_blobs.append(blob2)
        
        # Mixed case .Json (should be excluded)
        blob3 = Mock()
        blob3.name = "file3.Json"
        case_blobs.append(blob3)
        
        mock_bucket.list_blobs.return_value = case_blobs
        
        result = _list_json_files(mock_gcs_client, "case-bucket")
        
        # Only lowercase .json should be included
        assert result == ["file1.json"]
