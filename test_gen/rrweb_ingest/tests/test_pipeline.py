"""
Integration tests for the end-to-end ingest pipeline.

Tests the ingest_session function to ensure proper integration of all preprocessing
components and correct handling of various session scenarios and error conditions.
"""

import json
from unittest.mock import patch
import tempfile

import pytest

from rrweb_ingest.pipeline import ingest_session
from rrweb_ingest.models import Chunk
from rrweb_util import EventType, IncrementalSource


@pytest.fixture(name="create_session_file")
def fixture_create_session_file():
    """Helper function to create a temporary rrweb session JSON file."""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as f:

        def _create_session_file(events, session_guid="test_session", raw_string=None):
            """Create a temporary file with rrweb session data."""
            if raw_string:
                f.write(raw_string)
            else:
                data = {
                    "session_guid": session_guid,
                    "rrweb_data": events,
                    "metadata": {"environment": "test"},
                }
                json.dump(data, f)
            f.flush()
            return f.name

        yield _create_session_file


class TestIngestSession:
    """Test cases for the ingest_session function."""

    def test_ingest_basic_session(self, create_session_file):
        """Test ingesting a basic session with mixed event types."""
        events = [
            # FullSnapshot to establish baseline
            {
                "type": EventType.FULL_SNAPSHOT,
                "timestamp": 1000,
                "data": {"source": IncrementalSource.MUTATION},
            },
            # Some interactions
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1100,
                "data": {"source": IncrementalSource.MOUSE_INTERACTION, "id": 5},
            },  # click
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1200,
                "data": {"source": IncrementalSource.INPUT, "text": "hello"},
            },  # input
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1300,
                "data": {"source": IncrementalSource.SCROLL, "x": 50, "y": 100},
            },  # scroll
            # Another snapshot
            {
                "type": EventType.FULL_SNAPSHOT,
                "timestamp": 2000,
                "data": {"source": IncrementalSource.MUTATION},
            },
            # More interactions
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 2100,
                "data": {"source": IncrementalSource.MOUSE_INTERACTION, "id": 10},
            },  # click
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 2200,
                "data": {"source": IncrementalSource.MOUSE_INTERACTION, "id": 15},
            },  # click
        ]

        temp_path = create_session_file(events)
        session_id = "test_session_basic"

        result = ingest_session(session_id, temp_path)

        # Should return a non-empty list of Chunk objects
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(chunk, Chunk) for chunk in result)

        # Verify each chunk has required fields populated
        for chunk in result:
            assert chunk.chunk_id.startswith(session_id)
            assert chunk.start_time >= 0
            assert chunk.end_time >= chunk.start_time
            assert isinstance(chunk.events, list)
            assert len(chunk.events) > 0
            assert isinstance(chunk.metadata, dict)
            assert "num_events" in chunk.metadata
            assert "duration_ms" in chunk.metadata

    def test_ingest_session_with_noise_filtering(self, create_session_file):
        """Test that noise events are properly filtered during ingestion."""
        events = [
            {
                "type": EventType.FULL_SNAPSHOT,
                "timestamp": 1000,
                "data": {"source": IncrementalSource.MUTATION},
            },  # snapshot
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1100,
                "data": {"source": IncrementalSource.MOUSE_INTERACTION, "id": 5},
            },  # click
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1150,
                "data": {"source": IncrementalSource.MOUSE_MOVE},
            },  # mousemove (noise)
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1200,
                "data": {"source": IncrementalSource.SCROLL, "x": 5, "y": 5},
            },  # micro-scroll (noise)
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1300,
                "data": {"source": IncrementalSource.MOUSE_INTERACTION, "id": 10},
            },  # click
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1300,
                "data": {"source": IncrementalSource.MOUSE_INTERACTION, "id": 10},
            },  # duplicate
        ]

        temp_path = create_session_file(events)
        result = ingest_session("noise_test", temp_path)

        # Should have filtered out noise and duplicates
        assert len(result) == 1
        chunk = result[0]

        # Should only have the 2 unique click events (noise filtered, duplicate removed)
        assert chunk.metadata["num_events"] == 2
        assert all(
            event["data"]["source"] == IncrementalSource.MOUSE_INTERACTION
            for event in chunk.events
        )

    def test_ingest_session_chunking_by_snapshots(self, create_session_file):
        """Test that snapshots create proper chunk boundaries."""
        events = [
            # First chunk
            {"type": 2, "timestamp": 1000, "data": {"source": 0}},  # snapshot 1
            {"type": 3, "timestamp": 1100, "data": {"source": 2, "id": 1}},
            {"type": 3, "timestamp": 1200, "data": {"source": 2, "id": 2}},
            # Second chunk
            {"type": 2, "timestamp": 2000, "data": {"source": 0}},  # snapshot 2
            {"type": 3, "timestamp": 2100, "data": {"source": 2, "id": 3}},
            {"type": 3, "timestamp": 2200, "data": {"source": 2, "id": 4}},
            # Third chunk
            {"type": 2, "timestamp": 3000, "data": {"source": 0}},  # snapshot 3
            {"type": 3, "timestamp": 3100, "data": {"source": 2, "id": 5}},
        ]

        temp_path = create_session_file(events)
        result = ingest_session("snapshot_test", temp_path)

        # Should create multiple chunks based on snapshot boundaries
        assert len(result) >= 2  # At least 2 chunks expected

        # Verify chunk IDs are sequential
        for i, chunk in enumerate(result):
            expected_id = f"snapshot_test-chunk{i:03d}"
            assert chunk.chunk_id == expected_id

    def test_ingest_session_max_gap_ms_parameter(self, create_session_file):
        """Test that max_gap_ms parameter affects chunking behavior."""
        events = [
            {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 1}},
            {"type": 3, "timestamp": 1100, "data": {"source": 2, "id": 2}},
            {"type": 3, "timestamp": 8000, "data": {"source": 2, "id": 3}},  # 6.9s gap
            {"type": 3, "timestamp": 8100, "data": {"source": 2, "id": 4}},
        ]

        temp_path = create_session_file(events)

        # With large max_gap_ms, should stay in one chunk
        with patch("rrweb_ingest.segmenter.config.MAX_GAP_MS", 10_000):
            result_large_gap = ingest_session("gap_test", temp_path)

        # With small max_gap_ms, should split into multiple chunks
        with patch("rrweb_ingest.segmenter.config.MAX_GAP_MS", 5_000):
            result_small_gap = ingest_session("gap_test", temp_path)

        # Large gap should have fewer chunks than small gap
        assert len(result_large_gap) <= len(result_small_gap)

    def test_ingest_session_max_events_parameter(self, create_session_file):
        """Test that max_events parameter affects chunking behavior."""
        # Create 10 events close together in time
        events = [
            {"type": 3, "timestamp": 1000 + i * 10, "data": {"source": 2, "id": i}}
            for i in range(10)
        ]

        temp_path = create_session_file(events)

        # With large max_events, should stay in fewer chunks
        with patch("rrweb_ingest.segmenter.config.MAX_EVENTS", 20):
            result_large_max = ingest_session("events_test", temp_path)

        # With small max_events, should split into more chunks
        with patch("rrweb_ingest.segmenter.config.MAX_EVENTS", 3):
            result_small_max = ingest_session("events_test", temp_path)

        # Small max should create more chunks than large max
        assert len(result_small_max) > len(result_large_max)

        # Verify no chunk exceeds the max_events limit
        for chunk in result_small_max:
            assert chunk.metadata["num_events"] <= 3

    def test_ingest_session_micro_scroll_threshold_parameter(self, create_session_file):
        """Test that micro_scroll_threshold parameter affects filtering."""
        events = [
            {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 1}},  # click
            {
                "type": 3,
                "timestamp": 1100,
                "data": {"source": 3, "x": 15, "y": 15},
            },  # scroll
            {"type": 3, "timestamp": 1200, "data": {"source": 2, "id": 2}},  # click
        ]

        temp_path = create_session_file(events)

        # With high threshold, scroll should be filtered as noise
        with patch("rrweb_ingest.filter.config.MICRO_SCROLL_THRESHOLD", 20):
            result_high_threshold = ingest_session("scroll_test", temp_path)

        # With low threshold, scroll should be kept
        with patch("rrweb_ingest.filter.config.MICRO_SCROLL_THRESHOLD", 10):
            result_low_threshold = ingest_session("scroll_test", temp_path)

        # High threshold should filter out the scroll, keeping only clicks
        high_events = sum(
            chunk.metadata["num_events"] for chunk in result_high_threshold
        )
        low_events = sum(chunk.metadata["num_events"] for chunk in result_low_threshold)

        assert high_events < low_events

    def test_ingest_session_file_not_found(self):
        """Test that FileNotFoundError is properly propagated."""
        with pytest.raises(FileNotFoundError):
            ingest_session("test", "/nonexistent/path/file.json")

    def test_ingest_session_invalid_json(self, create_session_file):
        """Test that JSONDecodeError is properly propagated."""
        temp_path = create_session_file([], raw_string='{"invalid": json}')

        with pytest.raises(json.JSONDecodeError):
            ingest_session("test", temp_path)

    def test_ingest_session_malformed_session_structure(self):
        """Test that ValueError is raised for malformed session structure."""
        # Create file without rrweb_data field
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"session_guid": "test", "metadata": {}}, f)
            f.flush()
            temp_path = f.name

        with pytest.raises(ValueError, match="Missing 'rrweb_data' field"):
            ingest_session("test", temp_path)

    def test_ingest_session_empty_session_id(self, create_session_file):
        """Test that empty session_id raises ValueError."""
        events = [{"type": 3, "timestamp": 1000, "data": {"source": 2}}]
        temp_path = create_session_file(events)

        with pytest.raises(ValueError, match="session_id cannot be empty"):
            ingest_session("", temp_path)

    def test_ingest_session_events_missing_required_fields(self, create_session_file):
        """Test that events missing required fields raise appropriate errors."""
        events = [
            {"type": 3, "data": {"source": 2}},  # Missing timestamp
        ]
        temp_path = create_session_file(events)

        with pytest.raises(ValueError, match="missing required fields"):
            ingest_session("test", temp_path)

    def test_ingest_session_empty_after_filtering(self, create_session_file):
        """Test handling of chunks that become empty after noise filtering."""
        events = [
            {"type": 2, "timestamp": 1000, "data": {"source": 0}},  # snapshot
            {"type": 3, "timestamp": 1100, "data": {"source": 1}},  # mousemove (noise)
            {"type": 3, "timestamp": 1200, "data": {"source": 1}},  # mousemove (noise)
            {"type": 2, "timestamp": 2000, "data": {"source": 0}},  # snapshot
            {"type": 3, "timestamp": 2100, "data": {"source": 2, "id": 1}},  # click
        ]

        temp_path = create_session_file(events)
        result = ingest_session("empty_test", temp_path)

        # Should skip empty chunks and only return chunks with events
        assert len(result) == 1
        assert result[0].metadata["num_events"] == 1

    def test_ingest_session_preserves_event_order(self, create_session_file):
        """Test that event order is preserved within chunks."""
        events = [
            {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 1}},
            {"type": 3, "timestamp": 1100, "data": {"source": 2, "id": 2}},
            {"type": 3, "timestamp": 1200, "data": {"source": 2, "id": 3}},
        ]

        temp_path = create_session_file(events)
        result = ingest_session("order_test", temp_path)

        assert len(result) == 1
        chunk = result[0]

        # Verify events are in correct order
        assert chunk.events[0]["data"]["id"] == 1
        assert chunk.events[1]["data"]["id"] == 2
        assert chunk.events[2]["data"]["id"] == 3

    def test_ingest_session_metadata_accuracy(self, create_session_file):
        """Test that chunk metadata is accurately calculated."""
        events = [
            {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 1}},
            {"type": 3, "timestamp": 1500, "data": {"source": 2, "id": 2}},
            {"type": 3, "timestamp": 2000, "data": {"source": 2, "id": 3}},
        ]

        temp_path = create_session_file(events)
        result = ingest_session("metadata_test", temp_path)

        assert len(result) == 1
        chunk = result[0]

        # Verify metadata calculations
        assert chunk.start_time == 1000
        assert chunk.end_time == 2000
        assert chunk.metadata["num_events"] == 3
        assert chunk.metadata["duration_ms"] == 1000  # 2000 - 1000

    def test_ingest_session_complex_integration(self, create_session_file):
        """Test complex scenario with multiple chunking criteria and filtering."""
        events = [
            # First chunk - before snapshot
            {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 1}},
            {"type": 3, "timestamp": 1100, "data": {"source": 1}},  # noise
            # Snapshot boundary
            {"type": 2, "timestamp": 1500, "data": {"source": 0}},
            # Second chunk - after snapshot, before time gap
            {"type": 3, "timestamp": 1600, "data": {"source": 2, "id": 2}},
            {"type": 3, "timestamp": 1700, "data": {"source": 2, "id": 3}},
            # Large time gap
            {"type": 3, "timestamp": 15000, "data": {"source": 2, "id": 4}},
            {"type": 3, "timestamp": 15100, "data": {"source": 2, "id": 5}},
        ]

        temp_path = create_session_file(events)
        with patch("rrweb_ingest.segmenter.config.MAX_GAP_MS", 5000):
            result = ingest_session("complex_test", temp_path)

        # Should create multiple chunks due to snapshot and time gap
        assert len(result) >= 3

        # Verify all chunks have valid structure
        for chunk in result:
            assert chunk.metadata["num_events"] > 0
            assert chunk.start_time <= chunk.end_time
            assert len(chunk.events) == chunk.metadata["num_events"]

        # Verify noise was filtered (no mousemove events)
        all_events = []
        for chunk in result:
            all_events.extend(chunk.events)

        assert all(event["data"]["source"] != 1 for event in all_events)

    def test_ingest_session_with_custom_filters(self, create_session_file):
        """Test that custom filters are properly applied during ingestion."""
        events = [
            {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 1}},  # click
            {
                "type": 3,
                "timestamp": 1100,
                "data": {"source": 99, "id": 2},
            },  # custom source
            {
                "type": 3,
                "timestamp": 1200,
                "data": {"source": 5, "text": "input"},
            },  # input
        ]

        # Custom filter that removes events with source == 99
        def filter_source_99(event):
            return event.get("data", {}).get("source") == 99

        temp_path = create_session_file(events)
        with patch(
            "rrweb_ingest.segmenter.config.DEFAULT_CUSTOM_FILTERS", [filter_source_99]
        ):
            result = ingest_session("custom_filter_test", temp_path)

        # Should have filtered out the custom source event
        assert len(result) == 1
        chunk = result[0]
        assert chunk.metadata["num_events"] == 2

        # Verify the custom source event was filtered out
        sources = [event["data"]["source"] for event in chunk.events]
        assert 99 not in sources
        assert 2 in sources  # click
        assert 5 in sources  # input

    def test_ingest_session_config_defaults_when_none(self, create_session_file):
        """Test that pipeline uses config defaults."""
        events = [
            {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 1}},
            {"type": 3, "timestamp": 2000, "data": {"source": 2, "id": 2}},
        ]

        temp_path = create_session_file(events)

        # Explicitly pass None to test default fallback
        result = ingest_session("defaults_test", temp_path)

        assert len(result) == 1
        assert result[0].metadata["num_events"] == 2

    def test_ingest_session_all_events_filtered_as_noise(self, create_session_file):
        """Test handling when all events in a chunk are filtered as noise."""
        events = [
            {"type": 2, "timestamp": 1000, "data": {"source": 0}},  # snapshot
            {"type": 3, "timestamp": 1100, "data": {"source": 1}},  # mousemove (noise)
            {"type": 3, "timestamp": 1200, "data": {"source": 1}},  # mousemove (noise)
        ]

        temp_path = create_session_file(events)
        result = ingest_session("all_noise_test", temp_path)

        # Should return empty list when all interactions are filtered
        assert len(result) == 0

    def test_ingest_session_consecutive_snapshots_no_interactions(
        self, create_session_file
    ):
        """Test handling of consecutive snapshots with no interactions between."""
        events = [
            {"type": 2, "timestamp": 1000, "data": {"source": 0}},  # snapshot 1
            {"type": 2, "timestamp": 2000, "data": {"source": 0}},  # snapshot 2
            {"type": 2, "timestamp": 3000, "data": {"source": 0}},  # snapshot 3
            {
                "type": 3,
                "timestamp": 4000,
                "data": {"source": 2, "id": 1},
            },  # interaction
        ]

        temp_path = create_session_file(events)
        result = ingest_session("consecutive_snapshots_test", temp_path)

        # Should only create one chunk for the final interaction
        assert len(result) == 1
        assert result[0].metadata["num_events"] == 1
