## ✅ Incremental Implementation Plan for Rule-Based Action Detection

---

### **Step 1: Define Core Data Models**

**What it accomplishes:**
Introduce `DetectedAction` and `Rule` models using Python dataclasses. These represent the output and the parsed rule schema.

**How to verify:**

* Unit tests validate instantiation and field access
* Sample `Rule` object can be created from a dictionary
* No side effects; safe to merge independently

**Detailed Prompt**

#### ✅ Requirements

Create the following dataclasses in a new file:

📄 `test_gen/rule_engine/models.py`

##### 1. `DetectedAction`

Represents a user action detected by a rule.

Fields:

* `action_id: str` — human-readable label (e.g., `"search_query"`)
* `timestamp: int` — timestamp from the first matched event
* `confidence: float` — fixed or rule-supplied confidence
* `rule_id: str` — ID of the rule that matched
* `variables: Dict[str, Any]` — extracted values (e.g., input text)
* `target_element: Optional[UINode]` — the `UINode` involved, if any
* `related_events: List[int]` — indices of events in the chunk that contributed to the match

##### 2. `Rule`

Represents a rule parsed from YAML.

Fields:

* `id: str`
* `description: Optional[str]`
* `match: Dict[str, Any]` — event and node match conditions
* `confidence: float`
* `variables: Dict[str, str]` — variable extraction expressions
* `action_id: str`

Use Python 3.9+ typing (`list`, `dict`, `Optional`, not `List`, `Dict` from `typing` unless necessary).

---

#### 🧪 Testing

Create a unit test file:
📄 `test_gen/rule_engine/tests/test_models.py`

Write simple tests that:

* Instantiate `DetectedAction` and `Rule` with sample data
* Assert field values are correctly stored and accessible
* Ensure missing optional fields (like `description`) do not raise errors

Do not implement logic — just data structure definitions and basic tests.

---

### **Step 2: Implement Rule Loader**

**What it accomplishes:**
Add support for loading YAML rule files from disk and converting them into `Rule` objects.

**How to verify:**

* Load all rules in `test_gen/data/rules/` directory
* Unit tests verify parsing of well-formed rule files
* Invalid or missing fields raise clean validation errors

**Detailed Prompt**

You are building a rule-based engine that processes rrweb session chunks to detect user actions. Your current task is to implement the **Rule Loader**, which loads and validates rules from disk.

---

#### ✅ Requirements

Create the following module:
📄 `test_gen/rule_engine/rules_loader.py`

Implement a function:

```python
def load_rules(directory: Union[str, Path]) -> List[Rule]:
    ...
```

Where:

* `directory` points to the folder containing rule files (YAML format)
* Each file contains one rule (schema described below)
* The function loads and parses all rule files into `Rule` objects defined in `models.py`

Raise a `ValueError` for any rule missing required fields.

Use the `Rule` dataclass from:
📄 `test_gen/rule_engine/models.py`

---

#### 📁 Input Folder

All rule files are in:
`test_gen/data/rules/`
Each rule is a `.yaml` file with the following structure:

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
action_id: search_query
```

Required fields:

* `id`, `match`, `confidence`, `variables`, `action_id`

---

#### 🧪 Testing

Create the following test file:
📄 `test_gen/rule_engine/tests/test_rules_loader.py`

Write unit tests that:

* Load one or more valid `.yaml` files from a temp dir or fixture
* Confirm that a `Rule` object is returned with expected fields
* Include negative test: malformed rule (e.g., missing `action_id`) raises `ValueError`
* Include test for multiple rule files in the directory

---

#### ✅ Deliverables

* `rules_loader.py` with `load_rules(...)` function
* `test_rules_loader.py` with coverage of:

  * Valid parsing
  * Invalid structure
  * File iteration

Do not implement rule evaluation or matching yet — only loading and validation.

---

### **Step 3: Match Rule Against Single Event + Node**

**What it accomplishes:**
Implement matching logic for a single `UserInteraction` and its associated `UINode` using the `match` block from a rule.

**How to verify:**

* Unit tests for positive and negative rule matches
* Supports `tag` and `attributes` on node
* Supports `action` on event

---

**Detailed Prompt**

#### ✅ Requirements

Create or update this module:
📄 `test_gen/rule_engine/matcher.py`

Implement the following function:

```python
def rule_matches_event_node(
    rule: Rule,
    event: UserInteraction,
    node: UINode
) -> bool:
    ...
```

This function returns `True` if both:

* The `event` matches `rule.match.event`
* The `node` matches `rule.match.node`

Return `False` if any condition fails.

---

#### 🎯 Matching Criteria

##### `match.event` block supports:

* `action`: exact string match with `event.action`

##### `match.node` block supports:

* `tag`: exact string match with `node.tag`
* `attributes`: dictionary of required key-value pairs. Match only if all specified attributes are present in `node.attributes` and values are equal.

Example:

```yaml
match:
  event:
    action: input
  node:
    tag: input
    attributes:
      type: search
```

The above rule would match if:

* `event.action == "input"`
* `node.tag == "input"`
* `"type": "search"` exists in `node.attributes`

---

#### 🧪 Testing

Create the following test file:
📄 `test_gen/rule_engine/tests/test_matcher.py`

Write unit tests for `rule_matches_event_node(...)`:

* Positive case: event and node match fully
* Negative case: action mismatch
* Negative case: tag mismatch
* Negative case: missing or incorrect attribute

Use mock objects or real `UserInteraction` and `UINode` instances.

---

#### ✅ Deliverables

* Function: `rule_matches_event_node(rule, event, node) → bool`
* Unit test file: `test_matcher.py` with full coverage
* No dependencies on variable extraction, chunk traversal, or DOM queries yet

Let me know when you're ready for Step 4: Variable Extraction.

---

### **Step 4: Add Variable Extraction (Direct Fields)**

**What it accomplishes:**
Extract values from matched `event` and `node` based on the `variables:` section of a rule.

**How to verify:**

* Unit tests validate extraction from:

  * `event.value`
  * `node.text`
  * `node.attributes.<key>`
* Fallback or error behavior clearly defined (e.g., missing fields = None)

---

### **Step 5: Emit `DetectedAction` for Matches**

**What it accomplishes:**
Generate `DetectedAction` objects for successfully matched rules including confidence, timestamp, variables, etc.

**How to verify:**

* Unit tests confirm correct `DetectedAction` is returned for a sample match
* Timestamp uses `UserInteraction.timestamp`
* `related_events` contains only the matched event

---

### **Step 6: Integrate Matcher Over Full Chunk**

**What it accomplishes:**
Add a top-level matcher that runs over all `UserInteraction`s in a session chunk and applies all rules.

**How to verify:**

* Accepts a full `chunk` object and returns a list of `DetectedAction`s
* Unit tests validate end-to-end matching with mock chunks and rules
* No integration with file I/O or storage yet

---

### **Step 7: Add CSS-style Child Node Query Support**

**What it accomplishes:**
Support rules that extract values from descendant nodes via simple CSS selectors (e.g., `node.query("div > span").text`)

**How to verify:**

* Introduce helper for DOM traversal
* Mock DOM structure in tests
* Unit tests verify successful extraction or fallback behavior

---

### **Step 8: Serialize and Save Matched Actions**

**What it accomplishes:**
Write detected actions from a chunk to disk as JSON in `test_gen/data/action_mappings/`, keyed by `chunk_id`.

**How to verify:**

* CLI or function call can process a chunk and write a JSON file
* File content matches expected structure
* Integration test: process test chunk → check saved file

---

### **Step 9: Add CLI Entry Point**

**What it accomplishes:**
Add command-line interface to process a file or directory of chunk JSONs and produce matched actions.

**How to verify:**

* `python -m rule_engine.match_chunk input.json` works
* Accepts `--output` argument
* Prints summary: “3 actions detected from 1 rule”

---

### **Step 10: Add Logging and Rule Match Traceability**

**What it accomplishes:**
Introduce logging to trace which rules matched, which failed, and why (optional for debugging).

**How to verify:**

* Log output includes rule ID and matched element
* Can be toggled via verbosity flag

---

## 🚧 Future Steps (VNext)

After this MVP lands:

* Add multi-event rule support (e.g., input + click patterns)
* Introduce timing constraints
* Build visual or web-based rule explorer / tester
* Integrate feedback loop for refining or suppressing rules
