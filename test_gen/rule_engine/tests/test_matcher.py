"""
Tests for the rule matcher functionality.

This module tests the core matching logic that determines if UserInteraction
and UINode pairs match Rule conditions.
"""

import pytest
from typing import Dict, Any

from rule_engine.matcher import rule_matches_event_node
from rule_engine.models import Rule
from feature_extraction.models import UserInteraction, UINode


def create_test_rule(
    rule_id: str = "test_rule",
    match_event: Dict[str, Any] = None,
    match_node: Dict[str, Any] = None,
    action_id: str = "test_action",
    confidence: float = 0.9
) -> Rule:
    """Helper function to create test rules."""
    match_dict = {}
    if match_event is not None:
        match_dict["event"] = match_event
    if match_node is not None:
        match_dict["node"] = match_node
    
    return Rule(
        id=rule_id,
        description="Test rule",
        match=match_dict,
        confidence=confidence,
        variables={},
        action_id=action_id
    )


def create_test_event(
    action: str = "click",
    target_id: int = 1,
    value: Any = None,
    timestamp: int = 1000
) -> UserInteraction:
    """Helper function to create test user interactions."""
    return UserInteraction(
        action=action,
        target_id=target_id,
        value=value,
        timestamp=timestamp
    )


def create_test_node(
    node_id: int = 1,
    tag: str = "button",
    attributes: Dict[str, str] = None,
    text: str = "Click me",
    parent: int = None
) -> UINode:
    """Helper function to create test UI nodes."""
    if attributes is None:
        attributes = {}
    
    return UINode(
        id=node_id,
        tag=tag,
        attributes=attributes,
        text=text,
        parent=parent
    )


class TestRuleMatchesEventNode:
    """Tests for rule_matches_event_node function."""
    
    def test_positive_case_full_match(self):
        """Test that a rule matches when both event and node conditions are met."""
        rule = create_test_rule(
            match_event={"action": "input"},
            match_node={
                "tag": "input",
                "attributes": {"type": "search"}
            }
        )
        
        event = create_test_event(action="input")
        node = create_test_node(
            tag="input",
            attributes={"type": "search", "placeholder": "Search..."}
        )
        
        assert rule_matches_event_node(rule, event, node) is True
    
    def test_negative_case_action_mismatch(self):
        """Test that a rule doesn't match when event action doesn't match."""
        rule = create_test_rule(
            match_event={"action": "click"},
            match_node={"tag": "button"}
        )
        
        event = create_test_event(action="input")  # Different action
        node = create_test_node(tag="button")
        
        assert rule_matches_event_node(rule, event, node) is False
    
    def test_negative_case_tag_mismatch(self):
        """Test that a rule doesn't match when node tag doesn't match."""
        rule = create_test_rule(
            match_event={"action": "click"},
            match_node={"tag": "button"}
        )
        
        event = create_test_event(action="click")
        node = create_test_node(tag="div")  # Different tag
        
        assert rule_matches_event_node(rule, event, node) is False
    
    def test_negative_case_missing_attribute(self):
        """Test that a rule doesn't match when required attribute is missing."""
        rule = create_test_rule(
            match_event={"action": "click"},
            match_node={
                "tag": "input",
                "attributes": {"type": "submit"}
            }
        )
        
        event = create_test_event(action="click")
        node = create_test_node(
            tag="input",
            attributes={"placeholder": "Enter text"}  # Missing 'type' attribute
        )
        
        assert rule_matches_event_node(rule, event, node) is False
    
    def test_negative_case_incorrect_attribute_value(self):
        """Test that a rule doesn't match when attribute value is incorrect."""
        rule = create_test_rule(
            match_event={"action": "input"},
            match_node={
                "tag": "input",
                "attributes": {"type": "email"}
            }
        )
        
        event = create_test_event(action="input")
        node = create_test_node(
            tag="input",
            attributes={"type": "text"}  # Wrong value for 'type'
        )
        
        assert rule_matches_event_node(rule, event, node) is False
    
    def test_empty_match_conditions(self):
        """Test that a rule with empty match conditions matches everything."""
        rule = create_test_rule(
            match_event={},
            match_node={}
        )
        
        event = create_test_event(action="scroll")
        node = create_test_node(tag="div", attributes={"class": "container"})
        
        assert rule_matches_event_node(rule, event, node) is True
    
    def test_no_event_conditions(self):
        """Test matching when only node conditions are specified."""
        rule = create_test_rule(
            match_node={"tag": "button"}
        )
        
        event = create_test_event(action="click")
        node = create_test_node(tag="button")
        
        assert rule_matches_event_node(rule, event, node) is True
    
    def test_no_node_conditions(self):
        """Test matching when only event conditions are specified."""
        rule = create_test_rule(
            match_event={"action": "input"}
        )
        
        event = create_test_event(action="input")
        node = create_test_node(tag="input")
        
        assert rule_matches_event_node(rule, event, node) is True
    
    def test_multiple_attributes_match(self):
        """Test matching with multiple required attributes."""
        rule = create_test_rule(
            match_event={"action": "click"},
            match_node={
                "tag": "button",
                "attributes": {
                    "type": "submit",
                    "class": "btn-primary"
                }
            }
        )
        
        event = create_test_event(action="click")
        node = create_test_node(
            tag="button",
            attributes={
                "type": "submit",
                "class": "btn-primary",
                "id": "submit-btn"  # Extra attribute should not affect matching
            }
        )
        
        assert rule_matches_event_node(rule, event, node) is True
    
    def test_multiple_attributes_partial_match(self):
        """Test that partial attribute matching fails."""
        rule = create_test_rule(
            match_event={"action": "click"},
            match_node={
                "tag": "button",
                "attributes": {
                    "type": "submit",
                    "class": "btn-primary"
                }
            }
        )
        
        event = create_test_event(action="click")
        node = create_test_node(
            tag="button",
            attributes={
                "type": "submit"
                # Missing 'class' attribute
            }
        )
        
        assert rule_matches_event_node(rule, event, node) is False
    
    def test_complex_realistic_scenario(self):
        """Test a complex realistic search input scenario."""
        rule = create_test_rule(
            rule_id="search_input_rule",
            match_event={"action": "input"},
            match_node={
                "tag": "input",
                "attributes": {
                    "type": "search",
                    "name": "query"
                }
            },
            action_id="search_query"
        )
        
        event = create_test_event(
            action="input",
            target_id=123,
            value="machine learning",
            timestamp=1642500000000
        )
        
        node = create_test_node(
            node_id=123,
            tag="input",
            attributes={
                "type": "search",
                "name": "query",
                "placeholder": "Search for anything...",
                "aria-label": "Search input"
            },
            text=""
        )
        
        assert rule_matches_event_node(rule, event, node) is True