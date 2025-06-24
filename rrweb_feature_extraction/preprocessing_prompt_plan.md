Below is an **incremental implementation roadmap** for the **Input Ingestion & Preprocessing** module. Each step is self-contained, reviewable, and verifiable without breaking downstream behavior.

---

## 1. Project & Test Harness Setup

**Goal:** Establish repository structure, test framework, and basic CI.
**Accomplishes:**

* Create a new module/package (e.g. `rrweb_ingest/`)
* Add testing framework (e.g. pytest) and CI config stub
* Include a “hello ingestion” smoke test that imports the module
  **Verification:**
* All tests pass on checkout
* CI pipeline runs without errors

**Prompt for Coding Agent:**

You’re setting up the foundation for the **Input Ingestion & Preprocessing** module.

**Tasks:**

1. Create a new Python package named `rrweb_ingest/` with an `__init__.py`.
2. Initialize a Git repository (or ensure the folder is ready for version control).
3. Add a testing framework (using **pytest**):
   * Add `pytest` to `requirements.txt` or `pyproject.toml`.
   * Create a `rrweb_ingest/tests/` directory.
   * Write a basic smoke test in `rrweb_ingest/tests/test_smoke.py` that simply imports `rrweb_ingest` and asserts that the module loads without error.
4. Scaffold a Continuous Integration configuration file (e.g., `.github/workflows/ci.yml` or equivalent) that installs dependencies and runs `pytest`.

**Verification Criteria:**

* Running `pytest` passes with the single smoke test.
* CI pipeline configuration runs successfully (you can simulate it by running the CI steps locally).
* No production code is required beyond the package stub and the smoke test.

---

## 2. JSON Loader & Sorter

**Goal:** Implement `load_events(filepath)` to open, parse, validate, and sort a raw rrweb JSON file.
**Accomplishes:**

* File‐exists check + JSON parsing
* Schema check: each item has `type`, `timestamp`, `data`
* Return a list of events sorted by `timestamp`
  **Verification:**
* Unit tests validate correct sorting order
* Tests for malformed JSON and missing fields raise the expected exceptions

**Prompt for Coding Agent:**

You’re implementing the **JSON Loader & Sorter** for the Input Ingestion module.

**Tasks:**

1. In `rrweb_ingest/loader.py`, write a function `load_events(filepath: str) -> List[dict]` that:
   * Opens the file at `filepath`, reads its contents, and parses it as JSON.
   * Validates that the top-level JSON is a list and that each element is an object containing at least the keys `"type"`, `"timestamp"`, and `"data"`.
   * Raises a clear exception if the file doesn’t exist, isn’t valid JSON, or if any event is missing required fields.
   * Returns the list of events **sorted in ascending order** by their `timestamp`.
2. Add or update `rrweb_ingest/loader.py`’s docstring to describe the function’s behavior, inputs, outputs, and exceptions.
3. In `rrweb_ingest/tests/test_loader.py`, write unit tests covering:
   * Loading a well-formed small JSON session and verifying that the returned list is sorted.
   * Passing malformed JSON (invalid syntax) raises `JSONDecodeError`.
   * Passing a JSON array with an element missing `"type"`, `"timestamp"`, or `"data"` raises a `ValueError`.
   * Passing a non-list top-level JSON raises a `ValueError`.
**Verification Criteria:**
* All tests in `test_loader.py` pass under `pytest`.
* Calling `load_events` on a valid file returns the correctly sorted list without side-effects.
* Invalid inputs trigger the expected exception types and messages.
* No downstream functionality is affected; existing smoke tests still pass.

---

## 3. Event Classification

**Goal:** Add `classify_events(events)` to split into `snapshots`, `interactions`, and `others`.
**Accomplishes:**

* Iterate sorted events, assign to three buckets based on `type`
* Return a tuple `(snapshots, interactions, others)`
  **Verification:**
* Tests cover events of each `type` and assert correct bucket placement
* Edge case: empty event list yields three empty buckets

**Prompt for Coding Agent:**

You’re implementing **Event Classification** for the Input Ingestion module.

**Tasks:**

1. Create a new file `rrweb_ingest/classifier.py`.
2. In this file, implement a function `classify_events(events: List[dict]) -> Tuple[List[dict], List[dict], List[dict]]` that:
   * Accepts a **sorted** list of rrweb event dicts.
   * Splits them into three lists:
     * **`snapshots`**: all events where `event["type"] == 2` (FullSnapshot)
     * **`interactions`**: all events where `event["type"] == 3` (IncrementalSnapshot)
     * **`others`**: all remaining events
   * Returns `(snapshots, interactions, others)` in that exact order.
3. Add a module-level docstring and inline comments to explain classification logic.

**Testing:**

1. Create `rrweb_ingest/tests/test_classifier.py`.
2. Write unit tests to cover:

   * An empty event list returns three empty lists.
   * A mixed list of events with types 2, 3, and other values correctly populates each bucket.
   * Events with unexpected or missing `type` keys raise a `KeyError`.

**Verification Criteria:**

* All tests in `test_classifier.py` pass under `pytest`.
* The function signature and return order match the spec.
* Existing loader tests and smoke tests remain green.

---

## 4. Basic Chunk Segmentation

**Goal:** Implement `segment_into_chunks(interactions, snapshots)` that creates preliminary chunks at snapshot boundaries.
**Accomplishes:**

* Iterate `interactions`, start new chunk whenever hitting a `FullSnapshot` timestamp
* Produce a list of raw interaction lists
  **Verification:**
* Given synthetic interactions and snapshot events, assert chunk boundaries match snapshot positions
* No dropped or merged events beyond boundaries

**Prompt for Coding Agent:**

You’re implementing **Basic Chunk Segmentation** for the Input Ingestion module.

**Tasks:**

1. Create a new file `rrweb_ingest/segmenter.py`.
2. Implement a function
   ```python
   def segment_into_chunks(
       interactions: List[dict],
       snapshots: List[dict]
   ) -> List[List[dict]]:
       ...
   ```
   that:
   * Accepts two sorted lists of rrweb events:

     * `interactions`: events where `type == 3`.
     * `snapshots`: events where `type == 2`.
   * Iterates through `interactions`, starting a new chunk whenever:

     1. The timestamp of the next interaction meets or exceeds the next `FullSnapshot` timestamp.
     2. After crossing that boundary, uses subsequent snapshots in order.
   * Returns a list of chunks, where each chunk is a list of contiguous interaction events between snapshot boundaries.
3. Add docstrings that describe inputs, outputs, and the snapshot-boundary logic.

**Testing:**

1. Create `tests/test_segmenter.py`.
2. Write unit tests to cover:
   * No interactions and no snapshots → returns an empty list.
   * Interactions but no snapshots → returns a single chunk containing all interactions.
   * Multiple snapshots interleaved with interactions → splits interactions into the correct number of chunks at each snapshot timestamp.
   * Edge case where an interaction event timestamp exactly equals a snapshot timestamp → ensure boundary logic is consistent (e.g., interaction goes into the new chunk).

**Verification Criteria:**

* All tests in `test_segmenter.py` pass under `pytest`.
* Calling `segment_into_chunks` with sample data yields the expected chunk boundaries.
* No existing tests are broken by this change.

---

## 5. Time‐Gap & Size‐Cap Chunking

**Goal:** Enhance segmentation to respect `max_gap_ms` and `max_events` thresholds.
**Accomplishes:**

* Split chunks further when time gap between events exceeds threshold
* Enforce a maximum number of events per chunk
  **Verification:**
* Tests simulate gaps just below/above threshold and assert split/no‐split
* Tests simulate over‐sized chunks and assert automatic split

**Prompt for Coding Agent:**

You’re extending **Chunk Segmentation** to enforce time-gap and size-cap boundaries.

**Tasks:**

1. In `rrweb_ingest/segmenter.py`, update `segment_into_chunks` to also:

   * Split a chunk when the time difference between consecutive interaction events exceeds `max_gap_ms` (default 10 000 ms).
   * Split a chunk when the number of events in the current chunk reaches `max_events` (default 1000).
2. Introduce these thresholds as optional parameters on the function signature:

   ```python
   def segment_into_chunks(
       interactions: List[dict],
       snapshots: List[dict],
       max_gap_ms: int = 10_000,
       max_events: int = 1000
   ) -> List[List[dict]]:
   ```
3. Ensure that after a split, the next event starts a fresh chunk (i.e., no event is lost or duplicated).
4. Update the docstring to describe the new parameters and boundary logic.

**Testing:**

1. In `tests/test_segmenter.py`, add cases for:

   * A sequence of interactions with a gap just below `max_gap_ms` remains in one chunk, and with a gap just above splits into two.
   * A sequence of interactions exactly `max_events` long stays as one chunk, and one longer splits into two at the correct index.
   * Combined scenarios where both a time gap and size cap occur in the same stream.

**Verification Criteria:**

* All existing and new tests in `test_segmenter.py` pass under `pytest`.
* Segmentation behavior matches the spec for both time-gap and size-cap scenarios.
* No regressions: runs correctly when called without specifying `max_gap_ms` and `max_events` (defaults apply).

---

## 6. Noise-Filtering Framework

**Goal:** Introduce `is_low_signal(event)` predicate and `clean_chunk(events)` to drop trivial events.
**Accomplishes:**

* Define and document default noise rules (mousemove, micro-scroll, trivial mutation)
* Apply deduplication of identical events
  **Verification:**
* Parameterized tests for each noise rule ensure correct drop/keep decisions
* Duplicates in a chunk are reduced to one

**Prompt for Coding Agent:**

You’re building the **Noise-Filtering Framework** for the Input Ingestion module.

**Tasks:**

1. In `rrweb_feature_extraction/rrweb_ingest/filter.py`, implement a predicate function:

   ```python
   def is_low_signal(event: dict, micro_scroll_threshold: int = 20) -> bool:
       """
       Returns True if the event should be dropped as low-signal noise.
       """
   ```

   * Drop **mousemove** events (`source == 1`).
   * Drop **micro-scrolls** (`source == 3` with `abs(delta) < micro_scroll_threshold`).
   * Drop **trivial DOM mutations** (`source == 0` for insignificant attribute/text changes).
2. Implement a `clean_chunk` function in the same file:

   ```python
   def clean_chunk(events: List[dict]) -> List[dict]:
       """
       Removes low-signal and duplicate events from a chunk.
       """
   ```

   * Uses `is_low_signal` to filter out noise.
   * Deduplicates events by `(type, data.source, timestamp, target id)` so identical events appear only once.
3. Document both functions with clear docstrings describing parameters, return values, and default thresholds.

**Testing:**

1. Create `rrweb_feature_extraction/rrweb_ingest/tests/test_filter.py`.
2. Write unit tests for `is_low_signal` to confirm:

   * Mousemove events return `True`.
   * Scroll events below threshold return `True`; above threshold return `False`.
   * Simple mutation events with no meaningful change return `True`; significant mutation returns `False`.
3. Write tests for `clean_chunk` to confirm:

   * Noise events are removed.
   * Duplicate events are collapsed to one.
   * Non-noise, unique events are preserved in order.

**Verification Criteria:**

* All tests in `test_filter.py` pass under `pytest`.
* Filtering logic correctly drops or keeps events per the spec.
* Existing segmentation and loader tests remain unaffected.

---

## 7. Chunk Normalization & Schema

**Goal:** Wrap cleaned event lists into `Chunk` objects with standardized fields.
**Accomplishes:**

* Generate `chunk_id`, record `start_time`, `end_time`, `events`, and basic metadata (`num_events`, `duration_ms`)
* Define the `Chunk` dataclass or equivalent schema
  **Verification:**
* Tests confirm that fields match expectations on sample data
* JSON‐schema or type‐check validation passes for constructed chunks

**Prompt for Coding Agent:**

You’re implementing **Chunk Normalization & Schema** for the Input Ingestion module.

**Tasks:**

1. In `rrweb_feature_extraction/rrweb_ingest/models.py`, define a `Chunk` dataclass or equivalent schema with fields:

   ```python
   @dataclass
   class Chunk:
       chunk_id: str
       start_time: int
       end_time: int
       events: List[dict]
       metadata: dict
   ```

   * `metadata` should include at least `num_events` and `duration_ms`.
2. In `rrweb_feature_extraction/rrweb_ingest/normalizer.py`, implement a function:

   ```python
   def normalize_chunk(
       raw_events: List[dict],
       session_id: str,
       chunk_index: int
   ) -> Chunk:
       """
       Builds a Chunk object from a list of cleaned events.
       """
   ```

   * Compute `start_time` and `end_time` from the first and last event timestamps.
   * Generate `chunk_id` as `"{session_id}-chunk{chunk_index:03d}"`.
   * Populate `metadata` with `num_events` (length of `events`) and `duration_ms` (`end_time - start_time`).
   * Return the populated `Chunk` instance.
3. Add docstrings describing inputs, outputs, and chunk ID formatting rules.

**Testing:**

1. Create `rrweb_feature_extraction/rrweb_ingest/tests/test_normalizer.py`.
2. Write unit tests to cover:

   * A small list of synthetic events yields the correct `start_time`, `end_time`, `num_events`, `duration_ms`, and properly formatted `chunk_id`.
   * Edge case where all events share the same timestamp results in `duration_ms == 0`.
   * Passing an empty list of events raises a `ValueError` or similar.

**Verification Criteria:**

* All tests in `test_normalizer.py` pass under `pytest`.
* Calling `normalize_chunk` returns a `Chunk` matching the schema exactly.
* No downstream code is broken by introducing the new `Chunk` model.

---

## 8. End-to-End Ingest Pipeline

**Goal:** Wire together loader → classifier → segmentation → cleaning → normalization into `ingest_session(filepath)`.
**Accomplishes:**

* Single entry point that returns a list of `Chunk` instances
* Proper exception bubbling for invalid inputs
  **Verification:**
* Integration tests on real-world sample sessions verify consistent chunk counts and schema conformance
* Regression test ensures no change in chunk outputs for the same input

**Prompt for Coding Agent:**

You’re implementing the **End-to-End Ingest Pipeline** for the Input Ingestion module.

**Tasks:**

1. In `rrweb_feature_extraction/rrweb_ingest/pipeline.py`, create a function:

   ```python
   def ingest_session(
       session_id: str,
       filepath: str,
       *,
       max_gap_ms: int = 10_000,
       max_events: int = 1000,
       micro_scroll_threshold: int = 20
   ) -> List[Chunk]:
       """
       Load, classify, segment, filter, and normalize an rrweb session into Chunks.
       """
   ```
2. Inside `ingest_session`, sequentially invoke:

   * `load_events(filepath)`
   * `classify_events(...)`
   * `segment_into_chunks(...)` with `max_gap_ms` and `max_events`
   * For each raw chunk list:

     * `clean_chunk(...)` with `micro_scroll_threshold`
     * `normalize_chunk(...)` using `session_id` and chunk index
3. Ensure errors (e.g., file not found, invalid JSON) propagate cleanly to the caller.
4. Add a module-level docstring describing the overall pipeline and parameters.

**Testing:**

1. Create `rrweb_feature_extraction/rrweb_ingest/tests/test_pipeline.py`.
2. Write integration tests that:

   * Run `ingest_session` on a provided small sample rrweb JSON and assert:

     * The return value is a non-empty list of `Chunk` objects.
     * Each `Chunk` has `events`, `start_time`, `end_time`, and `metadata` populated.
   * Verify that changing `max_gap_ms` or `max_events` alters the number or size of chunks as expected.
   * Confirm that invalid file paths or malformed sessions raise the expected exceptions.

**Verification Criteria:**

* All new and existing tests (`loader`, `classifier`, `segmenter`, `filter`, `normalizer`) pass under `pytest`.
* `ingest_session` stitches together prior components without altering their individual behavior.
* CI pipeline remains green with the new integration tests included.


---

## 9. Configuration & Extensibility Hooks

**Goal:** Expose key thresholds (e.g. `max_gap_ms`, `max_events`) via a config object or parameters.
**Accomplishes:**

* Refactor hard-coded values into configurable settings
* Allow injection of custom noise filters
  **Verification:**
* Tests override thresholds and confirm altered chunking behavior
* Custom noise filter is invoked when provided

---

## 10. Documentation & Sample Data

**Goal:** Ship user-facing README and include a small sample rrweb JSON for manual exploration.
**Accomplishes:**

* Document each public function with expected inputs/outputs
* Provide example CLI or code snippet in README
  **Verification:**
* README code example runs successfully against the sample data
* Peer confirms documentation clarity in a short review
