import _ from 'lodash';
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { ApiState, ReduxState, Todo, TodoPatch } from './types';
import { create, list, patch } from './fetchApi';

const API_NAME = 'todosApi';
const TODOS_API = 'api/todos/todos/';

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

export const createTodo = createAsyncThunk<Todo, string, {}>(
  `${API_NAME}/create`,
  async (todoTitle: string) => {
    const newTodo = {
      created_at: Date.now(),
      description: todoTitle,
    };
    return create(TODOS_API, newTodo);
  },
);

export const listTodos = createAsyncThunk<Todo[], void, { state: ReduxState }>(
  `${API_NAME}/fetch`,
  async () => list(TODOS_API),
  {
    condition: (_unused, { getState }) => {
      return !getState().todosApi.loading;
    },
  },
);

export const updateTodo = createAsyncThunk<Todo, TodoPatch, {}>(
  `${API_NAME}/update`,
  async entryPatch => patch(TODOS_API, entryPatch),
);

function sortTodos(todos: Array<Todo>) {
  return _.sortBy(todos, ['completed', 'id']);
}

export default createSlice({
  name: API_NAME,
  initialState,
  reducers: {},
  extraReducers: {
    [createTodo.fulfilled.type]: (state, action: TodoAction) => {
      state.entries.push(action.payload);
      state.entries = sortTodos(state.entries);
    },
    [listTodos.pending.type]: state => {
      state.loading = true;
    },
    [listTodos.fulfilled.type]: (state, action: TodoListAction) => {
      state.loading = false;
      state.entries = sortTodos(action.payload);
    },
    [listTodos.rejected.type]: (state, action: ErrorAction) => {
      state.loading = false;
      console.warn(`Loading ${API_NAME} failed. ${action.error.message}`);
    },
    [updateTodo.fulfilled.type]: (state, action: TodoAction) => {
      const updatedEntry = action.payload;
      const existingEntry = _.find(
        state.entries,
        entry => entry.id === updatedEntry.id,
      );
      Object.assign(existingEntry, updatedEntry);
      state.entries = sortTodos(state.entries);
    },
    [updateTodo.rejected.type]: (_unused, action: ErrorAction) => {
      console.warn(`Updating ${API_NAME} failed. ${action.error.message}`);
    },
  },
});
