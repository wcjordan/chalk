# Plan: Add Linting and Formatting to Playwright Tests

## Goal
Add linting and formatting tooling to the `tests/` directory to match the standards used in `test_gen/`.

## Constraints / Non-Goals
- **Match existing patterns**: Use the same tools and configurations as `test_gen/` (black, flake8, pylint)
- **No behavior changes**: Only add tooling and fix linting issues; don't modify test behavior
- **Keep changes small**: Focus on setup and fixing existing violations pragmatically
- **Don't expand scope**: Only add linting/formatting infrastructure; don't refactor tests

## Stages

### Stage 1: Setup configuration and dependencies
**Goal**: Create linting/formatting configuration files and requirements file

**Steps**:
1. Create `tests/dev-requirements.txt` with black, flake8, pylint (matching test_gen versions)
2. Copy `.flake8` and `.pylintrc` from test_gen to tests folder
3. Create `tests/Makefile` with `lint`, `format`, and `init` targets (similar to test_gen)
4. Run `make init` to create venv and install dependencies

**Exit Criteria**:
- Configuration files exist in tests/
- Makefile targets are defined
- Virtual environment can be created successfully

**Commit**: "Add linting and formatting configuration to tests folder"

### Stage 2: Run formatters and fix basic linting issues
**Goal**: Format code with black and fix any obvious linting violations

**Steps**:
1. Run `make format` to apply black formatting
2. Run `make lint` to identify linting issues
3. Fix any critical linting issues that prevent tests from running
4. Update configuration files if needed to handle Playwright-specific patterns

**Exit Criteria**:
- Black formatting applied to all test files
- Critical linting issues resolved
- `make lint` runs without errors (or only acceptable warnings)

**Commit**: "Apply black formatting and fix linting issues in tests"

### Stage 3: Integrate with root Makefile
**Goal**: Add tests linting/formatting to the root project workflow

**Steps**:
1. Update root `Makefile` to include tests in `format` target
2. Consider adding tests linting to root `test` target or document separately
3. Update CLAUDE.md if needed to document the new targets

**Exit Criteria**:
- Root `make format` includes tests folder
- Documentation is clear on how to lint/format tests

**Commit**: "Integrate tests linting/formatting into root Makefile"

### Stage 4: Verify full workflow
**Goal**: Ensure all tooling works end-to-end

**Steps**:
1. Run `make format` from root to verify tests are formatted
2. Run `make lint` from tests/ to verify linting passes
3. Verify that tests still run correctly (no behavioral changes)
4. Clean up any temporary files

**Exit Criteria**:
- All verification commands pass
- Tests run successfully
- No regressions introduced

**Commit**: "Verify linting/formatting workflow for tests"

### Stage 5: Cleanup
**Goal**: Remove planning documents and finalize

**Steps**:
1. Delete `docs/in_progress/` files
2. Final verification that everything works

**Exit Criteria**:
- Planning files removed
- All verification passes
