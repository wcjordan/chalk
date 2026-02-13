#!/bin/bash
set -ex

BRANCH_NAME=$1
if [ -z "$BRANCH_NAME" ]; then
    echo "Branch name is not set. Please provide the name of the branch you want to create."
    exit 1
fi

WORKTREE_DIR=~/git/chalk-worktrees
mkdir -p "$WORKTREE_DIR"
git worktree add -b "$BRANCH_NAME" "$WORKTREE_DIR/$BRANCH_NAME" origin/main

# Install JS dependencies so that the husky pre-commit hooks work in the worktree
(cd "$WORKTREE_DIR/$BRANCH_NAME/ui/js" && yarn install --immutable)

# Setup Claude
if [ -f .claude/settings.local.json ]; then
    mkdir -p "$WORKTREE_DIR/$BRANCH_NAME/.claude"
    cp .claude/settings.local.json "$WORKTREE_DIR/$BRANCH_NAME/.claude/"
else
    echo "Warning: .claude/settings.local.json not found; skipping Claude setup for $WORKTREE_DIR/$BRANCH_NAME" >&2
fi

echo "Working in $WORKTREE_DIR/$BRANCH_NAME"
