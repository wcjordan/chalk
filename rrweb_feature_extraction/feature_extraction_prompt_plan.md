Below is an **incremental implementation roadmap** for the **Session Chunking & Feature Extraction** module. Each step is self-contained, reviewable in isolation, and verifiable without impacting existing preprocessing functionality.

---

## 1. Define Data Models & Test Harness

**What it accomplishes:**

* Introduce the `FeatureChunk`, `DomMutation`, `UserInteraction`, `EventDelay`, `UINode`, `MouseCluster`, and `ScrollPattern` data classes or schemas.
* Scaffold a test module for feature-extraction with fixtures for minimal `Chunk` inputs.

**How to verify:**

* Code review confirms all classes are declared and imported correctly.
* A placeholder test loads an empty `Chunk` and asserts a `FeatureChunk` can be constructed without errors.

---

## 2. Virtual DOM State Initialization

**What it accomplishes:**

* On receipt of a `Chunk`, consume any accompanying full-snapshot event and build the initial `node_by_id` map with node metadata.

**How to verify:**

* Unit test supplies a synthetic “full snapshot” payload and asserts that `node_by_id` contains the correct node IDs, tags, and attributes.

---

## 3. Virtual DOM Mutation Updates

**What it accomplishes:**

* Apply mutation events (`source == 0`) within a chunk to incrementally update `node_by_id`: handle adds, removes, attribute/text changes.

**How to verify:**

* Tests feed a sequence of mutation events and check that after each call the in-memory DOM reflects the expected additions, deletions, and updates.

---

## 4. DOM Mutation Extraction

**What it accomplishes:**

* Walk each event in a chunk and emit a list of structured `DomMutation` records (adds/removes/attribute/text).

**How to verify:**

* Given a chunk with known mutation events, assert that the extractor returns the correct number and types of `DomMutation` structs with matching timestamps.

---

## 5. User Interaction Extraction

**What it accomplishes:**

* Identify and extract click, input, and scroll events (`sources` 2, 5, 3) into a list of `UserInteraction` records.

**How to verify:**

* Supply mixed-source events to the extractor and verify only the intended interactions are returned, with correct fields populated.

---

## 6. Delay Computation

**What it accomplishes:**

* Compute inter-event time deltas and “reaction” delays (e.g., from click to next mutation) and output a list of `EventDelay` entries.

**How to verify:**

* Test with a known sequence of timestamps and confirm that every consecutive pair produces the correct delta, and specific “reaction” patterns are captured.

---

## 7. UI Metadata Resolution

**What it accomplishes:**

* For every extracted interaction and mutation, look up its `UINode` in `node_by_id` and emit enriched metadata: tag, `aria-label`, `data-testid`, role, DOM path.

**How to verify:**

* Create a small DOM map and ensure calls to the resolver generate the expected human-readable metadata and correct DOM path strings.

---

## 8. Mouse Trajectory Clustering

**What it accomplishes:**

* Cluster mousemove events (`source == 1`) within a chunk into `MouseCluster` objects based on configurable temporal and spatial thresholds.

**How to verify:**

* Feed in synthetic mouse paths with known gaps/distances and assert clusters split or merge according to the thresholds, checking cluster start/end times and path lengths.

---

## 9. Scroll-Pattern Detection

**What it accomplishes:**

* Identify scroll events and pair them with subsequent DOM mutations (within a maximum delay) to produce `ScrollPattern` records.

**How to verify:**

* Provide a series of scroll and mutation events with controlled timing and verify that only those within the specified window are paired, with correct delay values.

---

## 10. Assemble & Integrate Extractors

**What it accomplishes:**

* Wire steps 2–9 into a single `extract_features(chunk)` function that returns a populated `FeatureChunk`.
* Preserve existing `Chunk` inputs and do not alter preprocessing outputs.

**How to verify:**

* End-to-end tests against sample chunks confirm that each feature list (`dom_mutations`, `interactions`, `delays`, etc.) is non-empty and matches expected counts/values.
* Regression tests ensure feature extraction does not throw errors or mutate input chunks.

---

## 11. Configuration & Extensibility

**What it accomplishes:**

* Externalize key thresholds (e.g., time/distance for clustering) into a configurable settings object.
* Allow injection of custom filters or resolvers.

**How to verify:**

* Tests override configuration values and validate that clustering, delay detection, and noise filtering adjust behavior accordingly.
* Code review confirms settings are documented and used in all relevant steps.

---

## 12. Documentation & Sample Data

**What it accomplishes:**

* Update module README with usage examples for `extract_features`.
* Add a small, annotated sample `Chunk` JSON and expected `FeatureChunk` output for manual validation.

**How to verify:**

* Running the example in the README produces the documented output.
* Peer review of documentation ensures clarity and completeness.
