"""
Tests for the rule matcher functionality.

This module tests the core matching logic that determines if UserInteraction
and UINode pairs match Rule conditions.
"""

from typing import Dict, Any, Optional

from rule_engine.matcher import (
    rule_matches_event_node,
    apply_rule_to_event_and_node,
    detect_actions_in_session,
)
from rule_engine.models import Rule
from rrweb_util.user_interaction.models import UserInteraction
from rrweb_util.dom_state.models import UINode


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
    action: str = "click",
    target_id: int = 1,
    target_node: Optional[UINode] = None,
    value: Any = None,
    timestamp: int = 1000,
) -> UserInteraction:
    """Helper function to create test user interactions."""
    if target_node is None:
        target_node = create_test_node(node_id=target_id)
    return UserInteraction(
        action=action,
        target_id=target_id,
        target_node=target_node.to_dict(),
        value=value,
        timestamp=timestamp,
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

        node = create_test_node(
            tag="input", attributes={"type": "search", "placeholder": "Search..."}
        )
        event = create_test_event(action="input", target_node=node)

        assert rule_matches_event_node(rule, event) is True

    def test_negative_case_action_mismatch(self):
        """Test that a rule doesn't match when event action doesn't match."""
        rule = create_test_rule(
            match_event={"action": "click"}, match_node={"tag": "button"}
        )

        node = create_test_node(tag="button")
        event = create_test_event(action="input", target_node=node)  # Different action

        assert rule_matches_event_node(rule, event) is False

    def test_negative_case_tag_mismatch(self):
        """Test that a rule doesn't match when node tag doesn't match."""
        rule = create_test_rule(
            match_event={"action": "click"}, match_node={"tag": "button"}
        )

        node = create_test_node(tag="div")  # Different tag
        event = create_test_event(action="click", target_node=node)

        assert rule_matches_event_node(rule, event) is False

    def test_negative_case_missing_attribute(self):
        """Test that a rule doesn't match when required attribute is missing."""
        rule = create_test_rule(
            match_event={"action": "click"},
            match_node={"tag": "input", "attributes": {"type": "submit"}},
        )

        node = create_test_node(
            tag="input",
            attributes={"placeholder": "Enter text"},  # Missing 'type' attribute
        )
        event = create_test_event(action="click", target_node=node)

        assert rule_matches_event_node(rule, event) is False

    def test_negative_case_incorrect_attribute_value(self):
        """Test that a rule doesn't match when attribute value is incorrect."""
        rule = create_test_rule(
            match_event={"action": "input"},
            match_node={"tag": "input", "attributes": {"type": "email"}},
        )

        node = create_test_node(
            tag="input", attributes={"type": "text"}  # Wrong value for 'type'
        )
        event = create_test_event(action="input", target_node=node)

        assert rule_matches_event_node(rule, event) is False

    def test_empty_match_conditions(self):
        """Test that a rule with empty match conditions matches everything."""
        rule = create_test_rule(match_event={}, match_node={})

        node = create_test_node(tag="div", attributes={"class": "container"})
        event = create_test_event(action="scroll", target_node=node)

        assert rule_matches_event_node(rule, event) is True

    def test_no_event_conditions(self):
        """Test matching when only node conditions are specified."""
        rule = create_test_rule(match_node={"tag": "button"})

        node = create_test_node(tag="button")
        event = create_test_event(action="click", target_node=node)

        assert rule_matches_event_node(rule, event) is True

    def test_no_node_conditions(self):
        """Test matching when only event conditions are specified."""
        rule = create_test_rule(match_event={"action": "input"})

        node = create_test_node(tag="input")
        event = create_test_event(action="input", target_node=node)

        assert rule_matches_event_node(rule, event) is True

    def test_multiple_attributes_match(self):
        """Test matching with multiple required attributes."""
        rule = create_test_rule(
            match_event={"action": "click"},
            match_node={
                "tag": "button",
                "attributes": {"type": "submit", "class": "btn-primary"},
            },
        )

        node = create_test_node(
            tag="button",
            attributes={
                "type": "submit",
                "class": "btn-primary",
                "id": "submit-btn",  # Extra attribute should not affect matching
            },
        )
        event = create_test_event(action="click", target_node=node)

        assert rule_matches_event_node(rule, event) is True

    def test_multiple_attributes_partial_match(self):
        """Test that partial attribute matching fails."""
        rule = create_test_rule(
            match_event={"action": "click"},
            match_node={
                "tag": "button",
                "attributes": {"type": "submit", "class": "btn-primary"},
            },
        )

        node = create_test_node(
            tag="button",
            attributes={
                "type": "submit",
                # Missing 'class' attribute
            },
        )
        event = create_test_event(action="click", target_node=node)

        assert rule_matches_event_node(rule, event) is False

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
        event = create_test_event(
            action="input",
            target_id=123,
            target_node=node,
            value="machine learning",
            timestamp=1642500000000,
        )

        assert rule_matches_event_node(rule, event) is True


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

        node = create_test_node(
            node_id=123,
            tag="input",
            attributes={"type": "search", "placeholder": "Search..."},
            text="",
        )
        event = create_test_event(
            action="input",
            target_id=123,
            target_node=node,
            value="cats",
            timestamp=1642500000000,
        )

        event_index = 5
        result = apply_rule_to_event_and_node(rule, event, event_index)

        assert result is not None
        assert result.action_id == "search_query"
        assert result.timestamp == 1642500000000
        assert result.confidence == 0.85
        assert result.rule_id == "search_rule"
        assert result.variables == {"search_term": "cats", "placeholder": "Search..."}
        assert result.target_element == node.to_dict()
        assert result.related_events == [5]

    def test_failed_match_returns_none(self):
        """Test that a failed match returns None."""
        rule = create_test_rule(
            match_event={"action": "click"},
            match_node={"tag": "button"},
        )

        node = create_test_node(tag="button")
        event = create_test_event(action="input", target_node=node)  # Different action
        event_index = 10

        result = apply_rule_to_event_and_node(rule, event, event_index)

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

        node = create_test_node(tag="button", text="Submit")
        event = create_test_event(
            action="click",
            target_node=node,
            timestamp=1000000000,
        )

        event_index = 0

        result = apply_rule_to_event_and_node(rule, event, event_index)

        assert result is not None
        assert result.action_id == "button_click"
        assert result.timestamp == 1000000000
        assert result.confidence == 0.9
        assert result.rule_id == "simple_click"
        assert not result.variables
        assert result.target_element == node.to_dict()
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

        node = create_test_node(tag="input")
        event = create_test_event(action="input", target_node=node, value="test_value")
        event_index = 3

        result = apply_rule_to_event_and_node(rule, event, event_index)

        assert result is not None
        assert result.variables["valid_var"] == "test_value"
        assert result.variables["invalid_var"] is None
        assert result.variables["another_invalid"] is None


class TestDetectActionsInSession:
    """Tests for detect_actions_in_session function."""

    def test_end_to_end_single_match(self, create_processed_session):
        """Test end-to-end detection with one matching rule and interaction."""
        # Create a search input rule
        search_rule = create_test_rule(
            rule_id="search_input_rule",
            match_event={"action": "input"},
            match_node={"tag": "input", "attributes": {"type": "search"}},
            action_id="search_query",
            confidence=0.9,
        )
        search_rule.variables = {"search_term": "event.value"}

        # Create mock session with one user interaction and corresponding UI node
        node = create_test_node(
            node_id=123,
            tag="input",
            attributes={"type": "search", "name": "query"},
            text="",
        )
        interaction = create_test_event(
            action="input",
            target_id=123,
            target_node=node,
            value="machine learning",
            timestamp=1642500000000,
        )

        session = create_processed_session(interactions=[interaction])

        rules = [search_rule]

        # Execute the function
        result = detect_actions_in_session(session, rules)

        # Verify results
        assert len(result) == 1
        detected_action = result[0]
        assert detected_action.action_id == "search_query"
        assert detected_action.rule_id == "search_input_rule"
        assert detected_action.confidence == 0.9
        assert detected_action.timestamp == 1642500000000
        assert detected_action.variables == {"search_term": "machine learning"}
        assert detected_action.target_element == node.to_dict()
        assert detected_action.related_events == [0]

    def test_end_to_end_multiple_interactions_and_rules(self, create_processed_session):
        """Test end-to-end detection with multiple interactions and rules."""
        # Create multiple rules
        search_rule = create_test_rule(
            rule_id="search_rule",
            match_event={"action": "input"},
            match_node={"tag": "input", "attributes": {"type": "search"}},
            action_id="search_query",
            confidence=0.85,
        )
        search_rule.variables = {"query": "event.value"}

        button_rule = create_test_rule(
            rule_id="button_rule",
            match_event={"action": "click"},
            match_node={"tag": "button", "attributes": {"type": "submit"}},
            action_id="submit_form",
            confidence=0.95,
        )
        button_rule.variables = {"button_text": "node.text"}

        # Create multiple interactions and nodes
        search_node = create_test_node(
            node_id=100,
            tag="input",
            attributes={"type": "search"},
            text="",
        )

        button_node = create_test_node(
            node_id=200,
            tag="button",
            attributes={"type": "submit"},
            text="Search",
        )

        search_interaction = create_test_event(
            action="input",
            target_id=100,
            target_node=search_node,
            value="python tutorials",
            timestamp=1000,
        )

        click_interaction = create_test_event(
            action="click",
            target_id=200,
            target_node=button_node,
            timestamp=2000,
        )

        session = create_processed_session(
            interactions=[search_interaction, click_interaction],
        )

        rules = [search_rule, button_rule]

        # Execute the function
        result = detect_actions_in_session(session, rules)

        # Verify results
        assert len(result) == 2

        # Find the search action
        search_action = next(
            (action for action in result if action.action_id == "search_query"), None
        )
        assert search_action is not None
        assert search_action.rule_id == "search_rule"
        assert search_action.confidence == 0.85
        assert search_action.variables == {"query": "python tutorials"}
        assert search_action.related_events == [0]

        # Find the button action
        button_action = next(
            (action for action in result if action.action_id == "submit_form"), None
        )
        assert button_action is not None
        assert button_action.rule_id == "button_rule"
        assert button_action.confidence == 0.95
        assert button_action.variables == {"button_text": "Search"}
        assert button_action.related_events == [1]

    def test_no_matches_empty_result(self, create_processed_session):
        """Test that non-matching rules return empty result."""
        # Create a rule that won't match
        rule = create_test_rule(
            rule_id="no_match_rule",
            match_event={"action": "hover"},  # Looking for hover
            match_node={"tag": "div"},
            action_id="hover_action",
        )

        # Create interaction that won't match (click instead of hover)
        node = create_test_node(
            node_id=123,
            tag="button",  # Different tag than rule expects
        )

        interaction = create_test_event(
            action="click",
            target_id=123,
            target_node=node,
        )

        session = create_processed_session(interactions=[interaction])

        # Execute the function
        result = detect_actions_in_session(session, [rule])

        # Verify no matches
        assert len(result) == 0

    def test_empty_session_empty_result(self, create_processed_session):
        """Test that empty session returns empty result."""
        rule = create_test_rule(
            rule_id="test_rule",
            match_event={"action": "click"},
            match_node={"tag": "button"},
            action_id="click_action",
        )

        # Empty session
        session = create_processed_session(interactions=[])

        rules = [rule]

        # Execute the function
        result = detect_actions_in_session(session, rules)

        # Verify empty result
        assert len(result) == 0

    def test_empty_rules_empty_result(self, create_processed_session):
        """Test that empty rules list returns empty result."""
        # Create valid interaction and node
        node = create_test_node(node_id=123, tag="button")
        interaction = create_test_event(action="click", target_id=123, target_node=node)

        session = create_processed_session(interactions=[interaction])

        # Execute the function w/ empty rules
        result = detect_actions_in_session(session, [])

        # Verify empty result
        assert len(result) == 0
