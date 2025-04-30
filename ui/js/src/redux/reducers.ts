import { ThunkAction } from 'redux-thunk';
import { Action } from '@reduxjs/toolkit';

import { MoveTodoOperation, TodoPatch } from './types';
import labelsApiSlice, { listLabels } from './labelsApiSlice';
import notificationsSlice from './notificationsSlice';
import shortcutSlice from './shortcutSlice';
import { RootState } from './store';
import todosApiSlice, {
  createTodo,
  listTodos as listTodosApi,
  moveTodo as moveTodoApi,
  updateTodo as updateTodoApi,
} from './todosApiSlice';
import workspaceSlice from './workspaceSlice';
import { completeAuthCallback, getCsrfToken, recordSessionData } from './fetchApi';
import { getEnvFlags } from '../helpers';

type AppThunk = ThunkAction<void, RootState, unknown, Action<string>>;

export const updateTodo =
  (todoPatch: TodoPatch): AppThunk =>
  (dispatch) => {
    return Promise.all([
      dispatch(
        notificationsSlice.actions.addNotification(
          `Saving Todo: ${todoPatch.description}`,
        ),
      ),
      dispatch(workspaceSlice.actions.setEditTodoId(null)),
      dispatch(shortcutSlice.actions.addEditTodoOperation(todoPatch)),
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

export const moveTodo =
  (operation: MoveTodoOperation): AppThunk =>
  (dispatch, getState) => {
    const todo = getState().todosApi.entries.find(
      (todo) => todo.id === operation.todo_id,
    );
    return Promise.all([
      dispatch(
        notificationsSlice.actions.addNotification(
          `Reordering Todo: ${todo?.description}`,
        ),
      ),
      dispatch(shortcutSlice.actions.addMoveTodoOperation(operation)),
      dispatch(moveTodoApi(operation)),
    ]);
  };

export const listTodos = (): AppThunk => async (dispatch, getState) => {
  const latestGeneration = getState().shortcuts.latestGeneration;
  await Promise.all([
    dispatch(shortcutSlice.actions.incrementGenerations()),
    dispatch(listTodosApi()),
  ]);
  return dispatch(
    shortcutSlice.actions.clearOperationsUpThroughGeneration(latestGeneration),
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

export const recordSessionEvents =
  (sessionGuid: string, events: object[]): AppThunk =>
  async (_, getState) => {
    if (events.length === 0) {
      return;
    }

    // send events to the backend
    const data = JSON.stringify({
      session_guid: sessionGuid,
      session_data: events,
      environment: getEnvFlags().ENVIRONMENT,
    });
    const result = recordSessionData(data, getCsrfToken(getState));
    result.then((response: string) => {
      console.error('Events saved successfully');
      console.error(response);
    }).catch((error: string) => {
      console.error('Failed to save events');
      console.error(error);
    });
  };

export const addNotification = notificationsSlice.actions.addNotification;
export const dismissNotification =
  notificationsSlice.actions.dismissNotification;
export const setEditTodoId = workspaceSlice.actions.setEditTodoId;
export const setLabelTodoId = workspaceSlice.actions.setLabelTodoId;
export const setWorkContext = workspaceSlice.actions.setWorkContext;
export const toggleLabel = workspaceSlice.actions.toggleLabel;
export const toggleShowCompletedTodos =
  workspaceSlice.actions.toggleShowCompletedTodos;
export const toggleShowLabelFilter =
  workspaceSlice.actions.toggleShowLabelFilter;
export { createTodo, listLabels };
export default {
  labelsApi: labelsApiSlice.reducer,
  notifications: notificationsSlice.reducer,
  shortcuts: shortcutSlice.reducer,
  todosApi: todosApiSlice.reducer,
  workspace: workspaceSlice.reducer,
};
