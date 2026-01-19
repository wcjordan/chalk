# rrweb Session Processing & Feature Extraction

## Overview

This repository provides a complete pipeline for processing raw `rrweb` session recordings (JSON files ~200KB–2MB) into structured feature data for test generation and behavior analysis.

The pipeline is responsible for:

1. **Loading & validating** rrweb JSON session files
2. **Filtering out noise** (cursor-only moves, micro-scrolls, trivial mutations)
3. **Extracting features** from user interactions and DOM mutations
4. **Enriching events** with DOM node metadata and semantic context
5. **Rule-based matching** to identify user actions and behaviors

## Architecture

The pipeline consists of three main modules:

### 1. `rrweb_ingest`
Processes raw rrweb session files and extracts structured features:
- **`ingest_session(session_id, filepath)`** - Main entry point that loads, filters, and extracts features from an rrweb session
- **`load_events(filepath)`** - Loads and validates rrweb JSON
- **`filter_events(events)`** - Removes noise events (micro-scrolls, mousemoves, etc.)
- **`extract_features(session)`** - Extracts user interactions and DOM mutations with enriched metadata

### 2. `rrweb_util`
Shared utilities for DOM state management and feature extraction:
- **`rrweb_util.dom_state`** - DOM state tracking, node metadata extraction
- **`rrweb_util.user_interaction`** - User interaction models and extractors
- **`rrweb_util.helpers`** - Common helper functions

### 3. `rule_engine`
Rule-based matching to identify user actions from extracted features:
- **`match_session(session_file, rules)`** - Matches rules against a session's features
- **`load_rules(rules_dir)`** - Loads rule definitions from YAML files

## Installation

Install dependencies using:

```bash
make init
```

Or manually install with:

```bash
pip install -r requirements.txt
```

## Usage Example

```python
from rrweb_ingest import ingest_session

# Process an rrweb session file and extract features
session = ingest_session("session1", "path/to/sample.json")

# Examine extracted features
print(f"Session: {session.session_id}")
print(f"  Duration: {session.duration_ms}ms")
print(f"  User Interactions: {len(session.features['interactions'])}")
print(f"  DOM Mutations: {len(session.features['dom_mutations'])}")

# Access individual interactions with enriched metadata
for interaction in session.features["interactions"]:
    print(f"{interaction.action} on {interaction.node.tag} at {interaction.timestamp}")
    print(f"  Text: {interaction.node.text_content}")
    print(f"  Path: {interaction.node.dom_path}")
```

## Session Schema

Each processed session follows this structure:

```python
@dataclass
class Session:
    session_id: str                    # Unique session identifier
    duration_ms: int                   # Total session duration
    events: List[dict]                 # Filtered rrweb events
    features: Dict[str, List]          # Extracted features:
                                       #   - interactions: List[UserInteraction]
                                       #   - dom_mutations: List[DomMutation]
    metadata: dict                     # Additional session metadata
```

## Command Line Usage

Extract features from all sessions in a directory:

```bash
# Process all sessions with default settings
python -m rrweb_ingest

# Specify custom input/output directories
python -m rrweb_ingest --session_dir data/sessions --output_dir data/features

# Process a limited number of sessions
python -m rrweb_ingest --max_sessions 10

# Show help
python -m rrweb_ingest --help
```

## Testing

Run all tests:

```bash
make test
```

Run tests for specific modules:

```bash
pytest rrweb_ingest/tests/
pytest rrweb_util/tests/
pytest rule_engine/tests/
```

Run with coverage report:

```bash
pytest --cov=. --cov-report=html
```

## Sample Data

Sample rrweb session files are included in `rrweb_ingest/tests/fixture_data/` for testing and demonstration purposes.
