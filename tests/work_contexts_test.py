import pytest

from helpers.label_helpers import (
    add_labels,
    add_todo_w_labels,
    dismiss_add_label_modal,
    get_todo_labels,
)
from helpers.todo_helpers import (
    add_todo,
    find_todos,
    list_todo_descriptions,
    wait_for_todo,
    wait_for_todo_to_disappear,
)
from helpers.work_context_helpers import get_active_work_context, select_work_context


@pytest.mark.parametrize("test_name", ["Work Context: View Work Contexts"])
def test_work_contexts(page, todo_prefix):
    assert get_active_work_context(page) == "Inbox"

    # Add todo
    quick_todo_description = f"{todo_prefix} cool new idea"
    add_todo(page, quick_todo_description)

    # Wait for todo to appear
    wait_for_todo(page, quick_todo_description)

    # Verify todo visible
    todos = find_todos(page, quick_todo_description)
    assert todos.count() == 1
    todo_item = todos.first

    # Add label
    add_labels(page, todo_item, ["up next"], dismiss_picker=False)

    # Verify todo still visible while adding labels and label added
    todos = find_todos(page, quick_todo_description)
    assert todos.count() == 1
    todo_item = todos.first
    assert get_todo_labels(todo_item) == ["up next"]

    # Add label
    add_labels(page, todo_item, ["5 minutes"], dismiss_picker=False, open_picker=False)

    # Verify the todo is visible and label is added
    todos = find_todos(page, quick_todo_description)
    assert todos.count() == 1
    assert get_todo_labels(todos.first) == ["5 minutes", "up next"]

    # Dismiss picker modal
    dismiss_add_label_modal(page)

    # Verify todo is not visible
    wait_for_todo_to_disappear(page, quick_todo_description)
    todos = find_todos(page, quick_todo_description)
    assert todos.count() == 0

    # Add todos for shopping, urgent, & Chalk planning
    shopping_todo_description = f"{todo_prefix} buy milk"
    add_todo_w_labels(page, shopping_todo_description, ["Shopping"])
    urgent_todo_description = f"{todo_prefix} pay bills"
    add_todo_w_labels(page, urgent_todo_description, ["urgent"])
    planning_todo_description = f"{todo_prefix} investigate technology"
    add_todo_w_labels(page, planning_todo_description, ["Chalk", "vague"])

    todos = find_todos(page, todo_prefix, partial=True)
    assert todos.count() == 0

    # Select each work context and verify it has the expected todos
    _verify_todo_in_work_context(page, todo_prefix, urgent_todo_description, "Urgent")
    _verify_todo_in_work_context(
        page, todo_prefix, quick_todo_description, "Quick Fixes"
    )
    _verify_todo_in_work_context(
        page, todo_prefix, shopping_todo_description, "Shopping"
    )
    _verify_todo_in_work_context(page, todo_prefix, quick_todo_description, "Up Next")
    _verify_todo_in_work_context(
        page, todo_prefix, planning_todo_description, "Chalk Planning"
    )


def _verify_todo_in_work_context(page, todo_prefix, description, work_context):
    select_work_context(page, work_context)
    wait_for_todo(page, description)

    assert get_active_work_context(page) == work_context
    todos = find_todos(page, todo_prefix, partial=True)
    assert todos.count() == 1
    assert list_todo_descriptions(page, todo_prefix) == [description]
