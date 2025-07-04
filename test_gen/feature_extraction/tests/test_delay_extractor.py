"""
Unit tests for delay computation functions.

Tests the computation of inter-event delays and reaction delays between
user interactions and DOM mutations with proper timing validation.
"""

from unittest.mock import patch

import pytest

from feature_extraction.extractors import (
    compute_inter_event_delays,
    compute_reaction_delays,
)


@pytest.fixture(name="simple_events")
def fixture_simple_events():
    """Fixture providing events with known timestamps for delay testing."""
    return [
        {"type": 3, "timestamp": 1000, "data": {"source": 2}},  # Click
        {"type": 3, "timestamp": 1500, "data": {"source": 0}},  # Mutation
        {"type": 3, "timestamp": 3000, "data": {"source": 1}},  # Mouse move
    ]


@pytest.fixture(name="reaction_events_within_window")
def fixture_reaction_events_within_window():
    """Fixture providing click and mutation events within reaction window."""
    return [
        {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 42}},  # Click
        {
            "type": 3,
            "timestamp": 1800,
            "data": {"source": 0, "adds": []},
        },  # Mutation (800ms later)
        {"type": 3, "timestamp": 2000, "data": {"source": 1, "x": 100}},  # Mouse move
    ]


@pytest.fixture(name="reaction_events_outside_window")
def fixture_reaction_events_outside_window():
    """Fixture providing click and mutation events outside reaction window."""
    return [
        {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 42}},  # Click
        {
            "type": 3,
            "timestamp": 12000,
            "data": {"source": 0, "adds": []},
        },  # Mutation (11000ms later)
    ]


@pytest.fixture(name="multiple_interactions")
def fixture_multiple_interactions():
    """Fixture providing multiple interactions with corresponding mutations."""
    return [
        {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 10}},  # Click 1
        {
            "type": 3,
            "timestamp": 1100,
            "data": {"source": 0, "adds": []},
        },  # Mutation 1 (100ms later)
        {"type": 3, "timestamp": 2000, "data": {"source": 2, "id": 20}},  # Click 2
        {
            "type": 3,
            "timestamp": 2500,
            "data": {"source": 0, "texts": []},
        },  # Mutation 2 (500ms later)
        {"type": 3, "timestamp": 3000, "data": {"source": 1, "x": 50}},  # Mouse move
    ]


@pytest.fixture(name="mixed_source_events")
def fixture_mixed_source_events():
    """Fixture providing events with various sources to test filtering."""
    return [
        {"type": 3, "timestamp": 1000, "data": {"source": 1, "x": 100}},  # Mouse move
        {"type": 3, "timestamp": 1100, "data": {"source": 2, "id": 42}},  # Click
        {"type": 3, "timestamp": 1200, "data": {"source": 3, "y": 200}},  # Scroll
        {"type": 3, "timestamp": 1300, "data": {"source": 0, "adds": []}},  # Mutation
        {"type": 3, "timestamp": 1400, "data": {"source": 5, "text": "input"}},  # Input
    ]


def test_compute_inter_event_delays_simple_sequence(simple_events):
    """Test inter-event delays with known timestamps produce correct deltas."""
    delays = compute_inter_event_delays(simple_events)

    # Should have 2 delays for 3 events
    assert len(delays) == 2

    # First delay: 1000 -> 1500 (500ms)
    delay1 = delays[0]
    assert delay1.from_ts == 1000
    assert delay1.to_ts == 1500
    assert delay1.delta_ms == 500

    # Second delay: 1500 -> 3000 (1500ms)
    delay2 = delays[1]
    assert delay2.from_ts == 1500
    assert delay2.to_ts == 3000
    assert delay2.delta_ms == 1500


def test_compute_inter_event_delays_empty_list():
    """Test that empty event list returns empty delays list."""
    delays = compute_inter_event_delays([])
    assert len(delays) == 0


def test_compute_inter_event_delays_single_event():
    """Test that single event returns empty delays list."""
    single_event = [{"type": 3, "timestamp": 1000, "data": {}}]
    delays = compute_inter_event_delays(single_event)
    assert len(delays) == 0


def test_compute_inter_event_delays_preserves_order():
    """Test that delays preserve the original event order."""
    events = [
        {"type": 3, "timestamp": 100, "data": {}},
        {"type": 3, "timestamp": 200, "data": {}},
        {"type": 3, "timestamp": 150, "data": {}},  # Out of order timestamp
        {"type": 3, "timestamp": 300, "data": {}},
    ]

    delays = compute_inter_event_delays(events)

    # Should have 3 delays
    assert len(delays) == 3

    # Delays should follow the event order, not timestamp order
    assert delays[0].from_ts == 100 and delays[0].to_ts == 200  # 100ms
    assert delays[1].from_ts == 200 and delays[1].to_ts == 150  # -50ms (negative delta)
    assert delays[2].from_ts == 150 and delays[2].to_ts == 300  # 150ms


def test_compute_inter_event_delays_missing_timestamps():
    """Test that events with missing timestamps default to 0."""
    events = [
        {"type": 3, "data": {}},  # Missing timestamp
        {"type": 3, "timestamp": 1000, "data": {}},
        {"type": 3, "data": {}},  # Missing timestamp
    ]

    delays = compute_inter_event_delays(events)

    assert len(delays) == 2
    assert delays[0].from_ts == 0
    assert delays[0].to_ts == 1000
    assert delays[0].delta_ms == 1000
    assert delays[1].from_ts == 1000
    assert delays[1].to_ts == 0
    assert delays[1].delta_ms == -1000


def test_compute_reaction_delays_within_window(reaction_events_within_window):
    """Test reaction delays within window are captured correctly."""
    delays = compute_reaction_delays(reaction_events_within_window)

    # Should have 1 reaction delay
    assert len(delays) == 1

    delay = delays[0]
    assert delay.from_ts == 1000  # Click timestamp
    assert delay.to_ts == 1800  # Mutation timestamp
    assert delay.delta_ms == 800  # 800ms reaction time


def test_compute_reaction_delays_outside_window(reaction_events_outside_window):
    """Test no reaction delays are emitted when mutation is outside window."""
    with patch("feature_extraction.config.DEFAULT_MAX_REACTION_MS", 10000):
        delays = compute_reaction_delays(reaction_events_outside_window)

    # Should have no reaction delays (11000ms > 10000ms window)
    assert len(delays) == 0


def test_compute_reaction_delays_multiple_interactions(multiple_interactions):
    """Test multiple interactions produce multiple reaction delays."""
    delays = compute_reaction_delays(multiple_interactions)

    # Should have 2 reaction delays
    assert len(delays) == 2

    # First reaction: Click at 1000 -> Mutation at 1100 (100ms)
    delay1 = delays[0]
    assert delay1.from_ts == 1000
    assert delay1.to_ts == 1100
    assert delay1.delta_ms == 100

    # Second reaction: Click at 2000 -> Mutation at 2500 (500ms)
    delay2 = delays[1]
    assert delay2.from_ts == 2000
    assert delay2.to_ts == 2500
    assert delay2.delta_ms == 500


def test_compute_reaction_delays_custom_sources():
    """Test reaction delays with custom interaction and mutation sources."""
    events = [
        {"type": 3, "timestamp": 1000, "data": {"source": 5, "id": 42}},  # Input event
        {"type": 3, "timestamp": 1200, "data": {"source": 0, "adds": []}},  # Mutation
    ]

    # Use input events (source 5) as interactions
    delays = compute_reaction_delays(events, interaction_source=5, mutation_source=0)

    assert len(delays) == 1
    delay = delays[0]
    assert delay.from_ts == 1000
    assert delay.to_ts == 1200
    assert delay.delta_ms == 200


def test_compute_reaction_delays_custom_max_window():
    """Test reaction delays with custom maximum reaction window."""

    events = [
        {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 42}},  # Click
        {
            "type": 3,
            "timestamp": 1600,
            "data": {"source": 0, "adds": []},
        },  # Mutation (600ms later)
    ]

    # Use smaller window (500ms)
    with patch("feature_extraction.config.DEFAULT_MAX_REACTION_MS", 500):
        delays = compute_reaction_delays(events)
        # Should have no delays (600ms > 500ms window)
        assert len(delays) == 0

    # Use larger window (1000ms)
    with patch("feature_extraction.config.DEFAULT_MAX_REACTION_MS", 1000):
        delays = compute_reaction_delays(events)
        # Should have 1 delay (600ms <= 1000ms window)
        assert len(delays) == 1
        assert delays[0].delta_ms == 600


def test_compute_reaction_delays_ignores_non_interaction_sources(mixed_source_events):
    """Test that only events with specified interaction sources are considered."""
    delays = compute_reaction_delays(
        mixed_source_events,
        interaction_source=2,  # Only clicks
        mutation_source=0,  # DOM mutations
    )

    # Should only find the click at 1100 -> mutation at 1300 (200ms)
    assert len(delays) == 1
    delay = delays[0]
    assert delay.from_ts == 1100  # Click timestamp
    assert delay.to_ts == 1300  # Mutation timestamp
    assert delay.delta_ms == 200


def test_compute_reaction_delays_ignores_non_mutation_sources(mixed_source_events):
    """Test that only events with specified mutation sources are considered."""
    # Add a non-mutation event that could be confused for a mutation
    events_with_fake_mutation = mixed_source_events + [
        {
            "type": 3,
            "timestamp": 1150,
            "data": {"source": 1, "adds": []},
        },  # Mouse move with 'adds'
    ]

    delays = compute_reaction_delays(
        events_with_fake_mutation,
        interaction_source=2,  # Clicks
        mutation_source=0,  # Only DOM mutations (source 0)
    )

    # Should still only find click -> real mutation, not the fake one
    assert len(delays) == 1
    assert delays[0].to_ts == 1300  # Real mutation, not the fake one at 1150


def test_compute_reaction_delays_first_mutation_only():
    """Test that each interaction matches only the first mutation within window."""
    events = [
        {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 42}},  # Click
        {
            "type": 3,
            "timestamp": 1200,
            "data": {"source": 0, "adds": []},
        },  # First mutation
        {
            "type": 3,
            "timestamp": 1400,
            "data": {"source": 0, "texts": []},
        },  # Second mutation
    ]

    delays = compute_reaction_delays(events)

    # Should only match the first mutation
    assert len(delays) == 1
    delay = delays[0]
    assert delay.from_ts == 1000
    assert delay.to_ts == 1200  # First mutation, not 1400
    assert delay.delta_ms == 200


def test_compute_reaction_delays_no_mutations():
    """Test that interactions with no subsequent mutations produce no delays."""
    events = [
        {"type": 3, "timestamp": 1000, "data": {"source": 2, "id": 42}},  # Click
        {"type": 3, "timestamp": 1100, "data": {"source": 1, "x": 100}},  # Mouse move
        {"type": 3, "timestamp": 1200, "data": {"source": 3, "y": 200}},  # Scroll
    ]

    delays = compute_reaction_delays(events)

    # Should have no delays (no mutations)
    assert len(delays) == 0


def test_compute_reaction_delays_mutation_before_interaction():
    """Test that mutations occurring before interactions are not matched."""
    events = [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 0, "adds": []},
        },  # Mutation first
        {"type": 3, "timestamp": 1100, "data": {"source": 2, "id": 42}},  # Click after
    ]

    delays = compute_reaction_delays(events)

    # Should have no delays (mutation before interaction)
    assert len(delays) == 0


def test_compute_reaction_delays_non_incremental_events():
    """Test that non-IncrementalSnapshot events are ignored."""
    events = [
        {
            "type": 2,
            "timestamp": 1000,
            "data": {"source": 2},
        },  # FullSnapshot, not IncrementalSnapshot
        {"type": 3, "timestamp": 1100, "data": {"source": 2, "id": 42}},  # Click
        {
            "type": 4,
            "timestamp": 1200,
            "data": {"source": 0},
        },  # Meta event, not IncrementalSnapshot
        {"type": 3, "timestamp": 1300, "data": {"source": 0, "adds": []}},  # Mutation
    ]

    delays = compute_reaction_delays(events)

    # Should only consider the IncrementalSnapshot events
    assert len(delays) == 1
    delay = delays[0]
    assert delay.from_ts == 1100  # Click
    assert delay.to_ts == 1300  # Mutation
    assert delay.delta_ms == 200
