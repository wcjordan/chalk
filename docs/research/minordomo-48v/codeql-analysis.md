# CodeQL Actions Research

## Problem

The `.github/workflows/codeql-analysis.yml` workflow uses `github/codeql-action` v1, which was
deprecated on January 18, 2023, and is no longer updated or supported.

Affected action references:
- `github/codeql-action/init@v1`
- `github/codeql-action/autobuild@v1`
- `github/codeql-action/analyze@v1`

Also uses `actions/checkout@v2` which should be updated.

## Fix

Update all three `github/codeql-action/*@v1` references to `@v3`.

CodeQL v3 also requires `permissions.security-events: write` so the analyze step can upload
SARIF results to GitHub. The current workflow only has `contents: read`.

Update `actions/checkout@v2` to `@v4` while at it.

## Languages

Current matrix: `['javascript', 'python']` — these names are still valid in v3.

## No structural changes needed

The overall workflow structure (checkout → init → autobuild → analyze) is still correct for v3.
The `fetch-depth: 2` is no longer required by v3 but is harmless; can remove for cleanliness.
