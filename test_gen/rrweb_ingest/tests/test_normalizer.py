"""
Unit tests for the normalizer module.

Tests the normalize_chunk function to ensure proper creation of Chunk objects
from cleaned event lists with correct metadata and identifiers.
"""

import pytest
from rrweb_ingest.normalizer import normalize_chunk


class TestNormalizeChunk:
    """Test cases for the normalize_chunk function."""

    def test_normalize_events_same_timestamp(self):
        """Test edge case where all events have the same timestamp."""
        events = [
            {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 5}},
            {"type": 3, "timestamp": 1000, "data": {"source": 3, "x": 10}},
            {"type": 3, "timestamp": 1000, "data": {"source": 5, "text": "a"}},
        ]
        session_id = "same_time_session"
        chunk_index = 5

        result = normalize_chunk(events, session_id, chunk_index, {})

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

        result = normalize_chunk(events, session_id, chunk_index, {})

        # Should use min and max timestamps regardless of order
        assert result.start_time == 1000
        assert result.end_time == 3000
        assert result.metadata["duration_ms"] == 2000

    def test_empty_events_list_raises_error(self):
        """Test that passing an empty events list raises ValueError."""
        with pytest.raises(
            ValueError, match="Cannot create chunk from empty event list"
        ):
            normalize_chunk([], "session_id", 0, {})

    def test_empty_session_id_raises_error(self):
        """Test that passing an empty session_id raises ValueError."""
        events = [{"type": 3, "timestamp": 1000, "data": {}}]

        with pytest.raises(ValueError, match="session_id cannot be empty"):
            normalize_chunk(events, "", 0, {})

    def test_negative_chunk_index_raises_error(self):
        """Test that passing a negative chunk_index raises ValueError."""
        events = [{"type": 3, "timestamp": 1000, "data": {}}]

        with pytest.raises(ValueError, match="chunk_index must be non-negative"):
            normalize_chunk(events, "session_id", -1, {})

    def test_event_missing_timestamp_raises_error(self):
        """Test that events missing timestamp field raise KeyError."""
        events = [
            {"type": 3, "timestamp": 1000, "data": {}},
            {"type": 3, "data": {}},  # Missing timestamp
        ]

        with pytest.raises(
            KeyError, match="Event at index 1 missing required 'timestamp' field"
        ):
            normalize_chunk(events, "session_id", 0, {})

    def test_events_list_is_copied(self):
        """Test that the events list is copied, not referenced."""
        original_events = [
            {"type": 3, "timestamp": 1000, "data": {"source": 2}},
        ]

        result = normalize_chunk(original_events, "session_id", 0, {})

        # Modify original list
        original_events.append({"type": 3, "timestamp": 2000, "data": {}})

        # Chunk should still have original single event
        assert len(result.events) == 1
        assert result.events[0]["timestamp"] == 1000
