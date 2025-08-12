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
- `extract_and_save_features(session_dir, output_dir)`: Extract features and save as JSON files

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

## Usage Examples

### Basic Feature Extraction

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

### Batch Feature Extraction and Saving

```python
from feature_extraction.pipeline import extract_and_save_features

# Extract features from all sessions and save as JSON files
stats = extract_and_save_features(
    session_dir="test_gen/data/output_sessions",
    output_dir="test_gen/data/output_features", 
    max_sessions=50,  # Process first 50 sessions
    verbose=True
)

print(f"Processed {stats['sessions_processed']} sessions")
print(f"Saved {stats['chunks_saved']} feature chunks")
print(f"Total features extracted: {sum(stats['total_features'].values()):,}")

# Check for errors
if stats['errors']:
    print(f"Encountered {len(stats['errors'])} errors")
    for error in stats['errors']:
        print(f"  {error}")
```

### Using JSON Output with Rule Engine

```python
import json
from rule_engine.match_chunk import process_chunk_file
from rule_engine.rules_loader import load_rules

# First, extract features and save to JSON
extract_and_save_features(
    session_dir="test_gen/data/output_sessions",
    output_dir="test_gen/data/output_features"
)

# Then use the saved features with the rule engine
rules = load_rules("test_gen/data/rules")
feature_files = Path("test_gen/data/output_features").glob("*.json")

for feature_file in feature_files:
    # Load pre-extracted features instead of processing raw chunks
    with open(feature_file, 'r') as f:
        feature_data = json.load(f)
    
    # Process with rule engine (features already extracted)
    actions_detected, rules_matched = process_chunk_file(
        feature_file, rules, "test_gen/data/action_mappings", verbose=True
    )
```

### Command Line Usage

```bash
# Extract features from all sessions
python -m feature_extraction test_gen/data/output_sessions

# Extract with custom output directory
python -m feature_extraction test_gen/data/output_sessions --output my_features

# Process limited sessions with verbose output
python -m feature_extraction test_gen/data/output_sessions --max-sessions 10 --verbose

# Show help and options
python -m feature_extraction --help
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

The `extract_features` function returns a `FeatureChunk` object, and `extract_and_save_features` saves each chunk as a JSON file with the following structure:

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
    "metadata": {...},
    "processing_metadata": {
        "feature_extraction_timestamp": "2025-01-01T12:00:00Z",
        "dom_initialized_from_snapshot": true,
        "dom_state_nodes_final": 156,
        "feature_extraction_version": "1.0"
    }
}
```

## Testing

Run the test suite to verify functionality:

```bash
# Run all feature extraction tests
pytest test_gen/feature_extraction/tests/

# Run specific test modules
pytest test_gen/feature_extraction/tests/test_pipeline_features.py
pytest test_gen/feature_extraction/tests/test_serialization.py
pytest test_gen/feature_extraction/tests/test_extract_and_save_features.py

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
