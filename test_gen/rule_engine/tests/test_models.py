"""
Unit tests for the rule engine data models.

Tests the construction and basic functionality of all data classes
used in the rule-based action detection module.
"""

from rule_engine.models import DetectedAction, Rule
from rrweb_util.dom_state.models import UINode


def test_detected_action_creation():
    """Test that DetectedAction objects can be created with correct attributes."""
    ui_node = UINode(
        id=123,
        tag="input",
        attributes={"type": "text", "placeholder": "Search..."},
        text="",
        parent=100,
    )

    action = DetectedAction(
        action_id="search_query",
        timestamp=12345,
        confidence=0.9,
        rule_id="search_input_rule",
        variables={"query_text": "machine learning"},
        target_element=ui_node,
        related_events=[0, 1, 2],
    )

    assert action.action_id == "search_query"
    assert action.timestamp == 12345
    assert action.confidence == 0.9
    assert action.rule_id == "search_input_rule"
    assert action.variables == {"query_text": "machine learning"}
    assert action.target_element == ui_node
    assert action.related_events == [0, 1, 2]


def test_detected_action_no_target_element():
    """Test that DetectedAction can be created without a target element."""
    action = DetectedAction(
        action_id="page_load",
        timestamp=5000,
        confidence=1.0,
        rule_id="page_load_rule",
        variables={},
        target_element=None,
        related_events=[0],
    )

    assert action.target_element is None
    assert not action.variables
    assert action.related_events == [0]


def test_rule_creation():
    """Test that Rule objects can be created with correct attributes."""
    rule = Rule(
        id="click_button_rule",
        description="Detects button clicks",
        match={"event": {"type": "click"}, "node": {"tag": "button"}},
        confidence=0.95,
        variables={"button_text": "node.text"},
        action_id="button_click",
    )

    assert rule.id == "click_button_rule"
    assert rule.description == "Detects button clicks"
    assert rule.match == {"event": {"type": "click"}, "node": {"tag": "button"}}
    assert rule.confidence == 0.95
    assert rule.variables == {"button_text": "node.text"}
    assert rule.action_id == "button_click"


def test_rule_creation_minimal():
    """Test that Rule can be created with minimal required fields."""
    rule = Rule(
        id="minimal_rule",
        description=None,
        match={"event": {"type": "input"}},
        confidence=0.8,
        variables={},
        action_id="text_input",
    )

    assert rule.id == "minimal_rule"
    assert rule.description is None
    assert rule.match == {"event": {"type": "input"}}
    assert rule.confidence == 0.8
    assert not rule.variables
    assert rule.action_id == "text_input"


def test_rule_from_dict_like():
    """Test that Rule can be created from dictionary-like data."""
    rule_data = {
        "id": "form_submit_rule",
        "description": "Detects form submissions",
        "match": {"event": {"type": "submit"}, "node": {"tag": "form"}},
        "confidence": 0.99,
        "variables": {
            "form_id": "node.attributes.id",
            "form_action": "node.attributes.action",
        },
        "action_id": "form_submit",
    }

    rule = Rule(
        id=rule_data["id"],
        description=rule_data["description"],
        match=rule_data["match"],
        confidence=rule_data["confidence"],
        variables=rule_data["variables"],
        action_id=rule_data["action_id"],
    )

    assert rule.id == "form_submit_rule"
    assert rule.description == "Detects form submissions"
    assert rule.match["event"]["type"] == "submit"
    assert rule.match["node"]["tag"] == "form"
    assert rule.confidence == 0.99
    assert rule.variables["form_id"] == "node.attributes.id"
    assert rule.variables["form_action"] == "node.attributes.action"
    assert rule.action_id == "form_submit"
