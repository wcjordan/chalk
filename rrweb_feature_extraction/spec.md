# Requirements Document: rrweb Session Behavior Extraction

## 📌 Objective

To design a system that processes `rrweb` session recordings (\~200KB–2MB) and extracts **high-level user behaviors** (e.g., "clicked Submit", "scrolled to checkout section", "hovered over Settings but didn’t click") using a combination of deterministic rules and LLM interpretation. These behaviors will support downstream automation like test generation, usability analysis, and workflow classification.

---

## 🧠 Core Goals

1. **Segment rrweb session data** into meaningful user interaction chunks.
2. **Extract deterministic features** to describe user interactions:

   * DOM mutations
   * Direct inputs (clicks, scrolls, typing)
   * Temporal gaps and delays
   * Mouse trajectory patterns
   * UI metadata (ARIA labels, roles, etc.)
3. **Detect high-level user actions** from combinations of those features
4. **Summarize sessions** as structured, labeled behavioral sequences
5. **Eliminate irrelevant or noisy data** (idle movement, micro-scrolls, redundant changes)
6. **Annotate contextual intent** to support rules and LLM prompting

---

## 📆 Expected Outputs

Each processed session should emit:

### 1. Interaction Chunks

```json
{
  "chunk_id": "session_abc-01",
  "start": 123456789,
  "end": 123456899,
  "events": [...],
  "features": {
    "click": {
      "target_id": 34,
      "aria_label": "Submit Form",
      "tag": "button"
    },
    "delay_to_next_mutation": 1500,
    "mouse_path": [...]
  }
}
```

### 2. Summarized User Actions

```json
[
  {
    "action": "form_submit",
    "confidence": 0.85,
    "description": "Clicked on 'Submit' button after typing email."
  }
]
```

---

## 🔢 Session Preprocessing & Chunking

To make the sessions suitable for feature extraction and behavior inference, the raw rrweb JSON data must be preprocessed:

### 🔄 Step-by-Step Breakdown

#### 1. Parse and Sort Events

Events are first sorted by their `timestamp` to ensure temporal accuracy.

#### 2. Classify Events by Type

| Type                  | Description                                         |
| --------------------- | --------------------------------------------------- |
| `FullSnapshot`        | Full DOM snapshot                                   |
| `IncrementalSnapshot` | Small updates (mutations, mouse moves, input, etc.) |
| `Meta`                | Info about device/window dimensions                 |
| `Custom`              | App-specific, optional                              |
| `Plugin`              | Plugin-specific data (e.g., console logs)           |

#### 3. Segment into Logical Chunks

Heuristics for creating meaningful chunks:

* Start a new chunk if:

  * A `FullSnapshot` is seen
  * Time since last event > 10s
  * Scroll and click occur together
  * A form is submitted
* Limit each chunk by time (e.g. 5-10 seconds) or count (e.g. max 20 events)

#### 4. Filter Low-Signal Events

Remove or down-rank:

* Cursor-only movement sequences
* Scrolls < 20px
* Redundant DOM mutations (e.g. attribute flips)
* Inputs without blur or submit
* Repeated/no-op input or scroll actions

#### 5. Normalize and Output Structured Chunks

Each chunk will contain:

* Unique ID
* Time window (`start_time`, `end_time`)
* Events
* Summary features (e.g., first click, delay to mutation, scroll events)

---

## 📚 Feature Set Reference

### 🔄 Timestamps and Delays

* **Purpose:** Segment sessions, identify gaps, detect async system responses.
* **Examples:**

  * Long delay between click and mutation = async operation
  * Large idle gaps = separate workflow
  * Rapid click + mutation = highly responsive interaction

### 📏 DOM Mutations

* **Sources:** `IncrementalSnapshot` with `source: 0`
* **Types:**

  * `adds`, `removes`, `attributes`, `texts`
* **Usage:**

  * Reveal what changed in response to an interaction
  * Link to target elements (e.g., expanded menu, new DOM content)
  * Interpret structure and side effects of interactions

### 📉 Input / Click / Focus Events

* **Sources:** `IncrementalSnapshot` with `source`:

  * `2`: Mouse interactions (click, dblclick)
  * `5`: Input (text changes, checkboxes)
  * `3`: Scroll
* **Usage:**

  * Anchor events in time
  * Establish user intent (form fill, navigation, toggle)
  * Support rules (e.g., click on \[aria-label=Submit])

### 🦍 Mouse Trajectory Clusters

* **Sources:** `IncrementalSnapshot`, `source: 1`
* **Usage:**

  * Group mouse moves leading to interaction
  * Classify behavior: direct vs. exploratory
  * Detect rage clicks, hover-intent patterns, abandoned actions

### 📈 Scroll Events and Viewport Transitions

* **Sources:** `IncrementalSnapshot`, `source: 3`
* **Usage:**

  * Identify user reading/navigation zones
  * Detect lazy load triggers (scroll → mutation)
  * Differentiate workflows within long pages

### 🔍 UI Metadata and DOM Hierarchy

* **Extracted from:** DOM node definitions in `FullSnapshot` and `Mutation` nodes
* **Key fields:**

  * `tagName`, `id`, `class`
  * `data-testid`, `aria-label`, `role`
  * Text content
* **Usage:**

  * Semantic meaning of elements
  * Rule targeting (e.g., role=button and aria-label^="Submit")
  * LLM-readable labels for prompt context

---

## ⚖️ Behavioral Constraints

| Constraint           | Description                                                     |
| -------------------- | --------------------------------------------------------------- |
| Chunking by time     | Separate chunks if idle gap > 10s                               |
| Input chaining       | Input events with no submit/blur are partial                    |
| Mutation attribution | Match mutation within 1.5s of click/input                       |
| Scroll threshold     | Scrolls < 20px often ignored                                    |
| Mouse intent         | Mouse move clusters <3 points ignored unless followed by action |
| Metadata fallback    | If `aria-label` is missing, use textContent or testid           |

---

## ⚠️ Risks and Edge Cases

| Category             | Risk                                                                   |
| -------------------- | ---------------------------------------------------------------------- |
| DOM tracking         | Reused node IDs or lost updates can cause false paths                  |
| Animation noise      | Mutation-only animations may appear as actions                         |
| Incomplete input     | Text typed but no submit may be misleading                             |
| Mobile / touch       | Touch events differ in timing and source from mouse                    |
| Custom widgets       | Framework-specific UIs may not use semantic roles                      |
| High-frequency noise | Rapid DOM or mousemove flooding (e.g., sliders) may overwhelm analysis |

---

## ⏳ Future Enhancements (Post-MVP)

* Vector-based action embedding for similar session retrieval
* Feedback loop with human corrections
* LLM summarization of intent and workflow
* Rule confidence tuning based on session history
* Interactive review UI for feedback and validation
