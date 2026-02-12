import pytest

from helpers.todo_helpers import add_todo, find_todo, wait_for_todo


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
    assert 'https://example.com' == link_texts[0]
    assert 'http://test.com' == link_texts[1]

    # Click the first link and verify it opens the correct URL in a new tab
    with page.expect_popup() as popup_info:
        links.first.click()
    new_page = popup_info.value
    new_page.wait_for_load_state()
    assert new_page.url == 'https://example.com/'
