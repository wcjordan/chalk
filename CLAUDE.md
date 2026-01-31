# CLAUDE.md

## Project Overview

Chalk is a full-stack todo application with three main components:
1. **Django REST API** (`server/`) - PostgreSQL backend with Google OAuth authentication
2. **React Native + Expo UI** (`ui/js/`) - Cross-platform mobile/web frontend using Redux Toolkit
3. **Playwright E2E Tests** (`tests/`) - Integration tests running on BrowserStack

The app also includes a separate **test generation system** (`test_gen/`) for processing rrweb session recordings into structured features for test generation.

## Architecture

### Backend (`server/chalk/`)

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

### Frontend (`ui/js/src/`)

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

### Integration Tests (`tests/`)

**Playwright test structure:**
- `conftest.py` - Pytest fixtures including BrowserStack setup
- `*_test.py` - Test files for specific features
- `helpers/` - Shared test helper functions
  - `todo_helpers.py` - Todo CRUD operations
  - `label_helpers.py` - Label filtering operations

**Running tests:**
- Tests run against deployed environments (dev/CI/prod)
- Use OAuth refresh token for authentication (set in `.env`)
- BrowserStack credentials required for remote execution
- Each test creates temporary todos with unique prefixes for cleanup

### Test Generation System (`test_gen/`)

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
It processes session recordings for test generation research and is used to improve the repos integration tests.

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
- Jenkins-based continuous delivery (`Jenkinsfile`)
- Separate base image build (`jenkins/Jenkinsfile.base`)
- BrowserStack integration for E2E tests
- Sentry integration for error tracking

**Kubernetes:**
- Helm charts in `helm/` directory
- GCP workload identity for service account authentication
- Separate deployments for prod/staging/dev/CI environments
- CloudSQL PostgreSQL database

## Code Style

**Python:**
- Format with `yapf` (server) or `black` (test_gen)
- Lint with `flake8` and `pylint`
- Style configs: `server/.style.yapf`, `test_gen/` uses black defaults

**JavaScript/TypeScript:**
- Format with Prettier
- Lint with ESLint (includes import ordering)
- TypeScript strict mode enabled
- Use `make fix-imports` to auto-fix import order

**Pre-commit hooks:**
- Configured with Husky in `ui/js/`
- Runs formatters on staged files before commit

## Development Philosophy

### Core Beliefs

- **Incremental progress over big bangs** - Small changes that compile and pass tests
- **Learning from existing code** - Study and plan before implementing
- **Pragmatic over dogmatic** - Adapt to project reality
- **Clear intent over clever code** - Be boring and obvious

### Simplicity Means

- Single responsibility per function/class
- Avoid premature abstractions
- No clever tricks - choose the boring solution
- If you need to explain it, it's too complex

## Process

### 1. Planning & Staging

Break complex work into 3-5 stages. Document in `<PROJECT_ROOT>/IMPLEMENTATION_PLAN.md`:

```markdown
## Stage N: [Name]
**Goal**: [Specific deliverable]
**Success Criteria**: [Testable outcomes]
**Tests**: [Specific test cases]
**Status**: [Not Started|In Progress|Complete]
```
- Update status as you progress
- Remove file when all stages are done

### 2. Implementation Flow

1. **Understand** - Study existing patterns in codebase
2. **Test** - Write test first (red)
3. **Implement** - Minimal code to pass (green)
4. **Check-in** - Stop and ask to confirm tests are passing
4. **Refactor** - Clean up with tests passing
5. **Commit** - With clear message linking to plan

### 3. When Stuck (Stop after 3 attempts per issue)

**CRITICAL**: Maximum 3 attempts per issue, then STOP.

1. **Document what failed**:
   - What you tried
   - Specific error messages
   - Why you think it failed

2. **Research alternatives**:
   - Find 2-3 similar implementations
   - Note different approaches used

3. **Question fundamentals**:
   - Is this the right abstraction level?
   - Can this be split into smaller problems?
   - Is there a simpler approach entirely?

4. **Try different angle**:
   - Different library/framework feature?
   - Different architectural pattern?
   - Remove abstraction instead of adding?

## Technical Standards

### Architecture Principles

- **Composable architecture** - Create composable components with minimal responsibilities
- **Explicit over implicit** - Clear data flow and dependencies
- **Test-driven when possible** - Never disable tests, fix them

### Code Quality

- **Before committing**:
  - Stop and ask for confirmation that tests are passing and code is linted
  - Self-review changes
  - Ensure commit message explains "why"

### Error Handling

- Fail fast with descriptive messages
- Include context for debugging
- Handle errors at appropriate level
- Never silently swallow exceptions

## Decision Framework

When multiple valid approaches exist, choose based on:

1. **Testability** - Can I easily test this?
2. **Readability** - Will someone understand this in 6 months?
3. **Consistency** - Does this match project patterns?
4. **Simplicity** - Is this the simplest solution that works?
5. **Reversibility** - How hard to change later?

## Project Integration

### Learning the Codebase

- Find 3 similar features/components
- Identify common patterns and conventions
- Use same libraries/utilities when possible
- Follow existing test patterns

### Tooling

- Use project's existing build system
- Use project's test framework
- Use project's formatter/linter settings
- Don't introduce new tools without strong justification
- Stop and ask for tests and linting to be run whenever it would be beneficial

## Quality Gates

### Definition of Done

- [ ] Tests written and passing
- [ ] Code follows project conventions
- [ ] No linter/formatter warnings
- [ ] Commit messages are clear
- [ ] Implementation matches plan
- [ ] Stop and ask before introducing any new TODOs

### Test Guidelines

- Test behavior, not implementation
- Use snapshot testing instead of complex assertions
- Clear test names describing scenario
- Use existing test utilities/helpers
- Tests should be deterministic

## Important Reminders

**NEVER**:
- Use `--no-verify` to bypass commit hooks
- Disable tests instead of fixing them
- Commit code that doesn't compile
- Make assumptions - verify with existing code

**ALWAYS**:
- Commit working code incrementally
- Update plan documentation as you go
- Learn from existing implementations
- Stop after 3 failed attempts and reassess
