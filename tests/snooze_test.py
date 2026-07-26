import pytest

from helpers.todo_helpers import (
    add_todo,
    find_todos,
    snooze_todo,
    wait_for_todo,
    wait_for_todo_to_disappear,
)
from helpers.work_context_helpers import get_active_work_context, select_work_context


@pytest.mark.parametrize("test_name", ["Snooze: Snooze and view snoozed todo"])
def test_snooze(page, todo_prefix):
    # Add a todo
    todo_description = f"{todo_prefix} buy groceries next month"
    add_todo(page, todo_description)

    # Wait for it to appear
    wait_for_todo(page, todo_description)

    # Find the todo item
    todos = find_todos(page, todo_description)
    assert todos.count() == 1
    todo_item = todos.first

    # Snooze it via the alarm icon (select "Next Month" preset)
    snooze_todo(page, todo_item, "Next Month")

    # Verify the todo disappears from the current view (Inbox)
    wait_for_todo_to_disappear(page, todo_description)
    todos = find_todos(page, todo_description)
    assert todos.count() == 0

    # Click the "Snoozed" work context chip
    select_work_context(page, "Snoozed")

    # Verify the todo appears in the Snoozed work context
    wait_for_todo(page, todo_description)
    assert get_active_work_context(page) == "Snoozed"
    todos = find_todos(page, todo_description)
    assert todos.count() == 1
