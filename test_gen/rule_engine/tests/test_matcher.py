"""
Tests for the rule matcher functionality.

This module tests the core matching logic that determines if UserInteraction
and UINode pairs match Rule conditions.
"""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any

from rule_engine.matcher import (
    rule_matches_event_node,
    apply_rule_to_event_and_node,
    detect_actions_in_chunk,
    save_detected_actions,
)
from rule_engine.models import Rule
from feature_extraction.models import FeatureChunk, UserInteraction, UINode


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


def create_feature_chunk(
    ui_nodes: list[UINode] = None, interactions: list[UserInteraction] = None
) -> FeatureChunk:
    if ui_nodes is None:
        ui_nodes = []
    if interactions is None:
        interactions = []

    return FeatureChunk(
        chunk_id="test_chunk",
        start_time=0,
        end_time=1000,
        events=[],
        metadata={},
        features={
            "interactions": interactions,
            "ui_nodes": {node.id: node for node in ui_nodes},
        },
    )


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


class TestDetectActionsInChunk:
    """Tests for detect_actions_in_chunk function."""

    def test_end_to_end_single_match(self):
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

        # Create mock chunk with one user interaction and corresponding UI node
        interaction = create_test_event(
            action="input",
            target_id=123,
            value="machine learning",
            timestamp=1642500000000,
        )

        node = create_test_node(
            node_id=123,
            tag="input",
            attributes={"type": "search", "name": "query"},
            text="",
        )

        chunk = create_feature_chunk(ui_nodes=[node], interactions=[interaction])

        rules = [search_rule]

        # Execute the function
        result = detect_actions_in_chunk(chunk, rules)

        # Verify results
        assert len(result) == 1
        detected_action = result[0]
        assert detected_action.action_id == "search_query"
        assert detected_action.rule_id == "search_input_rule"
        assert detected_action.confidence == 0.9
        assert detected_action.timestamp == 1642500000000
        assert detected_action.variables == {"search_term": "machine learning"}
        assert detected_action.target_element == node
        assert detected_action.related_events == [0]

    def test_end_to_end_multiple_interactions_and_rules(self):
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
        search_interaction = create_test_event(
            action="input",
            target_id=100,
            value="python tutorials",
            timestamp=1000,
        )

        click_interaction = create_test_event(
            action="click",
            target_id=200,
            timestamp=2000,
        )

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

        chunk = create_feature_chunk(
            ui_nodes=[search_node, button_node],
            interactions=[search_interaction, click_interaction],
        )

        rules = [search_rule, button_rule]

        # Execute the function
        result = detect_actions_in_chunk(chunk, rules)

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

    def test_no_matches_empty_result(self):
        """Test that non-matching rules return empty result."""
        # Create a rule that won't match
        rule = create_test_rule(
            rule_id="no_match_rule",
            match_event={"action": "hover"},  # Looking for hover
            match_node={"tag": "div"},
            action_id="hover_action",
        )

        # Create interaction that won't match (click instead of hover)
        interaction = create_test_event(
            action="click",
            target_id=123,
        )

        node = create_test_node(
            node_id=123,
            tag="button",  # Different tag than rule expects
        )

        chunk = create_feature_chunk(ui_nodes=[node], interactions=[interaction])

        rules = [rule]

        # Execute the function
        result = detect_actions_in_chunk(chunk, rules)

        # Verify no matches
        assert len(result) == 0

    def test_missing_target_node_skipped(self):
        """Test that interactions with missing target nodes are skipped."""
        rule = create_test_rule(
            rule_id="test_rule",
            match_event={"action": "click"},
            match_node={"tag": "button"},
            action_id="click_action",
        )

        # Create interaction with target_id that doesn't exist in nodes
        interaction = create_test_event(
            action="click",
            target_id=999,  # This ID won't be found in nodes
        )

        node = create_test_node(
            node_id=123,  # Different ID
            tag="button",
        )

        chunk = create_feature_chunk(ui_nodes=[node], interactions=[interaction])

        rules = [rule]

        # Execute the function
        result = detect_actions_in_chunk(chunk, rules)

        # Verify no matches due to missing node
        assert len(result) == 0

    def test_empty_chunk_empty_result(self):
        """Test that empty chunk returns empty result."""
        rule = create_test_rule(
            rule_id="test_rule",
            match_event={"action": "click"},
            match_node={"tag": "button"},
            action_id="click_action",
        )

        # Empty chunk
        chunk = create_feature_chunk()

        rules = [rule]

        # Execute the function
        result = detect_actions_in_chunk(chunk, rules)

        # Verify empty result
        assert len(result) == 0

    def test_empty_rules_empty_result(self):
        """Test that empty rules list returns empty result."""
        # Create valid interaction and node
        interaction = create_test_event(action="click", target_id=123)
        node = create_test_node(node_id=123, tag="button")

        chunk = create_feature_chunk(ui_nodes=[node], interactions=[interaction])

        rules = []  # Empty rules list

        # Execute the function
        result = detect_actions_in_chunk(chunk, rules)

        # Verify empty result
        assert len(result) == 0

    def test_partial_chunk_features_graceful_handling(self):
        """Test handling of chunk with partial features."""
        rule = create_test_rule(
            rule_id="test_rule",
            match_event={"action": "click"},
            match_node={"tag": "button"},
            action_id="click_action",
        )

        # Chunk with features but missing user_interactions
        chunk = create_feature_chunk(
            ui_nodes=[create_test_node(node_id=123, tag="button")],
        )

        rules = [rule]

        # Execute the function
        result = detect_actions_in_chunk(chunk, rules)

        # Verify empty result
        assert len(result) == 0


class TestSaveDetectedActions:
    """Tests for save_detected_actions function."""

    def test_save_actions_with_data(self):
        """Test saving detected actions to JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test actions
            rule = create_test_rule(
                rule_id="test_rule_1", action_id="search_query", confidence=0.9
            )
            rule.variables = {"search_term": "event.value"}

            event = create_test_event(
                action="input",
                target_id=123,
                value="machine learning",
                timestamp=1642500000000,
            )

            node = create_test_node(
                node_id=123,
                tag="input",
                attributes={"type": "search", "placeholder": "Search..."},
                text="",
            )

            # Create a detected action using apply_rule_to_event_and_node
            detected_action = apply_rule_to_event_and_node(rule, event, node, 0)
            actions = [detected_action]

            chunk_id = "test_chunk_123"

            # Save actions
            save_detected_actions(actions, chunk_id, temp_dir)

            # Verify file was created
            expected_file = Path(temp_dir) / f"{chunk_id}.json"
            assert expected_file.exists()

            # Load and verify JSON content
            with open(expected_file, "r", encoding="utf-8") as f:
                saved_data = json.load(f)

            assert len(saved_data) == 1
            action_data = saved_data[0]

            # Verify all DetectedAction fields are present
            assert action_data["action_id"] == "search_query"
            assert action_data["timestamp"] == 1642500000000
            assert action_data["confidence"] == 0.9
            assert action_data["rule_id"] == "test_rule_1"
            assert action_data["variables"] == {"search_term": "machine learning"}
            assert action_data["related_events"] == [0]

            # Verify target_element (UINode) is properly serialized
            assert action_data["target_element"] is not None
            target_element = action_data["target_element"]
            assert target_element["id"] == 123
            assert target_element["tag"] == "input"
            assert target_element["attributes"] == {
                "type": "search",
                "placeholder": "Search...",
            }
            assert target_element["text"] == ""
            assert target_element["parent"] is None

    def test_save_empty_actions_list(self):
        """Test saving empty actions list creates valid empty JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            chunk_id = "empty_chunk_456"
            actions = []

            # Save empty actions
            save_detected_actions(actions, chunk_id, temp_dir)

            # Verify file was created
            expected_file = Path(temp_dir) / f"{chunk_id}.json"
            assert expected_file.exists()

            # Load and verify JSON content is empty list
            with open(expected_file, "r", encoding="utf-8") as f:
                saved_data = json.load(f)

            assert saved_data == []

    def test_integration_detect_and_save_actions(self):
        """Integration test: detect actions in chunk and save to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create rule and chunk data
            rule = create_test_rule(
                rule_id="integration_rule",
                match_event={"action": "input"},
                match_node={"tag": "input", "attributes": {"type": "search"}},
                action_id="search_query",
                confidence=0.9,
            )
            rule.variables = {"search_term": "event.value"}

            interaction = create_test_event(
                action="input",
                target_id=123,
                value="integration test",
                timestamp=1642500000000,
            )

            node = create_test_node(
                node_id=123, tag="input", attributes={"type": "search", "name": "query"}
            )

            chunk = create_feature_chunk(ui_nodes=[node], interactions=[interaction])

            # Detect actions
            detected_actions = detect_actions_in_chunk(chunk, [rule])
            assert len(detected_actions) == 1

            # Save detected actions
            chunk_id = "integration_test_chunk"
            save_detected_actions(detected_actions, chunk_id, temp_dir)

            # Verify saved file
            expected_file = Path(temp_dir) / f"{chunk_id}.json"
            assert expected_file.exists()

            with open(expected_file, "r", encoding="utf-8") as f:
                saved_data = json.load(f)

            assert len(saved_data) == 1
            action_data = saved_data[0]
            assert action_data["action_id"] == "search_query"
            assert action_data["variables"] == {"search_term": "integration test"}
            assert action_data["rule_id"] == "integration_rule"
