import pytest

from helpers.todo_helpers import add_todo, delete_todo, find_todo, wait_for_todo


@pytest.mark.parametrize('test_name', ['Todo: Clickable Links'])
def test_todo_clickable_links(page, todo_prefix):
    """Test that URLs in todo descriptions are rendered as clickable links"""

    # Add todo with a URL
    todo_description = f'{todo_prefix} Check https://example.com for info'
    add_todo(page, todo_description)

    # Wait for todo to be created
    wait_for_todo(page, todo_description)
    todo_item = find_todo(page, todo_description)

    # Verify the link is rendered
    # The LinkifiedText component should create a link with testID pattern: description-text-link-{index}
    link = todo_item.locator('[data-testid^="description-text-link-"]')
    assert link.count() == 1, "Expected to find one link in the todo description"

    # Verify the link text is the URL
    assert link.text_content() == 'https://example.com'

    # Cleanup
    delete_todo(todo_item)


@pytest.mark.parametrize('test_name', ['Todo: Multiple Clickable Links'])
def test_todo_multiple_links(page, todo_prefix):
    """Test that multiple URLs in a todo description are all rendered as clickable links"""

    # Add todo with multiple URLs
    todo_description = f'{todo_prefix} Visit https://example.com or http://test.com'
    add_todo(page, todo_description)

    # Wait for todo to be created
    wait_for_todo(page, todo_description)
    todo_item = find_todo(page, todo_description)

    # Verify both links are rendered
    links = todo_item.locator('[data-testid^="description-text-link-"]')
    assert links.count() == 2, "Expected to find two links in the todo description"

    # Verify the link texts
    link_texts = links.all_text_contents()
    assert 'https://example.com' in link_texts
    assert 'http://test.com' in link_texts

    # Cleanup
    delete_todo(todo_item)


@pytest.mark.parametrize('test_name', ['Todo: Plain Text Without Links'])
def test_todo_without_links(page, todo_prefix):
    """Test that todos without URLs render normally without link elements"""

    # Add todo without any URLs
    todo_description = f'{todo_prefix} Just plain text'
    add_todo(page, todo_description)

    # Wait for todo to be created
    wait_for_todo(page, todo_description)
    todo_item = find_todo(page, todo_description)

    # Verify no links are rendered
    links = todo_item.locator('[data-testid^="description-text-link-"]')
    assert links.count() == 0, "Expected no links in plain text todo"

    # Verify the description text is still visible
    description_text = todo_item.locator('[data-testid="description-text"]')
    assert description_text.count() == 1
    assert todo_description in description_text.text_content()

    # Cleanup
    delete_todo(todo_item)
