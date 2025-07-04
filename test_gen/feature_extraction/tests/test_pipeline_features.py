"""
Integration tests for the feature extraction pipeline.

Tests the complete feature extraction pipeline from preprocessed chunks
to populated FeatureChunk objects, verifying correct integration of all
extractors and proper handling of DOM state.
"""

import pytest
from rrweb_ingest.models import Chunk
from feature_extraction.pipeline import extract_features
from feature_extraction.dom_state import init_dom_state
from feature_extraction.models import UINode


@pytest.fixture(name="sample_chunk_with_interactions")
def fixture_sample_chunk_with_interactions():
    """Fixture providing a sample Chunk with various interaction and mutation events."""
    events = [
        # FullSnapshot event (for DOM initialization)
        {
            "type": 2,
            "timestamp": 10000,
            "data": {
                "node": {
                    "id": 1,
                    "tagName": "html",
                    "childNodes": [
                        {
                            "id": 2,
                            "tagName": "body",
                            "attributes": {"class": "main"},
                            "childNodes": [
                                {
                                    "id": 3,
                                    "tagName": "button",
                                    "attributes": {
                                        "id": "submit",
                                        "aria-label": "Submit Form",
                                        "data-testid": "submit-btn",
                                    },
                                    "textContent": "Submit",
                                    "childNodes": [],
                                }
                            ],
                        }
                    ],
                }
            },
        },
        # Mouse move events (for clustering)
        {
            "type": 3,
            "timestamp": 10100,
            "data": {"source": 1, "x": 100, "y": 200},
        },
        {
            "type": 3,
            "timestamp": 10150,
            "data": {"source": 1, "x": 110, "y": 210},
        },
        # Click interaction
        {
            "type": 3,
            "timestamp": 10200,
            "data": {"source": 2, "id": 3, "x": 115, "y": 215},
        },
        # DOM mutation (response to click)
        {
            "type": 3,
            "timestamp": 10400,
            "data": {
                "source": 0,
                "attributes": [{"id": 3, "attributes": {"class": "btn-clicked"}}],
            },
        },
        # Scroll event
        {
            "type": 3,
            "timestamp": 10500,
            "data": {"source": 3, "id": 2, "x": 0, "y": 100},
        },
        # Another DOM mutation (response to scroll)
        {
            "type": 3,
            "timestamp": 10700,
            "data": {
                "source": 0,
                "adds": [
                    {
                        "parentId": 2,
                        "node": {
                            "id": 4,
                            "tagName": "div",
                            "attributes": {"class": "lazy-loaded"},
                            "textContent": "Lazy content",
                        },
                    }
                ],
            },
        },
        # Input event
        {
            "type": 3,
            "timestamp": 10800,
            "data": {"source": 5, "id": 4, "text": "user input"},
        },
    ]

    return Chunk(
        chunk_id="test-session-chunk001",
        start_time=10000,
        end_time=10800,
        events=events,
        metadata={"num_events": len(events)},
    )


@pytest.fixture(name="initial_dom_state")
def fixture_initial_dom_state(sample_chunk_with_interactions):
    """Fixture providing initial DOM state from the FullSnapshot event."""
    full_snapshot = sample_chunk_with_interactions.events[0]
    return init_dom_state(full_snapshot)


def test_extract_features_returns_populated_feature_chunk(
    sample_chunk_with_interactions, initial_dom_state
):
    """Test that extract_features returns a FeatureChunk with non-empty feature lists."""
    feature_chunk = extract_features(sample_chunk_with_interactions, initial_dom_state)

    # Verify basic chunk properties are preserved
    assert feature_chunk.chunk_id == "test-session-chunk001"
    assert feature_chunk.start_time == 10000
    assert feature_chunk.end_time == 10800
    assert len(feature_chunk.events) == 8
    assert feature_chunk.metadata["num_events"] == 8

    # Verify all feature categories are present
    assert "dom_mutations" in feature_chunk.features
    assert "interactions" in feature_chunk.features
    assert "delays" in feature_chunk.features
    assert "ui_nodes" in feature_chunk.features
    assert "mouse_clusters" in feature_chunk.features
    assert "scroll_patterns" in feature_chunk.features

    # Verify feature lists are non-empty where expected
    assert len(feature_chunk.features["dom_mutations"]) > 0  # Should have 2 mutations
    assert len(feature_chunk.features["interactions"]) > 0  # Should have 3 interactions
    assert len(feature_chunk.features["delays"]) > 0  # Should have inter-event delays
    assert len(feature_chunk.features["ui_nodes"]) > 0  # Should have metadata for nodes
    assert len(feature_chunk.features["mouse_clusters"]) > 0  # Should have 1 cluster
    assert len(feature_chunk.features["scroll_patterns"]) > 0  # Should have 1 pattern


def test_extract_features_dom_mutations_correct(
    sample_chunk_with_interactions, initial_dom_state
):
    """Test that DOM mutations are extracted correctly."""
    feature_chunk = extract_features(sample_chunk_with_interactions, initial_dom_state)
    dom_mutations = feature_chunk.features["dom_mutations"]

    # Should have 2 mutations: 1 attribute change + 1 node addition
    assert len(dom_mutations) == 2

    # Find the attribute mutation
    attr_mutations = [m for m in dom_mutations if m.mutation_type == "attribute"]
    assert len(attr_mutations) == 1
    attr_mutation = attr_mutations[0]
    assert attr_mutation.target_id == 3
    assert attr_mutation.timestamp == 10400
    assert attr_mutation.details["attributes"]["class"] == "btn-clicked"

    # Find the node addition
    add_mutations = [m for m in dom_mutations if m.mutation_type == "add"]
    assert len(add_mutations) == 1
    add_mutation = add_mutations[0]
    assert add_mutation.target_id == 4
    assert add_mutation.timestamp == 10700
    assert add_mutation.details["tag"] == "div"
    assert add_mutation.details["text"] == "Lazy content"


def test_extract_features_user_interactions_correct(
    sample_chunk_with_interactions, initial_dom_state
):
    """Test that user interactions are extracted correctly."""
    feature_chunk = extract_features(sample_chunk_with_interactions, initial_dom_state)
    interactions = feature_chunk.features["interactions"]

    # Should have 3 interactions: 1 click + 1 scroll + 1 input
    assert len(interactions) == 3

    # Find the click interaction
    clicks = [i for i in interactions if i.action == "click"]
    assert len(clicks) == 1
    click = clicks[0]
    assert click.target_id == 3
    assert click.timestamp == 10200
    assert click.value["x"] == 115
    assert click.value["y"] == 215

    # Find the scroll interaction
    scrolls = [i for i in interactions if i.action == "scroll"]
    assert len(scrolls) == 1
    scroll = scrolls[0]
    assert scroll.target_id == 2
    assert scroll.timestamp == 10500

    # Find the input interaction
    inputs = [i for i in interactions if i.action == "input"]
    assert len(inputs) == 1
    input_interaction = inputs[0]
    assert input_interaction.target_id == 4
    assert input_interaction.timestamp == 10800
    assert input_interaction.value["value"] == "user input"


def test_extract_features_timing_delays_computed(
    sample_chunk_with_interactions, initial_dom_state
):
    """Test that timing delays are computed correctly."""
    feature_chunk = extract_features(sample_chunk_with_interactions, initial_dom_state)
    delays = feature_chunk.features["delays"]

    # Should have inter-event delays (7 for 8 events) plus reaction delays
    assert len(delays) >= 7

    # Check that we have some reaction delays (click->mutation, scroll->mutation)
    reaction_delays = [
        d
        for d in delays
        if d.delta_ms in [200, 200]  # Click->mutation, scroll->mutation
    ]
    assert len(reaction_delays) >= 1


def test_extract_features_ui_metadata_resolved(
    sample_chunk_with_interactions, initial_dom_state
):
    """Test that UI metadata is resolved for referenced nodes."""
    feature_chunk = extract_features(sample_chunk_with_interactions, initial_dom_state)
    ui_nodes = feature_chunk.features["ui_nodes"]

    # Should have metadata for nodes referenced in interactions and mutations
    assert len(ui_nodes) >= 2  # At least nodes 2, 3, and 4

    # Check metadata for the button node (node 3)
    if 3 in ui_nodes:
        button_metadata = ui_nodes[3]
        assert button_metadata["tag"] == "button"
        assert button_metadata["aria_label"] == "Submit Form"
        assert button_metadata["data_testid"] == "submit-btn"
        assert "dom_path" in button_metadata


def test_extract_features_mouse_clusters_created(
    sample_chunk_with_interactions, initial_dom_state
):
    """Test that mouse trajectory clusters are created."""
    feature_chunk = extract_features(sample_chunk_with_interactions, initial_dom_state)
    mouse_clusters = feature_chunk.features["mouse_clusters"]

    # Should have 1 cluster from the 2 mouse move events
    assert len(mouse_clusters) == 1
    cluster = mouse_clusters[0]
    assert cluster.start_ts == 10100
    assert cluster.end_ts == 10150
    assert cluster.point_count == 2


def test_extract_features_scroll_patterns_detected(
    sample_chunk_with_interactions, initial_dom_state
):
    """Test that scroll patterns are detected."""
    feature_chunk = extract_features(sample_chunk_with_interactions, initial_dom_state)
    scroll_patterns = feature_chunk.features["scroll_patterns"]

    # Should have 1 scroll pattern (scroll at 10500 -> mutation at 10700)
    assert len(scroll_patterns) == 1
    pattern = scroll_patterns[0]
    assert pattern.scroll_event["timestamp"] == 10500
    assert pattern.mutation_event["timestamp"] == 10700
    assert pattern.delay_ms == 200


def test_extract_features_timestamps_and_ids_align(
    sample_chunk_with_interactions, initial_dom_state
):
    """Test that all timestamps and IDs align with input events."""
    feature_chunk = extract_features(sample_chunk_with_interactions, initial_dom_state)

    # Collect all timestamps from original events
    original_timestamps = {
        event.get("timestamp") for event in sample_chunk_with_interactions.events
    }

    # Check that mutation timestamps are from original events
    for mutation in feature_chunk.features["dom_mutations"]:
        assert mutation.timestamp in original_timestamps

    # Check that interaction timestamps are from original events
    for interaction in feature_chunk.features["interactions"]:
        assert interaction.timestamp in original_timestamps

    # Check that delay timestamps reference original events
    for delay in feature_chunk.features["delays"]:
        assert delay.from_ts in original_timestamps
        assert delay.to_ts in original_timestamps


def test_extract_features_idempotent_calls(
    sample_chunk_with_interactions, initial_dom_state
):
    """Test that calling extract_features twice yields identical results without side effects."""
    # Make a copy of the initial DOM state for the second call
    dom_state_copy = {
        node_id: UINode(
            id=node.id,
            tag=node.tag,
            attributes=node.attributes.copy(),
            text=node.text,
            parent=node.parent,
        )
        for node_id, node in initial_dom_state.items()
    }

    # First extraction
    feature_chunk1 = extract_features(sample_chunk_with_interactions, initial_dom_state)

    # Second extraction with fresh DOM state
    feature_chunk2 = extract_features(sample_chunk_with_interactions, dom_state_copy)

    # Results should be identical
    assert feature_chunk1.chunk_id == feature_chunk2.chunk_id
    assert feature_chunk1.start_time == feature_chunk2.start_time
    assert feature_chunk1.end_time == feature_chunk2.end_time
    assert len(feature_chunk1.events) == len(feature_chunk2.events)

    # Feature counts should be identical
    assert len(feature_chunk1.features["dom_mutations"]) == len(
        feature_chunk2.features["dom_mutations"]
    )
    assert len(feature_chunk1.features["interactions"]) == len(
        feature_chunk2.features["interactions"]
    )
    assert len(feature_chunk1.features["delays"]) == len(
        feature_chunk2.features["delays"]
    )
    assert len(feature_chunk1.features["ui_nodes"]) == len(
        feature_chunk2.features["ui_nodes"]
    )
    assert len(feature_chunk1.features["mouse_clusters"]) == len(
        feature_chunk2.features["mouse_clusters"]
    )
    assert len(feature_chunk1.features["scroll_patterns"]) == len(
        feature_chunk2.features["scroll_patterns"]
    )


def test_extract_features_handles_empty_chunk():
    """Test that extract_features handles chunks with minimal events gracefully."""
    empty_chunk = Chunk(
        chunk_id="empty-chunk",
        start_time=1000,
        end_time=2000,
        events=[],
        metadata={},
    )

    empty_dom_state = {}

    feature_chunk = extract_features(empty_chunk, empty_dom_state)

    # Should return valid FeatureChunk with empty feature lists
    assert feature_chunk.chunk_id == "empty-chunk"
    assert len(feature_chunk.features["dom_mutations"]) == 0
    assert len(feature_chunk.features["interactions"]) == 0
    assert len(feature_chunk.features["delays"]) == 0
    assert len(feature_chunk.features["ui_nodes"]) == 0
    assert len(feature_chunk.features["mouse_clusters"]) == 0
    assert len(feature_chunk.features["scroll_patterns"]) == 0


def test_extract_features_handles_missing_nodes_gracefully():
    """Test that extract_features handles references to missing DOM nodes gracefully."""
    # Create a chunk with interactions referencing non-existent nodes
    chunk_with_missing_nodes = Chunk(
        chunk_id="missing-nodes-chunk",
        start_time=1000,
        end_time=2000,
        events=[
            {
                "type": 3,
                "timestamp": 1100,
                "data": {
                    "source": 2,
                    "id": 999,
                    "x": 100,
                    "y": 200,
                },  # Non-existent node
            },
            {
                "type": 3,
                "timestamp": 1200,
                "data": {
                    "source": 0,
                    "attributes": [{"id": 888, "attributes": {"class": "test"}}],
                },  # Non-existent node
            },
        ],
        metadata={},
    )

    empty_dom_state = {}

    # Should not raise errors
    feature_chunk = extract_features(chunk_with_missing_nodes, empty_dom_state)

    # Should still extract interactions and mutations
    assert len(feature_chunk.features["interactions"]) == 1
    assert len(feature_chunk.features["dom_mutations"]) == 1

    # But UI metadata should be empty (nodes not found)
    assert len(feature_chunk.features["ui_nodes"]) == 0
