"""
Unit tests for DOM state initialization and management.

Tests the creation of virtual DOM state from rrweb FullSnapshot events
and the accurate population of UINode mappings.
"""

import pytest
from feature_extraction.dom_state import init_dom_state
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
                                "childNodes": []
                            },
                            {
                                "id": 4,
                                "tagName": "div",
                                "attributes": {"id": "content"},
                                "textContent": "Hello World",
                                "childNodes": []
                            }
                        ]
                    }
                ]
            }
        }
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
        "data": {
            "node": {
                "id": 1,
                "type": "Document",
                "childNodes": []
            }
        }
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
                    "role": "button"
                },
                "textContent": "Submit",
                "childNodes": []
            }
        }
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
        "data": {
            "node": {
                "id": 1,
                "tagName": "div",
                "childNodes": []
            }
        }
    }
    
    node_by_id = init_dom_state(full_snapshot_event)
    
    div_node = node_by_id[1]
    assert div_node.attributes == {}
    assert div_node.text == ""


def test_init_dom_state_invalid_event_type():
    """Test that non-FullSnapshot events raise ValueError."""
    invalid_event = {
        "type": 3,  # Not a FullSnapshot
        "data": {"source": 0}
    }
    
    with pytest.raises(ValueError, match="Event must be a FullSnapshot event"):
        init_dom_state(invalid_event)


def test_init_dom_state_missing_data_node():
    """Test that events without data.node raise ValueError."""
    invalid_event = {
        "type": 2,
        "data": {}  # Missing node
    }
    
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
                        "textContent": "No ID"
                    },
                    {
                        "id": 2,
                        "tagName": "p",
                        "textContent": "Has ID"
                    }
                ]
            }
        }
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
