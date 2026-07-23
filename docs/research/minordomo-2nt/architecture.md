# Offline Support Research: Chalk Architecture

## State Management

**Framework:** Redux Toolkit with `createSlice` + `createAsyncThunk` (NOT RTK Query)

- Store: `ui/js/src/redux/store.ts` — bare `configureStore`, no persistence middleware
- Main thunks: `ui/js/src/redux/reducers.ts` (updateTodo, moveTodo, listTodos, createTodo)
- Todo CRUD async thunks: `ui/js/src/redux/todosApiSlice.ts`
- Optimistic op queue: `ui/js/src/redux/shortcutSlice.ts`
- Notifications: `ui/js/src/redux/notificationsSlice.ts`

## Todo Fetching & Mutation Flow

### Fetching
- `useDataLoader` hook (`ui/js/src/hooks/hooks.ts` lines 8-24): polls every 10 seconds unconditionally
- No exponential backoff, no pause when offline

### CRUD Operations
- CREATE: POST `/api/todos/todos/` → pushes to `entries` + `pendingCreates` on success; only `console.warn` on failure
- UPDATE: PATCH `/api/todos/todos/{id}/` → updates entry in place on success; only `console.warn` on failure
- MOVE: POST `/api/todos/todos/{id}/reorder/` → only `console.warn` on failure

## Optimistic Update Infrastructure (Partial Foundation Exists)

### shortcutSlice (`ui/js/src/redux/shortcutSlice.ts`)
- Queues EDIT_TODO and MOVE_TODO operations with generation numbers
- Applied visually via selector `selectShortcuttedTodoEntries` (`ui/js/src/selectors.ts` lines 21-73)
- Cleared after successful `listTodos` via `clearOperationsUpThroughGeneration`

### pendingCreates / pendingArchives
- `todosApiSlice.ts`: tracks IDs of locally-created/archived todos
- Cleared by `cleanupPendingState()` when server confirms the todo in list response

### Version-based Conflict Detection
- `updateTodoInPlace()` (`todosApiSlice.ts` lines 102-122): skips stale updates if `updatedTodo.version < currEntry.version`
- Django model increments `version` on every save (prevents overwriting newer changes)

## Critical Gaps for Offline Support

### No Network Detection
- No `@react-native-community/netinfo` import
- No connectivity hook or network status listener
- No mechanism to pause polling when offline

### No Persistence
- No `redux-persist`, no `AsyncStorage`, no `IndexedDB`
- All state lost on app restart

### Silent Error Handling
All four async thunks have `.rejected` handlers that only log to console:
- `createTodo.rejected` (line 205-207): `console.warn("Creating Todo failed...")`
- `listTodos.rejected` (line 230-234): sets `loading=false` + `console.warn()`
- `updateTodo.rejected` (line 242-244): `console.warn()`
- `moveTodo.rejected` (line 249-251): `console.warn()`

The `ErrorBar` component is only used for optimistic progress messages ("Saving Todo: ..."), not for errors.

## UI Components

- `ui/js/src/App.tsx`: Root component, renders `ErrorBar` for notifications
- `ui/js/src/components/ErrorBar.tsx`: Snackbar-style notification (types: `'default' | 'label'`)
- `ui/js/src/redux/notificationsSlice.ts`: Notification queue

## Server API

- `server/chalk/todos/models.py`: `TodoModel` with `version`, `completed_at`, `archived_at`, `order_rank`
- `server/chalk/todos/views.py`: REST endpoints for todos and labels
- Authentication: CSRF token for non-GET requests; session cookie for mobile
