"""
Module entry point for feature_extraction CLI.

Allows running the feature extraction CLI using:
python -m feature_extraction [args]
"""

from .extract_features_cli import main

if __name__ == "__main__":
    main()