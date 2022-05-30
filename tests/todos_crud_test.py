import pytest

from helpers.todo_helpers import (add_todo, delete_todo, edit_todo, find_todo,
                                  find_todos, wait_for_todo,
                                  wait_for_todo_to_disappear)


@pytest.mark.parametrize('test_name', ['Todo: Create, Update, Delete'])
def test_todos_crud(page, todo_prefix):
    # Add todo
    todo_description = f'{todo_prefix} test todo'
    add_todo(page, todo_description)

    # Find todo & verify
    wait_for_todo(page, todo_description)
    created_todo = find_todo(page, todo_description)

    # Edit todo
    updated_todo_description = f'{todo_prefix} test todo updated'
    edit_todo(page, created_todo, updated_todo_description)

    # Verify
    wait_for_todo_to_disappear(page, todo_description)
    wait_for_todo(page, updated_todo_description)

    todos_w_old_description = find_todos(page, todo_description)
    assert todos_w_old_description.count() == 0
    updated_todo = find_todo(page, updated_todo_description)

    # Delete todo
    delete_todo(updated_todo)

    # Verify
    wait_for_todo_to_disappear(page, updated_todo_description)
    deleted_todos = find_todos(page, updated_todo_description)
    assert deleted_todos.count() == 0
