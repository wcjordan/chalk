# Research: Butterbar for Todo Labeling (minordomo-1px)

## Issue
GH #316: Show a pale pastel yellow notification bar when a Todo is labeled by the current user.

## Current Notification System

### State (`types.ts`)
- `NotificationsState.notificationQueue: string[]` — a FIFO queue of notification strings

### Slice (`notificationsSlice.ts`)
- `addNotification(text: string)` — pushes a string to the queue
- `dismissNotification()` — shifts the first item

### UI (`ErrorBar.tsx`)
- Renders `react-native-paper` `<Snackbar>` with hardcoded dark/pink theme
- `App.tsx` feeds `notificationQueue[0]` as `text` prop; uses `key={notificationText}` to remount on change

### Existing callers of `addNotification` in `reducers.ts`
- `updateTodo`: `'Saving Todo: <description>'`
- `moveTodo`: `'Reordering Todo: <description>'`
- `completeAuthentication`: login failure messages
- `recordSessionEvents`: `'Failed to record session data'` (DEV only)

### Missing: `updateTodoLabels` dispatches no notification

## Labeling Flow
1. User completes an unlabeled todo → `updateTodo` dispatches `setLabelTodoId(todo.id)` to show modal
2. User picks labels in `LabelPicker` modal → calls `updateTodoLabels(labels)` 
3. `updateTodoLabels` reads `labelTodoId` from workspace state, dispatches `updateTodoApi({id, labels})`
4. The todo description is accessible via `getState().todosApi.entries.find(t => t.id === todoId)?.description`

## Implementation Plan

### Change needed

1. Extend the notification type system to support typed notifications:
   - Add `NotificationType = 'default' | 'label'` to `types.ts`
   - Change `notificationQueue: string[]` → `notificationQueue: Notification[]` where `Notification = {text: string, type: NotificationType}`
   - Update `notificationsSlice.ts` — `addNotification` accepts `Notification` object
   - Update `App.tsx` to pass type to `ErrorBar`
   - Update `ErrorBar.tsx` to apply pale yellow theme when `type === 'label'`
   - Update all existing `addNotification` calls in `reducers.ts` to use `{text, type: 'default'}`
   - Update tests to check `notificationQueue[0]` as objects

2. Dispatch label notification from `updateTodoLabels`:
   - Look up todo description from state
   - Dispatch `addNotification({text: 'Labeling Todo: <description>', type: 'label'})`
   - Add test to verify

## Color Choices
- Pale pastel yellow background for label notifications: `#FFFDE7` (Material very light yellow)
- Text on pale yellow: `#5D4037` (brown, good contrast on yellow)
- Existing error/default notifications keep their current dark/pink (#444 bg, #FAA0A0 text)

## Files to Change
- `ui/js/src/redux/types.ts` — add `Notification`, `NotificationType`
- `ui/js/src/redux/notificationsSlice.ts` — update action signature
- `ui/js/src/redux/reducers.ts` — update callers + add label notification
- `ui/js/src/components/ErrorBar.tsx` — conditional theming
- `ui/js/src/App.tsx` — pass type to ErrorBar
- `ui/js/src/redux/reducers.test.ts` — update tests for typed notifications
