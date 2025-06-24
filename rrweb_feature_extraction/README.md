# rrweb Feature Extraction - Input Ingestion & Preprocessing

## Overview

The **rrweb Feature Extraction** module processes raw `rrweb` session recordings (JSON files ~200KB–2MB) and transforms them into clean, structured "chunks" ready for downstream feature extraction and behavior analysis.

This module is responsible for:

1. **Loading & validating** rrweb JSON session files
2. **Sorting & classifying** events into snapshots, interactions, and other categories
3. **Segmenting** the interaction stream into meaningful chunks based on time gaps, size limits, and snapshot boundaries
4. **Filtering out noise** (cursor-only moves, micro-scrolls, trivial mutations)
5. **Normalizing** chunks into structured objects with metadata

## Public Functions

### Core Pipeline Function

- **`ingest_session(session_id, filepath, **kwargs)`** - Main entry point that processes an entire rrweb session file and returns a list of normalized `Chunk` objects

### Individual Processing Functions

- **`load_events(filepath)`** - Loads and validates rrweb JSON, returns sorted events
- **`classify_events(events)`** - Separates events into snapshots, interactions, and others
- **`segment_into_chunks(interactions, snapshots, **kwargs)`** - Groups interactions into logical chunks
- **`clean_chunk(events, **kwargs)`** - Removes low-signal noise and duplicate events
- **`normalize_chunk(raw_events, session_id, chunk_index)`** - Wraps cleaned events into structured `Chunk` objects

## Installation

Install dependencies using:

```bash
make init
```

Or manually install with:

```bash
pip install -r requirements.txt
```

## Usage Example

```python
from rrweb_ingest import ingest_session

# Process an rrweb session file
chunks = ingest_session("session1", "path/to/sample.json")

# Print chunk summaries
for chunk in chunks:
    print(f"Chunk: {chunk.chunk_id}")
    print(f"  Time: {chunk.start_time} - {chunk.end_time}")
    print(f"  Duration: {chunk.metadata['duration_ms']}ms")
    print(f"  Events: {chunk.metadata['num_events']}")
    print()
```

## Configuration

The ingestion process can be configured with various parameters:

```python
chunks = ingest_session(
    "session1", 
    "path/to/sample.json",
    max_gap_ms=15000,           # Split chunks on gaps > 15s
    max_events=500,             # Max 500 events per chunk
    max_duration_ms=45000,      # Max 45s duration per chunk
    micro_scroll_threshold=30   # Filter scrolls < 30px
)
```

## Chunk Schema

Each processed chunk follows this structure:

```python
@dataclass
class Chunk:
    chunk_id: str              # Format: "{session_id}-chunk{index:03d}"
    start_time: int            # Timestamp of first event
    end_time: int              # Timestamp of last event
    events: List[dict]         # Filtered rrweb events
    metadata: dict             # Additional info (num_events, duration_ms, etc.)
```

## Testing

Run the test suite:

```bash
pytest rrweb_ingest/tests/
```

Run with coverage:

```bash
pytest --cov=rrweb_ingest rrweb_ingest/tests/
```

## Sample Data

A sample rrweb session file is included at `rrweb_ingest/tests/fixtures/rrweb_sample.json` for testing and demonstration purposes.
