# Plan: Remove the SKIP_UNIT_TESTS parameter from Jenkins

## Overview

Unit tests were moved to GitHub Actions in PR #394. The GH Actions workflow runs tests and then triggers Jenkins with `SKIP_UNIT_TESTS=true`. This spec removes the parameter and the now-unused unit test stages from the Jenkins pipeline.

---

## Stage 1: Remove SKIP_UNIT_TESTS parameter and unit test stages from Jenkins

### Description

Remove the `SKIP_UNIT_TESTS` boolean parameter from `Jenkinsfile` along with all three unit test stages (`Test UI`, `Test UI Storybook`, `Test Server`) that were gated on it. Also remove the `chalk-ui-base` Docker image build from the `Build UI` stage since it was only used by the removed test stages. Finally, remove the `SKIP_UNIT_TESTS=true` parameter from the Jenkins trigger in `.github/workflows/unit-tests.yml`.

**Files to change:**

1. `Jenkinsfile`:
   - Remove the entire `parameters { ... }` block (lines 17–19) containing `SKIP_UNIT_TESTS`
   - Remove the `stage('Test UI')` block (lines 79–123) entirely
   - Remove the `stage('Test UI Storybook')` block (lines 124–183) entirely
   - Remove the `stage('Test Server')` block (lines 208–229) entirely
   - Remove the second `buildAndPushImage(...)` call in `stage('Build UI')` (lines 66–76) that builds `chalk-ui-base:${SANITIZED_BUILD_TAG}` with target `js_test_env` — only used by removed test stages

2. `.github/workflows/unit-tests.yml`:
   - Remove `--data-urlencode "SKIP_UNIT_TESTS=true" \` from the curl command in the `trigger-jenkins` job (line 122)

### Acceptance Criteria
- `Jenkinsfile` contains no reference to `SKIP_UNIT_TESTS`
- `Jenkinsfile` contains no `stage('Test UI')`, `stage('Test UI Storybook')`, or `stage('Test Server')` blocks
- `Jenkinsfile` does not build the `chalk-ui-base` image (target `js_test_env`)
- `.github/workflows/unit-tests.yml` Jenkins trigger curl command does not include `SKIP_UNIT_TESTS`
- Changes are committed and a PR is opened against the feature branch
