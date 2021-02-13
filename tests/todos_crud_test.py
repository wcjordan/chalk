import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.todo_helpers import add_todo, delete_todo, edit_todo, find_todos


@pytest.mark.parametrize('test_name', ['Todo: Create, Update, Delete'])
def test_todos_crud(driver, todo_prefix):
    # Add todo
    todo_description = "{} test todo".format(todo_prefix)
    add_todo(driver, todo_description)

    # Find todo & verify
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//span[text()="{}"]'.format(todo_description)))
    )
    created_todos = find_todos(driver, todo_description)
    assert len(created_todos) == 1
    todo_item = created_todos[0]

    # Edit todo
    updated_todo_description = "{} test todo updated".format(todo_prefix)
    edit_todo(todo_item, updated_todo_description)

    # Verify
    def text_updated(driver):
        if not EC.invisibility_of_element_located((By.XPATH, '//span[text()="{}"]'.format(todo_description)))(driver):
            return False
        if not EC.presence_of_element_located((By.XPATH, '//span[text()="{}"]'.format(updated_todo_description)))(driver):
            return False
        return True
    WebDriverWait(driver, 10).until(text_updated)

    todos_w_old_description = find_todos(driver, todo_description)
    assert len(todos_w_old_description) == 0
    updated_todos = find_todos(driver, updated_todo_description)
    assert len(updated_todos) == 1
    todo_item = updated_todos[0]

    # Delete todo
    delete_todo(todo_item)

    # Verify
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.XPATH, '//span[text()="{}"]'.format(updated_todo_description)))
    )
    deleted_todos = find_todos(driver, updated_todo_description)
    assert len(deleted_todos) == 0
