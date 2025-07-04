"""
Unit tests for UI metadata resolution.

Tests the resolution of human-readable metadata from DOM nodes including
semantic attributes, text content, and DOM path computation.
"""

import pytest
from feature_extraction.metadata import resolve_node_metadata
from feature_extraction.models import UINode


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
    expected_keys = {"tag", "aria_label", "data_testid", "role", "text", "dom_path"}
    assert set(metadata.keys()) == expected_keys

    # Check that all values are correct
    assert metadata["tag"] == "button"
    assert metadata["aria_label"] == "Test"
    assert metadata["data_testid"] == "test-btn"
    assert metadata["role"] == "button"
    assert metadata["text"] == "Click me"
    assert metadata["dom_path"] == "button"


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
