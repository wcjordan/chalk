"""
Smoke test for rrweb_ingest module.

This test simply verifies that the module can be imported without errors.
"""

import pytest


def test_import_rrweb_ingest():
    """Test that rrweb_ingest module can be imported successfully."""
    try:
        import rrweb_ingest  # pylint: disable=import-outside-toplevel

        assert rrweb_ingest is not None
        assert hasattr(rrweb_ingest, "__version__")
    except ImportError as e:
        pytest.fail(f"Failed to import rrweb_ingest: {e}")


def test_module_has_version():
    """Test that the module has a version attribute."""
    import rrweb_ingest  # pylint: disable=import-outside-toplevel

    assert hasattr(rrweb_ingest, "__version__")
    assert isinstance(rrweb_ingest.__version__, str)
    assert len(rrweb_ingest.__version__) > 0
