import pytest

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.todo_helpers import (add_todo, find_todo, wait_for_todo)


@pytest.mark.parametrize('test_name', ['Label: Label Persistence'])
def test_label_persistence(driver, todo_prefix):
    # Add todos
    todo_description = f'{todo_prefix} test todo'
    add_todo(driver, todo_description)

    # Wait for todo to appear
    wait_for_todo(driver, todo_description)
    todo_item = find_todo(driver, todo_description)

    # Add 5 min & errand labels
    labels = ['errand', '5 minutes']
    _add_labels(driver, todo_item, labels)

    # Wait for and verify labels are selected
    for item in labels:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f'//div[@data-testid="todo-labels"]//div[text()="{item}"]'))
        )

    todo_labels_container = todo_item.find_element(By.CSS_SELECTOR, 'div[data-testid="todo-labels"]')
    todo_labels = [ item.text for item in todo_labels_container.find_elements(By.XPATH, './div') ]
    assert todo_labels == labels


def _add_labels(driver, todo_item, labels):
    # Open label picker
    label_button = todo_item.find_element(By.CSS_SELECTOR, 'div[data-testid="label-todo"]');
    label_button.click()

    # Click specified label chips
    label_picker = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="label-picker"]');
    chips = { chip.text: chip for chip in label_picker.find_elements(By.XPATH, './div') }

    for label in labels:
        chips[label].click()

    # Dismiss modal
    # Click offset from modal center to avoid dialog
    modal = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Close modal"]')
    ActionChains(driver).move_to_element(modal).move_by_offset(0, -100).click().perform()
