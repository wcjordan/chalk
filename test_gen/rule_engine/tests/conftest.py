"""
Fixtures for testing the rule engine matcher.
"""

import pytest

from rrweb_ingest.models import ProcessedSession
from rrweb_util.user_interaction.models import UserInteraction


@pytest.fixture
def create_processed_session():
    """
    Fixture to create a ProcessedSession for testing.
    """

    def _create_processed_session(
        session_id: str = "test_session", interactions: list[UserInteraction] = None
    ) -> ProcessedSession:
        """
        Create a ProcessedSession for testing.

        Args:
            interactions: List of UserInteraction objects

        Returns:
            A ProcessedSession object populated with the provided interactions.
        """
        if interactions is None:
            interactions = [
                UserInteraction(
                    timestamp=1234567890,
                    action="click",
                    target_id=11,
                    target_node={
                        "id": 11,
                        "tag": "button",
                        "attributes": {"type": "submit"},
                        "text": "Submit",
                        "parent": "parent_id",
                    },
                    value=None,
                )
            ]

        return ProcessedSession(
            session_id=session_id,
            user_interactions=interactions,
        )

    return _create_processed_session
