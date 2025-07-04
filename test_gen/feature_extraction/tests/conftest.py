"""Common test fixtures"""

import pytest


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
