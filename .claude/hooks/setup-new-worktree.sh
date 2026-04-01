#!/bin/bash
# Sets up a new worktree with gitignored files and dependencies.
set -euo pipefail

INPUT=$(cat)
WORKTREE=$(echo "$INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['worktree_path'])")

if [ -z "$WORKTREE" ]; then
  echo "setup-new-worktree: could not read worktree_path from hook input" >&2
  exit 1
fi

# Copy gitignored .env so the worktree can run make targets
if [ -f "${CLAUDE_PROJECT_DIR}/.env" ]; then
  cp "${CLAUDE_PROJECT_DIR}/.env" "${WORKTREE}/.env"
  echo "Copied .env to ${WORKTREE}/"
fi

# Initialize test_gen dependencies
if [ -d "${WORKTREE}/test_gen" ]; then
  (cd "${WORKTREE}/test_gen" && make init)
  echo "Initialized test_gen in ${WORKTREE}/test_gen/"
fi

# Install JS dependencies so husky pre-commit hooks work in the worktree
if [ -d "${WORKTREE}/ui/js" ]; then
  (cd "${WORKTREE}/ui/js" && yarn install --immutable)
  echo "Installed JS dependencies in ${WORKTREE}/ui/js/"
fi

# Copy local Claude settings (gitignored)
if [ -f "${CLAUDE_PROJECT_DIR}/.claude/settings.local.json" ]; then
  mkdir -p "${WORKTREE}/.claude"
  cp "${CLAUDE_PROJECT_DIR}/.claude/settings.local.json" "${WORKTREE}/.claude/settings.local.json"
  echo "Copied settings.local.json to ${WORKTREE}/.claude/"
fi
