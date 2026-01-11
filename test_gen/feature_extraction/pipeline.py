"""
Feature Extraction Pipeline for rrweb Session Feature Extraction.

This module provides the main integration point for the feature extraction pipeline,
orchestrating all individual extractors to transform preprocessed chunks into rich
feature sets. The pipeline applies DOM mutations, extracts various feature types,
and assembles them into a comprehensive FeatureChunk for downstream analysis.

The extraction pipeline processes chunks in the following order:
1. Apply DOM mutations to maintain virtual DOM state
2. Extract DOM mutations and user interactions
3. Resolve UI metadata for extracted events
4. Detect scroll patterns
5. Assemble all features into a FeatureChunk

Configuration:
    All extractor functions use default parameters from config module.

This enables rule-based and LLM-driven behavior inference by providing structured,
semantic representations of user interactions and system responses.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Generator, Tuple

from rrweb_ingest.pipeline import iterate_sessions
from rrweb_util.dom_state.dom_state_helpers import apply_mutation, init_dom_state
from rrweb_util.user_interaction.extractors import extract_user_interactions
from .models import FeatureChunk, UINode
from .metadata import resolve_node_metadata

logger = logging.getLogger(__name__)


def extract_features(
    chunk: Dict,
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
        - ui_nodes: Dictionary of UI metadata for referenced nodes
        - scroll_patterns: List of scroll events paired with subsequent mutations

    Note:
        The dom_state parameter is modified in place as mutations are applied.
        This maintains consistency between the virtual DOM and extracted features.
    """
    # Apply mutations from the chunk to update DOM state
    apply_mutation(dom_state, chunk.events)

    interactions = extract_user_interactions(chunk.events)

    # Resolve UI metadata for referenced nodes
    # TODO extract and move this into rrweb_ingest
    ui_nodes = _resolve_ui_metadata(interactions, dom_state)

    # Assemble all features into FeatureChunk
    features = {
        "interactions": interactions,
        "ui_nodes": ui_nodes,
    }

    return FeatureChunk(
        chunk_id=chunk.chunk_id,
        start_time=chunk.start_time,
        end_time=chunk.end_time,
        events=chunk.events,
        features=features,
        metadata=chunk.metadata,
    )


def _resolve_ui_metadata(interactions, dom_state):
    """Resolve UI metadata for all nodes referenced in mutations and interactions."""
    ui_nodes = {}

    # Collect unique node IDs from mutations and interactions
    referenced_node_ids = _collect_referenced_node_ids(interactions)

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


def _collect_referenced_node_ids(interactions):
    """Collect unique node IDs referenced in interactions."""
    referenced_node_ids = set()
    for interaction in interactions:
        referenced_node_ids.add(interaction.target_id)
    return referenced_node_ids


def iterate_feature_extraction(
    session_dir: str, max_sessions: int = None
) -> Generator[Tuple[FeatureChunk, Dict[str, Any]], None, None]:
    """
    Generator function to iterate through all rrweb session files in a directory and extract features.

    This function processes each session file, extracts features using the
    extract_features function and yields the results.

    Args:
        session_dir: Directory containing rrweb JSON session files
        max_sessions: Optional limit on number of sessions to process
    """
    session_generator = iterate_sessions(session_dir, max_sessions=max_sessions)
    for session_chunks in session_generator:
        # TODO (jordan) This becomes logic in rrweb_ingest
        # extract_features(curr_chunk, dom)
        pass


def _extract_and_save_session_features(stats, output_path, chunk_data, chunk_metadata):
    """
    Extract features from a single session and save to disk.

    Args:
        stats: Dictionary to update processing statistics
        output_path: Path to the output directory
        chunk_data: The FeatureChunk containing the extracted features
        chunk_metadata: Metadata associated with the chunk
    """
    session_id = chunk_metadata["session_id"]
    chunk_id = chunk_data.chunk_id

    # Generate output filename: {session_id}_{chunk_id}.json
    output_filename = f"{session_id}_{chunk_id}.json"
    output_file_path = output_path / output_filename

    # Convert FeatureChunk to dictionary for JSON serialization
    chunk_dict = chunk_data.to_dict()

    # Add processing metadata
    chunk_dict["processing_metadata"] = {
        "feature_extraction_version": "1.0",
    }

    # Save to JSON file with pretty formatting
    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(chunk_dict, f, indent=2, ensure_ascii=False)

    # Update statistics
    stats["sessions_processed"] += 1
    for feature_type, feature_list in chunk_data.features.items():
        if feature_type in stats["total_features"]:
            if isinstance(feature_list, dict):  # ui_nodes case
                stats["total_features"][feature_type] += len(feature_list)
            elif isinstance(feature_list, list):  # all other features
                stats["total_features"][feature_type] += len(feature_list)

    logger.debug("  Saved: %s", output_filename)


def extract_and_save_features(
    session_dir: str,
    output_dir: str,
    max_sessions: int = None,
) -> Dict[str, Any]:
    """
    Extract features from all sessions and save them as JSON files to output directory.

    This function processes rrweb session files, extracts features using the complete
    feature extraction pipeline, and saves each FeatureChunk as a JSON file. The output
    files can then be loaded by the rule engine for action detection.

    Args:
        session_dir: Directory containing rrweb JSON session files
        output_dir: Directory where extracted features will be saved as JSON files
        max_sessions: Optional limit on number of sessions to process

    Returns:
        Dictionary containing processing statistics:
        - sessions_processed: Number of session files processed
        - total_features: Aggregate counts of each feature type
        - errors: List of any errors encountered during processing

    File Output Format:
        Each FeatureChunk is saved as: {output_dir}/{session_id}_{chunk_id}.json
        The JSON structure matches the FeatureChunk.to_dict() format with all
        nested feature objects serialized as dictionaries.
    """
    output_path = Path(output_dir)
    session_path = Path(session_dir)

    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    # Initialize statistics tracking
    stats = {
        "sessions_processed": 0,
        "total_features": {
            "interactions": 0,
            "ui_nodes": 0,
        },
        "errors": [],
    }

    logger.debug("Processing sessions from: %s", session_path)
    logger.debug("Saving features to: %s", output_path)

    # Process each session using the existing feature extraction generator
    chunk_generator = iterate_feature_extraction(session_dir, max_sessions=max_sessions)

    for chunk_data, chunk_metadata in chunk_generator:
        _extract_and_save_session_features(
            stats, output_path, chunk_data, chunk_metadata
        )

    logger.debug("\nProcessing Summary:")
    logger.debug("  Sessions processed: %d", stats["sessions_processed"])
    logger.debug("  Total features extracted:")
    for feature_type, count in stats["total_features"].items():
        if count > 0:
            logger.debug("    %s: %d", feature_type, count)
    if stats["errors"]:
        logger.warning("  Errors encountered: %d", len(stats["errors"]))

    return stats
