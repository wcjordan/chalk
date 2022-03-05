import pytest

from helpers.todo_helpers import (DELETE_ICON_TEXT, LABELS_ICON_TEXT,
                                  UNCHECKED_ICON_TEXT, WARNING_ICON_TEXT,
                                  add_todo, edit_todo, find_todo, wait_for_todo,
                                  wait_for_todo_to_disappear)


@pytest.mark.parametrize('test_name', ['Todo: Partial Edit'])
def test_todos_partial_edit(page, todo_prefix):
    # Add todos
    todo1_description = f'{todo_prefix} test todo to edit'
    add_todo(page, todo1_description)
    todo2_description = f'{todo_prefix} test todo to switch to'
    add_todo(page, todo2_description)

    # Wait for todos to appear
    wait_for_todo(page, todo1_description)
    wait_for_todo(page, todo2_description)
    first_todo = find_todo(page, todo1_description)
    second_todo = find_todo(page, todo2_description)

    # Edit the first todo
    edit_description = f'{todo_prefix} edited description'
    edit_todo(first_todo, edit_description, submit=False)

    # Switch to editing the 2nd todo
    second_todo.click()

    # Wait for and verify that the 1st todo has a warning icon and shows original description
    xpath_selector = f'xpath=//div[text()="{todo1_description}"]/../following-sibling::div/following-sibling::div/div/div[text()="{WARNING_ICON_TEXT}"]'
    page.locator(xpath_selector).wait_for()
    first_todo = find_todo(page, todo1_description)
    warning_icon = first_todo.locator(f'text="{WARNING_ICON_TEXT}"')
    assert warning_icon.count() == 1

    # Verify that 1st todo text is todo1_description
    expected_text = f'{UNCHECKED_ICON_TEXT}{todo1_description}{LABELS_ICON_TEXT}{DELETE_ICON_TEXT}{WARNING_ICON_TEXT}'
    assert first_todo.text_content() == expected_text

    # Return to editing the first todo
    first_todo.click()

    # Wait for todo1_description to be replaced by the input
    wait_for_todo_to_disappear(page, todo1_description)

    # Verify that the input text is still edit_description
    todo_input = first_todo.locator('textarea')
    assert todo_input.input_value() == edit_description

    # Click cancel button
    cancel_button = first_todo.locator('[data-testid="cancel-edit"]')
    cancel_button.click()

    # Wait for todo1_description to appeaer
    wait_for_todo(page, todo1_description)

    # Verify that the original description is still there and the warning icon is gone
    first_todo = find_todo(page, todo1_description)
    expected_text = f'{UNCHECKED_ICON_TEXT}{todo1_description}{LABELS_ICON_TEXT}{DELETE_ICON_TEXT}'
    assert first_todo.text_content() == expected_text
    warning_icons = first_todo.locator(f'text="{WARNING_ICON_TEXT}"]')
    assert warning_icons.count() == 0
