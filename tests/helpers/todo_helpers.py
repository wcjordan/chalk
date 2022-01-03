from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


CHECKED_ICON_TEXT = '󰄲'
DELETE_ICON_TEXT = '󰧧'
LABELS_ICON_TEXT = '󰜢'
UNCHECKED_ICON_TEXT = '󰄱'
WARNING_ICON_TEXT = '󰀪'


def add_todo(driver, description):
    add_input = driver.find_element(By.CSS_SELECTOR, 'textarea[data-testid="add-todo-input"]')

    # Clear input
    add_input.send_keys(Keys.COMMAND + "a")
    add_input.send_keys(Keys.DELETE)

    # Add new todo
    add_input.send_keys(description)
    add_input.send_keys(Keys.RETURN)


def complete_todo(todo_item):
    complete_button = todo_item.find_element(By.CSS_SELECTOR, 'div[data-testid="complete-todo"]')
    complete_button.click()


def delete_todo(todo_item):
    delete_button = todo_item.find_element(By.CSS_SELECTOR, 'div[data-testid="delete-todo"]')
    delete_button.click()


def edit_todo(todo_item, new_description, submit=True):
    todo_item.click()
    todo_input = todo_item.find_element_by_tag_name('textarea')
    todo_input.click()
    todo_input.send_keys(new_description)
    if submit:
        todo_input.send_keys(Keys.RETURN)


def find_todo(driver, description, partial=False):
    todos = find_todos(driver, description, partial)
    assert len(todos) == 1
    return todos[0]


def find_todos(driver, description, partial=False):
    def _has_div_child_matching_text(parent):
        def _comparator(item):
            if partial:
                return item.text.startswith(description)
            return item.text == description

        children = parent.find_elements_by_tag_name('div')
        return any(_comparator(item) for item in children)

    todo_list = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="todo-list"]').find_element(By.XPATH, './div');
    todo_items = todo_list.find_elements(By.XPATH, './div')
    return [ item for item in todo_items if _has_div_child_matching_text(item) ]


def list_todo_descriptions(driver, prefix):
    todo_items = find_todos(driver, prefix, partial=True)
    return [ item.find_element(By.CSS_SELECTOR, 'div[data-testid="description-text"]').text for item in todo_items ]


def wait_for_todo(driver, description):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, f'//div[text()="{description}"]'))
    )


def wait_for_todo_to_disappear(driver, description):
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.XPATH, f'//div[text()="{description}"]'))
    )
