"""
Mouse Trajectory Clustering for rrweb Session Feature Extraction.

This module provides functionality to group mouse movement events into clusters
based on temporal and spatial proximity. This is useful for understanding user
intent patterns, identifying hover zones, and detecting exploratory vs. direct
mouse movements.

The clustering algorithm groups consecutive mousemove events that occur within
configurable time and distance thresholds. When either threshold is exceeded,
a new cluster is started. This helps identify distinct phases of mouse activity
and can reveal user interaction patterns.

Parameters:
    time_delta_ms: Maximum time gap between mousemove events in the same cluster (default: 100ms)
    dist_delta_px: Maximum Euclidean distance between mousemove events in the same cluster (default: 50px)

Usage:
    clusters = cluster_mouse_trajectories(events, time_delta_ms=150, dist_delta_px=75)
    for cluster in clusters:
        print(f"Cluster: {cluster.point_count} points over {cluster.duration_ms}ms")
"""

import math
from typing import List
from .models import MouseCluster


def cluster_mouse_trajectories(
    events: List[dict], time_delta_ms: int = 100, dist_delta_px: int = 50
) -> List[MouseCluster]:
    """
    Groups rrweb mousemove events into clusters based on temporal
    and spatial proximity.

    This function processes rrweb events and groups mouse movement events
    (type == 3, data.source == 1) into clusters when consecutive events
    occur within specified time and distance thresholds. This is useful
    for identifying distinct phases of mouse activity and understanding
    user interaction patterns.

    Args:
        events: List of rrweb events to process
        time_delta_ms: Maximum time gap between events in same cluster (milliseconds)
        dist_delta_px: Maximum Euclidean distance between events in same cluster (pixels)

    Returns:
        List of MouseCluster objects in order of input events, each containing:
        - start_ts and end_ts: Time boundaries of the cluster
        - points: Ordered list of {x, y, ts} dictionaries
        - duration_ms: Total time span of the cluster
        - point_count: Number of mouse positions in the cluster

    Note:
        Only events with type == 3 and data.source == 1 are considered mousemove events.
        Empty input or no mousemove events will return an empty list.
    """
    mousemove_events = _filter_mousemove_events(events)

    if not mousemove_events:
        return []

    clusters = []
    current_cluster_points = []
    last_point = None

    for event in mousemove_events:
        current_point = _extract_point_from_event(event)

        should_start_new_cluster = _should_start_new_cluster(
            last_point, current_point, time_delta_ms, dist_delta_px
        )

        if should_start_new_cluster and current_cluster_points:
            cluster = _create_mouse_cluster(current_cluster_points)
            clusters.append(cluster)
            current_cluster_points = []

        current_cluster_points.append(current_point)
        last_point = current_point

    # Add the final cluster if it has points
    if current_cluster_points:
        cluster = _create_mouse_cluster(current_cluster_points)
        clusters.append(cluster)

    return clusters


def _filter_mousemove_events(events: List[dict]) -> List[dict]:
    """
    Filter events to only include mousemove events.

    Args:
        events: List of rrweb events to filter

    Returns:
        List of events where type == 3 and data.source == 1
    """
    return [
        event
        for event in events
        if event.get("type") == 3 and event.get("data", {}).get("source") == 1
    ]


def _extract_point_from_event(event: dict) -> dict:
    """
    Extract mouse position and timestamp from an rrweb event.

    Args:
        event: rrweb mousemove event

    Returns:
        Dictionary with x, y, and ts keys
    """
    data = event.get("data", {})
    timestamp = event.get("timestamp", 0)
    x = data.get("x", 0)
    y = data.get("y", 0)

    return {"x": x, "y": y, "ts": timestamp}


def _should_start_new_cluster(
    last_point: dict, current_point: dict, time_delta_ms: int, dist_delta_px: int
) -> bool:
    """
    Determine if a new cluster should be started based on time and distance thresholds.

    Args:
        last_point: Previous mouse position point (or None if first point)
        current_point: Current mouse position point
        time_delta_ms: Maximum time gap threshold
        dist_delta_px: Maximum distance threshold

    Returns:
        True if a new cluster should be started, False otherwise
    """
    if last_point is None:
        return False

    time_diff = current_point["ts"] - last_point["ts"]
    distance = _calculate_euclidean_distance(last_point, current_point)

    return time_diff > time_delta_ms or distance > dist_delta_px


def _calculate_euclidean_distance(point1: dict, point2: dict) -> float:
    """
    Calculate Euclidean distance between two points.

    Args:
        point1: Dictionary with x and y keys
        point2: Dictionary with x and y keys

    Returns:
        Euclidean distance between the points
    """
    dx = point2["x"] - point1["x"]
    dy = point2["y"] - point1["y"]
    return math.sqrt(dx * dx + dy * dy)


def _create_mouse_cluster(points: List[dict]) -> MouseCluster:
    """
    Create a MouseCluster object from a list of mouse position points.

    Args:
        points: List of dictionaries with x, y, ts keys

    Returns:
        MouseCluster object with computed metrics
    """
    if not points:
        raise ValueError("Cannot create cluster from empty points list")

    start_ts = points[0]["ts"]
    end_ts = points[-1]["ts"]
    duration_ms = end_ts - start_ts
    point_count = len(points)

    return MouseCluster(
        start_ts=start_ts,
        end_ts=end_ts,
        points=points,
        duration_ms=duration_ms,
        point_count=point_count,
    )
