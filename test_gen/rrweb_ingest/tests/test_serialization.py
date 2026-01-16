"""
Tests for JSON serialization functionality of rrweb_ingest models.
"""

import json
import pytest

from rrweb_ingest.models import ProcessedSession


@pytest.fixture(name="basic_processed_session")
def fixture_basic_processed_session(basic_user_interaction):
    """Fixture that provides a basic ProcessedSession instance."""
    return ProcessedSession(
        session_id="test-session-001",
        user_interactions=[basic_user_interaction],
    )


def test_processed_session_to_dict_complete(basic_processed_session):
    """Test ProcessedSession serialization with all feature types."""
    result = basic_processed_session.to_dict()

    # Verify basic properties
    assert result["session_id"] == "test-session-001"
    assert len(result["user_interactions"]) == 1
    assert (
        result["user_interactions"][0]
        == basic_processed_session.user_interactions[0].to_dict()
    )
    assert "metadata" in result
    assert "feature_extraction_version" in result["metadata"]


def test_feature_chunk_to_dict_empty_features():
    """Test ProcessedSession serialization with no user interactions."""
    result = ProcessedSession(session_id="empty-session").to_dict()
    assert result["user_interactions"] == []


def test_feature_chunk_serialization_roundtrip(basic_processed_session):
    """Test that serialization produces JSON-compatible output."""
    # Convert to dict and then to JSON string
    session_dict = basic_processed_session.to_dict()
    json_str = json.dumps(session_dict, ensure_ascii=False, indent=2)

    # Parse back from JSON
    parsed_dict = json.loads(json_str)

    # Verify key fields are preserved
    assert parsed_dict["session_id"] == basic_processed_session.session_id
    assert len(parsed_dict["user_interactions"]) == len(
        basic_processed_session.user_interactions
    )
    assert parsed_dict["user_interactions"] == session_dict["user_interactions"]
    assert parsed_dict["metadata"] == session_dict["metadata"]
