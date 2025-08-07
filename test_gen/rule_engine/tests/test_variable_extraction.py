"""
Unit tests for variable extraction functionality.

Tests the extract_variables function with various scenarios including
successful extractions, missing fields, and error handling.
"""

import pytest
from rule_engine.variable_resolver import extract_variables
from feature_extraction.models import UserInteraction, UINode


class TestExtractVariables:
    """Test cases for the extract_variables function."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        # Mock UserInteraction with typical click event data
        self.event = UserInteraction(
            action="input",
            target_id=123,
            value="cats",
            timestamp=1000
        )
        
        # Mock UINode with typical input field data
        self.node = UINode(
            id=123,
            tag="input",
            attributes={
                "placeholder": "Search...",
                "type": "text",
                "name": "search_query"
            },
            text="Search field",
            parent=456
        )
    
    def test_extract_event_value(self):
        """Test extraction of event.value."""
        variable_map = {"input_value": "event.value"}
        result = extract_variables(variable_map, self.event, self.node)
        
        assert result == {"input_value": "cats"}
    
    def test_extract_node_text(self):
        """Test extraction of node.text."""
        variable_map = {"node_text": "node.text"}
        result = extract_variables(variable_map, self.event, self.node)
        
        assert result == {"node_text": "Search field"}
    
    def test_extract_node_attribute(self):
        """Test extraction of node attributes."""
        variable_map = {"placeholder": "node.attributes.placeholder"}
        result = extract_variables(variable_map, self.event, self.node)
        
        assert result == {"placeholder": "Search..."}
    
    def test_extract_multiple_variables(self):
        """Test extraction of multiple variables in one call."""
        variable_map = {
            "input_value": "event.value",
            "placeholder": "node.attributes.placeholder",
            "node_text": "node.text",
            "field_type": "node.attributes.type"
        }
        result = extract_variables(variable_map, self.event, self.node)
        
        expected = {
            "input_value": "cats",
            "placeholder": "Search...",
            "node_text": "Search field",
            "field_type": "text"
        }
        assert result == expected
    
    def test_missing_attribute_returns_none(self):
        """Test that missing attributes return None."""
        variable_map = {"missing_attr": "node.attributes.nonexistent"}
        result = extract_variables(variable_map, self.event, self.node)
        
        assert result == {"missing_attr": None}
    
    def test_missing_event_field_returns_none(self):
        """Test that missing event fields return None."""
        variable_map = {"missing_field": "event.nonexistent"}
        result = extract_variables(variable_map, self.event, self.node)
        
        assert result == {"missing_field": None}
    
    def test_missing_node_field_returns_none(self):
        """Test that missing node fields return None."""
        variable_map = {"missing_field": "node.nonexistent"}
        result = extract_variables(variable_map, self.event, self.node)
        
        assert result == {"missing_field": None}
    
    def test_invalid_path_root_returns_none(self):
        """Test that invalid path roots return None."""
        variable_map = {"invalid": "invalid_root.field"}
        result = extract_variables(variable_map, self.event, self.node)
        
        assert result == {"invalid": None}
    
    def test_deeply_nested_invalid_path_returns_none(self):
        """Test that deeply nested invalid paths return None."""
        variable_map = {"invalid": "node.foo.bar.baz"}
        result = extract_variables(variable_map, self.event, self.node)
        
        assert result == {"invalid": None}
    
    def test_single_part_path_returns_none(self):
        """Test that single-part paths return None."""
        variable_map = {"invalid": "event"}
        result = extract_variables(variable_map, self.event, self.node)
        
        assert result == {"invalid": None}
    
    def test_empty_path_returns_none(self):
        """Test that empty paths return None."""
        variable_map = {"invalid": ""}
        result = extract_variables(variable_map, self.event, self.node)
        
        assert result == {"invalid": None}
    
    def test_event_action_extraction(self):
        """Test extraction of event.action."""
        variable_map = {"action_type": "event.action"}
        result = extract_variables(variable_map, self.event, self.node)
        
        assert result == {"action_type": "input"}
    
    def test_event_timestamp_extraction(self):
        """Test extraction of event.timestamp."""
        variable_map = {"event_time": "event.timestamp"}
        result = extract_variables(variable_map, self.event, self.node)
        
        assert result == {"event_time": 1000}
    
    def test_node_id_extraction(self):
        """Test extraction of node.id."""
        variable_map = {"node_id": "node.id"}
        result = extract_variables(variable_map, self.event, self.node)
        
        assert result == {"node_id": 123}
    
    def test_node_tag_extraction(self):
        """Test extraction of node.tag."""
        variable_map = {"element_tag": "node.tag"}
        result = extract_variables(variable_map, self.event, self.node)
        
        assert result == {"element_tag": "input"}
    
    def test_empty_variable_map(self):
        """Test that empty variable map returns empty result."""
        variable_map = {}
        result = extract_variables(variable_map, self.event, self.node)
        
        assert result == {}
    
    def test_node_with_empty_attributes(self):
        """Test extraction from node with empty attributes."""
        empty_node = UINode(
            id=789,
            tag="div",
            attributes={},
            text="",
            parent=None
        )
        
        variable_map = {"missing_attr": "node.attributes.placeholder"}
        result = extract_variables(variable_map, self.event, empty_node)
        
        assert result == {"missing_attr": None}
    
    def test_event_with_none_value(self):
        """Test extraction from event with None value."""
        none_event = UserInteraction(
            action="click",
            target_id=456,
            value=None,
            timestamp=2000
        )
        
        variable_map = {"event_value": "event.value"}
        result = extract_variables(variable_map, none_event, self.node)
        
        assert result == {"event_value": None}
    
    def test_event_with_complex_value(self):
        """Test extraction from event with complex value (dict/list)."""
        complex_event = UserInteraction(
            action="scroll",
            target_id=789,
            value={"x": 100, "y": 200},
            timestamp=3000
        )
        
        variable_map = {"scroll_data": "event.value"}
        result = extract_variables(variable_map, complex_event, self.node)
        
        assert result == {"scroll_data": {"x": 100, "y": 200}}
    
    def test_mixed_valid_and_invalid_paths(self):
        """Test extraction with mix of valid and invalid paths."""
        variable_map = {
            "valid_value": "event.value",
            "invalid_field": "event.nonexistent",
            "valid_placeholder": "node.attributes.placeholder",
            "invalid_attr": "node.attributes.missing"
        }
        result = extract_variables(variable_map, self.event, self.node)
        
        expected = {
            "valid_value": "cats",
            "invalid_field": None,
            "valid_placeholder": "Search...",
            "invalid_attr": None
        }
        assert result == expected