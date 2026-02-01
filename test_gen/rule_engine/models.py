"""
Data models for the Rule-Based Action Detection module.

This module defines the core data structures for representing detected actions
and the rules that identify them from event data.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List

from rrweb_util.dom_state.models import UINode


@dataclass
class DetectedAction:
    """
    Represents a user action detected by a rule.

    Captures the essential information about a detected action including
    the action type, timing, confidence, and associated context.

    Attributes:
        action_id: Human-readable label (e.g., "search_query")
        timestamp: Timestamp from the first matched event
        confidence: Fixed or rule-supplied confidence
        rule_id: ID of the rule that matched
        variables: Extracted values (e.g., input text)
        target_element: The UINode involved, if any
        related_events: Indices of events in the session that contributed to the match
    """

    action_id: str
    timestamp: int
    confidence: float
    rule_id: str
    variables: Dict[str, Any]
    target_element: Optional[UINode]
    related_events: List[int]


@dataclass
class Rule:
    """
    Represents a rule parsed from YAML.

    Defines the conditions and extraction logic for detecting specific
    user actions from feature sequences.

    Attributes:
        id: Unique identifier for the rule
        description: Optional human-readable description
        match: Feature match conditions
        confidence: Confidence value for detections using this rule
        variables: Variable extraction expressions
        action_id: The action type this rule detects
    """

    id: str
    description: Optional[str]
    match: Dict[str, Any]
    confidence: float
    variables: Dict[str, str]
    action_id: str
