"""
Tests for JSON serialization functionality of feature extraction models.

Tests that all dataclass models can be properly serialized to dictionaries
and that the FeatureChunk serialization handles complex nested structures correctly.
"""

import pytest
from feature_extraction.models import (
    DomMutation,
    UserInteraction,
    EventDelay,
    UINode,
    MouseCluster,
    ScrollPattern,
    FeatureChunk,
)


def test_dom_mutation_to_dict():
    """Test DomMutation serialization to dictionary."""
    mutation = DomMutation(
        mutation_type="attribute",
        target_id=123,
        details={"class": "active", "id": "button1"},
        timestamp=1000,
    )

    result = mutation.to_dict()

    assert result == {
        "mutation_type": "attribute",
        "target_id": 123,
        "details": {"class": "active", "id": "button1"},
        "timestamp": 1000,
    }


def test_user_interaction_to_dict():
    """Test UserInteraction serialization to dictionary."""
    interaction = UserInteraction(
        action="click",
        target_id=456,
        value={"x": 100, "y": 200},
        timestamp=2000,
    )

    result = interaction.to_dict()

    assert result == {
        "action": "click",
        "target_id": 456,
        "value": {"x": 100, "y": 200},
        "timestamp": 2000,
    }


def test_event_delay_to_dict():
    """Test EventDelay serialization to dictionary."""
    delay = EventDelay(from_ts=1000, to_ts=1500, delta_ms=500)

    result = delay.to_dict()

    assert result == {
        "from_ts": 1000,
        "to_ts": 1500,
        "delta_ms": 500,
    }


def test_ui_node_to_dict():
    """Test UINode serialization to dictionary."""
    node = UINode(
        id=789,
        tag="button",
        attributes={"class": "btn", "aria-label": "Submit"},
        text="Click me",
        parent=123,
    )

    result = node.to_dict()

    assert result == {
        "id": 789,
        "tag": "button",
        "attributes": {"class": "btn", "aria-label": "Submit"},
        "text": "Click me",
        "parent": 123,
    }


def test_ui_node_to_dict_no_parent():
    """Test UINode serialization when parent is None."""
    node = UINode(
        id=1,
        tag="html",
        attributes={},
        text="",
        parent=None,
    )

    result = node.to_dict()

    assert result == {
        "id": 1,
        "tag": "html",
        "attributes": {},
        "text": "",
        "parent": None,
    }


def test_mouse_cluster_to_dict():
    """Test MouseCluster serialization to dictionary."""
    cluster = MouseCluster(
        start_ts=1000,
        end_ts=1200,
        points=[
            {"x": 10, "y": 20, "ts": 1000},
            {"x": 15, "y": 25, "ts": 1100},
            {"x": 20, "y": 30, "ts": 1200},
        ],
        duration_ms=200,
        point_count=3,
    )

    result = cluster.to_dict()

    assert result == {
        "start_ts": 1000,
        "end_ts": 1200,
        "points": [
            {"x": 10, "y": 20, "ts": 1000},
            {"x": 15, "y": 25, "ts": 1100},
            {"x": 20, "y": 30, "ts": 1200},
        ],
        "duration_ms": 200,
        "point_count": 3,
    }


def test_scroll_pattern_to_dict():
    """Test ScrollPattern serialization to dictionary."""
    pattern = ScrollPattern(
        scroll_event={
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 3, "x": 0, "y": 100},
        },
        mutation_event={
            "type": 3,
            "timestamp": 1200,
            "data": {"source": 0, "adds": [{"id": 456}]},
        },
        delay_ms=200,
    )

    result = pattern.to_dict()

    assert result == {
        "scroll_event": {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 3, "x": 0, "y": 100},
        },
        "mutation_event": {
            "type": 3,
            "timestamp": 1200,
            "data": {"source": 0, "adds": [{"id": 456}]},
        },
        "delay_ms": 200,
    }


def test_feature_chunk_to_dict_complete():
    """Test FeatureChunk serialization with all feature types."""
    # Create sample features
    dom_mutation = DomMutation("add", 123, {"tag": "div"}, 1000)
    user_interaction = UserInteraction("click", 456, {"x": 100, "y": 200}, 2000)
    event_delay = EventDelay(1000, 2000, 1000)
    ui_node = UINode(789, "button", {"class": "btn"}, "Click", 456)
    mouse_cluster = MouseCluster(1000, 1100, [{"x": 10, "y": 20, "ts": 1050}], 100, 1)
    scroll_pattern = ScrollPattern(
        {"timestamp": 1000, "data": {"source": 3}},
        {"timestamp": 1200, "data": {"source": 0}},
        200,
    )

    feature_chunk = FeatureChunk(
        chunk_id="test-chunk-001",
        start_time=1000,
        end_time=3000,
        events=[{"type": 3, "timestamp": 1000}],
        features={
            "dom_mutations": [dom_mutation],
            "interactions": [user_interaction],
            "inter_event_delays": [event_delay],
            "reaction_delays": [event_delay],
            "ui_nodes": {789: ui_node},
            "mouse_clusters": [mouse_cluster],
            "scroll_patterns": [scroll_pattern],
        },
        metadata={"session_id": "test-session"},
    )

    result = feature_chunk.to_dict()

    # Verify basic chunk properties
    assert result["chunk_id"] == "test-chunk-001"
    assert result["start_time"] == 1000
    assert result["end_time"] == 3000
    assert result["events"] == [{"type": 3, "timestamp": 1000}]
    assert result["metadata"] == {"session_id": "test-session"}

    # Verify features are serialized correctly
    features = result["features"]

    # Check DOM mutations
    assert len(features["dom_mutations"]) == 1
    assert features["dom_mutations"][0] == dom_mutation.to_dict()

    # Check interactions
    assert len(features["interactions"]) == 1
    assert features["interactions"][0] == user_interaction.to_dict()

    # Check delays
    assert len(features["inter_event_delays"]) == 1
    assert features["inter_event_delays"][0] == event_delay.to_dict()
    assert len(features["reaction_delays"]) == 1
    assert features["reaction_delays"][0] == event_delay.to_dict()

    # Check UI nodes (converted to string keys)
    assert len(features["ui_nodes"]) == 1
    assert "789" in features["ui_nodes"]
    assert features["ui_nodes"]["789"] == ui_node.to_dict()

    # Check mouse clusters
    assert len(features["mouse_clusters"]) == 1
    assert features["mouse_clusters"][0] == mouse_cluster.to_dict()

    # Check scroll patterns
    assert len(features["scroll_patterns"]) == 1
    assert features["scroll_patterns"][0] == scroll_pattern.to_dict()


def test_feature_chunk_to_dict_empty_features():
    """Test FeatureChunk serialization with empty feature lists."""
    feature_chunk = FeatureChunk(
        chunk_id="empty-chunk",
        start_time=0,
        end_time=1000,
        events=[],
        features={
            "dom_mutations": [],
            "interactions": [],
            "inter_event_delays": [],
            "reaction_delays": [],
            "ui_nodes": {},
            "mouse_clusters": [],
            "scroll_patterns": [],
        },
        metadata={},
    )

    result = feature_chunk.to_dict()

    # Verify all feature lists are empty but present
    features = result["features"]
    assert features["dom_mutations"] == []
    assert features["interactions"] == []
    assert features["inter_event_delays"] == []
    assert features["reaction_delays"] == []
    assert features["ui_nodes"] == {}
    assert features["mouse_clusters"] == []
    assert features["scroll_patterns"] == []


def test_feature_chunk_to_dict_with_plain_objects():
    """Test FeatureChunk serialization when features contain plain objects instead of dataclasses."""
    # Simulate features that might already be dictionaries
    feature_chunk = FeatureChunk(
        chunk_id="mixed-chunk",
        start_time=0,
        end_time=1000,
        events=[],
        features={
            "dom_mutations": [
                {
                    "mutation_type": "add",
                    "target_id": 1,
                    "details": {},
                    "timestamp": 500,
                }
            ],
            "interactions": [
                {"action": "click", "target_id": 2, "value": {}, "timestamp": 600}
            ],
            "inter_event_delays": [],
            "reaction_delays": [],
            "ui_nodes": {
                "1": {
                    "id": 1,
                    "tag": "div",
                    "attributes": {},
                    "text": "",
                    "parent": None,
                }
            },
            "mouse_clusters": [],
            "scroll_patterns": [],
        },
        metadata={},
    )

    # Should not raise errors when features are already dictionaries
    result = feature_chunk.to_dict()

    # Verify plain objects are preserved
    assert result["features"]["dom_mutations"] == [
        {"mutation_type": "add", "target_id": 1, "details": {}, "timestamp": 500}
    ]
    assert result["features"]["interactions"] == [
        {"action": "click", "target_id": 2, "value": {}, "timestamp": 600}
    ]
    assert result["features"]["ui_nodes"] == {
        "1": {"id": 1, "tag": "div", "attributes": {}, "text": "", "parent": None}
    }


def test_feature_chunk_serialization_roundtrip():
    """Test that serialization produces JSON-compatible output."""
    import json

    # Create a FeatureChunk with various data types
    feature_chunk = FeatureChunk(
        chunk_id="roundtrip-test",
        start_time=1000,
        end_time=2000,
        events=[{"type": 3, "timestamp": 1500, "data": {"source": 2}}],
        features={
            "dom_mutations": [DomMutation("text", 1, {"newText": "Hello"}, 1100)],
            "interactions": [UserInteraction("input", 2, {"value": "test"}, 1200)],
            "inter_event_delays": [EventDelay(1000, 1100, 100)],
            "reaction_delays": [],
            "ui_nodes": {3: UINode(3, "input", {"type": "text"}, "", 1)},
            "mouse_clusters": [],
            "scroll_patterns": [],
        },
        metadata={"test": True, "count": 42},
    )

    # Convert to dict and then to JSON string
    chunk_dict = feature_chunk.to_dict()
    json_str = json.dumps(chunk_dict, ensure_ascii=False, indent=2)

    # Parse back from JSON
    parsed_dict = json.loads(json_str)

    # Verify key fields are preserved
    assert parsed_dict["chunk_id"] == "roundtrip-test"
    assert parsed_dict["start_time"] == 1000
    assert parsed_dict["end_time"] == 2000
    assert len(parsed_dict["events"]) == 1
    assert len(parsed_dict["features"]["dom_mutations"]) == 1
    assert len(parsed_dict["features"]["interactions"]) == 1
    assert len(parsed_dict["features"]["ui_nodes"]) == 1
    assert parsed_dict["metadata"]["test"] is True
    assert parsed_dict["metadata"]["count"] == 42
