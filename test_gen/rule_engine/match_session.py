"""
Command-line interface for rule-based action detection.

This module provides a CLI tool to run rule-based action detection
over preprocessed session JSON files and save detected actions to disk.
"""

import argparse
from dataclasses import asdict
import json
import logging
import sys
from pathlib import Path
from typing import List, Union

from rrweb_ingest.models import processed_session_from_dict
from rule_engine.models import DetectedAction
from .rules_loader import load_rules
from .matcher import detect_actions_in_session

logger = logging.getLogger("test_gen.rule_engine")


def process_session_file(
    session_file: Path, rules: List, output_dir: Path
) -> tuple[int, set]:
    """
    Process a single session JSON file and save detected actions.

    Args:
        session_file: Path to the session JSON file
        rules: List of Rule objects to apply
        output_dir: Directory to save detected actions

    Returns:
        Tuple of (number of actions detected, a set of the rules matched)
    """
    try:
        # Load and parse the session JSON
        with open(session_file, "r", encoding="utf-8") as f:
            session_data = json.load(f)

        # Validate session has required structure
        if not isinstance(session_data, dict) or "session_id" not in session_data:
            logger.error("Warning: Skipping %s - missing session_id", session_file.name)
            return 0, set()
        session_data = processed_session_from_dict(session_data)

        session_id = session_data.session_id
        logger.debug("Processing session %s from %s", session_id, session_file.name)

        # Detect actions using the rule engine
        detected_actions = detect_actions_in_session(session_data, rules)
        # Save detected actions to disk
        if detected_actions:
            _save_detected_actions(detected_actions, session_id, output_dir)

            # Count unique rules that matched
            unique_rules = set(action.rule_id for action in detected_actions)

            logger.debug(
                "  Found %d actions from %d rules",
                len(detected_actions),
                len(unique_rules),
            )

            return len(detected_actions), unique_rules

        logger.debug("  No actions detected")
        return 0, set()

    except json.JSONDecodeError as e:
        logger.error("Warning: Skipping %s - malformed JSON: %s", session_file.name, e)
        return 0, set()


def _parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the feature extraction tool.
    """
    parser = argparse.ArgumentParser(
        description="Process session JSON files and detect actions using rules"
    )
    parser.add_argument(
        "--input_path",
        default="data/output_features",
        help="Path to a session JSON file or directory containing session JSON files (default: data/output_features)",
    )
    parser.add_argument(
        "--rules-dir",
        default="data/rules",
        help="Directory containing rule YAML files (default: data/rules)",
    )
    parser.add_argument(
        "--output",
        default="data/action_mappings",
        help="Output directory for detected actions (default: data/action_mappings)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging (INFO level)",
    )
    parser.add_argument(
        "--trace-match",
        action="store_true",
        help="Enable trace matching logging (DEBUG level)",
    )

    return parser.parse_args()


def _setup_logger(args):
    """Set up logging for the rule engine based on the verbosity flags."""
    log_level = logging.WARNING  # Default: quiet
    if args.trace_match:
        log_level = logging.DEBUG  # Deep tracing
    elif args.verbose:
        log_level = logging.INFO  # Verbose mode

    # Configure the test_gen.rule_engine logger
    rule_engine_logger = logging.getLogger("test_gen.rule_engine")
    rule_engine_logger.setLevel(log_level)


def _save_detected_actions(
    actions: List[DetectedAction],
    session_id: str,
    output_dir: Union[str, Path] = "test_gen/data/action_mappings",
) -> None:
    """
    Serialize detected actions to disk as JSON using session_id as filename.
    Args:
        actions: List of DetectedAction objects to serialize
        session_id: ID to use for the filename
        output_dir: Directory to save the file to

    The function creates the output directory if it doesn't exist and saves
    the actions as JSON to {output_dir}/{session_id}.json.
    """
    # Convert output_dir to Path object
    output_path = Path(output_dir)

    # Create the output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    # Convert DetectedAction objects to JSON-serializable dicts
    serializable_actions = []
    for action in actions:
        action_dict = asdict(action)

        serializable_actions.append(action_dict)

    # Define the output file path
    output_file = output_path / f"{session_id}.json"

    # Write to JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(serializable_actions, f, indent=2, ensure_ascii=False)


def main():
    """Main entry point for the CLI tool."""
    args = _parse_arguments()
    _setup_logger(args)

    # Convert paths to Path objects
    input_path = Path(args.input_path)
    rules_dir = Path(args.rules_dir)
    output_dir = Path(args.output)

    # Validate input path exists
    if not input_path.exists():
        logger.error("Error: Input path does not exist: %s", input_path)
        sys.exit(1)

    try:
        # Load rules from the rules directory
        logger.debug("Loading rules from %s", rules_dir)
        rules = load_rules(rules_dir)
        logger.debug("Loaded %d rules", len(rules))
    except FileNotFoundError as e:
        logger.error("Error unable to find rules file in %s: %s", rules_dir, e)
        sys.exit(1)

    # Collect session files to process
    session_files = []

    if input_path.is_file():
        # Single file
        session_files = [input_path]
    elif input_path.is_dir():
        # Directory - find all JSON files
        session_files = list(input_path.glob("*.json"))
        if not session_files:
            logger.warning("Warning: No JSON files found in directory %s", input_path)
    else:
        logger.error("Input path is neither a file nor a directory: %s", input_path)
        sys.exit(1)

    # Process all session files
    total_actions = 0
    total_unique_rules = set()
    processed_files = 0

    for session_file in sorted(session_files):
        actions_count, rules_matched = process_session_file(
            session_file, rules, output_dir
        )

        processed_files += 1
        total_actions += actions_count
        total_unique_rules.update(rules_matched)

    # Print summary
    files_processed = len([f for f in session_files if f.exists()])
    unique_rules_count = len(total_unique_rules)

    logger.info(
        "%d actions detected from %d rules across %d files",
        total_actions,
        unique_rules_count,
        files_processed,
    )


if __name__ == "__main__":
    main()
