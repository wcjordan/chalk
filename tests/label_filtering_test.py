import pytest

from helpers.label_helpers import (
    add_todo_w_labels,
    clear_label_filters,
    get_label_filter_status,
    get_todo_labels,
    toggle_label_filter,
    toggle_label_filter_section,
)
from helpers.todo_helpers import (
    add_todo,
    find_todo,
    list_todo_descriptions,
    wait_for_todo,
    wait_for_todo_to_disappear,
)


@pytest.mark.parametrize("test_name", ["Label: Label Filtering"])
def test_label_filtering(page, todo_prefix):
    # Add todos w/ labels
    todo_5min_low_desc = f"{todo_prefix} test todo - 5min low energy"
    add_todo_w_labels(page, todo_5min_low_desc, ["low-energy", "5 minutes"])

    todo_25min_low_desc = f"{todo_prefix} test todo - 25min low energy"
    add_todo_w_labels(page, todo_25min_low_desc, ["low-energy", "25 minutes"])

    todo_25min_high_desc = f"{todo_prefix} test todo - 25min high energy"
    add_todo_w_labels(page, todo_25min_high_desc, ["high-energy", "25 minutes"])

    # Select low-energy & verify 2 low-energy todos shown
    toggle_label_filter_section(page)
    toggle_label_filter(page, "low-energy")
    wait_for_todo_to_disappear(page, todo_25min_high_desc)
    todo_descriptions = list_todo_descriptions(page, todo_prefix)
    assert todo_descriptions == [todo_5min_low_desc, todo_25min_low_desc]
    assert get_label_filter_status(page, "low-energy") == "Active"

    # Select 25 minutes & verify 1 low-energy 25 minutes todos shown
    toggle_label_filter(page, "25 minutes")
    wait_for_todo_to_disappear(page, todo_5min_low_desc)
    todo_descriptions = list_todo_descriptions(page, todo_prefix)
    assert todo_descriptions == [todo_25min_low_desc]
    assert get_label_filter_status(page, "25 minutes") == "Active"

    # Select 5 minutes & verify no todos shown
    toggle_label_filter(page, "5 minutes")
    wait_for_todo_to_disappear(page, todo_25min_low_desc)
    todo_descriptions = list_todo_descriptions(page, todo_prefix)
    assert todo_descriptions == []
    assert get_label_filter_status(page, "5 minutes") == "Active"

    # Unselect 5 minutes & verify 1 low-energy 25 minutes todos shown
    # Toggle twice since once switches to inverted
    toggle_label_filter(page, "5 minutes")
    toggle_label_filter(page, "5 minutes")
    wait_for_todo(page, todo_25min_low_desc)
    todo_descriptions = list_todo_descriptions(page, todo_prefix)
    assert todo_descriptions == [todo_25min_low_desc]
    assert get_label_filter_status(page, "5 minutes") == "Disabled"

    # Invert low-energy & verify 1 high-energy 25 min todo shown
    toggle_label_filter(page, "low-energy")
    wait_for_todo(page, todo_25min_high_desc)
    todo_descriptions = list_todo_descriptions(page, todo_prefix)
    assert todo_descriptions == [todo_25min_high_desc]
    assert get_label_filter_status(page, "low-energy") == "Inverted"

    # Unselect low-energy & verify 2 25 minutes todos shown
    toggle_label_filter(page, "low-energy")
    wait_for_todo(page, todo_25min_low_desc)
    todo_descriptions = list_todo_descriptions(page, todo_prefix)
    assert todo_descriptions == [todo_25min_low_desc, todo_25min_high_desc]
    assert get_label_filter_status(page, "low-energy") == "Disabled"


@pytest.mark.parametrize("test_name", ["Label: Auto-Assign Filter Labels"])
def test_create_todo_with_active_filters(page, todo_prefix):
    """Test that new todos automatically get active filter labels."""
    # Open label filter section
    toggle_label_filter_section(page)

    # Clear any existing filters first
    clear_label_filters(page)

    # Activate 'work' filter
    toggle_label_filter(page, "work")
    assert get_label_filter_status(page, "work") == "Active"

    toggle_label_filter(page, "5 minutes")
    toggle_label_filter(page, "5 minutes")
    assert get_label_filter_status(page, "5 minutes") == "Inverted"

    # Create a new todo while 'work' filter is active
    todo_desc = f"{todo_prefix} test todo with work label"
    add_todo(page, todo_desc)

    # Verify todo appears in the filtered list
    wait_for_todo(page, todo_desc)
    todo_descriptions = list_todo_descriptions(page, todo_prefix)
    assert todo_desc in todo_descriptions

    # Verify the todo has the 'work' label
    todo_item = find_todo(page, todo_desc)
    labels = get_todo_labels(todo_item)
    assert "work" in labels

    # Clear filters and verify todo still has the label
    clear_label_filters(page)
    wait_for_todo(page, todo_desc)
    todo_item = find_todo(page, todo_desc)
    labels = get_todo_labels(todo_item)
    assert "work" in labels
