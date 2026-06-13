# Implementation Plan: minordomo-1px
## Show a butterbar when labelling a Todo

**GH Issue:** https://github.com/wcjordan/chalk/issues/316

**Summary:** Add a pale pastel yellow "butterbar" notification that appears each time the user
toggles a label on a Todo. The notification reuses the existing `Snackbar`-based `ErrorBar`
component, extended to support a `'label'` type with distinct yellow styling. The implementation
refactors the notification queue from `string[]` to `Notification[]` (objects with `text` and
`type` fields) so different notification types can carry different visual themes.

**Design decisions:**
- One butterbar fires per label-chip click (consistent with how "Saving Todo" fires per `updateTodo`
  call). Multiple quick clicks queue multiple notifications that auto-dismiss in sequence.
- Dispatch lives inside the `updateTodoLabels` thunk (not in `todosApiSlice.extraReducers`) because
  notifications should only appear for actions triggered by the current user, not for label changes
  that arrive via server polling in `listTodos.fulfilled`.

---

## Stage 1: Extend notification system with typed notifications and update ErrorBar

### Description

Refactor the notification queue from `string[]` to `Notification[]` where each item carries a
`text` string and a `type` (`'default' | 'label'`). Update the `ErrorBar` component to apply a
pale pastel yellow theme when `type === 'label'`, keeping the existing dark/pink theme for
`'default'`. Add a `LabelErrorBar` Storybook story. All existing notification callsites are
updated to pass `{text, type: 'default'}`.

**Files to change:**
- `ui/js/src/redux/types.ts` — add `NotificationType` union and `Notification` interface; update
  `NotificationsState.notificationQueue` to `Notification[]`
- `ui/js/src/redux/notificationsSlice.ts` — `addNotification` action accepts `Notification`
  (callers pass an object, not a bare string)
- `ui/js/src/redux/reducers.ts` — update all four existing `addNotification` callsites to use
  `{text: '...', type: 'default'}`
- `ui/js/src/App.tsx` — extract `notificationType` from `notificationQueue[0]`; pass to ErrorBar
- `ui/js/src/components/ErrorBar.tsx` — accept optional `notificationType` prop; apply yellow theme
  (`surface: '#FFFDE7'`, `onSurface: '#5D4037'`) when `notificationType === 'label'`
- `ui/js/src/components/ErrorBar.stories.tsx` — add `LabelErrorBar` story
- `ui/js/src/redux/reducers.test.ts` — update assertions that check `notificationQueue[0]` to
  match the new `{text, type}` shape

### Acceptance Criteria
- `types.ts` exports `NotificationType = 'default' | 'label'` and `Notification = {text: string, type: NotificationType}`
- `NotificationsState.notificationQueue` is typed as `Notification[]`
- All existing `addNotification` dispatches pass `{text: '...', type: 'default'}`
- `ErrorBar` renders with pale yellow theme (`#FFFDE7` background, `#5D4037` text) when
  `notificationType === 'label'`; dark/pink theme otherwise
- `ErrorBar.stories.tsx` has a `LabelErrorBar` story that renders the yellow variant
- `make test` passes (all existing tests updated for the new notification shape)

---

## Stage 2: Dispatch label notification from updateTodoLabels

### Description

Add a `{text: 'Labeling Todo: <description>', type: 'label'}` notification dispatch inside the
`updateTodoLabels` thunk, just before the API call. The todo description is looked up from
`getState().todosApi.entries`. Add a test that verifies the butterbar notification is queued with
the correct type and text when `updateTodoLabels` is dispatched.

**Files to change:**
- `ui/js/src/redux/reducers.ts` — in `updateTodoLabels`, look up the todo by `labelTodoId` and
  dispatch `addNotification({text: 'Labeling Todo: <description>', type: 'label'})` before the
  API patch
- `ui/js/src/redux/reducers.test.ts` — add test: after `store.dispatch(updateTodoLabels(labels))`,
  verify `notificationQueue[0]` equals `{text: 'Labeling Todo: test todo', type: 'label'}`

### Acceptance Criteria
- After `updateTodoLabels` is dispatched, `notifications.notificationQueue` contains one item:
  `{text: 'Labeling Todo: <todo description>', type: 'label'}`
- The test in `reducers.test.ts` for `updateTodoLabels` verifies the notification is queued
- `make test` passes
