# rrweb Feature Extraction - Input Ingestion & Preprocessing Todo List

## Step 1: Project & Test Harness Setup

### Tasks:
- [x] Create `rrweb_ingest/` package directory structure
- [x] Add `__init__.py` to make it a proper Python package
- [x] Initialize Git repository or ensure folder is version control ready
- [x] Add pytest to project dependencies (`requirements.txt` or `pyproject.toml`)
- [x] Create `rrweb_ingest/tests/` directory for test files
- [x] Write basic smoke test in `tests/test_smoke.py` that imports `rrweb_ingest`
- [x] Create CI configuration file (`.github/workflows/ci.yml` or equivalent)
- [x] Configure CI to install dependencies and run pytest
- [x] Verify pytest runs successfully with smoke test
- [x] Test CI pipeline locally or in CI environment

## Step 2: JSON Loader & Sorter

### Tasks:
- [x] Implement `load_events(filepath)` function in `rrweb_ingest/loader.py`
- [x] Add file existence check with appropriate error handling
- [x] Parse JSON content into Python list structure
- [x] Validate each event has required fields: `type`, `timestamp`, `data`
- [x] Sort events by `timestamp` in ascending order
- [x] Handle malformed JSON with `JSONDecodeError` exceptions
- [x] Handle missing required fields with `ValueError` exceptions
- [x] Write unit tests for valid JSON loading and sorting
- [x] Write unit tests for malformed JSON error cases
- [x] Write unit tests for missing field validation
- [x] Test with sample rrweb JSON files
- [x] Verify correct timestamp sorting behavior

## Step 3: Event Classification

### Tasks:
- [x] Implement `classify_events(events)` function in `rrweb_ingest/classifier.py`
- [x] Create logic to separate events by `type` field:
  - [x] `type == 2` → snapshots (FullSnapshot)
  - [x] `type == 3` → interactions (IncrementalSnapshot)
  - [x] All other types → others (Meta, Custom, Plugin, etc.)
- [x] Return tuple of `(snapshots, interactions, others)` lists
- [x] Write unit tests for each event type classification
- [x] Test with mixed event types to verify correct bucketing
- [x] Test edge case: empty event list returns three empty lists
- [x] Verify no events are lost or duplicated during classification
- [ ] Add logging for classification statistics

## Step 4: Basic Chunk Segmentation

### Tasks:
- [x] Implement `segment_into_chunks(interactions, snapshots)` in `rrweb_ingest/segmenter.py`
- [x] Create logic to start new chunks at FullSnapshot boundaries
- [x] Iterate through interactions and group by snapshot timestamps
- [x] Handle case where no snapshots exist
- [x] Return list of raw interaction event lists (chunks)
- [x] Write unit tests with synthetic interaction and snapshot data
- [x] Test chunk boundaries align with snapshot positions
- [x] Verify no events are dropped during segmentation
- [x] Test edge cases: no snapshots, no interactions, single events
- [ ] Add logging for chunk count and sizes

## Step 5: Time-Gap & Size-Cap Chunking

### Tasks:
- [x] Enhance segmentation to respect `max_gap_ms` threshold (default 10,000ms)
- [x] Add logic to split chunks when time gap between events exceeds threshold
- [x] Implement `max_events` cap per chunk (default 1000 events)
- [ ] Add `max_duration_ms` cap per chunk (default 30,000ms)
- [x] Update `segment_into_chunks()` to handle all splitting criteria
- [x] Make thresholds configurable via parameters
- [x] Write unit tests for time gap splitting just below/above threshold
- [x] Write unit tests for event count cap enforcement
- [ ] Write unit tests for duration cap enforcement
- [x] Test combinations of multiple splitting criteria
- [x] Verify chunk sizes stay within all specified limits

## Step 6: Noise-Filtering Framework

### Tasks:
- [x] Implement `is_low_signal(event)` predicate function in `rrweb_ingest/filter.py`
- [x] Define noise rules for mousemove-only events (`source == 1`)
- [x] Define noise rules for micro-scrolls (`source == 3`, `|delta| < 20px`)
- [x] Define noise rules for trivial DOM mutations
- [ ] Define noise rules for incomplete input events (no submit/blur)
- [x] Implement `clean_chunk(events)` function to apply filters
- [x] Add deduplication logic for identical events
- [ ] Make noise rules configurable and extensible
- [x] Write parameterized tests for each noise rule type
- [x] Test that duplicates are properly removed
- [x] Test that legitimate events are preserved
- [ ] Add logging for filter statistics (kept vs. dropped)

## Step 7: Chunk Normalization & Schema

### Tasks:
- [x] Define `Chunk` dataclass in `rrweb_ingest/models.py`
- [x] Include fields: `chunk_id`, `start_time`, `end_time`, `events`, `metadata`
- [x] Implement chunk ID generation (`<session>-chunk<index>` format)
- [x] Calculate `start_time` and `end_time` from event timestamps
- [x] Add metadata fields: `num_events`, `duration_ms`, `snapshot_before`
- [x] Implement function to wrap cleaned events into Chunk objects
- [ ] Add JSON serialization support for Chunk objects
- [x] Write unit tests for Chunk object creation
- [x] Test field calculations match expected values
- [ ] Test JSON schema validation for Chunk objects
- [x] Verify chunk IDs are unique and properly formatted

## Step 8: End-to-End Ingest Pipeline

### Tasks:
- [ ] Implement `ingest_session(filepath)` main entry point in `rrweb_ingest/__init__.py`
- [ ] Wire together: loader → classifier → segmentation → cleaning → normalization
- [ ] Return list of `Chunk` instances from complete pipeline
- [ ] Ensure proper exception bubbling for invalid inputs
- [ ] Add comprehensive error handling and logging
- [ ] Write integration tests with real-world sample rrweb sessions
- [ ] Test with various session sizes and complexity levels
- [ ] Verify consistent chunk counts for same input data
- [ ] Test error handling for corrupted or invalid session files
- [ ] Add regression tests to prevent output changes
- [ ] Document expected input/output formats

## Step 9: Configuration & Extensibility Hooks

### Tasks:
- [ ] Create `Config` class or configuration object in `rrweb_ingest/config.py`
- [ ] Make configurable: `max_gap_ms`, `max_events`, `max_duration_ms`
- [ ] Make configurable: `micro_scroll_threshold`, noise filter rules
- [ ] Allow injection of custom noise filter functions
- [ ] Support configuration via file, environment variables, or parameters
- [ ] Update all functions to accept configuration parameters
- [ ] Write unit tests with overridden configuration values
- [ ] Test that custom noise filters are properly invoked
- [ ] Verify configuration changes affect chunking behavior as expected
- [ ] Add validation for configuration parameter ranges
- [ ] Document all configuration options

## Step 10: Documentation & Sample Data

### Tasks:
- [ ] Create comprehensive README.md with usage examples
- [ ] Document each public function with docstrings (inputs/outputs/exceptions)
- [ ] Include sample rrweb JSON file for testing and demonstration
- [ ] Provide CLI usage example or code snippet in README
- [ ] Add API documentation for all public classes and functions
- [ ] Create example scripts showing common usage patterns
- [ ] Document configuration options and their effects
- [ ] Add troubleshooting section for common issues
- [ ] Test that README code examples run successfully
- [ ] Get peer review of documentation for clarity and completeness
- [ ] Add performance benchmarks and expected processing times
- [ ] Include information about supported rrweb versions and formats
