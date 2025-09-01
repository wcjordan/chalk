#!/usr/bin/env python3
"""
Command-line interface for feature extraction.

This module provides a CLI tool to extract features from rrweb session files
and save them as JSON files for use by the rule engine or other analysis tools.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from .pipeline import extract_and_save_features

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO").upper())
logger = logging.getLogger(__name__)


def _parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the feature extraction tool.
    """
    parser = argparse.ArgumentParser(
        description="Extract features from rrweb session files and save as JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract features from all sessions in data/output_sessions
  python -m feature_extraction.extract_features_cli

  # Extract features with custom input and output directories
  python -m feature_extraction.extract_features_cli --session_dir data/my_sessions --output_dir data/my_features

  # Process only first 10 sessions with verbose debugging output
  LOGLEVEL=DEBUG python -m feature_extraction.extract_features_cli --max-sessions 10
        """,
    )

    parser.add_argument(
        "--session_dir",
        default="data/output_sessions",
        help="Directory containing rrweb JSON session files to process  (default: data/output_sessions)",
    )

    parser.add_argument(
        "--output_dir",
        default="data/output_features",
        help="Output directory for extracted feature JSON files (default: data/output_features)",
    )

    parser.add_argument(
        "--max-sessions",
        type=int,
        help="Maximum number of sessions to process (default: process all)",
    )

    return parser.parse_args()


def _validate_inputs(args):
    """
    Validate command-line arguments for the feature extraction tool.
    """
    # Convert paths to Path objects and validate
    session_dir = Path(args.session_dir)
    output_dir = Path(args.output_dir)

    if not session_dir.exists():
        logger.error("Session directory does not exist: %s", session_dir)
        sys.exit(1)

    if not session_dir.is_dir():
        logger.error("Session path is not a directory: %s", session_dir)
        sys.exit(1)

    # Check if session directory contains any JSON files
    json_files = list(session_dir.glob("*.json"))
    if not json_files:
        logger.warning("No JSON files found in session directory: %s", session_dir)

    logger.debug("Feature Extraction CLI")
    logger.debug("======================")
    logger.debug("Session directory: %s", session_dir)
    logger.debug("Output directory: %s", output_dir)
    logger.debug("Max sessions: %s", args.max_sessions or "unlimited")
    logger.debug("Found %d JSON files", len(json_files))
    logger.debug("")

    return session_dir, output_dir


def main():
    """Main entry point for the CLI tool."""
    args = _parse_arguments()
    session_dir, output_dir = _validate_inputs(args)

    try:
        # Run the feature extraction
        stats = extract_and_save_features(
            session_dir=str(session_dir),
            output_dir=str(output_dir),
            max_sessions=args.max_sessions,
        )

        # Print final summary
        logger.debug("\n%s", "=" * 50)

        logger.info("Feature extraction completed successfully!")
        logger.info("Sessions processed: %d", stats["sessions_processed"])
        logger.info("Feature chunks saved: %d", stats["chunks_saved"])

        # Print feature type counts if any were extracted
        feature_counts = stats["total_features"]
        total_feature_count = sum(count for count in feature_counts.values())

        if total_feature_count > 0:
            logger.info("Total features extracted: %d", total_feature_count)
            logger.debug("Feature breakdown:")
            for feature_type, count in feature_counts.items():
                if count > 0:
                    logger.debug("  %s: %d", feature_type, count)

        # Print error summary
        if stats["errors"]:
            logger.warning("Errors encountered: %d", len(stats["errors"]))
            logger.warning("Error details:")
            for error in stats["errors"]:
                logger.warning("  %s", error)
        else:
            logger.info("No errors encountered")

        logger.info("Output files saved to: %s", output_dir)

    except KeyboardInterrupt:
        logger.warning("Feature extraction interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
