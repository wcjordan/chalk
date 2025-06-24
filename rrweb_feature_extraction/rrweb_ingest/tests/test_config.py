"""
Unit tests for the configuration module.

Tests that the config module exposes correct default values and validates
configuration parameters properly.
"""

import pytest
from rrweb_ingest import config


class TestConfigDefaults:
    """Test cases for configuration default values."""

    def test_chunking_defaults(self):
        """Test that chunking configuration has expected default values."""
        assert config.MAX_GAP_MS == 10_000
        assert config.MAX_EVENTS == 1000
        assert config.MAX_DURATION_MS == 30_000

    def test_filtering_defaults(self):
        """Test that filtering configuration has expected default values."""
        assert config.MICRO_SCROLL_THRESHOLD == 20
        assert config.FILTER_EMPTY_MUTATIONS is True
        assert config.FILTER_STYLE_ONLY_MUTATIONS is True
        assert config.FILTER_INCOMPLETE_INPUTS is False

    def test_extensibility_defaults(self):
        """Test that extensibility configuration has expected default values."""
        assert config.DEFAULT_CUSTOM_FILTERS == []
        assert isinstance(config.DEFAULT_CUSTOM_FILTERS, list)

    def test_all_defaults_are_reasonable(self):
        """Test that all default values are within reasonable ranges."""
        # Chunking values should be positive
        assert config.MAX_GAP_MS > 0
        assert config.MAX_EVENTS > 0
        assert config.MAX_DURATION_MS > 0
        
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

    def test_validate_config_with_invalid_max_gap_ms(self):
        """Test that validate_config fails with invalid MAX_GAP_MS."""
        original_value = config.MAX_GAP_MS
        try:
            config.MAX_GAP_MS = 0
            with pytest.raises(ValueError, match="MAX_GAP_MS must be positive"):
                config.validate_config()
            
            config.MAX_GAP_MS = -1000
            with pytest.raises(ValueError, match="MAX_GAP_MS must be positive"):
                config.validate_config()
        finally:
            config.MAX_GAP_MS = original_value

    def test_validate_config_with_invalid_max_events(self):
        """Test that validate_config fails with invalid MAX_EVENTS."""
        original_value = config.MAX_EVENTS
        try:
            config.MAX_EVENTS = 0
            with pytest.raises(ValueError, match="MAX_EVENTS must be positive"):
                config.validate_config()
            
            config.MAX_EVENTS = -100
            with pytest.raises(ValueError, match="MAX_EVENTS must be positive"):
                config.validate_config()
        finally:
            config.MAX_EVENTS = original_value

    def test_validate_config_with_invalid_max_duration_ms(self):
        """Test that validate_config fails with invalid MAX_DURATION_MS."""
        original_value = config.MAX_DURATION_MS
        try:
            config.MAX_DURATION_MS = 0
            with pytest.raises(ValueError, match="MAX_DURATION_MS must be positive"):
                config.validate_config()
            
            config.MAX_DURATION_MS = -5000
            with pytest.raises(ValueError, match="MAX_DURATION_MS must be positive"):
                config.validate_config()
        finally:
            config.MAX_DURATION_MS = original_value

    def test_validate_config_with_invalid_micro_scroll_threshold(self):
        """Test that validate_config fails with invalid MICRO_SCROLL_THRESHOLD."""
        original_value = config.MICRO_SCROLL_THRESHOLD
        try:
            config.MICRO_SCROLL_THRESHOLD = -1
            with pytest.raises(ValueError, match="MICRO_SCROLL_THRESHOLD must be non-negative"):
                config.validate_config()
            
            config.MICRO_SCROLL_THRESHOLD = -50
            with pytest.raises(ValueError, match="MICRO_SCROLL_THRESHOLD must be non-negative"):
                config.validate_config()
        finally:
            config.MICRO_SCROLL_THRESHOLD = original_value

    def test_config_types(self):
        """Test that configuration values have expected types."""
        assert isinstance(config.MAX_GAP_MS, int)
        assert isinstance(config.MAX_EVENTS, int)
        assert isinstance(config.MAX_DURATION_MS, int)
        assert isinstance(config.MICRO_SCROLL_THRESHOLD, int)
        assert isinstance(config.DEFAULT_CUSTOM_FILTERS, list)
