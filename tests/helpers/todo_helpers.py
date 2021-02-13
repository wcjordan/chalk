from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def add_todo(driver, description):
    add_input = driver.find_element_by_id("add-todo-input")

    # Clear input
    add_input.send_keys(Keys.COMMAND + "a")
    add_input.send_keys(Keys.DELETE)

    # Add new todo
    add_input.send_keys(description)
    add_input.send_keys(Keys.RETURN)


def complete_todo(todo_item):
    item_svgs = todo_item.find_elements_by_tag_name('svg')
    assert len(item_svgs) == 2
    item_svgs[0].click()


def delete_todo(todo_item):
    item_svgs = todo_item.find_elements_by_tag_name('svg')
    assert len(item_svgs) == 2
    item_svgs[1].click()


def edit_todo(todo_item, new_description):
    todo_item.click()
    todo_input = todo_item.find_element_by_tag_name('input')
    todo_input.click()
    todo_input.send_keys(new_description)
    todo_input.send_keys(Keys.RETURN)


def find_todos(driver, description, partial=False):
    def _has_span_child_matching_text(parent):
        def _comparator(item):
            if partial:
                return item.text.startswith(description)
            return item.text == description

        children = parent.find_elements_by_tag_name('span')
        return any(_comparator(item) for item in children)

    todo_list = driver.find_element_by_id('todo-list')
    todo_items = todo_list.find_elements_by_tag_name('div')
    return [ item for item in todo_items if _has_span_child_matching_text(item) ]


def list_todo_descriptions(driver, prefix):
    todo_items = find_todos(driver, prefix, partial=True)
    return [ item.find_element_by_tag_name('span').text for item in todo_items ]
