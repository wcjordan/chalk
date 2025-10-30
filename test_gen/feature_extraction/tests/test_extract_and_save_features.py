"""
Tests for the extract_and_save_features function.

Tests that feature extraction and JSON file saving work correctly,
including error handling, file naming, and statistics tracking.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from feature_extraction.pipeline import extract_and_save_features
from feature_extraction.models import (
    DomMutation,
    FeatureChunk,
    UserInteraction,
    UINode,
    create_empty_features_obj,
)


@pytest.fixture(name="temp_output_dir")
def fixture_temp_output_dir():
    """Create a temporary directory for test output files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture(name="sample_feature_chunk")
def fixture_sample_feature_chunk():
    """Create a sample FeatureChunk for testing."""
    return FeatureChunk(
        chunk_id="test-chunk-001",
        start_time=1000,
        end_time=2000,
        events=[{"type": 3, "timestamp": 1500}],
        features=create_empty_features_obj(),
        metadata={"test": True},
    )


def test_extract_and_save_features_creates_output_directory(temp_output_dir):
    """Test that the function creates the output directory if it doesn't exist."""
    output_path = temp_output_dir / "new_output_dir"
    assert not output_path.exists()

    # Mock the iterator to return no chunks
    with patch("feature_extraction.pipeline.iterate_feature_extraction") as mock_iter:
        mock_iter.return_value = iter([])

        stats = extract_and_save_features(
            session_dir="dummy", output_dir=str(output_path)
        )

    assert output_path.exists()
    assert output_path.is_dir()
    assert stats["chunks_saved"] == 0


def test_extract_and_save_features_saves_single_chunk(
    temp_output_dir, sample_feature_chunk
):
    """Test that a single feature chunk is saved correctly."""
    chunk_metadata = {
        "session_id": "session-123",
        "dom_initialized_from_snapshot": True,
        "dom_state_nodes_final": 10,
    }

    with patch("feature_extraction.pipeline.iterate_feature_extraction") as mock_iter:
        mock_iter.return_value = iter([(sample_feature_chunk, chunk_metadata)])

        stats = extract_and_save_features(
            session_dir="dummy", output_dir=str(temp_output_dir)
        )

    # Check statistics
    assert stats["chunks_saved"] == 1
    assert stats["sessions_processed"] == 1
    assert len(stats["errors"]) == 0

    # Check file was created with correct name
    expected_filename = "session-123_test-chunk-001.json"
    output_file = temp_output_dir / expected_filename
    assert output_file.exists()

    # Verify file contents
    with open(output_file, "r", encoding="utf-8") as f:
        saved_data = json.load(f)

    assert saved_data["chunk_id"] == "test-chunk-001"
    assert saved_data["start_time"] == 1000
    assert saved_data["end_time"] == 2000
    assert "features" in saved_data
    assert "processing_metadata" in saved_data

    # Check processing metadata
    processing_meta = saved_data["processing_metadata"]
    assert processing_meta["dom_initialized_from_snapshot"] is True
    assert processing_meta["dom_state_nodes_final"] == 10
    assert processing_meta["feature_extraction_version"] == "1.0"


def test_extract_and_save_features_saves_multiple_chunks(temp_output_dir):
    """Test that multiple feature chunks are saved correctly."""
    chunks_and_metadata = [
        (
            FeatureChunk(
                chunk_id="chunk-001",
                start_time=1000,
                end_time=2000,
                events=[],
                features=create_empty_features_obj(),
                metadata={},
            ),
            {"session_id": "session-A"},
        ),
        (
            FeatureChunk(
                chunk_id="chunk-002",
                start_time=3000,
                end_time=4000,
                events=[],
                features=create_empty_features_obj(),
                metadata={},
            ),
            {"session_id": "session-B"},
        ),
    ]

    with patch("feature_extraction.pipeline.iterate_feature_extraction") as mock_iter:
        mock_iter.return_value = iter(chunks_and_metadata)

        stats = extract_and_save_features(
            session_dir="dummy", output_dir=str(temp_output_dir)
        )

    # Check statistics
    assert stats["chunks_saved"] == 2
    assert len(stats["errors"]) == 0

    # Check both files were created
    file1 = temp_output_dir / "session-A_chunk-001.json"
    file2 = temp_output_dir / "session-B_chunk-002.json"
    assert file1.exists()
    assert file2.exists()

    # Verify both files have correct content
    with open(file1, "r", encoding="utf-8") as f:
        data1 = json.load(f)
    with open(file2, "r", encoding="utf-8") as f:
        data2 = json.load(f)

    assert data1["chunk_id"] == "chunk-001"
    assert data2["chunk_id"] == "chunk-002"


def test_extract_and_save_features_verbose_output(
    caplog, temp_output_dir, sample_feature_chunk
):
    """Test that verbose mode produces expected output."""
    chunk_metadata = {"session_id": "session-123"}

    with patch(
        "feature_extraction.pipeline.iterate_feature_extraction"
    ) as mock_iter, caplog.at_level("DEBUG"):
        mock_iter.return_value = iter([(sample_feature_chunk, chunk_metadata)])

        extract_and_save_features(session_dir="dummy", output_dir=str(temp_output_dir))

    # Check console output
    assert "Processing sessions from:" in caplog.text
    assert "Saving features to:" in caplog.text
    assert "Saved: session-123_test-chunk-001.json" in caplog.text
    assert "Processing Summary:" in caplog.text
    assert "Chunks saved: 1" in caplog.text


def test_extract_and_save_features_max_sessions_parameter(temp_output_dir):
    """Test that max_sessions parameter is passed through correctly."""
    with patch("feature_extraction.pipeline.iterate_feature_extraction") as mock_iter:
        mock_iter.return_value = iter([])

        extract_and_save_features(
            session_dir="test/sessions",
            output_dir=str(temp_output_dir),
            max_sessions=5,
        )

    # Verify mock was called with correct parameters
    mock_iter.assert_called_with("test/sessions", max_sessions=5)


def test_extract_and_save_features_counts_feature_statistics(temp_output_dir):
    """Test that feature counts are calculated correctly in statistics."""

    chunk_with_features = FeatureChunk(
        chunk_id="feature-chunk",
        start_time=1000,
        end_time=2000,
        events=[],
        features={
            "dom_mutations": [
                DomMutation("add", 1, {}, 1000),
                DomMutation("remove", 2, {}, 1100),
            ],
            "interactions": [
                UserInteraction("click", 3, {}, 1200),
            ],
            "ui_nodes": {
                1: UINode(1, "div", {}, "", None),
                2: UINode(2, "button", {}, "Click", 1),
            },
            "scroll_patterns": [],
        },
        metadata={},
    )

    chunk_metadata = {"session_id": "stats-test"}

    with patch("feature_extraction.pipeline.iterate_feature_extraction") as mock_iter:
        mock_iter.return_value = iter([(chunk_with_features, chunk_metadata)])

        stats = extract_and_save_features(
            session_dir="dummy", output_dir=str(temp_output_dir)
        )

    # Check feature counts in statistics
    assert stats["total_features"]["dom_mutations"] == 2
    assert stats["total_features"]["interactions"] == 1
    assert stats["total_features"]["ui_nodes"] == 2
    assert stats["total_features"]["scroll_patterns"] == 0


def test_extract_and_save_features_json_formatting(
    temp_output_dir, sample_feature_chunk
):
    """Test that JSON files are properly formatted and readable."""
    chunk_metadata = {"session_id": "formatting-test"}

    with patch("feature_extraction.pipeline.iterate_feature_extraction") as mock_iter:
        mock_iter.return_value = iter([(sample_feature_chunk, chunk_metadata)])

        extract_and_save_features(session_dir="dummy", output_dir=str(temp_output_dir))

    # Read the saved file and verify it's properly formatted JSON
    output_file = temp_output_dir / "formatting-test_test-chunk-001.json"

    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Should be indented (pretty-printed)
    assert "  " in content  # Check for indentation

    # Should parse as valid JSON
    data = json.loads(content)
    assert data["chunk_id"] == "test-chunk-001"

    # Check that ensure_ascii=False worked (should support Unicode if present)
    # The file should be readable with UTF-8 encoding
