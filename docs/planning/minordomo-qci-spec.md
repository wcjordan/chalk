# Implementation Plan: Switch CI to GitHub Actions (Unit Tests + Jenkins Handoff)

**Epic:** minordomo-qci  
**GH Issue:** https://github.com/wcjordan/chalk/issues/381

## Overview

Move unit tests (server + UI + storybook) to GitHub Actions while keeping Jenkins for
Docker builds, integration tests, and CD. After GH Actions unit tests pass, it triggers
Jenkins via REST API with `SKIP_UNIT_TESTS=true` so Jenkins skips the test stages
but still builds Docker images and runs the downstream pipeline.

### Out of scope
- Workload Identity Federation (GH Actions unit tests run natively — no Docker/GAR needed)
- `bump-python-deps` scheduled Jenkins job migration
- Moving integration tests or CD to GH Actions

### Manual admin steps (required before or immediately after merge)
1. Create three GitHub Actions secrets on the `chalk` repo:
   - `JENKINS_URL` — base URL of the Jenkins instance
   - `JENKINS_USERNAME` — Jenkins API user
   - `JENKINS_API_KEY` — Jenkins API key / token
2. Disable the GitHub → Jenkins webhook so pushes no longer trigger Jenkins directly
   (until disabled, every push will trigger Jenkins twice: once by webhook and once by GH Actions)
3. Update branch protection required-check names from Jenkins check names to the new
   GH Actions job names: `test-server`, `test-ui`, `test-storybook`

---

## Stage 1: GH Actions unit test workflow

### Description

Create `.github/workflows/unit-tests.yml` with three jobs running natively (no Docker):

- **`test-server`** — Python 3.12, pip cache, installs `server/dev-requirements.txt`,
  runs `flake8`, `pylint`, and Django unit tests via `make test-inner`
- **`test-ui`** — Node (version matched to project), yarn cache, runs eslint, tsc, jest
- **`test-storybook`** — same Node setup; builds storybook with
  `STORYBOOK_TEST_ENV=true npx storybook build --test --quiet`, serves it with
  `npx http-server -p 9009`, then runs `npx test-storybook --no-index-json`

Trigger: `push` to `main` and `pull_request` targeting `main` — same surfaces as the
existing `ci.yml`.

Do **not** modify the existing `test_rrweb_ingest` job in `ci.yml`.

Use `actions/cache` (or the built-in cache flags on `actions/setup-python` /
`actions/setup-node`) for pip and yarn to keep runs fast.

Server test environment: set `DOMAIN=localhost SECRET_KEY=testkey` and source the
remaining vars from `.env_default` (use `grep -v "^#" .env_default` pattern).

### Acceptance Criteria
- New workflow file exists at `.github/workflows/unit-tests.yml`
- All three jobs run on pushes/PRs to `main`
- Server job runs flake8, pylint, and Django tests; passes on the current codebase
- UI job runs eslint, tsc, and jest; passes on the current codebase
- Storybook job builds storybook, serves it, and runs test-storybook; passes
- Pip and yarn caches are configured
- Existing `ci.yml` and its `test_rrweb_ingest` job are unchanged

---

## Stage 2: Add SKIP_UNIT_TESTS parameter to Jenkinsfile

### Description

Add a boolean `SKIP_UNIT_TESTS` parameter to `Jenkinsfile`. When `true`, the three Test
stages are skipped but the two Build stages continue to run — the Docker images they
produce are still required by the Integration Tests and CD stages.

Specifically, add `when { not { params.SKIP_UNIT_TESTS } }` (or equivalent) to:
- `Test UI` stage
- `Test UI Storybook` stage
- `Test Server` stage

Do **not** add this condition to `Build UI` or `Build Server` — those must keep running
so that Docker images tagged with `SANITIZED_BUILD_TAG` are available for deployment.

Verify the parameter declaration syntax is compatible with the existing pipeline (declarative
Jenkins pipeline uses `parameters { booleanParam(name: 'SKIP_UNIT_TESTS', defaultValue: false, ...) }`
at the top-level pipeline block).

### Acceptance Criteria
- `SKIP_UNIT_TESTS` boolean parameter added to `Jenkinsfile`
- Default value is `false` (existing behavior unchanged when not set)
- `Test UI`, `Test UI Storybook`, and `Test Server` stages are skipped when `SKIP_UNIT_TESTS=true`
- `Build UI` and `Build Server` stages still run regardless of `SKIP_UNIT_TESTS`
- `Integration Tests` and `Continuous Deployment` stages are unaffected
- The Jenkinsfile passes a syntax check (can be verified locally with `jenkins-linter` or
  by reviewing declarative pipeline syntax docs)

---

## Stage 3: GH Actions → Jenkins handoff trigger

### Description

After all three unit-test jobs pass, the GH Actions workflow triggers Jenkins via the
REST API so integration tests and CD still run.

Add a `trigger-jenkins` job to `.github/workflows/unit-tests.yml` that:
1. Depends on `test-server`, `test-ui`, and `test-storybook` (runs only when all pass)
2. Calls the Jenkins multibranch pipeline API:

   ```
   POST $JENKINS_URL/job/chalk/job/<url-encoded-branch>/buildWithParameters
   ```
   with `SKIP_UNIT_TESTS=true`. Note: slashes in branch names must be URL-encoded as `%2F`.

3. Authenticates using HTTP Basic Auth with `JENKINS_USERNAME` and `JENKINS_API_KEY`
   secrets.
4. Passes the triggering commit SHA so Jenkins builds the correct commit (use the
   `token` parameter or a `GIT_COMMIT` build parameter if supported by the Jenkins
   job; verify empirically).

Secrets referenced: `JENKINS_URL`, `JENKINS_USERNAME`, `JENKINS_API_KEY`.

**Note:** Until the GitHub → Jenkins webhook is disabled (a manual admin step), every
push will trigger Jenkins twice — once by the webhook (full pipeline) and once by this
step (with SKIP_UNIT_TESTS=true). This is wasteful but not broken. The PR description
must call out that the webhook disable is required immediately after merge.

### Acceptance Criteria
- `trigger-jenkins` job added to the unit-tests workflow
- Job only runs after all three unit-test jobs pass (correct `needs:` dependency)
- Job is skipped (not failed) when triggered by Dependabot or other bots that lack
  secrets access (use `if: github.actor != 'dependabot[bot]'` or similar guard)
- On success, a new Jenkins build is triggered for the correct branch with
  `SKIP_UNIT_TESTS=true`
- The trigger step uses the `JENKINS_URL`, `JENKINS_USERNAME`, `JENKINS_API_KEY` secrets
- A comment in the workflow file or the PR description documents the manual steps:
  disable the GH→Jenkins webhook and update branch protection required checks
