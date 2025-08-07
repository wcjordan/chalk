"""
Tests for the rule matcher functionality.

This module tests the core matching logic that determines if UserInteraction
and UINode pairs match Rule conditions.
"""

from typing import Dict, Any

from rule_engine.matcher import rule_matches_event_node, apply_rule_to_event_and_node
from rule_engine.models import Rule
from feature_extraction.models import UserInteraction, UINode


def create_test_rule(
    rule_id: str = "test_rule",
    match_event: Dict[str, Any] = None,
    match_node: Dict[str, Any] = None,
    action_id: str = "test_action",
    confidence: float = 0.9,
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
        action_id=action_id,
    )


def create_test_event(
    action: str = "click", target_id: int = 1, value: Any = None, timestamp: int = 1000
) -> UserInteraction:
    """Helper function to create test user interactions."""
    return UserInteraction(
        action=action, target_id=target_id, value=value, timestamp=timestamp
    )


def create_test_node(
    node_id: int = 1,
    tag: str = "button",
    attributes: Dict[str, str] = None,
    text: str = "Click me",
    parent: int = None,
) -> UINode:
    """Helper function to create test UI nodes."""
    if attributes is None:
        attributes = {}

    return UINode(id=node_id, tag=tag, attributes=attributes, text=text, parent=parent)


class TestRuleMatchesEventNode:
    """Tests for rule_matches_event_node function."""

    def test_positive_case_full_match(self):
        """Test that a rule matches when both event and node conditions are met."""
        rule = create_test_rule(
            match_event={"action": "input"},
            match_node={"tag": "input", "attributes": {"type": "search"}},
        )

        event = create_test_event(action="input")
        node = create_test_node(
            tag="input", attributes={"type": "search", "placeholder": "Search..."}
        )

        assert rule_matches_event_node(rule, event, node) is True

    def test_negative_case_action_mismatch(self):
        """Test that a rule doesn't match when event action doesn't match."""
        rule = create_test_rule(
            match_event={"action": "click"}, match_node={"tag": "button"}
        )

        event = create_test_event(action="input")  # Different action
        node = create_test_node(tag="button")

        assert rule_matches_event_node(rule, event, node) is False

    def test_negative_case_tag_mismatch(self):
        """Test that a rule doesn't match when node tag doesn't match."""
        rule = create_test_rule(
            match_event={"action": "click"}, match_node={"tag": "button"}
        )

        event = create_test_event(action="click")
        node = create_test_node(tag="div")  # Different tag

        assert rule_matches_event_node(rule, event, node) is False

    def test_negative_case_missing_attribute(self):
        """Test that a rule doesn't match when required attribute is missing."""
        rule = create_test_rule(
            match_event={"action": "click"},
            match_node={"tag": "input", "attributes": {"type": "submit"}},
        )

        event = create_test_event(action="click")
        node = create_test_node(
            tag="input",
            attributes={"placeholder": "Enter text"},  # Missing 'type' attribute
        )

        assert rule_matches_event_node(rule, event, node) is False

    def test_negative_case_incorrect_attribute_value(self):
        """Test that a rule doesn't match when attribute value is incorrect."""
        rule = create_test_rule(
            match_event={"action": "input"},
            match_node={"tag": "input", "attributes": {"type": "email"}},
        )

        event = create_test_event(action="input")
        node = create_test_node(
            tag="input", attributes={"type": "text"}  # Wrong value for 'type'
        )

        assert rule_matches_event_node(rule, event, node) is False

    def test_empty_match_conditions(self):
        """Test that a rule with empty match conditions matches everything."""
        rule = create_test_rule(match_event={}, match_node={})

        event = create_test_event(action="scroll")
        node = create_test_node(tag="div", attributes={"class": "container"})

        assert rule_matches_event_node(rule, event, node) is True

    def test_no_event_conditions(self):
        """Test matching when only node conditions are specified."""
        rule = create_test_rule(match_node={"tag": "button"})

        event = create_test_event(action="click")
        node = create_test_node(tag="button")

        assert rule_matches_event_node(rule, event, node) is True

    def test_no_node_conditions(self):
        """Test matching when only event conditions are specified."""
        rule = create_test_rule(match_event={"action": "input"})

        event = create_test_event(action="input")
        node = create_test_node(tag="input")

        assert rule_matches_event_node(rule, event, node) is True

    def test_multiple_attributes_match(self):
        """Test matching with multiple required attributes."""
        rule = create_test_rule(
            match_event={"action": "click"},
            match_node={
                "tag": "button",
                "attributes": {"type": "submit", "class": "btn-primary"},
            },
        )

        event = create_test_event(action="click")
        node = create_test_node(
            tag="button",
            attributes={
                "type": "submit",
                "class": "btn-primary",
                "id": "submit-btn",  # Extra attribute should not affect matching
            },
        )

        assert rule_matches_event_node(rule, event, node) is True

    def test_multiple_attributes_partial_match(self):
        """Test that partial attribute matching fails."""
        rule = create_test_rule(
            match_event={"action": "click"},
            match_node={
                "tag": "button",
                "attributes": {"type": "submit", "class": "btn-primary"},
            },
        )

        event = create_test_event(action="click")
        node = create_test_node(
            tag="button",
            attributes={
                "type": "submit",
                # Missing 'class' attribute
            },
        )

        assert rule_matches_event_node(rule, event, node) is False

    def test_complex_realistic_scenario(self):
        """Test a complex realistic search input scenario."""
        rule = create_test_rule(
            rule_id="search_input_rule",
            match_event={"action": "input"},
            match_node={
                "tag": "input",
                "attributes": {"type": "search", "name": "query"},
            },
            action_id="search_query",
        )

        event = create_test_event(
            action="input",
            target_id=123,
            value="machine learning",
            timestamp=1642500000000,
        )

        node = create_test_node(
            node_id=123,
            tag="input",
            attributes={
                "type": "search",
                "name": "query",
                "placeholder": "Search for anything...",
                "aria-label": "Search input",
            },
            text="",
        )

        assert rule_matches_event_node(rule, event, node) is True


class TestApplyRuleToEventAndNode:
    """Tests for apply_rule_to_event_and_node function."""

    def test_successful_match_returns_detected_action(self):
        """Test that a successful match returns a properly structured DetectedAction."""
        rule = create_test_rule(
            rule_id="search_rule",
            match_event={"action": "input"},
            match_node={"tag": "input", "attributes": {"type": "search"}},
            action_id="search_query",
            confidence=0.85,
        )
        rule.variables = {
            "search_term": "event.value",
            "placeholder": "node.attributes.placeholder",
        }

        event = create_test_event(
            action="input",
            target_id=123,
            value="cats",
            timestamp=1642500000000,
        )

        node = create_test_node(
            node_id=123,
            tag="input",
            attributes={"type": "search", "placeholder": "Search..."},
            text="",
        )

        event_index = 5
        result = apply_rule_to_event_and_node(rule, event, node, event_index)

        assert result is not None
        assert result.action_id == "search_query"
        assert result.timestamp == 1642500000000
        assert result.confidence == 0.85
        assert result.rule_id == "search_rule"
        assert result.variables == {"search_term": "cats", "placeholder": "Search..."}
        assert result.target_element == node
        assert result.related_events == [5]

    def test_failed_match_returns_none(self):
        """Test that a failed match returns None."""
        rule = create_test_rule(
            match_event={"action": "click"},
            match_node={"tag": "button"},
        )

        event = create_test_event(action="input")  # Different action
        node = create_test_node(tag="button")
        event_index = 10

        result = apply_rule_to_event_and_node(rule, event, node, event_index)

        assert result is None

    def test_match_with_empty_variables(self):
        """Test successful match with empty variables dictionary."""
        rule = create_test_rule(
            rule_id="simple_click",
            match_event={"action": "click"},
            match_node={"tag": "button"},
            action_id="button_click",
            confidence=0.9,
        )
        rule.variables = {}

        event = create_test_event(
            action="click",
            timestamp=1000000000,
        )

        node = create_test_node(tag="button", text="Submit")
        event_index = 0

        result = apply_rule_to_event_and_node(rule, event, node, event_index)

        assert result is not None
        assert result.action_id == "button_click"
        assert result.timestamp == 1000000000
        assert result.confidence == 0.9
        assert result.rule_id == "simple_click"
        assert not result.variables
        assert result.target_element == node
        assert result.related_events == [0]

    def test_match_with_unresolvable_variables(self):
        """Test that unresolvable variables are handled gracefully."""
        rule = create_test_rule(
            rule_id="test_rule",
            match_event={"action": "input"},
            match_node={"tag": "input"},
            action_id="input_action",
        )
        rule.variables = {
            "valid_var": "event.value",
            "invalid_var": "event.nonexistent",
            "another_invalid": "node.missing.field",
        }

        event = create_test_event(action="input", value="test_value")
        node = create_test_node(tag="input")
        event_index = 3

        result = apply_rule_to_event_and_node(rule, event, node, event_index)

        assert result is not None
        assert result.variables["valid_var"] == "test_value"
        assert result.variables["invalid_var"] is None
        assert result.variables["another_invalid"] is None
