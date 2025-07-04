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


def test_compute_inter_event_delays_empty_list():
    """Test that empty event list returns empty delays list."""
    delays = compute_inter_event_delays([])
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
