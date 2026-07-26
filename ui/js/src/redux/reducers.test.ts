import '../__mocks__/matchMediaMock';
import fetchMock from 'fetch-mock-jest';
import {
  completeAuthentication,
  createTodo,
  flushOfflineQueue,
  listTodos,
  moveTodo,
  updateTodo,
  updateTodoLabels,
} from './reducers';
import { getTodosApi } from './todosApiSlice';
import { getWsRoot } from './fetchApi';
import { setupStore } from './store';

describe('updateTodo', function () {
  afterEach(function () {
    fetchMock.restore();
  });

  it('should make a PATCH request and dispatch actions', async function () {
    const stubTodoPatch = {
      id: 1,
      description: 'test todo',
    };
    const stubTodo = Object.assign(
      {
        completed: false,
      },
      stubTodoPatch,
    );
    fetchMock.patchOnce(`${getTodosApi()}${stubTodoPatch.id}/`, {
      body: stubTodo,
    });

    const store = setupStore({
      todosApi: {
        entries: [
          {
            id: 1,
            completed: false,
            description: 'old desc',
          },
        ],
      },
      workspace: {
        editTodoId: 1,
      },
    });
    await store.dispatch(updateTodo(stubTodoPatch));

    // Verify we show a notification
    expect(store.getState().notifications.notificationQueue.length).toEqual(1);
    expect(store.getState().notifications.notificationQueue[0]).toEqual({
      text: 'Saving Todo: test todo',
      type: 'default',
    });

    // Verify we stop editing the todo
    expect(store.getState().workspace.editTodoId).toEqual(null);

    // Verify we create a shortcut operation for the edit
    expect(store.getState().shortcuts.operations.length).toEqual(1);
    expect(store.getState().shortcuts.operations[0]).toEqual({
      type: 'EDIT_TODO',
      payload: {
        id: 1,
        description: 'test todo',
      },
      generation: 0,
    });

    // Verify the todo is updated in the entries
    expect(store.getState().todosApi.entries).toEqual([
      {
        id: 1,
        completed: false,
        description: 'test todo',
      },
    ]);

    // Verify we make the server request
    expect(fetchMock).toBeDone();
  });

  it('should show label picker when completing unlabeled todo', async function () {
    const stubTodo = {
      id: 1,
      description: 'unlabeled todo',
      completed: false,
      labels: [],
    };
    fetchMock.patchOnce(`${getTodosApi()}${stubTodo.id}/`, {
      body: { ...stubTodo, completed: true },
    });

    const store = setupStore({
      todosApi: {
        entries: [stubTodo],
      },
      workspace: {
        labelTodoId: null,
      },
    });
    await store.dispatch(updateTodo({ id: 1, completed: true }));

    // Verify label picker is shown
    expect(store.getState().workspace.labelTodoId).toEqual(1);
  });

  it('should NOT show label picker when completing labeled todo', async function () {
    const stubTodo = {
      id: 1,
      description: 'labeled todo',
      completed: false,
      labels: ['work'],
    };
    fetchMock.patchOnce(`${getTodosApi()}${stubTodo.id}/`, {
      body: { ...stubTodo, completed: true },
    });

    const store = setupStore({
      todosApi: {
        entries: [stubTodo],
      },
      workspace: {
        labelTodoId: null,
      },
    });
    await store.dispatch(updateTodo({ id: 1, completed: true }));

    // Verify label picker is NOT shown
    expect(store.getState().workspace.labelTodoId).toEqual(null);
  });

  it('should NOT show label picker when uncompleting todo', async function () {
    const stubTodo = {
      id: 1,
      description: 'completed todo',
      completed: true,
      labels: [],
    };
    fetchMock.patchOnce(`${getTodosApi()}${stubTodo.id}/`, {
      body: { ...stubTodo, completed: false },
    });

    const store = setupStore({
      todosApi: {
        entries: [stubTodo],
      },
      workspace: {
        labelTodoId: null,
      },
    });
    await store.dispatch(updateTodo({ id: 1, completed: false }));

    // Verify label picker is NOT shown
    expect(store.getState().workspace.labelTodoId).toEqual(null);
  });

  it('should NOT show label picker when editing an already-completed todo', async function () {
    const stubTodo = {
      id: 1,
      description: 'already completed',
      completed: true,
      labels: [],
    };
    fetchMock.patchOnce(`${getTodosApi()}${stubTodo.id}/`, {
      body: stubTodo,
    });

    const store = setupStore({
      todosApi: {
        entries: [stubTodo],
      },
      workspace: {
        labelTodoId: null,
      },
    });
    await store.dispatch(
      updateTodo({
        id: 1,
        description: 'it was already completed',
        completed: true,
      }),
    );

    // Verify label picker is NOT shown
    expect(store.getState().workspace.labelTodoId).toEqual(null);
  });
});

describe('updateTodoLabels', function () {
  afterEach(function () {
    fetchMock.restore();
  });

  it('should make a PATCH request and dispatch actions', async function () {
    const todoId = 1;
    const newLabels = ['new', 'labels'];
    const payload = {
      id: todoId,
      labels: newLabels,
    };
    fetchMock.patchOnce(`${getTodosApi()}${todoId}/`, {
      body: payload,
    });

    const store = setupStore({
      todosApi: {
        entries: [
          {
            id: todoId,
            description: 'test todo',
            labels: newLabels,
          },
        ],
      },
      workspace: {
        labelTodoId: todoId,
      },
    });
    await store.dispatch(updateTodoLabels(newLabels));

    // Verify the todo is updated in the entries
    expect(store.getState().todosApi.entries).toEqual([
      {
        id: todoId,
        description: 'test todo',
        labels: newLabels,
      },
    ]);

    // Verify we make the server request
    expect(fetchMock).toBeDone();
  });

  it('should queue a label notification with todo description', async function () {
    const todoId = 1;
    const newLabels = ['new', 'labels'];
    fetchMock.patchOnce(`${getTodosApi()}${todoId}/`, {
      body: { id: todoId, labels: newLabels },
    });

    const store = setupStore({
      todosApi: {
        entries: [
          {
            id: todoId,
            description: 'test todo',
            labels: [],
          },
        ],
      },
      workspace: {
        labelTodoId: todoId,
      },
    });
    await store.dispatch(updateTodoLabels(newLabels));

    expect(store.getState().notifications.notificationQueue[0]).toEqual({
      text: 'Labeling Todo: test todo',
      type: 'label',
    });
  });

  it('should error if no Todo is being labeled', async function () {
    expect.assertions(1);

    const store = setupStore({
      workspace: {
        labelTodoId: null,
      },
    });
    await expect(
      async () => await store.dispatch(updateTodoLabels([])),
    ).rejects.toThrow('Unable to edit a todo w/ null ID');
  });
});

describe('completeAuthentication', function () {
  it('should make a request to auth_callback with the auth token', async function () {
    const token = 'token';

    fetchMock.getOnce(`${getWsRoot()}api/todos/auth_callback/?code=${token}`, {
      body: 'Logged In!',
      status: 200,
      headers: {
        'set-cookie':
          'csrftoken=sampleCSRFToken; Max-Age=31449600; Path=/; SameSite=Lax',
      },
    });

    const store = setupStore();
    await store.dispatch(completeAuthentication(token));

    // Verify the login info is stored
    expect(store.getState().workspace.loggedIn).toEqual(true);
    expect(store.getState().workspace.csrfToken).toEqual('sampleCSRFToken');

    // Verify we make the server request
    expect(fetchMock).toBeDone();
  });
});

describe('listTodos', function () {
  afterEach(function () {
    fetchMock.restore();
  });

  it('should make a GET request and dispatch actions', async function () {
    const response = [
      {
        description: 'todo1',
      },
      {
        description: 'todo2',
      },
    ];
    fetchMock.getOnce(`${getTodosApi()}`, response);

    const store = setupStore({
      shortcuts: {
        latestGeneration: 0,
        operations: [
          {
            type: 'EDIT_TODO',
            payload: { id: 1, description: 'old desc' },
            generation: 0,
          },
        ],
      },
    });
    await store.dispatch(listTodos());

    // Verify we increment the shortcut generation
    expect(store.getState().shortcuts.latestGeneration).toEqual(1);

    // Verify the todo entries are updated
    expect(store.getState().todosApi.entries).toEqual(response);

    // Verify older shortcuts are cleared
    expect(store.getState().shortcuts.operations.length).toEqual(0);

    // Verify we made the server request
    expect(fetchMock).toBeDone();
  });
});

describe('moveTodo', function () {
  afterEach(function () {
    fetchMock.restore();
  });

  it('should make a move request and dispatch actions', async function () {
    const moveOperation = {
      position: 'after',
      relative_id: 2,
      todo_id: 1,
    };
    fetchMock.postOnce(`${getTodosApi()}${moveOperation.todo_id}/reorder/`, {
      id: 1,
    });

    const store = setupStore({
      workspace: {},
      todosApi: {
        entries: [
          {
            id: 1,
            description: 'moving todo',
          },
          {
            id: 2,
          },
        ],
      },
    });
    await store.dispatch(moveTodo(moveOperation));

    // Verify we show a notification
    expect(store.getState().notifications.notificationQueue.length).toEqual(1);
    expect(store.getState().notifications.notificationQueue[0]).toEqual({
      text: 'Reordering Todo: moving todo',
      type: 'default',
    });

    // Verify we create a shortcut operation for the move
    expect(store.getState().shortcuts.operations.length).toEqual(1);
    expect(store.getState().shortcuts.operations[0]).toEqual({
      type: 'MOVE_TODO',
      payload: moveOperation,
      generation: 0,
    });

    // Verify we make the server request
    expect(fetchMock).toBeDone();
  });
});

describe('createTodo', function () {
  afterEach(function () {
    fetchMock.restore();
  });

  it('should enqueue a create op when API rejected with TypeError', async function () {
    fetchMock.postOnce(getTodosApi(), {
      throws: new TypeError('Network error'),
    });

    const store = setupStore();
    await store.dispatch(createTodo('new todo'));

    expect(store.getState().offlineQueue.pendingOps).toEqual([
      { type: 'create', payload: { description: 'new todo', labels: [] } },
    ]);
  });

  it('should NOT enqueue when API rejected with non-TypeError (HTTP error)', async function () {
    fetchMock.postOnce(getTodosApi(), { status: 500 });

    const store = setupStore();
    await store.dispatch(createTodo('new todo'));

    expect(store.getState().offlineQueue.pendingOps).toEqual([]);
  });

  it('should NOT enqueue on success', async function () {
    fetchMock.postOnce(getTodosApi(), {
      body: { id: 99, description: 'new todo', labels: [] },
    });

    const store = setupStore();
    await store.dispatch(createTodo('new todo'));

    expect(store.getState().offlineQueue.pendingOps).toEqual([]);
  });
});

describe('updateTodo offline enqueue', function () {
  afterEach(function () {
    fetchMock.restore();
  });

  it('should enqueue update op on TypeError rejection even when isOnline is true', async function () {
    fetchMock.patchOnce(`${getTodosApi()}1/`, {
      throws: new TypeError('Network error'),
    });

    const store = setupStore({
      network: { isOnline: true, consecutiveNetworkFailures: 0 },
      todosApi: {
        entries: [{ id: 1, description: 'test', completed: false }],
      },
    });
    await store.dispatch(updateTodo({ id: 1, description: 'updated' }));

    expect(store.getState().offlineQueue.pendingOps).toEqual([
      { type: 'update', payload: { id: 1, description: 'updated' } },
    ]);
  });

  it('should NOT enqueue update op on non-TypeError rejection', async function () {
    fetchMock.patchOnce(`${getTodosApi()}1/`, { status: 500 });

    const store = setupStore({
      todosApi: {
        entries: [{ id: 1, description: 'test', completed: false }],
      },
    });
    await store.dispatch(updateTodo({ id: 1, description: 'updated' }));

    expect(store.getState().offlineQueue.pendingOps).toEqual([]);
  });
});

describe('moveTodo offline enqueue', function () {
  afterEach(function () {
    fetchMock.restore();
  });

  it('should enqueue move op on TypeError rejection even when isOnline is true', async function () {
    const moveOperation = {
      position: 'after' as const,
      relative_id: 2,
      todo_id: 1,
    };
    fetchMock.postOnce(`${getTodosApi()}1/reorder/`, {
      throws: new TypeError('Network error'),
    });

    const store = setupStore({
      network: { isOnline: true, consecutiveNetworkFailures: 0 },
      todosApi: {
        entries: [{ id: 1, description: 'test' }, { id: 2 }],
      },
    });
    await store.dispatch(moveTodo(moveOperation));

    expect(store.getState().offlineQueue.pendingOps).toEqual([
      { type: 'move', payload: moveOperation },
    ]);
  });

  it('should NOT enqueue move op on non-TypeError rejection', async function () {
    const moveOperation = {
      position: 'after' as const,
      relative_id: 2,
      todo_id: 1,
    };
    fetchMock.postOnce(`${getTodosApi()}1/reorder/`, { status: 500 });

    const store = setupStore({
      todosApi: {
        entries: [{ id: 1, description: 'test' }, { id: 2 }],
      },
    });
    await store.dispatch(moveTodo(moveOperation));

    expect(store.getState().offlineQueue.pendingOps).toEqual([]);
  });
});

describe('flushOfflineQueue', function () {
  afterEach(function () {
    fetchMock.restore();
  });

  it('should return early and not show notification when queue is empty', async function () {
    const store = setupStore();
    await store.dispatch(flushOfflineQueue());

    expect(store.getState().notifications.notificationQueue).toEqual([]);
  });

  it('should process update ops and show success notification', async function () {
    fetchMock.patchOnce(`${getTodosApi()}1/`, {
      body: { id: 1, description: 'updated' },
    });
    fetchMock.getOnce(getTodosApi(), { body: [] });

    const store = setupStore({
      offlineQueue: {
        pendingOps: [
          { type: 'update', payload: { id: 1, description: 'updated' } },
        ],
      },
      todosApi: {
        entries: [{ id: 1, description: 'old' }],
        pendingCreates: [],
        pendingArchives: [],
      },
    });
    await store.dispatch(flushOfflineQueue());

    expect(store.getState().offlineQueue.pendingOps).toEqual([]);
    const notification = store.getState().notifications.notificationQueue[0];
    expect(notification).toEqual({ text: 'Changes synced', type: 'default' });
    expect(fetchMock).toBeDone();
  });

  it('should re-enqueue failed ops and show failure notification', async function () {
    fetchMock.patchOnce(`${getTodosApi()}1/`, {
      throws: new TypeError('Network error'),
    });
    fetchMock.getOnce(getTodosApi(), { body: [] });

    const failedOp = {
      type: 'update' as const,
      payload: { id: 1, description: 'updated' },
    };
    const store = setupStore({
      offlineQueue: { pendingOps: [failedOp] },
      todosApi: {
        entries: [{ id: 1, description: 'old' }],
        pendingCreates: [],
        pendingArchives: [],
      },
    });
    await store.dispatch(flushOfflineQueue());

    expect(store.getState().offlineQueue.pendingOps).toEqual([failedOp]);
    const notification = store.getState().notifications.notificationQueue[0];
    expect(notification).toEqual({
      text: 'Some changes could not be synced',
      type: 'default',
    });
  });

  it('should process ops in FIFO order', async function () {
    const callOrder: string[] = [];
    fetchMock.patch(`${getTodosApi()}1/`, () => {
      callOrder.push('update-1');
      return { body: { id: 1 } };
    });
    fetchMock.patch(`${getTodosApi()}2/`, () => {
      callOrder.push('update-2');
      return { body: { id: 2 } };
    });
    fetchMock.getOnce(getTodosApi(), { body: [] });

    const store = setupStore({
      offlineQueue: {
        pendingOps: [
          { type: 'update', payload: { id: 1, description: 'first' } },
          { type: 'update', payload: { id: 2, description: 'second' } },
        ],
      },
      todosApi: {
        entries: [
          { id: 1, description: 'a' },
          { id: 2, description: 'b' },
        ],
        pendingCreates: [],
        pendingArchives: [],
      },
    });
    await store.dispatch(flushOfflineQueue());

    expect(callOrder).toEqual(['update-1', 'update-2']);
  });

  it('should call listTodos after flush', async function () {
    fetchMock.patchOnce(`${getTodosApi()}1/`, {
      body: { id: 1, description: 'ok' },
    });
    fetchMock.getOnce(getTodosApi(), { body: [{ id: 1, description: 'ok' }] });

    const store = setupStore({
      offlineQueue: {
        pendingOps: [{ type: 'update', payload: { id: 1, description: 'ok' } }],
      },
      todosApi: {
        entries: [{ id: 1, description: 'old' }],
        pendingCreates: [],
        pendingArchives: [],
      },
    });
    await store.dispatch(flushOfflineQueue());

    expect(fetchMock).toBeDone();
  });
});

export {};
