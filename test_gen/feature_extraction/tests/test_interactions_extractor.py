"""
Unit tests for user interaction extraction.

Tests the extraction of structured UserInteraction records from rrweb events,
covering click, input, and scroll interactions with proper field mapping.
"""

# pylint: disable=duplicate-code

import pytest
from feature_extraction.extractors import extract_user_interactions
from rrweb_util import EventType, IncrementalSource


@pytest.fixture(name="non_interaction_events")
def fixture_non_interaction_events():
    """Fixture providing events that are not user interactions."""
    return [
        # FullSnapshot event
        {"type": EventType.FULL_SNAPSHOT, "timestamp": 1000, "data": {"node": {}}},
        # Mouse move event (source 1)
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 2000,
            "data": {"source": IncrementalSource.MOUSE_MOVE, "x": 100, "y": 200},
        },
        # DOM mutation event (source 0)
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 3000,
            "data": {"source": IncrementalSource.MUTATION, "adds": []},
        },
        # Unknown source
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 4000,
            "data": {"source": 99, "id": 123},
        },
        # Meta event
        {
            "type": EventType.CUSTOM,
            "timestamp": 5000,
            "data": {"width": 1920, "height": 1080},
        },
    ]


def test_extract_non_interaction_sources_ignored(non_interaction_events):
    """Test that non-interaction sources are ignored."""
    interactions = extract_user_interactions(non_interaction_events)

    # Should produce no interactions
    assert len(interactions) == 0


def test_extract_preserves_event_order():
    """Test that the returned list preserves the original event order."""
    # Create events with different timestamps in a specific order
    events = [
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {"source": IncrementalSource.SCROLL, "id": 1, "x": 0, "y": 100},
        },  # scroll
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 2000,
            "data": {
                "source": IncrementalSource.MOUSE_INTERACTION,
                "id": 2,
                "x": 50,
                "y": 60,
            },
        },  # click
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 3000,
            "data": {"source": IncrementalSource.INPUT, "id": 3, "text": "input"},
        },  # input
    ]

    interactions = extract_user_interactions(events)

    # Should preserve order: scroll, click, input
    assert len(interactions) == 3
    assert interactions[0].action == "scroll"
    assert interactions[0].timestamp == 1000
    assert interactions[1].action == "click"
    assert interactions[1].timestamp == 2000
    assert interactions[2].action == "input"
    assert interactions[2].timestamp == 3000


def test_extract_handles_missing_target_ids():
    """Test that interaction events without target IDs are safely ignored."""
    events_with_missing_ids = [
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {
                "source": IncrementalSource.MOUSE_INTERACTION,
                "x": 100,
                "y": 200,
            },  # Missing id
        },
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 2000,
            "data": {
                "source": IncrementalSource.MOUSE_INTERACTION,
                "id": 42,
                "x": 150,
                "y": 250,
            },  # Valid
        },
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 3000,
            "data": {"source": IncrementalSource.INPUT, "text": "no id"},  # Missing id
        },
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 4000,
            "data": {
                "source": IncrementalSource.INPUT,
                "id": 43,
                "text": "valid",
            },  # Valid
        },
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 5000,
            "data": {
                "source": IncrementalSource.SCROLL,
                "x": 0,
                "y": 100,
            },  # Missing id
        },
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 6000,
            "data": {
                "source": IncrementalSource.SCROLL,
                "id": 44,
                "x": 0,
                "y": 200,
            },  # Valid
        },
    ]

    interactions = extract_user_interactions(events_with_missing_ids)

    # Should only extract interactions with valid target IDs
    assert len(interactions) == 3

    # Verify all extracted interactions have valid target IDs
    target_ids = [i.target_id for i in interactions]
    assert 42 in target_ids  # Valid click
    assert 43 in target_ids  # Valid input
    assert 44 in target_ids  # Valid scroll


def test_extract_handles_missing_coordinates():
    """Test that click and scroll events handle missing x/y coordinates gracefully."""
    events_with_missing_coords = [
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {
                "source": IncrementalSource.MOUSE_INTERACTION,
                "id": 42,
            },  # Missing x, y
        },
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 2000,
            "data": {
                "source": IncrementalSource.SCROLL,
                "id": 43,
                "x": 100,
            },  # Missing y
        },
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 3000,
            "data": {
                "source": IncrementalSource.SCROLL,
                "id": 44,
                "y": 200,
            },  # Missing x
        },
    ]

    interactions = extract_user_interactions(events_with_missing_coords)

    assert len(interactions) == 3

    # Click with missing coordinates should default to 0
    click = interactions[0]
    assert click.action == "click"
    assert click.value["x"] == 0
    assert click.value["y"] == 0

    # Scroll with missing y should default to 0
    scroll1 = interactions[1]
    assert scroll1.action == "scroll"
    assert scroll1.value["x"] == 100
    assert scroll1.value["y"] == 0

    # Scroll with missing x should default to 0
    scroll2 = interactions[2]
    assert scroll2.action == "scroll"
    assert scroll2.value["x"] == 0
    assert scroll2.value["y"] == 200


def test_extract_handles_empty_input_data():
    """Test that input events with no text or checked data produce empty value dict."""
    events_with_empty_input = [
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {
                "source": IncrementalSource.INPUT,
                "id": 42,
            },  # No text or isChecked
        }
    ]

    interactions = extract_user_interactions(events_with_empty_input)

    assert len(interactions) == 1
    input_interaction = interactions[0]
    assert input_interaction.action == "input"
    assert input_interaction.target_id == 42
    assert input_interaction.value == {}
