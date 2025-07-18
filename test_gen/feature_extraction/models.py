"""
Data models for the Session Chunking & Feature Extraction module.

This module defines the core data structures used throughout the feature extraction
pipeline, including representations for DOM mutations, user interactions, timing
delays, UI nodes, mouse clusters, scroll patterns, and the final feature chunk.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class DomMutation:
    """
    Captures a DOM mutation event with its type, target, and timing.

    Represents changes to the DOM structure including node additions/removals,
    attribute changes, and text content modifications.

    Attributes:
        mutation_type: Type of mutation ("add", "remove", "attribute", "text")
        target_id: ID of the DOM node that was mutated
        details: Mutation-specific data (new attributes, text content, etc.)
        timestamp: When the mutation occurred (milliseconds)
    """

    mutation_type: str
    target_id: int
    details: Dict[str, Any]
    timestamp: int


@dataclass
class UserInteraction:
    """
    Captures a user interaction event with its action and context.

    Represents direct user actions like clicks, input changes, and scrolling
    with their associated DOM targets and values.

    Attributes:
        action: Type of interaction ("click", "input", "scroll")
        target_id: ID of the DOM node that was interacted with
        value: Input value, coordinates, or other action-specific data
        timestamp: When the interaction occurred (milliseconds)
    """

    action: str
    target_id: int
    value: Any
    timestamp: int


@dataclass
class EventDelay:
    """
    Captures timing information between two events.

    Represents the temporal relationship between events, useful for detecting
    reaction times, idle periods, and interaction patterns.

    Attributes:
        from_ts: Timestamp of the first event (milliseconds)
        to_ts: Timestamp of the second event (milliseconds)
        delta_ms: Time difference between events (milliseconds)
    """

    from_ts: int
    to_ts: int
    delta_ms: int


@dataclass
class UINode:
    """
    Represents a DOM node with its metadata and hierarchy information.

    Captures the essential properties of a DOM element including its structure,
    attributes, content, and position in the DOM tree.

    Attributes:
        id: Unique identifier for the DOM node
        tag: HTML tag name (e.g., "button", "input", "div")
        attributes: Dictionary of HTML attributes
        text: Text content of the node
        parent: ID of the parent node, or None for root
    """

    id: int
    tag: str
    attributes: Dict[str, str]
    text: str
    parent: Optional[int]


@dataclass
class MouseCluster:
    """
    Represents a cluster of related mouse movement events.

    Groups mouse movements that occur in close temporal and spatial proximity,
    useful for understanding user intent and interaction patterns.

    Attributes:
        start_ts: Timestamp when the cluster began (milliseconds)
        end_ts: Timestamp when the cluster ended (milliseconds)
        points: List of mouse positions with timestamps [{"x": int, "y": int, "ts": int}]
        duration_ms: Total duration of the cluster (milliseconds)
        point_count: Number of mouse positions in the cluster
    """

    start_ts: int
    end_ts: int
    points: List[Dict[str, int]]
    duration_ms: int
    point_count: int


@dataclass
class ScrollPattern:
    """
    Represents a scroll event paired with a subsequent DOM mutation.

    Captures scroll-triggered behaviors like lazy loading, infinite scroll,
    or content updates that occur in response to scrolling.

    Attributes:
        scroll_event: The original scroll event data
        mutation_event: The DOM mutation that followed the scroll
        delay_ms: Time between scroll and mutation (milliseconds)
    """

    scroll_event: Dict[str, Any]
    mutation_event: Dict[str, Any]
    delay_ms: int


@dataclass
class FeatureChunk:
    """
    Aggregates a chunk's events with extracted feature data.

    Extends the basic Chunk concept with rich feature sets extracted from
    the raw events, enabling higher-level behavior analysis.

    Attributes:
        chunk_id: Unique identifier for the chunk
        start_time: Timestamp of the first event in the chunk (milliseconds)
        end_time: Timestamp of the last event in the chunk (milliseconds)
        events: Original list of rrweb events in the chunk
        features: Dictionary containing extracted feature lists
        metadata: Additional metadata about the chunk
    """

    chunk_id: str
    start_time: int
    end_time: int
    events: List[Dict[str, Any]]
    features: Dict[str, List[Any]]
    metadata: Dict[str, Any]
