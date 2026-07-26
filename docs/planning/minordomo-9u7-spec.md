# Implementation Spec: TodoList stories all show the Snooze menu overlay

**Epic:** minordomo-9u7
**GH Issue:** https://github.com/wcjordan/chalk/issues/344

## Background

After the snooze feature was added (PR #340), `TodoList.stories.tsx` was not updated.
The `defaultState.workspace` object omits `snoozeTodoId`, so Redux receives `undefined`
for that key. Because `undefined !== null` is `true`, `SnoozeMenu` renders as `visible`
in every existing TodoList story.

---

## Stage 1: Fix snooze menu visibility in existing stories and add SnoozeMenuOverlay story

### Description

Update `ui/js/src/components/TodoList.stories.tsx` to:
1. Add `snoozeTodoId: null` to the `workspace` key in `defaultState` so existing stories
   no longer render the SnoozeMenu as visible.
2. Add a new exported `SnoozeMenuOverlay` story that sets `snoozeTodoId: 3` in the
   workspace state override, matching the pattern of `LabelPickerOverlay`.

After editing the story file, regenerate snapshots via `make update-snapshots` from
`<PROJECT_ROOT>/ui` (or run `make test` if snapshots auto-update on failure), then
commit the updated stories and snapshots.

### Acceptance Criteria
- `defaultState.workspace` in `TodoList.stories.tsx` includes `snoozeTodoId: null`
- The `DefaultTodoList`, `LabelPickerOverlay`, and `LoadingIndicator` stories do not
  render the SnoozeMenu as visible (no `data-testid="snooze-menu"` in their snapshots,
  or it is present only with `visible={false}`)
- A new `SnoozeMenuOverlay` story exists and renders the SnoozeMenu with `snoozeTodoId: 3`
- `make test` passes with all snapshots up to date
