"""
Configuration constants and extensibility hooks for the Session Chunking & Feature Extraction module.

This module defines default parameters used throughout the feature extraction pipeline,
allowing for easy customization of thresholds and behaviors without modifying core logic.
All extractor functions accept optional parameter overrides that default to these values.

Default Parameters:
    DEFAULT_TIME_DELTA_MS: Maximum time gap for mouse trajectory clustering (100ms)
    DEFAULT_DIST_DELTA_PX: Maximum distance for mouse trajectory clustering (50px)
    DEFAULT_SCROLL_REACTION_MS: Maximum time window for scroll→mutation patterns (2000ms)
    DEFAULT_MAX_REACTION_MS: Maximum time window for interaction→mutation reactions (10000ms)

Extensibility:
    Custom formatters and comparators can be passed to various functions to modify
    their behavior without changing the core algorithms.
"""

# Mouse trajectory clustering thresholds
DEFAULT_TIME_DELTA_MS = 100
DEFAULT_DIST_DELTA_PX = 50

# Scroll pattern detection threshold
DEFAULT_SCROLL_REACTION_MS = 2000

# Reaction delay detection threshold
DEFAULT_MAX_REACTION_MS = 10000


def default_dom_path_formatter(path_parts):
    """
    Default DOM path formatter that joins path parts with ' > '.

    Args:
        path_parts: List of path segment strings

    Returns:
        String representing the DOM path
    """
    return " > ".join(path_parts)


def default_distance_comparator(point1, point2):
    """
    Default Euclidean distance comparator for mouse trajectory clustering.

    Args:
        point1: Dictionary with x and y keys
        point2: Dictionary with x and y keys

    Returns:
        Float representing the Euclidean distance between points
    """
    import math

    dx = point2["x"] - point1["x"]
    dy = point2["y"] - point1["y"]
    return math.sqrt(dx * dx + dy * dy)
