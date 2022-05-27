import _ from 'lodash';
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { ApiState, NewTodo, ReduxState, Todo, TodoPatch } from './types';
import { create, getCsrfToken, getWsRoot, list, patch } from './fetchApi';

const API_NAME = 'todosApi';

// Exported for testing
export function getTodosApi(): string {
  return `${getWsRoot()}api/todos/todos/`;
}

interface ErrorAction {
  error: Error;
}

interface TodoAction {
  payload: Todo;
}

interface TodoListAction {
  payload: Array<Todo>;
}

const initialState: ApiState<Todo> = {
  entries: [],
  loading: false,
};

export const createTodo = createAsyncThunk<Todo, string, { state: ReduxState }>(
  `${API_NAME}/create`,
  async (todoTitle: string, { getState }) => {
    const newTodo = {
      created_at: Date.now(),
      description: todoTitle,
      labels: [],
    };
    return create<Todo, NewTodo>(
      getTodosApi(),
      newTodo,
      getCsrfToken(getState),
    );
  },
);

export const listTodos = createAsyncThunk<Todo[], void, { state: ReduxState }>(
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
  { state: ReduxState }
>(`${API_NAME}/update`, async (entryPatch, { getState }) =>
  patch<Todo, TodoPatch>(getTodosApi(), entryPatch, getCsrfToken(getState)),
);

/**
 * Filter out archived todos and sort todos by id.
 * Also sort completed todos to appear at the bottom.
 */
function processTodos(todos: Array<Todo>) {
  return _.sortBy(
    _.filter(todos, (todo) => !todo.archived),
    ['completed', 'id'],
  );
}

export default createSlice({
  name: API_NAME,
  initialState,
  reducers: {},
  extraReducers: {
    [createTodo.fulfilled.type]: (state, action: TodoAction) => {
      state.entries.push(action.payload);
      state.entries = processTodos(state.entries);
    },
    [createTodo.rejected.type]: (_state, action: ErrorAction) => {
      console.warn(`Creating Todo failed. ${action.error.message}`);
    },
    [listTodos.pending.type]: (state) => {
      state.loading = true;
    },
    [listTodos.fulfilled.type]: (state, action: TodoListAction) => {
      state.loading = false;
      state.entries = processTodos(action.payload);
    },
    [listTodos.rejected.type]: (state, action: ErrorAction) => {
      state.loading = false;
      console.warn(`Loading Todo failed. ${action.error.message}`);
    },
    [updateTodo.fulfilled.type]: (state, action: TodoAction) => {
      const updatedEntry = action.payload;
      const existingEntry = _.find(
        state.entries,
        (entry) => entry.id === updatedEntry.id,
      );
      if (existingEntry) {
        Object.assign(existingEntry, updatedEntry);
        state.entries = processTodos(state.entries);
      } else {
        console.warn('Unable to find todo by id: ' + updatedEntry.id);
      }
    },
    [updateTodo.rejected.type]: (_state, action: ErrorAction) => {
      console.warn(`Updating Todo failed. ${action.error.message}`);
    },
  },
});
