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

---

## 5. Time‐Gap & Size‐Cap Chunking

**Goal:** Enhance segmentation to respect `max_gap_ms` and `max_events` thresholds.
**Accomplishes:**

* Split chunks further when time gap between events exceeds threshold
* Enforce a maximum number of events per chunk
  **Verification:**
* Tests simulate gaps just below/above threshold and assert split/no‐split
* Tests simulate over‐sized chunks and assert automatic split

---

## 6. Noise-Filtering Framework

**Goal:** Introduce `is_low_signal(event)` predicate and `clean_chunk(events)` to drop trivial events.
**Accomplishes:**

* Define and document default noise rules (mousemove, micro-scroll, trivial mutation)
* Apply deduplication of identical events
  **Verification:**
* Parameterized tests for each noise rule ensure correct drop/keep decisions
* Duplicates in a chunk are reduced to one

---

## 7. Chunk Normalization & Schema

**Goal:** Wrap cleaned event lists into `Chunk` objects with standardized fields.
**Accomplishes:**

* Generate `chunk_id`, record `start_time`, `end_time`, `events`, and basic metadata (`num_events`, `duration_ms`)
* Define the `Chunk` dataclass or equivalent schema
  **Verification:**
* Tests confirm that fields match expectations on sample data
* JSON‐schema or type‐check validation passes for constructed chunks

---

## 8. End-to-End Ingest Pipeline

**Goal:** Wire together loader → classifier → segmentation → cleaning → normalization into `ingest_session(filepath)`.
**Accomplishes:**

* Single entry point that returns a list of `Chunk` instances
* Proper exception bubbling for invalid inputs
  **Verification:**
* Integration tests on real-world sample sessions verify consistent chunk counts and schema conformance
* Regression test ensures no change in chunk outputs for the same input

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
