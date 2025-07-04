"""
Unit tests for configuration and extensibility features.

Tests the configuration module exports, parameter overrides, and custom
extensibility hooks like DOM path formatters and distance comparators.
"""

import pytest
from feature_extraction import config
from feature_extraction.clustering import cluster_mouse_trajectories
from feature_extraction.scroll_patterns import detect_scroll_patterns
from feature_extraction.metadata import resolve_node_metadata
from feature_extraction.models import UINode


def test_config_module_exports_correct_defaults():
    """Test that the config module exports the correct default values."""
    assert config.DEFAULT_TIME_DELTA_MS == 100
    assert config.DEFAULT_DIST_DELTA_PX == 50
    assert config.DEFAULT_SCROLL_REACTION_MS == 2000
    assert config.DEFAULT_MAX_REACTION_MS == 10000
    
    # Test that default functions exist and are callable
    assert callable(config.default_dom_path_formatter)
    assert callable(config.default_distance_comparator)


def test_default_dom_path_formatter():
    """Test that the default DOM path formatter works correctly."""
    path_parts = ["html", "body", "div.container", "button#submit"]
    result = config.default_dom_path_formatter(path_parts)
    assert result == "html > body > div.container > button#submit"


def test_default_distance_comparator():
    """Test that the default distance comparator computes Euclidean distance."""
    point1 = {"x": 0, "y": 0}
    point2 = {"x": 3, "y": 4}
    distance = config.default_distance_comparator(point1, point2)
    assert distance == 5.0  # 3-4-5 triangle


def test_clustering_with_custom_distance_threshold():
    """Test that smaller DEFAULT_DIST_DELTA_PX splits clusters earlier."""
    events = [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 1, "x": 0, "y": 0},
        },
        {
            "type": 3,
            "timestamp": 1050,
            "data": {"source": 1, "x": 30, "y": 40},  # Distance = 50px exactly
        },
    ]

    # With default threshold (50px), should be one cluster
    clusters_default = cluster_mouse_trajectories(events)
    assert len(clusters_default) == 1

    # With smaller threshold (40px), should be two clusters
    clusters_strict = cluster_mouse_trajectories(events, dist_delta_px=40)
    assert len(clusters_strict) == 2


def test_clustering_with_custom_time_threshold():
    """Test that smaller time threshold splits clusters earlier."""
    events = [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 1, "x": 100, "y": 200},
        },
        {
            "type": 3,
            "timestamp": 1080,  # 80ms later
            "data": {"source": 1, "x": 110, "y": 210},
        },
    ]

    # With default threshold (100ms), should be one cluster
    clusters_default = cluster_mouse_trajectories(events)
    assert len(clusters_default) == 1

    # With smaller threshold (50ms), should be two clusters
    clusters_strict = cluster_mouse_trajectories(events, time_delta_ms=50)
    assert len(clusters_strict) == 2


def test_clustering_with_custom_distance_comparator():
    """Test that a custom distance comparator is invoked and affects clustering."""
    events = [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 1, "x": 0, "y": 0},
        },
        {
            "type": 3,
            "timestamp": 1050,
            "data": {"source": 1, "x": 100, "y": 100},  # Far apart
        },
    ]

    # Custom comparator that always returns a small distance
    def always_close_comparator(point1, point2):
        return 1.0  # Always return 1px distance

    # With custom comparator, should be one cluster (distance always < threshold)
    clusters = cluster_mouse_trajectories(
        events, dist_delta_px=50, distance_comparator=always_close_comparator
    )
    assert len(clusters) == 1

    # With default comparator, should be two clusters (distance > threshold)
    clusters_default = cluster_mouse_trajectories(events, dist_delta_px=50)
    assert len(clusters_default) == 2


def test_scroll_patterns_with_custom_reaction_window():
    """Test that custom max_reaction_ms affects scroll pattern detection."""
    events = [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 3, "id": 100, "x": 0, "y": 500},
        },  # Scroll
        {
            "type": 3,
            "timestamp": 1800,  # 800ms later
            "data": {"source": 0, "adds": [{"node": {"id": 200}}]},
        },  # Mutation
    ]

    # With default window (2000ms), should find pattern
    patterns_default = detect_scroll_patterns(events)
    assert len(patterns_default) == 1

    # With smaller window (500ms), should find no pattern
    patterns_strict = detect_scroll_patterns(events, max_reaction_ms=500)
    assert len(patterns_strict) == 0


def test_custom_dom_path_formatter():
    """Test that a custom DOM path formatter is invoked and its output appears."""
    node_by_id = {
        1: UINode(id=1, tag="html", attributes={}, text="", parent=None),
        2: UINode(id=2, tag="body", attributes={}, text="", parent=1),
        3: UINode(
            id=3,
            tag="button",
            attributes={"id": "submit"},
            text="Submit",
            parent=2,
        ),
    }

    # Custom formatter that uses different separators
    def custom_formatter(path_parts):
        return " >> ".join(path_parts)

    metadata = resolve_node_metadata(3, node_by_id, custom_formatter)

    # Should use custom separator
    assert metadata["dom_path"] == "html >> body >> button#submit"

    # Compare with default formatter
    metadata_default = resolve_node_metadata(3, node_by_id)
    assert metadata_default["dom_path"] == "html > body > button#submit"


def test_custom_dom_path_formatter_with_complex_logic():
    """Test that a custom DOM path formatter can implement complex logic."""
    node_by_id = {
        1: UINode(id=1, tag="html", attributes={}, text="", parent=None),
        2: UINode(id=2, tag="body", attributes={}, text="", parent=1),
        3: UINode(
            id=3,
            tag="div",
            attributes={"class": "container main"},
            text="",
            parent=2,
        ),
    }

    # Custom formatter that adds indices and uppercases tags
    def indexed_formatter(path_parts):
        formatted_parts = []
        for i, part in enumerate(path_parts):
            formatted_parts.append(f"[{i}]{part.upper()}")
        return " -> ".join(formatted_parts)

    metadata = resolve_node_metadata(3, node_by_id, indexed_formatter)

    # Should use custom formatting logic
    assert metadata["dom_path"] == "[0]HTML -> [1]BODY -> [2]DIV.CONTAINER"


def test_config_parameters_are_used_as_defaults():
    """Test that config parameters are actually used as function defaults."""
    # This test verifies that when no parameters are passed, the config defaults are used
    
    # Test clustering defaults
    events = [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 1, "x": 0, "y": 0},
        },
        {
            "type": 3,
            "timestamp": 1000 + config.DEFAULT_TIME_DELTA_MS + 1,  # Just over threshold
            "data": {"source": 1, "x": 0, "y": 0},
        },
    ]

    # Should split into two clusters due to time threshold
    clusters = cluster_mouse_trajectories(events)
    assert len(clusters) == 2

    # Test scroll pattern defaults
    scroll_events = [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 3, "id": 100, "x": 0, "y": 500},
        },
        {
            "type": 3,
            "timestamp": 1000 + config.DEFAULT_SCROLL_REACTION_MS + 1,  # Just over threshold
            "data": {"source": 0, "adds": [{"node": {"id": 200}}]},
        },
    ]

    # Should find no patterns due to time threshold
    patterns = detect_scroll_patterns(scroll_events)
    assert len(patterns) == 0


def test_extensibility_hooks_are_optional():
    """Test that extensibility hooks have sensible defaults and are optional."""
    node_by_id = {
        1: UINode(id=1, tag="div", attributes={}, text="", parent=None),
    }

    # Should work without passing custom formatter
    metadata = resolve_node_metadata(1, node_by_id)
    assert "dom_path" in metadata
    assert metadata["dom_path"] == "div"

    # Should work without passing custom distance comparator
    events = [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 1, "x": 0, "y": 0},
        },
    ]
    clusters = cluster_mouse_trajectories(events)
    assert len(clusters) == 1
