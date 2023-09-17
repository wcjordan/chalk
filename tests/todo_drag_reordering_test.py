import pytest

from helpers.todo_helpers import (add_todo, drag_todo, list_todo_descriptions, wait_for_todo)


@pytest.mark.parametrize('test_name', ['Todo: Drag Reordering'])
def test_todo_drag_reordering(page, todo_prefix):
    # Add 10 todos
    for idx in range(7):
        add_todo(page, f'{todo_prefix} #{idx}')
    wait_for_todo(page, f'{todo_prefix} #6')

    # Verify initial todo order
    assert list_todo_descriptions(page, todo_prefix) == [f'{todo_prefix} #{idx}' for idx in range(7)]

    # Wait for the progressbar to go away
    page.locator(f'[role="progressbar"]').wait_for(state='detached')

    # Drag todo #6 up above #1 & verify the todo order
    drag_todo(page, f'{todo_prefix} #6', f'{todo_prefix} #1')
    assert list_todo_descriptions(page, todo_prefix) == [
        f'{todo_prefix} #0',
        f'{todo_prefix} #6',
        f'{todo_prefix} #1',
        f'{todo_prefix} #2',
        f'{todo_prefix} #3',
        f'{todo_prefix} #4',
        f'{todo_prefix} #5',
    ]

    # Drag todo #5 to the top (above #0) & verify the todo order
    drag_todo(page, f'{todo_prefix} #5', f'{todo_prefix} #0')
    assert list_todo_descriptions(page, todo_prefix) == [
        f'{todo_prefix} #5',
        f'{todo_prefix} #0',
        f'{todo_prefix} #6',
        f'{todo_prefix} #1',
        f'{todo_prefix} #2',
        f'{todo_prefix} #3',
        f'{todo_prefix} #4',
    ]

    # Drag #2 down below #3 & verify the todo order
    drag_todo(page, f'{todo_prefix} #2', f'{todo_prefix} #3')
    assert list_todo_descriptions(page, todo_prefix) == [
        f'{todo_prefix} #5',
        f'{todo_prefix} #0',
        f'{todo_prefix} #6',
        f'{todo_prefix} #1',
        f'{todo_prefix} #3',
        f'{todo_prefix} #2',
        f'{todo_prefix} #4',
    ]

    # Drag #6, but drop it unmoved & verify the todo order
    drag_todo(page, f'{todo_prefix} #6', f'{todo_prefix} #6')
    assert list_todo_descriptions(page, todo_prefix) == [
        f'{todo_prefix} #5',
        f'{todo_prefix} #0',
        f'{todo_prefix} #6',
        f'{todo_prefix} #1',
        f'{todo_prefix} #3',
        f'{todo_prefix} #2',
        f'{todo_prefix} #4',
    ]

    # Drag #2 to the end (below #4) & verify the todo order
    drag_todo(page, f'{todo_prefix} #2', f'{todo_prefix} #4')
    assert list_todo_descriptions(page, todo_prefix) == [
        f'{todo_prefix} #5',
        f'{todo_prefix} #0',
        f'{todo_prefix} #6',
        f'{todo_prefix} #1',
        f'{todo_prefix} #3',
        f'{todo_prefix} #4',
        f'{todo_prefix} #2',
    ]
