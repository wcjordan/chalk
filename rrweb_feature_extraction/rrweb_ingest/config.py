"""
Configuration settings for rrweb ingestion pipeline.

This module defines default values for all configurable parameters used throughout
the ingestion pipeline. These defaults can be overridden by passing parameters
to individual functions or by modifying the values in this module.

Configuration Categories:
- Chunking thresholds: Control when new chunks are created
- Noise filtering: Control what events are considered low-signal
- Extensibility: Support for custom filtering logic

Usage Examples:
    # Use default values
    from rrweb_ingest.config import MAX_GAP_MS
    
    # Override in function calls
    chunks = segment_into_chunks(interactions, snapshots, max_gap_ms=5000)
    
    # Custom noise filter
    def custom_filter(event):
        return event.get("data", {}).get("source") == 99
    
    cleaned = clean_chunk(events, custom_filters=[custom_filter])
"""

# Chunking Configuration
# ======================

# Maximum time gap in milliseconds between consecutive interactions
# before starting a new chunk. Larger gaps typically indicate separate
# user workflows or sessions.
MAX_GAP_MS = 10_000

# Maximum number of events per chunk before forcing a split.
# Prevents chunks from becoming too large for efficient processing.
MAX_EVENTS = 1000

# Maximum duration in milliseconds for a single chunk.
# Ensures chunks represent reasonable time windows for analysis.
MAX_DURATION_MS = 30_000

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

# Extensibility Configuration
# ===========================

# Default custom filter functions (empty by default)
# Users can add custom predicates here or pass them to functions
DEFAULT_CUSTOM_FILTERS = []

# Configuration Validation
# ========================

def validate_config():
    """
    Validate that all configuration values are within reasonable ranges.
    
    Raises:
        ValueError: If any configuration value is invalid
    """
    if MAX_GAP_MS <= 0:
        raise ValueError("MAX_GAP_MS must be positive")
    
    if MAX_EVENTS <= 0:
        raise ValueError("MAX_EVENTS must be positive")
    
    if MAX_DURATION_MS <= 0:
        raise ValueError("MAX_DURATION_MS must be positive")
    
    if MICRO_SCROLL_THRESHOLD < 0:
        raise ValueError("MICRO_SCROLL_THRESHOLD must be non-negative")


# Validate configuration on import
validate_config()
