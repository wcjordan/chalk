"""
Module entry point for ingesting rrweb sessions via CLI.

Allows running the ingest CLI using:
python -m rrweb_ingest [args]
"""

from .cli import main

if __name__ == "__main__":
    main()
