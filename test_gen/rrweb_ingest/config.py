"""
Configuration settings for rrweb ingestion pipeline.

This module defines default values for all configurable parameters used throughout
the ingestion pipeline. These defaults can be overridden by modifying the values in this module.

Configuration Categories:
- Chunking thresholds: Control when new chunks are created
- Noise filtering: Control what events are considered low-signal
- Extensibility: Support for custom filtering logic

Usage Examples:
    # Use default values
    from rrweb_ingest.config import MAX_GAP_MS
"""

# Noise Filtering Configuration
# =============================

# Minimum scroll distance in pixels to be considered meaningful.
# Scrolls below this threshold are typically considered noise
# (accidental micro-scrolls, scroll wheel sensitivity, etc.).
MICRO_SCROLL_THRESHOLD = 20

# DOM Mutation Filtering
# ======================

# Whether to filter empty DOM mutations (no adds, removes, texts, or attributes)
FILTER_EMPTY_MUTATIONS = True

# Whether to filter single style-only attribute changes as trivial
FILTER_STYLE_ONLY_MUTATIONS = True

# Input Event Filtering
# ====================

# Whether to filter input events that don't have corresponding blur/submit
# within the same chunk (incomplete inputs are often noise)
FILTER_INCOMPLETE_INPUTS = False  # Not yet implemented

# Configuration Validation
# ========================


def validate_config():
    """
    Validate that all configuration values are within reasonable ranges.

    Raises:
        ValueError: If any configuration value is invalid
    """
    if MICRO_SCROLL_THRESHOLD < 0:
        raise ValueError("MICRO_SCROLL_THRESHOLD must be non-negative")


# Validate configuration on import
validate_config()
