"""
Unit tests for the segmenter module.

Tests the segment_into_chunks function to ensure proper segmentation of interaction
events based on FullSnapshot boundaries.
"""

from rrweb_ingest.segmenter import segment_into_chunks
from rrweb_ingest import config


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


def test_time_gap_just_below_threshold():
    """Test that time gap just below max_gap_ms keeps events in same chunk."""
    interactions = [
        {"type": 3, "timestamp": 1000, "data": {"id": "int1"}},
        {
            "type": 3,
            "timestamp": 10999,
            "data": {"id": "int2"},
        },  # Gap of 9999ms < 10000ms
        {"type": 3, "timestamp": 11000, "data": {"id": "int3"}},
    ]

    result = segment_into_chunks(interactions, [], max_gap_ms=10_000)

    # Should remain in single chunk since gap is below threshold
    assert len(result) == 1
    assert len(result[0]) == 3
    assert result[0][0]["data"]["id"] == "int1"
    assert result[0][1]["data"]["id"] == "int2"
    assert result[0][2]["data"]["id"] == "int3"


def test_time_gap_just_above_threshold():
    """Test that time gap just above max_gap_ms splits into separate chunks."""
    interactions = [
        {"type": 3, "timestamp": 1000, "data": {"id": "int1"}},
        {
            "type": 3,
            "timestamp": 11001,
            "data": {"id": "int2"},
        },  # Gap of 10001ms > 10000ms
        {"type": 3, "timestamp": 11100, "data": {"id": "int3"}},
    ]

    result = segment_into_chunks(interactions, [], max_gap_ms=10_000)

    # Should split into two chunks due to large gap
    assert len(result) == 2

    # First chunk: before gap
    assert len(result[0]) == 1
    assert result[0][0]["data"]["id"] == "int1"

    # Second chunk: after gap
    assert len(result[1]) == 2
    assert result[1][0]["data"]["id"] == "int2"
    assert result[1][1]["data"]["id"] == "int3"


def test_multiple_time_gaps():
    """Test multiple time gaps create multiple chunks."""
    interactions = [
        {"type": 3, "timestamp": 1000, "data": {"id": "int1"}},
        {"type": 3, "timestamp": 1100, "data": {"id": "int2"}},
        {"type": 3, "timestamp": 12000, "data": {"id": "int3"}},  # Gap > 10000ms
        {"type": 3, "timestamp": 12100, "data": {"id": "int4"}},
        {
            "type": 3,
            "timestamp": 25000,
            "data": {"id": "int5"},
        },  # Another gap > 10000ms
    ]

    result = segment_into_chunks(interactions, [], max_gap_ms=10_000)

    assert len(result) == 3

    # First chunk
    assert len(result[0]) == 2
    assert result[0][0]["data"]["id"] == "int1"
    assert result[0][1]["data"]["id"] == "int2"

    # Second chunk
    assert len(result[1]) == 2
    assert result[1][0]["data"]["id"] == "int3"
    assert result[1][1]["data"]["id"] == "int4"

    # Third chunk
    assert len(result[2]) == 1
    assert result[2][0]["data"]["id"] == "int5"


def test_max_events_exactly_at_limit():
    """Test that chunk with exactly max_events stays as one chunk."""
    interactions = [
        {"type": 3, "timestamp": i * 100, "data": {"id": f"int{i}"}}
        for i in range(5)  # Exactly 5 events
    ]

    result = segment_into_chunks(interactions, [], max_events=5)

    # Should remain as single chunk
    assert len(result) == 1
    assert len(result[0]) == 5


def test_max_events_exceeds_limit():
    """Test that chunk exceeding max_events splits correctly."""
    interactions = [
        {"type": 3, "timestamp": i * 100, "data": {"id": f"int{i}"}}
        for i in range(7)  # 7 events, limit is 5
    ]

    result = segment_into_chunks(interactions, [], max_events=5)

    # Should split into two chunks: 5 + 2
    assert len(result) == 2
    assert len(result[0]) == 5
    assert len(result[1]) == 2

    # Verify correct events in each chunk
    assert result[0][0]["data"]["id"] == "int0"
    assert result[0][4]["data"]["id"] == "int4"
    assert result[1][0]["data"]["id"] == "int5"
    assert result[1][1]["data"]["id"] == "int6"


def test_multiple_size_splits():
    """Test multiple size-based splits create correct chunks."""
    interactions = [
        {"type": 3, "timestamp": i * 100, "data": {"id": f"int{i}"}}
        for i in range(12)  # 12 events, limit is 5
    ]

    result = segment_into_chunks(interactions, [], max_events=5)

    # Should split into three chunks: 5 + 5 + 2
    assert len(result) == 3
    assert len(result[0]) == 5
    assert len(result[1]) == 5
    assert len(result[2]) == 2


def test_combined_snapshot_and_time_gap():
    """Test combination of snapshot boundary and time gap splitting."""
    interactions = [
        {"type": 3, "timestamp": 100, "data": {"id": "int1"}},
        {"type": 3, "timestamp": 200, "data": {"id": "int2"}},
        {
            "type": 3,
            "timestamp": 15000,
            "data": {"id": "int3"},
        },  # Large gap after snapshot
        {"type": 3, "timestamp": 15100, "data": {"id": "int4"}},
    ]
    snapshots = [
        {"type": 2, "timestamp": 150, "data": {"id": "snap1"}},
    ]

    result = segment_into_chunks(interactions, snapshots, max_gap_ms=10_000)

    # Should create 3 chunks: before snapshot, after snapshot before gap, after gap
    assert len(result) == 3

    # First chunk: before snapshot
    assert len(result[0]) == 1
    assert result[0][0]["data"]["id"] == "int1"

    # Second chunk: after snapshot, before gap
    assert len(result[1]) == 1
    assert result[1][0]["data"]["id"] == "int2"

    # Third chunk: after gap
    assert len(result[2]) == 2
    assert result[2][0]["data"]["id"] == "int3"
    assert result[2][1]["data"]["id"] == "int4"


def test_combined_snapshot_and_size_limit():
    """Test combination of snapshot boundary and size limit splitting."""
    interactions = [
        {"type": 3, "timestamp": 50, "data": {"id": f"int{i}"}}
        for i in range(3)  # 3 events before snapshot
    ] + [
        {"type": 3, "timestamp": 200 + i * 10, "data": {"id": f"int{i+3}"}}
        for i in range(7)  # 7 events after snapshot, exceeds limit of 5
    ]
    snapshots = [
        {"type": 2, "timestamp": 100, "data": {"id": "snap1"}},
    ]

    result = segment_into_chunks(interactions, snapshots, max_events=5)

    # Should create 3 chunks: 3 before snapshot, 5 after snapshot, 2 remaining
    assert len(result) == 3
    assert len(result[0]) == 3  # Before snapshot
    assert len(result[1]) == 5  # After snapshot, up to size limit
    assert len(result[2]) == 2  # Remaining events


def test_combined_time_gap_and_size_limit():
    """Test combination of time gap and size limit splitting."""
    interactions = (
        [
            {"type": 3, "timestamp": i * 100, "data": {"id": f"int{i}"}}
            for i in range(4)  # 4 events close together
        ]
        + [{"type": 3, "timestamp": 15000, "data": {"id": "int4"}}]  # Large gap
        + [
            {"type": 3, "timestamp": 15000 + i * 100, "data": {"id": f"int{i+5}"}}
            for i in range(7)  # 7 more events, exceeds limit
        ]
    )

    result = segment_into_chunks(interactions, [], max_gap_ms=10_000, max_events=5)

    # Should create 3 chunks: 4 before gap, 5 after gap, 3 remaining
    assert len(result) == 3
    assert len(result[0]) == 4  # Before time gap
    assert len(result[1]) == 5  # After gap, up to size limit
    assert len(result[2]) == 3  # Remaining events


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

    result = segment_into_chunks(
        interactions, snapshots, max_gap_ms=10_000, max_events=5
    )

    # Should create 4 chunks: 2 before snapshot, 5 after snapshot, 1 remaining, 2 after gap
    assert len(result) == 4
    assert len(result[0]) == 2  # Before snapshot
    assert len(result[1]) == 5  # After snapshot, up to size limit
    assert len(result[2]) == 1  # Remaining event before gap
    assert len(result[3]) == 2  # After time gap


def test_default_parameters_work():
    """Test that function works correctly with default parameters."""
    interactions = [
        {"type": 3, "timestamp": 1000, "data": {"id": "int1"}},
        {"type": 3, "timestamp": 2000, "data": {"id": "int2"}},
    ]

    # Should work without specifying max_gap_ms and max_events
    result = segment_into_chunks(interactions, [])

    assert len(result) == 1
    assert len(result[0]) == 2


def test_config_override_max_gap_ms():
    """Test that overriding max_gap_ms affects chunking behavior."""
    interactions = [
        {"type": 3, "timestamp": 1000, "data": {"id": "int1"}},
        {"type": 3, "timestamp": 8000, "data": {"id": "int2"}},  # 7s gap
    ]

    # With default config (10s), should stay in one chunk
    result_default = segment_into_chunks(interactions, [])
    assert len(result_default) == 1

    # With smaller threshold (5s), should split
    result_small = segment_into_chunks(interactions, [], max_gap_ms=5000)
    assert len(result_small) == 2


def test_config_override_max_events():
    """Test that overriding max_events affects chunking behavior."""
    interactions = [
        {"type": 3, "timestamp": i * 100, "data": {"id": f"int{i}"}} for i in range(10)
    ]

    # With default config (1000), should stay in one chunk
    result_default = segment_into_chunks(interactions, [])
    assert len(result_default) == 1

    # With smaller limit (5), should split
    result_small = segment_into_chunks(interactions, [], max_events=5)
    assert len(result_small) == 2
    assert len(result_small[0]) == 5
    assert len(result_small[1]) == 5


def test_uses_config_defaults_when_none_provided():
    """Test that function uses config defaults when None is explicitly passed."""
    interactions = [
        {"type": 3, "timestamp": 1000, "data": {"id": "int1"}},
        {"type": 3, "timestamp": 2000, "data": {"id": "int2"}},
    ]

    # Explicitly pass None to test default fallback
    result = segment_into_chunks(interactions, [], max_gap_ms=None, max_events=None)

    assert len(result) == 1
    assert len(result[0]) == 2
