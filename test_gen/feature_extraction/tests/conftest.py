"""Common test fixtures"""

import pytest

from feature_extraction.models import FeatureChunk, create_empty_features_obj


@pytest.fixture()
def create_full_snapshot_event():
    """Helper for creating a full snapshot data structure."""

    def _create_full_snapshot(
        node_id=1, timestamp=0, node_type="div", attributes=None, child_nodes=None
    ):
        """Create a full snapshot event with given parameters."""
        return {
            "type": 2,
            "timestamp": timestamp,
            "data": {
                "node": {
                    "id": node_id,
                    "type": node_type,
                    "attributes": attributes or {},
                    "childNodes": child_nodes or [],
                }
            },
        }

    return _create_full_snapshot


@pytest.fixture(name="empty_feature_chunk")
def fixture_empty_feature_chunk():
    """Fixture providing an empty feature chunk."""
    return FeatureChunk(
        chunk_id="empty-chunk",
        start_time=0,
        end_time=1000,
        events=[],
        features=create_empty_features_obj(),
        metadata={},
    )
