import { ThunkAction } from 'redux-thunk';
import { Action, Reducer } from '@reduxjs/toolkit';
import { persistReducer } from 'redux-persist';

import { getEnvFlags } from '../helpers';
import { selectActiveFilterLabels } from '../selectors';
import {
  completeAuthCallback,
  getCsrfToken,
  recordSessionData,
} from './fetchApi';
import { labelsApiSlice, listLabels } from './labelsApiSlice';
import networkSlice from './networkSlice';
import notificationsSlice from './notificationsSlice';
import offlineQueueSlice from './offlineQueueSlice';
import shortcutSlice from './shortcutSlice';
import { RootState } from './store';
import {
  createTodo as createTodoApi,
  listTodos as listTodosApi,
  moveTodo as moveTodoApi,
  todosApiSlice,
  updateTodo as updateTodoApi,
} from './todosApiSlice';
import { MoveTodoOperation, OfflineOperation, TodoPatch } from './types';
import { workspaceSlice } from './workspaceSlice';

type AppThunk = ThunkAction<void, RootState, unknown, Action<string>>;

// Negative, monotonically-decrementing IDs for optimistic create placeholders,
// distinguishing them from real (positive) server-assigned todo IDs.
let nextTempTodoId = -1;

export const updateTodo =
  (todoPatch: TodoPatch): AppThunk =>
  async (dispatch, getState) => {
    // Check if we should auto-show label picker
    const todo = getState().todosApi.entries.find((t) => t.id === todoPatch.id);
    const wasAlreadyCompleted = todo?.completed === true;
    const hasNoLabels = (todo?.labels?.length ?? 0) === 0;

    const shouldShowLabelPicker =
      todoPatch.completed === true && // Marking as complete
      !wasAlreadyCompleted && // Wasn't already complete
      hasNoLabels; // Has no labels

    dispatch(
      notificationsSlice.actions.addNotification({
        text: `Saving Todo: ${todoPatch.description ?? todo?.description}`,
        type: 'default',
      }),
    );
    dispatch(workspaceSlice.actions.setEditTodoId(null));
    dispatch(shortcutSlice.actions.addEditTodoOperation(todoPatch));

    // Show label picker for unlabeled completed todos
    if (shouldShowLabelPicker) {
      dispatch(workspaceSlice.actions.setLabelTodoId(todoPatch.id));
    }

    const result = await dispatch(updateTodoApi(todoPatch));
    if (
      updateTodoApi.rejected.match(result) &&
      result.error.name === 'TypeError'
    ) {
      dispatch(
        offlineQueueSlice.actions.enqueueOp({
          type: 'update',
          payload: todoPatch,
        }),
      );
    }
  };

export const updateTodoLabels =
  (labels: string[]): AppThunk =>
  (dispatch, getState) => {
    const todoId = getState().workspace.labelTodoId;
    if (todoId === null) {
      throw new Error('Unable to edit a todo w/ null ID');
    }

    const todo = getState().todosApi.entries.find((t) => t.id === todoId);
    dispatch(
      notificationsSlice.actions.addNotification({
        text: `Labeling Todo: ${todo?.description}`,
        type: 'label',
      }),
    );

    return dispatch(
      updateTodoApi({
        id: todoId,
        labels,
      }),
    );
  };

export const moveTodo =
  (operation: MoveTodoOperation): AppThunk =>
  async (dispatch, getState) => {
    const todo = getState().todosApi.entries.find(
      (todo) => todo.id === operation.todo_id,
    );
    dispatch(
      notificationsSlice.actions.addNotification({
        text: `Reordering Todo: ${todo?.description}`,
        type: 'default',
      }),
    );
    dispatch(shortcutSlice.actions.addMoveTodoOperation(operation));

    const result = await dispatch(moveTodoApi(operation));
    if (
      moveTodoApi.rejected.match(result) &&
      result.error.name === 'TypeError'
    ) {
      dispatch(
        offlineQueueSlice.actions.enqueueOp({
          type: 'move',
          payload: operation,
        }),
      );
    }
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
        dispatch(
          notificationsSlice.actions.addNotification({
            text: message,
            type: 'default',
          }),
        );
        throw new Error(message);
      }

      if (!csrfToken) {
        dispatch(
          notificationsSlice.actions.addNotification({
            text: 'Unexpectedly missing CSRFToken.  Please refresh and login again.',
            type: 'default',
          }),
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
        notificationsSlice.actions.addNotification({
          text: 'Login failed with a network error.  Please refresh and login again.',
          type: 'default',
        }),
      );
      throw ex;
    }
  };

export const recordSessionEvents =
  (sessionGuid: string, events: object[]): AppThunk =>
  async (dispatch, getState) => {
    if (events.length === 0) {
      return;
    }

    // send events to the backend
    const data = JSON.stringify({
      session_guid: sessionGuid,
      session_data: events,
      environment: getEnvFlags().ENVIRONMENT,
    });

    try {
      await recordSessionData(data, getCsrfToken(getState));
    } catch (error) {
      console.error('Failed to save events', error);
      // Only notify in development to avoid user-facing errors
      if (getEnvFlags().ENVIRONMENT === 'DEV') {
        dispatch(
          notificationsSlice.actions.addNotification({
            text: 'Failed to record session data',
            type: 'default',
          }),
        );
      }
    }
  };

export const createTodo =
  (todoTitle: string): AppThunk =>
  async (dispatch, getState) => {
    const activeLabels = selectActiveFilterLabels(getState());
    dispatch(
      shortcutSlice.actions.addCreateTodoOperation({
        tempId: nextTempTodoId--,
        description: todoTitle,
        labels: activeLabels,
      }),
    );
    const result = await dispatch(createTodoApi(todoTitle));
    if (
      createTodoApi.rejected.match(result) &&
      result.error.name === 'TypeError'
    ) {
      dispatch(
        offlineQueueSlice.actions.enqueueOp({
          type: 'create',
          payload: { description: todoTitle, labels: activeLabels },
        }),
      );
    }
  };

export const flushOfflineQueue = (): AppThunk => async (dispatch, getState) => {
  const pendingOps = getState().offlineQueue.pendingOps;
  if (pendingOps.length === 0) {
    return;
  }

  dispatch(offlineQueueSlice.actions.clearQueue());

  const failedOps: OfflineOperation[] = [];
  for (const op of pendingOps) {
    let result;
    if (op.type === 'create') {
      result = await dispatch(createTodoApi(op.payload.description));
      if (createTodoApi.rejected.match(result)) {
        failedOps.push(op);
      }
    } else if (op.type === 'update') {
      result = await dispatch(updateTodoApi(op.payload));
      if (updateTodoApi.rejected.match(result)) {
        failedOps.push(op);
      }
    } else if (op.type === 'move') {
      result = await dispatch(moveTodoApi(op.payload));
      if (moveTodoApi.rejected.match(result)) {
        failedOps.push(op);
      }
    }
  }

  for (const op of failedOps) {
    dispatch(offlineQueueSlice.actions.enqueueOp(op));
  }

  await dispatch(listTodosApi());

  if (failedOps.length === 0) {
    dispatch(
      notificationsSlice.actions.addNotification({
        text: 'Changes synced',
        type: 'default',
      }),
    );
  } else {
    dispatch(
      notificationsSlice.actions.addNotification({
        text: 'Some changes could not be synced',
        type: 'default',
      }),
    );
  }
};

export const addNotification = notificationsSlice.actions.addNotification;
export const dismissNotification =
  notificationsSlice.actions.dismissNotification;
export const setEditTodoId = workspaceSlice.actions.setEditTodoId;
export const setLabelTodoId = workspaceSlice.actions.setLabelTodoId;
export const setSnoozeTodoId = workspaceSlice.actions.setSnoozeTodoId;
export const setWorkContext = workspaceSlice.actions.setWorkContext;
export const setFilters = workspaceSlice.actions.setFilters;
export const toggleLabel = workspaceSlice.actions.toggleLabel;
export const toggleShowCompletedTodos =
  workspaceSlice.actions.toggleShowCompletedTodos;
export const toggleShowLabelFilter =
  workspaceSlice.actions.toggleShowLabelFilter;
export { listLabels };

function makePersistReducer<S, A extends Action>(
  key: string,
  reducer: Reducer<S, A>,
  blacklist: string[] = [],
): Reducer<S, A> {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const storage = require('./persistStorage').default;
  // persistReducer returns a compatible reducer type
  return persistReducer(
    { key, storage, blacklist },
    reducer,
  ) as unknown as Reducer<S, A>;
}

const offlineQueueReducer =
  process.env.NODE_ENV !== 'test'
    ? makePersistReducer('offlineQueue', offlineQueueSlice.reducer)
    : offlineQueueSlice.reducer;

const todosApiReducer =
  process.env.NODE_ENV !== 'test'
    ? makePersistReducer('todosApi', todosApiSlice.reducer, [
        'loading',
        'initialLoad',
      ])
    : todosApiSlice.reducer;

export const rootReducerConfig = {
  labelsApi: labelsApiSlice.reducer,
  network: networkSlice.reducer,
  notifications: notificationsSlice.reducer,
  offlineQueue: offlineQueueReducer,
  shortcuts: shortcutSlice.reducer,
  todosApi: todosApiReducer,
  workspace: workspaceSlice.reducer,
};
