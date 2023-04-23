import pytest

from helpers.label_helpers import (clear_label_filters, toggle_label_filter)
from helpers.todo_helpers import (add_todo, cancel_edit, edit_todo, find_todo,
                                  find_todos, wait_for_todo,
                                  wait_for_todo_to_disappear)


@pytest.mark.parametrize('test_name', ['Todo: Don\'t Filter During Edit'])
def test_dont_filter_edit(page, todo_prefix):
    # Remove default filter
    clear_label_filters(page)

    # Add todos
    todo1_description = f'{todo_prefix} todo to edit'
    add_todo(page, todo1_description)
    todo2_description = f'{todo_prefix} todo to filter'
    add_todo(page, todo2_description)

    # Wait for todos to appear
    wait_for_todo(page, todo1_description)
    wait_for_todo(page, todo2_description)
    todo_to_edit = find_todo(page, todo1_description)

    # Edit the todo
    edit_description = f'{todo_prefix} edited description'
    edit_todo(page, todo_to_edit, edit_description, submit=False)

    # Add filter
    toggle_label_filter(page, 'home')

    # Wait for the filter to apply
    wait_for_todo_to_disappear(page, todo2_description)

    # Verify todo being edited is visible
    todos = find_todos(page, edit_description)
    assert todos.count() == 1
    todo_item = todos.first

    # Cancel edit and verify todo is filtered
    cancel_edit(page, todo_item)
    wait_for_todo_to_disappear(page, edit_description)
    todos = find_todos(page, todo_prefix, partial=True)
    assert todos.count() == 0
