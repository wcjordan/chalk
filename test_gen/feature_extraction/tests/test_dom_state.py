"""
Unit tests for DOM state initialization and management.

Tests the creation of virtual DOM state from rrweb FullSnapshot events
and the accurate population of UINode mappings, as well as mutation
application for maintaining evolving DOM state.
"""

import pytest
from feature_extraction.dom_state import init_dom_state, apply_mutations
from feature_extraction.models import UINode


@pytest.fixture(name="simple_full_snapshot")
def fixture_simple_full_snapshot():
    """Fixture providing a simple FullSnapshot event with nested DOM structure."""
    return {
        "type": 2,
        "data": {
            "node": {
                "id": 1,
                "type": "Document",
                "childNodes": [
                    {
                        "id": 2,
                        "tagName": "html",
                        "attributes": {"lang": "en"},
                        "childNodes": [
                            {
                                "id": 3,
                                "tagName": "body",
                                "attributes": {"class": "main"},
                                "textContent": "",
                                "childNodes": [],
                            },
                            {
                                "id": 4,
                                "tagName": "div",
                                "attributes": {"id": "content"},
                                "textContent": "Hello World",
                                "childNodes": [],
                            },
                        ],
                    }
                ],
            }
        },
    }


@pytest.fixture(name="button_snapshot")
def fixture_button_snapshot():
    """Fixture providing a FullSnapshot with a button element with rich attributes."""
    return {
        "type": 2,
        "data": {
            "node": {
                "id": 1,
                "tagName": "button",
                "attributes": {
                    "aria-label": "Submit Form",
                    "class": "btn btn-primary",
                    "data-testid": "submit-button",
                    "role": "button",
                },
                "textContent": "Submit",
                "childNodes": [],
            }
        },
    }


@pytest.fixture(name="simple_node_by_id")
def fixture_simple_node_by_id():
    """Fixture providing a simple node_by_id dictionary for mutation testing."""
    return {
        1: UINode(id=1, tag="div", attributes={}, text="", parent=None),
        2: UINode(id=2, tag="span", attributes={}, text="existing", parent=1),
    }


@pytest.fixture(name="rich_node_by_id")
def fixture_rich_node_by_id():
    """Fixture providing a richer node_by_id dictionary for complex mutation testing."""
    return {
        1: UINode(id=1, tag="div", attributes={}, text="", parent=None),
        2: UINode(id=2, tag="span", attributes={"class": "old"}, text="old", parent=1),
        3: UINode(id=3, tag="p", attributes={}, text="to keep", parent=1),
    }


def test_init_dom_state_simple_tree(simple_full_snapshot):
    """Test initialization with a simple DOM tree (root with two children)."""
    node_by_id = init_dom_state(simple_full_snapshot)

    # Verify correct number of nodes
    assert len(node_by_id) == 4

    # Verify root node
    root_node = node_by_id[1]
    assert root_node.id == 1
    assert root_node.tag == "Document"
    assert root_node.parent is None
    assert root_node.attributes == {}

    # Verify html node
    html_node = node_by_id[2]
    assert html_node.id == 2
    assert html_node.tag == "html"
    assert html_node.parent == 1
    assert html_node.attributes == {"lang": "en"}

    # Verify body node
    body_node = node_by_id[3]
    assert body_node.id == 3
    assert body_node.tag == "body"
    assert body_node.parent == 2
    assert body_node.attributes == {"class": "main"}
    assert body_node.text == ""

    # Verify div node
    div_node = node_by_id[4]
    assert div_node.id == 4
    assert div_node.tag == "div"
    assert div_node.parent == 2
    assert div_node.attributes == {"id": "content"}
    assert div_node.text == "Hello World"


def test_init_dom_state_root_parent_is_none(simple_full_snapshot):
    """Test that the root node's parent is None."""
    node_by_id = init_dom_state(simple_full_snapshot)
    root_node = node_by_id[1]
    assert root_node.parent is None


def test_init_dom_state_attributes_and_text_captured(button_snapshot):
    """Test that node attributes and textContent are captured exactly."""
    node_by_id = init_dom_state(button_snapshot)

    button_node = node_by_id[1]
    assert button_node.tag == "button"
    assert button_node.attributes["aria-label"] == "Submit Form"
    assert button_node.attributes["class"] == "btn btn-primary"
    assert button_node.attributes["data-testid"] == "submit-button"
    assert button_node.attributes["role"] == "button"
    assert button_node.text == "Submit"


def test_init_dom_state_empty_attributes():
    """Test handling of nodes with no attributes."""
    full_snapshot_event = {
        "type": 2,
        "data": {"node": {"id": 1, "tagName": "div", "childNodes": []}},
    }

    node_by_id = init_dom_state(full_snapshot_event)

    div_node = node_by_id[1]
    assert div_node.attributes == {}
    assert div_node.text == ""


@pytest.mark.parametrize(
    "invalid_event,expected_error",
    [
        (
            {"type": 3, "data": {"source": 0}},  # Not a FullSnapshot
            "Event must be a FullSnapshot event",
        ),
        (
            {"type": 2, "data": {}},  # Missing node
            "FullSnapshot event must contain data.node",
        ),
        (
            {"type": 2},  # Missing data entirely
            "FullSnapshot event must contain data.node",
        ),
    ],
)
def test_init_dom_state_invalid_events(invalid_event, expected_error):
    """Test that invalid events raise ValueError with appropriate messages."""
    with pytest.raises(ValueError, match=expected_error):
        init_dom_state(invalid_event)


def test_init_dom_state_nodes_without_ids_ignored(create_full_snapshot_event):
    """Test that nodes without IDs are safely ignored."""
    full_snapshot_event = create_full_snapshot_event(
        child_nodes=[
            {"tagName": "span", "textContent": "No ID"},  # Missing ID
            {"id": 2, "tagName": "p", "textContent": "Has ID"},  # Valid node
        ]
    )

    node_by_id = init_dom_state(full_snapshot_event)

    # Should only contain nodes with IDs
    assert len(node_by_id) == 2
    assert 1 in node_by_id
    assert 2 in node_by_id

    # Verify the valid child node
    p_node = node_by_id[2]
    assert p_node.tag == "p"
    assert p_node.text == "Has ID"
    assert p_node.parent == 1


def test_apply_mutations_add_node(simple_node_by_id):
    """Test that apply_mutations correctly adds new nodes."""
    # Create a mutation event that adds a new node
    mutation_events = [
        {
            "type": 3,
            "data": {
                "source": 0,
                "adds": [
                    {
                        "parentId": 1,
                        "node": {
                            "id": 3,
                            "tagName": "button",
                            "attributes": {"class": "btn"},
                            "textContent": "Click me",
                        },
                    }
                ],
            },
        }
    ]

    apply_mutations(simple_node_by_id, mutation_events)

    # Assert the new node was added
    assert 3 in simple_node_by_id
    new_node = simple_node_by_id[3]
    assert new_node.id == 3
    assert new_node.tag == "button"
    assert new_node.attributes == {"class": "btn"}
    assert new_node.text == "Click me"
    assert new_node.parent == 1

    # Assert existing nodes are unchanged
    assert len(simple_node_by_id) == 3
    assert simple_node_by_id[1].tag == "div"
    assert simple_node_by_id[2].tag == "span"


def test_apply_mutations_remove_node(rich_node_by_id):
    """Test that apply_mutations correctly removes existing nodes."""
    # Create a mutation event that removes a node
    mutation_events = [
        {
            "type": 3,
            "data": {
                "source": 0,
                "removes": [{"id": 2}],
            },
        }
    ]

    apply_mutations(rich_node_by_id, mutation_events)

    # Assert the node was removed
    assert 2 not in rich_node_by_id
    assert len(rich_node_by_id) == 2

    # Assert other nodes are unchanged
    assert 1 in rich_node_by_id
    assert 3 in rich_node_by_id
    assert rich_node_by_id[3].text == "to keep"


@pytest.mark.parametrize(
    "mutation_type,mutation_data,expected_changes",
    [
        (
            "attributes",
            {
                "attributes": [
                    {
                        "id": 1,
                        "attributes": {"class": "btn btn-primary", "disabled": "true"},
                    }
                ]
            },
            lambda node: (
                node.attributes["class"] == "btn btn-primary"
                and node.attributes["disabled"] == "true"
                and node.tag == "button"
                and node.text == "Submit"
            ),
        ),
        (
            "texts",
            {"texts": [{"id": 1, "value": "Updated text content"}]},
            lambda node: (
                node.text == "Updated text content"
                and node.tag == "p"
                and not node.attributes
            ),
        ),
    ],
)
def test_apply_mutations_change_properties(
    mutation_type, mutation_data, expected_changes
):
    """Test that apply_mutations correctly updates node attributes and text."""
    # Setup different initial nodes based on mutation type
    if mutation_type == "attributes":
        node_by_id = {
            1: UINode(
                id=1,
                tag="button",
                attributes={"class": "btn", "disabled": "false"},
                text="Submit",
                parent=None,
            ),
        }
    else:  # texts
        node_by_id = {
            1: UINode(
                id=1,
                tag="p",
                attributes={},
                text="Original text",
                parent=None,
            ),
        }

    # Create mutation event
    mutation_events = [
        {
            "type": 3,
            "data": {"source": 0, **mutation_data},
        }
    ]

    apply_mutations(node_by_id, mutation_events)

    # Assert expected changes
    updated_node = node_by_id[1]
    assert expected_changes(updated_node)


def test_apply_mutations_ignore_invalid_node_ids(simple_node_by_id):
    """Test that mutations referencing nonexistent node IDs are safely ignored."""
    # Create mutation events that reference nonexistent nodes
    mutation_events = [
        {
            "type": 3,
            "data": {
                "source": 0,
                "removes": [{"id": 999}],  # Nonexistent node
                "attributes": [
                    {"id": 888, "attributes": {"class": "new"}}  # Nonexistent node
                ],
                "texts": [{"id": 777, "value": "new text"}],  # Nonexistent node
            },
        }
    ]

    # This should not raise any errors
    apply_mutations(simple_node_by_id, mutation_events)

    # Assert original nodes are unchanged
    assert len(simple_node_by_id) == 2
    assert 1 in simple_node_by_id
    assert simple_node_by_id[1].tag == "div"


def test_apply_mutations_mixed_operations(simple_node_by_id):
    """Test apply_mutations with multiple operation types in one event."""
    # Create a mutation event with multiple operations
    mutation_events = [
        {
            "type": 3,
            "data": {
                "source": 0,
                "adds": [
                    {
                        "parentId": 1,
                        "node": {
                            "id": 3,
                            "tagName": "p",
                            "textContent": "new paragraph",
                        },
                    }
                ],
                "removes": [{"id": 2}],
                "attributes": [{"id": 1, "attributes": {"class": "container"}}],
                "texts": [{"id": 1, "value": "updated div text"}],
            },
        }
    ]

    apply_mutations(simple_node_by_id, mutation_events)

    # Assert all operations were applied
    assert len(simple_node_by_id) == 2  # One removed, one added
    assert 2 not in simple_node_by_id  # Removed
    assert 3 in simple_node_by_id  # Added

    # Check added node
    new_node = simple_node_by_id[3]
    assert new_node.tag == "p"
    assert new_node.text == "new paragraph"
    assert new_node.parent == 1

    # Check updated node
    updated_node = simple_node_by_id[1]
    assert updated_node.attributes["class"] == "container"
    assert updated_node.text == "updated div text"


@pytest.mark.parametrize(
    "mutation_events",
    [
        # Non-mutation events
        [
            {"type": 2, "data": {"node": {}}},  # FullSnapshot, not mutation
            {
                "type": 3,
                "data": {"source": 1},
            },  # IncrementalSnapshot, but not mutation
            {
                "type": 3,
                "data": {"source": 2},
            },  # IncrementalSnapshot, but not mutation
        ],
        # Empty mutation data
        [
            {"type": 3, "data": {"source": 0}},  # No mutation data
            {
                "type": 3,
                "data": {
                    "source": 0,
                    "adds": [],
                    "removes": [],
                    "attributes": [],
                    "texts": [],
                },
            },  # Empty mutation data
        ],
    ],
)
def test_apply_mutations_ignore_invalid_events(simple_node_by_id, mutation_events):
    """Test that non-mutation events and empty mutation data are safely ignored."""
    original_length = len(simple_node_by_id)
    original_tag = simple_node_by_id[1].tag

    apply_mutations(simple_node_by_id, mutation_events)

    # Assert node_by_id is unchanged
    assert len(simple_node_by_id) == original_length
    assert simple_node_by_id[1].tag == original_tag
