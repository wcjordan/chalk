import pytest

from helpers.label_helpers import (add_labels, clear_label_filters, dismiss_add_label_modal, get_label_filter_status, toggle_label_filter)
from helpers.todo_helpers import (add_todo, find_todos, wait_for_todo,
                                  wait_for_todo_to_disappear)


@pytest.mark.parametrize('test_name', ['Workflow: Inbox Workflow'])
def test_inbox_workflow(page, todo_prefix):
    # Verify Unlabeled starts selected
    assert get_label_filter_status(page, 'Unlabeled') == 'Active'

    # Remove default filter
    clear_label_filters(page)

    # Add todo
    todo_description = f'{todo_prefix} fold laundry'
    add_todo(page, todo_description)

    # Wait for todo to appear
    wait_for_todo(page, todo_description)

    # Open inbox view
    toggle_label_filter(page, 'Unlabeled')

    # Verify todo visible
    todos = find_todos(page, todo_description)
    assert todos.count() == 1
    todo_item = todos.first

    # Add label
    add_labels(page, todo_item, ['errand'], dismiss_picker=False)

    # Verify todo visible
    todos = find_todos(page, todo_description)
    assert todos.count() == 1
    todo_item = todos.first

    # Verify labels
    todo_labels = todo_item.locator('[data-testid="todo-labels"] > div').all_text_contents()
    assert todo_labels == ['errand']

    # Add label
    add_labels(page, todo_item, ['email'], dismiss_picker=False,
               open_picker=False)

    # Verify todo visible
    todos = find_todos(page, todo_description)
    assert todos.count() == 1
    todo_item = todos.first

    # Verify labels
    todo_labels = todo_item.locator('[data-testid="todo-labels"] > div').all_text_contents()
    assert todo_labels == ['errand', 'email']

    # Dismiss picker modal
    dismiss_add_label_modal(page)

    # Verify todo is not visible
    wait_for_todo_to_disappear(page, todo_description)
    todos = find_todos(page, todo_description)
    assert todos.count() == 0
