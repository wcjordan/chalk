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
      const response = await completeAuthCallback(accessToken);
      const cookies = response.headers.get('set-cookie')?.split(' ');
      const csrfToken = cookies
        ?.find((val) => val.startsWith('csrftoken'))
        ?.slice(10, -1);

      if (response.status !== 200) {
        const responseText = await response.text();
        const message = `Login failed with status: ${response.status} ${response.statusText}\n${responseText}`;
        dispatch(notificationsSlice.actions.addNotification(message));
        throw new Error(message);
      }

      if (!csrfToken) {
        dispatch(
          notificationsSlice.actions.addNotification(
            'Unexpectedly missing CSRFToken.  Please refresh and login again.',
          ),
        );
        throw new Error(
          `CSRFToken missing from set-cookie header\n${response.headers.get(
            'set-cookie',
          )}`,
        );
      }

      dispatch(
        workspaceSlice.actions.logIn({
          loggedIn: true,
          csrfToken: csrfToken,
        }),
      );
    } catch (ex) {
      dispatch(
        notificationsSlice.actions.addNotification(
          'Login failed with a network error.  Please refresh and login again.',
        ),
      );
      throw ex;
    }
  };

export const addNotification = notificationsSlice.actions.addNotification;
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
