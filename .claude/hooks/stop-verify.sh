#!/bin/bash
# Verification gate: block agent stop if there are uncommitted changes and checks fail.
# Only runs when there is actual work to verify — skips clean working trees.

if git diff --quiet && git diff --cached --quiet; then
  exit 0
fi

if ! docker info > /dev/null 2>&1; then
  echo "Docker is not running — start Docker and re-run, or ask for help." >&2
  exit 2
fi

if ! make test 2>&1; then
  echo "tests failed — fix before stopping" >&2
  exit 2
fi
