CHECKED_ICON_TEXT = '󰄲'
DELETE_ICON_TEXT = '󰧧'
LABELS_ICON_TEXT = '󰜢'
UNCHECKED_ICON_TEXT = '󰄱'
WARNING_ICON_TEXT = '󰀪'


def add_todo(page, description):
    add_input = page.locator('[data-testid="add-todo-input"]')
    add_input.fill(description)
    add_input.press('Enter')


def complete_todo(todo_item):
    complete_button = todo_item.locator('[data-testid="complete-todo"]')
    complete_button.click()


def delete_todo(todo_item):
    delete_button = todo_item.locator('[data-testid="delete-todo"]')
    delete_button.click()


def edit_todo(todo_item, new_description, submit=True):
    todo_item.click()
    todo_input = todo_item.locator('textarea')
    todo_input.click()
    todo_input.fill(new_description)
    if submit:
        todo_input.press('Enter')


def find_todo(page, description, partial=False):
    todos = find_todos(page, description, partial)
    assert len(todos) == 1
    return todos[0]


def find_todos(page, description, partial=False):
    # TODO clean this up w/ `has` / `has_text` when Playwright v19 is available
    # on Browserstack
    text_pattern = f'text={description}' if partial else f'text="{description}"'
    todo_items = page.locator(f'[data-testid="todo-list"] > div > div')

    matching_todos = []
    todo_count = todo_items.count()
    for todo_idx in range(todo_count):
        todo = todo_items.nth(todo_idx)
        if todo.locator(text_pattern).is_visible():
            matching_todos.append(todo)

    return matching_todos


def list_todo_descriptions(page, prefix):
    # TODO clean this up to use all_text_contents when find_todos is switched
    # to use `has` / `has_text`

    todo_items = find_todos(page, prefix, partial=True)
    return [item.locator('[data-testid="description-text"]').text_content()
            for item in todo_items]


def wait_for_todo(page, description):
    page.locator(f'text="{description}"').wait_for()


def wait_for_todo_to_disappear(page, description):
    page.locator(f'text="{description}"').wait_for(state='detached')
