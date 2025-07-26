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

Configuration:
    Uses DEFAULT_TIME_DELTA_MS and DEFAULT_DIST_DELTA_PX from config module.

Usage:
    clusters = cluster_mouse_trajectories(events)
    for cluster in clusters:
        print(f"Cluster: {cluster.point_count} points over {cluster.duration_ms}ms")
"""

from typing import List
from .models import MouseCluster
from . import config
from rrweb_util import is_mouse_move_event, get_event_timestamp, get_mouse_coordinates


def cluster_mouse_trajectories(
    events: List[dict],
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

        should_start_new_cluster = _should_start_new_cluster(last_point, current_point)

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
    return [event for event in events if is_mouse_move_event(event)]


def _extract_point_from_event(event: dict) -> dict:
    """
    Extract mouse position and timestamp from an rrweb event.

    Args:
        event: rrweb mousemove event

    Returns:
        Dictionary with x, y, and ts keys
    """
    timestamp = get_event_timestamp(event)
    x, y = get_mouse_coordinates(event)
    return {"x": x, "y": y, "ts": timestamp}


def _should_start_new_cluster(
    last_point: dict,
    current_point: dict,
) -> bool:
    """
    Determine if a new cluster should be started based on time and distance thresholds.

    Args:
        last_point: Previous mouse position point (or None if first point)
        current_point: Current mouse position point

    Returns:
        True if a new cluster should be started, False otherwise
    """
    if last_point is None:
        return False

    time_diff = current_point["ts"] - last_point["ts"]
    distance = config.default_distance_comparator(last_point, current_point)

    return (
        time_diff > config.DEFAULT_TIME_DELTA_MS
        or distance > config.DEFAULT_DIST_DELTA_PX
    )


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
