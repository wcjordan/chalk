"""
Unit tests for the noise filtering module.

Tests the is_low_signal and clean_chunk functions to ensure proper identification
and removal of low-signal events and duplicates from rrweb chunks.
"""

# pylint: disable=duplicate-code

from unittest.mock import patch

from rrweb_ingest.filter import is_low_signal, clean_chunk
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

    def test_micro_scroll_below_threshold(self):
        """Test that scrolls below threshold are identified as noise."""
        micro_scroll_event = {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {
                "source": IncrementalSource.SCROLL,
                "x": 5,
                "y": 10,
            },  # Both below default 20px threshold
        }

        assert is_low_signal(micro_scroll_event) is True

    def test_micro_scroll_with_custom_threshold(self):
        """Test micro-scroll detection with custom threshold."""
        scroll_event = {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {"source": IncrementalSource.SCROLL, "x": 15, "y": 10},
        }

        # With default threshold (20), this should be noise
        assert is_low_signal(scroll_event) is True

        # With lower threshold (10), this should not be noise
        with patch("rrweb_ingest.filter.config.MICRO_SCROLL_THRESHOLD", 10):
            assert is_low_signal(scroll_event) is False

    def test_significant_scroll_above_threshold(self):
        """Test that scrolls above threshold are not identified as noise."""
        significant_scroll_event = {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {
                "source": IncrementalSource.SCROLL,
                "x": 50,
                "y": 100,
            },  # Above 20px threshold
        }

        assert is_low_signal(significant_scroll_event) is False

    def test_scroll_with_only_x_delta(self):
        """Test scroll detection when only x delta is present."""
        x_scroll_event = {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {"source": IncrementalSource.SCROLL, "x": 50},  # No y value
        }

        assert is_low_signal(x_scroll_event) is False

    def test_scroll_with_only_y_delta(self):
        """Test scroll detection when only y delta is present."""
        y_scroll_event = {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {"source": IncrementalSource.SCROLL, "y": 50},  # No x value
        }

        assert is_low_signal(y_scroll_event) is False

    def test_trivial_dom_mutation_empty(self):
        """Test that DOM mutations with no changes are identified as noise."""
        empty_mutation_event = {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {
                "source": IncrementalSource.MUTATION,
                "adds": [],
                "removes": [],
                "texts": [],
                "attributes": [],
            },
        }

        assert is_low_signal(empty_mutation_event) is True

    def test_trivial_dom_mutation_style_only(self):
        """Test that single style attribute changes are identified as noise."""
        style_mutation_event = {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {
                "source": IncrementalSource.MUTATION,
                "adds": [],
                "removes": [],
                "texts": [],
                "attributes": [{"attributes": {"style": "color: red;"}}],
            },
        }

        assert is_low_signal(style_mutation_event) is True

    def test_significant_dom_mutation_with_adds(self):
        """Test that DOM mutations with element additions are not noise."""
        add_mutation_event = {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {
                "source": IncrementalSource.MUTATION,
                "adds": [{"parentId": 1, "nextId": None, "node": {"tagName": "div"}}],
                "removes": [],
                "texts": [],
                "attributes": [],
            },
        }

        assert is_low_signal(add_mutation_event) is False

    def test_significant_dom_mutation_with_removes(self):
        """Test that DOM mutations with element removals are not noise."""
        remove_mutation_event = {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {
                "source": IncrementalSource.MUTATION,
                "adds": [],
                "removes": [{"parentId": 1, "id": 5}],
                "texts": [],
                "attributes": [],
            },
        }

        assert is_low_signal(remove_mutation_event) is False

    def test_significant_dom_mutation_with_text_changes(self):
        """Test that DOM mutations with text changes are not noise."""
        text_mutation_event = {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {
                "source": IncrementalSource.MUTATION,
                "adds": [],
                "removes": [],
                "texts": [{"id": 5, "value": "New text content"}],
                "attributes": [],
            },
        }

        assert is_low_signal(text_mutation_event) is False

    def test_significant_dom_mutation_multiple_attributes(self):
        """Test that DOM mutations with multiple attribute changes are not noise."""
        multi_attr_mutation_event = {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {
                "source": IncrementalSource.MUTATION,
                "adds": [],
                "removes": [],
                "texts": [],
                "attributes": [
                    {"attributes": {"class": "active"}},
                    {"attributes": {"data-id": "123"}},
                ],
            },
        }

        assert is_low_signal(multi_attr_mutation_event) is False

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


class TestCleanChunk:
    """Test cases for the clean_chunk function."""

    def test_empty_chunk(self):
        """Test that empty chunk returns empty list."""
        result = clean_chunk([])
        assert not result

    def test_preserves_event_order(self):
        """Test that non-noise, unique events are preserved in original order."""
        events = [
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1000,
                "data": {"source": IncrementalSource.MOUSE_INTERACTION, "id": 5},
            },  # click 1
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1500,
                "data": {"source": IncrementalSource.MOUSE_MOVE},
            },  # mousemove (noise)
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 2000,
                "data": {"source": IncrementalSource.MOUSE_INTERACTION, "id": 10},
            },  # click 2
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 3000,
                "data": {"source": IncrementalSource.INPUT, "id": 15},
            },  # input
        ]

        result = clean_chunk(events)

        assert len(result) == 3
        assert result[0]["timestamp"] == 1000  # click 1
        assert result[1]["timestamp"] == 2000  # click 2
        assert result[2]["timestamp"] == 3000  # input

    def test_deduplication_signature_components(self):
        """Test that deduplication uses correct signature components."""
        events = [
            # Same type, source, timestamp, but different target id - should keep both
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1000,
                "data": {"source": IncrementalSource.MOUSE_INTERACTION, "id": 5},
            },
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1000,
                "data": {"source": IncrementalSource.MOUSE_INTERACTION, "id": 10},
            },
            # Same everything including target id - should deduplicate
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 2000,
                "data": {"source": IncrementalSource.MOUSE_INTERACTION, "id": 5},
            },
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 2000,
                "data": {"source": IncrementalSource.MOUSE_INTERACTION, "id": 5},
            },
        ]

        result = clean_chunk(events)

        assert len(result) == 3
        # First two events should be kept (different target ids)
        assert result[0]["data"]["id"] == 5
        assert result[1]["data"]["id"] == 10
        # Third event should be kept, fourth should be deduplicated
        assert result[2]["data"]["id"] == 5

    def test_handles_events_without_target_id(self):
        """Test deduplication works for events without target id."""
        events = [
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1000,
                "data": {"source": IncrementalSource.SCROLL, "x": 50},
            },  # scroll without id
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1000,
                "data": {"source": IncrementalSource.SCROLL, "x": 50},
            },  # duplicate
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 2000,
                "data": {"source": IncrementalSource.SCROLL, "x": 100},
            },  # different scroll
        ]

        result = clean_chunk(events)

        assert len(result) == 2
        assert result[0]["data"]["x"] == 50
        assert result[1]["data"]["x"] == 100

    def test_complex_filtering_scenario(self):
        """Test a complex scenario with multiple types of noise and duplicates."""
        events = [
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1000,
                "data": {"source": IncrementalSource.MOUSE_INTERACTION, "id": 5},
            },  # click
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1100,
                "data": {"source": IncrementalSource.MOUSE_MOVE},
            },  # mousemove (noise)
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1200,
                "data": {"source": IncrementalSource.SCROLL, "x": 5, "y": 5},
            },  # micro-scroll (noise)
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1000,
                "data": {"source": IncrementalSource.MOUSE_INTERACTION, "id": 5},
            },  # duplicate click
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1300,
                "data": {
                    "source": IncrementalSource.MUTATION,
                    "adds": [],
                    "removes": [],
                    "texts": [],
                    "attributes": [],
                },
            },  # trivial mutation (noise)
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1400,
                "data": {"source": IncrementalSource.SCROLL, "x": 50, "y": 100},
            },  # significant scroll
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1500,
                "data": {"source": IncrementalSource.INPUT, "id": 10, "text": "input"},
            },  # input
        ]

        result = clean_chunk(events)

        # Should keep: click (deduplicated), significant scroll, input
        assert len(result) == 3
        assert (
            result[0]["data"]["source"] == IncrementalSource.MOUSE_INTERACTION
        )  # click
        assert (
            result[1]["data"]["source"] == IncrementalSource.SCROLL
        )  # significant scroll
        assert result[2]["data"]["source"] == IncrementalSource.INPUT  # input

    def test_custom_filters_applied(self):
        """Test that custom filter functions are properly applied."""
        events = [
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1000,
                "data": {"source": IncrementalSource.MOUSE_INTERACTION, "id": 5},
            },  # click
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1100,
                "data": {"source": 99, "id": 10},
            },  # custom source
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1200,
                "data": {"source": IncrementalSource.INPUT, "text": "input"},
            },  # input
        ]

        # Custom filter that removes events with source == 99
        def filter_source_99(event):
            return event.get("data", {}).get("source") == 99

        with patch(
            "rrweb_ingest.filter.config.DEFAULT_CUSTOM_FILTERS", [filter_source_99]
        ):
            result = clean_chunk(events)

        # Should keep click and input, filter out source 99
        assert len(result) == 2
        assert (
            result[0]["data"]["source"] == IncrementalSource.MOUSE_INTERACTION
        )  # click
        assert result[1]["data"]["source"] == IncrementalSource.INPUT  # input

    def test_multiple_custom_filters(self):
        """Test that multiple custom filters work together."""
        events = [
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1000,
                "data": {"source": IncrementalSource.MOUSE_INTERACTION, "id": 5},
            },  # click
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1100,
                "data": {"source": 99, "id": 10},
            },  # custom source 99
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1200,
                "data": {"source": 88, "id": 15},
            },  # custom source 88
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "timestamp": 1300,
                "data": {"source": IncrementalSource.INPUT, "text": "input"},
            },  # input
        ]

        # Custom filters
        def filter_source_99(event):
            return event.get("data", {}).get("source") == 99

        def filter_source_88(event):
            return event.get("data", {}).get("source") == 88

        with patch(
            "rrweb_ingest.filter.config.DEFAULT_CUSTOM_FILTERS",
            [filter_source_99, filter_source_88],
        ):
            result = clean_chunk(events)

        # Should keep only click and input
        assert len(result) == 2
        assert (
            result[0]["data"]["source"] == IncrementalSource.MOUSE_INTERACTION
        )  # click
        assert result[1]["data"]["source"] == IncrementalSource.INPUT  # input
