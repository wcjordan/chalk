"""
Integration tests for the CLI match_chunk module.

Tests the command-line interface for rule-based action detection,
including single file processing, directory processing, and error handling.
"""

import json
import tempfile
import logging
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from rule_engine.match_chunk import main, process_chunk_file
from rule_engine.rules_loader import load_rules
from feature_extraction.models import FeatureChunk, UserInteraction, UINode


def _ui_nodes_to_map(ui_nodes: list[UINode]) -> dict[int, UINode]:
    """Convert a list of UINodes to a dictionary keyed by node ID."""
    return {node.id: node for node in ui_nodes}


@pytest.fixture(name="create_sample_chunk")
def fixture_create_sample_chunk():
    """
    Fixture to create a sample chunk dictionary for testing.
    """

    def _create_sample_chunk(
        chunk_id: str, has_matching_interaction: bool = True
    ) -> dict:
        """Create a sample chunk dictionary for testing."""
        interactions = []
        nodes = []

        if has_matching_interaction:
            # Create a UserInteraction that will match our test rule
            interaction = UserInteraction(
                timestamp=1234567890,
                action="click",
                target_id=11,
                value=None,
            )
            interactions.append(interaction)

            # Create a UINode that will match our test rule
            node = UINode(
                id=11,
                tag="button",
                attributes={"type": "submit"},
                text="Submit",
                parent="parent_id",
            )
            nodes.append(node)

        return FeatureChunk(
            chunk_id=chunk_id,
            start_time=1234567890,
            end_time=1234567890,
            events=[],
            metadata={},
            features={
                "interactions": interactions,
                "ui_nodes": _ui_nodes_to_map(nodes),
            },
        )

    return _create_sample_chunk


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
        chunks_dir = temp_path / "chunks"
        chunks_dir.mkdir()

        yield temp_path, rules_dir, output_dir, chunks_dir


def test_single_file_processing(create_sample_chunk, sample_rule, temp_paths):
    """Test processing a single chunk JSON file."""
    temp_path, rules_dir, output_dir, _ = temp_paths

    # Create a sample rule file
    with open(rules_dir / "test_rule.yaml", "w", encoding="utf-8") as f:
        yaml.dump(sample_rule, f)

    # Create a sample chunk file
    chunk_file = temp_path / "test_chunk.json"
    chunk_data = create_sample_chunk("test_chunk_123", has_matching_interaction=True)

    with open(chunk_file, "w", encoding="utf-8") as f:
        json.dump(chunk_data.to_dict(), f, indent=2, ensure_ascii=False)

    # Test direct function call
    actions_count, matched_rules = process_chunk_file(
        chunk_file, load_rules(rules_dir), output_dir
    )

    # Assertions
    assert actions_count == 1
    assert len(matched_rules) == 1

    # Check that output file was created
    output_file = output_dir / "test_chunk_123.json"
    assert output_file.exists()

    # Verify output content
    with open(output_file, "r", encoding="utf-8") as f:
        saved_actions = json.load(f)

    assert len(saved_actions) == 1
    action = saved_actions[0]
    assert action["action_id"] == "submit_button_click"
    assert action["rule_id"] == "test_rule"
    assert action["confidence"] == 0.9
    assert action["variables"]["button_text"] == "Submit"


def test_directory_processing(caplog, sample_rule, create_sample_chunk, temp_paths):
    """Test processing a directory containing multiple chunk files."""
    _, rules_dir, output_dir, chunks_dir = temp_paths

    # Create a sample rule file
    with open(rules_dir / "test_rule.yaml", "w", encoding="utf-8") as f:
        yaml.dump(sample_rule, f)

    # Create multiple chunk files - one matching, one not matching
    chunk1_data = create_sample_chunk("chunk1", has_matching_interaction=True)
    with open(chunks_dir / "chunk1.json", "w", encoding="utf-8") as f:
        json.dump(chunk1_data.to_dict(), f, indent=2, ensure_ascii=False)

    chunk2_data = create_sample_chunk("chunk2", has_matching_interaction=False)
    with open(chunks_dir / "chunk2.json", "w", encoding="utf-8") as f:
        json.dump(chunk2_data.to_dict(), f, indent=2, ensure_ascii=False)

    # Test using command line arguments simulation
    test_args = [
        "--input_path",
        str(chunks_dir),
        "--rules-dir",
        str(rules_dir),
        "--output",
        str(output_dir),
        "--verbose",
    ]

    with patch("sys.argv", ["match_chunk.py"] + test_args):
        main()

    # Check output files
    output1 = output_dir / "chunk1.json"
    output2 = output_dir / "chunk2.json"

    assert output1.exists()  # Should exist for matching chunk
    assert not output2.exists()  # Should not exist for non-matching chunk

    # Verify the printed summary contains expected information
    assert "1 actions detected from 1 rules across 2 files" in caplog.text


def test_malformed_json_handling(sample_rule, temp_paths):
    """Test graceful handling of malformed JSON files."""
    temp_path, rules_dir, output_dir, _ = temp_paths

    # Create a sample rule file
    rule_file = rules_dir / "test_rule.yaml"
    rule_data = sample_rule

    with open(rule_file, "w", encoding="utf-8") as f:
        yaml.dump(rule_data, f)

    # Create a malformed JSON file
    bad_chunk_file = temp_path / "bad_chunk.json"
    with open(bad_chunk_file, "w", encoding="utf-8") as f:
        f.write("{ invalid json content")

    # Create a file missing chunk_id
    missing_id_file = temp_path / "missing_id.json"
    with open(missing_id_file, "w", encoding="utf-8") as f:
        json.dump({"some_data": "but no chunk_id"}, f)

    # Test processing malformed file
    rules = load_rules(rules_dir)
    actions_count1, rules_matched1 = process_chunk_file(
        bad_chunk_file, rules, output_dir
    )
    assert actions_count1 == 0
    assert rules_matched1 == set()

    # Test processing file missing chunk_id
    actions_count2, rules_matched2 = process_chunk_file(
        missing_id_file, rules, output_dir
    )
    assert actions_count2 == 0
    assert rules_matched2 == set()


def test_nonexistent_input_path(temp_paths):
    """Test handling of nonexistent input paths."""
    temp_path, _, _, _ = temp_paths
    nonexistent_path = temp_path / "does_not_exist.json"
    test_args = ["--input_path", str(nonexistent_path)]

    with patch("sys.argv", ["match_chunk.py"] + test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Should exit with error code 1
        assert exc_info.value.code == 1


def test_empty_directory(caplog, sample_rule, temp_paths):
    """Test processing an empty directory."""
    _, rules_dir, output_dir, chunks_dir = temp_paths

    # Create a sample rule file
    rule_file = rules_dir / "test_rule.yaml"
    rule_data = sample_rule

    with open(rule_file, "w", encoding="utf-8") as f:
        yaml.dump(rule_data, f)

    test_args = [
        "--input_path",
        str(chunks_dir),
        "--rules-dir",
        str(rules_dir),
        "--output",
        str(output_dir),
        "--verbose",
    ]

    with patch("sys.argv", ["match_chunk.py"] + test_args):
        main()

    # Should complete without error and report 0 actions
    assert "0 actions detected from 0 rules across 0 files" in caplog.text


def test_invalid_rules_directory(create_sample_chunk, temp_paths):
    """Test handling of invalid rules directory."""
    temp_path, _, _, _ = temp_paths

    # Create a valid chunk file
    chunk_file = temp_path / "test_chunk.json"
    chunk_data = create_sample_chunk("test_chunk")
    with open(chunk_file, "w", encoding="utf-8") as f:
        json.dump(chunk_data.to_dict(), f, indent=2, ensure_ascii=False)

    # Use nonexistent rules directory
    nonexistent_rules = temp_path / "nonexistent_rules"

    test_args = [
        "--input_path",
        str(chunk_file),
        "--rules-dir",
        str(nonexistent_rules),
    ]

    with patch("sys.argv", ["match_chunk.py"] + test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Should exit with error code 1
        assert exc_info.value.code == 1
