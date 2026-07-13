# Implementation Plan: Handle Being Offline (minordomo-2nt)

## Overview

When offline, the user should see an indication of their connectivity status. Todo changes that fail to save should be retained in memory and automatically applied once the connection is restored.

The app currently uses Redux Toolkit with `createAsyncThunk` and polls every 10 seconds. All failed API calls are silently swallowed with `console.warn` only. There is no network detection, no offline UI, and no retry logic.

**Network detection approach (no new packages):**
- Web: `window.addEventListener('online'/'offline')` + seed from `navigator.onLine`
- Native: two consecutive `listTodos.rejected` actions flip `isOnline` to `false`; any `listTodos.fulfilled` resets it to `true`

---

## Stage 1: Network Status Detection and Redux Slice

### Description

Add a `networkSlice` to Redux (`ui/js/src/redux/networkSlice.ts`) that tracks `isOnline: boolean`, defaulting to `true`. Create a platform-split `useNetworkMonitor` hook:

- `ui/js/src/hooks/useNetworkMonitor.web.ts`: subscribes to `window` `online` / `offline` events and seeds from `navigator.onLine`.
- `ui/js/src/hooks/useNetworkMonitor.ts` (native fallback): seeds `isOnline: true`, then the slice itself tracks consecutive `listTodos` failures (two rejections = offline, any fulfillment = online) via `extraReducers` in `networkSlice`.

Wire the web hook into `App.tsx`. The native path updates automatically via `extraReducers` reacting to `listTodos` actions — no hook wiring needed.

Add `networkSlice.reducer` to `rootReducerConfig` in `reducers.ts`.

### Acceptance Criteria
- `networkSlice` initialises `isOnline` to `true` and exposes a `setOnlineStatus(boolean)` action.
- On web, the `useNetworkMonitor` hook dispatches `setOnlineStatus(false/true)` when browser fires `offline`/`online` events; `App.tsx` calls this hook.
- On native, `networkSlice.extraReducers` increments a `consecutiveFailures` counter on `listTodos.rejected`; at ≥2 failures it sets `isOnline: false`. Any `listTodos.fulfilled` resets `consecutiveFailures` to 0 and sets `isOnline: true`.
- `make test` passes; unit tests cover: `setOnlineStatus` action, failure counter logic in `extraReducers`.

---

## Stage 2: Offline UI Indicator and Polling Pause

### Description

Show a persistent "You are offline" banner while `isOnline` is `false`. Use the existing `ErrorBar` component (with `permanent={true}`) rendered above the normal notification queue in `App.tsx`. When `isOnline` is `true`, the offline banner is hidden and normal notifications resume.

Also update `useDataLoader` to pause the 10-second poll interval while offline and restart it immediately when connectivity returns.

### Acceptance Criteria
- When `network.isOnline === false`, `App.tsx` renders `<ErrorBar permanent text="You are offline" />` regardless of any notification queue entries.
- When `network.isOnline === true`, the offline banner is not rendered.
- `useDataLoader` clears the interval while offline and re-establishes it (dispatching `listTodos()` immediately) when `isOnline` transitions back to `true`.
- `make test` passes; snapshot and unit tests cover: offline banner visible when `isOnline=false`, absent when `isOnline=true`; polling pauses/resumes.

---

## Stage 3: Pending Mutation Queue and Retry on Reconnect

### Description

Add an `offlineQueueSlice` (`ui/js/src/redux/offlineQueueSlice.ts`) that holds a list of failed operations: `{ type: 'create' | 'update' | 'move', payload: string | TodoPatch | MoveTodoOperation }`.

Update the mutation thunks in `reducers.ts` (`updateTodo`, `moveTodo`) and the `createTodo` rejected handler in `todosApiSlice.ts` to enqueue the failed operation when `network.isOnline === false`.

Add a `flushOfflineQueue` thunk in `reducers.ts` that drains the queue sequentially: dispatches each queued operation via the normal thunks (`createTodo` / `updateTodo` / `moveTodo`), removes entries on success, leaves them on failure. After draining, dispatches `listTodos()` to reconcile. On full success dispatches a `"Changes synced"` notification.

Trigger `flushOfflineQueue` automatically when `setOnlineStatus(true)` is dispatched — wire this in `App.tsx` via a `useEffect` watching `network.isOnline`, or in a dedicated listener hook.

This is in-memory only; the queue does not survive app restarts.

### Acceptance Criteria
- `offlineQueueSlice` exists with `enqueue` and `dequeue` (by index) actions.
- When `createTodo`, `updateTodo`, or `moveTodo` is rejected and `network.isOnline === false`, the failed operation is added to the queue.
- `flushOfflineQueue` processes operations in FIFO order; successful operations are removed from the queue.
- Operations that fail during the flush remain in the queue; a "Some changes could not be synced" notification is shown.
- When `network.isOnline` transitions to `true`, `flushOfflineQueue` is dispatched automatically.
- `make test` passes; unit tests cover: enqueue on rejection when offline, flush ordering, notifications on success/failure.
