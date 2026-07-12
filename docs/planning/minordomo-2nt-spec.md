# Implementation Plan: Handle Being Offline (minordomo-2nt)

## Overview

When offline, the user should see an indication of their connectivity status. Todo changes that fail to save should be retained in memory and automatically applied once the connection is restored.

The app currently uses Redux Toolkit with `createAsyncThunk` and polls every 10 seconds. All failed API calls are silently swallowed with `console.warn` only. There is no network detection, no offline UI, and no retry logic.

---

## Stage 1: Offline Detection & Offline Banner

### Description

Add network connectivity detection using `@react-native-community/netinfo`. Create a Redux slice to track online/offline state. Show a persistent offline banner in the UI when the network is unavailable. Pause the 10-second polling interval while offline and resume (with an immediate refresh) when connectivity is restored.

### Acceptance Criteria
- `@react-native-community/netinfo` is added to `ui/js/package.json` dependencies
- A `networkSlice` exists in `ui/js/src/redux/networkSlice.ts` with `isOnline: boolean` state and a `setOnlineStatus` action
- A `NetworkStatusListener` component (or hook) subscribes to `NetInfo.addEventListener` and dispatches `setOnlineStatus` on change
- An offline banner (e.g. "You are offline" strip above the todo list) renders when `isOnline` is false
- The 10-second polling in `useDataLoader` is paused when offline; on reconnect it fires an immediate `listTodos()` before resuming the interval
- Existing unit tests pass; new unit tests cover: (a) `networkSlice` actions, (b) banner appears/disappears when `isOnline` changes, (c) polling pauses/resumes correctly

---

## Stage 2: User Notifications for Failed Mutations

### Description

Convert the silent `console.warn` failures in all todo mutation thunks into visible user notifications. Extend the notification system to support an `'error'` type so the `ErrorBar` can render failed-save messages distinctly from progress messages. Each rejected thunk (`createTodo`, `updateTodo`, `moveTodo`) should dispatch an error notification with a clear message.

### Acceptance Criteria
- `notificationsSlice` notification type includes `'error'` in addition to `'default'` and `'label'`
- `ErrorBar` renders error notifications with a visually distinct style (e.g. different background color or icon)
- `createTodo.rejected`, `updateTodo.rejected`, and `moveTodo.rejected` handlers dispatch an error notification (e.g. "Failed to save todo. Will retry when online.") instead of only `console.warn`
- `listTodos.rejected` does NOT show an error notification (polling failures should be silent to avoid noise)
- Existing unit tests pass; new unit tests cover each rejected mutation case showing an error notification in state

---

## Stage 3: Pending Mutation Queue & Retry on Reconnect

### Description

Create a `pendingMutationsSlice` that stores failed mutation operations (create, update, move) in a queue. When a mutation thunk is rejected due to a network error, add the operation to this queue instead of discarding it. When the network comes back online (detected via Stage 1's `setOnlineStatus`), automatically dispatch a retry thunk that processes all queued operations in order and then refreshes the todo list.

Design notes:
- Store the minimal operation payload (type + arguments) needed to re-dispatch the thunk
- Retry each operation sequentially to preserve ordering; remove from queue on success
- If a retry fails again, leave it in the queue for the next reconnect cycle
- Move operations use relative positioning (before/after another todo ID); retry them as-is since the referenced todo likely still exists within the same session

### Acceptance Criteria
- `pendingMutationsSlice` exists with a queue of `{ type: 'create' | 'update' | 'move', payload: ... }` entries
- `createTodo.rejected`, `updateTodo.rejected`, `moveTodo.rejected` handlers enqueue the failed operation
- A `retryPendingMutations` thunk exists that processes the queue sequentially
- `retryPendingMutations` is dispatched automatically when `setOnlineStatus(true)` fires (in the NetworkStatusListener / store middleware or in the listener component)
- Successfully retried operations are removed from the queue; failed retries remain
- After processing the queue, `listTodos()` is dispatched to reconcile server state
- Existing unit tests pass; new unit tests cover: (a) operations enqueued on rejection, (b) queue cleared after successful retry, (c) failed retry leaves operation in queue
