#!/usr/bin/env python3
"""
Command-line interface for feature extraction.

This module provides a CLI tool to extract features from rrweb session files
and save them as JSON files for use by the rule engine or other analysis tools.
"""

import argparse
import sys
from pathlib import Path

from .pipeline import extract_and_save_features


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Extract features from rrweb session files and save as JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract features from all sessions in data/output_sessions
  python -m feature_extraction.extract_features_cli

  # Extract features with custom input and output directories
  python -m feature_extraction.extract_features_cli --session_dir data/my_sessions --output_dir data/my_features

  # Process only first 10 sessions with verbose output
  python -m feature_extraction.extract_features_cli --max-sessions 10 --verbose
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

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print detailed progress information",
    )

    args = parser.parse_args()

    # Convert paths to Path objects and validate
    session_dir = Path(args.session_dir)
    output_dir = Path(args.output_dir)

    if not session_dir.exists():
        print(
            f"Error: Session directory does not exist: {session_dir}", file=sys.stderr
        )
        sys.exit(1)

    if not session_dir.is_dir():
        print(f"Error: Session path is not a directory: {session_dir}", file=sys.stderr)
        sys.exit(1)

    # Check if session directory contains any JSON files
    json_files = list(session_dir.glob("*.json"))
    if not json_files:
        print(
            f"Warning: No JSON files found in session directory: {session_dir}",
            file=sys.stderr,
        )

    if args.verbose:
        print(f"Feature Extraction CLI")
        print(f"======================")
        print(f"Session directory: {session_dir}")
        print(f"Output directory: {output_dir}")
        print(f"Max sessions: {args.max_sessions or 'unlimited'}")
        print(f"Found {len(json_files)} JSON files")
        print()

    try:
        # Run the feature extraction
        stats = extract_and_save_features(
            session_dir=str(session_dir),
            output_dir=str(output_dir),
            max_sessions=args.max_sessions,
            verbose=args.verbose,
        )

        # Print final summary
        if args.verbose:
            print(f"\n{'='*50}")

        print(f"Feature extraction completed successfully!")
        print(f"Sessions processed: {stats['sessions_processed']}")
        print(f"Feature chunks saved: {stats['chunks_saved']}")

        # Print feature type counts if any were extracted
        feature_counts = stats["total_features"]
        total_feature_count = sum(count for count in feature_counts.values())

        if total_feature_count > 0:
            print(f"Total features extracted: {total_feature_count:,}")
            if args.verbose:
                print(f"Feature breakdown:")
                for feature_type, count in feature_counts.items():
                    if count > 0:
                        print(f"  {feature_type}: {count:,}")

        # Print error summary
        if stats["errors"]:
            print(f"Errors encountered: {len(stats['errors'])}")
            if args.verbose:
                print("Error details:")
                for error in stats["errors"]:
                    print(f"  {error}")
        else:
            print("No errors encountered")

        print(f"Output files saved to: {output_dir}")

    except KeyboardInterrupt:
        print(f"\nFeature extraction interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error during feature extraction: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
