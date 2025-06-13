**Session Chunking & Feature Extraction Specification**

---

## 1. Purpose

Transform pre-processed `rrweb` chunks into rich feature sets, enabling rule-based and LLM-driven behavior inference. Each chunk (a time-bounded list of filtered events) will be analyzed to extract:

* **DOM mutations** (adds/removes, attribute/text changes)
* **User interactions** (click, input, focus, scroll)
* **Timestamps & delays** (inter-event gaps, reaction times)
* **UI hierarchy & metadata** (tag names, `data-testid`, `aria-label`, `role`, DOM path)
* **Mouse trajectory clusters** (hover zones, intent paths)
* **Scroll/viewport transitions** (attention zones, load patterns)

---

## 2. Inputs & Outputs

* **Input:**
  A list of `Chunk` objects from the preprocessing stage, each:

  ```python
  @dataclass
  class Chunk:
      chunk_id: str
      start_time: int
      end_time: int
      events: List[dict]      # cleaned, sorted rrweb events
      metadata: dict
  ```
* **Output:**
  Extend each `Chunk` into a `FeatureChunk` containing:

  ```python
  @dataclass
  class FeatureChunk:
      chunk_id: str
      start_time: int
      end_time: int
      events: List[dict]
      features: {
          "dom_mutations": List[DomMutation],
          "interactions": List[UserInteraction],
          "delays": List[EventDelay],
          "ui_nodes": Dict[node_id, UINode],
          "mouse_clusters": List[MouseCluster],
          "scroll_patterns": List[ScrollPattern]
      }
      metadata: dict
  ```

---

## 3. Build & Maintain Virtual DOM State

1. **On FullSnapshot:** initialize `node_by_id` map:

   ```python
   node_by_id = {
     event.data.node.id: UINode(
       id, tagName, attributes, textContent, parentId
     )
   }
   ```
2. **On Mutation (source 0):** update `node_by_id` for:

   * `adds`: insert new `UINode`
   * `removes`: delete by `id`
   * `attributes` & `texts`: modify existing node

> **UINode**:
>
> ```python
> @dataclass
> class UINode:
>     id: int
>     tag: str
>     attributes: Dict[str,str]
>     text: str
>     parent: Optional[int]
> ```

---

## 4. DOM Mutation Extraction

* **Trigger:** `event.type == 3` and `event.data.source == 0`
* **For each mutation event:**

  * **Attributes changed:** record `{ id, attributes, timestamp }`
  * **Text changes:** record `{ id, text, timestamp }`
  * **Node adds/removes:** record `{ parentId/id, nodeInfo, timestamp }`

```python
def extract_dom_mutations(events):
    mutations = []
    for e in events:
        if e["type"]==3 and e["data"]["source"]==0:
            # collect adds, removes, attributes, texts
            ...
    return mutations
```

---

## 5. User Interaction Extraction

* **Click & Mouse Interaction** (`source == 2`): `{ action:"click", id, x,y, timestamp }`
* **Input Events** (`source == 5`): `{ action:"input", id, value/checked, timestamp }`
* **Scroll Events** (`source == 3`): `{ action:"scroll", id, x,y, timestamp }`

```python
def extract_user_interactions(events):
    interactions = []
    for e in events:
        s = e["data"]["source"]
        if   s==2: interactions.append({...})
        elif s==5: interactions.append({...})
        elif s==3: interactions.append({...})
    return interactions
```

---

## 6. Timestamp & Delay Features

* **Inter-event delay:** compute `ts[i] - ts[i-1]` for every event
* **Reaction time:** for each user interaction, find delay to next DOM mutation
* **Idle gaps:** any delay > `idle_threshold` (e.g., 10 s) flagged as boundary

```python
def compute_delays(events, idle_threshold=10000):
    delays=[]
    last_ts=None
    for e in events:
        ts=e["timestamp"]
        if last_ts is not None:
            delays.append({"from":last_ts,"to":ts,"delta":ts-last_ts})
        last_ts=ts
    return delays
```

---

## 7. UI Hierarchy & Metadata Resolution

* **For each interaction or mutation**, resolve:

  * `node = node_by_id[target_id]`
  * Extract `tag`, `attributes["data-testid"]`, `aria-label`, `role`, `text`
  * **Compute DOM path** by traversing `.parent` up to root

```python
def resolve_node_metadata(node_id, node_by_id):
    node=node_by_id[node_id]
    path=[]
    while node:
        path.insert(0, f"{node.tag}[id={node.id}]")
        node=node_by_id.get(node.parent)
    return {"tag":..., "aria_label":..., "path":" > ".join(path)}
```

---

## 8. Mouse Trajectory Clustering

* **Cluster criteria:**

  * `time_delta < 100 ms`
  * `spatial_delta < 50 px`
* **Output:** list of clusters, each with:

  * `start_ts`, `end_ts`, `path: List[{x,y,ts}]`, `length`, `duration`

```python
def cluster_mouse_trajectories(events):
    clusters=[]; current=[]; last=None
    for e in events:
        if e["data"]["source"]!=1: continue
        ...
    return clusters
```

---

## 9. Scroll & Viewport Transition Patterns

* **Basic extraction:** all `source == 3` scroll events
* **Scroll→Mutation detection:** for each scroll, if next mutation occurs within 2 s, record `{ scroll_event, mutation_event, delay }`

```python
def detect_scroll_patterns(events, max_delay=2000):
    patterns=[]; last_scroll_ts=None
    for e in events:
        if e["data"]["source"]==3: last_scroll_ts=e
        elif e["data"]["source"]==0 and last_scroll_ts:
            delta=e["timestamp"]-last_scroll_ts["timestamp"]
            if delta<max_delay:
                patterns.append({...})
                last_scroll_ts=None
    return patterns
```

---

## 10. Integration & Output

1. **For each `Chunk`:**

   * Build/maintain `node_by_id` state
   * Call feature extractors in order:

     * `extract_dom_mutations`
     * `extract_user_interactions`
     * `compute_delays`
     * `resolve_node_metadata` (on all extracted events)
     * `cluster_mouse_trajectories`
     * `detect_scroll_patterns`
2. **Assemble** into `FeatureChunk` and pass to downstream rule/LLM engine.

---

## 11. Risks & Edge Cases

* **Node ID churn:** ensure removed nodes aren’t reused erroneously
* **Partial inputs:** input events with no accompanying blur/submit
* **Custom widgets:** non-standard attributes may require fallback logic
* **High-frequency mousemove:** enforce max cluster size or ignore ultra-dense streams
* **Time discontinuities:** account for clock skew or logging lags

---

## 12. Next Steps

* **Unit tests** for each extractor using synthetic `rrweb` snippets
* **Benchmark** on real sessions to tune thresholds (time/distance)
* **Document** JSON schemas for `FeatureChunk` and sub-structures
* **Onboard** by running end-to-end on a sample session and inspecting results
