import { ThunkAction } from 'redux-thunk';
import { Action } from '@reduxjs/toolkit';

import { ReduxState, TodoPatch } from './types';
import labelsApiSlice, { listLabels } from './labelsApiSlice';
import notificationsSlice from './notificationsSlice';
import todosApiSlice, {
  createTodo,
  listTodos,
  updateTodo as updateTodoApi,
} from './todosApiSlice';
import workspaceSlice from './workspaceSlice';
import { completeAuthCallback } from './fetchApi';

type AppThunk = ThunkAction<void, ReduxState, unknown, Action<string>>;

export const updateTodo =
  (todoPatch: TodoPatch): AppThunk =>
  (dispatch) => {
    return Promise.all([
      dispatch(
        notificationsSlice.actions.addNotification(
          `Saving Todo: ${todoPatch.description}`,
        ),
      ),
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

// Used to exchange login token for session cookie in mobile login flow
export const completeAuthentication =
  (accessToken: string): AppThunk =>
  async (dispatch) => {
    try {
      const authResult = await completeAuthCallback(accessToken);
      if (authResult.status === 200) {
        dispatch(
          workspaceSlice.actions.logIn({
            loggedIn: true,
            csrfToken: authResult.csrfToken,
          }),
        );
      } else {
        // TODO Login failed w/ status & message
        // response.status and response.statusText and response.text()
        dispatch(
          notificationsSlice.actions.addNotification(
            `Login failed with status: ${authResult.status}`,
          ),
        );
      }
    } catch (ex) {
      // TODO Login failed with error
    }
  };

export const dismissNotification =
  notificationsSlice.actions.dismissNotification;
export const filterByLabels = workspaceSlice.actions.filterByLabels;
export const setTodoEditId = workspaceSlice.actions.setTodoEditId;
export const setTodoLabelingId = workspaceSlice.actions.setTodoLabelingId;
export { createTodo, listLabels, listTodos };
export default {
  labelsApi: labelsApiSlice.reducer,
  notifications: notificationsSlice.reducer,
  todosApi: todosApiSlice.reducer,
  workspace: workspaceSlice.reducer,
};
