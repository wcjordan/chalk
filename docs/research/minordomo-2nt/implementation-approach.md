# Offline Support: Implementation Approach Notes

## Confirmed Decisions (from GH issue #336 owner)

- **Persistent storage required**: The queue must survive app restarts. Owner explicitly confirmed in comments.
- See `docs/planning/minordomo-2nt-spec.md` for the complete 4-stage plan.

## Architecture

### Network State Detection

**Web:** `window` `online`/`offline` events + seed from `navigator.onLine` via `useNetworkMonitor.web.ts` hook.

**Native:** `networkSlice.extraReducers` reacts to `listTodosApi` actions:
- `fulfilled` → `isOnline: true`, reset failure counter
- `rejected` with `TypeError` (network error, not HTTP error) → increment `consecutiveNetworkFailures`; ≥2 sets `isOnline: false`
- rejected with non-TypeError → no change (500s, 404s don't flip offline status)

**Why keep polling while offline:** The 10s poll is the only reconnection signal on native. Pausing it would require a separate mechanism to detect coming back online. Web has browser events, but keeping the poll going on web too is simpler and keeps data fresh on reconnect.

### Offline Banner

Use a separate `<OfflineBanner>` component (not `ErrorBar`/Snackbar) rendered in `App.tsx`. The `ErrorBar` Snackbar is for the transient notification queue — mixing a permanent offline indicator into the same Snackbar would block notifications from rendering while offline.

### Offline Queue

`offlineQueueSlice` with `pendingOps: OfflineOperation[]`:
```ts
type OfflineOperation =
  | { type: 'create'; payload: { description: string; labels: string[] } }
  | { type: 'update'; payload: TodoPatch }
  | { type: 'move'; payload: MoveTodoOperation }
```

### Queuing Mutations

Modify `updateTodo`/`moveTodo` thunks in `reducers.ts` to check the rejected result and dispatch `enqueueOp` when offline. For `createTodo`, same pattern (moved from `todosApiSlice.ts` rejected handler).

### Flush Ordering (CRITICAL)

`flushOfflineQueue` → sequential op dispatch → `listTodosApi()` for reconciliation.

**Wrong order:** calling `listTodosApi` first clears shortcutSlice ops before queued mutations land. User briefly sees pre-edit state.

Flush is triggered from `App.tsx` `useEffect` on `network.isOnline` → `true`. Works for both web (set by browser event) and native (set by `extraReducers` on `listTodos.fulfilled`).

### Persistence (Stage 4)

Two nested `persistReducer` configurations:
- `offlineQueue`: full persistence (only has `pendingOps`)
- `todosApi`: blacklist `['loading', 'initialLoad']`; persist `entries`/`pendingCreates`/`pendingArchives`

`isOnline` is NOT persisted — always starts `true`.

Platform-split storage:
- Web: `redux-persist/lib/storage` (localStorage)
- Native: `@react-native-async-storage/async-storage`

Test bypass: `process.env.NODE_ENV === 'test'` skips `persistReducer` entirely, so existing test files don't need changes.

### Packages Required (Stage 4)

- `redux-persist`
- `@react-native-async-storage/async-storage`
