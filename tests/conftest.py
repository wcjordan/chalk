import json
import logging
import os
import pytest
import random
import urllib.parse

from playwright.sync_api import sync_playwright

from helpers.label_helpers import clear_label_filters, dismiss_add_label_modal
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
    parser.addoption("--server_domain", action="store")


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    server_domain = metafunc.config.option.server_domain
    if 'server_domain' in metafunc.fixturenames and server_domain is not None:
        metafunc.parametrize("server_domain", [server_domain])


@pytest.fixture
def todo_prefix():
    return 'Temp Test Prefix {} -'.format(random.randrange(10000))


@pytest.fixture(scope="session")
def playwright():
    pw = sync_playwright().start()
    yield pw
    pw.stop()


@pytest.fixture
def page(request, playwright, todo_prefix, test_name, server_domain):
    username = os.getenv("BROWSERSTACK_USERNAME")
    access_key = os.getenv("BROWSERSTACK_ACCESS_KEY")
    refresh_token = os.getenv("OAUTH_REFRESH_TOKEN")
    build_name = os.getenv("BROWSERSTACK_BUILD_NAME", 'Local')

    desired_cap = {
        'project': 'Chalk',
        'name': test_name,
        'build': build_name,

        'browser': 'chrome',
        'browser_version': 'latest',

        'os_version': 'Monterey',
        'resolution': '1920x1080',
        'os': 'OS X',

        'browserstack.username': username,
        'browserstack.accessKey': access_key,
        'client.playwrightVersion': '1.19.1',
    }

    browser = None
    connect_exception = None
    for attempt in range(3):
        try:
            browser = playwright.chromium.connect(f'wss://cdp.browserstack.com/playwright?caps={urllib.parse.quote(json.dumps(desired_cap, separators=(",", ":")))}')
            break
        except playwright._impl._api_types.Error as ex:
            connect_exception = ex
    if not browser:
        raise connect_exception

    page = browser.new_page()
    try:
        # Load page
        page.goto(f'http://{server_domain}/')
        if "accounts.google.com" in page.url:
            page.goto(f'http://{server_domain}/api/todos/auth_callback/?ci_refresh=true&code={refresh_token}')

        if not "chalk" in page.title():
            raise Exception("Unable to load page.")

        yield page

        if hasattr(request.node, 'rep_setup') and request.node.rep_setup.failed:
            set_session_status(page, 'failed', "Test setup failed.")
        elif hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
            set_session_status(page, 'failed', "Executing test failed.")
        elif hasattr(request.node, 'rep_teardown') and request.node.rep_teardown.failed:
            set_session_status(page, 'failed', "Test teardown failed.")
        else:
            set_session_status(page, 'passed',
                               "Test completed all steps without issue.")

    except Exception:
        logging.exception('Failed to execute test')
        set_session_status(page, 'failed', "An exception occurred while setting up the driver and loading the page.")

    finally:
        try:
            dismiss_add_label_modal(page, optional=True)
            clear_label_filters(page)

            cancel_edit_buttons = page.locator('[data-testid="cancel-edit"]').element_handles()
            for cancel_edit_btn in cancel_edit_buttons:
                cancel_edit_btn.click()
            page.locator('[data-testid="cancel-edit"]').wait_for(state='detached')

            todos_to_delete = find_todos(page, todo_prefix, partial=True)
            for todo in reversed(todos_to_delete):
                # reverse list so locators are still valid as later items are removed
                delete_todo(todo)
        except Exception:
            logging.exception('Failed to cleanup test')

        browser.close()


def set_session_status(page, status, reason):
    command = f'browserstack_executor: {{"action": "setSessionStatus", "arguments": {{"status": "{status}", "reason": "{reason}"}}}}'
    page.evaluate("() => {}", command)
