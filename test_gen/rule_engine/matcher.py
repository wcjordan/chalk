"""
Rule matching functionality for the Rule-Based Action Detection module.

This module implements the core matching logic to determine if a UserInteraction
and UINode pair matches the conditions specified in a Rule.
"""

from typing import Dict, Any, Optional, List

from feature_extraction.models import UserInteraction, UINode

from .models import Rule, DetectedAction
from .variable_resolver import extract_variables


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


def apply_rule_to_event_and_node(
    rule: Rule, event: UserInteraction, node: UINode, event_index: int
) -> Optional[DetectedAction]:
    """
    Apply a rule to an event and node, returning a DetectedAction if matched.

    Args:
        rule: The rule to evaluate
        event: The user interaction event to check
        node: The UI node to check
        event_index: The index of the event in the chunk

    Returns:
        DetectedAction if the rule matches, None otherwise
    """
    if not rule_matches_event_node(rule, event, node):
        return None

    variables = extract_variables(rule.variables, event, node)

    return DetectedAction(
        action_id=rule.action_id,
        timestamp=event.timestamp,
        confidence=rule.confidence,
        rule_id=rule.id,
        variables=variables,
        target_element=node,
        related_events=[event_index],
    )


def detect_actions_in_chunk(
    chunk: Dict[str, Any], rules: List[Rule]
) -> List[DetectedAction]:
    """
    Detect actions in a full chunk by applying all rules to all UserInteractions.

    This function iterates through each UserInteraction in the chunk, finds the
    corresponding UINode, and applies each rule to determine if any actions
    should be detected.

    Args:
        chunk: A chunk dictionary containing features with user_interactions and ui_nodes
        rules: List of rules to apply for action detection

    Returns:
        List of DetectedAction objects for all matched rules and interactions
    """
    detected_actions = []

    # Get user interactions and ui nodes from the chunk
    user_interactions = chunk.get("features", {}).get("user_interactions", [])
    ui_nodes = chunk.get("features", {}).get("ui_nodes", [])

    # Create a mapping from node ID to UINode for quick lookup
    node_map = {node.id: node for node in ui_nodes}

    # Iterate through each user interaction
    for event_index, interaction in enumerate(user_interactions):
        # Find the corresponding UINode using target_id
        target_node = node_map.get(interaction.target_id)

        # Skip if no corresponding node found
        if target_node is None:
            continue

        # Apply each rule to this event-node pair
        for rule in rules:
            detected_action = apply_rule_to_event_and_node(
                rule, interaction, target_node, event_index
            )

            # If the rule matched, add to our results
            if detected_action is not None:
                detected_actions.append(detected_action)

    return detected_actions
