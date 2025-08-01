# 📘 Specification: Rule-Based Action Detection Engine

## 📌 Purpose

This module implements a **rule-based action detection system** that evaluates preprocessed `rrweb` session chunks to identify **user-intent-level actions** (e.g., "submit form", "search query"). It is used as a **first-pass labeling system** prior to LLM refinement and is designed for **extensibility**, **transparency**, and **feedback correction**.

---

## 📥 Inputs

### 1. **Session Chunk**

Each chunk is a Python object with the following structure:

```python
{
  "chunk_id": str,
  "start_time": int,
  "end_time": int,
  "events": List[Dict[str, Any]],  # rrweb events
  "metadata": {
    "num_events": int,
    "duration_ms": int,
    "session_id": str,
    "snapshot_before": Dict[str, Any]  # FullSnapshot-style DOM state
  },
  "features": {
    "user_interactions": List[UserInteraction],
    "dom_mutations": List[DomMutation],
    "event_delays": List[EventDelay],
    "ui_nodes": List[UINode],
    "mouse_clusters": List[MouseCluster],
    "scroll_patterns": List[ScrollPattern]
  }
}
```

All feature types are Python `@dataclass` models.

---

### 2. **Rule File**

Rules are stored in **YAML** format (JSON-compatible) in the `test_gen/data/rules` directory. Each rule file defines a single pattern like this:

```yaml
id: search_input_basic
description: "Detects a user typing into a search box"
match:
  event:
    action: input
  node:
    tag: input
    attributes:
      type: search
confidence: 0.8
variables:
  input_value: event.value
  placeholder: node.attributes.placeholder
  testid: node.attributes.data-testid
  child_text: node.query("div.result-label").text
action_id: search_query
```

---

## 📤 Outputs

A list of `DetectedAction` objects per chunk:

```python
@dataclass
class DetectedAction:
    action_id: str
    timestamp: int              # Taken from first matched event
    confidence: float           # From rule
    rule_id: str
    variables: Dict[str, Any]
    target_element: Optional[UINode]
    related_events: List[int]   # Indexes of matching events in chunk.events
```

These will be collected and saved into the `test_gen/data/action_mappings/` storage layer.

---

## 🧠 Matcher Behavior

The engine will:

1. Iterate over each `UserInteraction` in a chunk
2. For each rule:

   * Compare the rule's `match.event` block against the interaction
   * Find the matching `UINode` (by `target_id`)
   * Match against `match.node` (tag, attributes, etc.)
3. If matched:

   * Extract `variables` from the event/node context
   * Use CSS-style selectors (via helper functions) to extract from children
   * Generate a `DetectedAction`

**Timestamp** is the `UserInteraction.timestamp`.

---

## 🧰 Rule Syntax - Supported Fields (V1)

### `id`

Unique identifier of the rule.

### `description`

Freeform text for human readers.

### `match.event`

* `action`: click | input | scroll
* (future) could include event structure filters (e.g., `value == "foo"`)

### `match.node`

Matches corresponding `UINode` fields:

* `tag`: tag name like `"input"`, `"button"`
* `attributes`: map of required attribute-value pairs

### `confidence`

Hardcoded float, used as-is for now. Later may be computed dynamically.

### `variables`

Dictionary mapping variable names → value expressions. Valid sources:

* `event` fields (e.g., `event.value`)
* `node` fields (e.g., `node.text`, `node.attributes.foo`)
* `node.query(css_selector).text` (first matching descendant)
* Later: `node.parent.query(...)`, `node.sibling(...)`, etc.

### `action_id`

The final label emitted (e.g., `search_query`, `submit_login`).

---

## 🔧 Extensibility: VNext Capabilities

The schema and engine should be **future-compatible** with:

| Feature              | Example                             |
| -------------------- | ----------------------------------- |
| Multi-event match    | `input` followed by `click`         |
| Timing constraints   | Max delta between two events        |
| Logical ops          | ORs, negations in match blocks      |
| More DOM traversal   | Ancestors, siblings                 |
| Confidence inference | Based on node metadata or frequency |
| Rule chaining        | Composed rules for workflows        |

---

## 🧪 Example Test Cases

Create PyTest tests in `test_gen/rule_engine/tests` to validate:

1. A rule matches a `UserInteraction` + `UINode` pair
2. Variable extraction works (attributes, nested, child text)
3. Related events list includes correct indices
4. No false matches on incorrect elements
5. Missing fields handled gracefully

Mock chunks can be constructed directly in tests using dataclass models.

---

## 🧱 Implementation Plan

### 1. **Define Models**

* `DetectedAction`
* `Rule` (can deserialize YAML → Python dict → internal object)

### 2. **Rule Loader**

* Load `.yaml` files from `test_gen/data/rules/` into memory
* Validate required fields

### 3. **Matching Engine**

* For each chunk:

  * For each `UserInteraction`:

    * Find matching rule(s)
    * Match against `UINode`
    * Evaluate `match.event`, `match.node`
    * Extract variables
    * Construct `DetectedAction`

### 4. **Variable Resolver**

* Parse paths like `node.attributes.foo`
* Support `.query("div > span")` with a CSS selector engine

  * DOM snapshot may be used for this (from `snapshot_before`)
  * Optional for v1: assume `UINode` has children attached directly for lookup

### 5. **Emit Results**

* Return or save `List[DetectedAction]`
* Store in `test_gen/data/action_mappings/{chunk_id}.json` or return in-memory

---

## 📂 Directory Structure

```
test_gen/rule_engine/
  matcher.py              # Main engine
  rules_loader.py         # Loads and validates rules
  variable_resolver.py    # Handles variable expressions
  models.py               # DetectedAction and support dataclasses
  utils.py                # DOM helpers, selector matching

test_gen/data/rules/
  search_input.yaml
  submit_button.yaml

test_gen/rule_engine/tests/
  test_matcher.py
  test_variable_extraction.py
```

---

## 🧭 Goals and Design Principles

* Modular, testable design
* Clear separation of:

  * Rule definition
  * Rule matching
  * Variable extraction
* Deterministic and explainable (no magic until LLM step)
* JSON/YAML rules editable by non-engineers if needed
