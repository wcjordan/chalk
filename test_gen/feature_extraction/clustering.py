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
        List of MouseCluster objects in chronological order, each containing:
        - start_ts and end_ts: Time boundaries of the cluster
        - points: Ordered list of {x, y, ts} dictionaries
        - duration_ms: Total time span of the cluster
        - point_count: Number of mouse positions in the cluster

    Note:
        Only events with type == 3 and data.source == 1 are considered mousemove events.
        Empty input or no mousemove events will return an empty list.
    """
    # Filter for mousemove events only
    mousemove_events = [
        event
        for event in events
        if event.get("type") == 3 and event.get("data", {}).get("source") == 1
    ]

    if not mousemove_events:
        return []

    clusters = []
    current_cluster_points = []
    last_point = None

    for event in mousemove_events:
        data = event.get("data", {})
        timestamp = event.get("timestamp", 0)
        x = data.get("x", 0)
        y = data.get("y", 0)

        current_point = {"x": x, "y": y, "ts": timestamp}

        # Check if we should start a new cluster
        should_start_new_cluster = False

        if last_point is not None:
            # Calculate time difference
            time_diff = timestamp - last_point["ts"]

            # Calculate Euclidean distance
            dx = x - last_point["x"]
            dy = y - last_point["y"]
            distance = math.sqrt(dx * dx + dy * dy)

            # Start new cluster if either threshold is exceeded
            if time_diff > time_delta_ms or distance > dist_delta_px:
                should_start_new_cluster = True

        # If we need to start a new cluster and have points in current cluster
        if should_start_new_cluster and current_cluster_points:
            cluster = _create_mouse_cluster(current_cluster_points)
            clusters.append(cluster)
            current_cluster_points = []

        # Add current point to the cluster
        current_cluster_points.append(current_point)
        last_point = current_point

    # Add the final cluster if it has points
    if current_cluster_points:
        cluster = _create_mouse_cluster(current_cluster_points)
        clusters.append(cluster)

    return clusters


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
