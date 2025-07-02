"""
Unit tests for the feature extraction data models.

Tests the construction and basic functionality of all data classes
used in the feature extraction pipeline.
"""

import pytest
from feature_extraction.models import (
    DomMutation,
    UserInteraction,
    EventDelay,
    UINode,
    MouseCluster,
    ScrollPattern,
    FeatureChunk
)


def test_dom_mutation_creation():
    """Test that DomMutation objects can be created with correct attributes."""
    mutation = DomMutation(
        mutation_type="attribute",
        target_id=123,
        details={"class": "active"},
        timestamp=12345
    )
    
    assert mutation.mutation_type == "attribute"
    assert mutation.target_id == 123
    assert mutation.details == {"class": "active"}
    assert mutation.timestamp == 12345


def test_user_interaction_creation():
    """Test that UserInteraction objects can be created with correct attributes."""
    interaction = UserInteraction(
        action="click",
        target_id=456,
        value={"x": 100, "y": 200},
        timestamp=23456
    )
    
    assert interaction.action == "click"
    assert interaction.target_id == 456
    assert interaction.value == {"x": 100, "y": 200}
    assert interaction.timestamp == 23456


def test_event_delay_creation():
    """Test that EventDelay objects can be created with correct attributes."""
    delay = EventDelay(
        from_ts=1000,
        to_ts=1500,
        delta_ms=500
    )
    
    assert delay.from_ts == 1000
    assert delay.to_ts == 1500
    assert delay.delta_ms == 500


def test_ui_node_creation():
    """Test that UINode objects can be created with correct attributes."""
    node = UINode(
        id=789,
        tag="button",
        attributes={"aria-label": "Submit", "class": "btn"},
        text="Submit Form",
        parent=100
    )
    
    assert node.id == 789
    assert node.tag == "button"
    assert node.attributes == {"aria-label": "Submit", "class": "btn"}
    assert node.text == "Submit Form"
    assert node.parent == 100


def test_ui_node_root_creation():
    """Test that UINode objects can be created with no parent (root node)."""
    root_node = UINode(
        id=1,
        tag="html",
        attributes={},
        text="",
        parent=None
    )
    
    assert root_node.parent is None


def test_mouse_cluster_creation():
    """Test that MouseCluster objects can be created with correct attributes."""
    cluster = MouseCluster(
        start_ts=5000,
        end_ts=5500,
        points=[
            {"x": 10, "y": 20, "ts": 5000},
            {"x": 15, "y": 25, "ts": 5100},
            {"x": 20, "y": 30, "ts": 5200}
        ],
        duration_ms=500,
        point_count=3
    )
    
    assert cluster.start_ts == 5000
    assert cluster.end_ts == 5500
    assert len(cluster.points) == 3
    assert cluster.points[0] == {"x": 10, "y": 20, "ts": 5000}
    assert cluster.duration_ms == 500
    assert cluster.point_count == 3


def test_scroll_pattern_creation():
    """Test that ScrollPattern objects can be created with correct attributes."""
    pattern = ScrollPattern(
        scroll_event={"type": 3, "data": {"source": 3, "x": 0, "y": 100}},
        mutation_event={"type": 3, "data": {"source": 0, "adds": []}},
        delay_ms=800
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
        features={
            "dom_mutations": [],
            "interactions": [],
            "delays": [],
            "ui_nodes": {},
            "mouse_clusters": [],
            "scroll_patterns": []
        },
        metadata={"num_events": 1, "duration_ms": 5000}
    )
    
    assert chunk.chunk_id == "session_123-chunk000"
    assert chunk.start_time == 10000
    assert chunk.end_time == 15000
    assert len(chunk.events) == 1
    assert "dom_mutations" in chunk.features
    assert chunk.metadata["num_events"] == 1


def test_feature_chunk_empty_features():
    """Test that FeatureChunk can be instantiated with empty feature lists."""
    chunk = FeatureChunk(
        chunk_id="test-chunk",
        start_time=0,
        end_time=1000,
        events=[],
        features={
            "dom_mutations": [],
            "interactions": [],
            "delays": [],
            "ui_nodes": {},
            "mouse_clusters": [],
            "scroll_patterns": []
        },
        metadata={}
    )
    
    # Verify all feature lists are present and empty
    assert isinstance(chunk.features["dom_mutations"], list)
    assert len(chunk.features["dom_mutations"]) == 0
    assert isinstance(chunk.features["interactions"], list)
    assert len(chunk.features["interactions"]) == 0
    assert isinstance(chunk.features["delays"], list)
    assert len(chunk.features["delays"]) == 0
    assert isinstance(chunk.features["ui_nodes"], dict)
    assert len(chunk.features["ui_nodes"]) == 0
    assert isinstance(chunk.features["mouse_clusters"], list)
    assert len(chunk.features["mouse_clusters"]) == 0
    assert isinstance(chunk.features["scroll_patterns"], list)
    assert len(chunk.features["scroll_patterns"]) == 0
