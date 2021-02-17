import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.todo_helpers import add_todo, complete_todo, find_todos, list_todo_descriptions


CHECKED_SVG_PATH = 'M256 8C119.033 8 8 119.033 8 256s111.033 248 248 248 248-111.033 248-248S392.967 8 256 8zm0 48c110.532 0 200 89.451 200 200 0 110.532-89.451 200-200 200-110.532 0-200-89.451-200-200 0-110.532 89.451-200 200-200m140.204 130.267l-22.536-22.718c-4.667-4.705-12.265-4.736-16.97-.068L215.346 303.697l-59.792-60.277c-4.667-4.705-12.265-4.736-16.97-.069l-22.719 22.536c-4.705 4.667-4.736 12.265-.068 16.971l90.781 91.516c4.667 4.705 12.265 4.736 16.97.068l172.589-171.204c4.704-4.668 4.734-12.266.067-16.971z'


@pytest.mark.parametrize('test_name', ['Todo: Checkmark Persistence'])
def test_todos_checkmark_persistence(driver, todo_prefix):
    # Add todos
    todo1_description = "{} 1st test todo".format(todo_prefix)
    add_todo(driver, todo1_description)
    todo2_description = "{} 2nd test todo".format(todo_prefix)
    add_todo(driver, todo2_description)

    # Wait for todos to appear
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//span[text()="{}"]'.format(todo1_description)))
    )
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//span[text()="{}"]'.format(todo2_description)))
    )
    first_todo = find_todos(driver, todo1_description)
    assert len(first_todo) == 1
    first_todo = first_todo[0]

    # Verify that the 1st todo appears before 2nd todo
    todo_descriptions = list_todo_descriptions(driver, todo_prefix)
    assert todo_descriptions == [todo1_description, todo2_description]

    # Check off the 1st todo
    complete_todo(first_todo)

    # Wait for and verify that checkbox appears checked
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[starts-with(@id,"todo-checked")]/span[text()="{}"]'.format(todo1_description)))
    )
    first_todo = find_todos(driver, todo1_description)
    assert len(first_todo) == 1
    first_todo = first_todo[0]
    assert first_todo.get_attribute('id').startswith('todo-checked')
    checkbox = first_todo.find_element_by_xpath('.//div/*[name()="svg"]/*[name()="path"]')
    # Verify that checkmark icon is shown
    assert checkbox.get_attribute('d') == CHECKED_SVG_PATH

    # Verify that the 2nd todo appears before 1st todo once the 1st is completed
    todo_descriptions = list_todo_descriptions(driver, todo_prefix)
    assert todo_descriptions == [todo2_description, todo1_description]
