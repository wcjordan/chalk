# Implementation Plan: Handle Being Offline (minordomo-2nt)

## Overview

When offline, the user should see an indication of their connectivity status. Todo changes that fail to save should be retained locally and automatically applied once the connection is restored. The queue **must survive app restarts** (persistent storage confirmed by owner in GH issue #336 comments).

The app currently uses Redux Toolkit with `createAsyncThunk` and polls every 10 seconds. All failed API calls are silently swallowed with `console.warn` only. There is no network detection, no offline UI, and no retry logic.

**Network detection approach (no extra packages for detection):**
- Web: `window.addEventListener('online'/'offline')` + seed from `navigator.onLine`
- Native: `listTodos.rejected` with `error.name === 'TypeError'` increments a failure counter in `networkSlice.extraReducers`; ≥2 consecutive network-error failures flip `isOnline` to `false`. Any `listTodos.fulfilled` resets to `true`. HTTP errors (non-TypeError rejections) do NOT affect the counter.

**Key design decisions baked into the spec:**
- Polling at 10s continues even while offline — it is the reconnection signal on native (we cannot pause it).
- Offline banner uses a separate `<OfflineBanner>` component, not the existing `ErrorBar`/Snackbar, to avoid blocking transient notifications from rendering.
- `isOnline` is never persisted (starts `true` on every launch; accurate state is discovered quickly from the first poll or browser event).
- Persistence covers the offline op queue AND `todosApi.entries`/`pendingCreates`/`pendingArchives`, so the user sees their todos if they reopen the app while still offline.

---

## Stage 1: Network Status Detection and Redux Slice

### Description

Add a `networkSlice` to Redux (`ui/js/src/redux/networkSlice.ts`) that tracks:
- `isOnline: boolean` (default `true`)
- `consecutiveNetworkFailures: number` (default `0`) — used for native offline detection

Expose actions: `setOnlineStatus(boolean)` and (internal) `recordListTodosResult({ success: boolean, isNetworkError: boolean })`.

In `extraReducers`, react to `listTodosApi` actions:
- `listTodos.fulfilled`: reset `consecutiveNetworkFailures` to `0`, set `isOnline: true`.
- `listTodos.rejected`: if `action.error.name === 'TypeError'` (network error, not HTTP error), increment `consecutiveNetworkFailures`; if `consecutiveNetworkFailures >= 2`, set `isOnline: false`. Non-TypeError rejections (HTTP 4xx/5xx) do not affect either field.

Create a platform-split `useNetworkMonitor` hook:
- `ui/js/src/hooks/useNetworkMonitor.web.ts`: on mount, subscribe to `window` `online`/`offline` events and seed from `navigator.onLine`. Dispatch `setOnlineStatus` on each event. Cleanup the listeners on unmount.
- `ui/js/src/hooks/useNetworkMonitor.ts` (native fallback): no-op — native detection is handled entirely by `extraReducers`.

Call `useNetworkMonitor()` in `App.tsx`.

Add `network: networkSlice.reducer` to `rootReducerConfig` in `reducers.ts`.

### Acceptance Criteria
- `networkSlice` initialises `isOnline: true`, `consecutiveNetworkFailures: 0`.
- `setOnlineStatus(false)` sets `isOnline: false`; `setOnlineStatus(true)` sets `isOnline: true` and resets `consecutiveNetworkFailures` to `0`.
- `listTodos.rejected` with a `TypeError` increments `consecutiveNetworkFailures`; at `2` sets `isOnline: false`.
- `listTodos.rejected` with a non-TypeError error (e.g., `Error: 500 Internal Server Error`) does NOT change `isOnline` or `consecutiveNetworkFailures`.
- `listTodos.fulfilled` resets `consecutiveNetworkFailures` to `0` and sets `isOnline: true`.
- `useNetworkMonitor.web.ts` dispatches `setOnlineStatus` on `online`/`offline` browser events.
- `make test` passes; unit tests cover all `extraReducers` cases and `setOnlineStatus` action.

---

## Stage 2: Offline Banner UI

### Description

Show a persistent "You are offline" banner while `isOnline` is `false`, rendered in `App.tsx` above the todo content and the existing `ErrorBar` notification snackbar. Use a new `OfflineBanner` component (`ui/js/src/components/OfflineBanner.tsx`) — not `ErrorBar` — to avoid interfering with the transient notification queue.

`OfflineBanner` is a non-dismissible bar (e.g., a `View` with a `Text` or `react-native-paper`'s `Banner`) that renders when `props.visible === true`.

When `isOnline` is `true`, `OfflineBanner` is hidden.

**Polling behaviour:** do NOT pause the 10-second poll in `useDataLoader` while offline. The poll continues — it is what drives the `listTodos.fulfilled` event that signals reconnection on native. (Web reconnection is signalled by the browser `online` event, but the poll catching up is still needed to refresh data.)

### Acceptance Criteria
- `OfflineBanner` renders a visible message when `visible={true}` and renders nothing (or hidden) when `visible={false}`.
- `App.tsx` reads `network.isOnline` and passes `visible={!isOnline}` to `OfflineBanner`.
- `ErrorBar` (notification snackbar) continues to render independently below — both can be visible simultaneously.
- `useDataLoader` polling interval is unchanged (continues at 10s regardless of `isOnline` state).
- `make test` passes; snapshot tests cover: banner visible when `isOnline=false`; banner hidden when `isOnline=true`; both `OfflineBanner` and `ErrorBar` present in `App.tsx` snapshot.

---

## Stage 3: Offline Mutation Queue and Flush on Reconnect

### Description

Add `offlineQueueSlice` (`ui/js/src/redux/offlineQueueSlice.ts`) with state `pendingOps: OfflineOperation[]` and actions `enqueueOp` and `dequeueOpByIndex`.

```ts
type OfflineOperation =
  | { type: 'create'; payload: { description: string; labels: string[] } }
  | { type: 'update'; payload: TodoPatch }
  | { type: 'move'; payload: MoveTodoOperation }
```

Add `offlineQueue: offlineQueueSlice.reducer` to `rootReducerConfig`.

**Queuing mutations:**
Modify the `updateTodo` and `moveTodo` thunks in `reducers.ts` to enqueue on rejection whenever the failure is a network error — regardless of the current `network.isOnline` flag. This is deliberate: native offline detection requires 2 consecutive network failures before `isOnline` flips to `false` (see Stage 1), so gating on `isOnline` would drop the first failed mutation. HTTP errors (non-`TypeError` rejections, e.g. 4xx/5xx) are NOT enqueued, since retrying them would fail identically.
```ts
const result = await dispatch(updateTodoApi(todoPatch));
if (updateTodoApi.rejected.match(result) && result.error.name === 'TypeError') {
  dispatch(offlineQueueSlice.actions.enqueueOp({ type: 'update', payload: todoPatch }));
}
```
Do the same for `moveTodoApi`. For `createTodo`, catch the rejected result in `reducers.ts` (not in `todosApiSlice.ts` which currently only logs) and, on a `TypeError` rejection, enqueue with `{ type: 'create', payload: { description, labels } }`.

**Flush thunk:**
Add `flushOfflineQueue` thunk in `reducers.ts`. It reads `pendingOps`, clears the queue, then runs each op sequentially via the normal thunks (`createTodo`, `updateTodoApi`, `moveTodoApi`). On completion, dispatches `listTodosApi()` to reconcile. Dispatches a `"Changes synced"` notification on full success, or `"Some changes could not be synced"` if any op fails (and re-enqueues failed ops).

**Trigger flush on reconnect:**
In `App.tsx`, add a `useEffect` watching `network.isOnline`: when it transitions to `true`, dispatch `flushOfflineQueue()`. This handles both web (`online` event → `setOnlineStatus(true)`) and native (`listTodos.fulfilled` → `extraReducers` sets `isOnline: true`).

Note: Stage 3 queue is in-memory only (no persistence yet — Stage 4 adds persistence).

### Acceptance Criteria
- `offlineQueueSlice` `enqueueOp` appends to `pendingOps`; `dequeueOpByIndex` removes by index.
- When `updateTodoApi` or `moveTodoApi` is rejected with a `TypeError` (network error), the operation is enqueued — regardless of the current `network.isOnline` value (covers the case where the failure occurs before `isOnline` has flipped to `false`).
- When `updateTodoApi` or `moveTodoApi` is rejected with a non-`TypeError` (HTTP error), the operation is NOT enqueued.
- When `createTodo` (the thunk in `reducers.ts`) fails with a `TypeError`, a `create` op is enqueued regardless of `network.isOnline`; a non-`TypeError` failure is not enqueued.
- `flushOfflineQueue` processes ops in FIFO order; successful ops are removed; failed ops are re-enqueued.
- After flush, `listTodosApi` is called for reconciliation.
- Appropriate success/failure notifications are shown.
- When `network.isOnline` transitions to `true`, `flushOfflineQueue` is dispatched.
- `make test` passes; unit tests cover: enqueue on network-error rejection regardless of `isOnline` state, no enqueue on HTTP-error rejection, flush ordering, notification on success/failure, flush triggered on `isOnline` transition.

---

## Stage 4: Persistent Offline Queue and Cached Todos

### Description

Make the offline queue and the todo list survive app restarts using `redux-persist`.

**Packages to add:**
- `redux-persist` (core)
- `@react-native-async-storage/async-storage` (native storage engine)

**Storage engine (platform-split):**
```ts
// ui/js/src/redux/persistStorage.ts
import { Platform } from 'react-native';
// Use a conditional require so bundlers don't include the unused engine:
const storage =
  Platform.OS === 'web'
    ? require('redux-persist/lib/storage').default   // localStorage
    : require('@react-native-async-storage/async-storage').default; // AsyncStorage
export default storage;
```

**What to persist and what to exclude:**

Two nested `persistReducer` calls (within `rootReducerConfig` construction in `reducers.ts`):

1. `offlineQueue` slice — persist the whole slice (only `pendingOps`). Key: `'offlineQueue'`.

2. `todosApi` slice — persist `entries`, `pendingCreates`, `pendingArchives` but NOT `loading` or `initialLoad`. Key: `'todosApi'`. Use `blacklist: ['loading', 'initialLoad']` in its persist config.

`isOnline` is NOT persisted (always starts `true`; accurate state discovered within seconds from first poll or browser event).

**Store changes (`store.ts`):**
- Wrap affected reducers with `persistReducer` before passing to `combineReducers`.
- Call `persistStore(store)` in a new `createPersistor(store)` export.
- Add the `redux-persist` serializable-check middleware exception (`serializableCheck: { ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER] }`).
- **Test environment bypass:** in `reducers.ts` where persist configs are applied, guard with `process.env.NODE_ENV !== 'test'`; in test environment use the plain reducers. This avoids changes to any existing test files.

**App bootstrap (`index.ts` / `App.tsx`):**
- Create the persistor via `createPersistor(store)`.
- Wrap the app root with `<PersistGate loading={null} persistor={persistor}>` from `redux-persist/integration/react`.

### Acceptance Criteria
- `redux-persist` and `@react-native-async-storage/async-storage` are added to `package.json`; `yarn.lock` updated.
- `offlineQueueSlice` state is serialized to storage on every change and rehydrated on launch.
- `todosApi.entries`, `pendingCreates`, `pendingArchives` are persisted; `loading` and `initialLoad` are not.
- After simulating an app restart in tests (store rehydration), `pendingOps` from the prior session are present and `isOnline` is `true`.
- No existing unit tests are modified (test environment uses plain reducers via `NODE_ENV` guard).
- `make test` passes.
