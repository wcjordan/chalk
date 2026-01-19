"""
Configuration constants and extensibility hooks.

This module defines default parameters used throughout the feature extraction pipeline,
allowing for easy customization of behaviors without modifying core logic.
"""


def default_dom_path_formatter(path_parts):
    """
    Default DOM path formatter that joins path parts with ' > '.

    Args:
        path_parts: List of path segment strings

    Returns:
        String representing the DOM path
    """
    return " > ".join(path_parts)
