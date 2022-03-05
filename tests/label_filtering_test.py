import pytest

from helpers.label_helpers import add_todo_w_labels, toggle_label_filter
from helpers.todo_helpers import (list_todo_descriptions, wait_for_todo,
                                  wait_for_todo_to_disappear)


@pytest.mark.parametrize('test_name', ['Label: Label Filtering'])
def test_label_filtering(page, todo_prefix):
    # Add todos w/ labels
    todo_5min_low_desc = f'{todo_prefix} test todo - 5min low energy'
    add_todo_w_labels(page, todo_5min_low_desc, ['low-energy', '5 minutes'])

    todo_25min_low_desc = f'{todo_prefix} test todo - 25min low energy'
    add_todo_w_labels(page, todo_25min_low_desc, ['low-energy', '25 minutes'])

    todo_25min_high_desc = f'{todo_prefix} test todo - 25min high energy'
    add_todo_w_labels(page, todo_25min_high_desc, ['high-energy', '25 minutes'])

    # Select low-energy & verify 2 low-energy todos shown
    toggle_label_filter(page, 'low-energy')
    wait_for_todo_to_disappear(page, todo_25min_high_desc)
    todo_descriptions = list_todo_descriptions(page, todo_prefix)
    assert todo_descriptions == [todo_5min_low_desc, todo_25min_low_desc]

    # Select 25 minutes & verify 1 low-energy 25 minutes todos shown
    toggle_label_filter(page, '25 minutes')
    wait_for_todo_to_disappear(page, todo_5min_low_desc)
    todo_descriptions = list_todo_descriptions(page, todo_prefix)
    assert todo_descriptions == [todo_25min_low_desc]

    # Select 5 minutes & verify no todos shown
    toggle_label_filter(page, '5 minutes')
    wait_for_todo_to_disappear(page, todo_25min_low_desc)
    todo_descriptions = list_todo_descriptions(page, todo_prefix)
    assert todo_descriptions == []

    # Unselect 5 minutes & verify 1 low-energy 25 minutes todos shown
    toggle_label_filter(page, '5 minutes')
    wait_for_todo(page, todo_25min_low_desc)
    todo_descriptions = list_todo_descriptions(page, todo_prefix)
    assert todo_descriptions == [todo_25min_low_desc]

    # Unselect low-energy & verify 2 25 minutes todos shown
    toggle_label_filter(page, 'low-energy')
    wait_for_todo(page, todo_25min_high_desc)
    todo_descriptions = list_todo_descriptions(page, todo_prefix)
    assert todo_descriptions == [todo_25min_low_desc, todo_25min_high_desc]
