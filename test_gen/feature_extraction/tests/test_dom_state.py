"""
Unit tests for DOM state initialization and management.

Tests the creation of virtual DOM state from rrweb FullSnapshot events
and the accurate population of UINode mappings, as well as mutation
application for maintaining evolving DOM state.
"""

import pytest
from feature_extraction.dom_state import init_dom_state, apply_mutations
from feature_extraction.models import UINode


def test_init_dom_state_simple_tree():
    """Test initialization with a simple DOM tree (root with two children)."""
    full_snapshot_event = {
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

    node_by_id = init_dom_state(full_snapshot_event)

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


def test_init_dom_state_root_parent_is_none():
    """Test that the root node's parent is None."""
    full_snapshot_event = {
        "type": 2,
        "data": {"node": {"id": 1, "type": "Document", "childNodes": []}},
    }

    node_by_id = init_dom_state(full_snapshot_event)

    root_node = node_by_id[1]
    assert root_node.parent is None


def test_init_dom_state_attributes_and_text_captured():
    """Test that node attributes and textContent are captured exactly."""
    full_snapshot_event = {
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

    node_by_id = init_dom_state(full_snapshot_event)

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


def test_init_dom_state_invalid_event_type():
    """Test that non-FullSnapshot events raise ValueError."""
    invalid_event = {"type": 3, "data": {"source": 0}}  # Not a FullSnapshot

    with pytest.raises(ValueError, match="Event must be a FullSnapshot event"):
        init_dom_state(invalid_event)


def test_init_dom_state_missing_data_node():
    """Test that events without data.node raise ValueError."""
    invalid_event = {"type": 2, "data": {}}  # Missing node

    with pytest.raises(ValueError, match="FullSnapshot event must contain data.node"):
        init_dom_state(invalid_event)


def test_init_dom_state_missing_data():
    """Test that events without data raise ValueError."""
    invalid_event = {
        "type": 2
        # Missing data entirely
    }

    with pytest.raises(ValueError, match="FullSnapshot event must contain data.node"):
        init_dom_state(invalid_event)


def test_init_dom_state_nodes_without_ids_ignored():
    """Test that nodes without IDs are safely ignored."""
    full_snapshot_event = {
        "type": 2,
        "data": {
            "node": {
                "id": 1,
                "tagName": "div",
                "childNodes": [
                    {
                        # Missing id - should be ignored
                        "tagName": "span",
                        "textContent": "No ID",
                    },
                    {"id": 2, "tagName": "p", "textContent": "Has ID"},
                ],
            }
        },
    }

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


def test_apply_mutations_add_node():
    """Test that apply_mutations correctly adds new nodes."""
    # Start with a simple node_by_id map
    node_by_id = {
        1: UINode(id=1, tag="div", attributes={}, text="", parent=None),
        2: UINode(id=2, tag="span", attributes={}, text="existing", parent=1),
    }

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

    apply_mutations(node_by_id, mutation_events)

    # Assert the new node was added
    assert 3 in node_by_id
    new_node = node_by_id[3]
    assert new_node.id == 3
    assert new_node.tag == "button"
    assert new_node.attributes == {"class": "btn"}
    assert new_node.text == "Click me"
    assert new_node.parent == 1

    # Assert existing nodes are unchanged
    assert len(node_by_id) == 3
    assert node_by_id[1].tag == "div"
    assert node_by_id[2].tag == "span"


def test_apply_mutations_remove_node():
    """Test that apply_mutations correctly removes existing nodes."""
    # Start with a simple node_by_id map
    node_by_id = {
        1: UINode(id=1, tag="div", attributes={}, text="", parent=None),
        2: UINode(id=2, tag="span", attributes={}, text="to remove", parent=1),
        3: UINode(id=3, tag="p", attributes={}, text="to keep", parent=1),
    }

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

    apply_mutations(node_by_id, mutation_events)

    # Assert the node was removed
    assert 2 not in node_by_id
    assert len(node_by_id) == 2

    # Assert other nodes are unchanged
    assert 1 in node_by_id
    assert 3 in node_by_id
    assert node_by_id[3].text == "to keep"


def test_apply_mutations_change_attributes():
    """Test that apply_mutations correctly updates node attributes."""
    # Start with a node that has some attributes
    node_by_id = {
        1: UINode(
            id=1,
            tag="button",
            attributes={"class": "btn", "disabled": "false"},
            text="Submit",
            parent=None,
        ),
    }

    # Create a mutation event that changes attributes
    mutation_events = [
        {
            "type": 3,
            "data": {
                "source": 0,
                "attributes": [
                    {
                        "id": 1,
                        "attributes": {"class": "btn btn-primary", "disabled": "true"},
                    }
                ],
            },
        }
    ]

    apply_mutations(node_by_id, mutation_events)

    # Assert attributes were updated
    updated_node = node_by_id[1]
    assert updated_node.attributes["class"] == "btn btn-primary"
    assert updated_node.attributes["disabled"] == "true"

    # Assert other properties unchanged
    assert updated_node.tag == "button"
    assert updated_node.text == "Submit"


def test_apply_mutations_change_text():
    """Test that apply_mutations correctly updates node text content."""
    # Start with a node that has text
    node_by_id = {
        1: UINode(
            id=1,
            tag="p",
            attributes={},
            text="Original text",
            parent=None,
        ),
    }

    # Create a mutation event that changes text
    mutation_events = [
        {
            "type": 3,
            "data": {
                "source": 0,
                "texts": [{"id": 1, "value": "Updated text content"}],
            },
        }
    ]

    apply_mutations(node_by_id, mutation_events)

    # Assert text was updated
    updated_node = node_by_id[1]
    assert updated_node.text == "Updated text content"

    # Assert other properties unchanged
    assert updated_node.tag == "p"
    assert updated_node.attributes == {}


def test_apply_mutations_ignore_invalid_node_ids():
    """Test that mutations referencing nonexistent node IDs are safely ignored."""
    # Start with a simple node_by_id map
    node_by_id = {
        1: UINode(id=1, tag="div", attributes={}, text="", parent=None),
    }

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
    apply_mutations(node_by_id, mutation_events)

    # Assert original node is unchanged
    assert len(node_by_id) == 1
    assert 1 in node_by_id
    assert node_by_id[1].tag == "div"


def test_apply_mutations_mixed_operations():
    """Test apply_mutations with multiple operation types in one event."""
    # Start with initial nodes
    node_by_id = {
        1: UINode(id=1, tag="div", attributes={}, text="", parent=None),
        2: UINode(id=2, tag="span", attributes={"class": "old"}, text="old", parent=1),
    }

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

    apply_mutations(node_by_id, mutation_events)

    # Assert all operations were applied
    assert len(node_by_id) == 2  # One removed, one added
    assert 2 not in node_by_id  # Removed
    assert 3 in node_by_id  # Added

    # Check added node
    new_node = node_by_id[3]
    assert new_node.tag == "p"
    assert new_node.text == "new paragraph"
    assert new_node.parent == 1

    # Check updated node
    updated_node = node_by_id[1]
    assert updated_node.attributes["class"] == "container"
    assert updated_node.text == "updated div text"


def test_apply_mutations_ignore_non_mutation_events():
    """Test that non-mutation events are ignored."""
    # Start with a simple node_by_id map
    node_by_id = {
        1: UINode(id=1, tag="div", attributes={}, text="", parent=None),
    }

    # Create events that are not mutation events
    mutation_events = [
        {"type": 2, "data": {"node": {}}},  # FullSnapshot, not mutation
        {"type": 3, "data": {"source": 1}},  # IncrementalSnapshot, but not mutation
        {"type": 3, "data": {"source": 2}},  # IncrementalSnapshot, but not mutation
    ]

    apply_mutations(node_by_id, mutation_events)

    # Assert node_by_id is unchanged
    assert len(node_by_id) == 1
    assert node_by_id[1].tag == "div"


def test_apply_mutations_empty_mutation_data():
    """Test that mutation events with empty data don't cause errors."""
    # Start with a simple node_by_id map
    node_by_id = {
        1: UINode(id=1, tag="div", attributes={}, text="", parent=None),
    }

    # Create mutation events with empty or missing data
    mutation_events = [
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
    ]

    apply_mutations(node_by_id, mutation_events)

    # Assert node_by_id is unchanged
    assert len(node_by_id) == 1
    assert node_by_id[1].tag == "div"
