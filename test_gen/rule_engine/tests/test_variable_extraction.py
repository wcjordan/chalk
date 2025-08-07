"""
Unit tests for variable extraction functionality.

Tests the extract_variables function with various scenarios including
successful extractions, missing fields, error handling, and CSS-style queries.
"""

import pytest

from rule_engine.variable_resolver import extract_variables
from rule_engine.utils import query_node_text
from feature_extraction.models import UserInteraction, UINode


@pytest.fixture(name="mock_event")
def fixture_mock_event():
    """Set up test fixtures for each test method."""
    # Mock UserInteraction with typical click event data
    return UserInteraction(action="input", target_id=123, value="cats", timestamp=1000)


@pytest.fixture(name="mock_node")
def fixture_mock_node():
    """Set up test fixtures for each test method."""
    # Mock UINode with typical input field data
    return UINode(
        id=123,
        tag="input",
        attributes={
            "placeholder": "Search...",
            "type": "text",
            "name": "search_query",
        },
        text="Search field",
        parent=456,
    )


def test_extract_event_value(mock_event, mock_node):
    """Test extraction of event.value."""
    variable_map = {"input_value": "event.value"}
    result = extract_variables(variable_map, mock_event, mock_node)

    assert result == {"input_value": "cats"}


def test_extract_node_text(mock_event, mock_node):
    """Test extraction of node.text."""
    variable_map = {"node_text": "node.text"}
    result = extract_variables(variable_map, mock_event, mock_node)

    assert result == {"node_text": "Search field"}


def test_extract_node_attribute(mock_event, mock_node):
    """Test extraction of node attributes."""
    variable_map = {"placeholder": "node.attributes.placeholder"}
    result = extract_variables(variable_map, mock_event, mock_node)

    assert result == {"placeholder": "Search..."}


def test_extract_multiple_variables(mock_event, mock_node):
    """Test extraction of multiple variables in one call."""
    variable_map = {
        "input_value": "event.value",
        "placeholder": "node.attributes.placeholder",
        "node_text": "node.text",
        "field_type": "node.attributes.type",
    }
    result = extract_variables(variable_map, mock_event, mock_node)

    expected = {
        "input_value": "cats",
        "placeholder": "Search...",
        "node_text": "Search field",
        "field_type": "text",
    }
    assert result == expected


def test_missing_attribute_returns_none(mock_event, mock_node):
    """Test that missing attributes return None."""
    variable_map = {"missing_attr": "node.attributes.nonexistent"}
    result = extract_variables(variable_map, mock_event, mock_node)

    assert result == {"missing_attr": None}


def test_missing_event_field_returns_none(mock_event, mock_node):
    """Test that missing event fields return None."""
    variable_map = {"missing_field": "event.nonexistent"}
    result = extract_variables(variable_map, mock_event, mock_node)

    assert result == {"missing_field": None}


def test_missing_node_field_returns_none(mock_event, mock_node):
    """Test that missing node fields return None."""
    variable_map = {"missing_field": "node.nonexistent"}
    result = extract_variables(variable_map, mock_event, mock_node)

    assert result == {"missing_field": None}


def test_invalid_path_root_returns_none(mock_event, mock_node):
    """Test that invalid path roots return None."""
    variable_map = {"invalid": "invalid_root.field"}
    result = extract_variables(variable_map, mock_event, mock_node)

    assert result == {"invalid": None}


def test_deeply_nested_invalid_path_returns_none(mock_event, mock_node):
    """Test that deeply nested invalid paths return None."""
    variable_map = {"invalid": "node.foo.bar.baz"}
    result = extract_variables(variable_map, mock_event, mock_node)

    assert result == {"invalid": None}


def test_single_part_path_returns_none(mock_event, mock_node):
    """Test that single-part paths return None."""
    variable_map = {"invalid": "event"}
    result = extract_variables(variable_map, mock_event, mock_node)

    assert result == {"invalid": None}


def test_empty_path_returns_none(mock_event, mock_node):
    """Test that empty paths return None."""
    variable_map = {"invalid": ""}
    result = extract_variables(variable_map, mock_event, mock_node)

    assert result == {"invalid": None}


def test_event_action_extraction(mock_event, mock_node):
    """Test extraction of event.action."""
    variable_map = {"action_type": "event.action"}
    result = extract_variables(variable_map, mock_event, mock_node)

    assert result == {"action_type": "input"}


def test_event_timestamp_extraction(mock_event, mock_node):
    """Test extraction of event.timestamp."""
    variable_map = {"event_time": "event.timestamp"}
    result = extract_variables(variable_map, mock_event, mock_node)

    assert result == {"event_time": 1000}


def test_node_id_extraction(mock_event, mock_node):
    """Test extraction of node.id."""
    variable_map = {"node_id": "node.id"}
    result = extract_variables(variable_map, mock_event, mock_node)

    assert result == {"node_id": 123}


def test_node_tag_extraction(mock_event, mock_node):
    """Test extraction of node.tag."""
    variable_map = {"element_tag": "node.tag"}
    result = extract_variables(variable_map, mock_event, mock_node)

    assert result == {"element_tag": "input"}


def test_empty_variable_map(mock_event, mock_node):
    """Test that empty variable map returns empty result."""
    variable_map = {}
    result = extract_variables(variable_map, mock_event, mock_node)

    assert not result


def test_node_with_empty_attributes(mock_event):
    """Test extraction from node with empty attributes."""
    empty_node = UINode(id=789, tag="div", attributes={}, text="", parent=None)

    variable_map = {"missing_attr": "node.attributes.placeholder"}
    result = extract_variables(variable_map, mock_event, empty_node)

    assert result == {"missing_attr": None}


def test_event_with_none_value(mock_node):
    """Test extraction from event with None value."""
    none_event = UserInteraction(
        action="click", target_id=456, value=None, timestamp=2000
    )

    variable_map = {"event_value": "event.value"}
    result = extract_variables(variable_map, none_event, mock_node)

    assert result == {"event_value": None}


def test_event_with_complex_value(mock_node):
    """Test extraction from event with complex value (dict/list)."""
    complex_event = UserInteraction(
        action="scroll", target_id=789, value={"x": 100, "y": 200}, timestamp=3000
    )

    variable_map = {"scroll_data": "event.value"}
    result = extract_variables(variable_map, complex_event, mock_node)

    assert result == {"scroll_data": {"x": 100, "y": 200}}


def test_mixed_valid_and_invalid_paths(mock_event, mock_node):
    """Test extraction with mix of valid and invalid paths."""
    variable_map = {
        "valid_value": "event.value",
        "invalid_field": "event.nonexistent",
        "valid_placeholder": "node.attributes.placeholder",
        "invalid_attr": "node.attributes.missing",
    }
    result = extract_variables(variable_map, mock_event, mock_node)

    expected = {
        "valid_value": "cats",
        "invalid_field": None,
        "valid_placeholder": "Search...",
        "invalid_attr": None,
    }
    assert result == expected


@pytest.fixture(name="mock_dom_tree")
def fixture_mock_dom_tree():
    """Create a mock DOM tree for testing CSS-style queries."""
    # Create nodes:
    # root (div, id=1)
    #   ├── header (div, id=2)
    #   │   └── title (span, id=3, text="Page Title")
    #   └── content (div, id=4)
    #       ├── form (form, id=5)
    #       │   ├── label (label, id=6, text="Search:")
    #       │   └── input (input, id=7, text="")
    #       └── footer (span, id=8, text="Footer text")

    root = UINode(id=1, tag="div", attributes={"class": "root"}, text="", parent=None)
    header = UINode(id=2, tag="div", attributes={"class": "header"}, text="", parent=1)
    title = UINode(id=3, tag="span", attributes={}, text="Page Title", parent=2)
    content = UINode(
        id=4, tag="div", attributes={"class": "content"}, text="", parent=1
    )
    form = UINode(id=5, tag="form", attributes={}, text="", parent=4)
    label = UINode(id=6, tag="label", attributes={}, text="Search:", parent=5)
    input_field = UINode(
        id=7, tag="input", attributes={"type": "text"}, text="", parent=5
    )
    footer = UINode(
        id=8, tag="span", attributes={"class": "footer"}, text="Footer text", parent=4
    )

    all_nodes = [root, header, title, content, form, label, input_field, footer]

    return {"root": root, "all_nodes": all_nodes}


def test_query_node_text_simple_tag_match(mock_dom_tree):
    """Test query_node_text with simple tag selector."""
    root = mock_dom_tree["root"]
    all_nodes = mock_dom_tree["all_nodes"]

    # Should find the first span (title)
    result = query_node_text(root, all_nodes, "span")
    assert result == "Page Title"


def test_query_node_text_direct_child_selector(mock_dom_tree):
    """Test query_node_text with direct child selector using '>'."""
    root = mock_dom_tree["root"]
    all_nodes = mock_dom_tree["all_nodes"]

    # Should find span that is direct child of div > div (content > form doesn't have direct span child)
    # But div (header) > span should match
    result = query_node_text(root, all_nodes, "div > span")
    assert result == "Page Title"  # First match is header > title


def test_query_node_text_nested_selector(mock_dom_tree):
    """Test query_node_text with nested selector."""
    root = mock_dom_tree["root"]
    all_nodes = mock_dom_tree["all_nodes"]

    # Should find label that is child of form
    result = query_node_text(root, all_nodes, "form > label")
    assert result == "Search:"


def test_query_node_text_no_match(mock_dom_tree):
    """Test query_node_text when no nodes match the selector."""
    root = mock_dom_tree["root"]
    all_nodes = mock_dom_tree["all_nodes"]

    # Should return None for non-existent tag
    result = query_node_text(root, all_nodes, "button")
    assert result is None


def test_query_node_text_empty_selector(mock_dom_tree):
    """Test query_node_text with empty selector."""
    root = mock_dom_tree["root"]
    all_nodes = mock_dom_tree["all_nodes"]

    result = query_node_text(root, all_nodes, "")
    assert result is None


def test_query_node_text_invalid_selector(mock_dom_tree):
    """Test query_node_text with invalid selector."""
    root = mock_dom_tree["root"]
    all_nodes = mock_dom_tree["all_nodes"]

    # Invalid selector with empty part after '>'
    result = query_node_text(root, all_nodes, "div > ")
    assert result is None


def test_extract_variables_with_node_query(mock_event, mock_dom_tree):
    """Test extract_variables with node.query().text expressions."""
    all_nodes = mock_dom_tree["all_nodes"]
    # Use the form node as the root for this test
    form_node = next(node for node in all_nodes if node.tag == "form")

    variable_map = {
        "label_text": 'node.query("label").text',
        "regular_field": "node.tag",
    }

    result = extract_variables(variable_map, mock_event, form_node, all_nodes)

    expected = {"label_text": "Search:", "regular_field": "form"}
    assert result == expected


def test_extract_variables_with_node_query_single_quotes(mock_event, mock_dom_tree):
    """Test extract_variables with node.query().text using single quotes."""
    all_nodes = mock_dom_tree["all_nodes"]
    root = mock_dom_tree["root"]

    variable_map = {"page_title": "node.query('span').text"}

    result = extract_variables(variable_map, mock_event, root, all_nodes)

    assert result == {"page_title": "Page Title"}


def test_extract_variables_with_node_query_no_match(mock_event, mock_dom_tree):
    """Test extract_variables with node.query().text when no nodes match."""
    all_nodes = mock_dom_tree["all_nodes"]
    root = mock_dom_tree["root"]

    variable_map = {"missing": 'node.query("button").text'}

    result = extract_variables(variable_map, mock_event, root, all_nodes)

    assert result == {"missing": None}


def test_extract_variables_with_node_query_complex_selector(mock_event, mock_dom_tree):
    """Test extract_variables with complex CSS selector."""
    all_nodes = mock_dom_tree["all_nodes"]
    root = mock_dom_tree["root"]

    variable_map = {
        "form_label": 'node.query("form > label").text',
        "header_title": 'node.query("div > span").text',
    }

    result = extract_variables(variable_map, mock_event, root, all_nodes)

    expected = {
        "form_label": "Search:",
        "header_title": "Page Title",  # First match from header > title
    }
    assert result == expected


def test_extract_variables_node_query_without_all_nodes(mock_event, mock_node):
    """Test that node.query() expressions return None when all_nodes is not provided."""
    variable_map = {"child_text": 'node.query("span").text'}

    # Call without all_nodes parameter
    result = extract_variables(variable_map, mock_event, mock_node)

    assert result == {"child_text": None}


def test_extract_variables_invalid_query_expression(mock_event, mock_dom_tree):
    """Test extract_variables with invalid node.query() expression."""
    all_nodes = mock_dom_tree["all_nodes"]
    root = mock_dom_tree["root"]

    variable_map = {
        "invalid1": "node.query('span')",  # Missing .text
        "invalid2": 'node.query("span").value',  # Wrong method
        "invalid3": 'node.find("span").text',  # Wrong method name
    }

    result = extract_variables(variable_map, mock_event, root, all_nodes)

    expected = {"invalid1": None, "invalid2": None, "invalid3": None}
    assert result == expected


def test_extract_variables_mixed_expressions(mock_event, mock_dom_tree):
    """Test extract_variables with mix of regular paths and node.query() expressions."""
    all_nodes = mock_dom_tree["all_nodes"]
    root = mock_dom_tree["root"]

    variable_map = {
        "event_action": "event.action",
        "node_tag": "node.tag",
        "query_result": 'node.query("span").text',
        "missing_field": "event.nonexistent",
    }

    result = extract_variables(variable_map, mock_event, root, all_nodes)

    expected = {
        "event_action": "input",
        "node_tag": "div",
        "query_result": "Page Title",
        "missing_field": None,
    }
    assert result == expected
