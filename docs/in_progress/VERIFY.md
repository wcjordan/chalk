# Verification: Linting and Formatting for Playwright Tests

## Commands

### Format tests
```bash
cd tests
make format
```

### Lint tests
```bash
cd tests
make lint
```

### Format from root
```bash
make format
```

### Run integration tests (to verify no regressions)
```bash
make integration-test
```
Note: Requires dev environment running (`make start`)

## Environment Assumptions
- Python 3 is available
- Virtual environment can be created
- Dev dependencies can be installed

## Success Criteria

### Stage 1: Configuration Setup
- ✅ `tests/dev-requirements.txt` exists
- ✅ `tests/.flake8` exists
- ✅ `tests/.pylintrc` exists
- ✅ `tests/Makefile` exists with `init`, `lint`, `format` targets
- ✅ `make init` creates `.venv` successfully

### Stage 2: Formatting and Linting
- ✅ `make format` runs without errors
- ✅ All Python files are formatted by black
- ✅ `make lint` runs and reports issues (if any)
- ✅ Critical linting issues are resolved

### Stage 3: Integration
- ✅ Root `make format` includes tests folder
- ✅ Documentation updated if necessary

### Stage 4: Full Workflow
- ✅ `make format` from root works
- ✅ `make lint` from tests/ passes (or acceptable warnings only)
- ✅ Integration tests still pass (no behavioral changes)

## Failure Indicators
- ❌ Configuration files missing or malformed
- ❌ Virtual environment creation fails
- ❌ Black/flake8/pylint not installed properly
- ❌ Tests fail after formatting (behavioral regression)
- ❌ Makefile targets error out
