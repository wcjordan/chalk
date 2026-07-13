# Offline Support: Implementation Approach Notes

## Proposed Architecture

### Network State Detection

**Chosen approach:** Infer offline status from `listTodosApi.rejected` in a new `networkSlice`
using `extraReducers`. When `listTodosApi.fulfilled`, set `isOffline: false`.

**Concern:** A single failed poll (500, DNS blip) would flip the banner incorrectly.
**Mitigation options:**
- Distinguish `TypeError` (fetch network error) from HTTP error responses
- Require N consecutive failures before flipping
- Web: use `navigator.onLine` + `online`/`offline` events as primary signal (since `Platform.OS` is already used in fetchApi.ts)

### Offline Queue

**Location:** `networkSlice` (new Redux slice), fields:
- `isOffline: boolean`
- `pendingOfflineOps: OfflineOperation[]`

**OfflineOperation type (discriminated union):**
```ts
type OfflineOperation =
  | { type: 'update'; payload: TodoPatch }
  | { type: 'move'; payload: MoveTodoOperation }
  | { type: 'create'; payload: NewTodo & { tempId: number } }
```

### Queuing mutations

When `updateTodo.rejected` / `moveTodo.rejected` and `isOffline`:
- Add op to `pendingOfflineOps` in networkSlice
- The `shortcutSlice` already holds optimistic state visually; nothing extra needed for UI

When `createTodo.rejected` and `isOffline`:
- Generate temp negative ID (e.g., `-Date.now()`)
- Add todo to entries optimistically (with temp ID)
- Queue `{ type: 'create', payload: { ...newTodo, tempId } }`
- `pendingCreates` currently assumes server IDs; will need adjustment for temp IDs

### Reconnect flush ordering (CRITICAL)

Correct sequence when coming back online:
1. Flush offline queue first (each op updates entries via its `.fulfilled`)
2. THEN do a fresh `listTodos` to reconcile state with server

**Wrong order:** `listTodosApi.fulfilled` clears shortcutSlice ops via
`clearOperationsUpThroughGeneration` BEFORE queued mutations land — user sees
pre-edit state briefly.

**Implementation:** In `listTodos` thunk (reducers.ts), capture `wasOffline` before
dispatching `listTodosApi`. If `wasOffline && !isOffline` after success, call
`flushOfflineQueue()` first, then do another `listTodosApi` to reconcile.

### Persistence Question (OPEN)

The issue says "stored locally" — this is ambiguous:
- **In-memory only** (3 stages): queue in Redux, lost on app restart/tab close
- **Persistent** (4 stages): requires `redux-persist` + `AsyncStorage`/`localStorage`

No persistence infrastructure exists in this codebase. This answer significantly
changes the plan scope. **Must clarify with user.**

## Stage Draft (pending persistence answer)

**Stage 1:** Network slice + offline detection + offline banner UI
- `networkSlice.ts` with `isOffline`, `pendingOfflineOps`
- `extraReducers` listening to `listTodosApi` actions
- Permanent banner in `App.tsx` when offline

**Stage 2:** Queue update/move mutations; flush on reconnect
- Wrap `updateTodo`/`moveTodo` thunks to enqueue on rejection when offline
- `flushOfflineQueue` thunk with correct ordering (flush → then reconcile)

**Stage 3:** Queue create mutations with temp-ID optimistic UI
- Temp negative ID generation
- Adjust `pendingCreates`/`handleListResponse`/`cleanupPendingState` for temp IDs
- On flush: POST create → swap temp ID for real ID in entries

**Stage 4 (if persistence required):** Add `redux-persist` integration
- Persist `networkSlice.pendingOfflineOps` to `AsyncStorage` (native) / `localStorage` (web)
