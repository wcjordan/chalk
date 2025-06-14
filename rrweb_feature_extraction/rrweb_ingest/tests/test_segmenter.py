"""
Unit tests for the segmenter module.

Tests the segment_into_chunks function to ensure proper segmentation of interaction
events based on FullSnapshot boundaries.
"""

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


def test_single_snapshot_splits_interactions():
    """Test that a single snapshot correctly splits interactions."""
    interactions = [
        {"type": 3, "timestamp": 100, "data": {"id": "int1"}},
        {"type": 3, "timestamp": 200, "data": {"id": "int2"}},
        {"type": 3, "timestamp": 400, "data": {"id": "int3"}},
        {"type": 3, "timestamp": 500, "data": {"id": "int4"}},
    ]
    snapshots = [
        {"type": 2, "timestamp": 300, "data": {"id": "snap1"}},
    ]

    result = segment_into_chunks(interactions, snapshots)

    assert len(result) == 2
    # First chunk: interactions before snapshot timestamp 300
    assert len(result[0]) == 2
    assert result[0][0]["data"]["id"] == "int1"  # timestamp 100
    assert result[0][1]["data"]["id"] == "int2"  # timestamp 200

    # Second chunk: interactions at or after snapshot timestamp 300
    assert len(result[1]) == 2
    assert result[1][0]["data"]["id"] == "int3"  # timestamp 400
    assert result[1][1]["data"]["id"] == "int4"  # timestamp 500


def test_multiple_snapshots_create_multiple_chunks():
    """Test that multiple snapshots create the correct number of chunks."""
    interactions = [
        {"type": 3, "timestamp": 50, "data": {"id": "int1"}},
        {"type": 3, "timestamp": 150, "data": {"id": "int2"}},
        {"type": 3, "timestamp": 250, "data": {"id": "int3"}},
        {"type": 3, "timestamp": 350, "data": {"id": "int4"}},
        {"type": 3, "timestamp": 450, "data": {"id": "int5"}},
    ]
    snapshots = [
        {"type": 2, "timestamp": 100, "data": {"id": "snap1"}},
        {"type": 2, "timestamp": 200, "data": {"id": "snap2"}},
        {"type": 2, "timestamp": 400, "data": {"id": "snap3"}},
    ]

    result = segment_into_chunks(interactions, snapshots)

    assert len(result) == len(snapshots) + 1

    # Chunk 1: before first snapshot (timestamp < 100)
    assert len(result[0]) == 1
    assert result[0][0]["data"]["id"] == "int1"  # timestamp 50

    # Chunk 2: between first and second snapshot (100 <= timestamp < 200)
    assert len(result[1]) == 1
    assert result[1][0]["data"]["id"] == "int2"  # timestamp 150

    # Chunk 3: between second and third snapshot (200 <= timestamp < 400)
    assert len(result[2]) == 2
    assert result[2][0]["data"]["id"] == "int3"  # timestamp 250
    assert result[2][1]["data"]["id"] == "int4"  # timestamp 350

    # Chunk 4: after last snapshot (timestamp >= 400)
    assert len(result[3]) == 1
    assert result[3][0]["data"]["id"] == "int5"  # timestamp 450


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
