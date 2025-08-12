"""
Integration tests for the CLI match_chunk module.

Tests the command-line interface for rule-based action detection,
including single file processing, directory processing, and error handling.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from rule_engine.match_chunk import main, process_chunk_file
from rule_engine.models import Rule
from rule_engine.rules_loader import load_rules
from feature_extraction.models import UserInteraction, UINode


@pytest.fixture(name="create_sample_chunk")
def fixture_create_sample_chunk():
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
                target_id="node_1",
                value=None,
            )
            interactions.append(interaction)

            # Create a UINode that will match our test rule
            node = UINode(
                id="node_1",
                tag="button",
                attributes={"type": "submit"},
                text="Submit",
                parent="parent_id"
            )
            nodes.append(node)

        return {
            "chunk_id": chunk_id,
            "features": {"user_interactions": interactions, "ui_nodes": nodes},
        }
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

def test_single_file_processing(create_sample_chunk, sample_rule):
    """Test processing a single chunk JSON file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create directories
        rules_dir = temp_path / "rules"
        output_dir = temp_path / "output"
        rules_dir.mkdir()
        output_dir.mkdir()

        # Create a sample rule file
        rule_file = rules_dir / "test_rule.yaml"
        rule_data = sample_rule

        with open(rule_file, "w", encoding="utf-8") as f:
            yaml.dump(rule_data, f)

        # Create a sample chunk file
        chunk_file = temp_path / "test_chunk.json"
        chunk_data = create_sample_chunk(
            "test_chunk_123", has_matching_interaction=True
        )

        with open(chunk_file, "w", encoding="utf-8") as f:
            json.dump(chunk_data, f)

        # Test direct function call
        rules = load_rules(rules_dir)
        actions_count, rules_count = process_chunk_file(
            chunk_file, rules, output_dir, verbose=True
        )

        # Assertions
        assert actions_count == 1
        assert rules_count == 1

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

def test_directory_processing(sample_rule, create_sample_chunk):
    """Test processing a directory containing multiple chunk files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create directories
        rules_dir = temp_path / "rules"
        output_dir = temp_path / "output"
        chunks_dir = temp_path / "chunks"
        rules_dir.mkdir()
        output_dir.mkdir()
        chunks_dir.mkdir()

        # Create a sample rule file
        rule_file = rules_dir / "test_rule.yaml"
        rule_data = sample_rule

        with open(rule_file, "w", encoding="utf-8") as f:
            yaml.dump(rule_data, f)

        # Create multiple chunk files - one matching, one not matching
        chunk1_file = chunks_dir / "chunk1.json"
        chunk1_data = create_sample_chunk(
            "chunk1", has_matching_interaction=True
        )
        with open(chunk1_file, "w", encoding="utf-8") as f:
            json.dump(chunk1_data, f)

        chunk2_file = chunks_dir / "chunk2.json"
        chunk2_data = create_sample_chunk(
            "chunk2", has_matching_interaction=False
        )
        with open(chunk2_file, "w", encoding="utf-8") as f:
            json.dump(chunk2_data, f)

        # Test using command line arguments simulation
        test_args = [
            str(chunks_dir),
            "--rules-dir",
            str(rules_dir),
            "--output",
            str(output_dir),
            "--verbose",
        ]

        with patch("sys.argv", ["match_chunk.py"] + test_args):
            with patch("sys.stdout") as mock_stdout:
                main()

        # Check output files
        output1 = output_dir / "chunk1.json"
        output2 = output_dir / "chunk2.json"

        assert output1.exists()  # Should exist for matching chunk
        assert not output2.exists()  # Should not exist for non-matching chunk

        # Verify the printed summary contains expected information
        printed_output = "".join(
            call.args[0] for call in mock_stdout.write.calls if call.args
        )
        assert "1 actions detected from 1 rules across 2 files" in printed_output

def test_malformed_json_handling(sample_rule):
    """Test graceful handling of malformed JSON files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create directories
        rules_dir = temp_path / "rules"
        output_dir = temp_path / "output"
        rules_dir.mkdir()
        output_dir.mkdir()

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
        actions_count1, rules_count1 = process_chunk_file(
            bad_chunk_file, rules, output_dir
        )
        assert actions_count1 == 0
        assert rules_count1 == 0

        # Test processing file missing chunk_id
        actions_count2, rules_count2 = process_chunk_file(
            missing_id_file, rules, output_dir
        )
        assert actions_count2 == 0
        assert rules_count2 == 0

def test_nonexistent_input_path():
    """Test handling of nonexistent input paths."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        nonexistent_path = temp_path / "does_not_exist.json"

        test_args = [str(nonexistent_path)]

        with patch("sys.argv", ["match_chunk.py"] + test_args):
            with patch("sys.stderr") as mock_stderr:
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # Should exit with error code 1
                assert exc_info.value.code == 1

def test_empty_directory(sample_rule):
    """Test processing an empty directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create directories
        rules_dir = temp_path / "rules"
        output_dir = temp_path / "output"
        empty_dir = temp_path / "empty"
        rules_dir.mkdir()
        output_dir.mkdir()
        empty_dir.mkdir()

        # Create a sample rule file
        rule_file = rules_dir / "test_rule.yaml"
        rule_data = sample_rule

        with open(rule_file, "w", encoding="utf-8") as f:
            yaml.dump(rule_data, f)

        test_args = [
            str(empty_dir),
            "--rules-dir",
            str(rules_dir),
            "--output",
            str(output_dir),
        ]

        with patch("sys.argv", ["match_chunk.py"] + test_args):
            with patch("sys.stdout") as mock_stdout:
                main()

        # Should complete without error and report 0 actions
        printed_output = "".join(
            call.args[0] for call in mock_stdout.write.calls if call.args
        )
        assert "0 actions detected from 0 rules across 0 files" in printed_output

def test_invalid_rules_directory(create_sample_chunk):
    """Test handling of invalid rules directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a valid chunk file
        chunk_file = temp_path / "test_chunk.json"
        chunk_data = create_sample_chunk("test_chunk")
        with open(chunk_file, "w", encoding="utf-8") as f:
            json.dump(chunk_data, f)

        # Use nonexistent rules directory
        nonexistent_rules = temp_path / "nonexistent_rules"

        test_args = [str(chunk_file), "--rules-dir", str(nonexistent_rules)]

        with patch("sys.argv", ["match_chunk.py"] + test_args):
            with patch("sys.stderr") as mock_stderr:
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # Should exit with error code 1
                assert exc_info.value.code == 1
