"""
Tests for the extract_and_save_features function.

Tests that feature extraction and JSON file saving work correctly,
including error handling, file naming, and statistics tracking.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from feature_extraction.pipeline import extract_and_save_features
from feature_extraction.models import FeatureChunk


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test output files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_feature_chunk():
    """Create a sample FeatureChunk for testing."""
    return FeatureChunk(
        chunk_id="test-chunk-001",
        start_time=1000,
        end_time=2000,
        events=[{"type": 3, "timestamp": 1500}],
        features={
            "dom_mutations": [],
            "interactions": [],
            "inter_event_delays": [],
            "reaction_delays": [],
            "ui_nodes": {},
            "mouse_clusters": [],
            "scroll_patterns": [],
        },
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
            session_dir="dummy", output_dir=str(output_path), verbose=False
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
            session_dir="dummy", output_dir=str(temp_output_dir), verbose=False
        )

    # Check statistics
    assert stats["chunks_saved"] == 1
    assert stats["sessions_processed"] == 0  # Will be 0 due to mocking
    assert len(stats["errors"]) == 0

    # Check file was created with correct name
    expected_filename = "session-123_test-chunk-001.json"
    output_file = temp_output_dir / expected_filename
    assert output_file.exists()

    # Verify file contents
    with open(output_file, "r") as f:
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
                features={
                    "dom_mutations": [],
                    "interactions": [],
                    "inter_event_delays": [],
                    "reaction_delays": [],
                    "ui_nodes": {},
                    "mouse_clusters": [],
                    "scroll_patterns": [],
                },
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
                features={
                    "dom_mutations": [],
                    "interactions": [],
                    "inter_event_delays": [],
                    "reaction_delays": [],
                    "ui_nodes": {},
                    "mouse_clusters": [],
                    "scroll_patterns": [],
                },
                metadata={},
            ),
            {"session_id": "session-B"},
        ),
    ]

    with patch("feature_extraction.pipeline.iterate_feature_extraction") as mock_iter:
        mock_iter.return_value = iter(chunks_and_metadata)

        stats = extract_and_save_features(
            session_dir="dummy", output_dir=str(temp_output_dir), verbose=False
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
    with open(file1, "r") as f:
        data1 = json.load(f)
    with open(file2, "r") as f:
        data2 = json.load(f)

    assert data1["chunk_id"] == "chunk-001"
    assert data2["chunk_id"] == "chunk-002"


def test_extract_and_save_features_handles_chunk_processing_error(
    temp_output_dir, sample_feature_chunk
):
    """Test error handling when individual chunk processing fails."""
    chunk_metadata = {"session_id": "session-123"}

    # Mock the feature chunk to have a problematic to_dict method
    problematic_chunk = MagicMock()
    problematic_chunk.chunk_id = "problematic-chunk"
    problematic_chunk.to_dict.side_effect = Exception("Serialization failed")

    chunks_data = [
        (sample_feature_chunk, chunk_metadata),  # This should succeed
        (problematic_chunk, chunk_metadata),  # This should fail
    ]

    with patch("feature_extraction.pipeline.iterate_feature_extraction") as mock_iter:
        mock_iter.return_value = iter(chunks_data)

        stats = extract_and_save_features(
            session_dir="dummy", output_dir=str(temp_output_dir), verbose=False
        )

    # Check statistics - one success, one error
    assert stats["chunks_saved"] == 1
    assert len(stats["errors"]) == 1
    assert "problematic-chunk" in stats["errors"][0]
    assert "Serialization failed" in stats["errors"][0]

    # Check only the successful file was created
    successful_file = temp_output_dir / "session-123_test-chunk-001.json"
    problematic_file = temp_output_dir / "session-123_problematic-chunk.json"
    assert successful_file.exists()
    assert not problematic_file.exists()


def test_extract_and_save_features_handles_fatal_error(temp_output_dir):
    """Test error handling when the entire iteration fails."""
    with patch("feature_extraction.pipeline.iterate_feature_extraction") as mock_iter:
        mock_iter.side_effect = Exception("Fatal iteration error")

        stats = extract_and_save_features(
            session_dir="dummy", output_dir=str(temp_output_dir), verbose=False
        )

    # Check error was recorded
    assert stats["chunks_saved"] == 0
    assert stats["sessions_processed"] == 0
    assert len(stats["errors"]) == 1
    assert "Fatal error in feature extraction" in stats["errors"][0]
    assert "Fatal iteration error" in stats["errors"][0]


def test_extract_and_save_features_verbose_output(
    temp_output_dir, sample_feature_chunk, capsys
):
    """Test that verbose mode produces expected output."""
    chunk_metadata = {"session_id": "session-123"}

    with patch("feature_extraction.pipeline.iterate_feature_extraction") as mock_iter:
        mock_iter.return_value = iter([(sample_feature_chunk, chunk_metadata)])

        stats = extract_and_save_features(
            session_dir="dummy", output_dir=str(temp_output_dir), verbose=True
        )

    # Check console output
    captured = capsys.readouterr()
    assert "Processing sessions from:" in captured.out
    assert "Saving features to:" in captured.out
    assert "Saved: session-123_test-chunk-001.json" in captured.out
    assert "Processing Summary:" in captured.out
    assert "Chunks saved: 1" in captured.out


def test_extract_and_save_features_max_sessions_parameter(temp_output_dir):
    """Test that max_sessions parameter is passed through correctly."""
    with patch("feature_extraction.pipeline.iterate_feature_extraction") as mock_iter:
        mock_iter.return_value = iter([])

        extract_and_save_features(
            session_dir="test/sessions",
            output_dir=str(temp_output_dir),
            max_sessions=5,
            verbose=False,
        )

    # Verify mock was called with correct parameters
    mock_iter.assert_called_with("test/sessions", max_sessions=5)


def test_extract_and_save_features_counts_feature_statistics(temp_output_dir):
    """Test that feature counts are calculated correctly in statistics."""
    from feature_extraction.models import DomMutation, UserInteraction, UINode

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
            "inter_event_delays": [],
            "reaction_delays": [],
            "ui_nodes": {
                1: UINode(1, "div", {}, "", None),
                2: UINode(2, "button", {}, "Click", 1),
            },
            "mouse_clusters": [],
            "scroll_patterns": [],
        },
        metadata={},
    )

    chunk_metadata = {"session_id": "stats-test"}

    with patch("feature_extraction.pipeline.iterate_feature_extraction") as mock_iter:
        mock_iter.return_value = iter([(chunk_with_features, chunk_metadata)])

        stats = extract_and_save_features(
            session_dir="dummy", output_dir=str(temp_output_dir), verbose=False
        )

    # Check feature counts in statistics
    assert stats["total_features"]["dom_mutations"] == 2
    assert stats["total_features"]["interactions"] == 1
    assert stats["total_features"]["ui_nodes"] == 2
    assert stats["total_features"]["inter_event_delays"] == 0
    assert stats["total_features"]["reaction_delays"] == 0
    assert stats["total_features"]["mouse_clusters"] == 0
    assert stats["total_features"]["scroll_patterns"] == 0


def test_extract_and_save_features_json_formatting(
    temp_output_dir, sample_feature_chunk
):
    """Test that JSON files are properly formatted and readable."""
    chunk_metadata = {"session_id": "formatting-test"}

    with patch("feature_extraction.pipeline.iterate_feature_extraction") as mock_iter:
        mock_iter.return_value = iter([(sample_feature_chunk, chunk_metadata)])

        extract_and_save_features(
            session_dir="dummy", output_dir=str(temp_output_dir), verbose=False
        )

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
