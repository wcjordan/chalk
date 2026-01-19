"""
Fixtures for rrweb_ingest tests
"""

import os
import pytest

from rrweb_util.test_utils.fixtures import (  # noqa: F401  # pylint: disable=unused-import
    basic_user_interaction,
)


@pytest.fixture
def sample_data_path():
    """
    Fixture that provides the path to the sample rrweb session JSON file for testing.
    """
    # Get the path to the sample fixture
    current_dir = os.path.dirname(__file__)
    sample_path = os.path.join(current_dir, "fixture_data", "rrweb_sample.json")

    # Ensure the sample file exists
    assert os.path.exists(sample_path), f"Sample file not found at {sample_path}"

    return sample_path
