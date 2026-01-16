"""
Fixtures for rrweb_util tests
"""

import pytest

from rrweb_util.user_interaction.extractors import UserInteraction


@pytest.fixture
def basic_user_interaction():
    """Fixture that provides a basic UserInteraction instance."""
    target_node = {
        "tag": "button",
        "attributes": {"id": "submit-btn", "class": "btn primary"},
        "text": "Submit",
        "dom_path": ["html", "body", "div[1]", "button[1]"],
    }
    return UserInteraction(
        action="click",
        target_id=456,
        target_node=target_node,
        value={"x": 100, "y": 200},
        timestamp=2000,
    )
