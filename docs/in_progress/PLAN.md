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

## Open Questions (to clarify before implementation)
1. **Duplicate names**: Should the system prevent creating labels with duplicate names?
2. **Label fields**: Should labels have additional fields (color, icon, display order, description)?
3. **Name constraints**: Should there be validation on label names (max length, allowed characters, required field)?
4. **Admin display**: Should the admin interface show associated todos for each label?
5. **Case sensitivity**: Are labels case-sensitive? (e.g., "Work" vs "work")
6. **Empty/whitespace names**: Should empty or whitespace-only names be prevented?

## Stages

### Stage 1: Register LabelModel in Django Admin (BLOCKED on clarifications)
**Goal**: Make LabelModel editable in Django admin UI

**Steps**:
1. Update `server/chalk/todos/admin.py` to register `LabelModel`
2. Configure admin display to show label name and ID
3. Add inline display for associated todos (if desired - see question #4)
4. Add field validation based on answers to questions above

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
