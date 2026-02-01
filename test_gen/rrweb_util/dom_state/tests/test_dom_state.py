"""
Unit tests for DOM state initialization and management.

Tests the creation of virtual DOM state from rrweb FullSnapshot events
and the accurate population of UINode mappings, as well as mutation
application for maintaining evolving DOM state.
"""

import pytest
from rrweb_util import EventType, IncrementalSource
from rrweb_util.dom_state.dom_state_helpers import init_dom_state, apply_mutation
from rrweb_util.dom_state.models import UINode


@pytest.fixture(name="create_full_snapshot_event")
def fixture_create_full_snapshot_event():
    """Helper for creating a full snapshot data structure."""

    def _create_full_snapshot(
        node_id=1, timestamp=0, node_type="div", attributes=None, child_nodes=None
    ):
        """Create a full snapshot event with given parameters."""
        return {
            "type": 2,
            "timestamp": timestamp,
            "data": {
                "node": {
                    "id": node_id,
                    "type": node_type,
                    "attributes": attributes or {},
                    "childNodes": child_nodes or [],
                }
            },
        }

    return _create_full_snapshot


@pytest.fixture(name="simple_full_snapshot")
def fixture_simple_full_snapshot():
    """Fixture providing a simple FullSnapshot event with nested DOM structure."""
    return {
        "type": EventType.FULL_SNAPSHOT,
        "data": {
            "node": {
                "id": 1,
                "type": 9,  # "document_node",
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
        "type": EventType.FULL_SNAPSHOT,
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
        1: UINode(id=1, tag="div", attributes={}, text="", parent=None, children=[2]),
        2: UINode(
            id=2, tag="span", attributes={}, text="existing", parent=1, children=[]
        ),
    }


@pytest.fixture(name="rich_node_by_id")
def fixture_rich_node_by_id():
    """Fixture providing a richer node_by_id dictionary for complex mutation testing."""
    return {
        1: UINode(
            id=1, tag="div", attributes={}, text="", parent=None, children=[2, 3]
        ),
        2: UINode(
            id=2,
            tag="span",
            attributes={"class": "old"},
            text="old",
            parent=1,
            children=[],
        ),
        3: UINode(id=3, tag="p", attributes={}, text="to keep", parent=1, children=[]),
    }


def test_init_dom_state_simple_tree(simple_full_snapshot):
    """Test initialization with a simple DOM tree (root with two children)."""
    node_by_id = init_dom_state(simple_full_snapshot)

    # Verify correct number of nodes
    assert len(node_by_id) == 4

    # Verify root node
    root_node = node_by_id[1]
    assert root_node.id == 1
    assert root_node.tag == "document_node"
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
        "type": EventType.FULL_SNAPSHOT,
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
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "data": {"source": IncrementalSource.MUTATION},
            },  # Not a FullSnapshot
            "Event must be a FullSnapshot event",
        ),
        (
            {"type": EventType.FULL_SNAPSHOT, "data": {}},  # Missing node
            "FullSnapshot event must contain data.node",
        ),
        (
            {"type": EventType.FULL_SNAPSHOT},  # Missing data entirely
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


def test_apply_mutation_add_node(simple_node_by_id):
    """Test that apply_mutation correctly adds new nodes."""
    # Create a mutation event that adds a new node
    mutation_events = [
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "data": {
                "source": IncrementalSource.MUTATION,
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

    for event in mutation_events:
        apply_mutation(simple_node_by_id, event)

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


def test_apply_mutation_remove_node(rich_node_by_id):
    """Test that apply_mutation correctly removes existing nodes."""
    # Create a mutation event that removes a node
    initial_length = len(rich_node_by_id)
    mutation_events = [
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "data": {
                "source": IncrementalSource.MUTATION,
                "removes": [{"id": 2}],
            },
        }
    ]

    for event in mutation_events:
        apply_mutation(rich_node_by_id, event)

    # Assert the node was not removed
    assert 2 in rich_node_by_id
    assert len(rich_node_by_id) == initial_length

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
def test_apply_mutation_change_properties(
    mutation_type, mutation_data, expected_changes
):
    """Test that apply_mutation correctly updates node attributes and text."""
    # Setup different initial nodes based on mutation type
    if mutation_type == "attributes":
        node_by_id = {
            1: UINode(
                id=1,
                tag="button",
                attributes={"class": "btn", "disabled": "false"},
                text="Submit",
                parent=None,
                children=[],
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
                children=[],
            ),
        }

    # Create mutation event
    mutation_events = [
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "data": {"source": IncrementalSource.MUTATION, **mutation_data},
        }
    ]

    for event in mutation_events:
        apply_mutation(node_by_id, event)

    # Assert expected changes
    updated_node = node_by_id[1]
    assert expected_changes(updated_node)


def test_apply_mutation_ignore_invalid_node_ids(simple_node_by_id):
    """Test that mutations referencing nonexistent node IDs are safely ignored."""
    # Create mutation events that reference nonexistent nodes
    mutation_events = [
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "data": {
                "source": IncrementalSource.MUTATION,
                "removes": [{"id": 999}],  # Nonexistent node
                "attributes": [
                    {"id": 888, "attributes": {"class": "new"}}  # Nonexistent node
                ],
                "texts": [{"id": 777, "value": "new text"}],  # Nonexistent node
            },
        }
    ]

    # This should not raise any errors
    for event in mutation_events:
        apply_mutation(simple_node_by_id, event)

    # Assert original nodes are unchanged
    assert len(simple_node_by_id) == 2
    assert 1 in simple_node_by_id
    assert simple_node_by_id[1].tag == "div"


def test_apply_mutation_mixed_operations(simple_node_by_id):
    """Test apply_mutation with multiple operation types in one event."""
    # Create a mutation event with multiple operations
    mutation_events = [
        {
            "type": EventType.INCREMENTAL_SNAPSHOT,
            "data": {
                "source": IncrementalSource.MUTATION,
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

    for event in mutation_events:
        apply_mutation(simple_node_by_id, event)

    # Assert all operations were applied
    assert len(simple_node_by_id) == 3  # One added
    assert 2 in simple_node_by_id  # Removes are ignored
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
            {
                "type": EventType.FULL_SNAPSHOT,
                "data": {"node": {}},
            },  # FullSnapshot, not mutation
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "data": {"source": IncrementalSource.MOUSE_MOVE},
            },  # IncrementalSnapshot, but not mutation
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "data": {"source": IncrementalSource.MOUSE_INTERACTION},
            },  # IncrementalSnapshot, but not mutation
        ],
        # Empty mutation data
        [
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "data": {"source": IncrementalSource.MUTATION},
            },  # No mutation data
            {
                "type": EventType.INCREMENTAL_SNAPSHOT,
                "data": {
                    "source": IncrementalSource.MUTATION,
                    "adds": [],
                    "removes": [],
                    "attributes": [],
                    "texts": [],
                },
            },  # Empty mutation data
        ],
    ],
)
def test_apply_mutation_ignore_invalid_events(simple_node_by_id, mutation_events):
    """Test that non-mutation events and empty mutation data are safely ignored."""
    original_length = len(simple_node_by_id)
    original_tag = simple_node_by_id[1].tag

    for event in mutation_events:
        apply_mutation(simple_node_by_id, event)

    # Assert node_by_id is unchanged
    assert len(simple_node_by_id) == original_length
    assert simple_node_by_id[1].tag == original_tag


def test_init_dom_state_builds_children_lists(simple_full_snapshot):
    """Test that init_dom_state populates children lists bidirectionally."""
    node_by_id = init_dom_state(simple_full_snapshot)

    # Verify root node has children
    root = node_by_id[1]
    assert root.children == [2]

    # Verify html node has children
    html_node = node_by_id[2]
    assert 3 in html_node.children
    assert 4 in html_node.children

    # Verify leaf nodes have empty children lists
    body_node = node_by_id[3]
    assert body_node.children == []

    div_node = node_by_id[4]
    assert div_node.children == []


def test_init_dom_state_bidirectional_relationships(simple_full_snapshot):
    """Test that parent-child relationships are bidirectional."""
    node_by_id = init_dom_state(simple_full_snapshot)

    # Test bidirectional relationship: root -> html
    root = node_by_id[1]
    html_node = node_by_id[2]
    assert html_node.parent == root.id
    assert html_node.id in root.children

    # Test bidirectional relationship: html -> body
    body_node = node_by_id[3]
    assert body_node.parent == html_node.id
    assert body_node.id in html_node.children

    # Test bidirectional relationship: html -> div
    div_node = node_by_id[4]
    assert div_node.parent == html_node.id
    assert div_node.id in html_node.children


def test_apply_mutation_maintains_children_list(simple_node_by_id):
    """Test that apply_mutation maintains parent's children list when adding nodes."""
    # Create a mutation event that adds a new node
    mutation_event = {
        "type": EventType.INCREMENTAL_SNAPSHOT,
        "data": {
            "source": IncrementalSource.MUTATION,
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

    apply_mutation(simple_node_by_id, mutation_event)

    # Verify parent's children list includes new child
    parent = simple_node_by_id[1]
    assert 3 in parent.children
    assert 2 in parent.children  # Existing child still there

    # Verify new child's parent reference
    new_child = simple_node_by_id[3]
    assert new_child.parent == 1


def test_apply_mutation_fails_with_missing_parent():
    """Test that apply_mutation raises ValueError when parent doesn't exist."""
    node_by_id = {
        1: UINode(id=1, tag="div", attributes={}, text="", parent=None, children=[])
    }

    # Try to add child with non-existent parent
    mutation_event = {
        "type": EventType.INCREMENTAL_SNAPSHOT,
        "data": {
            "source": IncrementalSource.MUTATION,
            "adds": [
                {
                    "parentId": 999,  # Non-existent parent
                    "node": {
                        "id": 2,
                        "tagName": "span",
                        "textContent": "orphan",
                    },
                }
            ],
        },
    }

    with pytest.raises(ValueError, match="parent 999 does not exist"):
        apply_mutation(node_by_id, mutation_event)


def test_uinode_children_serialization():
    """Test that UINode.to_dict() and from_dict() handle children field."""
    node = UINode(
        id=1,
        tag="div",
        attributes={"class": "container"},
        text="Hello",
        parent=None,
        children=[2, 3],
    )

    # Test to_dict includes children
    data = node.to_dict()
    assert data["children"] == [2, 3]

    # Test from_dict restores children
    restored = UINode.from_dict(data)
    assert restored.children == [2, 3]


def test_uinode_from_dict_backward_compatibility():
    """Test that from_dict handles missing children field (backward compatibility)."""
    # Old serialized data without children field
    data = {
        "id": 1,
        "tag": "div",
        "attributes": {},
        "text": "",
        "parent": None,
    }

    node = UINode.from_dict(data)
    assert node.children == []  # Should default to empty list
