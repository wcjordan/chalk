import time

CHECKED_ICON_TEXT = '󰄲'
DELETE_ICON_TEXT = '󰧧'
LABELS_ICON_TEXT = '󰜢'
UNCHECKED_ICON_TEXT = '󰄱'
WARNING_ICON_TEXT = '󰀪'


def add_todo(page, description):
    add_input = page.locator('[data-testid="add-todo-input"]')
    add_input.fill(description)
    add_input.press('Enter')


def cancel_edit(page, todo):
    cancel_button = todo.locator('[data-testid="cancel-edit"]')
    cancel_button.click()


def complete_todo(todo_item):
    complete_button = todo_item.locator('[data-testid="complete-todo"]')
    complete_button.click()


def delete_todo(todo_item):
    delete_button = todo_item.locator('[data-testid="delete-todo"]')
    delete_button.click()


def edit_todo(page, todo_item, new_description, submit=True):
    todo_item.click()
    todo_input = todo_item.locator('textarea')
    todo_input.click()
    todo_input.fill(new_description)
    if submit:
        # Need to re-find todo since locator was on the old description
        find_todo(page, new_description).locator('textarea').press('Enter')


def find_todo(page, description, partial=False):
    todos = find_todos(page, description, partial)
    assert todos.count() == 1
    return todos.first


def find_todos(page, description, partial=False):
    text_pattern = f'text={description}' if partial else f'text="{description}"'
    return page.locator(f'[data-testid="todo-list"] > div > div',
                        has=page.locator(text_pattern))


def list_todo_descriptions(page, prefix):
    return find_todos(page, prefix, partial=True).locator(
        '[data-testid="description-text"]').all_text_contents()


def wait_for_todo(page, description):
    page.locator(f'text="{description}"').wait_for()


def wait_for_todo_to_disappear(page, description):
    page.locator(f'text="{description}"').wait_for(state='detached')


def drag_todo(page, todo_item, relative_todo_item):
    if isinstance(todo_item, str):
        todo_item = find_todo(page, todo_item)
    if isinstance(relative_todo_item, str):
        relative_todo_item = find_todo(page, relative_todo_item)

    start_box = todo_item.bounding_box()
    todo_item.hover()
    page.mouse.down()
    time.sleep(0.5)

    # For some reason the Pan Gesture Handler only reacts to the N-1 steps
    # so we use 10 steps and overshoot the target to land as close as possible to the actual target y
    target_box = relative_todo_item.bounding_box()
    target_y = target_box['y'] + target_box['height'] / 2
    start_y = start_box['y'] + start_box['height'] / 2
    overshoot_y = (target_y - start_y) * 1 / 11
    if overshoot_y == 0:
        overshoot_y = 10
    page.mouse.move(target_box['x'], target_box['y'] + target_box['height'] / 2 + overshoot_y, steps=10)

    page.mouse.up()
    time.sleep(1)
