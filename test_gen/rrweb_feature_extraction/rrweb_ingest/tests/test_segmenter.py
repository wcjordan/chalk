"""
Unit tests for the segmenter module.

Tests the segment_into_chunks function to ensure proper segmentation of interaction
events based on FullSnapshot boundaries.
"""

from unittest.mock import patch

from rrweb_ingest.segmenter import segment_into_chunks


def test_no_interactions_no_snapshots():
    """Test that empty inputs return an empty list."""
    result = segment_into_chunks([], [])
    assert not result


def test_no_interactions_with_snapshots():
    """Test that no interactions with snapshots returns an empty list."""
    snapshots = [
        {"type": 2, "timestamp": 1000, "data": {}},
        {"type": 2, "timestamp": 2000, "data": {}},
    ]
    result = segment_into_chunks([], snapshots)
    assert not result


def test_interactions_no_snapshots():
    """Test that interactions without snapshots returns a single chunk."""
    interactions = [
        {"type": 3, "timestamp": 100, "data": {"id": "int1"}},
        {"type": 3, "timestamp": 200, "data": {"id": "int2"}},
        {"type": 3, "timestamp": 300, "data": {"id": "int3"}},
    ]

    result = segment_into_chunks(interactions, [])

    assert len(result) == 1
    assert result[0] == interactions


def test_interaction_timestamp_equals_snapshot_timestamp():
    """Test boundary condition where interaction timestamp equals snapshot timestamp."""
    interactions = [
        {"type": 3, "timestamp": 100, "data": {"id": "int1"}},
        {"type": 3, "timestamp": 200, "data": {"id": "int2"}},  # Equals snapshot
        {"type": 3, "timestamp": 300, "data": {"id": "int3"}},
    ]
    snapshots = [
        {"type": 2, "timestamp": 200, "data": {"id": "snap1"}},
    ]

    result = segment_into_chunks(interactions, snapshots)

    assert len(result) == 2

    # First chunk: interactions before snapshot timestamp
    assert len(result[0]) == 1
    assert result[0][0]["data"]["id"] == "int1"  # timestamp 100

    # Second chunk: interactions at or after snapshot timestamp (>= 200)
    assert len(result[1]) == 2
    assert result[1][0]["data"]["id"] == "int2"  # timestamp 200 (equals snapshot)
    assert result[1][1]["data"]["id"] == "int3"  # timestamp 300


def test_all_interactions_before_snapshots():
    """Test case where all interactions occur before any snapshots."""
    interactions = [
        {"type": 3, "timestamp": 50, "data": {"id": "int1"}},
        {"type": 3, "timestamp": 75, "data": {"id": "int2"}},
    ]
    snapshots = [
        {"type": 2, "timestamp": 100, "data": {"id": "snap1"}},
        {"type": 2, "timestamp": 200, "data": {"id": "snap2"}},
    ]

    result = segment_into_chunks(interactions, snapshots)

    assert len(result) == 1
    assert len(result[0]) == len(interactions)
    assert result[0] == interactions


def test_all_interactions_after_snapshots():
    """Test case where all interactions occur after all snapshots."""
    interactions = [
        {"type": 3, "timestamp": 300, "data": {"id": "int1"}},
        {"type": 3, "timestamp": 400, "data": {"id": "int2"}},
    ]
    snapshots = [
        {"type": 2, "timestamp": 100, "data": {"id": "snap1"}},
        {"type": 2, "timestamp": 200, "data": {"id": "snap2"}},
    ]

    result = segment_into_chunks(interactions, snapshots)

    assert len(result) == 1
    assert len(result[0]) == 2
    assert result[0] == interactions


def test_consecutive_snapshots_create_empty_chunks():
    """Test that consecutive snapshots don't create empty chunks."""
    interactions = [
        {"type": 3, "timestamp": 50, "data": {"id": "int1"}},
        {"type": 3, "timestamp": 350, "data": {"id": "int2"}},
    ]
    snapshots = [
        {"type": 2, "timestamp": 100, "data": {"id": "snap1"}},
        {
            "type": 2,
            "timestamp": 200,
            "data": {"id": "snap2"},
        },  # No interactions between 100-200
        {
            "type": 2,
            "timestamp": 300,
            "data": {"id": "snap3"},
        },  # No interactions between 200-300
    ]

    result = segment_into_chunks(interactions, snapshots)

    # Should only create chunks where there are actual interactions
    assert len(result) == 2

    # First chunk: before first snapshot
    assert len(result[0]) == 1
    assert result[0][0]["data"]["id"] == "int1"  # timestamp 50

    # Second chunk: after all snapshots
    assert len(result[1]) == 1
    assert result[1][0]["data"]["id"] == "int2"  # timestamp 350


def test_all_three_splitting_criteria():
    """Test combination of snapshot, time gap, and size limit splitting."""
    interactions = (
        [
            {"type": 3, "timestamp": 50, "data": {"id": "int0"}},
            {"type": 3, "timestamp": 60, "data": {"id": "int1"}},
        ]
        + [
            {"type": 3, "timestamp": 200 + i * 10, "data": {"id": f"int{i+2}"}}
            for i in range(6)  # 6 events after snapshot, exceeds limit of 5
        ]
        + [
            {"type": 3, "timestamp": 15000, "data": {"id": "int8"}},  # Large gap
            {"type": 3, "timestamp": 15100, "data": {"id": "int9"}},
        ]
    )
    snapshots = [
        {"type": 2, "timestamp": 100, "data": {"id": "snap1"}},
    ]

    with patch("rrweb_ingest.segmenter.config.MAX_GAP_MS", 10_000), patch(
        "rrweb_ingest.segmenter.config.MAX_EVENTS", 5
    ):
        result = segment_into_chunks(interactions, snapshots)

    # Should create 4 chunks: 2 before snapshot, 5 after snapshot, 1 remaining, 2 after gap
    assert len(result) == 4
    assert len(result[0]) == 2  # Before snapshot
    assert len(result[1]) == 5  # After snapshot, up to size limit
    assert len(result[2]) == 1  # Remaining event before gap
    assert len(result[3]) == 2  # After time gap
