import _ from 'lodash';
import { createAsyncThunk, createSlice, current } from '@reduxjs/toolkit';
import { selectActiveFilterLabels } from '../selectors';
import { RootState } from './store';
import {
  MoveTodoOperation,
  NewTodo,
  Todo,
  TodoPatch,
  TodosApiState,
} from './types';
import {
  create,
  getCsrfToken,
  getWsRoot,
  list,
  patch,
  postRequest,
} from './fetchApi';

const API_NAME = 'todosApi';

// Exported for testing
export function getTodosApi(): string {
  return `${getWsRoot()}api/todos/todos/`;
}

const initialState: TodosApiState = {
  entries: [],
  loading: false,
  initialLoad: true,
  pendingCreates: [],
  pendingArchives: [],
};

export const createTodo = createAsyncThunk<Todo, string, { state: RootState }>(
  `${API_NAME}/create`,
  async (todoTitle: string, { getState }) => {
    const state = getState();
    const activeLabels = selectActiveFilterLabels(state);

    const newTodo = {
      created_at: Date.now(),
      description: todoTitle,
      labels: activeLabels,
    };
    return create<Todo, NewTodo>(
      getTodosApi(),
      newTodo,
      getCsrfToken(getState),
    );
  },
);

export const listTodos = createAsyncThunk<Todo[], void, { state: RootState }>(
  `${API_NAME}/list`,
  async () => list<Todo>(getTodosApi()),
  {
    condition: (_unused, { getState }) => {
      return !getState().todosApi.loading;
    },
  },
);

export const updateTodo = createAsyncThunk<
  Todo,
  TodoPatch,
  { state: RootState }
>(`${API_NAME}/update`, async (entryPatch, { getState }) =>
  patch<Todo, TodoPatch>(getTodosApi(), entryPatch, getCsrfToken(getState)),
);

export const moveTodo = createAsyncThunk<
  Todo,
  MoveTodoOperation,
  { state: RootState }
>(`${API_NAME}/move`, async (moveOp, { getState }) =>
  postRequest<Todo, MoveTodoOperation>(
    `${getTodosApi()}${moveOp.todo_id}/reorder/`,
    moveOp,
    getCsrfToken(getState),
  ),
);

/**
 * Filter out archived todos.
 * Also sort completed todos to appear at the bottom.
 */
function processTodos(todos: Todo[]) {
  const unarchived = _.filter(todos, (todo) => !todo.archived);
  const completed = _.filter(unarchived, (todo) => todo.completed);
  const incomplete = _.filter(unarchived, (todo) => !todo.completed);
  return incomplete.concat(completed);
}

function updateTodoInPlace(existingEntry: Todo, updatedTodo: Todo) {
  // Extract the unproxied Immer value to compare against
  const currEntry = current(existingEntry);

  // Skip stale updates: if the server version is older than our local version,
  // this update doesn't include recent changes, so we should ignore it
  if (updatedTodo.version < currEntry.version) {
    console.debug(
      `Skipping stale update for todo ${updatedTodo.id}: ` +
        `server version ${updatedTodo.version} < local version ${currEntry.version}`,
    );
    return;
  }

  const todoKeys = Object.keys(updatedTodo) as (keyof Todo)[];
  for (const key of todoKeys) {
    if (!_.isEqual(currEntry[key], updatedTodo[key])) {
      existingEntry[key] = updatedTodo[key];
    }
  }
}

function updateTodoFromResponse(entries: Todo[], updatedTodo: Todo) {
  const existingEntry = _.find(
    entries,
    (entry: Todo) => entry.id === updatedTodo.id,
  );
  if (existingEntry) {
    updateTodoInPlace(existingEntry, updatedTodo);
    entries = processTodos(entries);
  } else {
    console.warn('Unable to find todo by id: ' + updatedTodo.id);
  }
  return entries;
}

function handleListResponse(entries: Todo[], updatedTodos: Todo[]) {
  const entryMap = _.keyBy(entries, (entry: Todo) => entry.id);
  for (const [index, updatedTodo] of updatedTodos.entries()) {
    const existingEntry = entryMap[updatedTodo.id];
    if (existingEntry) {
      updateTodoInPlace(existingEntry, updatedTodo);
      updatedTodos[index] = existingEntry;
    }
  }

  return processTodos(updatedTodos);
}

export const todosApiSlice = createSlice({
  name: API_NAME,
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      // create todo
      .addCase(createTodo.fulfilled, (state, action) => {
        state.entries.push(action.payload);
        state.entries = processTodos(state.entries);
      })
      .addCase(createTodo.rejected, (_, action) => {
        console.warn(`Creating Todo failed. ${action.error.message}`);
      })
      // list todos
      .addCase(listTodos.pending, (state) => {
        state.loading = true;
      })
      .addCase(listTodos.fulfilled, (state, action) => {
        state.initialLoad = false;
        state.loading = false;
        state.entries = handleListResponse(
          state.entries,
          Array.from(action.payload),
        );
      })
      .addCase(listTodos.rejected, (state, action) => {
        state.initialLoad = false;
        state.loading = false;
        console.warn(`Loading Todo failed. ${action.error.message}`);
      })
      // update todo
      .addCase(updateTodo.fulfilled, (state, action) => {
        state.entries = updateTodoFromResponse(state.entries, action.payload);
      })
      .addCase(updateTodo.rejected, (_, action) => {
        console.warn(`Updating Todo failed. ${action.error.message}`);
      })
      // reorder todo
      .addCase(moveTodo.fulfilled, (state, action) => {
        state.entries = updateTodoFromResponse(state.entries, action.payload);
      })
      .addCase(moveTodo.rejected, (_, action) => {
        console.warn(`Moving Todo failed. ${action.error.message}`);
      });
  },
});
