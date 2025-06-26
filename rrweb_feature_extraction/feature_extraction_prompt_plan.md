Below is an **incremental implementation roadmap** for the **Session Chunking & Feature Extraction** module. Each step is self-contained, reviewable in isolation, and verifiable without impacting existing preprocessing functionality.

---

## 1. Define Data Models & Test Harness

**What it accomplishes:**

* Introduce the `FeatureChunk`, `DomMutation`, `UserInteraction`, `EventDelay`, `UINode`, `MouseCluster`, and `ScrollPattern` data classes or schemas.
* Scaffold a test module for feature-extraction with fixtures for minimal `Chunk` inputs.

**How to verify:**

* Code review confirms all classes are declared and imported correctly.
* A placeholder test loads an empty `Chunk` and asserts a `FeatureChunk` can be constructed without errors.

**Prompt for Coding Agent:**

> You’re setting up the foundation for the **Session Chunking & Feature Extraction** module.
>
> **Tasks:**
>
> 1. Create a new Python module `rrweb_features/models.py`.
> 2. In this file, define the following data classes (or equivalent schemas):
>
>    * **`DomMutation`**: captures mutation type (add/remove/attribute/text), target node ID, details, and timestamp.
>    * **`UserInteraction`**: captures action type (click/input/scroll), target node ID, any value/x/y fields, and timestamp.
>    * **`EventDelay`**: captures two event IDs or timestamps and the delta between them.
>    * **`UINode`**: captures node ID, tag name, attributes dict, text content, and parent ID.
>    * **`MouseCluster`**: captures cluster start/end timestamps, list of (x,y,ts) points, and optionally cluster duration or length.
>    * **`ScrollPattern`**: captures the scroll event, the paired mutation event, and the delay.
>    * **`FeatureChunk`**: aggregates a chunk’s `chunk_id`, `start_time`, `end_time`, original events list, and a `features` dict containing lists of the above objects.
> 3. Add type hints and module‐level docstrings explaining each class’s purpose.
> 4. Scaffold a test module `tests/test_models.py` that:
>
>    * Imports each class and constructs one instance of each with dummy values.
>    * Asserts that attributes are stored correctly (e.g., `mutation.timestamp == 12345`).
>    * Verifies that a `FeatureChunk` can be instantiated with empty lists for all feature fields.
>
> **Verification Criteria:**
>
> * Code review confirms all data classes are declared with the required fields and type hints.
> * Running `pytest tests/test_models.py` passes without errors.
> * No existing preprocessing tests are broken by these additions.

---

## 2. Virtual DOM State Initialization

**What it accomplishes:**

* On receipt of a `Chunk`, consume any accompanying full-snapshot event and build the initial `node_by_id` map with node metadata.

**How to verify:**

* Unit test supplies a synthetic “full snapshot” payload and asserts that `node_by_id` contains the correct node IDs, tags, and attributes.

**Prompt for Coding Agent:**

> You’re implementing **Virtual DOM State Initialization** for the Session Chunking & Feature Extraction module.
>
> **Tasks:**
>
> 1. Create a new file `rrweb_features/dom_state.py`.
> 2. In this file, implement a function:
>
>    ```python
>    def init_dom_state(full_snapshot_event: dict) -> Dict[int, UINode]:
>        """
>        Given a FullSnapshot rrweb event, builds and returns a node_by_id map.
>        """
>    ```
>
>    * The `full_snapshot_event` is an rrweb event with `type == 2` and `data.node` (or equivalent) containing the entire DOM tree.
>    * Traverse the snapshot payload and instantiate a `UINode` for each DOM node, capturing:
>
>      * `id` (node identifier)
>      * `tag` (tagName or type)
>      * `attributes` (attribute dict)
>      * `text` (textContent, if present)
>      * `parent` (parent node ID, or `None` for root)
>    * Return a `dict` mapping each node’s integer ID to its `UINode` instance.
> 3. Add a module‐level docstring explaining that this creates the initial virtual DOM from the first snapshot.
>
> **Testing:**
>
> 1. Create `tests/test_dom_state.py`.
> 2. Write unit tests to cover:
>
>    * Passing a synthetic FullSnapshot event with a simple DOM tree (e.g., root with two children) results in a `node_by_id` dict with the correct keys and `UINode` fields.
>    * The root node’s parent is `None`.
>    * Node attributes and textContent are captured exactly.
>
> **Verification Criteria:**
>
> * `pytest tests/test_dom_state.py` passes without errors.
> * Code review confirms correct traversal of the snapshot structure and accurate population of the `UINode` map.
> * No existing feature extraction or ingestion tests are broken by this addition.

---

## 3. Virtual DOM Mutation Updates

**What it accomplishes:**

* Apply mutation events (`source == 0`) within a chunk to incrementally update `node_by_id`: handle adds, removes, attribute/text changes.

**How to verify:**

* Tests feed a sequence of mutation events and check that after each call the in-memory DOM reflects the expected additions, deletions, and updates.

**Prompt for Coding Agent:**

> You’re implementing **Virtual DOM Mutation Updates** for the Session Chunking & Feature Extraction module.
>
> **Tasks:**
>
> 1. In `rrweb_features/dom_state.py`, add a function:
>
>    ```python
>    def apply_mutations(
>        node_by_id: Dict[int, UINode],
>        mutation_events: List[dict]
>    ) -> None:
>        """
>        Applies a sequence of rrweb mutation events to update the in-memory DOM state in place.
>        """
>    ```
>
>    * **Handle “adds”**: for each `added` record in an event’s `data.adds`, create a new `UINode` and insert it into `node_by_id` under its `id`.
>    * **Handle “removes”**: for each `removed` record in `data.removes`, delete that node’s ID from `node_by_id`.
>    * **Handle “attributes”**: for each attribute mutation in `data.attributes`, update the corresponding `UINode.attributes` dict.
>    * **Handle “texts”**: for each text mutation in `data.texts`, update the corresponding `UINode.text` field.
>    * Ignore any mutation entries without matching node IDs.
> 2. Update the module docstring to explain that this function maintains the evolving DOM based on incremental snapshots.
>
> **Testing:**
>
> 1. In `tests/test_dom_state.py`, add tests for `apply_mutations`:
>
>    * Start with a small `node_by_id` map (e.g., two nodes), apply a mutation event that:
>
>      * Adds a new child node → assert the new `UINode` appears.
>      * Removes an existing node → assert it’s deleted.
>      * Changes an attribute on one node → assert `attributes` updated.
>      * Changes text on one node → assert `text` updated.
>    * Test that invalid mutation entries (e.g., referencing nonexistent node IDs) are safely ignored without error.
>
> **Verification Criteria:**
>
> * `pytest tests/test_dom_state.py` passes, including new mutation update tests.
> * Code review confirms that `apply_mutations` mutates `node_by_id` correctly and handles all mutation types.
> * No regressions in existing virtual DOM initialization tests.

---

## 4. DOM Mutation Extraction

**What it accomplishes:**

* Walk each event in a chunk and emit a list of structured `DomMutation` records (adds/removes/attribute/text).

**How to verify:**

* Given a chunk with known mutation events, assert that the extractor returns the correct number and types of `DomMutation` structs with matching timestamps.

**Prompt for Coding Agent:**

> You’re implementing **DOM Mutation Extraction** for the Session Chunking & Feature Extraction module.
>
> **Tasks:**
>
> 1. Create or update `rrweb_features/extractors.py` (or a dedicated `dom_extractor.py`).
> 2. Implement a function:
>
>    ```python
>    def extract_dom_mutations(events: List[dict]) -> List[DomMutation]:
>        """
>        From a list of rrweb events, return structured DomMutation records
>        for all mutation events (source == 0).
>        """
>    ```
>
>    * Iterate over each event where `event["type"] == 3` and `event["data"]["source"] == 0`.
>    * For each event, emit one `DomMutation` entry per:
>
>      * **Attribute changes** (`data.attributes`): capture node ID, changed attributes dict, and timestamp.
>      * **Text changes** (`data.texts`): capture node ID, new text value, and timestamp.
>      * **Node additions** (`data.adds`): capture parent ID, new node’s ID, tag, attributes, text (if any), and timestamp.
>      * **Node removals** (`data.removes`): capture removed node ID and timestamp.
>    * Ensure the returned list preserves the original event order.
> 3. Add a docstring explaining the function’s purpose, inputs, and outputs.
>
> **Testing:**
>
> 1. Create `tests/test_dom_extractor.py`.
> 2. Write unit tests to cover:
>
>    * A single mutation event with multiple attribute changes produces one `DomMutation` per attribute.
>    * A text-change event produces a `DomMutation` of type `"text"`.
>    * An add/remove event produces the appropriate `DomMutation` entries with correct fields.
>    * A mixed sequence of mutation and non-mutation events: only mutation events are extracted.
>    * Events with empty `data.attributes`, `data.texts`, `data.adds`, or `data.removes` do not produce spurious entries.
>
> **Verification Criteria:**
>
> * `pytest tests/test_dom_extractor.py` passes without failures.
> * The extracted `DomMutation` objects match expected properties (type, node IDs, values, timestamp) in all test cases.
> * No existing feature-extraction tests are broken by this change.

---

## 5. User Interaction Extraction

**What it accomplishes:**

* Identify and extract click, input, and scroll events (`sources` 2, 5, 3) into a list of `UserInteraction` records.

**How to verify:**

* Supply mixed-source events to the extractor and verify only the intended interactions are returned, with correct fields populated.

**Prompt for Coding Agent:**

> You’re implementing **User Interaction Extraction** for the Session Chunking & Feature Extraction module.
>
> **Tasks:**
>
> 1. In `rrweb_features/extractors.py`, implement a function:
>
>    ```python
>    def extract_user_interactions(events: List[dict]) -> List[UserInteraction]:
>        """
>        From a list of rrweb events, return structured UserInteraction records
>        for click, input, and scroll actions.
>        """
>    ```
>
>    * Iterate over each event where `event["type"] == 3`.
>    * For events with `data.source == 2`, emit a `UserInteraction` of type `"click"` (include `target_id`, `x`, `y`, `timestamp`).
>    * For `data.source == 5`, emit a `UserInteraction` of type `"input"` (include `target_id`, `value` or `checked`, `timestamp`).
>    * For `data.source == 3`, emit a `UserInteraction` of type `"scroll"` (include `target_id`, `x`, `y`, `timestamp`).
>    * Ignore other sources.
>    * Preserve event order in the returned list.
> 2. Add a docstring explaining inputs, outputs, and the mapping from `data.source` values to interaction types.
>
> **Testing:**
>
> 1. Create `tests/test_interactions_extractor.py`.
> 2. Write unit tests to cover:
>
>    * A mixed list of incremental snapshot events yields only click, input, and scroll interactions.
>    * Click events correctly produce type `"click"` with the right coordinates and target.
>    * Input events capture `value` or `checked` fields as expected.
>    * Scroll events produce `"scroll"` interactions with `x`/`y` data.
>    * Non-interaction sources are ignored.
>
> **Verification Criteria:**
>
> * `pytest tests/test_interactions_extractor.py` passes without failures.
> * The returned `UserInteraction` objects have correct types and fields according to the spec.
> * No regressions in existing feature-extraction or preprocessing tests.

---

## 6. Delay Computation

**What it accomplishes:**

* Compute inter-event time deltas and “reaction” delays (e.g., from click to next mutation) and output a list of `EventDelay` entries.

**How to verify:**

* Test with a known sequence of timestamps and confirm that every consecutive pair produces the correct delta, and specific “reaction” patterns are captured.

**Prompt for Coding Agent:**

> You’re implementing **Delay Computation** for the Session Chunking & Feature Extraction module.
>
> **Tasks:**
>
> 1. In `rrweb_features/extractors.py` (or a dedicated `delay_extractor.py`), implement two functions:
>
>    ```python
>    def compute_inter_event_delays(events: List[dict]) -> List[EventDelay]:
>        """
>        For a list of rrweb events sorted by timestamp, return an EventDelay
>        record for each consecutive pair, capturing `from_ts`, `to_ts`, and `delta_ms`.
>        """
>    ```
>
>    ```python
>    def compute_reaction_delays(
>        events: List[dict],
>        interaction_source: int = 2,      # click
>        mutation_source: int = 0,         # DOM mutation
>        max_reaction_ms: int = 10000
>    ) -> List[EventDelay]:
>        """
>        For each user interaction event (source == interaction_source),
>        find the next mutation event (source == mutation_source) within
>        `max_reaction_ms` milliseconds and emit an EventDelay capturing
>        the interaction timestamp, mutation timestamp, and delta.
>        """
>    ```
> 2. Add docstrings explaining each function’s inputs, outputs, and parameter meanings.
>
> **Testing:**
>
> 1. Create `tests/test_delay_extractor.py`.
> 2. Write unit tests to cover:
>
>    * **Inter-event delays:** Given events with timestamps \[1000, 1500, 3000], assert two delays (500 ms, 1500 ms) with correct `from_ts`/`to_ts`.
>    * **Reaction delays within window:** For a click at 1000 ms and mutation at 1800 ms, assert one reaction delay of 800 ms.
>    * **No reaction outside window:** If the next mutation is at 12000 ms (> `max_reaction_ms`), assert no reaction delay is emitted.
>    * **Multiple interactions:** For clicks at 1000 and 2000 ms followed by mutations at 1100 and 2500 ms, assert two reaction delays.
>    * **Non-interaction sources ignored:** Ensure only events with the specified sources are considered.
>
> **Verification Criteria:**
>
> * Running `pytest tests/test_delay_extractor.py` passes all cases.
> * `compute_inter_event_delays` returns one `EventDelay` per adjacent event pair.
> * `compute_reaction_delays` returns one `EventDelay` per valid interaction→mutation pairing within the `max_reaction_ms` window.
> * No regressions in existing feature-extraction or preprocessing tests.

---

## 7. UI Metadata Resolution

**What it accomplishes:**

* For every extracted interaction and mutation, look up its `UINode` in `node_by_id` and emit enriched metadata: tag, `aria-label`, `data-testid`, role, DOM path.

**How to verify:**

* Create a small DOM map and ensure calls to the resolver generate the expected human-readable metadata and correct DOM path strings.

**Prompt for Coding Agent:**

> You’re implementing **UI Metadata Resolution** for the Session Chunking & Feature Extraction module.
>
> **Tasks:**
>
> 1. In `rrweb_features/metadata.py`, implement a function:
>
>    ```python
>    def resolve_node_metadata(
>        node_id: int,
>        node_by_id: Dict[int, UINode]
>    ) -> Dict[str, Any]:
>        """
>        Given a node ID and the current virtual DOM map, return a metadata
>        dict including:
>          - tag (e.g., “button”, “input”)
>          - aria_label (from attributes or None)
>          - data_testid (from attributes or None)
>          - role (from attributes or None)
>          - text (text content or None)
>          - dom_path (e.g., “html > body > div > button#submit”)
>        """
>    ```
>
>    * Look up the `UINode` by `node_id` in `node_by_id`.
>    * Extract `tag`, `attributes["aria-label"]`, `attributes["data-testid"]`, `attributes["role"]`, and `text`.
>    * Compute `dom_path` by walking `.parent` pointers to the root, concatenating tag names and IDs/classes as identifiers.
>    * Return a dict with those five keys.
> 2. Add a module‐level docstring explaining that this function provides human-readable context for UI nodes.
>
> **Testing:**
>
> 1. Create `tests/test_metadata.py`.
> 2. Write unit tests that:
>
>    * Given a simple `node_by_id` map with nested nodes, `resolve_node_metadata` returns the correct `dom_path`.
>    * Nodes with and without `aria-label`, `data-testid`, and `role` attributes correctly produce `None` or the attribute value.
>    * Text content is captured accurately.
>    * Passing a nonexistent `node_id` raises a `KeyError` or returns a clear error.
>
> **Verification Criteria:**
>
> * `pytest tests/test_metadata.py` passes all tests.
> * The returned metadata dict has exactly the specified keys with correct values.
> * No regressions in existing feature-extraction or preprocessing tests.

---

## 8. Mouse Trajectory Clustering

**What it accomplishes:**

* Cluster mousemove events (`source == 1`) within a chunk into `MouseCluster` objects based on configurable temporal and spatial thresholds.

**How to verify:**

* Feed in synthetic mouse paths with known gaps/distances and assert clusters split or merge according to the thresholds, checking cluster start/end times and path lengths.

**Prompt for Coding Agent:**

> You’re implementing **Mouse Trajectory Clustering** for the Session Chunking & Feature Extraction module.
>
> **Tasks:**
>
> 1. In `rrweb_features/clustering.py`, implement a function:
>
>    ```python
>    def cluster_mouse_trajectories(
>        events: List[dict],
>        time_delta_ms: int = 100,
>        dist_delta_px: int = 50
>    ) -> List[MouseCluster]:
>        """
>        Groups rrweb mousemove events into clusters based on temporal
>        and spatial proximity.
>        """
>    ```
>
>    * Iterate through `events`, filtering only those where `type == 3` and `data.source == 1`.
>    * For each event, compute the time difference and Euclidean distance to the previous mousemove.
>    * Start a new cluster whenever either threshold is exceeded; otherwise, append to the current cluster.
>    * For each cluster, build a `MouseCluster` object capturing:
>
>      * `start_ts` and `end_ts`
>      * Ordered list of points `[{x, y, ts}, …]`
>      * `duration_ms` and `point_count`
>    * Return the list of clusters in chronological order.
> 2. Add a module‐level docstring explaining clustering parameters and usage.
>
> **Testing:**
>
> 1. Create `tests/test_clustering.py`.
> 2. Write unit tests that:
>
>    * Given consecutive mousemove events within both thresholds, they form a single cluster.
>    * Given events separated by more than `time_delta_ms`, they split into two clusters.
>    * Given events with spatial separation exceeding `dist_delta_px`, they split into two clusters.
>    * A mix of temporal and spatial splits produces the correct number of clusters with accurate `start_ts`, `end_ts`, and `point_count`.
>    * Passing no mousemove events returns an empty list.
>
> **Verification Criteria:**
>
> * Running `pytest tests/test_clustering.py` passes all cases.
> * Clusters match expected boundaries and metrics based on synthetic event streams.
> * No regressions in existing feature‐extraction or preprocessing tests.

---

## 9. Scroll-Pattern Detection

**What it accomplishes:**

* Identify scroll events and pair them with subsequent DOM mutations (within a maximum delay) to produce `ScrollPattern` records.

**How to verify:**

* Provide a series of scroll and mutation events with controlled timing and verify that only those within the specified window are paired, with correct delay values.

**Prompt for Coding Agent:**

> You’re implementing **Scroll-Pattern Detection** for the Session Chunking & Feature Extraction module.
>
> **Tasks:**
>
> 1. In `rrweb_features/scroll_patterns.py`, implement a function:
>
>    ```python
>    def detect_scroll_patterns(
>        events: List[dict],
>        max_reaction_ms: int = 2000
>    ) -> List[ScrollPattern]:
>        """
>        Identifies scroll events followed by DOM mutations within a time window.
>        """
>    ```
>
>    * Iterate through `events`, filtering for scroll events (`type == 3`, `data.source == 3`).
>    * For each scroll, look ahead for the next mutation event (`type == 3`, `data.source == 0`) whose `timestamp` is within `max_reaction_ms` of the scroll.
>    * When a valid pair is found, create a `ScrollPattern` record containing the scroll event, the matched mutation event, and the delay between them.
>    * Reset the lookahead cursor after a match so that each scroll matches at most one mutation.
>    * Return all `ScrollPattern` records in chronological order.
> 2. Add a module‐level docstring explaining the purpose of detecting scroll→mutation patterns and the meaning of `max_reaction_ms`.
>
> **Testing:**
>
> 1. Create `tests/test_scroll_patterns.py`.
> 2. Write unit tests that verify:
>
>    * A scroll event followed by a mutation within `max_reaction_ms` yields one `ScrollPattern`.
>    * A scroll event with no subsequent mutation, or with the next mutation outside the time window, yields no pattern.
>    * Multiple scrolls each match to their nearest valid mutation when within the window.
>    * Events out of order or non-scroll/mutation sources are ignored.
>    * Passing an empty event list returns an empty list.
>
> **Verification Criteria:**
>
> * `pytest tests/test_scroll_patterns.py` passes all scenarios.
> * The `ScrollPattern` objects correctly capture the scroll event, mutation event, and delay.
> * No regressions in existing feature-extraction or preprocessing tests.

---

## 10. Assemble & Integrate Extractors

**What it accomplishes:**

* Wire steps 2–9 into a single `extract_features(chunk)` function that returns a populated `FeatureChunk`.
* Preserve existing `Chunk` inputs and do not alter preprocessing outputs.

**How to verify:**

* End-to-end tests against sample chunks confirm that each feature list (`dom_mutations`, `interactions`, `delays`, etc.) is non-empty and matches expected counts/values.
* Regression tests ensure feature extraction does not throw errors or mutate input chunks.

**Prompt for Coding Agent:**

> You’re implementing the **Assemble & Integrate Extractors** step for the Session Chunking & Feature Extraction module.
>
> **Tasks:**
>
> 1. Create a new file `rrweb_features/pipeline.py`.
> 2. In this file, implement a function:
>
>    ```python
>    def extract_features(
>        chunk: Chunk,
>        dom_state: Dict[int, UINode]
>    ) -> FeatureChunk:
>        """
>        Given a preprocessed Chunk and its initial virtual DOM state,
>        run all feature extractors and return a populated FeatureChunk.
>        """
>    ```
> 3. Inside `extract_features`, perform the following in order:
>
>    * **Apply mutations** from the chunk to update `dom_state`.
>    * **Extract** and collect:
>
>      * `DomMutation` entries via `extract_dom_mutations`
>      * `UserInteraction` entries via `extract_user_interactions`
>      * `EventDelay` entries via `compute_inter_event_delays` and `compute_reaction_delays`
>      * UI metadata for each mutation and interaction using `resolve_node_metadata`
>      * `MouseCluster` entries via `cluster_mouse_trajectories`
>      * `ScrollPattern` entries via `detect_scroll_patterns`
>    * **Assemble** all results into a new `FeatureChunk`, copying `chunk_id`, `start_time`, `end_time`, and original `events`.
> 4. Add a module‐level docstring describing the overall extraction pipeline and its inputs/outputs.
>
> **Testing:**
>
> 1. Create `tests/test_pipeline_features.py`.
> 2. Write an integration test that:
>
>    * Feeds a sample `Chunk` (with a FullSnapshot event and a few interaction/mutation events) and its `dom_state` into `extract_features`.
>    * Asserts that the returned `FeatureChunk` has non-empty lists for each feature category and that all timestamps and IDs align with the input events.
>    * Verifies that calling `extract_features` twice on the same input yields identical results without side effects.
>
> **Verification Criteria:**
>
> * `pytest tests/test_pipeline_features.py` passes.
> * `FeatureChunk` contains all expected feature lists populated correctly.
> * No regressions in existing ingestion or extractor tests.

---

## 11. Configuration & Extensibility

**What it accomplishes:**

* Externalize key thresholds (e.g., time/distance for clustering) into a configurable settings object.
* Allow injection of custom filters or resolvers.

**How to verify:**

* Tests override configuration values and validate that clustering, delay detection, and noise filtering adjust behavior accordingly.
* Code review confirms settings are documented and used in all relevant steps.

**Prompt for Coding Agent:**

> You’re adding **Configuration & Extensibility Hooks** to the Session Chunking & Feature Extraction module.
>
> **Tasks:**
>
> 1. Create a new module `rrweb_features/config.py` that defines default parameters for all extractors, for example:
>
>    ```python
>    # rrweb_features/config.py
>    DEFAULT_TIME_DELTA_MS = 100
>    DEFAULT_DIST_DELTA_PX = 50
>    DEFAULT_SCROLL_REACTION_MS = 2000
>    DEFAULT_MAX_REACTION_MS = 10000
>    ```
> 2. Refactor existing extractor functions in `dom_state.py`, `extractors.py`, `clustering.py`, `scroll_patterns.py`, and `pipeline.py` to import and use these defaults instead of hard-coded literals. Ensure each function signature accepts optional overrides that default to the values in `config.py`.
> 3. Introduce at least one extensibility hook:
>
>    * In the metadata resolver, allow passing a custom formatting function for DOM paths.
>    * Or in clustering, accept a pluggable distance or time comparator.
> 4. Update docstrings in each affected module to document:
>
>    * Which config constants are used,
>    * How to override them via function parameters,
>    * How to supply custom hooks or plugins.
>
> **Testing:**
>
> 1. Create `tests/test_config_features.py`.
> 2. Write unit tests to verify:
>
>    * The `config` module exports the correct default values.
>    * Calling clustering and scroll-pattern functions with custom parameter overrides changes their behavior (e.g., smaller `DEFAULT_DIST_DELTA_PX` splits clusters earlier).
>    * A custom DOM path formatter passed into the metadata resolver is invoked and its output appears in the returned metadata.
>
> **Verification Criteria:**
>
> * All existing feature-extraction and pipeline tests still pass under `pytest`.
> * New tests in `test_config_features.py` pass, demonstrating both default and overridden configurations.
> * Code review confirms no remaining hard-coded thresholds and clear documentation of extensibility points.

---

## 12. Documentation & Sample Data

**What it accomplishes:**

* Update module README with usage examples for `extract_features`.
* Add a small, annotated sample `Chunk` JSON and expected `FeatureChunk` output for manual validation.

**How to verify:**

* Running the example in the README produces the documented output.
* Peer review of documentation ensures clarity and completeness.

**Prompt for Coding Agent:**

> You’re creating **Documentation & Sample Data** for the Session Chunking & Feature Extraction module.
>
> **Tasks:**
>
> 1. **Update `README.md`** at the project root (or in `rrweb_features/README.md`) to include:
>
>    * A concise overview of the module’s purpose and key functions (`init_dom_state`, `apply_mutations`, `extract_dom_mutations`, `extract_user_interactions`, `compute_inter_event_delays`, `compute_reaction_delays`, `resolve_node_metadata`, `cluster_mouse_trajectories`, `detect_scroll_patterns`, `extract_features`).
>    * Installation instructions and dependencies.
>    * A usage example showing how to:
>
>      ```python
>      from rrweb_ingest.pipeline import ingest_session
>      from rrweb_features.dom_state import init_dom_state
>      from rrweb_features.pipeline import extract_features
>
>      chunks = ingest_session("mysession", "path/to/session.json")
>      for chunk in chunks:
>          if chunk.metadata.get("snapshot_before"):
>              dom = init_dom_state(chunk.metadata["snapshot_before"])
>          feature_chunk = extract_features(chunk, dom)
>          print(f"{feature_chunk.chunk_id}:",
>                len(feature_chunk.features["dom_mutations"]),
>                len(feature_chunk.features["mouse_clusters"]))
>      ```
> 2. **Add sample data** under `tests/fixtures/`:
>
>    * `sample_session.json`: a small rrweb session (\~15–25 events) that includes at least one FullSnapshot, several IncrementalSnapshots covering clicks, inputs, mutations, mousemoves, and scrolls.
>    * `sample_featurechunk.json` (optional): expected output structure for one chunk after feature extraction.
> 3. **Write a fixtures-based test** in `tests/test_fixtures_features.py` that:
>
>    * Loads `sample_session.json` via `ingest_session`.
>    * Initializes DOM with `init_dom_state` from the first chunk’s `snapshot_before`.
>    * Calls `extract_features` on the first chunk.
>    * Asserts that each feature list (`dom_mutations`, `interactions`, `delays`, `ui_nodes`, `mouse_clusters`, `scroll_patterns`) is present and non-empty.
>    * (Optional) Compares the result against `sample_featurechunk.json` for strict schema validation.
>
> **Verification Criteria:**
>
> * The **README** example runs without errors and produces meaningful output.
> * **`pytest tests/test_fixtures_features.py`** passes, demonstrating end-to-end ingestion and feature extraction on the sample session.
> * The **sample session fixture** covers all major event types and the test confirms accurate feature detection.
> * Documentation clearly guides a new developer through installation, running examples, and understanding expected outputs.
