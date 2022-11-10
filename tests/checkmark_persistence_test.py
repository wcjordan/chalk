import pytest

from helpers.todo_helpers import (CHECKED_ICON_TEXT, DELETE_ICON_TEXT,
                                  LABELS_ICON_TEXT, add_todo, complete_todo,
                                  find_todo, list_todo_descriptions,
                                  wait_for_todo)


@pytest.mark.parametrize('test_name', ['Todo: Checkmark Persistence'])
def test_todos_checkmark_persistence(page, todo_prefix):
    # Add todos
    todo1_description = f'{todo_prefix} 1st test todo'
    add_todo(page, todo1_description)
    todo2_description = f'{todo_prefix} 2nd test todo'
    add_todo(page, todo2_description)

    # Wait for todos to appear
    wait_for_todo(page, todo1_description)
    wait_for_todo(page, todo2_description)
    first_todo = find_todo(page, todo1_description)

    # Verify that the 1st todo appears before 2nd todo
    todo_descriptions = list_todo_descriptions(page, todo_prefix)
    assert todo_descriptions == [todo1_description, todo2_description]

    # Check off the 1st todo
    complete_todo(first_todo)

    # Wait for and verify that checkbox appears checked
    checked_selector = f'div:has([data-testid="complete-todo"]):has-text("{CHECKED_ICON_TEXT}") + div:has-text("{todo1_description}")'
    page.locator(checked_selector).wait_for()

    first_todo = find_todo(page, todo1_description)
    first_todo_checkmark = first_todo.locator(f'text="{CHECKED_ICON_TEXT}"')
    assert first_todo_checkmark.count() == 1
    expected_text = f'{CHECKED_ICON_TEXT}{todo1_description}{LABELS_ICON_TEXT}{DELETE_ICON_TEXT}'
    assert first_todo.text_content() == expected_text

    # Verify that the 2nd todo appears before 1st todo once the 1st is completed
    todo_descriptions = list_todo_descriptions(page, todo_prefix)
    assert todo_descriptions == [todo2_description, todo1_description]
