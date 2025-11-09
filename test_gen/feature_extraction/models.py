"""
Data models for the Session Chunking & Feature Extraction module.

This module defines the core data structures used throughout the feature extraction
pipeline for the final feature chunk.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Union
from rrweb_util.dom_state.models import DomMutation, UINode
from rrweb_util.user_interaction.models import ScrollPattern, UserInteraction


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
    features: Dict[str, Union[List[Any], Dict[str, Any]]]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        # Convert features dictionary, handling different object types
        features_dict = {}
        for key, value_list in self.features.items():
            if key == "ui_nodes":
                # ui_nodes is a Dict[int, UINode] converted to Dict[str, dict]
                if isinstance(value_list, dict):
                    features_dict[key] = {
                        str(node_id): (
                            node.to_dict() if hasattr(node, "to_dict") else node
                        )
                        for node_id, node in value_list.items()
                    }
                else:
                    features_dict[key] = value_list
            else:
                # Other features are lists of objects
                features_dict[key] = [
                    item.to_dict() if hasattr(item, "to_dict") else item
                    for item in value_list
                ]

        return {
            "chunk_id": self.chunk_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "events": self.events,
            "features": features_dict,
            "metadata": self.metadata,
        }


def feature_chunk_from_dict(data: Dict[str, Any]) -> FeatureChunk:
    """Create a FeatureChunk instance from a dictionary."""
    features = {}
    for key, value in data.get("features", {}).items():
        if key == "ui_nodes":
            # Convert UI nodes back to their original structure
            features[key] = {
                int(node_id): UINode(**node_data)
                for node_id, node_data in value.items()
            }
        elif key == "interactions":
            # Other features are lists of objects
            features[key] = [UserInteraction(**item_data) for item_data in value]
        elif key == "dom_mutations":
            features[key] = [DomMutation(**item_data) for item_data in value]
        elif key == "scroll_patterns":
            features[key] = [ScrollPattern(**item_data) for item_data in value]
        else:
            raise ValueError(f"Unknown feature key: {key}")

    return FeatureChunk(
        chunk_id=data["chunk_id"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        events=data["events"],
        features=features,
        metadata=data["metadata"],
    )


def create_empty_features_obj() -> Dict[str, Union[List[Any], Dict[str, Any]]]:
    """Create an empty features object for a FeatureChunk."""
    return {
        "dom_mutations": [],
        "interactions": [],
        "ui_nodes": {},
        "scroll_patterns": [],
    }
