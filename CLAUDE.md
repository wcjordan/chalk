# CLAUDE.md

## Repo Map (entrypoints)

Chalk is a full-stack todo app:
- `server/` Django REST API (settings in `server/chalk/settings/`)
- `ui/js/` React Native + Expo app (entry `ui/js/src/App.tsx`)
- `tests/` Playwright E2E tests (BrowserStack via `tests/conftest.py`)
- `test_gen/` System to generate tests from rrweb sessions (research project)

No tight coupling to the rest of the project is allowed in the `test_gen` folder.

If you need more detail on the project structure and architecture, see `docs/GETTING_AROUND.md`.

---

## Verification commands

Prefer existing Make targets.

Chalk app:
- Unit tests + lint: `make test` (from `<PROJECT_ROOT>` - runs tests for both server and UI in containers)
- Format ui, server, & tests code: `make format` (from `<PROJECT_ROOT>`)
- Create Django migrations: `(cd server && make create-migrations)` (from `<PROJECT_ROOT>` - runs Django in container)

test_gen:
- Tests: `make test` (from `<PROJECT_ROOT>/test_gen`)
- Lint: `make lint` (from `<PROJECT_ROOT>/test_gen`)
- Format: `make format` (from `<PROJECT_ROOT>/test_gen`)

### Autofixing test & linting issues

- Out of date UI snapshots: `make update-snapshots` (from `<PROJECT_ROOT>/ui`)
- Import order in UI: `make fix-imports` (from `<PROJECT_ROOT>/ui`)
- Out of date test_gen snapshots: `make update-snapshots` (from `<PROJECT_ROOT>/test_gen`)

---

## Agent workflow (Plan → Implement → Verify)

Use a verification-driven iterative looping workflow
Favor small testable steps, externalized state, and explicit verification.

### Principles (keep in mind always)
- Small diffs; avoid rewrites.
- Use repo code + test output as truth.
- Tests and linting must pass after each implementation step.
- Don't expand scope silently.
- Be pragmatic to keep changes small.  Adapt to the project's current state.
- Externalize state (plans, decisions, work in progress) into transient files (see below).
- Long chat context can degrade quality. Reset context when appropriate (see below).
- Use `TaskCreate` / `TaskUpdate` to track in-conversation steps and mark progress.

### Simplicity Means

- Single responsibility per function/class
- Avoid premature abstractions
- Code should be clear in intent rather than clever.  Be boring and obvious.
- No clever tricks - choose the boring solution
- If you need to explain it, it's too complex

### Transient working files (authoritative)
Store these in: `<PROJECT_ROOT>/docs/in_progress/`

Use native plan mode (`EnterPlanMode`) for planning.

1) `STATUS.md` — current state (≤10 bullets)
- What's done / next
- Current failures/blockers
- Key decisions

2) `NEED_HELP.md` — only when stuck (see rule below)

Commit changes to `docs/in_progress` after planning is complete.
Delete these files when all the work is complete.

---

## Planning

For any non-trivial changes, use `EnterPlanMode` to break down the problem into subtasks.
The plan should be concise and actionable (5 stages max).
Each stage should have explicit testable outcomes and specific test cases that prove correctness, plus an instruction to commit after completion.

Plans are working documents. Revise as new information is discovered.
Update `STATUS.md` as you progress and commit progress.

When finalizing planning, ask me clarifying questions about anything ambiguous.
Ask me questions one at a time.  Questions should clarify the plan and build on my previous answers.
Revise the plan based on my answers.  Clarify all ambiguity before starting on the implementation steps.

---

## Git Worktrees

**Use the `EnterWorktree` tool for all non-trivial work.** Each task should run in an isolated git worktree to keep changes contained and reviewable. Worktrees are created at `.claude/worktrees/<name>`.

When spawning subagents via the Agent tool, pass `isolation: "worktree"` to give each subagent its own isolated repo copy. The worktree is automatically cleaned up if the subagent makes no changes.

The `WorktreeCreate` hook (`.claude/hooks/setup-new-worktree.sh`) runs automatically on
`EnterWorktree` and handles:
- Copying `.env` (gitignored)
- Running `test_gen/make init`
- Running `yarn install --immutable` in `ui/js/`
- Copying `.claude/settings.local.json` (gitignored)

---

## Implementation loop (repeat per stage)

1. Follow existing patterns (find 2–3 similar examples).
2. Add new tests first when feasible; otherwise add coverage before finishing.
3. Implement minimal change.
4. Run `make test` to verify.
5. Update `STATUS.md` with command + result.
6. Cleanup once tests are passing.
7. Commit with clear message describing the change.

---

## Stuck rule (hard stop)

Maximum **3 attempts** per issue. If still blocked:
- STOP and update `NEED_HELP.md` with:
  - What you tried
  - Exact errors/output
  - 2–3 alternative approaches, libraries, abstractions, patterns, etc
  - A simpler reframing / smaller subproblem

---

## Context resets

Reset / restart from files at boundaries:
- After creating or materially revising the plan
- After a vertical slice / stage completion
- After thrash (repeated failures)
- Before final review/polish

After reset, treat only these as authoritative:
- Repo contents
- Native plan (plan mode), `STATUS.md`, `NEED_HELP.md`
- Current diffs + latest verification output

---

## Quality gates

Definition of Done:
- Tests + lint pass (`make test`)
- Implementation matches plan exit criteria
- No new TODOs without adding a plan stage to address them

NEVER:
- Bypass hooks with `--no-verify`
- Disable tests instead of fixing them
- Commit broken code

ALWAYS:
- Commit incrementally
- Update the plan / `STATUS.md` as you go
- Prefer boring, readable code

If verification fails:
- Treat failures as data
- Reassess the plan if needed
- Avoid rationalizing or ignoring failing signals

If issues are found:
- Update the plan or status
- Re-enter the implementation loop

---

## General Guidelines

- Do not silently change behavior without updating the plan.
- Do not expand scope without noting it explicitly.
- Avoid speculative refactors unless justified in the plan.
- Prefer evidence (tests, code, output) over narrative explanation.

### Architecture Principles

- **Composable architecture** - Create composable components with minimal responsibilities
- **Explicit over implicit** - Clear data flow and dependencies
- **Test-driven when possible** - Never disable tests, fix them

### Code Quality

- When committing:
  - Tests should be passing and code should be linted
  - Self-review changes
  - Ensure commit message explains "why"

### Error Handling

- Fail fast with descriptive messages
- Include context for debugging
- Handle errors at appropriate level
- Never silently swallow exceptions

### Decision Framework

When multiple valid approaches exist, choose based on:

1. **Testability** - Can I easily test this?
2. **Readability** - Will someone understand this in 6 months?
3. **Consistency** - Does this match project patterns?
4. **Simplicity** - Is this the simplest solution that works?
5. **Reversibility** - How hard to change later?

### Test Guidelines

- Test behavior, not implementation
- Prefer snapshot testing to complex assertions
- Use existing test utilities/helpers
- Tests should be deterministic
