"""
Tests for UserInteraction enhanced getter methods.

Tests the convenience methods for accessing pre-computed DOM path
and text content extraction values.
"""

import pytest
from rrweb_util.user_interaction.models import UserInteraction


@pytest.fixture(name="sample_interaction")
def fixture_sample_interaction():
    """Fixture providing a sample UserInteraction with full metadata."""
    return UserInteraction(
        action="click",
        target_id=123,
        target_node={
            "tag": "button",
            "text": "Submit",
            "all_descendant_text": "Submit Now",
            "data_testid": "submit-btn",
            "dom_path": "html > body > div.container > button#submit-btn",
            "aria_label": "Submit form",
            "role": "button",
            "nearest_ancestor_testid": "form-container",
            "nearest_ancestor_testid_dom_path": "html > body > div.container",
        },
        value={"x": 100, "y": 200},
        timestamp=1000000,
    )


def test_get_dom_path(sample_interaction):
    """Test that get_dom_path returns the correct value."""
    assert (
        sample_interaction.get_dom_path()
        == "html > body > div.container > button#submit-btn"
    )


def test_get_data_testid(sample_interaction):
    """Test that get_data_testid returns the correct value."""
    assert sample_interaction.get_data_testid() == "submit-btn"


def test_get_nearest_ancestor_testid(sample_interaction):
    """Test that get_nearest_ancestor_testid returns the correct value."""
    assert sample_interaction.get_nearest_ancestor_testid() == "form-container"


def test_get_nearest_ancestor_testid_dom_path(sample_interaction):
    """Test that get_nearest_ancestor_testid_dom_path returns the correct value."""
    assert (
        sample_interaction.get_nearest_ancestor_testid_dom_path()
        == "html > body > div.container"
    )


def test_get_element_text(sample_interaction):
    """Test that get_element_text returns the direct text content."""
    assert sample_interaction.get_element_text() == "Submit"


def test_get_all_descendant_text(sample_interaction):
    """Test that get_all_descendant_text returns concatenated text."""
    assert sample_interaction.get_all_descendant_text() == "Submit Now"


def test_get_aria_label(sample_interaction):
    """Test that get_aria_label returns the aria-label value."""
    assert sample_interaction.get_aria_label() == "Submit form"


def test_get_role(sample_interaction):
    """Test that get_role returns the role value."""
    assert sample_interaction.get_role() == "button"


def test_get_tag(sample_interaction):
    """Test that get_tag returns the tag name."""
    assert sample_interaction.get_tag() == "button"


def test_missing_values_return_none():
    """Test that missing values return None instead of raising errors."""
    interaction = UserInteraction(
        action="click",
        target_id=456,
        target_node={
            "tag": "div",
            # All other fields intentionally missing
        },
        value={},
        timestamp=2000000,
    )

    assert interaction.get_dom_path() is None
    assert interaction.get_data_testid() is None
    assert interaction.get_nearest_ancestor_testid() is None
    assert interaction.get_nearest_ancestor_testid_dom_path() is None
    assert interaction.get_element_text() is None
    assert interaction.get_all_descendant_text() is None
    assert interaction.get_aria_label() is None
    assert interaction.get_role() is None
    assert interaction.get_tag() == "div"  # Only tag is present


def test_to_dict_includes_target_node():
    """Test that to_dict preserves all target_node fields."""
    interaction = UserInteraction(
        action="input",
        target_id=789,
        target_node={
            "tag": "input",
            "text": "",
            "all_descendant_text": None,
            "data_testid": "email-input",
            "dom_path": "html > body > form > input#email",
            "aria_label": "Email address",
            "role": None,
            "nearest_ancestor_testid": "login-form",
            "nearest_ancestor_testid_dom_path": "html > body > form",
        },
        value={"value": "test@example.com"},
        timestamp=3000000,
    )

    result = interaction.to_dict()

    assert result["action"] == "input"
    assert result["target_id"] == 789
    assert result["target_node"]["tag"] == "input"
    assert result["target_node"]["data_testid"] == "email-input"
    assert result["target_node"]["all_descendant_text"] is None
    assert result["target_node"]["nearest_ancestor_testid"] == "login-form"
    assert result["value"]["value"] == "test@example.com"
    assert result["timestamp"] == 3000000
