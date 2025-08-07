"""
Rule matching functionality for the Rule-Based Action Detection module.

This module implements the core matching logic to determine if a UserInteraction
and UINode pair matches the conditions specified in a Rule.
"""

from typing import Dict, Any

from feature_extraction.models import UserInteraction, UINode

from .models import Rule


def rule_matches_event_node(rule: Rule, event: UserInteraction, node: UINode) -> bool:
    """
    Determine if a rule matches a specific event and node combination.

    Args:
        rule: The rule to evaluate
        event: The user interaction event to check
        node: The UI node to check

    Returns:
        True if both the event matches rule.match.event and
        the node matches rule.match.node, False otherwise
    """
    # Check if event matches rule.match.event
    if not _event_matches(rule.match.get("event", {}), event):
        return False

    # Check if node matches rule.match.node
    if not _node_matches(rule.match.get("node", {}), node):
        return False

    return True


def _event_matches(match_event: Dict[str, Any], event: UserInteraction) -> bool:
    """
    Check if an event matches the match.event criteria.

    Args:
        match_event: The event matching criteria from the rule
        event: The actual user interaction event

    Returns:
        True if the event matches all criteria, False otherwise
    """
    # Check action match
    if "action" in match_event:
        if match_event["action"] != event.action:
            return False

    return True


def _node_matches(match_node: Dict[str, Any], node: UINode) -> bool:
    """
    Check if a node matches the match.node criteria.

    Args:
        match_node: The node matching criteria from the rule
        node: The actual UI node

    Returns:
        True if the node matches all criteria, False otherwise
    """
    # Check tag match
    if "tag" in match_node:
        if match_node["tag"] != node.tag:
            return False

    # Check attributes match
    if "attributes" in match_node:
        required_attributes = match_node["attributes"]
        if not isinstance(required_attributes, dict):
            return False

        for key, expected_value in required_attributes.items():
            if key not in node.attributes:
                return False
            if node.attributes[key] != expected_value:
                return False

    return True
