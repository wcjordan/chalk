"""
Unit tests for configuration and extensibility features.

Tests the configuration module exports and custom extensibility hooks
like DOM path formatters and distance comparators using mock patches.
"""

from feature_extraction import config


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
