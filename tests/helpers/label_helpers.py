from helpers.todo_helpers import (add_todo, find_todo, wait_for_todo)


def add_labels(page, todo_item, labels, dismiss_picker=True, open_picker=True):
    # Open label picker
    if open_picker:
        label_button = todo_item.locator('[data-testid="label-todo"]')
        label_button.click()

    # Click specified label chips
    for label in labels:
        chip = page.locator(f'[data-testid="label-picker"] :text-is("{label}")')
        chip.click()
        # Wait for selected label to appear
        todo_item.locator(f'text="{label}"').wait_for()

    if dismiss_picker:
        dismiss_add_label_modal(page)


def add_todo_w_labels(page, todo_description, labels):
    # Add todos
    add_todo(page, todo_description)

    # Wait for todo to appear`
    wait_for_todo(page, todo_description)
    todo_item = find_todo(page, todo_description)

    # Add labels
    add_labels(page, todo_item, labels)
    return todo_item


def clear_label_filters(page):
    selected_chips = page.locator(f'[data-testid="label-filter"] [aria-selected=true]')
    chip_elements = selected_chips.element_handles()
    for chip in chip_elements:
        chip.click()


def dismiss_add_label_modal(page, optional=False):
    modals = page.locator('[aria-label="Close modal"]')
    modals_count = modals.count()
    if modals_count or not optional:
        assert modals_count == 1
        # Click offset from modal center to avoid dialog
        modals.first.click(position={'x': 0, 'y': 0})


def toggle_label_filter(page, label):
    label_toggle = page.locator(f'[data-testid="label-filter"] :text-is("{label}")')
    label_toggle.click()
