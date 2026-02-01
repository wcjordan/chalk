"""
Data models for the rrweb_ingest module.

Defines the composite data structure of features we extract when processing an rrweb session
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from rrweb_util.user_interaction.models import UserInteraction

FEATURE_EXTRACTION_VERSION = "0.1"


@dataclass
class ProcessedSession:
    """
    Represents a fully processed rrweb session with extracted features.
    Includes UserInteractions and the UINodes involved in those interactions.

    Attributes:
        session_id: Unique identifier for the session
        user_interactions: User interactions extracted from the session
        metadata: Additional metadata about the session extraction process (e.g. version info)
    """

    session_id: str
    user_interactions: List[UserInteraction] = field(default_factory=list)
    metadata: Dict[str, Any] = field(
        default_factory=lambda: {
            "feature_extraction_version": FEATURE_EXTRACTION_VERSION
        }
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "user_interactions": [
                ui.to_dict() if hasattr(ui, "to_dict") else ui
                for ui in self.user_interactions
            ],
            "metadata": self.metadata,
        }


def processed_session_from_dict(data: Dict[str, Any]) -> ProcessedSession:
    """Create a ProcessedSession instance from a dictionary."""
    return ProcessedSession(
        session_id=data["session_id"],
        user_interactions=[UserInteraction(**ui) for ui in data["user_interactions"]],
        metadata=data["metadata"],
    )
