# Plan: Add a CODEOWNERS for wcjordan

## Overview

Add a `.github/CODEOWNERS` file to the chalk repository to require @wcjordan as a reviewer on every pull request. This mirrors the setup already in place in the minordomo repo.

---

## Stage 1: Create .github/CODEOWNERS

### Description

Create `.github/CODEOWNERS` at the repo root with a single rule that matches all files and requires @wcjordan as a reviewer. GitHub automatically reads this file and enforces the listed owners as required reviewers on any PR touching matching files.

File contents:
```
* @wcjordan
```

Commit the file once created.

### Acceptance Criteria

- `.github/CODEOWNERS` exists in the repository with content `* @wcjordan`
- The file is committed to the feature branch
- `make test` passes (no regressions from a config-only change)
