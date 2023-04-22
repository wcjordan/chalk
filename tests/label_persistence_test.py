import pytest

from helpers.label_helpers import (add_todo_w_labels, toggle_label_filter)


@pytest.mark.parametrize('test_name', ['Label: Label Persistence'])
def test_label_persistence(page, todo_prefix):
    # Remove default filter
    toggle_label_filter(page, 'Unlabeled')

    # Add todo w/ 5 min & errand labels
    todo_description = f'{todo_prefix} test todo'
    labels = ['errand', '5 minutes']
    todo_item = add_todo_w_labels(page, todo_description, labels)

    # Verify labels are selected
    todo_labels = todo_item.locator('[data-testid="todo-labels"] > div').all_text_contents()
    assert todo_labels == labels
