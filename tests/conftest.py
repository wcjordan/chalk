import os
import pytest
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.todo_helpers import delete_todo, find_todos


# Add details of failures so we can report to browserstack in the driver fixture
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)


def pytest_addoption(parser):
    parser.addoption("--server_domain", action="store", default="chalk.flipperkid.com")


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    server_domain = metafunc.config.option.server_domain
    if 'server_domain' in metafunc.fixturenames and server_domain is not None:
        metafunc.parametrize("server_domain", [server_domain])


@pytest.fixture
def todo_prefix():
    return 'Temp Test Prefix {} -'.format(random.randrange(10000))


@pytest.fixture
def driver(request, todo_prefix, test_name, server_domain):

    username = os.getenv("BROWSERSTACK_USERNAME")
    access_key = os.getenv("BROWSERSTACK_ACCESS_KEY")
    build_name = os.getenv("BROWSERSTACK_BUILD_NAME", 'Local')

    desired_cap = {
        'project': 'Chalk',
        'name': test_name,
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
        driver.get(f'http://{server_domain}/')
        if not "chalk" in driver.title:
            raise Exception("Unable to load page.")

        yield driver

        if hasattr(request.node, 'rep_setup') and request.node.rep_setup.failed:
            driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "Test setup failed."}}')
        elif hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
            driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "Executing test failed."}}')
        elif hasattr(request.node, 'rep_teardown') and request.node.rep_teardown.failed:
            driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "Test teardown failed."}}')
        else:
            driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "Test completed all steps without issue."}}')

    except Exception as e:
        failure_msg = 'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "An exception occurred while setting up the driver and loading the page."}}'
        driver.execute_script(failure_msg)

    finally:
        cancel_edit_buttons = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="cancel-edit"]');
        for btn in cancel_edit_buttons:
            btn.click()
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[data-testid="cancel-edit"]'))
        )

        todos_to_delete = find_todos(driver, todo_prefix, partial=True)
        for todo in todos_to_delete:
            delete_todo(todo)

        driver.quit()
