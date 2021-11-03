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
    label_picker = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="label-picker"]')
    chips = { chip.text: chip for chip in label_picker.find_elements(By.XPATH, './div') }

    for label in labels:
        chips[label].click()

    # Dismiss modal
    # Click offset from modal center to avoid dialog
    modal = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Close modal"]')
    ActionChains(driver).move_to_element(modal).move_by_offset(0, -100).click().perform()


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


def toggle_label_filter(driver, label):
    label_toggle = driver.find_element(By.XPATH, f'//div[@data-testid="label-filter"]//div[text()="{label}"]')
    label_toggle.click()
