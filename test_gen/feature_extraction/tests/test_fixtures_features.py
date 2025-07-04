"""
Fixtures-based integration tests for the feature extraction pipeline.

Tests the complete pipeline using sample session data to verify end-to-end
functionality and accurate feature detection across all major event types.
"""

import json
import os
import pytest
from rrweb_ingest.pipeline import ingest_session
from feature_extraction.dom_state import init_dom_state
from feature_extraction.pipeline import extract_features


@pytest.fixture(name="sample_session_path")
def fixture_sample_session_path():
    """Fixture providing the path to the sample session JSON file."""
    current_dir = os.path.dirname(__file__)
    return os.path.join(current_dir, "fixtures", "sample_session.json")


@pytest.fixture(name="sample_featurechunk_path")
def fixture_sample_featurechunk_path():
    """Fixture providing the path to the expected feature chunk JSON file."""
    current_dir = os.path.dirname(__file__)
    return os.path.join(current_dir, "fixtures", "sample_featurechunk.json")


@pytest.fixture(name="sample_session_data")
def fixture_sample_session_data(sample_session_path):
    """Fixture providing the loaded sample session data."""
    with open(sample_session_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(name="expected_featurechunk")
def fixture_expected_featurechunk(sample_featurechunk_path):
    """Fixture providing the expected feature chunk structure."""
    with open(sample_featurechunk_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_sample_session_loads_successfully(sample_session_data):
    """Test that the sample session JSON loads and has expected structure."""
    assert isinstance(sample_session_data, list)
    assert len(sample_session_data) >= 15  # Should have ~15-25 events
    assert len(sample_session_data) <= 25

    # Should have at least one FullSnapshot event
    full_snapshots = [event for event in sample_session_data if event.get("type") == 2]
    assert len(full_snapshots) >= 1

    # Should have various IncrementalSnapshot events
    incremental_snapshots = [
        event for event in sample_session_data if event.get("type") == 3
    ]
    assert len(incremental_snapshots) >= 10


def test_sample_session_covers_all_event_types(sample_session_data):
    """Test that the sample session covers all major event types."""
    # Collect all source types from IncrementalSnapshot events
    sources = set()
    for event in sample_session_data:
        if event.get("type") == 3:
            source = event.get("data", {}).get("source")
            if source is not None:
                sources.add(source)

    # Should include mousemove (1), click (2), scroll (3), mutation (0), input (5)
    expected_sources = {0, 1, 2, 3, 5}
    assert expected_sources.issubset(
        sources
    ), f"Missing sources: {expected_sources - sources}"


def test_end_to_end_feature_extraction(sample_session_path):
    """Test complete pipeline from sample session to feature extraction."""
    # Load session via ingest_session
    chunks = ingest_session("sample-session", sample_session_path)

    assert len(chunks) >= 1, "Should produce at least one chunk"

    # Process the first chunk
    first_chunk = chunks[0]

    # Initialize DOM state from FullSnapshot if available
    dom_state = {}
    if first_chunk.metadata.get("snapshot_before"):
        dom_state = init_dom_state(first_chunk.metadata["snapshot_before"])
    else:
        # Find FullSnapshot in chunk events
        for event in first_chunk.events:
            if event.get("type") == 2:
                dom_state = init_dom_state(event)
                break

    assert len(dom_state) > 0, "Should have initialized DOM state"

    # Extract features from the chunk
    feature_chunk = extract_features(first_chunk, dom_state)

    # Verify basic structure
    assert feature_chunk.chunk_id == first_chunk.chunk_id
    assert feature_chunk.start_time == first_chunk.start_time
    assert feature_chunk.end_time == first_chunk.end_time
    assert len(feature_chunk.events) == len(first_chunk.events)

    # Verify all feature categories are present
    required_features = [
        "dom_mutations",
        "interactions",
        "inter_event_delays",
        "reaction_delays",
        "ui_nodes",
        "mouse_clusters",
        "scroll_patterns",
    ]

    for feature_type in required_features:
        assert (
            feature_type in feature_chunk.features
        ), f"Missing feature type: {feature_type}"

    # Verify feature lists are non-empty where expected
    assert len(feature_chunk.features["dom_mutations"]) > 0, "Should have DOM mutations"
    assert (
        len(feature_chunk.features["interactions"]) > 0
    ), "Should have user interactions"
    assert (
        len(feature_chunk.features["inter_event_delays"]) > 0
    ), "Should have inter-event delays"
    assert (
        len(feature_chunk.features["reaction_delays"]) > 0
    ), "Should have reaction delays"
    assert len(feature_chunk.features["ui_nodes"]) > 0, "Should have UI metadata"
    assert (
        len(feature_chunk.features["mouse_clusters"]) > 0
    ), "Should have mouse clusters"
    assert (
        len(feature_chunk.features["scroll_patterns"]) > 0
    ), "Should have scroll patterns"


def test_feature_extraction_accuracy(sample_session_path):
    """Test that feature extraction produces accurate results for known sample data."""
    chunks = ingest_session("sample-session", sample_session_path)
    first_chunk = chunks[0]

    # Initialize DOM state
    dom_state = {}
    for event in first_chunk.events:
        if event.get("type") == 2:
            dom_state = init_dom_state(event)
            break

    feature_chunk = extract_features(first_chunk, dom_state)

    # Verify specific feature counts based on sample data
    # Sample session should have:
    # - 5 DOM mutations (2 attribute, 1 text, 1 add, 1 attribute)
    # - 5 user interactions (2 clicks, 1 input, 1 scroll, 1 click)
    # - 3 mouse clusters
    # - 1 scroll pattern

    assert (
        len(feature_chunk.features["dom_mutations"]) == 5
    ), f"Expected 5 DOM mutations, got {len(feature_chunk.features['dom_mutations'])}"

    assert (
        len(feature_chunk.features["interactions"]) == 5
    ), f"Expected 5 interactions, got {len(feature_chunk.features['interactions'])}"

    assert (
        len(feature_chunk.features["mouse_clusters"]) == 3
    ), f"Expected 3 mouse clusters, got {len(feature_chunk.features['mouse_clusters'])}"

    assert (
        len(feature_chunk.features["scroll_patterns"]) == 1
    ), f"Expected 1 scroll pattern, got {len(feature_chunk.features['scroll_patterns'])}"

    # Verify interaction types
    interaction_types = [i.action for i in feature_chunk.features["interactions"]]
    assert interaction_types.count("click") == 3, "Should have 3 click interactions"
    assert interaction_types.count("input") == 1, "Should have 1 input interaction"
    assert interaction_types.count("scroll") == 1, "Should have 1 scroll interaction"

    # Verify mutation types
    mutation_types = [m.mutation_type for m in feature_chunk.features["dom_mutations"]]
    assert mutation_types.count("attribute") == 3, "Should have 3 attribute mutations"
    assert mutation_types.count("text") == 1, "Should have 1 text mutation"
    assert mutation_types.count("add") == 1, "Should have 1 add mutation"


def test_ui_metadata_resolution(sample_session_path):
    """Test that UI metadata is correctly resolved for sample session nodes."""
    chunks = ingest_session("sample-session", sample_session_path)
    first_chunk = chunks[0]

    # Initialize DOM state
    dom_state = {}
    for event in first_chunk.events:
        if event.get("type") == 2:
            dom_state = init_dom_state(event)
            break

    feature_chunk = extract_features(first_chunk, dom_state)
    ui_nodes = feature_chunk.features["ui_nodes"]

    # Should have metadata for referenced nodes
    assert len(ui_nodes) >= 4, "Should have metadata for at least 4 nodes"

    # Check specific nodes from sample data
    # Node 9: email input
    if 9 in ui_nodes:
        email_node = ui_nodes[9]
        assert email_node["tag"] == "input"
        assert email_node["aria_label"] == "Email Address"
        assert email_node["data_testid"] == "email-input"
        assert "email" in email_node["dom_path"]

    # Node 10: submit button
    if 10 in ui_nodes:
        submit_node = ui_nodes[10]
        assert submit_node["tag"] == "button"
        assert submit_node["aria_label"] == "Submit Form"
        assert submit_node["data_testid"] == "submit-btn"
        assert submit_node["text"] == "Submit"


def test_timing_accuracy(sample_session_path):
    """Test that timing delays are computed accurately."""
    chunks = ingest_session("sample-session", sample_session_path)
    first_chunk = chunks[0]

    # Initialize DOM state
    dom_state = {}
    for event in first_chunk.events:
        if event.get("type") == 2:
            dom_state = init_dom_state(event)
            break

    feature_chunk = extract_features(first_chunk, dom_state)

    # Check inter-event delays
    inter_delays = feature_chunk.features["inter_event_delays"]
    assert len(inter_delays) >= 15, "Should have delays for consecutive events"

    # Check reaction delays
    reaction_delays = feature_chunk.features["reaction_delays"]
    assert len(reaction_delays) >= 3, "Should have reaction delays"

    # Verify reaction delay timing (input->mutation should be 50ms)
    input_reaction = None
    for delay in reaction_delays:
        if delay.delta_ms == 50:  # Input to mutation delay
            input_reaction = delay
            break

    assert input_reaction is not None, "Should find input->mutation reaction delay"
    assert input_reaction.delta_ms == 50


def test_mouse_clustering_accuracy(sample_session_path):
    """Test that mouse clustering produces expected results."""
    chunks = ingest_session("sample-session", sample_session_path)
    first_chunk = chunks[0]

    # Initialize DOM state
    dom_state = {}
    for event in first_chunk.events:
        if event.get("type") == 2:
            dom_state = init_dom_state(event)
            break

    feature_chunk = extract_features(first_chunk, dom_state)
    mouse_clusters = feature_chunk.features["mouse_clusters"]

    assert len(mouse_clusters) == 3, "Should have 3 mouse clusters"

    # Check first cluster (3 points over 100ms)
    first_cluster = mouse_clusters[0]
    assert first_cluster.point_count == 3
    assert first_cluster.duration_ms == 100
    assert len(first_cluster.points) == 3

    # Verify point coordinates
    assert first_cluster.points[0]["x"] == 100
    assert first_cluster.points[0]["y"] == 150
    assert first_cluster.points[2]["x"] == 140
    assert first_cluster.points[2]["y"] == 170


def test_scroll_pattern_detection(sample_session_path):
    """Test that scroll patterns are correctly detected."""
    chunks = ingest_session("sample-session", sample_session_path)
    first_chunk = chunks[0]

    # Initialize DOM state
    dom_state = {}
    for event in first_chunk.events:
        if event.get("type") == 2:
            dom_state = init_dom_state(event)
            break

    feature_chunk = extract_features(first_chunk, dom_state)
    scroll_patterns = feature_chunk.features["scroll_patterns"]

    assert len(scroll_patterns) == 1, "Should have 1 scroll pattern"

    pattern = scroll_patterns[0]
    assert pattern.delay_ms == 200, "Scroll->mutation delay should be 200ms"
    assert pattern.scroll_event["data"]["source"] == 3, "Should be scroll event"
    assert pattern.mutation_event["data"]["source"] == 0, "Should be mutation event"


def test_feature_chunk_schema_validation(sample_session_path, expected_featurechunk):
    """Test that the extracted feature chunk matches the expected schema."""
    chunks = ingest_session("sample-session", sample_session_path)
    first_chunk = chunks[0]

    # Initialize DOM state
    dom_state = {}
    for event in first_chunk.events:
        if event.get("type") == 2:
            dom_state = init_dom_state(event)
            break

    feature_chunk = extract_features(first_chunk, dom_state)

    # Compare structure with expected output
    expected = expected_featurechunk

    # Verify feature counts match expectations
    for feature_type in expected["features"]:
        actual_count = len(feature_chunk.features[feature_type])
        expected_count = len(expected["features"][feature_type])
        assert (
            actual_count == expected_count
        ), f"Feature {feature_type}: expected {expected_count}, got {actual_count}"

    # Verify specific mutation details
    actual_mutations = feature_chunk.features["dom_mutations"]
    expected_mutations = expected["features"]["dom_mutations"]

    for i, expected_mutation in enumerate(expected_mutations):
        actual_mutation = actual_mutations[i]
        assert actual_mutation.mutation_type == expected_mutation["mutation_type"]
        assert actual_mutation.target_id == expected_mutation["target_id"]
        assert actual_mutation.timestamp == expected_mutation["timestamp"]


def test_error_handling_with_malformed_session():
    """Test that the pipeline handles malformed session data gracefully."""
    # Create a minimal malformed session
    malformed_session = [
        {"type": "invalid", "timestamp": 1000},  # Invalid type
        {"timestamp": 2000},  # Missing type
        {"type": 3, "data": {}},  # Missing source
    ]

    # Write to temporary file
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(malformed_session, f)
        temp_path = f.name

    try:
        # Should not crash, but may produce empty chunks
        chunks = ingest_session("malformed-session", temp_path)

        # If chunks are produced, feature extraction should handle them gracefully
        if chunks:
            feature_chunk = extract_features(chunks[0], {})
            assert isinstance(feature_chunk.features, dict)
            assert all(
                isinstance(feature_list, (list, dict))
                for feature_list in feature_chunk.features.values()
            )

    finally:
        # Clean up temporary file
        os.unlink(temp_path)


def test_performance_with_sample_session(sample_session_path):
    """Test that feature extraction completes in reasonable time."""
    import time

    start_time = time.time()

    chunks = ingest_session("sample-session", sample_session_path)
    first_chunk = chunks[0]

    # Initialize DOM state
    dom_state = {}
    for event in first_chunk.events:
        if event.get("type") == 2:
            dom_state = init_dom_state(event)
            break

    feature_chunk = extract_features(first_chunk, dom_state)

    end_time = time.time()
    processing_time = end_time - start_time

    # Should complete in under 1 second for sample data
    assert processing_time < 1.0, f"Processing took {processing_time:.2f}s, too slow"

    # Verify results are complete
    assert len(feature_chunk.features["dom_mutations"]) > 0
    assert len(feature_chunk.features["interactions"]) > 0
