import _ from 'lodash';
import { createAsyncThunk, createSlice, current } from '@reduxjs/toolkit';
import { RootState } from './store';
import {
  ApiState,
  MoveTodoOperation,
  NewTodo,
  Todo,
  TodoPatch,
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

const initialState: ApiState<Todo> = {
  entries: [],
  loading: false,
  initialLoad: true,
};

export const createTodo = createAsyncThunk<Todo, string, { state: RootState }>(
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

function updateTodosFromResponse(entries: Todo[], updatedTodos: Todo[]) {
  const entryMap = _.keyBy(entries, (entry: Todo) => entry.id);
  for (const updatedTodo of updatedTodos) {
    const existingEntry = entryMap[updatedTodo.id];
    if (existingEntry) {
      // Extract the unproxied Immer value to compare against
      const currEntry = current(existingEntry);
      for (const key of Object.keys(updatedTodo)) {
        if (!_.isEqual(currEntry[key as keyof Todo], updatedTodo[key as keyof Todo])) {
          existingEntry[key as keyof Todo] = updatedTodo[key as keyof Todo];
        }
      }
    } else {
      entries.push(updatedTodo);
    }
  }

  return processTodos(entries);
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
        state.entries = updateTodosFromResponse(state.entries, action.payload);
      })
      .addCase(listTodos.rejected, (state, action) => {
        state.initialLoad = false;
        state.loading = false;
        console.warn(`Loading Todo failed. ${action.error.message}`);
      })
      // update todo
      .addCase(updateTodo.fulfilled, (state, action) => {
        state.entries = updateTodosFromResponse(state.entries, [action.payload]);
      })
      .addCase(updateTodo.rejected, (_, action) => {
        console.warn(`Updating Todo failed. ${action.error.message}`);
      })
      // reorder todo
      .addCase(moveTodo.fulfilled, (state, action) => {
        state.entries = updateTodosFromResponse(state.entries, [action.payload]);
      })
      .addCase(moveTodo.rejected, (_, action) => {
        console.warn(`Moving Todo failed. ${action.error.message}`);
      });
  },
});
