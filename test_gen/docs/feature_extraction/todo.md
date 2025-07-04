# rrweb Feature Extraction - Session Chunking & Feature Extraction Todo List

## Step 1: Define Data Models & Test Harness

### Tasks:
- [x] Create `test_gen/feature_extraction/` package directory structure
- [x] Add `__init__.py` to make it a proper Python package
- [x] Create `test_gen/feature_extraction/models.py` with data classes:
  - [x] `DomMutation` - captures mutation type, target node ID, details, timestamp
  - [x] `UserInteraction` - captures action type, target node ID, value/coordinates, timestamp
  - [x] `EventDelay` - captures event IDs/timestamps and delta between them
  - [x] `UINode` - captures node ID, tag, attributes dict, text content, parent ID
  - [x] `MouseCluster` - captures cluster timestamps, point list, duration/length
  - [x] `ScrollPattern` - captures scroll event, paired mutation event, delay
  - [x] `FeatureChunk` - aggregates chunk data with features dict
- [x] Add type hints and module-level docstrings for all classes
- [x] Create `test_gen/feature_extraction/tests/` directory
- [x] Create `test_gen/feature_extraction/tests/test_models.py`:
  - [x] Import and construct instances of each class with dummy values
  - [x] Assert attributes are stored correctly
  - [x] Verify `FeatureChunk` can be instantiated with empty feature lists
- [x] Verify pytest runs successfully on model tests
- [x] Ensure no existing preprocessing tests are broken

## Step 2: Virtual DOM State Initialization

### Tasks:
- [x] Create `test_gen/feature_extraction/dom_state.py`
- [x] Implement `init_dom_state(full_snapshot_event: dict) -> Dict[int, UINode]`:
  - [x] Handle rrweb events with `type == 2` and `data.node`
  - [x] Traverse snapshot payload to build node tree
  - [x] Extract node ID, tag, attributes, text content, parent ID
  - [x] Return dict mapping node IDs to UINode instances
- [x] Add module-level docstring explaining virtual DOM initialization
- [x] Create `test_gen/feature_extraction/tests/test_dom_state.py`:
  - [x] Test with synthetic FullSnapshot event and simple DOM tree
  - [x] Verify correct node_by_id dict with proper keys and UINode fields
  - [x] Test root node has parent = None
  - [x] Test node attributes and textContent captured exactly
- [x] Verify pytest passes without errors
- [x] Code review confirms correct snapshot traversal and UINode population

## Step 3: Virtual DOM Mutation Updates

### Tasks:
- [x] Add `apply_mutations(node_by_id: Dict[int, UINode], mutation_events: List[dict]) -> None` to `dom_state.py`:
  - [x] Handle "adds" - create new UINode and insert into node_by_id
  - [x] Handle "removes" - delete node ID from node_by_id
  - [x] Handle "attributes" - update UINode.attributes dict
  - [x] Handle "texts" - update UINode.text field
  - [x] Ignore mutations with non-existent node IDs
- [x] Update module docstring to explain incremental DOM maintenance
- [x] Add tests to `test_dom_state.py` for `apply_mutations`:
  - [x] Test adding new child node
  - [x] Test removing existing node
  - [x] Test changing node attributes
  - [x] Test changing node text
  - [x] Test invalid mutations are safely ignored
- [x] Verify pytest passes including new mutation tests
- [x] Code review confirms correct node_by_id mutations for all types
- [x] No regressions in existing virtual DOM initialization tests

## Step 4: DOM Mutation Extraction

### Tasks:
- [x] Create `test_gen/feature_extraction/extractors.py` (or `dom_extractor.py`)
- [x] Implement `extract_dom_mutations(events: List[dict]) -> List[DomMutation]`:
  - [x] Filter events where `type == 3` and `data.source == 0`
  - [x] Extract attribute changes from `data.attributes`
  - [x] Extract text changes from `data.texts`
  - [x] Extract node additions from `data.adds`
  - [x] Extract node removals from `data.removes`
  - [x] Preserve original event order in returned list
- [x] Add docstring explaining function purpose, inputs, outputs
- [x] Create `test_gen/feature_extraction/tests/test_dom_extractor.py`:
  - [x] Test single mutation event with multiple attribute changes
  - [x] Test text-change events produce correct DomMutation
  - [x] Test add/remove events produce appropriate DomMutation entries
  - [x] Test mixed sequence filters only mutation events
  - [x] Test empty mutation data doesn't produce spurious entries
- [x] Verify pytest passes without failures
- [x] Extracted DomMutation objects match expected properties
- [x] No regressions in existing feature-extraction tests

## Step 5: User Interaction Extraction

### Tasks:
- [x] Add `extract_user_interactions(events: List[dict]) -> List[UserInteraction]` to `extractors.py`:
  - [x] Filter events where `type == 3`
  - [x] Handle `data.source == 2` as "click" interactions (target_id, x, y, timestamp)
  - [x] Handle `data.source == 5` as "input" interactions (target_id, value/checked, timestamp)
  - [x] Handle `data.source == 3` as "scroll" interactions (target_id, x, y, timestamp)
  - [x] Ignore other sources
  - [x] Preserve event order in returned list
- [x] Add docstring explaining source value mappings to interaction types
- [x] Create `test_gen/feature_extraction/tests/test_interactions_extractor.py`:
  - [x] Test mixed incremental snapshot events yield only click/input/scroll
  - [x] Test click events produce correct type with coordinates and target
  - [x] Test input events capture value/checked fields
  - [x] Test scroll events produce scroll interactions with x/y data
  - [x] Test non-interaction sources are ignored
- [x] Verify pytest passes without failures
- [x] UserInteraction objects have correct types and fields per spec
- [x] No regressions in existing tests

## Step 6: Delay Computation

### Tasks:
- [x] Add delay computation functions to `extractors.py` (or create `delay_extractor.py`):
- [x] Implement `compute_inter_event_delays(events: List[dict]) -> List[EventDelay]`:
  - [x] Process events sorted by timestamp
  - [x] Create EventDelay for each consecutive pair with from_ts, to_ts, delta_ms
- [x] Implement `compute_reaction_delays(events, interaction_source=2, mutation_source=0, max_reaction_ms=10000) -> List[EventDelay]`:
  - [x] Find interaction events with specified source
  - [x] Find next mutation event within max_reaction_ms window
  - [x] Create EventDelay capturing interaction→mutation timing
- [x] Add docstrings explaining inputs, outputs, parameter meanings
- [x] Create `test_gen/feature_extraction/tests/test_delay_extractor.py`:
  - [x] Test inter-event delays with known timestamps produce correct deltas
  - [x] Test reaction delays within window are captured
  - [x] Test no reaction delays outside max window
  - [x] Test multiple interactions produce multiple reaction delays
  - [x] Test non-interaction sources are ignored
- [x] Verify pytest passes all cases
- [x] Functions return correct EventDelay counts and timing
- [x] No regressions in existing tests

## Step 7: UI Metadata Resolution

### Tasks:
- [ ] Create `test_gen/feature_extraction/metadata.py`
- [ ] Implement `resolve_node_metadata(node_id: int, node_by_id: Dict[int, UINode]) -> Dict[str, Any]`:
  - [ ] Look up UINode by node_id
  - [ ] Extract tag, aria_label, data_testid, role from attributes
  - [ ] Extract text content
  - [ ] Compute dom_path by walking parent pointers to root
  - [ ] Return dict with tag, aria_label, data_testid, role, text, dom_path keys
- [ ] Add module-level docstring explaining human-readable UI context
- [ ] Create `test_gen/feature_extraction/tests/test_metadata.py`:
  - [ ] Test simple node_by_id map produces correct dom_path
  - [ ] Test nodes with/without aria_label, data_testid, role attributes
  - [ ] Test text content captured accurately
  - [ ] Test nonexistent node_id raises KeyError or clear error
- [ ] Verify pytest passes all tests
- [ ] Returned metadata dict has specified keys with correct values
- [ ] No regressions in existing tests

## Step 8: Mouse Trajectory Clustering

### Tasks:
- [ ] Create `test_gen/feature_extraction/clustering.py`
- [ ] Implement `cluster_mouse_trajectories(events: List[dict], time_delta_ms=100, dist_delta_px=50) -> List[MouseCluster]`:
  - [ ] Filter events where `type == 3` and `data.source == 1`
  - [ ] Compute time difference and Euclidean distance to previous mousemove
  - [ ] Start new cluster when either threshold exceeded
  - [ ] Build MouseCluster with start_ts, end_ts, point list, duration_ms, point_count
  - [ ] Return clusters in chronological order
- [ ] Add module-level docstring explaining clustering parameters
- [ ] Create `test_gen/feature_extraction/tests/test_clustering.py`:
  - [ ] Test consecutive events within thresholds form single cluster
  - [ ] Test events separated by time_delta_ms split into two clusters
  - [ ] Test events with spatial separation > dist_delta_px split clusters
  - [ ] Test mix of temporal/spatial splits produces correct cluster count
  - [ ] Test no mousemove events returns empty list
- [ ] Verify pytest passes all cases
- [ ] Clusters match expected boundaries and metrics
- [ ] No regressions in existing tests

## Step 9: Scroll-Pattern Detection

### Tasks:
- [ ] Create `test_gen/feature_extraction/scroll_patterns.py`
- [ ] Implement `detect_scroll_patterns(events: List[dict], max_reaction_ms=2000) -> List[ScrollPattern]`:
  - [ ] Filter scroll events (`type == 3`, `data.source == 3`)
  - [ ] For each scroll, find next mutation event (`type == 3`, `data.source == 0`)
  - [ ] Check mutation timestamp within max_reaction_ms of scroll
  - [ ] Create ScrollPattern with scroll event, mutation event, delay
  - [ ] Reset lookahead after match (each scroll matches ≤1 mutation)
  - [ ] Return ScrollPattern records in chronological order
- [ ] Add module-level docstring explaining scroll→mutation pattern detection
- [ ] Create `test_gen/feature_extraction/tests/test_scroll_patterns.py`:
  - [ ] Test scroll followed by mutation within window yields ScrollPattern
  - [ ] Test scroll with no subsequent/distant mutation yields no pattern
  - [ ] Test multiple scrolls match to nearest valid mutations
  - [ ] Test out-of-order or non-scroll/mutation sources ignored
  - [ ] Test empty event list returns empty list
- [ ] Verify pytest passes all scenarios
- [ ] ScrollPattern objects capture scroll event, mutation event, delay correctly
- [ ] No regressions in existing tests

## Step 10: Assemble & Integrate Extractors

### Tasks:
- [ ] Create `test_gen/feature_extraction/pipeline.py`
- [ ] Implement `extract_features(chunk: Chunk, dom_state: Dict[int, UINode]) -> FeatureChunk`:
  - [ ] Apply mutations from chunk to update dom_state
  - [ ] Extract DomMutation entries via extract_dom_mutations
  - [ ] Extract UserInteraction entries via extract_user_interactions
  - [ ] Extract EventDelay entries via compute_inter_event_delays and compute_reaction_delays
  - [ ] Resolve UI metadata for each mutation and interaction
  - [ ] Extract MouseCluster entries via cluster_mouse_trajectories
  - [ ] Extract ScrollPattern entries via detect_scroll_patterns
  - [ ] Assemble results into FeatureChunk with chunk_id, times, events
- [ ] Add module-level docstring describing extraction pipeline
- [ ] Create `test_gen/feature_extraction/tests/test_pipeline_features.py`:
  - [ ] Test sample Chunk with FullSnapshot and interaction/mutation events
  - [ ] Assert FeatureChunk has non-empty lists for each feature category
  - [ ] Verify timestamps and IDs align with input events
  - [ ] Test calling extract_features twice yields identical results
- [ ] Verify pytest passes
- [ ] FeatureChunk contains all expected feature lists populated correctly
- [ ] No regressions in existing tests

## Step 11: Configuration & Extensibility

### Tasks:
- [ ] Create `test_gen/feature_extraction/config.py` with default parameters:
  - [ ] DEFAULT_TIME_DELTA_MS = 100
  - [ ] DEFAULT_DIST_DELTA_PX = 50
  - [ ] DEFAULT_SCROLL_REACTION_MS = 2000
  - [ ] DEFAULT_MAX_REACTION_MS = 10000
- [ ] Refactor extractor functions to import and use config defaults:
  - [ ] Update dom_state.py functions
  - [ ] Update extractors.py functions
  - [ ] Update clustering.py functions
  - [ ] Update scroll_patterns.py functions
  - [ ] Update pipeline.py functions
- [ ] Add function signature overrides that default to config values
- [ ] Add extensibility hooks:
  - [ ] Custom DOM path formatting function in metadata resolver
  - [ ] Pluggable distance/time comparator in clustering
- [ ] Update docstrings to document config constants and override methods
- [ ] Create `test_gen/feature_extraction/tests/test_config_features.py`:
  - [ ] Test config module exports correct default values
  - [ ] Test custom parameter overrides change behavior
  - [ ] Test custom DOM path formatter is invoked and output appears
- [ ] Verify all existing tests still pass
- [ ] New config tests pass demonstrating defaults and overrides
- [ ] Code review confirms no hard-coded thresholds remain

## Step 12: Documentation & Sample Data

### Tasks:
- [ ] Create/update `test_gen/feature_extraction/README.md`:
  - [ ] Concise overview of module purpose and key functions
  - [ ] Installation instructions and dependencies
  - [ ] Usage example showing integration with rrweb_ingest pipeline
  - [ ] Example output showing feature extraction results
- [ ] Create sample data under `test_gen/feature_extraction/tests/fixtures/`:
  - [ ] `sample_session.json` - small rrweb session (~15-25 events)
  - [ ] Include FullSnapshot, IncrementalSnapshots with clicks, inputs, mutations, mousemoves, scrolls
  - [ ] `sample_featurechunk.json` (optional) - expected output structure
- [ ] Create `test_gen/feature_extraction/tests/test_fixtures_features.py`:
  - [ ] Load sample_session.json via ingest_session
  - [ ] Initialize DOM with init_dom_state from first chunk
  - [ ] Call extract_features on first chunk
  - [ ] Assert each feature list is present and non-empty
  - [ ] Optional: compare result against sample_featurechunk.json
- [ ] Verify README example runs without errors
- [ ] Verify pytest passes on fixtures test
- [ ] Sample session covers all major event types
- [ ] Documentation guides new developers through installation and usage

## Step 13: Integration Testing & Validation

### Tasks:
- [ ] Create end-to-end integration tests:
  - [ ] Test complete pipeline from raw rrweb JSON to FeatureChunk
  - [ ] Validate feature extraction accuracy on real session data
  - [ ] Test error handling for malformed or incomplete sessions
- [ ] Performance testing:
  - [ ] Benchmark feature extraction on various session sizes
  - [ ] Identify bottlenecks in DOM state management or clustering
  - [ ] Optimize critical paths if needed
- [ ] Edge case testing:
  - [ ] Sessions with no FullSnapshot events
  - [ ] Sessions with only mousemove events
  - [ ] Sessions with rapid DOM mutations
  - [ ] Sessions with custom widgets or non-standard attributes
- [ ] Validation against specification:
  - [ ] Verify all feature types from spec are extracted
  - [ ] Confirm output schema matches FeatureChunk definition
  - [ ] Test configurability of all documented thresholds

## Step 14: Final Documentation & Cleanup

### Tasks:
- [ ] Complete API documentation with docstrings for all public functions
- [ ] Add troubleshooting section for common issues
- [ ] Include performance benchmarks and expected processing times
- [ ] Document supported rrweb versions and formats
- [ ] Code review for consistency, error handling, and best practices
- [ ] Final integration test with preprocessing pipeline
- [ ] Update main project README to include feature extraction module
- [ ] Tag release version and update changelog
