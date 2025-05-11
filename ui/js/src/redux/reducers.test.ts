import '../__mocks__/matchMediaMock';
import fetchMock from 'fetch-mock-jest';
import {
  completeAuthentication,
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
    expect(store.getState().notifications.notificationQueue[0]).toEqual(
      'Saving Todo: test todo',
    );

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
    expect(store.getState().notifications.notificationQueue[0]).toEqual(
      'Reordering Todo: moving todo',
    );

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

export {};
