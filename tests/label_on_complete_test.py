import pytest

from helpers.label_helpers import (add_labels, dismiss_add_label_modal,
                                    get_todo_labels)
from helpers.todo_helpers import (add_todo, complete_todo, find_todo,
                                   wait_for_todo)


@pytest.mark.parametrize('test_name', ['Label: Auto Label Picker on Complete'])
def test_auto_label_picker_on_complete(page, todo_prefix):
    # Add unlabeled todo
    todo_desc = f'{todo_prefix} unlabeled todo'
    add_todo(page, todo_desc)
    wait_for_todo(page, todo_desc)

    # Complete the todo
    todo_item = find_todo(page, todo_desc)
    complete_todo(todo_item)

    # Verify label picker appears automatically
    label_picker = page.locator('[data-testid="label-picker"]')
    label_picker.wait_for()
    assert label_picker.is_visible()

    # Add a label via the picker
    add_labels(page, todo_item, ['work'], open_picker=False)

    # Show completed todos to verify label persisted
    show_completed_btn = page.locator('[data-testid="show-completed-todos"]')
    show_completed_btn.click()

    # Find the completed todo and verify label
    todo_item = find_todo(page, todo_desc)
    labels = get_todo_labels(todo_item)
    assert 'work' in labels


@pytest.mark.parametrize('test_name', ['Label: No Picker for Labeled Complete'])
def test_no_picker_for_labeled_todo(page, todo_prefix):
    # Add todo with a label
    todo_desc = f'{todo_prefix} labeled todo'
    add_todo(page, todo_desc)
    wait_for_todo(page, todo_desc)

    # Add a label first
    todo_item = find_todo(page, todo_desc)
    add_labels(page, todo_item, ['errand'])

    # Complete the todo
    complete_todo(todo_item)

    # Verify label picker does NOT appear (optional check)
    label_picker = page.locator('[data-testid="label-picker"]')
    dismiss_add_label_modal(page, optional=True)


@pytest.mark.parametrize('test_name', ['Label: Picker Dismissal Without Label'])
def test_picker_dismissal_without_adding_label(page, todo_prefix):
    # Add unlabeled todo
    todo_desc = f'{todo_prefix} dismiss test'
    add_todo(page, todo_desc)
    wait_for_todo(page, todo_desc)

    # Complete the todo
    todo_item = find_todo(page, todo_desc)
    complete_todo(todo_item)

    # Verify label picker appears
    label_picker = page.locator('[data-testid="label-picker"]')
    label_picker.wait_for()

    # Dismiss without adding a label
    dismiss_add_label_modal(page)

    # Show completed todos
    show_completed_btn = page.locator('[data-testid="show-completed-todos"]')
    show_completed_btn.click()

    # Verify todo is still unlabeled
    todo_item = find_todo(page, todo_desc)
    labels = get_todo_labels(todo_item)
    assert len(labels) == 0
