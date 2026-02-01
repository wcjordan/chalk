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

## Agent Working Guidelines

This repository uses a structured, verification-driven workflow for AI-assisted changes.
The agent should favor small, testable steps, externalized state, and explicit verification.

The goal is correctness, debuggability, and predictable progress — not speed or cleverness.

Prioritize
- Explicit state over memory
- Verification over confidence
- Resettable progress over long conversations

## Development Philosophy

### Core Principles

1. Prefer **small diffs** over large rewrites.
2. **tests and linting** must pass after each implementation step.
3. Learn from existing code.  Study and plan before implementing.
4. Externalize plans, decisions, and state into files.
5. Be pragmatic to keep changes small.  Adapt to the project's current state.
6. Code should be clear in intent rather than clever.  Be boring and obvious.
7. Assume conversational context can become stale or misleading.
8. When in doubt, re-ground on files and verification output.

### Simplicity Means

- Single responsibility per function/class
- Avoid premature abstractions
- No clever tricks - choose the boring solution
- If you need to explain it, it's too complex

## Process

### Overview

Unless explicitly instructed otherwise, follow this sequence:

1. **Plan**
2. **Implement (in small steps)**
3. **Verify**
4. **Review / Adjust**
5. **Checkpoint and continue**

These phases may repeat.

### 1. Planning Phase

#### `<PROJECT_ROOT>/docs/in_progress/PLAN.md`
Before making non-trivial changes, create or update a transient plan file
The plan should be concise and actionable.
Break complex work into 3-5 implementation stages.

Each stage should have a section in `PLAN.md` containing:
- Goal or problem statement
- Constraints and non-goals
- High-level approach
- Implementation steps (ensure these are small and simple)
- Verification strategy (include testable outcomes and specific test cases)
- Exit criteria (what "done" means)
- Status (Not Started|In Progress|Complete)

Plans are **working documents**, not final design docs.
They may be revised as new information is discovered.

If the plan changes materially, update `PLAN.md`.
Update the status of each stage as you progress
Remove file when all stages are done

#### `<PROJECT_ROOT>/docs/in_progress/VERIFY.md`

Before implementation, capture how correctness will be evaluated.
Include:
- Exact commands to run tests, linters, builds, or checks
- Any environment assumptions
- Expected signals of success or failure

Verification instructions must be concrete and executable.

### 2. Implementation Loop

1. **Understand** - Study existing patterns in codebase
2. **Test** - Write tests first (red)
3. **Implement** - Minimal code to pass (green)
4. **Verification** - Run and confirm tests and linting are passing
4. **Refactor** - Clean up with tests passing
5. **Commit** - With clear message linking to plan

During implementation:

- Work in **small, focused changes**
- After each meaningful change:
  - Run relevant verification
  - Observe results
  - Adjust the next step

Maintain a short running summary:

### `<PROJECT_ROOT>/docs/in_progress/STATUS.md`
Keep this brief (≤10 bullets):
- What has been completed
- What remains
- Current failures or blockers
- Any important decisions made

This file represents the **current state of work**.

### 3. Ask for Help When Stuck (Stop after 3 attempts per issue)

**CRITICAL**: Maximum 3 attempts per issue, then STOP.

Update `<PROJECT_ROOT>/docs/in_progress/NEED_HELP.md`

1. **Document what failed**:
   - What you tried
   - Specific error messages
   - Why you think it failed

2. **Research alternatives**:
   - Find 2-3 similar implementations
   - Note different approaches used
   - Add ideas to `NEED_HELP.md`

3. **Question fundamentals**:
   - Is this the right abstraction level?
   - Can this be split into smaller problems?
   - Is there a simpler approach entirely?
   - Add ideas to `NEED_HELP.md`

4. **Different angles**:
   - Different library/framework feature?
   - Different architectural pattern?
   - Remove abstraction instead of adding?
   - Add ideas to `NEED_HELP.md`

### 4. Verification Phase

Verification is not optional.

- Run the commands listed in `VERIFY.md`
- Capture relevant output (especially failures)
- Update `STATUS.md` with results

If verification fails:
- Treat failures as data
- Reassess the plan if needed
- Avoid rationalizing or ignoring failing signals

### 5. Context Management and Resets

Long conversational context can degrade results.

The agent should **intentionally clear and reload context** at natural boundaries, including:

- After finalizing or revising `PLAN.md`
- After completing a significant vertical slice
- After repeated failed attempts or thrashing
- Before review or final polish

#### When resetting context:
Assume the conversation history is discarded.
Resume work using only:
- Repository contents
- `PLAN.md`
- `VERIFY.md`
- `STATUS.md`
- `NEED_HELP.md`
- Current diffs and test output

Only information written to files should be treated as authoritative.

### 6. Review and Adjustment

Before declaring work complete:

- Re-read `PLAN.md` and confirm exit criteria are met
- Ensure verification passes
- Check for unintended scope creep
- Prefer clarity and maintainability over cleverness

If issues are found:
- Update the plan or status
- Re-enter the implementation loop

### 7. General Guardrails

- Do not silently change behavior without updating the plan.
- Do not expand scope without noting it explicitly.
- Avoid speculative refactors unless justified in `PLAN.md`.
- Prefer evidence (tests, code, output) over narrative explanation.

## Technical Standards

### Architecture Principles

- **Composable architecture** - Create composable components with minimal responsibilities
- **Explicit over implicit** - Clear data flow and dependencies
- **Test-driven when possible** - Never disable tests, fix them

### Code Quality

- **When committing**:
  - Tests should be passing and code should be linted
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
- Run tests and linting whenever it would be beneficial

## Quality Gates

### Definition of Done

- [ ] Tests written and passing
- [ ] Code follows project conventions
- [ ] No linter/formatter warnings
- [ ] Commit messages are clear
- [ ] Implementation matches plan
- [ ] When introducing any new TODOs update the `PLAN.md` to add a stage to address them

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
