"""
Unit tests for the normalizer module.

Tests the normalize_chunk function to ensure proper creation of Chunk objects
from cleaned event lists with correct metadata and identifiers.
"""

import pytest
from rrweb_ingest.normalizer import normalize_chunk
from rrweb_ingest.models import Chunk


class TestNormalizeChunk:
    """Test cases for the normalize_chunk function."""

    def test_normalize_basic_chunk(self):
        """Test normalizing a basic chunk with multiple events."""
        events = [
            {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 5}},
            {"type": 3, "timestamp": 1200, "data": {"source": 3, "x": 50}},
            {"type": 3, "timestamp": 1500, "data": {"source": 5, "text": "input"}},
        ]
        session_id = "test_session"
        chunk_index = 0

        result = normalize_chunk(events, session_id, chunk_index)

        # Verify it returns a Chunk object
        assert isinstance(result, Chunk)

        # Verify chunk_id formatting
        assert result.chunk_id == "test_session-chunk000"

        # Verify timestamps
        assert result.start_time == 1000
        assert result.end_time == 1500

        # Verify events are copied
        assert result.events == events
        assert result.events is not events  # Should be a copy

        # Verify metadata
        assert result.metadata["num_events"] == 3
        assert result.metadata["duration_ms"] == 500  # 1500 - 1000

    def test_normalize_chunk_with_higher_index(self):
        """Test chunk ID formatting with higher chunk index."""
        events = [
            {"type": 3, "timestamp": 2000, "data": {"source": 2}},
        ]
        session_id = "session_xyz"
        chunk_index = 42

        result = normalize_chunk(events, session_id, chunk_index)

        assert result.chunk_id == "session_xyz-chunk042"

    def test_normalize_chunk_with_three_digit_index(self):
        """Test chunk ID formatting with three-digit chunk index."""
        events = [
            {"type": 3, "timestamp": 3000, "data": {"source": 2}},
        ]
        session_id = "big_session"
        chunk_index = 999

        result = normalize_chunk(events, session_id, chunk_index)

        assert result.chunk_id == "big_session-chunk999"

    def test_normalize_single_event_chunk(self):
        """Test normalizing a chunk with a single event."""
        events = [
            {"type": 3, "timestamp": 5000, "data": {"source": 2, "id": 10}},
        ]
        session_id = "single_event_session"
        chunk_index = 1

        result = normalize_chunk(events, session_id, chunk_index)

        assert result.chunk_id == "single_event_session-chunk001"
        assert result.start_time == 5000
        assert result.end_time == 5000
        assert result.metadata["num_events"] == 1
        assert result.metadata["duration_ms"] == 0  # Same start and end time

    def test_normalize_events_same_timestamp(self):
        """Test edge case where all events have the same timestamp."""
        events = [
            {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 5}},
            {"type": 3, "timestamp": 1000, "data": {"source": 3, "x": 10}},
            {"type": 3, "timestamp": 1000, "data": {"source": 5, "text": "a"}},
        ]
        session_id = "same_time_session"
        chunk_index = 5

        result = normalize_chunk(events, session_id, chunk_index)

        assert result.start_time == 1000
        assert result.end_time == 1000
        assert result.metadata["duration_ms"] == 0
        assert result.metadata["num_events"] == 3

    def test_normalize_events_out_of_order(self):
        """Test that start_time and end_time are computed correctly even if events are out of order."""
        events = [
            {"type": 3, "timestamp": 2000, "data": {"source": 2}},
            {"type": 3, "timestamp": 1000, "data": {"source": 3}},  # Earlier timestamp
            {"type": 3, "timestamp": 3000, "data": {"source": 5}},
        ]
        session_id = "out_of_order_session"
        chunk_index = 2

        result = normalize_chunk(events, session_id, chunk_index)

        # Should use min and max timestamps regardless of order
        assert result.start_time == 1000
        assert result.end_time == 3000
        assert result.metadata["duration_ms"] == 2000

    def test_empty_events_list_raises_error(self):
        """Test that passing an empty events list raises ValueError."""
        with pytest.raises(
            ValueError, match="Cannot create chunk from empty event list"
        ):
            normalize_chunk([], "session_id", 0)

    def test_empty_session_id_raises_error(self):
        """Test that passing an empty session_id raises ValueError."""
        events = [{"type": 3, "timestamp": 1000, "data": {}}]

        with pytest.raises(ValueError, match="session_id cannot be empty"):
            normalize_chunk(events, "", 0)

    def test_negative_chunk_index_raises_error(self):
        """Test that passing a negative chunk_index raises ValueError."""
        events = [{"type": 3, "timestamp": 1000, "data": {}}]

        with pytest.raises(ValueError, match="chunk_index must be non-negative"):
            normalize_chunk(events, "session_id", -1)

    def test_event_missing_timestamp_raises_error(self):
        """Test that events missing timestamp field raise KeyError."""
        events = [
            {"type": 3, "timestamp": 1000, "data": {}},
            {"type": 3, "data": {}},  # Missing timestamp
        ]

        with pytest.raises(
            KeyError, match="Event at index 1 missing required 'timestamp' field"
        ):
            normalize_chunk(events, "session_id", 0)

    def test_events_list_is_copied(self):
        """Test that the events list is copied, not referenced."""
        original_events = [
            {"type": 3, "timestamp": 1000, "data": {"source": 2}},
        ]

        result = normalize_chunk(original_events, "session_id", 0)

        # Modify original list
        original_events.append({"type": 3, "timestamp": 2000, "data": {}})

        # Chunk should still have original single event
        assert len(result.events) == 1
        assert result.events[0]["timestamp"] == 1000

    def test_metadata_contains_required_fields(self):
        """Test that metadata contains all required fields."""
        events = [
            {"type": 3, "timestamp": 1000, "data": {}},
            {"type": 3, "timestamp": 1500, "data": {}},
        ]

        result = normalize_chunk(events, "session_id", 0)

        # Check required metadata fields
        assert "num_events" in result.metadata
        assert "duration_ms" in result.metadata
        assert isinstance(result.metadata["num_events"], int)
        assert isinstance(result.metadata["duration_ms"], int)

    def test_chunk_object_validation(self):
        """Test that the returned Chunk object passes its own validation."""
        events = [
            {"type": 3, "timestamp": 1000, "data": {"source": 2}},
        ]

        # This should not raise any validation errors
        result = normalize_chunk(events, "valid_session", 0)

        # Verify the chunk is properly constructed
        assert result.chunk_id
        assert result.start_time >= 0
        assert result.end_time >= result.start_time
        assert isinstance(result.events, list)
        assert isinstance(result.metadata, dict)

    def test_complex_session_id_formatting(self):
        """Test chunk ID formatting with complex session IDs."""
        events = [{"type": 3, "timestamp": 1000, "data": {}}]

        # Test with UUID-like session ID
        session_id = "4b458001-0e2c-483e-b013-a3410e3d8b1f"
        result = normalize_chunk(events, session_id, 7)

        expected_chunk_id = "4b458001-0e2c-483e-b013-a3410e3d8b1f-chunk007"
        assert result.chunk_id == expected_chunk_id

    def test_large_timestamp_values(self):
        """Test handling of large timestamp values."""
        events = [
            {"type": 3, "timestamp": 1640995200000, "data": {}},  # Jan 1, 2022 in ms
            {"type": 3, "timestamp": 1640995260000, "data": {}},  # 1 minute later
        ]

        result = normalize_chunk(events, "large_timestamp_session", 0)

        assert result.start_time == 1640995200000
        assert result.end_time == 1640995260000
        assert result.metadata["duration_ms"] == 60000  # 1 minute in ms
