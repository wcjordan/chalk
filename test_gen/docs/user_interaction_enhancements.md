# UserInteraction Enhancements: DOM Path & Text Content Extraction

## Overview

The `UserInteraction` dataclass has been enhanced with pre-computed DOM path and text content extraction capabilities. These values are automatically computed when interactions are extracted and stored in the `target_node` dictionary.

## Pre-computed Fields

When a `UserInteraction` is created, the following fields are automatically computed and stored in `target_node`:

### DOM Path & Element Identification

- **`dom_path`**: Full CSS-like selector path from root to the element
  - Example: `"html > body > div.container > button#submit"`

- **`data_testid`**: The `data-testid` attribute value of the element
  - Example: `"submit-button"`

- **`nearest_ancestor_testid`**: The `data-testid` of the nearest ancestor with one
  - Useful for elements without their own test ID but within a testable container
  - Example: `"user-profile-section"`

- **`nearest_ancestor_testid_dom_path`**: The DOM path to that ancestor
  - Example: `"html > body > div[data-testid='user-profile-section']"`

### Text Content

- **`text`**: Direct text content of the element (not including descendants)
  - Example: `"Submit"`

- **`all_descendant_text`**: Concatenated text from the element and ALL its descendants
  - Useful for buttons/links with nested spans
  - Example: For `<button><span>Submit</span> <span>Now</span></button>` → `"Submit Now"`

- **`aria_label`**: The `aria-label` attribute value
  - Example: `"Submit form"`

- **`role`**: The ARIA `role` attribute value
  - Example: `"button"`

## Accessing Values in Code

The `UserInteraction` class provides convenient getter methods:

```python
from rrweb_util.user_interaction.models import UserInteraction

# Create or retrieve a UserInteraction
interaction: UserInteraction = ...

# DOM Path & Identification
dom_path = interaction.get_dom_path()
testid = interaction.get_data_testid()
ancestor_testid = interaction.get_nearest_ancestor_testid()
ancestor_path = interaction.get_nearest_ancestor_testid_dom_path()

# Text Content
element_text = interaction.get_element_text()
full_text = interaction.get_all_descendant_text()
aria = interaction.get_aria_label()
role = interaction.get_role()
tag = interaction.get_tag()
```

## Using in Rules Engine

These fields can be accessed in rule YAML files using the variable resolver:

### Direct Field Access

```yaml
# Example: Capture button click with full text
id: "submit_button_click"
match:
  event:
    action: click
  node:
    tag: button
variables:
  button_label: "event.target_node.all_descendant_text"
  dom_location: "event.target_node.dom_path"
  parent_testid: "event.target_node.nearest_ancestor_testid"
confidence: 0.9
action_id: "submit_form"
```

### Method Call Access

```yaml
# Example: Using getter methods
id: "input_search"
match:
  event:
    action: input
  node:
    tag: input
    attributes:
      type: search
variables:
  search_query: "event.value.value"
  input_label: "event.get_aria_label()"
  full_button_text: "event.get_all_descendant_text()"
  element_path: "event.get_dom_path()"
  nearest_testid: "event.get_nearest_ancestor_testid()"
confidence: 0.95
action_id: "search_query_entered"
```

## Example Use Cases

### 1. Identifying Buttons with Nested Spans

Many modern UIs have buttons with complex nested structures:

```html
<button data-testid="checkout-btn">
  <span class="icon">🛒</span>
  <span class="label">Proceed to</span>
  <span class="label-bold">Checkout</span>
</button>
```

Rule to capture this:

```yaml
id: "checkout_button_click"
match:
  event:
    action: click
  node:
    tag: button
    attributes:
      data-testid: checkout-btn
variables:
  full_label: "event.get_all_descendant_text()"  # Returns: "🛒 Proceed to Checkout"
  testid: "event.get_data_testid()"               # Returns: "checkout-btn"
confidence: 1.0
action_id: "proceed_to_checkout"
```

### 2. Contextualizing Elements Without Test IDs

When clicking on elements that don't have their own test ID:

```html
<div data-testid="user-profile">
  <div class="header">
    <h2>John Doe</h2>
    <button id="123">Edit Profile</button>
  </div>
</div>
```

Rule for the edit button:

```yaml
id: "edit_profile_button"
match:
  event:
    action: click
  node:
    tag: button
variables:
  button_text: "event.get_all_descendant_text()"              # "Edit Profile"
  context_area: "event.get_nearest_ancestor_testid()"        # "user-profile"
  full_context_path: "event.get_nearest_ancestor_testid_dom_path()"
confidence: 0.85
action_id: "edit_user_profile"
```

### 3. Complex Input Fields

For input fields with labels or placeholder text:

```html
<div data-testid="search-container">
  <label for="search">Search Products</label>
  <input type="search" id="search" aria-label="Product search field" />
</div>
```

Rule:

```yaml
id: "product_search"
match:
  event:
    action: input
  node:
    tag: input
    attributes:
      type: search
variables:
  search_term: "event.value.value"
  accessibility_label: "event.get_aria_label()"         # "Product search field"
  container: "event.get_nearest_ancestor_testid()"      # "search-container"
confidence: 0.9
action_id: "search_products"
```

## Implementation Details

### Where Values Are Computed

Values are pre-computed in `rrweb_util/dom_state/node_metadata.py`:

- `resolve_node_metadata()` is called when extracting interactions
- It computes all fields and returns them in the metadata dict
- This dict becomes the `target_node` field in `UserInteraction`

### Performance Considerations

- All values are computed **once** when the interaction is extracted
- No on-demand computation when accessing via getter methods
- Efficient for rules that query the same interaction multiple times
- Text traversal uses depth-first search with memoization

### Handling Missing Values

- All getter methods return `Optional[str]` (can return `None`)
- Missing attributes, empty text, or nodes without parents gracefully return `None`
- Rules should handle `None` values appropriately

## Testing

Example test to verify the enhancements:

```python
from rrweb_util.user_interaction.models import UserInteraction

def test_text_extraction():
    interaction = UserInteraction(
        action="click",
        target_id=123,
        target_node={
            "tag": "button",
            "text": "Submit",
            "all_descendant_text": "Submit Now",
            "data_testid": "submit-btn",
            "dom_path": "html > body > button#submit-btn",
        },
        value={},
        timestamp=1000,
    )

    assert interaction.get_tag() == "button"
    assert interaction.get_element_text() == "Submit"
    assert interaction.get_all_descendant_text() == "Submit Now"
    assert interaction.get_data_testid() == "submit-btn"
    assert interaction.get_dom_path() == "html > body > button#submit-btn"
```

## Future Enhancements

Potential future additions:

1. **Attribute queries**: `get_attribute(name)` method
2. **Element type helpers**: `is_button()`, `is_text_input()` methods
3. **Sibling queries**: Find adjacent elements with specific properties
4. **CSS class matching**: Query based on CSS classes
5. **Parent chain access**: Get list of all parent elements up to root
