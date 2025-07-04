"""
Unit tests for DOM mutation extraction.

Tests the extraction of structured DomMutation records from rrweb mutation events,
covering attribute changes, text modifications, node additions, and removals.
"""

import pytest
from feature_extraction.extractors import extract_dom_mutations


@pytest.fixture(name="single_attribute_mutation_event")
def fixture_single_attribute_mutation_event():
    """Fixture providing a mutation event with multiple attribute changes."""
    return {
        "type": 3,
        "timestamp": 12345,
        "data": {
            "source": 0,
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


@pytest.fixture(name="text_change_event")
def fixture_text_change_event():
    """Fixture providing a mutation event with text content changes."""
    return {
        "type": 3,
        "timestamp": 23456,
        "data": {
            "source": 0,
            "texts": [
                {"id": 100, "value": "Updated text content"},
                {"id": 101, "value": "Another text update"},
            ],
        },
    }


@pytest.fixture(name="node_addition_event")
def fixture_node_addition_event():
    """Fixture providing a mutation event with node additions."""
    return {
        "type": 3,
        "timestamp": 34567,
        "data": {
            "source": 0,
            "adds": [
                {
                    "parentId": 50,
                    "node": {
                        "id": 200,
                        "tagName": "button",
                        "attributes": {"class": "btn", "type": "submit"},
                        "textContent": "Click me",
                    },
                },
                {
                    "parentId": 51,
                    "node": {
                        "id": 201,
                        "tagName": "div",
                        "attributes": {},
                        "textContent": "",
                    },
                },
            ],
        },
    }


@pytest.fixture(name="node_removal_event")
def fixture_node_removal_event():
    """Fixture providing a mutation event with node removals."""
    return {
        "type": 3,
        "timestamp": 45678,
        "data": {
            "source": 0,
            "removes": [
                {"id": 300},
                {"id": 301},
            ],
        },
    }


@pytest.fixture(name="mixed_mutation_event")
def fixture_mixed_mutation_event():
    """Fixture providing a mutation event with multiple operation types."""
    return {
        "type": 3,
        "timestamp": 56789,
        "data": {
            "source": 0,
            "attributes": [{"id": 10, "attributes": {"class": "updated"}}],
            "texts": [{"id": 20, "value": "new text"}],
            "adds": [
                {
                    "parentId": 30,
                    "node": {
                        "id": 40,
                        "tagName": "span",
                        "attributes": {"role": "alert"},
                        "textContent": "Alert message",
                    },
                }
            ],
            "removes": [{"id": 50}],
        },
    }


@pytest.fixture(name="non_mutation_events")
def fixture_non_mutation_events():
    """Fixture providing events that are not mutation events."""
    return [
        # FullSnapshot event
        {"type": 2, "timestamp": 1000, "data": {"node": {}}},
        # Mouse move event
        {"type": 3, "timestamp": 2000, "data": {"source": 1, "x": 100, "y": 200}},
        # Click event
        {"type": 3, "timestamp": 3000, "data": {"source": 2, "id": 123}},
        # Scroll event
        {"type": 3, "timestamp": 4000, "data": {"source": 3, "x": 0, "y": 100}},
        # Input event
        {
            "type": 3,
            "timestamp": 5000,
            "data": {"source": 5, "id": 456, "text": "input"},
        },
    ]


def test_extract_single_attribute_mutation(single_attribute_mutation_event):
    """Test that a single mutation event with multiple attribute changes produces one DomMutation per attribute."""
    mutations = extract_dom_mutations([single_attribute_mutation_event])

    # Should produce exactly one mutation for the attribute change
    assert len(mutations) == 1

    mutation = mutations[0]
    assert mutation.mutation_type == "attribute"
    assert mutation.target_id == 42
    assert mutation.timestamp == 12345
    assert mutation.details["attributes"]["class"] == "btn btn-primary active"
    assert mutation.details["attributes"]["disabled"] == "true"
    assert mutation.details["attributes"]["aria-label"] == "Submit Form"


def test_extract_text_changes(text_change_event):
    """Test that text-change events produce DomMutation of type 'text'."""
    mutations = extract_dom_mutations([text_change_event])

    # Should produce two mutations, one for each text change
    assert len(mutations) == 2

    # First text change
    mutation1 = mutations[0]
    assert mutation1.mutation_type == "text"
    assert mutation1.target_id == 100
    assert mutation1.timestamp == 23456
    assert mutation1.details["text"] == "Updated text content"

    # Second text change
    mutation2 = mutations[1]
    assert mutation2.mutation_type == "text"
    assert mutation2.target_id == 101
    assert mutation2.timestamp == 23456
    assert mutation2.details["text"] == "Another text update"


def test_extract_node_additions(node_addition_event):
    """Test that add events produce appropriate DomMutation entries with correct fields."""
    mutations = extract_dom_mutations([node_addition_event])

    # Should produce two mutations, one for each added node
    assert len(mutations) == 2

    # First added node (button)
    mutation1 = mutations[0]
    assert mutation1.mutation_type == "add"
    assert mutation1.target_id == 200
    assert mutation1.timestamp == 34567
    assert mutation1.details["parent_id"] == 50
    assert mutation1.details["tag"] == "button"
    assert mutation1.details["attributes"]["class"] == "btn"
    assert mutation1.details["attributes"]["type"] == "submit"
    assert mutation1.details["text"] == "Click me"

    # Second added node (div)
    mutation2 = mutations[1]
    assert mutation2.mutation_type == "add"
    assert mutation2.target_id == 201
    assert mutation2.timestamp == 34567
    assert mutation2.details["parent_id"] == 51
    assert mutation2.details["tag"] == "div"
    assert mutation2.details["attributes"] == {}
    assert mutation2.details["text"] == ""


def test_extract_node_removals(node_removal_event):
    """Test that remove events produce appropriate DomMutation entries."""
    mutations = extract_dom_mutations([node_removal_event])

    # Should produce two mutations, one for each removed node
    assert len(mutations) == 2

    # First removed node
    mutation1 = mutations[0]
    assert mutation1.mutation_type == "remove"
    assert mutation1.target_id == 300
    assert mutation1.timestamp == 45678
    assert mutation1.details == {}

    # Second removed node
    mutation2 = mutations[1]
    assert mutation2.mutation_type == "remove"
    assert mutation2.target_id == 301
    assert mutation2.timestamp == 45678
    assert mutation2.details == {}


def test_extract_mixed_mutation_operations(mixed_mutation_event):
    """Test that mixed mutation events produce all expected DomMutation types."""
    mutations = extract_dom_mutations([mixed_mutation_event])

    # Should produce 4 mutations: 1 attribute + 1 text + 1 add + 1 remove
    assert len(mutations) == 4

    # Check that we have one of each type
    mutation_types = [m.mutation_type for m in mutations]
    assert "attribute" in mutation_types
    assert "text" in mutation_types
    assert "add" in mutation_types
    assert "remove" in mutation_types

    # Verify all mutations have the same timestamp
    for mutation in mutations:
        assert mutation.timestamp == 56789


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
        {"type": 3, "timestamp": 1000, "data": {"source": 0}},
        # Event with empty mutation arrays
        {
            "type": 3,
            "timestamp": 2000,
            "data": {
                "source": 0,
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
            "type": 3,
            "timestamp": 1000,
            "data": {"source": 0, "removes": [{"id": 1}]},
        },
        {
            "type": 3,
            "timestamp": 2000,
            "data": {"source": 0, "texts": [{"id": 2, "value": "text"}]},
        },
        {
            "type": 3,
            "timestamp": 3000,
            "data": {
                "source": 0,
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
            "type": 3,
            "timestamp": 1000,
            "data": {
                "source": 0,
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
        "type": 3,
        "timestamp": 1000,
        "data": {
            "source": 0,
            "adds": [
                {
                    "parentId": 50,
                    "node": {
                        "id": 100,
                        "type": "text",  # Using 'type' instead of 'tagName'
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
    assert mutation.details["tag"] == "text"
    assert mutation.details["text"] == "Text node"
