# Research: Remove SKIP_UNIT_TESTS from Jenkins

## Background

PR #394 moved unit tests to GitHub Actions (`unit-tests.yml`). The GH Actions workflow:
1. Runs `test-server`, `test-ui`, `test-storybook` jobs
2. After tests pass, triggers Jenkins via `trigger-jenkins` job with `SKIP_UNIT_TESTS=true`

## Current State in Jenkinsfile

The Jenkinsfile has:
- `parameters { booleanParam(name: 'SKIP_UNIT_TESTS', ...) }` (line 17-19)
- Three unit test stages gated by `when { expression { !params.SKIP_UNIT_TESTS } }`:
  - `Test UI` (uses `chalk-ui-base` image, runs `make test-inner`)
  - `Test UI Storybook` (uses `chalk-ui-base` image, runs `make test-storybook-inner`)
  - `Test Server` (runs Django tests via `make test-inner`)
- `Build UI` stage builds two images:
  - `chalk-ui:$SANITIZED_BUILD_TAG` (target `js_app_prod`) — used for deployment
  - `chalk-ui-base:$SANITIZED_BUILD_TAG` (target `js_test_env`) — only used by test stages

## Current State in unit-tests.yml

The `trigger-jenkins` job POSTs `--data-urlencode "SKIP_UNIT_TESTS=true"` when triggering Jenkins.

## Required Changes

1. **Jenkinsfile**:
   - Remove `parameters` block with `SKIP_UNIT_TESTS`
   - Remove `Test UI` stage entirely
   - Remove `Test UI Storybook` stage entirely
   - Remove `Test Server` stage entirely
   - Remove `chalk-ui-base` image build from `Build UI` stage (only used by removed test stages)

2. **.github/workflows/unit-tests.yml**:
   - Remove `--data-urlencode "SKIP_UNIT_TESTS=true"` from curl command in `trigger-jenkins` job

## Files to Change
- `Jenkinsfile`
- `.github/workflows/unit-tests.yml`
