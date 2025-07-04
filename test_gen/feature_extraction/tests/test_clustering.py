"""
Unit tests for mouse trajectory clustering.

Tests the clustering of mouse movement events based on temporal and spatial
proximity thresholds, verifying correct cluster boundaries and metrics.
"""

import pytest
from feature_extraction.clustering import cluster_mouse_trajectories


@pytest.fixture(name="consecutive_events_within_thresholds")
def fixture_consecutive_events_within_thresholds():
    """Fixture providing consecutive mousemove events within both time and distance thresholds."""
    return [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 1, "x": 100, "y": 200},
        },
        {
            "type": 3,
            "timestamp": 1050,  # 50ms later (< 100ms threshold)
            "data": {"source": 1, "x": 120, "y": 210},  # ~22px away (< 50px threshold)
        },
        {
            "type": 3,
            "timestamp": 1080,  # 30ms later (< 100ms threshold)
            "data": {"source": 1, "x": 130, "y": 215},  # ~11px away (< 50px threshold)
        },
    ]


@pytest.fixture(name="events_separated_by_time")
def fixture_events_separated_by_time():
    """Fixture providing mousemove events separated by more than time threshold."""
    return [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 1, "x": 100, "y": 200},
        },
        {
            "type": 3,
            "timestamp": 1050,  # 50ms later (within threshold)
            "data": {"source": 1, "x": 110, "y": 205},
        },
        {
            "type": 3,
            "timestamp": 1200,  # 150ms later (> 100ms threshold)
            "data": {"source": 1, "x": 115, "y": 210},
        },
        {
            "type": 3,
            "timestamp": 1230,  # 30ms later (within threshold)
            "data": {"source": 1, "x": 120, "y": 215},
        },
    ]


@pytest.fixture(name="events_separated_by_distance")
def fixture_events_separated_by_distance():
    """Fixture providing mousemove events separated by more than distance threshold."""
    return [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 1, "x": 100, "y": 200},
        },
        {
            "type": 3,
            "timestamp": 1050,  # 50ms later (within threshold)
            "data": {"source": 1, "x": 120, "y": 210},  # ~22px away (within threshold)
        },
        {
            "type": 3,
            "timestamp": 1080,  # 30ms later (within threshold)
            "data": {"source": 1, "x": 200, "y": 300},  # ~113px away (> 50px threshold)
        },
        {
            "type": 3,
            "timestamp": 1100,  # 20ms later (within threshold)
            "data": {"source": 1, "x": 210, "y": 305},  # ~11px away (within threshold)
        },
    ]


@pytest.fixture(name="mixed_temporal_spatial_splits")
def fixture_mixed_temporal_spatial_splits():
    """Fixture providing events with both temporal and spatial splits."""
    return [
        # Cluster 1: Two close events
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 1, "x": 100, "y": 200},
        },
        {
            "type": 3,
            "timestamp": 1030,  # 30ms later (within threshold)
            "data": {"source": 1, "x": 110, "y": 205},  # ~11px away (within threshold)
        },
        # Cluster 2: Separated by distance
        {
            "type": 3,
            "timestamp": 1060,  # 30ms later (within threshold)
            "data": {"source": 1, "x": 300, "y": 400},  # ~283px away (> 50px threshold)
        },
        # Cluster 3: Separated by time
        {
            "type": 3,
            "timestamp": 1200,  # 140ms later (> 100ms threshold)
            "data": {"source": 1, "x": 310, "y": 405},  # ~11px away (within threshold)
        },
        {
            "type": 3,
            "timestamp": 1220,  # 20ms later (within threshold)
            "data": {"source": 1, "x": 315, "y": 410},  # ~7px away (within threshold)
        },
    ]


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


def test_consecutive_events_within_thresholds_form_single_cluster(consecutive_events_within_thresholds):
    """Test that consecutive mousemove events within both thresholds form a single cluster."""
    clusters = cluster_mouse_trajectories(consecutive_events_within_thresholds)

    assert len(clusters) == 1

    cluster = clusters[0]
    assert cluster.start_ts == 1000
    assert cluster.end_ts == 1080
    assert cluster.duration_ms == 80
    assert cluster.point_count == 3

    # Verify all points are included
    assert len(cluster.points) == 3
    assert cluster.points[0] == {"x": 100, "y": 200, "ts": 1000}
    assert cluster.points[1] == {"x": 120, "y": 210, "ts": 1050}
    assert cluster.points[2] == {"x": 130, "y": 215, "ts": 1080}


def test_events_separated_by_time_split_into_clusters(events_separated_by_time):
    """Test that events separated by more than time_delta_ms split into two clusters."""
    clusters = cluster_mouse_trajectories(events_separated_by_time, time_delta_ms=100)

    assert len(clusters) == 2

    # First cluster: events at 1000ms and 1050ms
    cluster1 = clusters[0]
    assert cluster1.start_ts == 1000
    assert cluster1.end_ts == 1050
    assert cluster1.duration_ms == 50
    assert cluster1.point_count == 2

    # Second cluster: events at 1200ms and 1230ms
    cluster2 = clusters[1]
    assert cluster2.start_ts == 1200
    assert cluster2.end_ts == 1230
    assert cluster2.duration_ms == 30
    assert cluster2.point_count == 2


def test_events_separated_by_distance_split_into_clusters(events_separated_by_distance):
    """Test that events with spatial separation exceeding dist_delta_px split into two clusters."""
    clusters = cluster_mouse_trajectories(events_separated_by_distance, dist_delta_px=50)

    assert len(clusters) == 2

    # First cluster: first two events (close together)
    cluster1 = clusters[0]
    assert cluster1.start_ts == 1000
    assert cluster1.end_ts == 1050
    assert cluster1.point_count == 2

    # Second cluster: last two events (after the big jump)
    cluster2 = clusters[1]
    assert cluster2.start_ts == 1080
    assert cluster2.end_ts == 1100
    assert cluster2.point_count == 2


def test_mixed_temporal_spatial_splits_produce_correct_clusters(mixed_temporal_spatial_splits):
    """Test that a mix of temporal and spatial splits produces the correct number of clusters."""
    clusters = cluster_mouse_trajectories(
        mixed_temporal_spatial_splits, 
        time_delta_ms=100, 
        dist_delta_px=50
    )

    assert len(clusters) == 3

    # Cluster 1: First two events (close in time and space)
    cluster1 = clusters[0]
    assert cluster1.start_ts == 1000
    assert cluster1.end_ts == 1030
    assert cluster1.point_count == 2

    # Cluster 2: Single event after spatial jump
    cluster2 = clusters[1]
    assert cluster2.start_ts == 1060
    assert cluster2.end_ts == 1060
    assert cluster2.point_count == 1

    # Cluster 3: Last two events after temporal gap
    cluster3 = clusters[2]
    assert cluster3.start_ts == 1200
    assert cluster3.end_ts == 1220
    assert cluster3.point_count == 2


def test_no_mousemove_events_returns_empty_list(non_mousemove_events):
    """Test that passing no mousemove events returns an empty list."""
    clusters = cluster_mouse_trajectories(non_mousemove_events)
    assert len(clusters) == 0


def test_empty_events_list_returns_empty_list():
    """Test that passing an empty events list returns an empty list."""
    clusters = cluster_mouse_trajectories([])
    assert len(clusters) == 0


def test_single_mousemove_event_creates_single_point_cluster():
    """Test that a single mousemove event creates a cluster with one point."""
    events = [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 1, "x": 100, "y": 200},
        }
    ]

    clusters = cluster_mouse_trajectories(events)

    assert len(clusters) == 1
    cluster = clusters[0]
    assert cluster.start_ts == 1000
    assert cluster.end_ts == 1000
    assert cluster.duration_ms == 0
    assert cluster.point_count == 1
    assert cluster.points[0] == {"x": 100, "y": 200, "ts": 1000}


def test_custom_thresholds_affect_clustering():
    """Test that custom time and distance thresholds affect clustering behavior."""
    events = [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 1, "x": 100, "y": 200},
        },
        {
            "type": 3,
            "timestamp": 1080,  # 80ms later
            "data": {"source": 1, "x": 130, "y": 230},  # ~42px away
        },
    ]

    # With default thresholds (100ms, 50px), should be one cluster
    clusters_default = cluster_mouse_trajectories(events)
    assert len(clusters_default) == 1

    # With stricter time threshold (50ms), should be two clusters
    clusters_strict_time = cluster_mouse_trajectories(events, time_delta_ms=50)
    assert len(clusters_strict_time) == 2

    # With stricter distance threshold (30px), should be two clusters
    clusters_strict_dist = cluster_mouse_trajectories(events, dist_delta_px=30)
    assert len(clusters_strict_dist) == 2


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

    clusters = cluster_mouse_trajectories(events, time_delta_ms=100)

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
            "data": {"source": 1, "x": 100, "y": 200},
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


def test_cluster_metrics_accuracy():
    """Test that cluster metrics (duration, point count) are computed accurately."""
    events = [
        {
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 1, "x": 100, "y": 200},
        },
        {
            "type": 3,
            "timestamp": 1025,
            "data": {"source": 1, "x": 105, "y": 205},
        },
        {
            "type": 3,
            "timestamp": 1075,
            "data": {"source": 1, "x": 110, "y": 210},
        },
    ]

    clusters = cluster_mouse_trajectories(events)

    assert len(clusters) == 1
    cluster = clusters[0]

    # Verify metrics
    assert cluster.start_ts == 1000
    assert cluster.end_ts == 1075
    assert cluster.duration_ms == 75  # 1075 - 1000
    assert cluster.point_count == 3
    assert len(cluster.points) == 3


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
            "data": {"source": 1, "x": 30, "y": 40},  # Distance = sqrt(30^2 + 40^2) = 50px exactly
        },
        {
            "type": 3,
            "timestamp": 1100,
            "data": {"source": 1, "x": 31, "y": 41},  # Distance = sqrt(1^2 + 1^2) ≈ 1.4px
        },
    ]

    # With distance threshold of 50px, first two should cluster, third should be separate
    clusters = cluster_mouse_trajectories(events, dist_delta_px=50)
    assert len(clusters) == 1  # All in one cluster (50px is exactly at threshold)

    # With distance threshold of 49px, should split after first event
    clusters = cluster_mouse_trajectories(events, dist_delta_px=49)
    assert len(clusters) == 2  # Split because 50px > 49px threshold
````

Now I'll update the todo list to mark Step 8 as completed:

test_gen/docs/feature_extraction/todo.md
````markdown
<<<<<<< SEARCH
## Step 8: Mouse Trajectory Clustering

### Tasks:
- [ ] Create `test_gen/feature_extraction/clustering.py`
- [ ] Implement `cluster_mouse_trajectories(events: List[dict], time_delta_ms=100, dist_delta_px=50) -> List[MouseCluster]`:
  - [ ] Filter events where `type == 3` and `data.source == 1`
  - [ ] Compute time difference and Euclidean distance to previous mousemove
  - [ ] Start new cluster when either threshold exceeded
  - [ ] Build MouseCluster with start_ts, end_ts, point list, duration_ms, point_count
  - [ ] Return clusters in chronological order
- [ ] Add module-level docstring explaining clustering parameters
- [ ] Create `test_gen/feature_extraction/tests/test_clustering.py`:
  - [ ] Test consecutive events within thresholds form single cluster
  - [ ] Test events separated by time_delta_ms split into two clusters
  - [ ] Test events with spatial separation > dist_delta_px split clusters
  - [ ] Test mix of temporal/spatial splits produces correct cluster count
  - [ ] Test no mousemove events returns empty list
- [ ] Verify pytest passes all cases
- [ ] Clusters match expected boundaries and metrics
- [ ] No regressions in existing tests
