"""
Integration tests for the end-to-end ingest pipeline.

Tests the ingest_session function to ensure proper integration of all preprocessing
components and correct handling of various session scenarios and error conditions.
"""

import json
import tempfile

import pytest

from rrweb_ingest.pipeline import ingest_session
from rrweb_util import EventType, IncrementalSource


@pytest.fixture(name="create_session_file")
def fixture_create_session_file():
    """Helper function to create a temporary rrweb session JSON file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as f:

        def _create_session_file(events, session_guid="test_session", raw_string=None):
            """Create a temporary file with rrweb session data."""
            if raw_string:
                f.write(raw_string)
            else:
                data = {
                    "session_guid": session_guid,
                    "rrweb_data": events,
                    "metadata": {"environment": "test"},
                }
                json.dump(data, f)
            f.flush()
            return f.name

        yield _create_session_file


class TestIngestSession:
    """Test cases for the ingest_session function."""

    def test_ingest_basic_session(self, snapshot, sample_data_path):
        """Test ingesting a basic session with mixed event types."""
        session_id = "sample"
        session_chunk = ingest_session(session_id, sample_data_path)

        # Verify we got a list of Chunk objects
        assert isinstance(session_chunk, dict), "ingest_session should return a dict"
        assert "session_id" in session_chunk
        assert "user_interactions" in session_chunk

        # Verify session_id format
        assert (
            session_chunk["session_id"] == "sample"
        ), f"Expected 'sample', got '{session_chunk['session_id']}'"

        # Verify events list
        assert isinstance(
            session_chunk["user_interactions"], list
        ), "events should be a list"
        assert (
            len(session_chunk["user_interactions"]) > 0
        ), "chunk should contain events"

        # Verify the sample fixture contains all major event types.
        # Collect all event sources from all chunks
        target_ids_found = set()
        actions_found = set()

        for event in session_chunk["user_interactions"]:
            target_ids_found.add(event.target_id)
            actions_found.add(event.action)

        assert "click" in actions_found, "Should contain click events"
        assert "input" in actions_found, "Should contain input events"
        assert (
            len(actions_found) <= 2
        ), "Should not contain unexpected actions (mouse interactions, scrolls, & other noise)"

        # Verify we have various target IDs
        expected_targets = {6, 10, 12}  # Based on our sample data
        found_targets = target_ids_found.intersection(expected_targets)
        assert (
            len(found_targets) >= 3
        ), f"Should find at least 3 targets, found: {found_targets}"

        # Test that event order & content is preserved
        assert session_chunk == snapshot(name="session_chunk")

    def test_ingest_session_file_not_found(self):
        """Test that FileNotFoundError is properly propagated."""
        with pytest.raises(FileNotFoundError):
            ingest_session("test", "/nonexistent/path/file.json")

    def test_ingest_session_invalid_json(self, create_session_file):
        """Test that JSONDecodeError is properly propagated."""
        temp_path = create_session_file([], raw_string='{"invalid": json}')

        with pytest.raises(json.JSONDecodeError):
            ingest_session("test", temp_path)

    def test_ingest_session_malformed_session_structure(self):
        """Test that ValueError is raised for malformed session structure."""
        # Create file without rrweb_data field
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"session_guid": "test", "metadata": {}}, f)
            f.flush()
            temp_path = f.name

        with pytest.raises(ValueError, match="Missing 'rrweb_data' field"):
            ingest_session("test", temp_path)

    def test_ingest_session_empty_session_id(self, create_session_file):
        """Test that empty session_id raises ValueError."""
        events = [{"type": 3, "timestamp": 1000, "data": {"source": 2}}]
        temp_path = create_session_file(events)

        with pytest.raises(ValueError, match="session_id cannot be empty"):
            ingest_session("", temp_path)

    def test_ingest_session_events_missing_required_fields(self, create_session_file):
        """Test that events missing required fields raise appropriate errors."""
        events = [
            {"type": 3, "data": {"source": 2}},  # Missing timestamp
        ]
        temp_path = create_session_file(events)

        with pytest.raises(ValueError, match="missing required fields"):
            ingest_session("test", temp_path)
