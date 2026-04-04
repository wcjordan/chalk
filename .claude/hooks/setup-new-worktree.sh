#!/bin/bash
# Sets up a new worktree with gitignored files and dependencies.
set -euo pipefail

INPUT=$(cat)
# The WorktreeCreate payload has no path field; derive the path from the worktree name.
# Worktrees are always created at $CLAUDE_PROJECT_DIR/.claude/worktrees/<name>.
NAME=$(echo "$INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['name'])")

if [ -z "$NAME" ]; then
  echo "setup-new-worktree: could not read name from hook input" >&2
  exit 1
fi

WORKTREE="${CLAUDE_PROJECT_DIR}/.claude/worktrees/${NAME}"

if [ -d "$WORKTREE" ]; then
  echo "setup-new-worktree: worktree already exists at $WORKTREE" >&2
  exit 1
fi

# Remove the worktree dir on failure so we don't leave partial state.
trap 'rm -rf "$WORKTREE"' ERR

# Create the git worktree on a new branch.
mkdir -p "${CLAUDE_PROJECT_DIR}/.claude/worktrees"
git -C "$CLAUDE_PROJECT_DIR" worktree add "$WORKTREE" -b "$NAME" HEAD >&2

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

# Output the worktree path on stdout — the tool uses this as the handoff signal.
echo "$WORKTREE"
