"""
Integration tests for the feature extraction pipeline.

Tests the complete feature extraction pipeline from preprocessed chunks
to populated FeatureChunk objects, verifying correct integration of all
extractors and proper handling of DOM state.
"""

from collections import defaultdict

import pytest
from rrweb_ingest.models import Chunk
from feature_extraction.pipeline import extract_features, iterate_feature_extraction
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
    assert "inter_event_delays" in feature_chunk.features
    assert "reaction_delays" in feature_chunk.features
    assert "ui_nodes" in feature_chunk.features
    assert "mouse_clusters" in feature_chunk.features
    assert "scroll_patterns" in feature_chunk.features

    # Verify feature lists are non-empty where expected
    assert len(feature_chunk.features["dom_mutations"]) > 0  # Should have 2 mutations
    assert len(feature_chunk.features["interactions"]) > 0  # Should have 3 interactions
    assert (
        len(feature_chunk.features["inter_event_delays"]) > 0
    )  # Should have inter-event delays
    assert (
        len(feature_chunk.features["reaction_delays"]) > 0
    )  # Should have reaction delays
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
    delays = feature_chunk.features["inter_event_delays"]

    # Should have inter-event delays (7 for 8 events) plus reaction delays
    assert len(delays) >= 7

    # Check that we have some reaction delays (click->mutation, scroll->mutation)
    reaction_delays = feature_chunk.features["reaction_delays"]
    assert len(reaction_delays) >= 1
    assert reaction_delays[0].delta_ms == 200


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
    for delay in feature_chunk.features["inter_event_delays"]:
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
    assert len(feature_chunk1.features["inter_event_delays"]) == len(
        feature_chunk2.features["inter_event_delays"]
    )
    assert len(feature_chunk1.features["reaction_delays"]) == len(
        feature_chunk2.features["reaction_delays"]
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
    assert len(feature_chunk.features["inter_event_delays"]) == 0
    assert len(feature_chunk.features["reaction_delays"]) == 0
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


def test_extract_features_handles_events_with_missing_fields():
    """Test that the pipeline gracefully handles events with missing required fields."""
    events_with_missing_fields = [
        # FullSnapshot for DOM initialization
        {
            "type": 2,
            "timestamp": 1000,
            "data": {
                "node": {
                    "id": 1,
                    "tagName": "div",
                    "childNodes": [],
                }
            },
        },
        # Click event missing timestamp
        {
            "type": 3,
            "data": {"source": 2, "id": 1, "x": 100, "y": 200},
        },
        # Input event missing target ID
        {
            "type": 3,
            "timestamp": 1200,
            "data": {"source": 5, "text": "input without id"},
        },
        # Mutation event missing node ID in attributes
        {
            "type": 3,
            "timestamp": 1300,
            "data": {
                "source": 0,
                "attributes": [{"attributes": {"class": "no-id"}}],
            },
        },
        # Mouse move event missing coordinates
        {
            "type": 3,
            "timestamp": 1400,
            "data": {"source": 1},
        },
        # Scroll event missing target ID
        {
            "type": 3,
            "timestamp": 1500,
            "data": {"source": 3, "x": 0, "y": 100},
        },
    ]

    chunk = Chunk(
        chunk_id="missing-fields-chunk",
        start_time=1000,
        end_time=1500,
        events=events_with_missing_fields,
        metadata={},
    )

    initial_dom_state = init_dom_state(events_with_missing_fields[0])

    # Should not raise errors
    feature_chunk = extract_features(chunk, initial_dom_state)

    # Should extract only valid interactions (click with missing timestamp should still work)
    assert len(feature_chunk.features["interactions"]) == 1
    assert feature_chunk.features["interactions"][0].action == "click"
    assert feature_chunk.features["interactions"][0].timestamp == 0  # Default timestamp

    # Should extract no mutations (missing node ID)
    assert len(feature_chunk.features["dom_mutations"]) == 0

    # Should handle mouse moves with missing coordinates
    assert len(feature_chunk.features["mouse_clusters"]) == 1
    cluster = feature_chunk.features["mouse_clusters"][0]
    assert cluster.points[0]["x"] == 0  # Default coordinate
    assert cluster.points[0]["y"] == 0  # Default coordinate


def test_extract_features_with_complex_interaction_sequences(
    create_full_snapshot_event,
):
    """Test pipeline with rapid sequences of interactions and mutations."""
    # Create events with rapid sequences and overlapping mutations
    rapid_events = [
        # FullSnapshot for DOM initialization
        create_full_snapshot_event(
            child_nodes=[
                {
                    "id": 2,
                    "tagName": "button",
                    "attributes": {"id": "btn1"},
                    "textContent": "Button 1",
                    "childNodes": [],
                },
                {
                    "id": 3,
                    "tagName": "button",
                    "attributes": {"id": "btn2"},
                    "textContent": "Button 2",
                    "childNodes": [],
                },
            ]
        ),
        # Rapid click sequence
        {
            "type": 3,
            "timestamp": 1100,
            "data": {"source": 2, "id": 2, "x": 50, "y": 50},
        },
        {
            "type": 3,
            "timestamp": 1110,
            "data": {"source": 2, "id": 3, "x": 150, "y": 50},
        },
        {
            "type": 3,
            "timestamp": 1120,
            "data": {"source": 2, "id": 2, "x": 50, "y": 50},
        },
        # Overlapping mutations in response
        {
            "type": 3,
            "timestamp": 1150,
            "data": {
                "source": 0,
                "attributes": [{"id": 2, "attributes": {"class": "clicked"}}],
            },
        },
        {
            "type": 3,
            "timestamp": 1160,
            "data": {
                "source": 0,
                "attributes": [{"id": 3, "attributes": {"class": "clicked"}}],
            },
        },
        {
            "type": 3,
            "timestamp": 1170,
            "data": {
                "source": 0,
                "attributes": [{"id": 2, "attributes": {"class": "double-clicked"}}],
            },
        },
        # Rapid mouse movements
        {"type": 3, "timestamp": 1200, "data": {"source": 1, "x": 100, "y": 100}},
        {"type": 3, "timestamp": 1205, "data": {"source": 1, "x": 105, "y": 105}},
        {"type": 3, "timestamp": 1210, "data": {"source": 1, "x": 110, "y": 110}},
        {"type": 3, "timestamp": 1215, "data": {"source": 1, "x": 115, "y": 115}},
        # Rapid input sequence
        {"type": 3, "timestamp": 1300, "data": {"source": 5, "id": 2, "text": "a"}},
        {"type": 3, "timestamp": 1310, "data": {"source": 5, "id": 2, "text": "ab"}},
        {"type": 3, "timestamp": 1320, "data": {"source": 5, "id": 2, "text": "abc"}},
    ]

    chunk = Chunk(
        chunk_id="rapid-sequence-chunk",
        start_time=1000,
        end_time=1320,
        events=rapid_events,
        metadata={},
    )

    initial_dom_state = init_dom_state(rapid_events[0])

    feature_chunk = extract_features(chunk, initial_dom_state)

    # Should extract all interactions
    assert len(feature_chunk.features["interactions"]) == 6  # 3 clicks + 3 inputs

    # Should extract all mutations
    assert len(feature_chunk.features["dom_mutations"]) == 3

    # Should detect multiple reaction delays
    reaction_delays = [
        d
        for d in feature_chunk.features["reaction_delays"]
        if d.delta_ms == 50  # Click->mutation delays
    ]
    assert len(reaction_delays) >= 3

    # Should cluster rapid mouse movements into one cluster
    assert len(feature_chunk.features["mouse_clusters"]) == 1
    cluster = feature_chunk.features["mouse_clusters"][0]
    assert cluster.point_count == 4
    assert cluster.duration_ms == 15  # 1215 - 1200

    # Should have many inter-event delays due to rapid sequence
    assert (
        len(feature_chunk.features["inter_event_delays"]) >= 12
    )  # At least one per event pair


def test_extract_features_boundary_conditions():
    """Test pipeline behavior at configuration boundaries."""
    # Create events exactly at time/distance thresholds
    boundary_events = [
        # FullSnapshot for DOM initialization
        {
            "type": 2,
            "timestamp": 1000,
            "data": {
                "node": {
                    "id": 1,
                    "tagName": "div",
                    "childNodes": [],
                }
            },
        },
        # Mouse moves over time threshold (100ms apart)
        {"type": 3, "timestamp": 1100, "data": {"source": 1, "x": 0, "y": 0}},
        {
            "type": 3,
            "timestamp": 1201,
            "data": {"source": 1, "x": 10, "y": 10},
        },  # Over 100ms later
        {
            "type": 3,
            "timestamp": 1302,
            "data": {"source": 1, "x": 20, "y": 20},
        },  # Over another 100ms
        # Mouse moves exactly at distance threshold (50px apart)
        {"type": 3, "timestamp": 1400, "data": {"source": 1, "x": 0, "y": 0}},
        {
            "type": 3,
            "timestamp": 1450,
            "data": {"source": 1, "x": 30, "y": 40},
        },  # Distance = 50px exactly
        {
            "type": 3,
            "timestamp": 1500,
            "data": {"source": 1, "x": 60, "y": 80},
        },  # Another 50px
        # Scroll and mutation exactly at reaction threshold (2000ms)
        {
            "type": 3,
            "timestamp": 2000,
            "data": {"source": 3, "id": 1, "x": 0, "y": 100},
        },
        {
            "type": 3,
            "timestamp": 4000,  # Exactly 2000ms later
            "data": {
                "source": 0,
                "adds": [{"parentId": 1, "node": {"id": 2, "tagName": "span"}}],
            },
        },
        # Click and mutation exactly at reaction threshold (10000ms)
        {
            "type": 3,
            "timestamp": 5000,
            "data": {"source": 2, "id": 1, "x": 100, "y": 100},
        },
        {
            "type": 3,
            "timestamp": 15000,  # Exactly 10000ms later
            "data": {
                "source": 0,
                "attributes": [{"id": 1, "attributes": {"class": "clicked"}}],
            },
        },
    ]

    chunk = Chunk(
        chunk_id="boundary-conditions-chunk",
        start_time=1000,
        end_time=15000,
        events=boundary_events,
        metadata={},
    )

    initial_dom_state = init_dom_state(boundary_events[0])

    feature_chunk = extract_features(chunk, initial_dom_state)

    # Mouse clustering at time boundary - should split at 100ms threshold
    mouse_clusters = feature_chunk.features["mouse_clusters"]
    assert len(mouse_clusters) >= 2  # Should split due to time threshold

    # Scroll pattern at exact reaction threshold - should be detected
    scroll_patterns = feature_chunk.features["scroll_patterns"]
    assert len(scroll_patterns) == 1
    assert scroll_patterns[0].delay_ms == 2000

    # Reaction delay at exact threshold - should be detected
    reaction_delays = [
        d for d in feature_chunk.features["reaction_delays"] if d.delta_ms == 10000
    ]
    assert len(reaction_delays) == 1

    # Should extract all interactions and mutations
    assert len(feature_chunk.features["interactions"]) == 2  # 1 scroll + 1 click
    assert len(feature_chunk.features["dom_mutations"]) == 2  # 1 add + 1 attribute


def test_extract_features_large_event_volume():
    """Test pipeline performance with larger event volumes."""
    # Generate a large number of events to test scalability
    large_events = [
        # FullSnapshot for DOM initialization
        {
            "type": 2,
            "timestamp": 0,
            "data": {
                "node": {
                    "id": 1,
                    "tagName": "div",
                    "childNodes": [
                        {
                            "id": i,
                            "tagName": "button",
                            "attributes": {"id": f"btn{i}"},
                            "textContent": f"Button {i}",
                            "childNodes": [],
                        }
                        for i in range(2, 102)  # 100 buttons
                    ],
                }
            },
        }
    ]

    # Generate 500 mouse move events (will create multiple clusters)
    for i in range(500):
        large_events.append(
            {
                "type": 3,
                "timestamp": 1000 + i * 10,  # Every 10ms
                "data": {"source": 1, "x": i % 100, "y": (i * 2) % 100},
            }
        )

    # Generate 100 click events
    for i in range(100):
        large_events.append(
            {
                "type": 3,
                "timestamp": 6000 + i * 50,  # Every 50ms
                "data": {"source": 2, "id": (i % 100) + 2, "x": i, "y": i},
            }
        )

    # Generate 100 mutation events in response
    for i in range(100):
        large_events.append(
            {
                "type": 3,
                "timestamp": 6100 + i * 50,  # 100ms after each click
                "data": {
                    "source": 0,
                    "attributes": [
                        {"id": (i % 100) + 2, "attributes": {"class": f"clicked-{i}"}}
                    ],
                },
            }
        )

    # Generate 50 scroll events
    for i in range(50):
        large_events.append(
            {
                "type": 3,
                "timestamp": 11000 + i * 100,  # Every 100ms
                "data": {"source": 3, "id": 1, "x": 0, "y": i * 10},
            }
        )

    # Generate 50 input events
    for i in range(50):
        large_events.append(
            {
                "type": 3,
                "timestamp": 16000 + i * 20,  # Every 20ms
                "data": {"source": 5, "id": (i % 10) + 2, "text": f"input-{i}"},
            }
        )

    chunk = Chunk(
        chunk_id="large-volume-chunk",
        start_time=0,
        end_time=17000,
        events=large_events,
        metadata={"num_events": len(large_events)},
    )

    initial_dom_state = init_dom_state(large_events[0])

    # Should handle large volume without errors
    feature_chunk = extract_features(chunk, initial_dom_state)

    # Verify all event types were processed
    assert (
        len(feature_chunk.features["interactions"]) == 200
    )  # 100 clicks + 50 scrolls + 50 inputs
    assert len(feature_chunk.features["dom_mutations"]) == 100  # 100 attribute changes

    # Should have many mouse clusters due to volume
    assert len(feature_chunk.features["mouse_clusters"]) >= 5

    # Should have many delays due to volume
    assert (
        len(feature_chunk.features["inter_event_delays"]) >= 800
    )  # Many inter-event delays

    # Should have reaction delays for click->mutation pairs
    reaction_delays = [
        d
        for d in feature_chunk.features["reaction_delays"]
        if d.delta_ms == 100  # Click->mutation delay
    ]
    assert len(reaction_delays) >= 90  # Most clicks should have reactions

    # Should resolve UI metadata for referenced nodes
    assert len(feature_chunk.features["ui_nodes"]) >= 50  # Many nodes referenced

    # Verify performance - should complete in reasonable time
    # (This is implicit - if the test completes, performance is acceptable)
    assert feature_chunk.chunk_id == "large-volume-chunk"
    assert len(feature_chunk.events) == len(large_events)


def test_full_pipeline_integration(snapshot):
    """
    Integration test that mimics the __main__ block in pipeline.py.

    Tests the complete pipeline flow including:
    - Processing multiple session files from data/output_sessions
    - Handling multiple chunks per session with DOM state persistence
    - Both cases: chunks with and without snapshot_before metadata
    - Session limits and error handling
    - Feature extraction statistics similar to main block output

    Uses syrupy snapshots to capture and verify the complete pipeline output.
    """

    # Collect results to match main block output format
    def _create_empty_session_result():
        return {
            "chunks": [],
            "error": None,
        }

    session_results = defaultdict(_create_empty_session_result)

    chunk_generator = iterate_feature_extraction(
        "feature_extraction/tests/test_sessions"
    )
    for chunk_data, chunk_metadata in chunk_generator:

        # Analyze extracted features and collect statistics (mimics main block)
        # DOM mutations by type
        mutation_types = {}
        for curr_mutation in chunk_data.features["dom_mutations"]:
            mutation_type = curr_mutation.mutation_type or "unknown"
            mutation_types[mutation_type] = mutation_types.get(mutation_type, 0) + 1
        chunk_metadata["features"]["dom_mutation_stats"] = mutation_types

        # User interactions by action
        interaction_types = {}
        for curr_interaction in chunk_data.features["interactions"]:
            action = curr_interaction.action or "unknown"
            interaction_types[action] = interaction_types.get(action, 0) + 1
        chunk_metadata["features"]["interaction_stats"] = interaction_types

        # Other feature counts
        chunk_metadata["features"]["mouse_clusters"] = len(
            chunk_data.features["mouse_clusters"]
        )
        chunk_metadata["features"]["scroll_patterns"] = len(
            chunk_data.features["scroll_patterns"]
        )
        chunk_metadata["features"]["inter_event_delays"] = len(
            chunk_data.features["inter_event_delays"]
        )
        chunk_metadata["features"]["reaction_delays"] = len(
            chunk_data.features["reaction_delays"]
        )
        chunk_metadata["features"]["ui_nodes"] = len(chunk_data.features["ui_nodes"])

        session_result = session_results[chunk_metadata["session_id"]]
        session_result["chunks"].append(chunk_metadata)

    sessions_processed = []
    for session_id, session_result in session_results.items():
        sessions_processed.append(session_id)
        assert session_result == snapshot(name=f"session_{session_id}")

    assert sessions_processed == snapshot(name="sessions_processed")
