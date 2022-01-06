import { Platform } from 'react-native';
import { ThunkAction } from 'redux-thunk';
import { Action, createSlice } from '@reduxjs/toolkit';

import { ReduxState, TodoPatch, WorkspaceState } from './types';
import labelsApiSlice, { listLabels } from './labelsApiSlice';
import todosApiSlice, {
  createTodo,
  listTodos,
  updateTodo as updateTodoApi,
} from './todosApiSlice';
import { completeAuthCallback } from './fetchApi';

type AppThunk = ThunkAction<void, ReduxState, unknown, Action<string>>;

const isWeb = Platform.select({
  native: false,
  default: true,
});

const initialWorkspace: WorkspaceState = {
  csrfToken: null,
  editId: null,
  labelTodoId: null,
  filterLabels: [],
  loggedIn: isWeb,
};
const workspaceSlice = createSlice({
  name: 'workspace',
  initialState: initialWorkspace,
  reducers: {
    filterByLabels: (state, action) => {
      state.filterLabels = Array.from(action.payload);
    },
    logIn: (state, action) => {
      state.loggedIn = action.payload.loggedIn;
      state.csrfToken = action.payload.csrfToken;
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

// Used only for mobile
export const completeAuthentication =
  (accessToken: string): AppThunk =>
  async (dispatch) => {
    const authResult = await completeAuthCallback(accessToken);
    if (authResult.status === 200) {
      dispatch(
        workspaceSlice.actions.logIn({
          loggedIn: true,
          csrfToken: authResult.csrfToken,
        }),
      );
    } else {
      // TODO
      console.log('Log in failed');
    }
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
