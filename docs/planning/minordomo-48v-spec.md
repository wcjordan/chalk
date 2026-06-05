# Implementation Plan: Fix failing CodeQL actions

GitHub Issue: https://github.com/wcjordan/chalk/issues/312

## Summary

The `.github/workflows/codeql-analysis.yml` workflow uses deprecated `github/codeql-action` v1.
This single-stage fix upgrades the workflow to v3 and adds the required `security-events: write`
permission.

---

## Stage 1: Upgrade CodeQL workflow from v1 to v3

### Description

Update `.github/workflows/codeql-analysis.yml` to use current, supported versions of the
CodeQL GitHub Actions:

1. Change all three `github/codeql-action/*@v1` references to `@v3`:
   - `github/codeql-action/init@v1` → `github/codeql-action/init@v3`
   - `github/codeql-action/autobuild@v1` → `github/codeql-action/autobuild@v3`
   - `github/codeql-action/analyze@v1` → `github/codeql-action/analyze@v3`
2. Add `security-events: write` to the workflow permissions block (required by v3 for SARIF upload).
3. Update `actions/checkout@v2` → `actions/checkout@v4`.
4. Remove the now-unnecessary `fetch-depth: 2` option from the checkout step.

### Acceptance Criteria

- All three `@v1` references are replaced with `@v3` in `codeql-analysis.yml`
- The `permissions` block includes `security-events: write`
- `actions/checkout` is at `@v4`
- No other workflow files are modified
- `make test` passes (linting/unit tests unaffected by a CI workflow change)
- A commit is created and pushed with a descriptive message
