import _ from 'lodash';
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { ApiState, NewTodo, ReduxState, Todo, TodoPatch } from './types';
import { create, getCsrfToken, getWsRoot, list, patch } from './fetchApi';

const API_NAME = 'todosApi';

// Exported for testing
export function getTodosApi(): string {
  return `${getWsRoot()}api/todos/todos/`;
}

const initialState: ApiState<Todo> = {
  entries: [],
  loading: false,
  initialLoad: true,
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
 * Filter out archived todos.
 * Also sort completed todos to appear at the bottom.
 */
function processTodos(todos: Array<Todo>) {
  const unarchived = _.filter(todos, (todo) => !todo.archived);
  const completed = _.filter(unarchived, (todo) => todo.completed);
  const incomplete = _.filter(unarchived, (todo) => !todo.completed);
  return incomplete.concat(completed);
}

export default createSlice({
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
        state.entries = processTodos(action.payload);
      })
      .addCase(listTodos.rejected, (state, action) => {
        state.initialLoad = false;
        state.loading = false;
        console.warn(`Loading Todo failed. ${action.error.message}`);
      })
      // update todo
      .addCase(updateTodo.fulfilled, (state, action) => {
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
      })
      .addCase(updateTodo.rejected, (_, action) => {
        console.warn(`Updating Todo failed. ${action.error.message}`);
      });
  },
});
