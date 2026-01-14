"""Common test fixtures"""

import pytest

from feature_extraction.models import FeatureChunk, create_empty_features_obj


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
