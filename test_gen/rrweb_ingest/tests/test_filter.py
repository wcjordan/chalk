"""
Unit tests for the noise filtering module.

Tests the is_low_signal function to ensure proper identification
and removal of low-signal events from rrweb chunks.
"""

# pylint: disable=duplicate-code

from unittest.mock import patch

from rrweb_ingest.filter import is_low_signal
from rrweb_util import EventType, IncrementalSource


class TestIsLowSignal:
    """Test cases for the is_low_signal function."""

    def test_mousemove_events_are_noise(self):
        """Test that mousemove events (source == 1) are identified as noise."""
        mousemove_event = {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {
                "source": IncrementalSource.MOUSE_MOVE,
                "positions": [{"x": 100, "y": 200}],
            },
        }

        assert is_low_signal(mousemove_event) is True

    def test_non_incremental_events_not_filtered(self):
        """Test that non-IncrementalSnapshot events are never filtered."""
        # FullSnapshot event
        snapshot_event = {
            "type": EventType.FULL_SNAPSHOT,
            "timestamp": 1000,
            "data": {"source": IncrementalSource.MOUSE_MOVE},
        }
        assert is_low_signal(snapshot_event) is False

        # Meta event
        meta_event = {
            "type": EventType.META,
            "timestamp": 1000,
            "data": {"source": IncrementalSource.MOUSE_MOVE},
        }
        assert is_low_signal(meta_event) is False

    def test_scroll_events_are_noise(self):
        """Test that scrolls events are identified as noise."""
        scroll_event = {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {
                "source": IncrementalSource.SCROLL,
                "x": 5,
                "y": 10,
            },  # Both below default 20px threshold
        }

        assert is_low_signal(scroll_event) is True

    def test_non_mutation_interaction_events(self):
        """Test that non-mutation interaction events are not filtered."""
        # Click event (source == 2)
        click_event = {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {"source": IncrementalSource.MOUSE_INTERACTION, "type": 0, "id": 5},
        }
        assert is_low_signal(click_event) is False

        # Input event (source == 5)
        input_event = {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {"source": IncrementalSource.INPUT, "text": "user input", "id": 10},
        }
        assert is_low_signal(input_event) is False

    def test_event_missing_data_field(self):
        """Test handling of events missing the data field."""
        event_no_data = {"type": EventType.INCREMENTAL_SNAPSHOT, "timestamp": 1000}
        assert is_low_signal(event_no_data) is False

    def test_event_missing_source_field(self):
        """Test handling of events missing the source field in data."""
        event_no_source = {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {},
        }
        assert is_low_signal(event_no_source) is False
