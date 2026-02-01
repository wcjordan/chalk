"""
Tests for JSON serialization functionality of user interaction models.
"""


def test_user_interaction_to_dict(basic_user_interaction):
    """Test UserInteraction serialization to dictionary."""
    result = basic_user_interaction.to_dict()

    assert result == {
        "action": "click",
        "target_id": 456,
        "target_node": basic_user_interaction.target_node,
        "value": {"x": 100, "y": 200},
        "timestamp": 2000,
    }
