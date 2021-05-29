import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.todo_helpers import (UNCHECKED_ICON_TEXT, DELETE_ICON_TEXT, WARNING_ICON_TEXT, add_todo, complete_todo, edit_todo, find_todo, list_todo_descriptions, wait_for_todo, wait_for_todo_to_disappear)


@pytest.mark.parametrize('test_name', ['Todo: Partial Edit'])
def test_todos_partial_edit(driver, todo_prefix):
    # Add todos
    todo1_description = f'{todo_prefix} test todo to edit'
    add_todo(driver, todo1_description)
    todo2_description = f'{todo_prefix} test todo to switch to'
    add_todo(driver, todo2_description)

    # Wait for todos to appear
    wait_for_todo(driver, todo1_description)
    wait_for_todo(driver, todo2_description)
    first_todo = find_todo(driver, todo1_description)
    second_todo = find_todo(driver, todo2_description)

    # Edit the first todo
    edit_description = f'{todo_prefix} edited description'
    edit_todo(first_todo, edit_description, submit=False)

    # Switch to editing the 2nd todo
    second_todo.click()

    # Wait for and verify that the 1st todo has a warning icon and shows original description
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, f'//div[text()="{todo1_description}"]/../following-sibling::div/following-sibling::div/div/div[text()="{WARNING_ICON_TEXT}"]'))
    )
    first_todo = find_todo(driver, todo1_description)
    warning_icon = first_todo.find_element(By.XPATH, f'//div[text()="{WARNING_ICON_TEXT}"]')
    assert warning_icon

    # Verify that 1st todo text is todo1_description
    expected_text = f'{UNCHECKED_ICON_TEXT}\n{todo1_description}\n{DELETE_ICON_TEXT}\n{WARNING_ICON_TEXT}'
    assert first_todo.text == expected_text

    # Return to editing the first todod
    first_todo.click()

    # Wait for todo1_description to be replaced by the input
    wait_for_todo_to_disappear(driver, todo1_description)

    # Verify that the input text is still edit_description
    todo_input = first_todo.find_element_by_tag_name('textarea')
    assert todo_input.get_attribute('value') == edit_description

    # Click cancel button
    cancel_button = first_todo.find_element(By.CSS_SELECTOR, 'div[data-testid="cancel-edit"]');
    cancel_button.click()

    # Wait for todo1_description to appeaer
    wait_for_todo(driver, todo1_description)

    # Verify that the original description is still there and the warning icon is gone
    first_todo = find_todo(driver, todo1_description)
    expected_text = f'{UNCHECKED_ICON_TEXT}\n{todo1_description}\n{DELETE_ICON_TEXT}'
    assert first_todo.text == expected_text
    warning_icons = first_todo.find_elements(By.XPATH, f'//div[text()="{WARNING_ICON_TEXT}"]')
    assert len(warning_icons) == 0
