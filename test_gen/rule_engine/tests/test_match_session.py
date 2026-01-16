"""
Integration tests for the CLI match_session module.

Tests the command-line interface for rule-based action detection,
including single file processing, directory processing, and error handling.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from rule_engine.match_session import main, process_session_file
from rule_engine.rules_loader import load_rules


@pytest.fixture(name="sample_rule")
def fixture_sample_rule() -> dict:
    """Create a sample rule dictionary for testing."""
    return {
        "id": "test_rule",
        "description": "Test rule for button clicks",
        "match": {
            "event": {"action": "click"},
            "node": {"tag": "button", "attributes": {"type": "submit"}},
        },
        "confidence": 0.9,
        "variables": {"button_text": "node.text"},
        "action_id": "submit_button_click",
    }


@pytest.fixture(name="temp_paths")
def fixture_temp_paths():
    """Fixture to create a temporary directories for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        rules_dir = temp_path / "rules"
        rules_dir.mkdir()
        output_dir = temp_path / "output"
        output_dir.mkdir()
        sessions_dir = temp_path / "sessions"
        sessions_dir.mkdir()

        yield temp_path, rules_dir, output_dir, sessions_dir


def test_single_file_processing(
    snapshot, create_processed_session, sample_rule, temp_paths
):
    """Test processing a single session JSON file."""
    _, rules_dir, output_dir, sessions_dir = temp_paths

    # Create a sample rule file
    with open(rules_dir / "test_rule.yaml", "w", encoding="utf-8") as f:
        yaml.dump(sample_rule, f)

    # Create a sample session file
    session_file = sessions_dir / "test_session.json"
    session_data = create_processed_session("test_session_123")

    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(session_data.to_dict(), f, indent=2, ensure_ascii=False)

    # Test direct function call
    actions_count, matched_rules = process_session_file(
        session_file, load_rules(rules_dir), output_dir
    )

    # Assertions
    assert actions_count == 1
    assert len(matched_rules) == 1

    # Check that output file was created
    output_file = output_dir / "test_session_123.json"
    assert output_file.exists()

    # Verify output content
    with open(output_file, "r", encoding="utf-8") as f:
        saved_actions = json.load(f)

    assert len(saved_actions) == 1
    assert saved_actions == snapshot(name="processed_session_dict")


def test_directory_processing(
    caplog, snapshot, sample_rule, create_processed_session, temp_paths
):
    """Test processing a directory containing multiple session files."""
    _, rules_dir, output_dir, sessions_dir = temp_paths

    # Create a sample rule file
    with open(rules_dir / "test_rule.yaml", "w", encoding="utf-8") as f:
        yaml.dump(sample_rule, f)

    # Create multiple session files - one matching, one not matching
    session1_data = create_processed_session("session1")
    with open(sessions_dir / "session1.json", "w", encoding="utf-8") as f:
        json.dump(session1_data.to_dict(), f, indent=2, ensure_ascii=False)

    session2_data = create_processed_session("session2", [])
    with open(sessions_dir / "session2.json", "w", encoding="utf-8") as f:
        json.dump(session2_data.to_dict(), f, indent=2, ensure_ascii=False)

    # Test using command line arguments simulation
    test_args = [
        "--input_path",
        str(sessions_dir),
        "--rules-dir",
        str(rules_dir),
        "--output",
        str(output_dir),
        "--verbose",
    ]

    with patch("sys.argv", ["match_session.py"] + test_args):
        main()

    # Verify the printed summary contains expected information
    assert "1 actions detected from 1 rules across 2 files" in caplog.text

    # Check output files
    output1 = output_dir / "session1.json"
    assert output1.exists()  # Should exist for matching session
    output2 = output_dir / "session2.json"
    assert not output2.exists()  # Should not exist for non-matching session

    # Load and verify JSON content
    with open(output1, "r", encoding="utf-8") as f:
        saved_data = json.load(f)

    assert len(saved_data) == 1
    assert saved_data == snapshot(name="processed_session_dict")


def test_malformed_json_handling(sample_rule, temp_paths):
    """Test graceful handling of malformed JSON files."""
    temp_path, rules_dir, output_dir, _ = temp_paths

    # Create a sample rule file
    rule_file = rules_dir / "test_rule.yaml"
    rule_data = sample_rule

    with open(rule_file, "w", encoding="utf-8") as f:
        yaml.dump(rule_data, f)

    # Create a malformed JSON file
    bad_session_file = temp_path / "bad_session.json"
    with open(bad_session_file, "w", encoding="utf-8") as f:
        f.write("{ invalid json content")

    # Create a file missing session_id
    missing_id_file = temp_path / "missing_id.json"
    with open(missing_id_file, "w", encoding="utf-8") as f:
        json.dump({"some_data": "but no session_id"}, f)

    # Test processing malformed file
    rules = load_rules(rules_dir)
    actions_count1, rules_matched1 = process_session_file(
        bad_session_file, rules, output_dir
    )
    assert actions_count1 == 0
    assert rules_matched1 == set()

    # Test processing file missing session_id
    actions_count2, rules_matched2 = process_session_file(
        missing_id_file, rules, output_dir
    )
    assert actions_count2 == 0
    assert rules_matched2 == set()


def test_nonexistent_input_path(temp_paths):
    """Test handling of nonexistent input paths."""
    temp_path, _, _, _ = temp_paths
    nonexistent_path = temp_path / "does_not_exist.json"
    test_args = ["--input_path", str(nonexistent_path)]

    with patch("sys.argv", ["match_session.py"] + test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Should exit with error code 1
        assert exc_info.value.code == 1


def test_empty_directory(caplog, sample_rule, temp_paths):
    """Test processing an empty directory."""
    _, rules_dir, output_dir, sessions_dir = temp_paths

    # Create a sample rule file
    rule_file = rules_dir / "test_rule.yaml"
    rule_data = sample_rule

    with open(rule_file, "w", encoding="utf-8") as f:
        yaml.dump(rule_data, f)

    test_args = [
        "--input_path",
        str(sessions_dir),
        "--rules-dir",
        str(rules_dir),
        "--output",
        str(output_dir),
        "--verbose",
    ]

    with patch("sys.argv", ["match_session.py"] + test_args):
        main()

    # Should complete without error and report 0 actions
    assert "0 actions detected from 0 rules across 0 files" in caplog.text


def test_invalid_rules_directory(create_processed_session, temp_paths):
    """Test handling of invalid rules directory."""
    temp_path, _, _, _ = temp_paths

    # Create a valid session file
    session_file = temp_path / "test_session.json"
    session_data = create_processed_session("test_session")
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(session_data.to_dict(), f, indent=2, ensure_ascii=False)

    # Use nonexistent rules directory
    nonexistent_rules = temp_path / "nonexistent_rules"

    test_args = [
        "--input_path",
        str(session_file),
        "--rules-dir",
        str(nonexistent_rules),
    ]

    with patch("sys.argv", ["match_session.py"] + test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Should exit with error code 1
        assert exc_info.value.code == 1
