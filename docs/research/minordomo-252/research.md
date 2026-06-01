# Research: Add CODEOWNERS for wcjordan

## Summary

The task is to add a `.github/CODEOWNERS` file to the chalk repository so that @wcjordan is required as a reviewer on every pull request.

## Reference Implementation

The minordomo repo has the identical setup at `.github/CODEOWNERS`:

```
* @wcjordan
```

Commit reference: https://github.com/wcjordan/minordomo/commit/46e82c48236661092118beac293a7df070e201ba

## Current State

- No `CODEOWNERS` file exists anywhere in the chalk repo.
- `.github/` directory exists at repo root, containing `workflows/ci.yml` and `workflows/codeql-analysis.yml`.
- GitHub reads CODEOWNERS from `.github/CODEOWNERS`, `CODEOWNERS`, or `docs/CODEOWNERS`.

## Implementation

Single file to create: `.github/CODEOWNERS` with content `* @wcjordan`.

No tests or code changes required — this is a pure GitHub configuration file.
