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
