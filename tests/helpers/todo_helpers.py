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
