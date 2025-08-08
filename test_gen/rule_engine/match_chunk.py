"""
Command-line interface for rule-based action detection.

This module provides a CLI tool to run rule-based action detection
over preprocessed chunk JSON files and save detected actions to disk.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

from .rules_loader import load_rules
from .matcher import detect_actions_in_chunk, save_detected_actions
from .models import DetectedAction


def process_chunk_file(
    chunk_file: Path, rules: List, output_dir: Path, verbose: bool = False
) -> tuple[int, int]:
    """
    Process a single chunk JSON file and save detected actions.

    Args:
        chunk_file: Path to the chunk JSON file
        rules: List of Rule objects to apply
        output_dir: Directory to save detected actions
        verbose: Whether to print extra information

    Returns:
        Tuple of (number of actions detected, number of rules matched)
    """
    try:
        # Load and parse the chunk JSON
        with open(chunk_file, "r", encoding="utf-8") as f:
            chunk_data = json.load(f)

        # Validate chunk has required structure
        if not isinstance(chunk_data, dict) or "chunk_id" not in chunk_data:
            print(
                f"Warning: Skipping {chunk_file.name} - missing chunk_id",
                file=sys.stderr,
            )
            return 0, 0

        chunk_id = chunk_data["chunk_id"]

        if verbose:
            print(f"Processing chunk {chunk_id} from {chunk_file.name}")

        # Detect actions using the rule engine
        detected_actions = detect_actions_in_chunk(chunk_data, rules)

        # Save detected actions to disk
        if detected_actions:
            save_detected_actions(detected_actions, chunk_id, output_dir)

            # Count unique rules that matched
            unique_rules = len(set(action.rule_id for action in detected_actions))

            if verbose:
                print(
                    f"  Found {len(detected_actions)} actions from {unique_rules} rules"
                )

            return len(detected_actions), unique_rules
        else:
            if verbose:
                print(f"  No actions detected")
            return 0, 0

    except json.JSONDecodeError as e:
        print(
            f"Warning: Skipping {chunk_file.name} - malformed JSON: {e}",
            file=sys.stderr,
        )
        return 0, 0
    except Exception as e:
        print(f"Warning: Skipping {chunk_file.name} - error: {e}", file=sys.stderr)
        return 0, 0


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Process chunk JSON files and detect actions using rules"
    )
    parser.add_argument(
        "input_path",
        help="Path to a chunk JSON file or directory containing chunk JSON files",
    )
    parser.add_argument(
        "--rules-dir",
        default="test_gen/data/rules",
        help="Directory containing rule YAML files (default: test_gen/data/rules)",
    )
    parser.add_argument(
        "--output",
        default="test_gen/data/action_mappings",
        help="Output directory for detected actions (default: test_gen/data/action_mappings)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print extra information during processing",
    )

    args = parser.parse_args()

    # Convert paths to Path objects
    input_path = Path(args.input_path)
    rules_dir = Path(args.rules_dir)
    output_dir = Path(args.output)

    # Validate input path exists
    if not input_path.exists():
        print(f"Error: Input path does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        # Load rules from the rules directory
        if args.verbose:
            print(f"Loading rules from {rules_dir}")
        rules = load_rules(rules_dir)
        if args.verbose:
            print(f"Loaded {len(rules)} rules")

    except Exception as e:
        print(f"Error loading rules from {rules_dir}: {e}", file=sys.stderr)
        sys.exit(1)

    # Collect chunk files to process
    chunk_files = []

    if input_path.is_file():
        # Single file
        chunk_files = [input_path]
    elif input_path.is_dir():
        # Directory - find all JSON files
        chunk_files = list(input_path.glob("*.json"))
        if not chunk_files:
            print(
                f"Warning: No JSON files found in directory {input_path}",
                file=sys.stderr,
            )
    else:
        print(
            f"Error: Input path is neither a file nor a directory: {input_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Process all chunk files
    total_actions = 0
    total_unique_rules = set()
    processed_files = 0

    for chunk_file in sorted(chunk_files):
        actions_count, rules_count = process_chunk_file(
            chunk_file, rules, output_dir, args.verbose
        )

        if actions_count > 0 or rules_count > 0:
            processed_files += 1
            total_actions += actions_count

            # We need to track unique rule IDs across all files
            # Since process_chunk_file only returns count, we'll re-detect to get rule IDs
            try:
                with open(chunk_file, "r", encoding="utf-8") as f:
                    chunk_data = json.load(f)
                if isinstance(chunk_data, dict) and "chunk_id" in chunk_data:
                    detected_actions = detect_actions_in_chunk(chunk_data, rules)
                    for action in detected_actions:
                        total_unique_rules.add(action.rule_id)
            except:
                pass  # Already handled errors in process_chunk_file

    # Print summary
    files_processed = len([f for f in chunk_files if f.exists()])
    unique_rules_count = len(total_unique_rules)

    print(
        f"{total_actions} actions detected from {unique_rules_count} rules across {files_processed} files"
    )


if __name__ == "__main__":
    main()
