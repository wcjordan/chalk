"""
Unit tests for mouse trajectory clustering.

Tests the clustering of mouse movement events based on temporal and spatial
proximity thresholds, verifying correct cluster boundaries and metrics.
"""

from unittest.mock import patch

import pytest

from feature_extraction.clustering import cluster_mouse_trajectories


@pytest.fixture(name="non_mousemove_events")
def fixture_non_mousemove_events():
    """Fixture providing events that are not mousemove events."""
    return [
        # FullSnapshot event
        {"type": 2, "timestamp": 1000, "data": {"node": {}}},
        # Click event (source 2)
        {"type": 3, "timestamp": 1100, "data": {"source": 2, "id": 42}},
        # DOM mutation (source 0)
        {"type": 3, "timestamp": 1200, "data": {"source": 0, "adds": []}},
        # Scroll event (source 3)
        {"type": 3, "timestamp": 1300, "data": {"source": 3, "x": 0, "y": 100}},
        # Input event (source 5)
        {"type": 3, "timestamp": 1400, "data": {"source": 5, "text": "input"}},
    ]


def test_no_mousemove_events_returns_empty_list(non_mousemove_events):
    """Test that passing no mousemove events returns an empty list."""
    clusters = cluster_mouse_trajectories(non_mousemove_events)
    assert len(clusters) == 0


def test_empty_events_list_returns_empty_list():
    """Test that passing an empty events list returns an empty list."""
    clusters = cluster_mouse_trajectories([])
    assert len(clusters) == 0


def test_clusters_preserve_chronological_order():
    """Test that clusters are returned in chronological order."""
    events = [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 1, "x": 100, "y": 200},
        },
        {
            "type": 3,
            "timestamp": 2000,  # Large time gap
            "data": {"source": 1, "x": 200, "y": 300},
        },
        {
            "type": 3,
            "timestamp": 500,  # Earlier timestamp (out of order)
            "data": {"source": 1, "x": 50, "y": 100},
        },
    ]

    with patch("feature_extraction.config.DEFAULT_TIME_DELTA_MS", 100):
        clusters = cluster_mouse_trajectories(events)

    # Should have 3 clusters due to large gaps
    assert len(clusters) == 3

    # Clusters should be in the order they appear in the events list
    assert clusters[0].start_ts == 1000
    assert clusters[1].start_ts == 2000
    assert clusters[2].start_ts == 500


def test_missing_coordinates_default_to_zero():
    """Test that missing x/y coordinates default to 0."""
    events = [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 1, "x": 10, "y": 5},
        },
        {
            "type": 3,
            "timestamp": 1050,
            "data": {"source": 1},  # Missing x and y
        },
        {
            "type": 3,
            "timestamp": 1100,
            "data": {"source": 1, "x": 10},  # Missing y
        },
    ]

    clusters = cluster_mouse_trajectories(events)

    assert len(clusters) == 1  # Should form one cluster
    cluster = clusters[0]
    assert cluster.point_count == 3

    # Check that missing coordinates default to 0
    assert cluster.points[1] == {"x": 0, "y": 0, "ts": 1050}
    assert cluster.points[2] == {"x": 10, "y": 0, "ts": 1100}


def test_euclidean_distance_calculation():
    """Test that Euclidean distance is calculated correctly for clustering decisions."""
    events = [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 1, "x": 0, "y": 0},
        },
        {
            "type": 3,
            "timestamp": 1050,
            "data": {
                "source": 1,
                "x": 30,
                "y": 40,
            },  # Distance = sqrt(30^2 + 40^2) = 50px exactly
        },
        {
            "type": 3,
            "timestamp": 1100,
            "data": {
                "source": 1,
                "x": 31,
                "y": 41,
            },  # Distance = sqrt(1^2 + 1^2) ≈ 1.4px
        },
    ]

    # With distance threshold of 50px, all events should be in one cluster
    with patch("feature_extraction.config.DEFAULT_DIST_DELTA_PX", 50):
        clusters = cluster_mouse_trajectories(events)
    assert len(clusters) == 1  # All in one cluster (50px is exactly at threshold)

    # With distance threshold of 49px, should split after first event
    with patch("feature_extraction.config.DEFAULT_DIST_DELTA_PX", 49):
        clusters = cluster_mouse_trajectories(events)
    assert len(clusters) == 2  # Split because 50px > 49px threshold
