# Plan: Add Custom Labels

## Overview
Add the ability to create custom labels via Django admin UI. Custom labels will automatically appear in the React app's label picker and can be used to label todos. Existing hardcoded labels in workContexts remain unchanged.

## Current State Analysis
- **Backend**: `LabelModel` exists with `id`, `name`, and ManyToMany relationship to `TodoModel`
- **API**: `LabelViewSet` already exposes labels at `/api/todos/labels/`
- **Frontend**: `labelsApiSlice` fetches labels from API; `LabelPicker` displays all labels
- **Hardcoded labels**: Used in `workContexts` for predefined filters (e.g., 'urgent', 'backlog', 'Chalk')
- **No admin registration**: `LabelModel` is not currently registered in Django admin

## Constraints & Non-Goals
- **In scope**: Only CREATE labels via Django admin
- **Out of scope**: Delete, rename, or edit labels (future work)
- **Out of scope**: Creating labels in React app (future work)
- **Out of scope**: Migrating existing hardcoded labels to database (keep them hardcoded for now)
- **Architectural decision needed**: Validation rules (duplicates, naming constraints)

## Clarified Requirements
1. **Duplicate names**: ✓ Enforce unique names (case-insensitive)
2. **Label fields**: ✓ Keep simple - just name and id
3. **Name constraints**: ✓ Strict validation - max 50 chars, alphanumeric + spaces + common punctuation
4. **Admin display**: ✓ Show count of associated todos (not inline list)
5. **Case sensitivity**: ✓ Case-insensitive uniqueness
6. **Empty/whitespace names**: ✓ Prevent via validation

## Stages

### Stage 1: Update Model and Register in Django Admin
**Goal**: Add validation to LabelModel and make it editable in Django admin UI

**Steps**:
1. Update `LabelModel` in `server/chalk/todos/models.py`:
   - Change `name` from TextField to CharField with max_length=50
   - Add unique constraint (case-insensitive)
   - Add validation for allowed characters
2. Create migration for model changes
3. Update `server/chalk/todos/admin.py` to register `LabelModel`:
   - Configure admin display to show label name, ID, and todo count
   - Add custom admin methods for todo count display
4. Test validation rules work correctly

**Exit Criteria**:
- Navigate to Django admin and see Labels section
- Can create new labels via admin interface
- Validation rules are enforced

**Commit**: After admin registration is complete and tested

### Stage 2: Verify Custom Labels in React App
**Goal**: Confirm custom labels created in admin appear in React app

**Steps**:
1. Start Django server and React app
2. Create a test custom label via Django admin
3. Verify label appears in label picker when labeling a todo
4. Verify todo can be labeled with custom label
5. Verify custom label appears on todo in the UI

**Exit Criteria**:
- Custom labels created in admin show up in React label picker
- Todos can be labeled with custom labels
- Custom labels display correctly on todo items

**Commit**: No code changes expected (verification only)

### Stage 3: Add Tests
**Goal**: Add backend tests for label creation

**Steps**:
1. Add test for creating label via admin
2. Add test for validation rules (based on Stage 1 decisions)
3. Verify existing label API tests still pass

**Exit Criteria**:
- New tests pass
- All existing tests pass
- `make test` runs successfully

**Commit**: After tests are added and passing

### Stage 4: Documentation
**Goal**: Document the custom labels feature

**Steps**:
1. Add comment in admin.py explaining label creation workflow
2. Update any relevant documentation about labels

**Exit Criteria**:
- Code is documented
- Changes are ready for review

**Commit**: Final commit with documentation

## Definition of Done
- [x] Plan created and clarified
- [ ] All stages complete
- [ ] Tests passing (`make test`)
- [ ] No linting errors (`make format`)
- [ ] Manual verification successful
- [ ] Code documented
