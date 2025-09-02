"""
Command-line interface for rule-based action detection.

This module provides a CLI tool to run rule-based action detection
over preprocessed chunk JSON files and save detected actions to disk.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List

from feature_extraction.models import feature_chunk_from_dict
from .rules_loader import load_rules
from .matcher import detect_actions_in_chunk, save_detected_actions

logger = logging.getLogger("test_gen.rule_engine")


def process_chunk_file(
    chunk_file: Path, rules: List, output_dir: Path
) -> tuple[int, set]:
    """
    Process a single chunk JSON file and save detected actions.

    Args:
        chunk_file: Path to the chunk JSON file
        rules: List of Rule objects to apply
        output_dir: Directory to save detected actions

    Returns:
        Tuple of (number of actions detected, a set of the rules matched)
    """
    try:
        # Load and parse the chunk JSON
        with open(chunk_file, "r", encoding="utf-8") as f:
            chunk_data = json.load(f)

        # Validate chunk has required structure
        if not isinstance(chunk_data, dict) or "chunk_id" not in chunk_data:
            logger.error("Warning: Skipping %s - missing chunk_id", chunk_file.name)
            return 0, set()
        feature_chunk = feature_chunk_from_dict(chunk_data)

        chunk_id = feature_chunk.chunk_id
        logger.debug("Processing chunk %s from %s", chunk_id, chunk_file.name)

        # Detect actions using the rule engine
        detected_actions = detect_actions_in_chunk(feature_chunk, rules)

        # Save detected actions to disk
        if detected_actions:
            save_detected_actions(detected_actions, chunk_id, output_dir)

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
        logger.error("Warning: Skipping %s - malformed JSON: %s", chunk_file.name, e)
        return 0, set()


def _parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the feature extraction tool.
    """
    parser = argparse.ArgumentParser(
        description="Process chunk JSON files and detect actions using rules"
    )
    parser.add_argument(
        "--input_path",
        default="data/output_features",
        help="Path to a chunk JSON file or directory containing chunk JSON files (default: data/output_features)",
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


def main():
    """Main entry point for the CLI tool."""
    args = _parse_arguments()

    # Set up logging based on verbosity flags
    log_level = logging.WARNING  # Default: quiet
    if args.trace_match:
        log_level = logging.DEBUG  # Deep tracing
    elif args.verbose:
        log_level = logging.INFO  # Verbose mode

    # Configure the test_gen.rule_engine logger
    rule_engine_logger = logging.getLogger("test_gen.rule_engine")
    rule_engine_logger.setLevel(log_level)

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

    # Collect chunk files to process
    chunk_files = []

    if input_path.is_file():
        # Single file
        chunk_files = [input_path]
    elif input_path.is_dir():
        # Directory - find all JSON files
        chunk_files = list(input_path.glob("*.json"))
        if not chunk_files:
            logger.warning("Warning: No JSON files found in directory %s", input_path)
    else:
        logger.error("Input path is neither a file nor a directory: %s", input_path)
        sys.exit(1)

    # Process all chunk files
    total_actions = 0
    total_unique_rules = set()
    processed_files = 0

    for chunk_file in sorted(chunk_files):
        actions_count, rules_matched = process_chunk_file(chunk_file, rules, output_dir)

        processed_files += 1
        total_actions += actions_count
        total_unique_rules.update(rules_matched)

    # Print summary
    files_processed = len([f for f in chunk_files if f.exists()])
    unique_rules_count = len(total_unique_rules)

    logger.info(
        "%d actions detected from %d rules across %d files",
        total_actions,
        unique_rules_count,
        files_processed,
    )


if __name__ == "__main__":
    main()
