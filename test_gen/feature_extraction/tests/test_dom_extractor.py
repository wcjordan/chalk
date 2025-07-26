"""
Unit tests for DOM mutation extraction.

Tests the extraction of structured DomMutation records from rrweb mutation events,
covering attribute changes, text modifications, node additions, and removals.
"""

import pytest
from feature_extraction.extractors import extract_dom_mutations
from rrweb_util import EventType, IncrementalSource


@pytest.fixture(name="single_attribute_mutation_event")
def fixture_single_attribute_mutation_event():
    """Fixture providing a mutation event with multiple attribute changes."""
    return {
        "type": EventType.INCREMENTAL_SNAPSHOT,
        "timestamp": 12345,
        "data": {
            "source": IncrementalSource.MUTATION,
            "attributes": [
                {
                    "id": 42,
                    "attributes": {
                        "class": "btn btn-primary active",
                        "disabled": "true",
                        "aria-label": "Submit Form",
                    },
                }
            ],
        },
    }


@pytest.fixture(name="non_mutation_events")
def fixture_non_mutation_events():
    """Fixture providing events that are not mutation events."""
    return [
        # FullSnapshot event
        {"type": EventType.FULL_SNAPSHOT, "timestamp": 1000, "data": {"node": {}}},
        # Mouse move event
        {"type": EventType.INCREMENTAL_SNAPSHOT, "timestamp": 2000, "data": {"source": IncrementalSource.MOUSE_MOVE, "x": 100, "y": 200}},
        # Click event
        {"type": EventType.INCREMENTAL_SNAPSHOT, "timestamp": 3000, "data": {"source": IncrementalSource.MOUSE_INTERACTION, "id": 123}},
        # Scroll event
        {"type": EventType.INCREMENTAL_SNAPSHOT, "timestamp": 4000, "data": {"source": IncrementalSource.SCROLL, "x": 0, "y": 100}},
        # Input event
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 5000,
            "data": {"source": IncrementalSource.INPUT, "id": 456, "text": "input"},
        },
    ]


def test_extract_mixed_sequence_filters_only_mutations(
    single_attribute_mutation_event, non_mutation_events
):
    """Test that a mixed sequence of mutation and non-mutation events only extracts mutations."""
    # Mix mutation and non-mutation events
    mixed_events = (
        non_mutation_events[:2]
        + [single_attribute_mutation_event]
        + non_mutation_events[2:]
    )

    mutations = extract_dom_mutations(mixed_events)

    # Should only extract the one mutation event
    assert len(mutations) == 1
    assert mutations[0].mutation_type == "attribute"
    assert mutations[0].target_id == 42


def test_extract_empty_mutation_data():
    """Test that events with empty mutation data do not produce spurious entries."""
    empty_mutation_events = [
        # Event with no mutation data at all
        {"type": EventType.INCREMENTAL_SNAPSHOT, "timestamp": 1000, "data": {"source": IncrementalSource.MUTATION}},
        # Event with empty mutation arrays
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 2000,
            "data": {
                "source": IncrementalSource.MUTATION,
                "attributes": [],
                "texts": [],
                "adds": [],
                "removes": [],
            },
        },
    ]

    mutations = extract_dom_mutations(empty_mutation_events)

    # Should produce no mutations
    assert len(mutations) == 0


def test_extract_preserves_event_order():
    """Test that the returned list preserves the original event order."""
    # Create events with different timestamps in a specific order
    events = [
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {"source": IncrementalSource.MUTATION, "removes": [{"id": 1}]},
        },
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 2000,
            "data": {"source": IncrementalSource.MUTATION, "texts": [{"id": 2, "value": "text"}]},
        },
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 3000,
            "data": {
                "source": IncrementalSource.MUTATION,
                "attributes": [{"id": 3, "attributes": {"class": "test"}}],
            },
        },
    ]

    mutations = extract_dom_mutations(events)

    # Should preserve order: remove, text, attribute
    assert len(mutations) == 3
    assert mutations[0].mutation_type == "remove"
    assert mutations[0].timestamp == 1000
    assert mutations[1].mutation_type == "text"
    assert mutations[1].timestamp == 2000
    assert mutations[2].mutation_type == "attribute"
    assert mutations[2].timestamp == 3000


def test_extract_handles_missing_node_ids():
    """Test that mutation records without node IDs are safely ignored."""
    events_with_missing_ids = [
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "timestamp": 1000,
            "data": {
                "source": IncrementalSource.MUTATION,
                "attributes": [
                    {"attributes": {"class": "test"}},  # Missing id
                    {"id": 42, "attributes": {"valid": "true"}},  # Valid
                ],
                "texts": [
                    {"value": "no id"},  # Missing id
                    {"id": 43, "value": "valid text"},  # Valid
                ],
                "adds": [
                    {
                        "parentId": 50,
                        "node": {"tagName": "div"},  # Missing id
                    },
                    {
                        "parentId": 51,
                        "node": {"id": 44, "tagName": "span"},  # Valid
                    },
                ],
                "removes": [
                    {},  # Missing id
                    {"id": 45},  # Valid
                ],
            },
        }
    ]

    mutations = extract_dom_mutations(events_with_missing_ids)

    # Should only extract mutations with valid node IDs
    assert len(mutations) == 4  # 1 attribute + 1 text + 1 add + 1 remove

    # Verify all extracted mutations have valid target IDs
    target_ids = [m.target_id for m in mutations]
    assert 42 in target_ids  # Valid attribute
    assert 43 in target_ids  # Valid text
    assert 44 in target_ids  # Valid add
    assert 45 in target_ids  # Valid remove


def test_extract_handles_node_type_fallback():
    """Test that node additions handle 'type' field when 'tagName' is missing."""
    event_with_type_field = {
        "type": EventType.INCREMENTAL_SNAPSHOT,
        "timestamp": 1000,
        "data": {
            "source": IncrementalSource.MUTATION,
            "adds": [
                {
                    "parentId": 50,
                    "node": {
                        "id": 100,
                        "type": 3,  # Using 'type' instead of 'tagName'.  Type for text_node
                        "textContent": "Text node",
                    },
                }
            ],
        },
    }

    mutations = extract_dom_mutations([event_with_type_field])

    assert len(mutations) == 1
    mutation = mutations[0]
    assert mutation.mutation_type == "add"
    assert mutation.details["tag"] == "text_node"
    assert mutation.details["text"] == "Text node"
