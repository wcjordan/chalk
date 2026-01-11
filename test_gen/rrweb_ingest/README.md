# Session Chunking & Feature Extraction Module

This module ingests rrweb sessions into rich feature sets, enabling rule-based and LLM-driven behavior inference. It extracts structured data about user interactions and the DOM nodes they interact with from rrweb session recordings.

## Usage Examples

TODO (jordan) These are out of date, please update (the Command Line Usage part should be up to date)

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
python -m rrweb_ingest

# Extract with custom output directory
python -m rrweb_ingest --output_dir my_features

# Process limited sessions
python -m rrweb_ingest --max_sessions 10

# Show help and options
python -m rrweb_ingest --help
```
