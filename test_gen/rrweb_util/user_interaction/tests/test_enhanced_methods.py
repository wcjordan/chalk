"""
Tests for UserInteraction with pre-computed field access.

Tests direct access to pre-computed DOM path and text content extraction
values stored in target_node dict.
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


def test_access_dom_path(sample_interaction):
    """Test direct access to dom_path field."""
    assert (
        sample_interaction.target_node["dom_path"]
        == "html > body > div.container > button#submit-btn"
    )


def test_access_data_testid(sample_interaction):
    """Test direct access to data_testid field."""
    assert sample_interaction.target_node["data_testid"] == "submit-btn"


def test_access_nearest_ancestor_testid(sample_interaction):
    """Test direct access to nearest_ancestor_testid field."""
    assert sample_interaction.target_node["nearest_ancestor_testid"] == "form-container"


def test_access_nearest_ancestor_testid_dom_path(sample_interaction):
    """Test direct access to nearest_ancestor_testid_dom_path field."""
    assert (
        sample_interaction.target_node["nearest_ancestor_testid_dom_path"]
        == "html > body > div.container"
    )


def test_access_element_text(sample_interaction):
    """Test direct access to text field."""
    assert sample_interaction.target_node["text"] == "Submit"


def test_access_all_descendant_text(sample_interaction):
    """Test direct access to all_descendant_text field."""
    assert sample_interaction.target_node["all_descendant_text"] == "Submit Now"


def test_access_aria_label(sample_interaction):
    """Test direct access to aria_label field."""
    assert sample_interaction.target_node["aria_label"] == "Submit form"


def test_access_role(sample_interaction):
    """Test direct access to role field."""
    assert sample_interaction.target_node["role"] == "button"


def test_access_tag(sample_interaction):
    """Test direct access to tag field."""
    assert sample_interaction.target_node["tag"] == "button"


def test_missing_values_use_get():
    """Test that missing values can be accessed safely with .get()."""
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

    assert interaction.target_node.get("dom_path") is None
    assert interaction.target_node.get("data_testid") is None
    assert interaction.target_node.get("nearest_ancestor_testid") is None
    assert interaction.target_node.get("nearest_ancestor_testid_dom_path") is None
    assert interaction.target_node.get("text") is None
    assert interaction.target_node.get("all_descendant_text") is None
    assert interaction.target_node.get("aria_label") is None
    assert interaction.target_node.get("role") is None
    assert interaction.target_node["tag"] == "div"  # Only tag is present


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
