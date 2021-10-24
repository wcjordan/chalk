import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.todo_helpers import (CHECKED_ICON_TEXT, DELETE_ICON_TEXT, LABELS_ICON_TEXT, add_todo, complete_todo, find_todo, list_todo_descriptions, wait_for_todo)


@pytest.mark.parametrize('test_name', ['Todo: Checkmark Persistence'])
def test_todos_checkmark_persistence(driver, todo_prefix):
    # Add todos
    todo1_description = f'{todo_prefix} 1st test todo'
    add_todo(driver, todo1_description)
    todo2_description = f'{todo_prefix} 2nd test todo'
    add_todo(driver, todo2_description)

    # Wait for todos to appear
    wait_for_todo(driver, todo1_description)
    wait_for_todo(driver, todo2_description)
    first_todo = find_todo(driver, todo1_description)

    # Verify that the 1st todo appears before 2nd todo
    todo_descriptions = list_todo_descriptions(driver, todo_prefix)
    assert todo_descriptions == [todo1_description, todo2_description]

    # Check off the 1st todo
    complete_todo(first_todo)

    # Wait for and verify that checkbox appears checked
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,
            f'//div[@data-testid="complete-todo" and @aria-checked="true"]/../following-sibling::div/div[text()="{todo1_description}"]'))
    )
    first_todo = find_todo(driver, todo1_description)
    first_todo_checkmark = first_todo.find_element(By.CSS_SELECTOR, 'div[aria-checked="true"]');
    assert first_todo_checkmark
    expected_text = f'{CHECKED_ICON_TEXT}\n{todo1_description}\n{LABELS_ICON_TEXT}\n{DELETE_ICON_TEXT}'
    assert first_todo.text == expected_text

    # Verify that the 2nd todo appears before 1st todo once the 1st is completed
    todo_descriptions = list_todo_descriptions(driver, todo_prefix)
    assert todo_descriptions == [todo2_description, todo1_description]
