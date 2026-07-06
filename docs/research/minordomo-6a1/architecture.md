# Snooze Feature Research Notes

## Feature Requirements (GH #324)
- Icon on todo (similar to label or archive)
- Preset times: til tomorrow, Saturday, next month, etc, or calendar widget
- View sorted list of snoozed todos as a Work Context

## Codebase Architecture

### Backend (server/)
- `TodoModel` in `server/chalk/todos/models.py`: fields include `archived`, `completed`, `order_rank`, with timestamps via `pre_save` signal `update_derived_fields`
- `TodoSerializer` in `serializers.py`: exposes fields list including `archived`, `completed`, `labels`, etc.
- `TodoViewSet` in `views.py`: standard DRF `ModelViewSet`, queryset is `all()` — returns ALL todos including archived; frontend handles filtering
- Migrations in `migrations/` — latest is `0012_...`

### Frontend (ui/js/src/)
- **Types** (`redux/types.ts`): `Todo`, `TodoPatch`, `WorkspaceState`, `WorkContext`
- **WorkContexts** (`redux/workspaceSlice.ts`): hardcoded label-based workContexts dict (inbox, urgent, quickFixes, upNext, work, shopping, chalkPlanning). `WorkspaceState` includes `filterLabels` (label-based), `showCompletedTodos`
- **Selectors** (`selectors.ts`): `selectFilteredTodos` — filters todos by label criteria; `selectActiveWorkContext` — matches filterLabels to workContexts dict
- **`processTodos`** (`redux/todosApiSlice.ts`): filters archived todos before storing in Redux state (applied at load time); completed todos sorted to bottom
- **TodoItem** (`components/TodoItem.tsx`): renders label icon (`tag-plus`), delete icon (`delete-outline`); dispatches `setLabelTodoId` and `updateTodo({archived: true})`
- **LabelPicker** (`components/LabelPicker.tsx`): modal pattern used for label selection

## Key Design Decisions for Snooze

### Data Storage
Add `snoozed_until: DateTimeField(null=True)` to `TodoModel`. No auto-managed timestamp needed — value is set explicitly to a future datetime.

### Frontend Filtering
- Snoozed todos (`snoozed_until > now`) are filtered OUT of normal lists in `selectFilteredTodos` (NOT in `processTodos`, since snoozed todos must remain in state for the Snoozed work context)
- When in "Snoozed" mode, show ONLY currently-snoozed todos, sorted ascending by `snoozed_until`
- When snooze expires (time passes), todos reappear in normal list on next refresh

### Snoozed Work Context
The existing work context system is label-based. "Snoozed" requires a date-based filter. Approach:
- Add `snoozedOnly: boolean` to `WorkspaceState` (analogous to `showCompletedTodos`)
- Add `setSnoozedOnly` action
- Add special "Snoozed" chip to `WorkContextFilter` that sets `snoozedOnly` (and clears label filters)
- `selectActiveWorkContext` updated to return `'snoozed'` when `snoozedOnly` is true
- `selectFilteredTodos` updated to handle `snoozedOnly` mode

### Snooze Picker Component
New `SnoozeMenu` modal (similar to `LabelPicker`) with preset options:
- "Tomorrow" — next day at 7am
- "This Saturday" — upcoming Saturday at 7am
- "Next Week" — next Monday at 7am
- "Next Month" — 1st of next month at 7am
- "Remove snooze" — clear `snoozed_until` (for already-snoozed todos)

`WorkspaceState` gets `snoozeTodoId: number | null` to control modal visibility.

### TodoItem Changes
Add alarm icon (`alarm-plus`) button alongside label and delete. Dispatches `setSnoozeTodoId`.

## Test Patterns
- Unit tests: Django `TestCase` in `server/chalk/todos/tests.py`
- UI snapshots: Storybook stories in `components/__snapshots__/`
- E2E: Playwright tests in `tests/` with helpers in `tests/helpers/`
- E2E work context test: `tests/work_contexts_test.py` — good reference for snooze E2E

## Files to Touch (Summary)
- `server/chalk/todos/models.py` — add `snoozed_until`
- `server/chalk/todos/serializers.py` — expose field
- `server/chalk/todos/tests.py` — update stub matcher, add snooze tests
- New migration file
- `ui/js/src/redux/types.ts` — add `snoozed_until` to Todo, TodoPatch; add `snoozedOnly` to WorkspaceState
- `ui/js/src/redux/workspaceSlice.ts` — add state + actions
- `ui/js/src/selectors.ts` — update filtering + active context detection
- `ui/js/src/components/WorkContextFilter.tsx` — add Snoozed chip
- `ui/js/src/components/SnoozeMenu.tsx` — new component
- `ui/js/src/components/TodoItem.tsx` — add snooze button
- `ui/js/src/components/TodoList.tsx` — wire SnoozeMenu
- New stories + snapshots
- `tests/snooze_test.py` — new E2E test
