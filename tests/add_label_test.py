import pytest

from helpers.label_helpers import (
    get_label_filter_status,
    toggle_label_filter,
    toggle_label_filter_section,
)


@pytest.mark.parametrize("test_name", ["Label: Add Label"])
def test_add_label(page, base_url):
    page.goto(f"{base_url}/api/admin")
    page.get_by_text("Label models").click()
    page.get_by_text("ADD LABEL MODEL").click()
    page.get_by_label("Name").fill("Test Label")
    page.get_by_role("button", name="Save", exact=True).click()

    # Verify label appears in label picker
    page.goto(f"{base_url}/")
    toggle_label_filter_section(page)
    assert get_label_filter_status(page, "Test Label") == "Disabled"
    toggle_label_filter(page, "Test Label")
    assert get_label_filter_status(page, "Test Label") == "Active"
