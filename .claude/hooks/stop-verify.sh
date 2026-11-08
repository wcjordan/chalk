#!/bin/bash
# Verification gate: block agent stop if there are uncommitted changes and checks fail.
# Only runs when there is actual work to verify — skips clean working trees.

input=$(cat)

# Already continuing because of this hook; don't loop.
if echo "$input" | grep -q '"stop_hook_active": *true'; then
  exit 0
fi

# Only verify when files covered by `make test` changed.
if ! git diff HEAD --name-only | grep -qE '^(server|ui|tests)/'; then
  exit 0
fi

# Docker down is something only the user can fix: warn without blocking (exit 1).
if ! docker info > /dev/null 2>&1; then
  echo "Docker is not running — changes are unverified. Start Docker and run make test." >&2
  exit 1
fi

if ! make test 2>&1; then
  echo "tests failed — fix before stopping" >&2
  exit 2
fi
