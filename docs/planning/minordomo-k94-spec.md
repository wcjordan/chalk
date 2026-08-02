# minordomo-k94: Add a Jenkins job to bump Python deps

## Overview

Add a weekly Jenkins pipeline that uses `pur` to update pinned Python dependency
versions across three directories (`server/`, `test_gen/`, `tests/`). When updates
are found, the job commits them to a dated branch and opens a PR against `main`.

---

## Stage 1: Add Jenkins pipeline and bump script

### Description

Create two files in `jenkins/`:

1. **`jenkins/bump-python-deps.Jenkinsfile`** — Pipeline definition with a weekly cron
   trigger (`H H * * 1` on `main`). Uses a `python:3.12-bookworm` pod. The step:
   - Installs `pur` via pip and `gh` CLI via the official GitHub apt repo
   - Exports `GH_TOKEN="${GH_APP_PSW}"` and runs `gh auth setup-git`
   - Configures `git user.email` and `git user.name`
   - Calls `bash jenkins/bump-python-deps.sh`
   The `GH_APP` Jenkins credential (username-password) must be bound as
   `environment { GH_APP = credentials('github-app') }`.
   Include `@Library('jenkins-shared-library') _` at the top and
   `post { failure { notifyFailure() } }` to match the main Jenkinsfile pattern.

2. **`jenkins/bump-python-deps.sh`** — Shell script (bash, `set -euo pipefail`) that:
   - Creates a branch named `chore/bump-python-deps-$(date +%Y%m%d)`
   - Runs pur in each directory:
     ```bash
     (cd server && pur -r requirements.txt && pur -r dev-requirements.txt)
     (cd test_gen && pur -r requirements.txt && pur -r dev-requirements.txt)
     (cd tests && pur --skip playwright -r requirements.txt)
     ```
   - Exits 0 with a message if `git diff --quiet` (no changes)
   - Stages the five requirement files, commits, pushes, and opens a PR via `gh pr create`
     targeting `main` with title `"chore: bump Python dependencies"`

Commit the two files and any no-op touch to verify shellcheck passes.

### Acceptance Criteria

- `jenkins/bump-python-deps.Jenkinsfile` exists with a weekly cron trigger, `GH_APP`
  credential binding, and calls `jenkins/bump-python-deps.sh`
- `jenkins/bump-python-deps.sh` exists, is executable, and passes `shellcheck`
- Script correctly skips `playwright` in `tests/` and bumps both `requirements.txt`
  and `dev-requirements.txt` in `server/` and `test_gen/`
- Script exits 0 without creating a branch or PR when there are no changes
- Code committed and pushed to the feature branch with a clear commit message
