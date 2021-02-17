import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.todo_helpers import add_todo, delete_todo, edit_todo, find_todo, find_todos, wait_for_todo, wait_for_todo_to_disappear


@pytest.mark.parametrize('test_name', ['Todo: Create, Update, Delete'])
def test_todos_crud(driver, todo_prefix):
    # Add todo
    todo_description = "{} test todo".format(todo_prefix)
    add_todo(driver, todo_description)

    # Find todo & verify
    wait_for_todo(driver, todo_description)
    created_todo = find_todo(driver, todo_description)

    # Edit todo
    updated_todo_description = "{} test todo updated".format(todo_prefix)
    edit_todo(created_todo, updated_todo_description)

    # Verify
    wait_for_todo_to_disappear(driver, todo_description)
    wait_for_todo(driver, updated_todo_description)

    todos_w_old_description = find_todos(driver, todo_description)
    assert len(todos_w_old_description) == 0
    updated_todo = find_todo(driver, updated_todo_description)

    # Delete todo
    delete_todo(updated_todo)

    # Verify
    wait_for_todo_to_disappear(driver, updated_todo_description)
    deleted_todos = find_todos(driver, updated_todo_description)
    assert len(deleted_todos) == 0
