"""
Unit tests for scroll-pattern detection.

Tests the detection of scroll events followed by DOM mutations within
specified time windows, verifying correct pattern matching and timing.
"""

import pytest

from feature_extraction.scroll_patterns import detect_scroll_patterns


@pytest.fixture(name="scroll_with_mutation_outside_window")
def fixture_scroll_with_mutation_outside_window():
    """Fixture providing a scroll event with mutation outside the time window."""
    return [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 3, "id": 100, "x": 0, "y": 500},
        },  # Scroll
        {
            "type": 3,
            "timestamp": 4000,  # 3000ms later (outside 2000ms window)
            "data": {"source": 0, "adds": [{"node": {"id": 200}}]},
        },  # Mutation
    ]


@pytest.fixture(name="scroll_with_no_mutation")
def fixture_scroll_with_no_mutation():
    """Fixture providing a scroll event with no subsequent mutation."""
    return [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 3, "id": 100, "x": 0, "y": 500},
        },  # Scroll
        {
            "type": 3,
            "timestamp": 1500,
            "data": {"source": 1, "x": 200, "y": 300},
        },  # Mouse move
        {
            "type": 3,
            "timestamp": 2000,
            "data": {"source": 2, "id": 150},
        },  # Click
    ]


@pytest.fixture(name="out_of_order_events")
def fixture_out_of_order_events():
    """Fixture providing events with timestamps out of chronological order."""
    return [
        {
            "type": 3,
            "timestamp": 2000,
            "data": {"source": 3, "id": 100, "x": 0, "y": 500},
        },  # Scroll (later timestamp)
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 0, "adds": [{"node": {"id": 200}}]},
        },  # Mutation (earlier timestamp)
        {
            "type": 3,
            "timestamp": 2200,  # 200ms after scroll
            "data": {"source": 0, "texts": [{"id": 201, "value": "text"}]},
        },  # Another mutation
    ]


@pytest.fixture(name="non_scroll_mutation_events")
def fixture_non_scroll_mutation_events():
    """Fixture providing events that are not scroll or mutation events."""
    return [
        # FullSnapshot event
        {"type": 2, "timestamp": 1000, "data": {"node": {}}},
        # Mouse move event
        {"type": 3, "timestamp": 1100, "data": {"source": 1, "x": 100, "y": 200}},
        # Click event
        {"type": 3, "timestamp": 1200, "data": {"source": 2, "id": 42}},
        # Input event
        {"type": 3, "timestamp": 1300, "data": {"source": 5, "text": "input"}},
        # Meta event
        {"type": 4, "timestamp": 1400, "data": {"width": 1920, "height": 1080}},
    ]


def test_scroll_with_mutation_outside_window_yields_no_pattern(
    scroll_with_mutation_outside_window,
):
    """Test that a scroll event with next mutation outside time window yields no pattern."""
    patterns = detect_scroll_patterns(scroll_with_mutation_outside_window)

    # Should have no patterns (3000ms > 2000ms window)
    assert len(patterns) == 0


def test_scroll_with_no_subsequent_mutation_yields_no_pattern(scroll_with_no_mutation):
    """Test that a scroll event with no subsequent mutation yields no pattern."""
    patterns = detect_scroll_patterns(scroll_with_no_mutation)

    # Should have no patterns (no mutations)
    assert len(patterns) == 0


def test_out_of_order_events_handled_correctly(out_of_order_events):
    """Test that events out of order or non-scroll/mutation sources are ignored."""
    patterns = detect_scroll_patterns(out_of_order_events)

    # Should find one pattern: scroll at 2000 -> mutation at 2200
    assert len(patterns) == 1

    pattern = patterns[0]
    assert pattern.scroll_event["timestamp"] == 2000
    assert pattern.mutation_event["timestamp"] == 2200
    assert pattern.delay_ms == 200

    # The mutation at 1000 should be ignored (before scroll)


def test_non_scroll_mutation_sources_ignored(non_scroll_mutation_events):
    """Test that events that are not scroll or mutation events are ignored."""
    patterns = detect_scroll_patterns(non_scroll_mutation_events)

    # Should have no patterns (no scroll or mutation events)
    assert len(patterns) == 0


def test_empty_event_list_returns_empty_list():
    """Test that passing an empty event list returns an empty list."""
    patterns = detect_scroll_patterns([])
    assert len(patterns) == 0


def test_scroll_matches_first_mutation_only():
    """Test that each scroll matches at most one mutation (the first within window)."""
    events = [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 3, "id": 100, "x": 0, "y": 500},
        },  # Scroll
        {
            "type": 3,
            "timestamp": 1200,  # 200ms later
            "data": {"source": 0, "adds": [{"node": {"id": 200}}]},
        },  # First mutation
        {
            "type": 3,
            "timestamp": 1400,  # 400ms later
            "data": {"source": 0, "texts": [{"id": 201, "value": "text"}]},
        },  # Second mutation
    ]

    patterns = detect_scroll_patterns(events)

    # Should only match the first mutation
    assert len(patterns) == 1
    pattern = patterns[0]
    assert pattern.scroll_event["timestamp"] == 1000
    assert pattern.mutation_event["timestamp"] == 1200  # First mutation, not 1400
    assert pattern.delay_ms == 200


def test_patterns_returned_in_chronological_order():
    """Test that ScrollPattern records are returned in chronological order by scroll timestamp."""
    events = [
        {
            "type": 3,
            "timestamp": 2000,
            "data": {"source": 3, "id": 101, "x": 0, "y": 1000},
        },  # Second scroll
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 3, "id": 100, "x": 0, "y": 500},
        },  # First scroll
        {
            "type": 3,
            "timestamp": 1200,  # 200ms after first scroll
            "data": {"source": 0, "adds": [{"node": {"id": 200}}]},
        },  # Mutation for first scroll
        {
            "type": 3,
            "timestamp": 2300,  # 300ms after second scroll
            "data": {"source": 0, "texts": [{"id": 201, "value": "text"}]},
        },  # Mutation for second scroll
    ]

    patterns = detect_scroll_patterns(events)

    assert len(patterns) == 2

    # Should be ordered by scroll timestamp (1000, then 2000)
    assert patterns[0].scroll_event["timestamp"] == 1000
    assert patterns[1].scroll_event["timestamp"] == 2000


def test_mutation_before_scroll_ignored():
    """Test that mutations occurring before scroll events are not matched."""
    events = [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 0, "adds": [{"node": {"id": 200}}]},
        },  # Mutation first
        {
            "type": 3,
            "timestamp": 1500,
            "data": {"source": 3, "id": 100, "x": 0, "y": 500},
        },  # Scroll after
    ]

    patterns = detect_scroll_patterns(events)

    # Should have no patterns (mutation before scroll)
    assert len(patterns) == 0


def test_missing_timestamps_default_to_zero():
    """Test that events with missing timestamps are handled gracefully."""
    events = [
        {
            "type": 3,
            "data": {"source": 3, "id": 100, "x": 0, "y": 500},
        },  # Scroll with missing timestamp
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 0, "adds": [{"node": {"id": 200}}]},
        },  # Mutation with timestamp
    ]

    patterns = detect_scroll_patterns(events)

    # Should find pattern (0 -> 1000, delay = 1000ms)
    assert len(patterns) == 1
    pattern = patterns[0]
    assert pattern.delay_ms == 1000


def test_scroll_and_mutation_event_data_preserved():
    """Test that the original scroll and mutation event data is preserved in patterns."""
    events = [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {
                "source": 3,
                "id": 100,
                "x": 0,
                "y": 500,
                "custom_field": "scroll_data",
            },
        },
        {
            "type": 3,
            "timestamp": 1200,
            "data": {
                "source": 0,
                "adds": [{"node": {"id": 200, "tagName": "div"}}],
                "custom_field": "mutation_data",
            },
        },
    ]

    patterns = detect_scroll_patterns(events)

    assert len(patterns) == 1
    pattern = patterns[0]

    # Verify original event data is preserved
    assert pattern.scroll_event["data"]["custom_field"] == "scroll_data"
    assert pattern.mutation_event["data"]["custom_field"] == "mutation_data"
    assert pattern.scroll_event["data"]["x"] == 0
    assert pattern.scroll_event["data"]["y"] == 500
    assert pattern.mutation_event["data"]["adds"][0]["node"]["tagName"] == "div"
