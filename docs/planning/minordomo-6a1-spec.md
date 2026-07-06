# Spec: Add the ability to snooze a todo for a period of time

## Overview

Add a snooze feature to the Chalk todo app. Users can snooze a todo until a preset time (Tomorrow, This Saturday, Next Week, Next Month). Snoozed todos are hidden from the main list and visible in a dedicated "Snoozed" work context showing them sorted by wake-up time.

---

## Stage 1: Backend — Add snoozed_until field to TodoModel

### Description

Add a `snoozed_until` DateTimeField (nullable) to `TodoModel`. Update the serializer to expose it. Create the Django migration. Update existing unit tests and add new ones covering the field.

Specifically:
- Add `snoozed_until = models.DateTimeField(null=True)` to `TodoModel` in `server/chalk/todos/models.py`
- The `update_derived_fields` signal does NOT need to auto-manage this field (it is set explicitly by the frontend to a future datetime; no derived timestamp logic is needed)
- Update `TodoSerializer.Meta.fields` in `serializers.py` to include `snoozed_until`
- Run `(cd server && make create-migrations)` to generate the migration
- Update `_stub_todo_matcher` in `tests.py` to include `snoozed_until`
- Add unit tests verifying the field is returned by the serializer and survives PATCH round-trip
- Run `make test` to verify all tests pass
- Commit

### Acceptance Criteria
- `snoozed_until` appears in the API response for todo list and detail endpoints
- PATCH to `snoozed_until` with a future datetime persists correctly
- PATCH to `snoozed_until: null` clears the snooze
- All existing server unit tests still pass

---

## Stage 2: Frontend — Types, state, and filtering logic

### Description

Wire the snooze data model through the Redux layer and update the filtering selectors to hide snoozed todos from normal views.

Specifically:
- `redux/types.ts`:
  - Add `snoozed_until?: string | null` to `Todo` and `TodoPatch`
  - Add `snoozedOnly: boolean` and `snoozeTodoId: number | null` to `WorkspaceState`
- `redux/workspaceSlice.ts`:
  - Add `snoozedOnly: false` and `snoozeTodoId: null` to `initialState`
  - Add `setSnoozedOnly` reducer (sets `snoozedOnly`, clears `filterLabels` to empty when enabling)
  - Add `setSnoozeTodoId` reducer
- `selectors.ts`:
  - Update `selectFilteredTodos`: when `snoozedOnly` is false, additionally filter out todos where `snoozed_until` is set and is in the future (i.e. `new Date(todo.snoozed_until) > new Date()`)
  - When `snoozedOnly` is true, return only currently-snoozed todos sorted ascending by `snoozed_until` (ignoring label filters and `showCompletedTodos`)
  - Update `selectActiveWorkContext`: return `'snoozed'` when `snoozedOnly` is true (takes priority over label-based matching)
- Export `setSnoozedOnly` and `setSnoozeTodoId` from `redux/reducers.ts`
- Update `selectors.test.ts` and `redux/workspaceSlice.test.ts` with new cases
- Run `make test` to verify all tests pass
- Commit

### Acceptance Criteria
- A todo with `snoozed_until` set to a future time is absent from normal filtered list
- A todo with `snoozed_until` set to a past time (expired) appears normally in the list
- When `snoozedOnly` is true, only currently-snoozed todos are returned, sorted by `snoozed_until` ascending
- `selectActiveWorkContext` returns `'snoozed'` when `snoozedOnly` is true

---

## Stage 3: Frontend — Snooze UI (SnoozeMenu, TodoItem icon, WorkContextFilter chip)

### Description

Build the snooze picker modal and wire up all UI touchpoints.

Specifically:
- `components/SnoozeMenu.tsx` (new file): modal component (modeled on `LabelPicker`) displaying preset snooze time options as tappable chips/buttons:
  - "Tomorrow" — next day at 07:00 local time
  - "This Saturday" — upcoming Saturday at 07:00 local time (if today is Saturday, use next Saturday)
  - "Next Week" — next Monday at 07:00 local time
  - "Next Month" — 1st of next month at 07:00 local time
  - "Remove snooze" — set `snoozed_until: null` (only shown when the selected todo is currently snoozed)
  - Tapping an option dispatches `updateTodo({ id: snoozeTodoId, snoozed_until: <ISO string> })` then closes the menu (`setSnoozeTodoId(null)`)
- `components/TodoItem.tsx`: add an `alarm-plus` IconButton (between the label and delete icons) that calls `event.stopPropagation()` then dispatches `setSnoozeTodoId(todo.id)`
- `components/WorkContextFilter.tsx`: add a "Snoozed" `LabelChip` at the end of the chip list that dispatches `setSnoozedOnly(true)` on press; pass `status={activeWorkContext === 'snoozed' ? FILTER_STATUS.Active : undefined}`; when any label-based chip is tapped, also dispatch `setSnoozedOnly(false)` (handle in `setWorkContext` thunk or via existing `setWorkContext` reducer which already sets `filterLabels` — add `setSnoozedOnly(false)` call in `setWorkContext` action or in the `workspaceSlice` reducer for `setWorkContext`)
- `redux/workspaceSlice.ts` / `redux/reducers.ts`: ensure that dispatching `setWorkContext` resets `snoozedOnly` to false
- `components/TodoList.tsx`: import and render `SnoozeMenu` (alongside `LabelPicker`), passing `visible={snoozeTodoId !== null}` and the current `snoozeTodoId`
- Add `components/SnoozeMenu.stories.tsx` with representative stories
- Run `make update-snapshots` then `make test` to verify all tests pass
- Commit

### Acceptance Criteria
- Alarm icon appears on each todo in view (non-editing state)
- Tapping the alarm icon opens the SnoozeMenu modal
- Selecting a preset time PATCHes the todo with `snoozed_until` set appropriately and closes the modal
- "Remove snooze" option visible when todo is currently snoozed; clears the field
- "Snoozed" chip visible in the work context filter
- Tapping "Snoozed" chip shows only currently-snoozed todos
- Tapping any other work context chip exits snoozed-only mode
- Storybook snapshots updated

---

## Stage 4: E2E Tests

### Description

Add a Playwright E2E test covering the end-to-end snooze flow.

Specifically:
- Create `tests/snooze_test.py` with test `test_snooze` parametrized with `"Snooze: Snooze and view snoozed todo"`
- Test flow:
  1. Add a todo
  2. Wait for it to appear
  3. Snooze it via the alarm icon (select "Next Month" preset)
  4. Verify the todo disappears from the current view (Inbox)
  5. Click the "Snoozed" work context chip
  6. Verify the todo appears in the Snoozed work context
- Add a helper `snooze_todo(page, todo_item, preset)` to `tests/helpers/todo_helpers.py` that clicks the alarm icon on a given todo and selects the given preset from the snooze menu
- Run `make test` (unit + lint pass); E2E tests run on BrowserStack and are not run locally in CI
- Commit

### Acceptance Criteria
- `tests/snooze_test.py` exists and contains a well-structured Playwright test following conventions in `tests/work_contexts_test.py`
- Helper `snooze_todo` added to `tests/helpers/todo_helpers.py`
- `make test` passes (unit tests and lint; E2E tests are skipped locally)
