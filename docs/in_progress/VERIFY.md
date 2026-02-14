# Verification Steps

## After Each Stage

Run from project root:
```bash
make test
```

This runs:
- Django server tests
- React Native UI tests
- Linting

## Stage-Specific Verification

### Stage 1: Server-Side Version Field
```bash
cd server
python manage.py makemigrations todos --name add_version_field
python manage.py migrate
cd ..
make test
```

Expected:
- Migration creates version field (IntegerField, default=1)
- All existing tests pass
- API responses include version field

### Stage 2: Client Type Updates
```bash
make test
```

Expected:
- TypeScript compilation succeeds
- No type errors

### Stage 3: Version-Aware Update Logic
```bash
make test
```

Expected:
- Tests pass
- Manual test: Edit todo, check console for "Skipping stale update" logs

### Stage 4: Server Tests
```bash
make test
```

Expected:
- New version tests pass
- All existing tests still pass

### Stage 5: Client Tests
```bash
make test
```

Expected:
- New client tests pass
- Full test suite passes

## Success Criteria

- All tests pass
- No linting errors
- Version field present in API responses
- Stale updates are skipped (visible in console logs)
- Optimistic updates remain visible during polls
