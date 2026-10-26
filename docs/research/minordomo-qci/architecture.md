# CI Architecture Research — minordomo-qci

## Current Jenkins CI Pipeline (Jenkinsfile)

Stages (in order):
1. **Init** — load changeset helper groovy; decide whether to run integration tests
2. **Build (parallel)**
   - **UI**: Build `chalk-ui` and `chalk-ui-base` Docker images via `docker buildx`, push to GAR (`us-east4-docker.pkg.dev/<project>/default-gar/`)
   - **Server**: Build `chalk-server` Docker image via `docker buildx`, push to GAR
3. **Test (sequential within each parallel track)**
   - **Test UI** — runs `make test-inner` inside the `chalk-ui-base` container (eslint, tsc, jest)
   - **Test UI Storybook** — two-container pod: one serves storybook-static via http-server, one runs `make test-storybook-inner`
   - **Test Server** — runs `pip install + make test-inner` inside a `python:3.12-bookworm` container (flake8, pylint, django unit tests)
4. **Integration Tests** (skipped if only docs/test_gen/.github changed)
   - Deploys a temporary Helm release to GKE namespace `test`
   - Runs Playwright tests against that deployment via BrowserStack
   - Tears down the Helm release in `post.always`
5. **Continuous Deployment** (only on `main`)
   - Deploys to `chalk-prod` Helm release in GKE namespace `prod`

### Changeset logic
- Integration tests skipped when ALL changed files are in: `.github/`, `test_gen/`, `docs/`
- Integration tests always run on `main`

### Credentials required by Jenkins
- `chalk-prod-cd-sentry-dsn` — Sentry DSN for UI build
- `jenkins-gke-sa` — GCP SA key file for GKE access (integration tests + CD)
- `chalk-prod-cd-oauth-web-client-json` — OAuth JSON for Helm deploy
- `chalk-prod-cd-oauth-refresh-token` — OAuth refresh token for Playwright tests
- `browserstack_key` — BrowserStack username + access key
- `chalk-prod-cd-server-db-password` — Prod DB password (CD only)
- `chalk-prod-cd-permitted-users` — Prod permitted users (CD only)
- `chalk-prod-cd-server-secret-key` — Prod Django secret key (CD only)
- `github-app` — GitHub App credentials (used in bump-python-deps Jenkinsfile)

### GAR Image Caching
Build cache is stored in GAR:
- `chalk-ui-cache:ci_app` / `chalk-ui-cache:ci_test` (for UI builds)
- `chalk-server-cache:ci_server` (for server builds)

## Existing GH Actions

`/.github/workflows/ci.yml` — only covers `test_gen` module:
- Sets up Python 3.11, installs `test_gen/dev-requirements.txt`, runs `python -m pytest -v */tests`

## Test Commands (can run natively without Docker)

### Server unit tests
```bash
pip install -r server/dev-requirements.txt
cd server
env $(grep -v "^#" ../.env_default | xargs) DOMAIN=localhost SECRET_KEY=testkey make test-inner
# make test-inner runs: flake8, pylint, django test chalk.todos
```

### UI unit tests (natively with Node 24 + corepack/yarn)
```bash
cd ui/js
corepack enable && yarn install --immutable
# Lint
yarn eslint --max-warnings=0 .
# Typecheck
yarn tsc
# Jest
yarn jest
```

### UI Storybook tests (need pre-built storybook)
```bash
cd ui/js
STORYBOOK_TEST_ENV=true npx storybook build --test --quiet  # build storybook-static
# Then run test-storybook in background, serve storybook from storybook-static
npx http-server -p 9009 ./storybook-static &
npx test-storybook --no-index-json --url http://127.0.0.1:9009
```

## Integration Test Requirements
- GKE cluster `<project>-gke` in zone `us-east4-c`
- Helm deploy to `test` namespace with unique name based on BUILD_TAG
- Wait for server readiness + healthz endpoint
- BrowserStack for cross-browser Playwright tests
- OAuth refresh token for authentication
- Teardown in `post.always`

## Other Jenkins Jobs in chalk repo
- `jenkins/bump-python-deps.Jenkinsfile` — weekly cron (on main) bumps Python deps, opens PR via GitHub App

## Key Questions for Spec

1. **Scope**: Unit tests only (server + UI + storybook)? Or also integration tests (GKE + BrowserStack)? Or also CD (deploy to prod on main)?
2. **GCP Auth**: Workload Identity Federation (WIF) or SA key stored as GH secret?
3. **Existing Jenkinsfile**: Keep alongside GH Actions initially, or remove as part of this epic?
4. **bump-python-deps**: In scope to migrate to GH Actions scheduled workflow?
