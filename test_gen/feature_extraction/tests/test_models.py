"""
Unit tests for the feature extraction data models.

Tests the construction and basic functionality of all data classes
used in the feature extraction pipeline.
"""

from feature_extraction.models import (
    UserInteraction,
    UINode,
    ScrollPattern,
    FeatureChunk,
    create_empty_features_obj,
)


def test_user_interaction_creation():
    """Test that UserInteraction objects can be created with correct attributes."""
    interaction = UserInteraction(
        action="click", target_id=456, value={"x": 100, "y": 200}, timestamp=23456
    )

    assert interaction.action == "click"
    assert interaction.target_id == 456
    assert interaction.value == {"x": 100, "y": 200}
    assert interaction.timestamp == 23456


def test_ui_node_creation():
    """Test that UINode objects can be created with correct attributes."""
    node = UINode(
        id=789,
        tag="button",
        attributes={"aria-label": "Submit", "class": "btn"},
        text="Submit Form",
        parent=100,
    )

    assert node.id == 789
    assert node.tag == "button"
    assert node.attributes == {"aria-label": "Submit", "class": "btn"}
    assert node.text == "Submit Form"
    assert node.parent == 100


def test_ui_node_root_creation():
    """Test that UINode objects can be created with no parent (root node)."""
    root_node = UINode(id=1, tag="html", attributes={}, text="", parent=None)

    assert root_node.parent is None


def test_scroll_pattern_creation():
    """Test that ScrollPattern objects can be created with correct attributes."""
    pattern = ScrollPattern(
        scroll_event={"type": 3, "data": {"source": 3, "x": 0, "y": 100}},
        mutation_event={"type": 3, "data": {"source": 0, "adds": []}},
        delay_ms=800,
    )

    assert pattern.scroll_event["type"] == 3
    assert pattern.mutation_event["type"] == 3
    assert pattern.delay_ms == 800


def test_feature_chunk_creation():
    """Test that FeatureChunk objects can be created with correct attributes."""
    chunk = FeatureChunk(
        chunk_id="session_123-chunk000",
        start_time=10000,
        end_time=15000,
        events=[{"type": 2, "timestamp": 10000}],
        features=create_empty_features_obj(),
        metadata={"num_events": 1, "duration_ms": 5000},
    )

    assert chunk.chunk_id == "session_123-chunk000"
    assert chunk.start_time == 10000
    assert chunk.end_time == 15000
    assert len(chunk.events) == 1
    assert "dom_mutations" in chunk.features
    assert chunk.metadata["num_events"] == 1


def test_feature_chunk_empty_features(empty_feature_chunk):
    """Test that FeatureChunk can be instantiated with empty feature lists."""
    features = empty_feature_chunk.features
    # Verify all feature lists are present and empty
    assert isinstance(features["dom_mutations"], list)
    assert len(features["dom_mutations"]) == 0
    assert isinstance(features["interactions"], list)
    assert len(features["interactions"]) == 0
    assert isinstance(features["ui_nodes"], dict)
    assert len(features["ui_nodes"]) == 0
    assert isinstance(features["scroll_patterns"], list)
    assert len(features["scroll_patterns"]) == 0
