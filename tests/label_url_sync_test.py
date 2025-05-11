import pytest

from helpers.label_helpers import (add_todo_w_labels, toggle_label_filter,
                                   toggle_label_filter_section, get_label_filter_status)
from helpers.todo_helpers import (list_todo_descriptions, wait_for_todo_to_disappear)
from helpers.work_context_helpers import (get_active_work_context)


@pytest.mark.parametrize('test_name', ['Label: Filter URL Sync'])
def test_url_updates_with_filters(page, todo_prefix):
    base_url = page.url.split('?')[0]

    # Open label filter section
    toggle_label_filter_section(page)

    # Add a filter and verify URL updates
    toggle_label_filter(page, 'work')
    assert page.url == f'{base_url}?labels=work'

    # Add another filter and verify URL updates
    toggle_label_filter(page, '5 minutes')
    assert page.url == f'{base_url}?labels=work%2C5+minutes'

    # Toggle a filter to inverted and verify URL updates
    toggle_label_filter(page, 'work')
    assert page.url == f'{base_url}?labels=5+minutes&inverted=work'

    # Remove all filters and verify URL returns to base
    toggle_label_filter(page, 'work')
    toggle_label_filter(page, '5 minutes')
    toggle_label_filter(page, '5 minutes')
    assert page.url == base_url


@pytest.mark.parametrize('test_name', ['Label: Load Filters From URL'])
def test_load_filters_from_url(page, todo_prefix):
    # Add todos with different labels
    work_todo_desc = f'{todo_prefix} test todo - work'
    add_todo_w_labels(page, work_todo_desc, ['work'])

    home_todo_desc = f'{todo_prefix} test todo - home'
    add_todo_w_labels(page, home_todo_desc, ['home'])

    # Navigate to URL with filters
    base_url = page.url.split('?')[0]
    filter_url = f"{base_url}?labels=work"
    page.goto(filter_url)

    # Verify the filter is applied & only the work todo is visible
    wait_for_todo_to_disappear(page, home_todo_desc)
    todo_descriptions = list_todo_descriptions(page, todo_prefix)
    assert todo_descriptions == [work_todo_desc]
    toggle_label_filter_section(page)
    assert get_label_filter_status(page, 'work') == 'Active'

    # Navigate to URL with inverted filter
    filter_url = f"{base_url}?inverted=work"
    page.goto(filter_url)

    # Verify the filter is applied as inverted
    wait_for_todo_to_disappear(page, work_todo_desc)
    todo_descriptions = list_todo_descriptions(page, todo_prefix)
    assert todo_descriptions == [home_todo_desc]
    toggle_label_filter_section(page)
    assert get_label_filter_status(page, 'work') == 'Inverted'

    # Navigate to default URL
    page.goto(base_url)

    # Verify navigating to the default URL uses the Inbox work context
    todo_descriptions = list_todo_descriptions(page, todo_prefix)
    assert todo_descriptions == []
    assert get_active_work_context(page) == 'Inbox'
    toggle_label_filter_section(page)
    assert get_label_filter_status(page, 'work') == 'Disabled'
    assert get_label_filter_status(page, 'Unlabeled') == 'Active'
