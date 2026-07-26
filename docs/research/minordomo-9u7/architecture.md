# Research: TodoList stories show Snooze menu overlay

## Root Cause

`TodoList.stories.tsx` has a `defaultState` object where the `workspace` key does not include `snoozeTodoId`:

```js
const defaultState = {
  ...
  workspace: {
    editTodoId: 3,
    filterLabels: {...},
    labelTodoId: null,
    // snoozeTodoId is MISSING
  },
};
```

`setupStore(preloadedState)` calls Redux Toolkit's `configureStore({ preloadedState })`.
Redux does NOT merge the preloadedState with the slice's default state — it uses the
preloadedState verbatim. So `state.workspace.snoozeTodoId` is `undefined`, not `null`.

In `TodoList.tsx`, the SnoozeMenu is rendered with:
```tsx
<SnoozeMenu snoozeTodoId={snoozeTodoId} visible={snoozeTodoId !== null} />
```

`undefined !== null` evaluates to `true`, so the SnoozeMenu renders as visible in every story.

## Fix

Two changes needed in `ui/js/src/components/TodoList.stories.tsx`:

1. Add `snoozeTodoId: null` to the `workspace` object in `defaultState` so that
   `snoozeTodoId !== null` correctly evaluates to `false` for all existing stories.

2. Add a new `SnoozeMenuOverlay` story (analogous to `LabelPickerOverlay`) that sets
   `snoozeTodoId: 3` in the workspace state override.

## Files to change

- `ui/js/src/components/TodoList.stories.tsx` — the only file that needs editing
- Snapshots under `ui/js/src/components/__snapshots__/TodoList.stories.tsx.snap` will
  need regeneration via `make update-snapshots`

## Related components

- `SnoozeMenu.tsx` — the overlay component; accepts `snoozeTodoId` and `visible` props
- `workspaceSlice.ts` — default `snoozeTodoId: null` at line 86
- `LabelPickerOverlay` story — the model for the new story
