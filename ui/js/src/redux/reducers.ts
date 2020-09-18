import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import {
  ApiState,
  AppThunk,
  ReduxState,
  Todo,
  TodoPatch,
  WorkspaceState,
} from './types';
import createApiReducer from './reducers/createApiReducer';
import getRequestOpts from './getRequestOptions';

const API_NAME = 'todosApi';
const TODOS_API = 'api/todos/todos/';

export const createTodo = createAsyncThunk<
  Todo,
  string,
  {
    state: ReduxState;
  }
>(`${API_NAME}/create`, async (todoTitle: string) => {
  // TODO persist todo - see createApiReducer for example
  const newTodo = {
    created_at: Date.now(),
    description: todoTitle,
  };

  const requestOpts = getRequestOpts('POST');
  requestOpts.body = JSON.stringify(newTodo);
  const response = await fetch(TODOS_API, requestOpts);
  return await response.json();
});

interface CreateTodoAction {
  payload: Todo;
}

const {
  fetchThunk: fetchTodos,
  updateThunk,
  reducer: todosReducer,
} = createApiReducer<Todo, TodoPatch>(
  API_NAME,
  TODOS_API,
  state => state.todosApi,
  {
    [createTodo.fulfilled.type]: (
      state: ApiState<Todo>,
      action: CreateTodoAction,
    ) => {
      state.entries.push(action.payload);
    },
  },
);

const initialWorkspace: WorkspaceState = {
  editId: null,
};
const workspaceSlice = createSlice({
  name: 'workspace',
  initialState: initialWorkspace,
  reducers: {
    editTodo: (state, action) => {
      state.editId = action.payload;
      return state;
    },
    updateTodo: state => {
      state.editId = null;
    },
  },
});

export const updateTodo = (
  id: number,
  description: string,
): AppThunk => dispatch => {
  dispatch(workspaceSlice.actions.updateTodo());
  dispatch(
    updateThunk({
      id,
      description,
    }),
  );
};

const editTodo = workspaceSlice.actions.editTodo;
export { fetchTodos, editTodo };
export default {
  todosApi: todosReducer,
  workspace: workspaceSlice.reducer,
};
