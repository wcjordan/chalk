# Implementation Spec: Extend bump-python-deps.sh to cover tests/dev-requirements.txt

GH Issue: https://github.com/wcjordan/chalk/issues/390

## Background

`jenkins/bump-python-deps.sh` automatically bumps pinned Python dependency versions using `pur`. It currently processes `tests/requirements.txt` (skipping `playwright`) but omits `tests/dev-requirements.txt`, which contains pinned versions of `black`, `flake8`, and `pylint`.

This spec adds `tests/dev-requirements.txt` to the bump script.

---

## Stage 1: Add tests/dev-requirements.txt to bump-python-deps.sh

### Description

Extend `jenkins/bump-python-deps.sh` to run `pur` against `tests/dev-requirements.txt` and include it in the `git add` block.

Changes to `jenkins/bump-python-deps.sh`:
1. Update the `tests` pur command (line 25) to also bump `dev-requirements.txt`:
   ```bash
   (cd tests && pur --skip playwright -r requirements.txt && pur -r dev-requirements.txt)
   ```
2. Add `tests/dev-requirements.txt` to the `git add` block.

### Acceptance Criteria
- `jenkins/bump-python-deps.sh` runs `pur -r dev-requirements.txt` inside the `tests/` directory.
- `tests/dev-requirements.txt` is included in the `git add` block alongside `tests/requirements.txt`.
- Running `shellcheck jenkins/bump-python-deps.sh` (or `make test`) passes with no new errors.
- The script's overall structure and error-handling behavior (`set -euo pipefail`) is unchanged.
