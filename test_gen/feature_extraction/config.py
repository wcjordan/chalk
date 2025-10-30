"""
Configuration constants and extensibility hooks for the Session Chunking & Feature Extraction module.

This module defines default parameters used throughout the feature extraction pipeline,
allowing for easy customization of thresholds and behaviors without modifying core logic.
All extractor functions accept optional parameter overrides that default to these values.

Default Parameters:
    DEFAULT_SCROLL_REACTION_MS: Maximum time window for scroll→mutation patterns (2000ms)

Extensibility:
    Custom formatters and comparators can be passed to various functions to modify
    their behavior without changing the core algorithms.
"""

# Scroll pattern detection threshold
DEFAULT_SCROLL_REACTION_MS = 2000


def default_dom_path_formatter(path_parts):
    """
    Default DOM path formatter that joins path parts with ' > '.

    Args:
        path_parts: List of path segment strings

    Returns:
        String representing the DOM path
    """
    return " > ".join(path_parts)
