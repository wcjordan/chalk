# Getting Around

## Backend (`server/chalk/`)

**Django app structure:**
- `chalk/todos/` - Main app containing all todo logic
  - `models.py` - Todo and Label models with django-simple-history for change tracking
  - `views.py` - REST API viewsets for todos, labels, and work contexts
  - `oauth.py` - Custom Google OAuth authentication backend
  - `serializers.py` - DRF serializers
  - `signals.py` - Django signals for model events
  - `tests.py` - Unit tests

**Settings:**
- `chalk/settings/base.py` - Base Django configuration
- `chalk/settings/production.py` - Production overrides
- `chalk/settings/testing.py` - Test configuration

**Authentication:**
- Uses custom `OAuthBackend` with Google OAuth
- Session-based authentication for web, token-based for mobile
- User permissions controlled via `PERMITTED_USERS` environment variable

**Database:**
- PostgreSQL with django-simple-history for audit trails
- Local dev uses a starter database restored from `db/starter_db/`

## Frontend (`ui/js/src/`)

**React Native + Expo architecture:**
- `App.tsx` - Root component with provider setup
- `components/` - React Native Paper components for UI
- `redux/` - Redux Toolkit state management
  - `store.ts` - Store configuration
  - `reducers.ts` - Root reducer combining slices
  - `todosApiSlice.ts` - RTK Query API for todos
  - `labelsApiSlice.ts` - RTK Query API for labels
  - `workspaceSlice.ts` - Client-side workspace state (filtering, UI settings)
  - `shortcutSlice.ts` - Keyboard shortcut state
  - `notificationsSlice.ts` - Toast notification state
  - `fetchApi.ts` - Base API configuration with auth handling
- `selectors.ts` - Memoized selectors for derived state
- `hooks/` - Custom React hooks

**Key patterns:**
- Uses Redux Toolkit's `createAsyncThunk` for API calls
- RTK Query for data fetching with automatic caching
- React Native Paper for Material Design components
- Expo for cross-platform native functionality
- Storybook for component development and visual regression testing

**Build targets:**
- Web: Expo web build
- Android: EAS Build with separate dev/preview/production profiles
- Testing: Containerized Jest + Storybook test runner

## Integration Tests (`tests/`)

**Playwright test structure:**
- `conftest.py` - Pytest fixtures including BrowserStack setup
- `*_test.py` - Test files for specific features
- `helpers/` - Shared test helper functions
  - `todo_helpers.py` - Todo CRUD operations
  - `label_helpers.py` - Label filtering operations

**Running integration tests:**
- Tests run against deployed environments (dev/CI/prod)
- Use OAuth refresh token for authentication (set in `.env`)
- BrowserStack credentials required for remote execution
- Each test creates temporary todos with unique prefixes for cleanup

**Running unit tests and linting:**
For the Chalk application
- To run unit tests & lint, run `make test` from `<PROJECT_ROOT>`
- To format the server code, run `make format` from `<PROJECT_ROOT>/server`
- To format the ui code, run `make format` from `<PROJECT_ROOT>/ui`

For the test_gen module
- To run unit tests, run `make test` from `<PROJECT_ROOT>/test_gen`
- To lint, run `make lint` from `<PROJECT_ROOT>/test_gen`
- To format the code, run `make format` from `<PROJECT_ROOT>/test_gen`

## Test Generation System (`test_gen/`)

**Three-module pipeline for processing rrweb session recordings:**

1. **`rrweb_ingest/`** - Main ingestion pipeline
   - `ingest_session(session_id, filepath)` - Entry point for processing
   - `load_events()` - Loads and validates rrweb JSON
   - `filter_events()` - Removes noise (micro-scrolls, mousemoves)
   - `extract_features()` - Extracts user interactions and DOM mutations

2. **`rrweb_util/`** - Shared utilities
   - `dom_state/` - DOM state tracking and node metadata extraction
   - `user_interaction/` - User interaction models and extractors
   - `helpers/` - Common helper functions

3. **`rule_engine/`** - Rule-based matching
   - `match_session()` - Matches rules against session features
   - `load_rules()` - Loads rule definitions from YAML files

This system is separate from the main Chalk app with no shared dependencies.
It processes session recordings for test generation research and is used to improve the repo's integration tests.

## Deployment & Infrastructure

**Local development:**
- Uses Tilt to orchestrate Kubernetes development environment
- Nginx proxy for routing (`dev_nginx.conf`)
- Expo dev server for hot reloading mobile changes

**Containerization:**
- All components build as Docker images pushed to GCP Artifact Registry
- Multi-stage builds with build caching
- `Dockerfile` in each component directory

**CI/CD:**
- Hybrid CI: GitHub Actions runs unit tests natively; Jenkins handles Docker builds, integration tests, and CD
- Unit test workflow: `.github/workflows/unit-tests.yml` — runs `test-server`, `test-ui`, `test-storybook` jobs on push/PR to `main`
- After unit tests pass, GH Actions triggers Jenkins (`$JENKINS_URL/job/chalk/job/<branch>/buildWithParameters`) with `SKIP_UNIT_TESTS=true`
- Jenkins `Jenkinsfile` accepts `SKIP_UNIT_TESTS` boolean parameter: when true, Test stages are skipped but Build stages (and integration tests/CD) still run
- Separate base image build (`jenkins/Jenkinsfile.base`)
- BrowserStack integration for E2E tests
- Sentry integration for error tracking
- **Pending manual admin steps (required for full migration):** disable the GitHub→Jenkins webhook on the chalk repo (until disabled, every push triggers Jenkins twice); update branch protection required-check names from Jenkins check names to GH Actions job names (`test-server`, `test-ui`, `test-storybook`); create GH Actions secrets `JENKINS_URL`, `JENKINS_USERNAME`, `JENKINS_API_KEY` on the chalk repo

**Kubernetes:**
- Helm charts in `helm/` directory
- GCP workload identity for service account authentication
- Separate deployments for prod/staging/dev/CI environments
- CloudSQL PostgreSQL database
