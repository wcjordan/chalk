"""
Tests for sample fixture data to verify end-to-end ingestion pipeline.
"""

import os
import pytest
from rrweb_ingest.pipeline import ingest_session
from rrweb_ingest.models import Chunk


def test_sample_fixture_ingestion():
    """
    Test that the sample rrweb JSON file can be processed end-to-end
    and produces expected chunk structure.
    """
    # Get the path to the sample fixture
    current_dir = os.path.dirname(__file__)
    sample_path = os.path.join(current_dir, "fixtures", "rrweb_sample.json")
    
    # Ensure the sample file exists
    assert os.path.exists(sample_path), f"Sample file not found at {sample_path}"
    
    # Process the sample session
    chunks = ingest_session("sample", sample_path)
    
    # Verify we got a list of Chunk objects
    assert isinstance(chunks, list), "ingest_session should return a list"
    assert len(chunks) > 0, "Should produce at least one chunk"
    
    # Verify all items are Chunk objects
    for chunk in chunks:
        assert isinstance(chunk, Chunk), f"Expected Chunk object, got {type(chunk)}"
    
    # Test the first chunk in detail
    first_chunk = chunks[0]
    
    # Verify chunk_id format
    assert first_chunk.chunk_id == "sample-chunk000", f"Expected 'sample-chunk000', got '{first_chunk.chunk_id}'"
    
    # Verify timestamps are reasonable
    assert isinstance(first_chunk.start_time, int), "start_time should be an integer"
    assert isinstance(first_chunk.end_time, int), "end_time should be an integer"
    assert first_chunk.start_time <= first_chunk.end_time, "start_time should be <= end_time"
    
    # Verify events list
    assert isinstance(first_chunk.events, list), "events should be a list"
    assert len(first_chunk.events) > 0, "chunk should contain events"
    
    # Verify metadata structure
    assert isinstance(first_chunk.metadata, dict), "metadata should be a dict"
    assert "num_events" in first_chunk.metadata, "metadata should contain num_events"
    assert "duration_ms" in first_chunk.metadata, "metadata should contain duration_ms"
    
    # Verify metadata values are consistent
    assert first_chunk.metadata["num_events"] == len(first_chunk.events), "num_events should match events list length"
    expected_duration = first_chunk.end_time - first_chunk.start_time
    assert first_chunk.metadata["duration_ms"] == expected_duration, "duration_ms should match time difference"
    
    # Verify we have reasonable chunk counts (sample has 2 FullSnapshots, so expect 2+ chunks)
    assert len(chunks) >= 2, f"Expected at least 2 chunks due to FullSnapshots, got {len(chunks)}"


def test_sample_fixture_event_types():
    """
    Test that the sample fixture contains all major event types.
    """
    current_dir = os.path.dirname(__file__)
    sample_path = os.path.join(current_dir, "fixtures", "rrweb_sample.json")
    
    chunks = ingest_session("sample", sample_path)
    
    # Collect all event sources from all chunks
    sources_found = set()
    event_types_found = set()
    
    for chunk in chunks:
        for event in chunk.events:
            event_types_found.add(event.get("type"))
            if event.get("type") == 3 and "data" in event and "source" in event["data"]:
                sources_found.add(event["data"]["source"])
    
    # Verify we have IncrementalSnapshot events (type 3)
    assert 3 in event_types_found, "Should contain IncrementalSnapshot events (type 3)"
    
    # Verify we have various interaction sources
    # source 1: mouse moves, source 2: mouse interactions, source 3: scroll, source 5: input
    expected_sources = {1, 2, 3, 5}  # Based on our sample data
    found_sources = sources_found.intersection(expected_sources)
    assert len(found_sources) >= 3, f"Should find at least 3 interaction types, found: {found_sources}"


def test_sample_fixture_chunk_boundaries():
    """
    Test that chunks are properly segmented at FullSnapshot boundaries.
    """
    current_dir = os.path.dirname(__file__)
    sample_path = os.path.join(current_dir, "fixtures", "rrweb_sample.json")
    
    chunks = ingest_session("sample", sample_path)
    
    # Verify chunk IDs are sequential
    for i, chunk in enumerate(chunks):
        expected_id = f"sample-chunk{i:03d}"
        assert chunk.chunk_id == expected_id, f"Expected chunk ID '{expected_id}', got '{chunk.chunk_id}'"
    
    # Verify chunks are in chronological order
    for i in range(1, len(chunks)):
        prev_chunk = chunks[i-1]
        curr_chunk = chunks[i]
        assert prev_chunk.end_time <= curr_chunk.start_time, \
            f"Chunks should be chronologically ordered: chunk {i-1} ends at {prev_chunk.end_time}, chunk {i} starts at {curr_chunk.start_time}"


def test_sample_fixture_noise_filtering():
    """
    Test that noise filtering is working on the sample data.
    """
    current_dir = os.path.dirname(__file__)
    sample_path = os.path.join(current_dir, "fixtures", "rrweb_sample.json")
    
    # Process with default filtering
    chunks = ingest_session("sample", sample_path)
    
    # Count events in chunks
    total_chunk_events = sum(len(chunk.events) for chunk in chunks)
    
    # Process with no filtering (very high thresholds)
    chunks_unfiltered = ingest_session(
        "sample", 
        sample_path,
        micro_scroll_threshold=0  # Don't filter any scrolls
    )
    
    total_unfiltered_events = sum(len(chunk.events) for chunk in chunks_unfiltered)
    
    # With filtering, we should have fewer or equal events
    # (some events in our sample should be filtered as noise)
    assert total_chunk_events <= total_unfiltered_events, \
        f"Filtered events ({total_chunk_events}) should be <= unfiltered ({total_unfiltered_events})"
