import pytest

from selenium.webdriver.common.by import By

from helpers.label_helpers import add_todo_w_labels


@pytest.mark.parametrize('test_name', ['Label: Label Persistence'])
def test_label_persistence(driver, todo_prefix):
    # Add todo w/ 5 min & errand labels
    todo_description = f'{todo_prefix} test todo'
    labels = ['errand', '5 minutes']
    todo_item = add_todo_w_labels(driver, todo_description, labels)

    # Verify labels are selected
    todo_labels_container = todo_item.find_element(By.CSS_SELECTOR, 'div[data-testid="todo-labels"]')
    todo_labels = [ item.text for item in todo_labels_container.find_elements(By.XPATH, './div') ]
    assert todo_labels == labels
