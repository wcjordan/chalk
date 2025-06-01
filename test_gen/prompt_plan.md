### **Phase 1: CLI Foundation**

---

**Subtasks:**

1. Set up Python project folder + CLI skeleton
2. Implement CLI using `click` (or `argparse`) with subcommands: `analyze`, `report`, `generate`
3. Add argument parsing + config loading
4. Create placeholder log + error handling

**Agent Prompts:**

* *Prompt 1:*
  “Generate a Python CLI skeleton using `click` with three subcommands: `analyze`, `report`, `generate`. Each subcommand should print ‘running \[command]’ as a placeholder.”

* *Prompt 2:*
  “Add argument parsing to the CLI so the user can pass input and output directory paths. Make sure these are available inside each subcommand.”

* *Prompt 3:*
  “Implement a basic logging setup (using `logging`) so that all CLI actions are logged to both console and file, with error and debug levels configurable via command-line flags.”

---

### **Phase 2: Session Analysis**

---

**Subtasks:**

1. Load and parse combined rrweb JSON session files
2. Integrate pluggable LLM API wrapper (initial: OpenAI API)
3. Build rule-based matcher (detect repeated selectors, actions)
4. Combine LLM + rule results to generate workflow mappings with confidence scores
5. Store mappings + confidence in a structured flat file (YAML or JSON)

**Agent Prompts:**

* *Prompt 1:*
  “Write a Python function to load a directory of rrweb JSON session files. Each file contains a full session (combined chunks). Parse them into Python objects for analysis.”

* *Prompt 2:*
  “Create a Python module wrapping the OpenAI API (or other LLM API) with a `run_prompt()` function. It should allow passing the prompt + system message + past examples, and return structured JSON output.”

* *Prompt 3:*
  “Implement a rule-based analysis module that scans the loaded session data and detects frequently used CSS selectors, button texts, and common patterns. Output a dictionary of proposed action mappings.”

* *Prompt 4:*
  “Write a function that combines the LLM-proposed mappings and rule-based mappings into a unified list of workflows, attaching a confidence score (0–1) to each.”

* *Prompt 5:*
  “Save the combined mappings + confidence scores to a YAML file called `workflow_mappings.yaml`. Include original session ID references for traceability.”

---

### **Phase 3: Reporting**

---

**Subtasks:**

1. Generate a combined report file summarizing all workflows, actions, confidence scores
2. Highlight unknown or low-confidence areas for review
3. Allow human edits/annotations in the report (flat file)
4. Load back annotated corrections into the system

**Agent Prompts:**

* *Prompt 1:*
  “Generate a YAML or markdown report summarizing all analyzed workflows, their associated user actions, and confidence scores. Highlight entries with confidence below 0.7.”

* *Prompt 2:*
  “Write a Python function that parses the human-edited YAML or markdown report and extracts corrections or annotations, updating the internal mappings accordingly.”

---

### **Phase 4: Test Generation**

---

**Subtasks:**

1. Create Python Playwright test script generator
2. Build helper module with reusable user actions (with docstrings + descriptions)
3. Embed workflow + action descriptions in test files
4. Write generated files directly to the `tests/` folder
5. Generate metadata files (traceability, mappings, etc.)

**Agent Prompts:**

* *Prompt 1:*
  “Write a Python function that generates a Playwright Python test file for a given workflow. It should import helper functions, include a descriptive docstring, and be placed in the `tests/` folder.”

* *Prompt 2:*
  “Create a helper module (`helpers.py`) defining reusable functions for common user actions (e.g., add\_task, complete\_task). Each helper should include a plain-English docstring explaining its purpose.”

* *Prompt 3:*
  “Write a metadata generator that outputs a YAML or JSON file summarizing which workflows are covered by which generated test files and helper functions.”

---

### **Phase 5: Learning System**

---

**Subtasks:**

1. Build feedback history store (flat file) to track past corrections
2. Modify analyzer to load feedback history as part of context
3. Update prompt construction for the LLM to include relevant prior feedback
4. Provide mechanism to update rules/mappings over time

**Agent Prompts:**

* *Prompt 1:*
  “Design a Python class that manages a feedback history store saved as a YAML or JSON file. It should support adding new corrections and retrieving prior corrections for use in future analyses.”

* *Prompt 2:*
  “Update the session analyzer to load the feedback history and include it in the prompt context when calling the LLM. Ensure that past corrections help guide new predictions.”

* *Prompt 3:*
  “Write a function that, after each run, updates the feedback history file with any new human corrections or LLM improvements.”

✅ Awesome! Here’s a **set of full LLM prompt templates** (with example inputs + expected outputs) designed to guide an agentic LLM doing the session-to-workflow analysis.

---

## Detailed Prompts

---

### 🛠 **Prompt Template 1: Map Session to User Workflows**

---

**Prompt:**

> You are an expert in UI behavior analysis.
> I will provide you with an rrweb-captured user session represented as a sequence of DOM events (clicks, input, navigations).
>
> Your task is to:
> 1️⃣ Identify which **user workflows** are represented in the session (e.g., add task, edit task, complete task, search tasks, delete task, filter by tag).
> 2️⃣ Break the workflows into **individual user actions**, specifying the CSS selectors or DOM paths interacted with.
> 3️⃣ Assign a **confidence score** (0–1) to each workflow and action.
> 4️⃣ Summarize in a structured JSON format.
>
> You may reference the following **existing workflow-to-action mappings** for context:
> {EXISTING\_MAPPINGS}
>
> If you encounter unknown workflows, flag them clearly for human review.

---

**Example Input (session excerpt):**

```json
{
  "session_id": "session_1234",
  "events": [
    {"type": "click", "selector": "button.add-task", "timestamp": 12345},
    {"type": "input", "selector": "input.task-title", "value": "Buy milk", "timestamp": 12346},
    {"type": "click", "selector": "button.submit-task", "timestamp": 12347},
    {"type": "click", "selector": "button.filter-tag", "timestamp": 12350},
    {"type": "click", "selector": "li.tag-item[data-tag='groceries']", "timestamp": 12351}
  ]
}
```

---

**Expected Output (JSON):**

```json
{
  "session_id": "session_1234",
  "workflows": [
    {
      "name": "add_task",
      "confidence": 0.95,
      "actions": [
        {"selector": "button.add-task", "description": "Click Add Task button", "confidence": 0.95},
        {"selector": "input.task-title", "description": "Enter task title", "confidence": 0.98},
        {"selector": "button.submit-task", "description": "Submit new task", "confidence": 0.96}
      ]
    },
    {
      "name": "filter_by_tag",
      "confidence": 0.9,
      "actions": [
        {"selector": "button.filter-tag", "description": "Open tag filter menu", "confidence": 0.92},
        {"selector": "li.tag-item[data-tag='groceries']", "description": "Select 'groceries' tag", "confidence": 0.9}
      ]
    }
  ],
  "unknown_workflows": []
}
```

---

### 🛠 **Prompt Template 2: Propose New Rule Candidates**

---

**Prompt:**

> Given the following rrweb session data, analyze the **repeated patterns** of CSS selectors, button texts, and common actions.
>
> Generate a list of **proposed new rule candidates** to help match user actions to workflows in the future.
>
> Present the results as structured JSON, showing:
>
> * Selector or pattern
> * Example text or attribute
> * Proposed workflow mapping (if possible)
> * Confidence score

---

**Example Input (session excerpt):**

```json
[
  {"type": "click", "selector": "button.add-task"},
  {"type": "input", "selector": "input.task-title"},
  {"type": "click", "selector": "button.submit-task"},
  {"type": "click", "selector": "button.add-task"},
  {"type": "input", "selector": "input.task-title"},
  {"type": "click", "selector": "button.submit-task"}
]
```

---

**Expected Output (JSON):**

```json
{
  "new_rule_candidates": [
    {
      "selector": "button.add-task",
      "example_text": "Add Task",
      "proposed_workflow": "add_task",
      "confidence": 0.95
    },
    {
      "selector": "input.task-title",
      "example_text": "Task Title",
      "proposed_workflow": "add_task",
      "confidence": 0.9
    },
    {
      "selector": "button.submit-task",
      "example_text": "Submit",
      "proposed_workflow": "add_task",
      "confidence": 0.92
    }
  ]
}
```

---

### 🛠 **Prompt Template 3: Refine Mappings with Feedback**

---

**Prompt:**

> Here are existing workflow mappings and past human feedback corrections.
> Please refine the mappings to reflect the feedback and improve the confidence scores.
> Provide the updated mappings in structured JSON.
>
> **Existing mappings:**
> {EXISTING\_MAPPINGS}
>
> **Feedback history:**
> {FEEDBACK\_HISTORY}

---

**Example Input:**

```json
{
  "existing_mappings": [
    {"workflow": "add_task", "selector": "button.add-task", "confidence": 0.7},
    {"workflow": "filter_by_tag", "selector": "button.filter-tag", "confidence": 0.6}
  ],
  "feedback": [
    {"workflow": "add_task", "selector": "button.add-task", "confirmed": true},
    {"workflow": "filter_by_tag", "selector": "button.filter-tag", "corrected_to": "open_filter_menu"}
  ]
}
```

---

**Expected Output:**

```json
{
  "updated_mappings": [
    {"workflow": "add_task", "selector": "button.add-task", "confidence": 0.95},
    {"workflow": "open_filter_menu", "selector": "button.filter-tag", "confidence": 0.9}
  ]
}
```

---

### 🛠 **Prompt Template 4: Summarize Workflow for Test Code Generation**

---

**Prompt:**

> Summarize the following workflow into a **plain-English description** and **Python helper function docstring**.
>
> Provide:
>
> * Workflow name
> * Plain-English summary
> * Recommended Python helper function name
> * Docstring text

---

**Example Input:**

```json
{
  "workflow": "add_task",
  "actions": [
    {"selector": "button.add-task", "description": "Click Add Task button"},
    {"selector": "input.task-title", "description": "Enter task title"},
    {"selector": "button.submit-task", "description": "Submit new task"}
  ]
}
```

---

**Expected Output:**

```json
{
  "workflow_name": "add_task",
  "summary": "This workflow adds a new task by opening the task form, entering the title, and submitting it.",
  "helper_function": "add_task",
  "docstring": "Adds a new task by opening the task form, entering a title, and submitting it."
}
```

