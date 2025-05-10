import pytest

from helpers.label_helpers import (toggle_label_filter, toggle_label_filter_section,
                                  get_label_filter_status)
from helpers.todo_helpers import (add_todo, find_todos, wait_for_todo)


@pytest.mark.parametrize('test_name', ['URL: Filter URL Sync'])
def test_url_updates_with_filters(page, todo_prefix):
    # Add a todo to work with
    todo_description = f'{todo_prefix} test todo'
    add_todo(page, todo_description)
    wait_for_todo(page, todo_description)

    # Open label filter section
    toggle_label_filter_section(page)
    
    # Add a filter and verify URL updates
    toggle_label_filter(page, 'work')
    page.wait_for_url('**?labels=work')
    
    # Add another filter and verify URL updates
    toggle_label_filter(page, '5 minutes')
    page.wait_for_url('**?labels=work,5%20minutes')
    
    # Toggle a filter to inverted and verify URL updates
    toggle_label_filter(page, 'work')
    page.wait_for_url('**?labels=5%20minutes&inverted=work')
    
    # Remove all filters and verify URL returns to base
    toggle_label_filter(page, 'work')
    toggle_label_filter(page, '5 minutes')
    page.wait_for_url('**/todos')


@pytest.mark.parametrize('test_name', ['URL: Load Filters From URL'])
def test_load_filters_from_url(page, todo_prefix):
    # Add todos with different labels
    work_todo = f'{todo_prefix} work todo'
    add_todo(page, work_todo)
    wait_for_todo(page, work_todo)
    
    home_todo = f'{todo_prefix} home todo'
    add_todo(page, home_todo)
    wait_for_todo(page, home_todo)
    
    # Navigate to URL with filters
    base_url = page.url.split('?')[0]
    filter_url = f"{base_url}?labels=work"
    page.goto(filter_url)
    
    # Verify the filter is applied
    toggle_label_filter_section(page)
    assert get_label_filter_status(page, 'work') == 'Active'
    
    # Verify only the work todo is visible
    todos = find_todos(page, todo_prefix, partial=True)
    assert todos.count() == 1
    assert work_todo in todos.first.text_content()
    
    # Navigate to URL with inverted filter
    filter_url = f"{base_url}?inverted=work"
    page.goto(filter_url)
    
    # Verify the filter is applied as inverted
    assert get_label_filter_status(page, 'work') == 'Inverted'
    
    # Verify only the home todo is visible
    todos = find_todos(page, todo_prefix, partial=True)
    assert todos.count() == 1
    assert home_todo in todos.first.text_content()
