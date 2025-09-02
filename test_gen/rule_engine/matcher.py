"""
Rule matching functionality for the Rule-Based Action Detection module.

This module implements the core matching logic to determine if a UserInteraction
and UINode pair matches the conditions specified in a Rule.
"""

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

from feature_extraction.models import UserInteraction, UINode

from .models import Rule, DetectedAction
from .variable_resolver import extract_variables

logger = logging.getLogger("test_gen.rule_engine")


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
    node_id = getattr(node, "id", "unknown")
    logger.debug(
        "Evaluating rule '%s' against event.action='%s', node.tag='%s', node.id='%s'",
        rule.id,
        event.action,
        node.tag,
        node_id,
    )

    # Check if event matches rule.match.event
    if not _event_matches(rule.match.get("event", {}), event):
        logger.debug(
            "Rule '%s': action mismatch (expected: %s, got: %s)",
            rule.id,
            rule.match.get("event", {}).get("action"),
            event.action,
        )
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
            logger.debug(
                "Node tag mismatch (expected: %s, got: %s)", match_node["tag"], node.tag
            )
            return False

    # Check attributes match
    if "attributes" in match_node:
        required_attributes = match_node["attributes"]
        if not isinstance(required_attributes, dict):
            return False

        missing_attrs = []
        mismatched_attrs = []

        for key, expected_value in required_attributes.items():
            if key not in node.attributes:
                missing_attrs.append(key)
            elif node.attributes[key] != expected_value:
                mismatched_attrs.append(
                    f"{key}={node.attributes[key]} (expected: {expected_value})"
                )

        if missing_attrs:
            logger.debug("Missing attributes: %s", missing_attrs)
            return False
        if mismatched_attrs:
            logger.debug("Mismatched attributes: %s", mismatched_attrs)
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

    # Truncate large variable values for logging
    truncated_vars = {}
    for k, v in variables.items():
        if isinstance(v, str) and len(v) > 80:
            truncated_vars[k] = v[:77] + "..."
        else:
            truncated_vars[k] = v

    logger.info(
        "Rule '%s' matched: action_id='%s', event_index=%d, timestamp=%d, variables=%s",
        rule.id,
        rule.action_id,
        event_index,
        event.timestamp,
        truncated_vars,
    )

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
    chunk_features = chunk.features
    user_interactions = chunk_features.get("interactions", [])
    node_map = chunk_features.get("ui_nodes", {})

    logger.debug("Processing %d interactions in chunk", len(user_interactions))

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

    # Log chunk-level summary
    unique_rules_matched = set(action.rule_id for action in detected_actions)
    logger.info(
        "Chunk processing complete: %d rules evaluated, %d matches found, %d distinct rules matched",
        len(rules),
        len(detected_actions),
        len(unique_rules_matched),
    )

    return detected_actions


def save_detected_actions(
    actions: List[DetectedAction],
    chunk_id: str,
    output_dir: Union[str, Path] = "test_gen/data/action_mappings",
) -> None:
    """
    Serialize detected actions to disk as JSON using chunk_id as filename.

    Args:
        actions: List of DetectedAction objects to serialize
        chunk_id: ID to use for the filename
        output_dir: Directory to save the file to

    The function creates the output directory if it doesn't exist and saves
    the actions as JSON to {output_dir}/{chunk_id}.json.
    """
    # Convert output_dir to Path object
    output_path = Path(output_dir)

    # Create the output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    # Convert DetectedAction objects to JSON-serializable dicts
    serializable_actions = []
    for action in actions:
        action_dict = asdict(action)

        serializable_actions.append(action_dict)

    # Define the output file path
    output_file = output_path / f"{chunk_id}.json"

    # Write to JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(serializable_actions, f, indent=2, ensure_ascii=False)
