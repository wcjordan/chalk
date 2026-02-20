import pytest

from helpers.todo_helpers import (
    CHECKED_ICON_TEXT,
    DELETE_ICON_TEXT,
    LABELS_ICON_TEXT,
    add_todo,
    complete_todo,
    find_todo,
    list_todo_descriptions,
    wait_for_todo,
)
from helpers.label_helpers import dismiss_add_label_modal


@pytest.mark.parametrize("test_name", ["Todo: Checkmark Persistence"])
def test_todos_checkmark_persistence(page, todo_prefix):
    # Add todos
    todo1_description = f"{todo_prefix} 1st test todo"
    add_todo(page, todo1_description)
    todo2_description = f"{todo_prefix} 2nd test todo"
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

    # Dismiss without adding a label
    dismiss_add_label_modal(page)

    # Show completed todos, then
    # Wait for and verify that checkbox appears checked
    show_completed_btn = page.locator('[data-testid="show-completed-todos"]')
    show_completed_btn.click()

    # Wait for todo to be marked as completed and message bar to disappear
    page.locator('[data-testid="message-bar"]').wait_for()
    page.locator('[data-testid="message-bar"]').wait_for(state="detached")

    checked_selector = (
        f'[data-testid="card"]:has-text("{CHECKED_ICON_TEXT}{todo1_description}")'
    )
    page.locator(checked_selector).wait_for()

    first_todo = find_todo(page, todo1_description)
    first_todo_checkmark = first_todo.locator(f'text="{CHECKED_ICON_TEXT}"')
    assert first_todo_checkmark.count() == 1
    expected_text = (
        f"{CHECKED_ICON_TEXT}{todo1_description}{LABELS_ICON_TEXT}{DELETE_ICON_TEXT}"
    )
    assert first_todo.text_content() == expected_text

    # Verify that the 2nd todo appears before 1st todo once the 1st is completed
    todo_descriptions = list_todo_descriptions(page, todo_prefix)
    assert todo_descriptions == [todo2_description, todo1_description]
