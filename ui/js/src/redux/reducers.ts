import { ThunkAction } from 'redux-thunk';
import { Action, createSlice } from '@reduxjs/toolkit';
import { getItemAsync, setItemAsync } from 'expo-secure-store';

import { ReduxState, TodoPatch, WorkspaceState } from './types';
import labelsApiSlice, { listLabels } from './labelsApiSlice';
import todosApiSlice, {
  createTodo,
  listTodos,
  updateTodo as updateTodoApi,
} from './todosApiSlice';
import { completeAuthCallback } from './fetchApi';

type AppThunk = ThunkAction<void, ReduxState, unknown, Action<string>>;

const initialWorkspace: WorkspaceState = {
  editId: null,
  labelTodoId: null,
  filterLabels: [],
  sessionCookie: null,
};
const workspaceSlice = createSlice({
  name: 'workspace',
  initialState: initialWorkspace,
  reducers: {
    filterByLabels: (state, action) => {
      state.filterLabels = Array.from(action.payload);
    },
    setSessionCookie: (state, action) => {
      const sessionCookie = action.payload;
      state.sessionCookie = sessionCookie;
      setItemAsync('session_cookie', sessionCookie);
    },
    setTodoLabelingId: (state, action) => {
      state.labelTodoId = action.payload;
    },
    setTodoEditId: (state, action) => {
      state.editId = action.payload;
    },
  },
});

export const updateTodo =
  (todoPatch: TodoPatch): AppThunk =>
  (dispatch) => {
    return Promise.all([
      dispatch(workspaceSlice.actions.setTodoEditId(null)),
      dispatch(updateTodoApi(todoPatch)),
    ]);
  };

export const updateTodoLabels =
  (labels: string[]): AppThunk =>
  (dispatch, getState) => {
    const todoId = getState().workspace.labelTodoId;
    if (todoId === null) {
      throw new Error('Unable to edit a todo w/ null ID');
    }

    return dispatch(
      updateTodoApi({
        id: todoId,
        labels,
      }),
    );
  };

export const completeAuthentication =
  (accessToken: string): AppThunk =>
  async (dispatch) => {
    const cookie = await completeAuthCallback(accessToken);
    return dispatch(workspaceSlice.actions.setSessionCookie(cookie));
  };

export const loadSessionCookie = (): AppThunk => async (dispatch) => {
  const cookie = await getItemAsync('session_cookie');
  return dispatch(workspaceSlice.actions.setSessionCookie(cookie));
};

export const filterByLabels = workspaceSlice.actions.filterByLabels;
export const setTodoEditId = workspaceSlice.actions.setTodoEditId;
export const setTodoLabelingId = workspaceSlice.actions.setTodoLabelingId;
export { createTodo, listLabels, listTodos };
export default {
  labelsApi: labelsApiSlice.reducer,
  todosApi: todosApiSlice.reducer,
  workspace: workspaceSlice.reducer,
};
