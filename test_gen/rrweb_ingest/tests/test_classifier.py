"""
Unit tests for the event classifier module.

Tests the classify_events function to ensure proper categorization of rrweb events
into snapshots, interactions, and others based on event type.
"""

import pytest
from rrweb_ingest.classifier import classify_events
from rrweb_util import EventType


def test_classify_empty_event_list():
    """Test that an empty event list returns three empty lists."""
    snapshots, interactions, others = classify_events([])

    assert not snapshots
    assert not interactions
    assert not others


def test_classify_missing_type_field():
    """Test that events missing the 'type' field raise KeyError."""
    events_missing_type = [
        {"timestamp": 1000, "data": {"source": "no_type"}},
        {"type": 2, "timestamp": 2000, "data": {"source": "has_type"}},
    ]

    with pytest.raises(KeyError):
        classify_events(events_missing_type)


def test_classify_unexpected_type_values():
    """Test that events with unexpected type values are placed in 'others'."""
    events_with_unusual_types = [
        {"type": 99, "timestamp": 1000, "data": {}},
        {"type": -1, "timestamp": 2000, "data": {}},
        {"type": "string", "timestamp": 3000, "data": {}},
    ]

    snapshots, interactions, others = classify_events(events_with_unusual_types)

    assert len(snapshots) == 0
    assert len(interactions) == 0
    assert len(others) == 3
    assert others[0]["type"] == 99
    assert others[1]["type"] == -1
    assert others[2]["type"] == "string"


def test_classify_preserves_event_order():
    """Test that events maintain their relative order within each category."""
    events = [
        {"type": 2, "timestamp": 1000, "data": {"id": "snap1"}},
        {"type": 3, "timestamp": 2000, "data": {"id": "int1"}},
        {"type": 2, "timestamp": 3000, "data": {"id": "snap2"}},
        {"type": 3, "timestamp": 4000, "data": {"id": "int2"}},
        {"type": 0, "timestamp": 5000, "data": {"id": "other1"}},
    ]

    snapshots, interactions, others = classify_events(events)

    # Verify order is preserved within each category
    assert snapshots[0]["data"]["id"] == "snap1"
    assert snapshots[1]["data"]["id"] == "snap2"
    assert interactions[0]["data"]["id"] == "int1"
    assert interactions[1]["data"]["id"] == "int2"
    assert others[0]["data"]["id"] == "other1"
