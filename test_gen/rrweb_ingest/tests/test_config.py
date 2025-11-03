"""
Unit tests for the configuration module.

Tests that the config module exposes correct default values and validates
configuration parameters properly.
"""

import pytest
from rrweb_ingest import config


class TestConfigDefaults:
    """Test cases for configuration default values."""

    def test_filtering_defaults(self):
        """Test that filtering configuration has expected default values."""
        assert config.MICRO_SCROLL_THRESHOLD == 20
        assert config.FILTER_EMPTY_MUTATIONS is True
        assert config.FILTER_STYLE_ONLY_MUTATIONS is True
        assert config.FILTER_INCOMPLETE_INPUTS is False

    def test_extensibility_defaults(self):
        """Test that extensibility configuration has expected default values."""
        assert not config.DEFAULT_CUSTOM_FILTERS
        assert isinstance(config.DEFAULT_CUSTOM_FILTERS, list)

    def test_all_defaults_are_reasonable(self):
        """Test that all default values are within reasonable ranges."""
        # Threshold should be non-negative
        assert config.MICRO_SCROLL_THRESHOLD >= 0

        # Boolean flags should be boolean
        assert isinstance(config.FILTER_EMPTY_MUTATIONS, bool)
        assert isinstance(config.FILTER_STYLE_ONLY_MUTATIONS, bool)
        assert isinstance(config.FILTER_INCOMPLETE_INPUTS, bool)


class TestConfigValidation:
    """Test cases for configuration validation."""

    def test_validate_config_with_defaults(self):
        """Test that validate_config passes with default values."""
        # Should not raise any exceptions
        config.validate_config()

    def test_validate_config_with_invalid_micro_scroll_threshold(self):
        """Test that validate_config fails with invalid MICRO_SCROLL_THRESHOLD."""
        original_value = config.MICRO_SCROLL_THRESHOLD
        try:
            config.MICRO_SCROLL_THRESHOLD = -1
            with pytest.raises(
                ValueError, match="MICRO_SCROLL_THRESHOLD must be non-negative"
            ):
                config.validate_config()

            config.MICRO_SCROLL_THRESHOLD = -50
            with pytest.raises(
                ValueError, match="MICRO_SCROLL_THRESHOLD must be non-negative"
            ):
                config.validate_config()
        finally:
            config.MICRO_SCROLL_THRESHOLD = original_value

    def test_config_types(self):
        """Test that configuration values have expected types."""
        assert isinstance(config.MICRO_SCROLL_THRESHOLD, int)
        assert isinstance(config.DEFAULT_CUSTOM_FILTERS, list)
