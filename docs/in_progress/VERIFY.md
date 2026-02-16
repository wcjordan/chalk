# Verification Plan: Custom Labels

## Automated Verification

### Run all tests
```bash
# From project root
make test
```

### Format code
```bash
# From project root
make format
```

### Expected Results
- All tests pass
- No linting errors
- Code is properly formatted

## Manual Verification

### Prerequisites
- Django server running (port 8000)
- React app running (Expo)
- Admin user account

### Test Cases

#### TC1: Access Labels in Django Admin
1. Navigate to http://localhost:8000/admin/
2. Log in as admin user
3. Verify "Labels" section appears under "TODOS"
4. Click on "Labels"

**Expected**: Labels admin page loads successfully

#### TC2: Create Custom Label
1. In Labels admin, click "Add label"
2. Enter a custom label name (e.g., "TestLabel")
3. Click "Save"

**Expected**:
- Label is created successfully
- Redirected to labels list
- New label appears in the list

#### TC3: Validation Rules (if applicable)
Test based on validation rules implemented:
- Attempt to create duplicate label (if duplicates prevented)
- Attempt to create label with invalid name (if constraints exist)
- Attempt to create empty/whitespace label (if prevented)

**Expected**: Appropriate validation errors displayed

#### TC4: Custom Label in React Label Picker
1. Open React app
2. Create or select a todo
3. Open label picker for that todo
4. Verify custom label from TC2 appears in picker

**Expected**: Custom label "TestLabel" appears in label picker

#### TC5: Apply Custom Label to Todo
1. In label picker, select custom label
2. Close label picker
3. Verify label appears on todo

**Expected**: Todo displays custom label chip

#### TC6: Filter by Custom Label
1. Click on custom label chip to filter
2. Verify filtering works

**Expected**: Only todos with custom label are shown

#### TC7: API Response
```bash
curl http://localhost:8000/api/todos/labels/ -H "Cookie: sessionid=<your-session>"
```

**Expected**: JSON response includes custom label with id and name

## Environment Assumptions
- Django running in development mode
- SQLite database (or configured database)
- Admin user exists with credentials
- React app connected to Django backend
- No authentication issues

## Success Criteria
- All automated tests pass
- All manual test cases pass
- No console errors in browser or server
- Labels persist across server restarts
