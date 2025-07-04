# Session Chunking & Feature Extraction Module

This module transforms pre-processed rrweb chunks into rich feature sets, enabling rule-based and LLM-driven behavior inference. It extracts structured data about DOM mutations, user interactions, timing patterns, and UI metadata from rrweb session recordings.

## Overview

The feature extraction pipeline processes chunks of rrweb events and extracts:

- **DOM mutations**: Node additions, removals, attribute changes, and text modifications
- **User interactions**: Clicks, inputs, scrolls with target elements and coordinates
- **Timing delays**: Inter-event gaps and reaction times between interactions and mutations
- **UI metadata**: Semantic attributes, DOM paths, and accessibility information
- **Mouse clusters**: Grouped mouse movements based on temporal and spatial proximity
- **Scroll patterns**: Scroll events paired with subsequent DOM mutations

## Key Functions

- `init_dom_state(full_snapshot_event)`: Initialize virtual DOM from FullSnapshot event
- `apply_mutations(node_by_id, mutation_events)`: Update virtual DOM with incremental changes
- `extract_dom_mutations(events)`: Extract structured DOM change records
- `extract_user_interactions(events)`: Extract click, input, and scroll interactions
- `compute_inter_event_delays(events)`: Compute timing between consecutive events
- `compute_reaction_delays(events)`: Detect interaction→mutation reaction patterns
- `resolve_node_metadata(node_id, node_by_id)`: Get semantic UI context for nodes
- `cluster_mouse_trajectories(events)`: Group related mouse movements
- `detect_scroll_patterns(events)`: Find scroll events that trigger mutations
- `extract_features(chunk, dom_state)`: Main pipeline function orchestrating all extractors

## Installation

This module is part of the `test_gen` package and requires the `rrweb_ingest` module for preprocessing.

### Dependencies

- Python 3.8+
- `rrweb_ingest` module (for session preprocessing)
- Standard library modules: `dataclasses`, `typing`, `logging`, `math`

### Setup

```bash
# Install from the project root
pip install -e .

# Or add the test_gen directory to your Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/test_gen"
```

## Usage Example

```python
from rrweb_ingest.pipeline import ingest_session
from feature_extraction.dom_state import init_dom_state
from feature_extraction.pipeline import extract_features

# Process a session file
chunks = ingest_session("mysession", "path/to/session.json")

for chunk in chunks:
    # Initialize DOM state from FullSnapshot if available
    if chunk.metadata.get("snapshot_before"):
        dom = init_dom_state(chunk.metadata["snapshot_before"])
    else:
        dom = {}  # Start with empty DOM state
    
    # Extract features from the chunk
    feature_chunk = extract_features(chunk, dom)
    
    # Analyze extracted features
    print(f"{feature_chunk.chunk_id}:")
    print(f"  DOM mutations: {len(feature_chunk.features['dom_mutations'])}")
    print(f"  User interactions: {len(feature_chunk.features['interactions'])}")
    print(f"  Mouse clusters: {len(feature_chunk.features['mouse_clusters'])}")
    print(f"  Scroll patterns: {len(feature_chunk.features['scroll_patterns'])}")
    
    # Access specific feature data
    for interaction in feature_chunk.features["interactions"]:
        if interaction.action == "click":
            print(f"  Click on node {interaction.target_id} at {interaction.timestamp}")
    
    for mutation in feature_chunk.features["dom_mutations"]:
        if mutation.mutation_type == "add":
            print(f"  Added node {mutation.target_id}: {mutation.details['tag']}")
```

## Configuration

The module uses configurable thresholds that can be customized:

```python
from feature_extraction import config

# Default clustering thresholds
config.DEFAULT_TIME_DELTA_MS = 100    # Mouse clustering time threshold
config.DEFAULT_DIST_DELTA_PX = 50     # Mouse clustering distance threshold

# Default reaction time windows
config.DEFAULT_SCROLL_REACTION_MS = 2000   # Scroll→mutation window
config.DEFAULT_MAX_REACTION_MS = 10000     # Interaction→mutation window

# Custom DOM path formatting
def custom_path_formatter(path_parts):
    return " >> ".join(path_parts)

# Use custom formatter in metadata resolution
from feature_extraction.metadata import resolve_node_metadata
metadata = resolve_node_metadata(node_id, node_by_id, custom_path_formatter)
```

## Output Structure

The `extract_features` function returns a `FeatureChunk` with the following structure:

```python
{
    "chunk_id": "session_abc-chunk001",
    "start_time": 1234567890,
    "end_time": 1234567900,
    "events": [...],  # Original rrweb events
    "features": {
        "dom_mutations": [
            {
                "mutation_type": "attribute",
                "target_id": 42,
                "details": {"attributes": {"class": "active"}},
                "timestamp": 1234567895
            }
        ],
        "interactions": [
            {
                "action": "click",
                "target_id": 42,
                "value": {"x": 100, "y": 200},
                "timestamp": 1234567892
            }
        ],
        "inter_event_delays": [...],
        "reaction_delays": [...],
        "ui_nodes": {
            42: {
                "tag": "button",
                "aria_label": "Submit Form",
                "data_testid": "submit-btn",
                "role": "button",
                "text": "Submit",
                "dom_path": "html > body > form > button#submit"
            }
        },
        "mouse_clusters": [...],
        "scroll_patterns": [...]
    },
    "metadata": {...}
}
```

## Testing

Run the test suite to verify functionality:

```bash
# Run all feature extraction tests
pytest test_gen/feature_extraction/tests/

# Run specific test modules
pytest test_gen/feature_extraction/tests/test_pipeline_features.py
pytest test_gen/feature_extraction/tests/test_fixtures_features.py

# Run with verbose output
pytest -v test_gen/feature_extraction/tests/
```

## Performance Considerations

- **DOM State Management**: The virtual DOM is maintained in memory and updated incrementally. For large sessions, consider processing chunks in batches.
- **Mouse Clustering**: Dense mouse movement streams may produce many small clusters. Adjust `DEFAULT_TIME_DELTA_MS` and `DEFAULT_DIST_DELTA_PX` for your use case.
- **Memory Usage**: Feature extraction preserves all original event data plus extracted features. For memory-constrained environments, consider processing chunks individually.

## Troubleshooting

### Common Issues

**Missing FullSnapshot Events**: If chunks don't contain FullSnapshot events, DOM metadata resolution may be limited. Ensure session preprocessing includes snapshot events.

**Empty Feature Lists**: Check that input events contain the expected rrweb event types and sources. Use verbose logging to debug event filtering.

**Incorrect DOM Paths**: Verify that the virtual DOM state is properly initialized and maintained through mutation application.

### Debugging

Enable debug logging to trace feature extraction:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Feature extraction will log warnings for missing nodes
feature_chunk = extract_features(chunk, dom_state)
```

## Contributing

When adding new extractors or modifying existing ones:

1. Add comprehensive unit tests in `tests/`
2. Update configuration constants in `config.py`
3. Document new features in this README
4. Ensure backward compatibility with existing `FeatureChunk` schema

## License

This module is part of the larger test generation project. See the project root for license information.
