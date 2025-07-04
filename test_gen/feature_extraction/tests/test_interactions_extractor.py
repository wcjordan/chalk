"""
Unit tests for user interaction extraction.

Tests the extraction of structured UserInteraction records from rrweb events,
covering click, input, and scroll interactions with proper field mapping.
"""

import pytest
from feature_extraction.extractors import extract_user_interactions


@pytest.fixture(name="click_events")
def fixture_click_events():
    """Fixture providing click interaction events."""
    return [
        {
            "type": 3,
            "timestamp": 12345,
            "data": {
                "source": 2,
                "id": 42,
                "x": 150,
                "y": 200,
                "type": "click",
            },
        },
        {
            "type": 3,
            "timestamp": 23456,
            "data": {
                "source": 2,
                "id": 84,
                "x": 300,
                "y": 400,
                "type": "dblclick",
            },
        },
    ]


@pytest.fixture(name="input_events")
def fixture_input_events():
    """Fixture providing input interaction events."""
    return [
        {
            "type": 3,
            "timestamp": 34567,
            "data": {
                "source": 5,
                "id": 100,
                "text": "Hello World",
            },
        },
        {
            "type": 3,
            "timestamp": 45678,
            "data": {
                "source": 5,
                "id": 101,
                "isChecked": True,
            },
        },
        {
            "type": 3,
            "timestamp": 56789,
            "data": {
                "source": 5,
                "id": 102,
                "text": "Updated text",
                "isChecked": False,
            },
        },
    ]


@pytest.fixture(name="scroll_events")
def fixture_scroll_events():
    """Fixture providing scroll interaction events."""
    return [
        {
            "type": 3,
            "timestamp": 67890,
            "data": {
                "source": 3,
                "id": 200,
                "x": 0,
                "y": 500,
            },
        },
        {
            "type": 3,
            "timestamp": 78901,
            "data": {
                "source": 3,
                "id": 201,
                "x": 100,
                "y": 1000,
            },
        },
    ]


@pytest.fixture(name="non_interaction_events")
def fixture_non_interaction_events():
    """Fixture providing events that are not user interactions."""
    return [
        # FullSnapshot event
        {"type": 2, "timestamp": 1000, "data": {"node": {}}},
        # Mouse move event (source 1)
        {"type": 3, "timestamp": 2000, "data": {"source": 1, "x": 100, "y": 200}},
        # DOM mutation event (source 0)
        {
            "type": 3,
            "timestamp": 3000,
            "data": {"source": 0, "adds": []},
        },
        # Unknown source
        {"type": 3, "timestamp": 4000, "data": {"source": 99, "id": 123}},
        # Meta event
        {"type": 4, "timestamp": 5000, "data": {"width": 1920, "height": 1080}},
    ]


def test_extract_click_interactions(click_events):
    """Test that click events correctly produce type 'click' with coordinates and target."""
    interactions = extract_user_interactions(click_events)

    assert len(interactions) == 2

    # First click
    click1 = interactions[0]
    assert click1.action == "click"
    assert click1.target_id == 42
    assert click1.value["x"] == 150
    assert click1.value["y"] == 200
    assert click1.timestamp == 12345

    # Second click (dblclick)
    click2 = interactions[1]
    assert click2.action == "click"
    assert click2.target_id == 84
    assert click2.value["x"] == 300
    assert click2.value["y"] == 400
    assert click2.timestamp == 23456


def test_extract_input_interactions(input_events):
    """Test that input events capture value or checked fields as expected."""
    interactions = extract_user_interactions(input_events)

    assert len(interactions) == 3

    # Text input
    input1 = interactions[0]
    assert input1.action == "input"
    assert input1.target_id == 100
    assert input1.value["value"] == "Hello World"
    assert "checked" not in input1.value
    assert input1.timestamp == 34567

    # Checkbox input
    input2 = interactions[1]
    assert input2.action == "input"
    assert input2.target_id == 101
    assert input2.value["checked"] is True
    assert "value" not in input2.value
    assert input2.timestamp == 45678

    # Combined text and checkbox input
    input3 = interactions[2]
    assert input3.action == "input"
    assert input3.target_id == 102
    assert input3.value["value"] == "Updated text"
    assert input3.value["checked"] is False
    assert input3.timestamp == 56789


def test_extract_scroll_interactions(scroll_events):
    """Test that scroll events produce 'scroll' interactions with x/y data."""
    interactions = extract_user_interactions(scroll_events)

    assert len(interactions) == 2

    # First scroll
    scroll1 = interactions[0]
    assert scroll1.action == "scroll"
    assert scroll1.target_id == 200
    assert scroll1.value["x"] == 0
    assert scroll1.value["y"] == 500
    assert scroll1.timestamp == 67890

    # Second scroll
    scroll2 = interactions[1]
    assert scroll2.action == "scroll"
    assert scroll2.target_id == 201
    assert scroll2.value["x"] == 100
    assert scroll2.value["y"] == 1000
    assert scroll2.timestamp == 78901


def test_extract_mixed_interactions_filters_only_interactions(
    click_events, input_events, scroll_events, non_interaction_events
):
    """Test that a mixed list of incremental snapshot events yields only click, input, and scroll interactions."""
    # Mix all event types together
    mixed_events = (
        non_interaction_events[:2]
        + click_events[:1]
        + non_interaction_events[2:3]
        + input_events[:1]
        + non_interaction_events[3:]
        + scroll_events[:1]
    )

    interactions = extract_user_interactions(mixed_events)

    # Should only extract the interaction events
    assert len(interactions) == 3

    # Verify we got one of each type in the correct order
    assert interactions[0].action == "click"
    assert interactions[0].target_id == 42
    assert interactions[1].action == "input"
    assert interactions[1].target_id == 100
    assert interactions[2].action == "scroll"
    assert interactions[2].target_id == 200


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
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 3, "id": 1, "x": 0, "y": 100},
        },  # scroll
        {
            "type": 3,
            "timestamp": 2000,
            "data": {"source": 2, "id": 2, "x": 50, "y": 60},
        },  # click
        {
            "type": 3,
            "timestamp": 3000,
            "data": {"source": 5, "id": 3, "text": "input"},
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
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 2, "x": 100, "y": 200},  # Missing id
        },
        {
            "type": 3,
            "timestamp": 2000,
            "data": {"source": 2, "id": 42, "x": 150, "y": 250},  # Valid
        },
        {
            "type": 3,
            "timestamp": 3000,
            "data": {"source": 5, "text": "no id"},  # Missing id
        },
        {
            "type": 3,
            "timestamp": 4000,
            "data": {"source": 5, "id": 43, "text": "valid"},  # Valid
        },
        {
            "type": 3,
            "timestamp": 5000,
            "data": {"source": 3, "x": 0, "y": 100},  # Missing id
        },
        {
            "type": 3,
            "timestamp": 6000,
            "data": {"source": 3, "id": 44, "x": 0, "y": 200},  # Valid
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
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 2, "id": 42},  # Missing x, y
        },
        {
            "type": 3,
            "timestamp": 2000,
            "data": {"source": 3, "id": 43, "x": 100},  # Missing y
        },
        {
            "type": 3,
            "timestamp": 3000,
            "data": {"source": 3, "id": 44, "y": 200},  # Missing x
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
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 5, "id": 42},  # No text or isChecked
        }
    ]

    interactions = extract_user_interactions(events_with_empty_input)

    assert len(interactions) == 1
    input_interaction = interactions[0]
    assert input_interaction.action == "input"
    assert input_interaction.target_id == 42
    assert input_interaction.value == {}
