"""
Unit tests for UI metadata resolution.

Tests the resolution of human-readable metadata from DOM nodes including
semantic attributes, text content, and DOM path computation.
"""

import pytest
from rrweb_util.dom_state.models import UINode
from rrweb_util.dom_state.node_metadata import resolve_node_metadata


@pytest.fixture(name="simple_nested_nodes")
def fixture_simple_nested_nodes():
    """Fixture providing a simple nested node structure for DOM path testing."""
    return {
        1: UINode(id=1, tag="html", attributes={}, text="", parent=None),
        2: UINode(id=2, tag="body", attributes={}, text="", parent=1),
        3: UINode(
            id=3, tag="div", attributes={"class": "container"}, text="", parent=2
        ),
        4: UINode(
            id=4,
            tag="button",
            attributes={"id": "submit", "class": "btn btn-primary"},
            text="Submit Form",
            parent=3,
        ),
    }


@pytest.fixture(name="rich_attributes_nodes")
def fixture_rich_attributes_nodes():
    """Fixture providing nodes with rich semantic attributes."""
    return {
        1: UINode(id=1, tag="html", attributes={}, text="", parent=None),
        2: UINode(
            id=2,
            tag="button",
            attributes={
                "aria-label": "Close Dialog",
                "data-testid": "close-button",
                "role": "button",
                "class": "close-btn",
            },
            text="×",
            parent=1,
        ),
        3: UINode(
            id=3,
            tag="input",
            attributes={
                "aria-label": "Email Address",
                "data-testid": "email-input",
                "type": "email",
            },
            text="",
            parent=1,
        ),
        4: UINode(
            id=4,
            tag="div",
            attributes={"class": "content"},
            text="Plain content",
            parent=1,
        ),
    }


@pytest.fixture(name="nodes_without_attributes")
def fixture_nodes_without_attributes():
    """Fixture providing nodes with minimal or no attributes."""
    return {
        1: UINode(id=1, tag="div", attributes={}, text="", parent=None),
        2: UINode(id=2, tag="span", attributes={}, text="Some text", parent=1),
        3: UINode(id=3, tag="p", attributes={}, text="", parent=1),
    }


def test_resolve_node_metadata_correct_dom_path(simple_nested_nodes):
    """Test that resolve_node_metadata returns the correct dom_path for nested nodes."""
    metadata = resolve_node_metadata(4, simple_nested_nodes)

    expected_path = "html > body > div.container > button#submit.btn"
    assert metadata["dom_path"] == expected_path


def test_resolve_node_metadata_root_node_path(simple_nested_nodes):
    """Test that the root node produces a simple single-element path."""
    metadata = resolve_node_metadata(1, simple_nested_nodes)

    assert metadata["dom_path"] == "html"


def test_resolve_node_metadata_with_aria_label(rich_attributes_nodes):
    """Test that nodes with aria-label attribute return the correct value."""
    metadata = resolve_node_metadata(2, rich_attributes_nodes)

    assert metadata["aria_label"] == "Close Dialog"
    assert metadata["tag"] == "button"
    assert metadata["text"] == "×"


def test_resolve_node_metadata_with_data_testid(rich_attributes_nodes):
    """Test that nodes with data-testid attribute return the correct value."""
    metadata = resolve_node_metadata(3, rich_attributes_nodes)

    assert metadata["data_testid"] == "email-input"
    assert metadata["aria_label"] == "Email Address"
    assert metadata["tag"] == "input"


def test_resolve_node_metadata_with_role(rich_attributes_nodes):
    """Test that nodes with role attribute return the correct value."""
    metadata = resolve_node_metadata(2, rich_attributes_nodes)

    assert metadata["role"] == "button"
    assert metadata["aria_label"] == "Close Dialog"
    assert metadata["data_testid"] == "close-button"


def test_resolve_node_metadata_without_semantic_attributes(nodes_without_attributes):
    """Test that nodes without aria-label, data-testid, and role return None for those fields."""
    metadata = resolve_node_metadata(2, nodes_without_attributes)

    assert metadata["aria_label"] is None
    assert metadata["data_testid"] is None
    assert metadata["role"] is None
    assert metadata["tag"] == "span"
    assert metadata["text"] == "Some text"


def test_resolve_node_metadata_text_content_captured(rich_attributes_nodes):
    """Test that text content is captured accurately."""
    # Test node with text content
    metadata = resolve_node_metadata(4, rich_attributes_nodes)
    assert metadata["text"] == "Plain content"

    # Test node with empty text content
    metadata = resolve_node_metadata(3, rich_attributes_nodes)
    assert metadata["text"] is None


def test_resolve_node_metadata_nonexistent_node_raises_keyerror(simple_nested_nodes):
    """Test that passing a nonexistent node_id raises a KeyError."""
    with pytest.raises(KeyError, match="Node ID 999 not found in node_by_id"):
        resolve_node_metadata(999, simple_nested_nodes)


def test_resolve_node_metadata_all_required_keys():
    """Test that the returned metadata dict has exactly the specified keys."""
    node_by_id = {
        1: UINode(
            id=1,
            tag="button",
            attributes={
                "aria-label": "Test",
                "data-testid": "test-btn",
                "role": "button",
            },
            text="Click me",
            parent=None,
        )
    }

    metadata = resolve_node_metadata(1, node_by_id)

    # Check that all required keys are present
    expected_keys = {
        "tag",
        "aria_label",
        "data_testid",
        "role",
        "text",
        "dom_path",
        "all_descendant_text",
        "nearest_ancestor_testid",
        "nearest_ancestor_testid_dom_path",
    }
    assert set(metadata.keys()) == expected_keys

    # Check that all values are correct
    assert metadata["tag"] == "button"
    assert metadata["aria_label"] == "Test"
    assert metadata["data_testid"] == "test-btn"
    assert metadata["role"] == "button"
    assert metadata["text"] == "Click me"
    assert metadata["dom_path"] == "button"
    assert metadata["all_descendant_text"] == "Click me"
    assert metadata["nearest_ancestor_testid"] is None  # No parent
    assert metadata["nearest_ancestor_testid_dom_path"] is None


def test_resolve_node_metadata_dom_path_with_id_and_class():
    """Test that DOM path correctly includes both ID and class when present."""
    node_by_id = {
        1: UINode(id=1, tag="div", attributes={}, text="", parent=None),
        2: UINode(
            id=2,
            tag="section",
            attributes={"id": "main", "class": "content primary"},
            text="",
            parent=1,
        ),
    }

    metadata = resolve_node_metadata(2, node_by_id)

    # Should include both ID and first class
    assert metadata["dom_path"] == "div > section#main.content"


def test_resolve_node_metadata_dom_path_class_only():
    """Test that DOM path correctly includes class when ID is not present."""
    node_by_id = {
        1: UINode(id=1, tag="div", attributes={}, text="", parent=None),
        2: UINode(
            id=2,
            tag="span",
            attributes={"class": "highlight important"},
            text="",
            parent=1,
        ),
    }

    metadata = resolve_node_metadata(2, node_by_id)

    # Should include first class only
    assert metadata["dom_path"] == "div > span.highlight"


def test_resolve_node_metadata_dom_path_id_only():
    """Test that DOM path correctly includes ID when class is not present."""
    node_by_id = {
        1: UINode(id=1, tag="div", attributes={}, text="", parent=None),
        2: UINode(
            id=2,
            tag="input",
            attributes={"id": "username"},
            text="",
            parent=1,
        ),
    }

    metadata = resolve_node_metadata(2, node_by_id)

    # Should include ID only
    assert metadata["dom_path"] == "div > input#username"


def test_resolve_node_metadata_dom_path_no_identifiers():
    """Test that DOM path works correctly when nodes have no ID or class."""
    node_by_id = {
        1: UINode(id=1, tag="html", attributes={}, text="", parent=None),
        2: UINode(id=2, tag="body", attributes={}, text="", parent=1),
        3: UINode(id=3, tag="div", attributes={}, text="", parent=2),
    }

    metadata = resolve_node_metadata(3, node_by_id)

    # Should just use tag names
    assert metadata["dom_path"] == "html > body > div"


def test_resolve_node_metadata_empty_class_attribute():
    """Test that empty class attributes are handled gracefully."""
    node_by_id = {
        1: UINode(id=1, tag="div", attributes={"class": ""}, text="", parent=None),
        2: UINode(id=2, tag="span", attributes={"class": "   "}, text="", parent=1),
    }

    # Empty class should not add class selector
    metadata = resolve_node_metadata(1, node_by_id)
    assert metadata["dom_path"] == "div"

    # Whitespace-only class should not add class selector
    metadata = resolve_node_metadata(2, node_by_id)
    assert metadata["dom_path"] == "div > span"


def test_resolve_node_metadata_missing_parent_reference():
    """Test that missing parent references are handled gracefully."""
    node_by_id = {
        1: UINode(id=1, tag="div", attributes={}, text="", parent=None),
        2: UINode(
            id=2, tag="span", attributes={}, text="", parent=999
        ),  # Parent doesn't exist
    }

    # Should still work, just stop at the node with missing parent
    metadata = resolve_node_metadata(2, node_by_id)
    assert metadata["dom_path"] == "span"
    assert metadata["tag"] == "span"


def test_all_descendant_text_simple_button():
    """Test that all_descendant_text collects text from nested spans in a button."""
    node_by_id = {
        1: UINode(id=1, tag="button", attributes={}, text="", parent=None),
        2: UINode(id=2, tag="span", attributes={}, text="Submit", parent=1),
        3: UINode(id=3, tag="span", attributes={}, text="Now", parent=1),
    }

    metadata = resolve_node_metadata(1, node_by_id)

    # Should concatenate text from all descendants
    assert metadata["all_descendant_text"] == "Submit Now"


def test_all_descendant_text_with_node_own_text():
    """Test that all_descendant_text includes the node's own text."""
    node_by_id = {
        1: UINode(id=1, tag="div", attributes={}, text="Parent text", parent=None),
        2: UINode(id=2, tag="span", attributes={}, text="Child text", parent=1),
    }

    metadata = resolve_node_metadata(1, node_by_id)

    # Should include both parent and child text
    assert metadata["all_descendant_text"] == "Parent text Child text"


def test_all_descendant_text_deeply_nested():
    """Test that all_descendant_text works with deeply nested structures."""
    node_by_id = {
        1: UINode(id=1, tag="div", attributes={}, text="Level 1", parent=None),
        2: UINode(id=2, tag="div", attributes={}, text="Level 2", parent=1),
        3: UINode(id=3, tag="span", attributes={}, text="Level 3", parent=2),
        4: UINode(id=4, tag="strong", attributes={}, text="Level 4", parent=3),
    }

    metadata = resolve_node_metadata(1, node_by_id)

    # Should collect all levels
    assert metadata["all_descendant_text"] == "Level 1 Level 2 Level 3 Level 4"


def test_all_descendant_text_no_text_returns_none():
    """Test that all_descendant_text returns None when no text exists."""
    node_by_id = {
        1: UINode(id=1, tag="div", attributes={}, text="", parent=None),
        2: UINode(id=2, tag="span", attributes={}, text="", parent=1),
        3: UINode(id=3, tag="span", attributes={}, text="   ", parent=1),  # Whitespace
    }

    metadata = resolve_node_metadata(1, node_by_id)

    # Should return None when no meaningful text
    assert metadata["all_descendant_text"] is None


def test_all_descendant_text_normalizes_whitespace():
    """Test that all_descendant_text normalizes extra whitespace."""
    node_by_id = {
        1: UINode(id=1, tag="div", attributes={}, text="  Text  A  ", parent=None),
        2: UINode(id=2, tag="span", attributes={}, text="  Text   B  ", parent=1),
    }

    metadata = resolve_node_metadata(1, node_by_id)

    # Should normalize to single spaces
    assert metadata["all_descendant_text"] == "Text A Text B"


def test_all_descendant_text_leaf_node():
    """Test that all_descendant_text works for leaf nodes without children."""
    node_by_id = {
        1: UINode(id=1, tag="div", attributes={}, text="", parent=None),
        2: UINode(id=2, tag="span", attributes={}, text="Leaf text", parent=1),
    }

    metadata = resolve_node_metadata(2, node_by_id)

    # Leaf node should just return its own text
    assert metadata["all_descendant_text"] == "Leaf text"


def test_nearest_ancestor_testid_direct_parent():
    """Test finding data-testid on the direct parent."""
    node_by_id = {
        1: UINode(
            id=1,
            tag="div",
            attributes={"data-testid": "container"},
            text="",
            parent=None,
        ),
        2: UINode(id=2, tag="button", attributes={}, text="Click me", parent=1),
    }

    metadata = resolve_node_metadata(2, node_by_id)

    assert metadata["nearest_ancestor_testid"] == "container"
    assert metadata["nearest_ancestor_testid_dom_path"] == "div"


def test_nearest_ancestor_testid_grandparent():
    """Test finding data-testid on a grandparent when parent doesn't have one."""
    node_by_id = {
        1: UINode(
            id=1,
            tag="section",
            attributes={"data-testid": "user-profile"},
            text="",
            parent=None,
        ),
        2: UINode(id=2, tag="div", attributes={"class": "header"}, text="", parent=1),
        3: UINode(id=3, tag="button", attributes={}, text="Edit", parent=2),
    }

    metadata = resolve_node_metadata(3, node_by_id)

    assert metadata["nearest_ancestor_testid"] == "user-profile"
    assert metadata["nearest_ancestor_testid_dom_path"] == "section"


def test_nearest_ancestor_testid_no_ancestor_with_testid():
    """Test that nearest_ancestor_testid returns None when no ancestor has one."""
    node_by_id = {
        1: UINode(id=1, tag="div", attributes={}, text="", parent=None),
        2: UINode(id=2, tag="span", attributes={}, text="", parent=1),
        3: UINode(id=3, tag="button", attributes={}, text="Click", parent=2),
    }

    metadata = resolve_node_metadata(3, node_by_id)

    assert metadata["nearest_ancestor_testid"] is None
    assert metadata["nearest_ancestor_testid_dom_path"] is None


def test_nearest_ancestor_testid_root_node():
    """Test that root node returns None for nearest_ancestor_testid."""
    node_by_id = {
        1: UINode(
            id=1,
            tag="div",
            attributes={"data-testid": "root"},
            text="",
            parent=None,
        ),
    }

    metadata = resolve_node_metadata(1, node_by_id)

    # Root node has no parent, so should return None
    assert metadata["nearest_ancestor_testid"] is None
    assert metadata["nearest_ancestor_testid_dom_path"] is None


def test_nearest_ancestor_testid_stops_at_first_match():
    """Test that it stops at the first ancestor with data-testid."""
    node_by_id = {
        1: UINode(
            id=1,
            tag="section",
            attributes={"data-testid": "outer"},
            text="",
            parent=None,
        ),
        2: UINode(
            id=2,
            tag="div",
            attributes={"data-testid": "inner"},
            text="",
            parent=1,
        ),
        3: UINode(id=3, tag="button", attributes={}, text="Click", parent=2),
    }

    metadata = resolve_node_metadata(3, node_by_id)

    # Should return the nearest (inner), not outer
    assert metadata["nearest_ancestor_testid"] == "inner"
    assert metadata["nearest_ancestor_testid_dom_path"] == "section > div"


def test_nearest_ancestor_testid_with_complex_dom_path():
    """Test that DOM path to ancestor is computed correctly."""
    node_by_id = {
        1: UINode(id=1, tag="html", attributes={}, text="", parent=None),
        2: UINode(id=2, tag="body", attributes={}, text="", parent=1),
        3: UINode(
            id=3,
            tag="div",
            attributes={"data-testid": "main-content", "class": "container"},
            text="",
            parent=2,
        ),
        4: UINode(id=4, tag="section", attributes={}, text="", parent=3),
        5: UINode(id=5, tag="button", attributes={"id": "submit"}, text="", parent=4),
    }

    metadata = resolve_node_metadata(5, node_by_id)

    assert metadata["nearest_ancestor_testid"] == "main-content"
    assert metadata["nearest_ancestor_testid_dom_path"] == "html > body > div.container"
