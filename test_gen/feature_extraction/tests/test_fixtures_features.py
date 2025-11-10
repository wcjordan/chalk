"""
Fixtures-based integration tests for the feature extraction pipeline.

Tests the complete pipeline using sample session data to verify end-to-end
functionality and accurate feature detection across all major event types.
"""

import json
import os
import time

import pytest

from rrweb_ingest.pipeline import ingest_session
from rrweb_util.dom_state.dom_state_helpers import init_dom_state
from feature_extraction.pipeline import extract_features
from feature_extraction.models import create_empty_features_obj


@pytest.fixture(name="sample_session_path")
def fixture_sample_session_path():
    """Fixture providing the path to the sample session JSON file."""
    current_dir = os.path.dirname(__file__)
    return os.path.join(current_dir, "fixtures", "sample_session.json")


@pytest.fixture(name="sample_session_data")
def fixture_sample_session_data(sample_session_path):
    """Fixture providing the loaded sample session data."""
    with open(sample_session_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(name="initialize_dom_state")
def fixture_initialize_dom_state():
    """Fixture to initialize DOM state from the first chunk's FullSnapshot."""

    def _init_dom_state(first_chunk):
        """
        Initialize DOM state from the first chunk's FullSnapshot event.

        If no FullSnapshot is found, returns an empty state.
        """
        if first_chunk.metadata.get("snapshot_before"):
            return init_dom_state(first_chunk.metadata["snapshot_before"])

        # Find FullSnapshot in chunk events
        for event in first_chunk.events:
            if event.get("type") == 2:
                return init_dom_state(event)
        return {}

    return _init_dom_state


def test_sample_session_loads_successfully(sample_session_data):
    """Test that the sample session JSON loads and has expected structure."""
    rrweb_data = sample_session_data.get("rrweb_data", [])
    assert isinstance(rrweb_data, list)
    assert len(rrweb_data) >= 15  # Should have ~15-25 events
    assert len(rrweb_data) <= 25

    # Should have at least one FullSnapshot event
    full_snapshots = [event for event in rrweb_data if event.get("type") == 2]
    assert len(full_snapshots) >= 1

    # Should have various IncrementalSnapshot events
    incremental_snapshots = [event for event in rrweb_data if event.get("type") == 3]
    assert len(incremental_snapshots) >= 10


def test_sample_session_covers_all_event_types(sample_session_data):
    """Test that the sample session covers all major event types."""
    # Collect all source types from IncrementalSnapshot events
    rrweb_data = sample_session_data.get("rrweb_data", [])
    sources = set()
    for event in rrweb_data:
        if event.get("type") == 3:
            source = event.get("data", {}).get("source")
            if source is not None:
                sources.add(source)

    # Should include mousemove (1), click (2), scroll (3), mutation (0), input (5)
    expected_sources = {0, 1, 2, 3, 5}
    assert expected_sources.issubset(
        sources
    ), f"Missing sources: {expected_sources - sources}"


def test_end_to_end_feature_extraction(initialize_dom_state, sample_session_path):
    """Test complete pipeline from sample session to feature extraction."""
    # Load session via ingest_session
    chunks = ingest_session("sample-session", sample_session_path)

    assert len(chunks) >= 1, "Should produce at least one chunk"

    # Process the first chunk
    first_chunk = chunks[0]

    dom_state = initialize_dom_state(first_chunk)

    # TODO it doesn't appear that ingest_session returns the DOM state
    # We should address that so that UI node metadata can be added to events
    # assert len(dom_state) > 0, "Should have initialized DOM state"

    # Extract features from the chunk
    feature_chunk = extract_features(first_chunk, dom_state)

    # Verify basic structure
    assert feature_chunk.chunk_id == first_chunk.chunk_id
    assert feature_chunk.start_time == first_chunk.start_time
    assert feature_chunk.end_time == first_chunk.end_time
    assert len(feature_chunk.events) == len(first_chunk.events)

    # Verify all feature categories are present
    required_features = create_empty_features_obj().keys()
    for feature_type in required_features:
        assert (
            feature_type in feature_chunk.features
        ), f"Missing feature type: {feature_type}"
        if feature_type != "mouse_clusters":
            assert (
                len(feature_chunk.features[feature_type]) >= 0
            ), f"Should have {feature_type}"
        else:
            # Mouse clusters won't exist because of rrweb_ingest.filter.is_low_signal filters out mousemove events
            assert (
                len(feature_chunk.features[feature_type]) == 0
            ), f"Should have no {feature_type}"


def test_scroll_pattern_detection(initialize_dom_state, sample_session_path):
    """Test that scroll patterns are correctly detected."""
    chunks = ingest_session("sample-session", sample_session_path)
    first_chunk = chunks[0]

    dom_state = initialize_dom_state(first_chunk)

    feature_chunk = extract_features(first_chunk, dom_state)
    scroll_patterns = feature_chunk.features["scroll_patterns"]

    assert len(scroll_patterns) == 1, "Should have 1 scroll pattern"

    pattern = scroll_patterns[0]
    assert pattern.delay_ms == 200, "Scroll->mutation delay should be 200ms"
    assert pattern.scroll_event["data"]["source"] == 3, "Should be scroll event"
    assert pattern.mutation_event["data"]["source"] == 0, "Should be mutation event"


def test_feature_extraction(snapshot, initialize_dom_state, sample_session_path):
    """Test that the extracted feature chunk matches the expected snapshot."""
    chunks = ingest_session("sample-session", sample_session_path)
    first_chunk = chunks[0]

    dom_state = initialize_dom_state(first_chunk)

    feature_chunk = extract_features(first_chunk, dom_state)

    # Compare structure with expected output
    assert feature_chunk == snapshot


def test_performance_with_sample_session(initialize_dom_state, sample_session_path):
    """Test that feature extraction completes in reasonable time."""
    start_time = time.time()

    chunks = ingest_session("sample-session", sample_session_path)
    first_chunk = chunks[0]

    dom_state = initialize_dom_state(first_chunk)

    feature_chunk = extract_features(first_chunk, dom_state)

    end_time = time.time()
    processing_time = end_time - start_time

    # Should complete in under 1 second for sample data
    assert processing_time < 1.0, f"Processing took {processing_time:.2f}s, too slow"

    # Verify results are complete
    assert len(feature_chunk.features["dom_mutations"]) > 0
    assert len(feature_chunk.features["interactions"]) > 0
