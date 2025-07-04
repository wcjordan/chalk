"""
Feature Extraction Pipeline for rrweb Session Feature Extraction.

This module provides the main integration point for the feature extraction pipeline,
orchestrating all individual extractors to transform preprocessed chunks into rich
feature sets. The pipeline applies DOM mutations, extracts various feature types,
and assembles them into a comprehensive FeatureChunk for downstream analysis.

The extraction pipeline processes chunks in the following order:
1. Apply DOM mutations to maintain virtual DOM state
2. Extract DOM mutations, user interactions, and timing delays
3. Resolve UI metadata for extracted events
4. Cluster mouse trajectories and detect scroll patterns
5. Assemble all features into a FeatureChunk

Configuration:
    All extractor functions use default parameters from config module.
    Custom parameters can be passed through the extract_features function.

This enables rule-based and LLM-driven behavior inference by providing structured,
semantic representations of user interactions and system responses.
"""

import logging
from typing import Dict

from rrweb_ingest.models import Chunk
from .models import FeatureChunk, UINode
from .dom_state import apply_mutations
from .extractors import (
    extract_dom_mutations,
    extract_user_interactions,
    compute_inter_event_delays,
    compute_reaction_delays,
)
from .metadata import resolve_node_metadata
from .clustering import cluster_mouse_trajectories
from .scroll_patterns import detect_scroll_patterns

logger = logging.getLogger(__name__)


def extract_features(
    chunk: Chunk,
    dom_state: Dict[int, UINode],
) -> FeatureChunk:
    """
    Given a preprocessed Chunk and its initial virtual DOM state,
    run all feature extractors and return a populated FeatureChunk.

    This function orchestrates the complete feature extraction pipeline, applying
    DOM mutations to maintain state consistency and then running all feature
    extractors to produce a comprehensive analysis of user behavior and system
    responses within the chunk.

    Args:
        chunk: Preprocessed Chunk containing filtered and normalized rrweb events
        dom_state: Dictionary mapping node IDs to UINode instances representing
                  the current virtual DOM state (will be modified in place)

    Returns:
        FeatureChunk containing the original chunk data plus extracted features:
        - dom_mutations: List of DOM changes (adds, removes, attribute/text changes)
        - interactions: List of user actions (clicks, inputs, scrolls)
        - delays: List of timing relationships between events
        - ui_nodes: Dictionary of UI metadata for referenced nodes
        - mouse_clusters: List of grouped mouse movement patterns
        - scroll_patterns: List of scroll events paired with subsequent mutations

    Note:
        The dom_state parameter is modified in place as mutations are applied.
        This maintains consistency between the virtual DOM and extracted features.
    """
    # Apply mutations from the chunk to update DOM state
    apply_mutations(dom_state, chunk.events)

    # Extract core features
    dom_mutations = extract_dom_mutations(chunk.events)
    interactions = extract_user_interactions(chunk.events)
    all_delays = _extract_timing_delays(chunk.events)

    # Resolve UI metadata for referenced nodes
    ui_nodes = _resolve_ui_metadata(dom_mutations, interactions, dom_state)

    # Extract behavioral patterns
    mouse_clusters = cluster_mouse_trajectories(chunk.events)
    scroll_patterns = detect_scroll_patterns(chunk.events)

    # Assemble all features into FeatureChunk
    features = {
        "dom_mutations": dom_mutations,
        "interactions": interactions,
        "delays": all_delays,
        "ui_nodes": ui_nodes,
        "mouse_clusters": mouse_clusters,
        "scroll_patterns": scroll_patterns,
    }

    return FeatureChunk(
        chunk_id=chunk.chunk_id,
        start_time=chunk.start_time,
        end_time=chunk.end_time,
        events=chunk.events,
        features=features,
        metadata=chunk.metadata,
    )


def _extract_timing_delays(events):
    """Extract and combine inter-event and reaction delays."""
    inter_event_delays = compute_inter_event_delays(events)
    reaction_delays = compute_reaction_delays(events)
    return inter_event_delays + reaction_delays


def _resolve_ui_metadata(dom_mutations, interactions, dom_state):
    """Resolve UI metadata for all nodes referenced in mutations and interactions."""
    ui_nodes = {}

    # Collect unique node IDs from mutations and interactions
    referenced_node_ids = _collect_referenced_node_ids(dom_mutations, interactions)

    # Resolve metadata for each referenced node
    for node_id in referenced_node_ids:
        try:
            ui_nodes[node_id] = resolve_node_metadata(node_id, dom_state)
        except KeyError:
            # Node not found in DOM state - log and skip metadata resolution
            logger.warning(
                "Node ID %s not found in DOM state. Skipping metadata resolution.",
                node_id,
            )
            continue

    return ui_nodes


def _collect_referenced_node_ids(dom_mutations, interactions):
    """Collect unique node IDs referenced in mutations and interactions."""
    referenced_node_ids = set()
    for mutation in dom_mutations:
        referenced_node_ids.add(mutation.target_id)
    for interaction in interactions:
        referenced_node_ids.add(interaction.target_id)
    return referenced_node_ids
