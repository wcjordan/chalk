# Research: Extend bump-python-deps.sh to cover tests/dev-requirements.txt

## Current State

`jenkins/bump-python-deps.sh` bumps Python deps for:
- `server/requirements.txt` and `server/dev-requirements.txt`
- `test_gen/requirements.txt` and `test_gen/dev-requirements.txt`
- `tests/requirements.txt` (skipping playwright)

It does NOT bump `tests/dev-requirements.txt`.

## tests/dev-requirements.txt contents

```
-r requirements.txt

# These are used for development or linting
black==26.10.1
flake8==7.3.0
pylint==4.0.6
```

It includes pinned versions of `black`, `flake8`, and `pylint`.
It references `requirements.txt` (which has `playwright` pinned), but playwright is NOT directly in dev-requirements.txt.

## Required Change

Two changes to `jenkins/bump-python-deps.sh`:

1. Add `pur -r dev-requirements.txt` to the tests section (line 25):
   ```bash
   (cd tests && pur --skip playwright -r requirements.txt && pur -r dev-requirements.txt)
   ```

2. Add `tests/dev-requirements.txt` to the `git add` block (after `tests/requirements.txt`).

The `--skip playwright` flag is not needed for `dev-requirements.txt` since playwright is not listed there directly. However, `pur` only processes requirements that are explicitly listed in the file, so the `-r requirements.txt` reference line won't cause pur to touch playwright.

## Why Simple

This is a one-file, two-line change to an existing shell script. No new dependencies, no logic changes — just adding coverage for the missing file.
