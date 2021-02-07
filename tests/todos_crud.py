import json
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def _has_span_child_matching_text(parent, text):
    children = parent.find_elements_by_tag_name('span')
    return any(item.text == text for item in children)


username = os.getenv("BROWSERSTACK_USERNAME")
access_key = os.getenv("BROWSERSTACK_ACCESS_KEY")
build_name = os.getenv("BROWSERSTACK_BUILD_NAME", 'Local')

desired_cap = {
 'project': 'Chalk',
 'name': 'Todo: Create, Update, Delete',
 'build': build_name,

 'browser': 'Chrome',
 'browser_version': 'latest',

 'os_version': 'Catalina',
 'resolution': '1920x1080',
 'os': 'OS X',

 'browserstack.user': username,
 'browserstack.key': access_key
}
driver = webdriver.Remote(
    command_executor='https://hub-cloud.browserstack.com/wd/hub',
    desired_capabilities=desired_cap)

try:
    # Load page
    driver.get("http://chalk.flipperkid.com/")
    if not "chalk" in driver.title:
        raise Exception("Unable to load page.")

    # Add todo
    todo_text = "Temp - test todo"
    add_input = driver.find_element_by_id("add-todo-input")
    add_input.send_keys(todo_text)
    add_input.send_keys(Keys.RETURN)

    # Find todo & verify
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//span[text()="{}"]'.format(todo_text)))
    )
    todo_list = driver.find_element_by_id('todo-list')
    todo_items = todo_list.find_elements_by_tag_name('div')
    found_items = [ item for item in todo_items if _has_span_child_matching_text(item, todo_text) ]
    print('Found {} todos, expecting 1 match'.format(len(found_items)))
    todo_item = found_items[0]

    # Edit todo
    updated_todo_text = "Temp - test todo updated"
    todo_item.click()
    todo_input = todo_item.find_element_by_tag_name('input')
    todo_input.click()
    todo_input.send_keys(updated_todo_text)
    todo_input.send_keys(Keys.RETURN)

    # Verify
    def text_updated(driver):
        if not EC.invisibility_of_element_located((By.XPATH, '//span[text()="{}"]'.format(todo_text)))(driver):
            print('found old text')
            return False
        if not EC.presence_of_element_located((By.XPATH, '//span[text()="{}"]'.format(updated_todo_text)))(driver):
            print('didnt find updated text')
            return False
        return True

    WebDriverWait(driver, 10).until(text_updated)
    todo_list = driver.find_element_by_id('todo-list')
    todo_items = todo_list.find_elements_by_tag_name('div')
    found_items = [ item for item in todo_items if _has_span_child_matching_text(item, todo_text) ]
    print('Found {} todos, expecting 0 matches'.format(len(found_items)))
    found_items = [ item for item in todo_items if _has_span_child_matching_text(item, updated_todo_text) ]
    print('Found {} todos, expecting 1 match'.format(len(found_items)))
    todo_item = found_items[0]

    # Delete todo
    item_svgs = found_items[0].find_elements_by_tag_name('svg')
    print('Found {} svgs, expecting 2'.format(len(item_svgs)))
    item_svgs[1].click()

    # Verify
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.XPATH, '//span[text()="{}"]'.format(updated_todo_text)))
    )
    todo_list = driver.find_element_by_id('todo-list')
    todo_items = todo_list.find_elements_by_tag_name('div')
    found_items = [ item for item in todo_items[1:] if item.find_element_by_tag_name('span').text == updated_todo_text ]
    print('Found {} todos, expecting 0 matches'.format(len(found_items)))

    # Setting the status of test as 'passed' or 'failed'
    driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "Todo created!"}}')

except Exception as e:
    failure_msg = 'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "An exception occurred during the test driving"}}'
    driver.execute_script(failure_msg)
    raise e

finally:
    driver.quit()
