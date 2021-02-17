import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.todo_helpers import add_todo, complete_todo, edit_todo, find_todo, list_todo_descriptions, wait_for_todo, wait_for_todo_to_disappear


WARNING_SVG_PATH = 'M569.517 440.013C587.975 472.007 564.806 512 527.94 512H48.054c-36.937 0-59.999-40.055-41.577-71.987L246.423 23.985c18.467-32.009 64.72-31.951 83.154 0l239.94 416.028zM288 354c-25.405 0-46 20.595-46 46s20.595 46 46 46 46-20.595 46-46-20.595-46-46-46zm-43.673-165.346l7.418 136c.347 6.364 5.609 11.346 11.982 11.346h48.546c6.373 0 11.635-4.982 11.982-11.346l7.418-136c.375-6.874-5.098-12.654-11.982-12.654h-63.383c-6.884 0-12.356 5.78-11.981 12.654z'


@pytest.mark.parametrize('test_name', ['Todo: Partial Edit'])
def test_todos_partial_edit(driver, todo_prefix):
    # Add todos
    todo1_description = "{} test todo to edit".format(todo_prefix)
    add_todo(driver, todo1_description)
    todo2_description = "{} test todo to switch to".format(todo_prefix)
    add_todo(driver, todo2_description)

    # Wait for todos to appear
    wait_for_todo(driver, todo1_description)
    wait_for_todo(driver, todo2_description)
    first_todo = find_todo(driver, todo1_description)
    second_todo = find_todo(driver, todo2_description)

    # Edit the first todo
    edit_description = "{} edited description".format(todo_prefix)
    edit_todo(first_todo, edit_description, submit=False)

    # Switch to editing the 2nd todo
    second_todo.click()

    # Wait for and verify that the 1st todo has a warning icon and shows original description
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//./span[text()="{}"]//following-sibling::*[name()="svg"]'.format(todo1_description)))
    )
    first_todo = find_todo(driver, todo1_description)
    warning_icon = first_todo.find_element_by_xpath('./child::*[name()="svg"]/*[name()="path"]')
    assert warning_icon.get_attribute('d') == WARNING_SVG_PATH

    # Verify that 1st todo text is todo1_description
    assert first_todo.find_element_by_xpath('./span').text == todo1_description

    # Return to editing the first todod
    first_todo.click()

    # Wait for todo1_description to be replaced by the input
    wait_for_todo_to_disappear(driver, todo1_description)

    # Verify that the input text is still edit_description
    todo_input = first_todo.find_element_by_tag_name('input')
    assert todo_input.get_attribute('value') == edit_description

    # Click clear text button
    item_svgs = first_todo.find_elements_by_tag_name('svg')
    assert len(item_svgs) >= 2
    item_svgs[1].click()

    # Wait for todo1_description to appeaer
    wait_for_todo(driver, todo1_description)

    # Verify that the original description is still there and the warning icon is gone
    first_todo = find_todo(driver, todo1_description)
    assert first_todo.find_element_by_xpath('./span').text == todo1_description
    warning_icons = first_todo.find_elements_by_xpath('./child::*[name()="svg"]')
    assert len(warning_icons) == 0
