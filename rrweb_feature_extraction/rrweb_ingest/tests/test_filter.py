"""
Unit tests for the noise filtering module.

Tests the is_low_signal and clean_chunk functions to ensure proper identification
and removal of low-signal events and duplicates from rrweb chunks.
"""

from rrweb_ingest.filter import is_low_signal, clean_chunk


class TestIsLowSignal:
    """Test cases for the is_low_signal function."""

    def test_mousemove_events_are_noise(self):
        """Test that mousemove events (source == 1) are identified as noise."""
        mousemove_event = {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 1, "positions": [{"x": 100, "y": 200}]},
        }

        assert is_low_signal(mousemove_event) is True

    def test_non_incremental_events_not_filtered(self):
        """Test that non-IncrementalSnapshot events are never filtered."""
        # FullSnapshot event
        snapshot_event = {"type": 2, "timestamp": 1000, "data": {"source": 1}}
        assert is_low_signal(snapshot_event) is False

        # Meta event
        meta_event = {"type": 0, "timestamp": 1000, "data": {"source": 1}}
        assert is_low_signal(meta_event) is False

    def test_micro_scroll_below_threshold(self):
        """Test that scrolls below threshold are identified as noise."""
        micro_scroll_event = {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 3, "x": 5, "y": 10},  # Both below default 20px threshold
        }

        assert is_low_signal(micro_scroll_event) is True

    def test_micro_scroll_with_custom_threshold(self):
        """Test micro-scroll detection with custom threshold."""
        scroll_event = {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 3, "x": 15, "y": 10},
        }

        # With default threshold (20), this should be noise
        assert is_low_signal(scroll_event) is True

        # With lower threshold (10), this should not be noise
        assert is_low_signal(scroll_event, micro_scroll_threshold=10) is False

    def test_significant_scroll_above_threshold(self):
        """Test that scrolls above threshold are not identified as noise."""
        significant_scroll_event = {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 3, "x": 50, "y": 100},  # Above 20px threshold
        }

        assert is_low_signal(significant_scroll_event) is False

    def test_scroll_with_only_x_delta(self):
        """Test scroll detection when only x delta is present."""
        x_scroll_event = {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 3, "x": 50},  # No y value
        }

        assert is_low_signal(x_scroll_event) is False

    def test_scroll_with_only_y_delta(self):
        """Test scroll detection when only y delta is present."""
        y_scroll_event = {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 3, "y": 50},  # No x value
        }

        assert is_low_signal(y_scroll_event) is False

    def test_trivial_dom_mutation_empty(self):
        """Test that DOM mutations with no changes are identified as noise."""
        empty_mutation_event = {
            "type": 3,
            "timestamp": 1000,
            "data": {
                "source": 0,
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
            "type": 3,
            "timestamp": 1000,
            "data": {
                "source": 0,
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
            "type": 3,
            "timestamp": 1000,
            "data": {
                "source": 0,
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
            "type": 3,
            "timestamp": 1000,
            "data": {
                "source": 0,
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
            "type": 3,
            "timestamp": 1000,
            "data": {
                "source": 0,
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
            "type": 3,
            "timestamp": 1000,
            "data": {
                "source": 0,
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
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 2, "type": 0, "id": 5},
        }
        assert is_low_signal(click_event) is False

        # Input event (source == 5)
        input_event = {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 5, "text": "user input", "id": 10},
        }
        assert is_low_signal(input_event) is False

    def test_event_missing_data_field(self):
        """Test handling of events missing the data field."""
        event_no_data = {"type": 3, "timestamp": 1000}
        assert is_low_signal(event_no_data) is False

    def test_event_missing_source_field(self):
        """Test handling of events missing the source field in data."""
        event_no_source = {"type": 3, "timestamp": 1000, "data": {}}
        assert is_low_signal(event_no_source) is False


class TestCleanChunk:
    """Test cases for the clean_chunk function."""

    def test_empty_chunk(self):
        """Test that empty chunk returns empty list."""
        result = clean_chunk([])
        assert not result

    def test_removes_mousemove_noise(self):
        """Test that mousemove events are removed from chunks."""
        events = [
            {"type": 3, "timestamp": 1000, "data": {"source": 1}},  # mousemove (noise)
            {"type": 3, "timestamp": 2000, "data": {"source": 2, "id": 5}},  # click
            {"type": 3, "timestamp": 3000, "data": {"source": 1}},  # mousemove (noise)
        ]

        result = clean_chunk(events)

        assert len(result) == 1
        assert result[0]["data"]["source"] == 2  # Only click event remains

    def test_removes_micro_scroll_noise(self):
        """Test that micro-scroll events are removed from chunks."""
        events = [
            {
                "type": 3,
                "timestamp": 1000,
                "data": {"source": 3, "x": 5, "y": 10},
            },  # micro-scroll
            {"type": 3, "timestamp": 2000, "data": {"source": 2, "id": 5}},  # click
            {
                "type": 3,
                "timestamp": 3000,
                "data": {"source": 3, "x": 50, "y": 100},
            },  # significant scroll
        ]

        result = clean_chunk(events)

        assert len(result) == 2
        assert result[0]["data"]["source"] == 2  # click
        assert result[1]["data"]["source"] == 3  # significant scroll
        assert result[1]["data"]["x"] == 50  # verify it's the right scroll event

    def test_removes_duplicate_events(self):
        """Test that duplicate events are collapsed to one."""
        events = [
            {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 5}},  # click
            {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 5}},  # duplicate
            {
                "type": 3,
                "timestamp": 2000,
                "data": {"source": 2, "id": 10},
            },  # different click
        ]

        result = clean_chunk(events)

        assert len(result) == 2
        assert result[0]["timestamp"] == 1000
        assert result[0]["data"]["id"] == 5
        assert result[1]["timestamp"] == 2000
        assert result[1]["data"]["id"] == 10

    def test_preserves_event_order(self):
        """Test that non-noise, unique events are preserved in original order."""
        events = [
            {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 5}},  # click 1
            {"type": 3, "timestamp": 1500, "data": {"source": 1}},  # mousemove (noise)
            {"type": 3, "timestamp": 2000, "data": {"source": 2, "id": 10}},  # click 2
            {"type": 3, "timestamp": 3000, "data": {"source": 5, "id": 15}},  # input
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
            {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 5}},
            {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 10}},
            # Same everything including target id - should deduplicate
            {"type": 3, "timestamp": 2000, "data": {"source": 2, "id": 5}},
            {"type": 3, "timestamp": 2000, "data": {"source": 2, "id": 5}},
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
                "type": 3,
                "timestamp": 1000,
                "data": {"source": 3, "x": 50},
            },  # scroll without id
            {"type": 3, "timestamp": 1000, "data": {"source": 3, "x": 50}},  # duplicate
            {
                "type": 3,
                "timestamp": 2000,
                "data": {"source": 3, "x": 100},
            },  # different scroll
        ]

        result = clean_chunk(events)

        assert len(result) == 2
        assert result[0]["data"]["x"] == 50
        assert result[1]["data"]["x"] == 100

    def test_preserves_non_incremental_events(self):
        """Test that non-IncrementalSnapshot events are preserved."""
        events = [
            {"type": 2, "timestamp": 1000, "data": {"source": 0}},  # FullSnapshot
            {"type": 3, "timestamp": 1500, "data": {"source": 1}},  # mousemove (noise)
            {"type": 0, "timestamp": 2000, "data": {"source": 0}},  # Meta event
            {"type": 3, "timestamp": 2500, "data": {"source": 2, "id": 5}},  # click
        ]

        result = clean_chunk(events)

        assert len(result) == 3
        assert result[0]["type"] == 2  # FullSnapshot preserved
        assert result[1]["type"] == 0  # Meta event preserved
        assert result[2]["type"] == 3  # Click preserved
        assert result[2]["data"]["source"] == 2  # Mousemove filtered out

    def test_complex_filtering_scenario(self):
        """Test a complex scenario with multiple types of noise and duplicates."""
        events = [
            {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 5}},  # click
            {"type": 3, "timestamp": 1100, "data": {"source": 1}},  # mousemove (noise)
            {
                "type": 3,
                "timestamp": 1200,
                "data": {"source": 3, "x": 5, "y": 5},
            },  # micro-scroll (noise)
            {
                "type": 3,
                "timestamp": 1000,
                "data": {"source": 2, "id": 5},
            },  # duplicate click
            {
                "type": 3,
                "timestamp": 1300,
                "data": {
                    "source": 0,
                    "adds": [],
                    "removes": [],
                    "texts": [],
                    "attributes": [],
                },
            },  # trivial mutation (noise)
            {
                "type": 3,
                "timestamp": 1400,
                "data": {"source": 3, "x": 50, "y": 100},
            },  # significant scroll
            {
                "type": 3,
                "timestamp": 1500,
                "data": {"source": 5, "id": 10, "text": "input"},
            },  # input
        ]

        result = clean_chunk(events)

        # Should keep: click (deduplicated), significant scroll, input
        assert len(result) == 3
        assert result[0]["data"]["source"] == 2  # click
        assert result[1]["data"]["source"] == 3  # significant scroll
        assert result[2]["data"]["source"] == 5  # input
