from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.todo_helpers import (add_todo, find_todo, wait_for_todo)


def _add_labels(driver, todo_item, labels):
    # Open label picker
    label_button = todo_item.find_element(By.CSS_SELECTOR, 'div[data-testid="label-todo"]')
    label_button.click()

    # Click specified label chips
    for label in labels:
        label_picker = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="label-picker"]')
        chip = label_picker.find_element(By.XPATH, f'.//div[text()="{label}"]')
        chip.click()

    dismiss_add_label_modal(driver)


def add_todo_w_labels(driver, todo_description, labels):
    # Add todos
    add_todo(driver, todo_description)

    # Wait for todo to appear`
    wait_for_todo(driver, todo_description)
    todo_item = find_todo(driver, todo_description)

    # Add labels
    _add_labels(driver, todo_item, labels)

    # Wait for selected labels to appear
    todo_list = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="todo-list"]')
    for item in labels:
        xpath_selector = f'./div/div[.//div[text()="{todo_description}"] and .//div[text()="{item}"]]'
        WebDriverWait(todo_list, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath_selector))
        )

    return todo_item


def dismiss_add_label_modal(driver, optional=False):
    # Click offset from modal center to avoid dialog
    modals = driver.find_elements(By.CSS_SELECTOR, 'div[aria-label="Close modal"]')
    if modals or not optional:
        assert len(modals) == 1
        ActionChains(driver).move_to_element(modals[0]).move_by_offset(0, -100).click().perform()


def toggle_label_filter(driver, label):
    label_toggle = driver.find_element(By.XPATH, f'//div[@data-testid="label-filter"]//div[text()="{label}"]')
    label_toggle.click()
