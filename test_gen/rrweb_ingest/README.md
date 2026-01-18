# rrweb Session Ingestion & Feature Extraction

This module processes raw rrweb session recordings and extracts rich feature sets for rule-based and LLM-driven behavior inference. It combines session ingestion, noise filtering, and feature extraction into a unified pipeline.

## What Changed

This module was refactored to consolidate functionality previously split across `rrweb_ingest` and `feature_extraction`:

- **Removed chunking/segmentation** - Sessions are now processed as complete units rather than being split into chunks
- **Integrated feature extraction** - DOM mutations and user interactions are extracted directly during ingestion
- **Simplified pipeline** - Eliminated separate `classifier`, `segmenter`, `normalizer` modules
- **Enriched metadata** - All interactions include full DOM node context (tag, text, attributes, path)
- **Moved shared code** - Common utilities moved to `rrweb_util` for reuse across modules

## Usage Examples

### Basic Feature Extraction

```python
from rrweb_ingest.pipeline import ingest_session

# Process a session file - features are extracted automatically
session = ingest_session("mysession", "path/to/session.json")

# Analyze extracted features
print(f"Session: {session.session_id}")
print(f"  User interactions: {len(session.user_interactions)}")

# Access interaction data with enriched DOM node metadata
for interaction in session.user_interactions:
    if interaction.action == "click":
        print(f"  Click at {interaction.timestamp}:")
        print(f"    Element: {interaction.target_node.tag}")
        print(f"    Text: {interaction.target_node.text}")
        print(f"    Path: {interaction.target_node.dom_path}")
```

### Batch Processing and Saving

```python
from rrweb_ingest.cli import process_sessions

# Process all sessions in a directory and save as JSON files
stats = process_sessions(
    session_dir="test_gen/data/output_sessions",
    output_dir="test_gen/data/output_features",
    max_sessions=50,  # Process first 50 sessions
)

print(f"Processed {stats['sessions_processed']} sessions")
print(f"Saved {stats['sessions_saved']} feature files")
print(f"Total interactions: {stats['total_interactions']}")
```

### Using with Rule Engine

```python
from pathlib import Path
from rule_engine.match_session import process_session_file
from rule_engine.rules_loader import load_rules

# First, extract features and save to JSON using the CLI
# python -m rrweb_ingest --session_dir data/sessions --output_dir data/features

# Load rules
rules = load_rules("test_gen/data/rules")

# Process each session file with the rule engine
session_files = Path("test_gen/data/output_features").glob("*.json")

for session_file in session_files:
    # Match rules against the session's features
    actions_count, rules_matched = process_session_file(
        session_files,
        rules,
        "test_gen/data/action_mappings",
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
