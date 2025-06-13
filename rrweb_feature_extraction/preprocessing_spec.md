**Input Ingestion & Preprocessing Specification**

---

## 1. Overview

The **Input Ingestion** module is responsible for taking raw `rrweb` session recordings (JSON blobs \~200 KB–2 MB) and transforming them into **clean, structured “chunks”** ready for downstream feature extraction and behavior analysis.

**Key Responsibilities**

1. **Load & validate** the JSON session.
2. **Sort & classify** events into snapshots, interactions, and other categories.
3. **Segment** the interaction stream into meaningful chunks.
4. **Filter out noise** (cursor-only moves, micro‐scrolls, idle gaps).
5. **Emit** a normalized chunk object for each segment.

---

## 2. Module Interfaces

```python
def ingest_session(filepath: str) -> List[Chunk]:
    """
    Load an rrweb session file, preprocess, and return a list of cleaned chunks.
    Raises:
      - JSONDecodeError: invalid JSON
      - FileNotFoundError: missing file
    """
```

**`Chunk`** (output type) should conform to:

```python
@dataclass
class Chunk:
    chunk_id: str
    start_time: int         # timestamp of first event
    end_time: int           # timestamp of last event
    events: List[dict]      # raw events after filtering
    metadata: dict          # e.g. snapshot_before, event_counts
```

---

## 3. JSON Parsing & Validation

1. **Open file / blob**
2. **Load JSON** into Python list
3. **Validate** that each item is a dict with at least:

   * `type` (int)
   * `timestamp` (int)
   * `data` (dict)

```python
import json

def load_events(filepath: str) -> List[dict]:
    with open(filepath) as f:
        raw = json.load(f)
    if not isinstance(raw, list):
        raise ValueError("Session must be JSON array")
    # Basic validation
    for e in raw:
        if not all(k in e for k in ("type", "timestamp", "data")):
            raise ValueError(f"Invalid event shape: {e}")
    # Sort by timestamp ascending
    return sorted(raw, key=lambda e: e["timestamp"])
```

---

## 4. Event Classification

After sorting, classify each event into three buckets:

| Bucket           | Criteria                                               | Purpose                     |
| ---------------- | ------------------------------------------------------ | --------------------------- |
| **Snapshots**    | `type == 2`  (FullSnapshot)                            | Mark chunk boundaries       |
| **Interactions** | `type == 3`  (IncrementalSnapshot)                     | Candidate for chunks        |
| **Others**       | `type in {0,1,4,5,6,...}` (`Meta`, `Custom`, `Plugin`) | Logged/ignored or later use |

```python
def classify_events(events):
    snapshots, interactions, others = [], [], []
    for e in events:
        if e["type"] == 2:
            snapshots.append(e)
        elif e["type"] == 3:
            interactions.append(e)
        else:
            others.append(e)
    return snapshots, interactions, others
```

---

## 5. Chunking Heuristics

Group `interactions` into **“interaction windows”**, using configurable thresholds:

* **New chunk triggers**:

  * Encounter a **FullSnapshot** (from `snapshots` list)
  * **Gap in time** > `max_gap_ms` (default 10 000 ms)
* **Chunk caps**:

  * Maximum events per chunk (e.g., 1000)
  * Maximum duration per chunk (e.g., 30 s)

```python
from datetime import timedelta

MAX_GAP_MS = 10_000
MAX_EVENTS = 1000

def segment_into_chunks(interactions, snapshots):
    chunks, current = [], []
    last_ts = None
    snap_iter = iter(snapshots)
    next_snap = next(snap_iter, None)

    for e in interactions:
        ts = e["timestamp"]
        # FullSnapshot boundary
        if next_snap and ts >= next_snap["timestamp"]:
            if current:
                chunks.append(current); current = []
            next_snap = next(snap_iter, None)
            last_ts = None

        # Time gap boundary
        if last_ts and (ts - last_ts) > MAX_GAP_MS:
            chunks.append(current); current = []

        current.append(e)
        last_ts = ts

        # Size cap
        if len(current) >= MAX_EVENTS:
            chunks.append(current); current = []; last_ts = None

    if current:
        chunks.append(current)
    return chunks
```

---

## 6. Noise-Filtering Heuristics

Inside each chunk, drop or down-rank events that carry little signal:

1. **Mousemove only** (`source == 1`)
2. **Micro-scrolls** (`source == 3` with `|delta| < 20px`)
3. **Minor DOM mutations** (`source == 0` with trivial attribute changes)
4. **Idle typing** (input events with no submit or blur within chunk)
5. **Exact duplicates** (same type, target, timestamp)

```python
def is_low_signal(e):
    if e["type"] != 3:
        return False
    d = e["data"]
    s = d.get("source")
    if s == 1:
        return True
    if s == 3 and abs(d.get("y",0)) < 20:
        return True
    if s == 0 and is_trivial_mutation(d):
        return True
    return False

def clean_chunk(chunk_events):
    seen = set()
    cleaned = []
    for e in chunk_events:
        key = (e["type"], e["data"].get("source"), e["timestamp"])
        if key in seen:
            continue
        seen.add(key)
        if not is_low_signal(e):
            cleaned.append(e)
    return cleaned
```

---

## 7. Normalized Chunk Schema

Each finalized chunk must be represented as:

```json
{
  "chunk_id": "<session>-<seq#>",
  "start_time": <int>,
  "end_time": <int>,
  "events": [ /* cleaned events */ ],
  "metadata": {
    "num_events": <int>,
    "duration_ms": <int>,
    "snapshot_before": { /* optional full snapshot */ }
  }
}
```

* **`chunk_id`**: `<sessionName>-chunk<zeroPaddedIndex>`
* **`snapshot_before`**: the most recent FullSnapshot event, if available.

---

## 8. Configuration & Extensibility

* **Parameters** (make configurable):

  * `max_gap_ms`, `max_events`, `micro_scroll_threshold`
* **Pluggable filters**: support custom `is_low_signal` rules
* **Logging & metrics**: count dropped vs. kept events for monitoring
* **Error handling**: robust to missing fields or out-of-order data

---

## 9. Onboarding Checklist

1. **Run sample ingestion** on provided session JSON
2. **Inspect output chunks** for expected boundaries
3. **Adjust thresholds** to match real-world session patterns
4. **Write unit tests** for:

   * JSON loading & validation
   * Event classification
   * Chunk segmentation
   * Noise filtering
5. **Document** any deviations when integrating into the full pipeline
