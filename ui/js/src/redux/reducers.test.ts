import '../__mocks__/matchMediaMock';
import configureMockStore from 'redux-mock-store';
import fetchMock from 'fetch-mock-jest';
import thunk from 'redux-thunk';
import {
  completeAuthentication,
  listTodos,
  moveTodo,
  updateTodo,
  updateTodoLabels,
} from './reducers';
import { getTodosApi } from './todosApiSlice';
import { getWsRoot } from './fetchApi';

const mockStore = configureMockStore([thunk]);

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

    const store = mockStore({ workspace: {} });
    await store.dispatch(updateTodo(stubTodoPatch));

    const actions = store.getActions();
    expect(actions.length).toEqual(5);

    // Verify we show a notification
    expect(actions[0]).toEqual({
      payload: 'Saving Todo: test todo',
      type: 'notifications/addNotification',
    });

    // Verify we stop editing the todo
    expect(actions[1]).toEqual({
      payload: null,
      type: 'workspace/setEditTodoId',
    });

    // Verify we create a shortcut operation for the edit
    expect(actions[2]).toEqual({
      payload: stubTodoPatch,
      type: 'shortcuts/addEditTodoOperation',
    });

    // Verify the pending handler is called based on the patch argument
    const pendingAction = actions[3];
    expect(pendingAction.meta.arg).toEqual(stubTodoPatch);
    expect(pendingAction.type).toEqual('todosApi/update/pending');

    // Verify the fulfilled handler is called with the returned todo
    const fulfilledAction = actions[4];
    expect(fulfilledAction.meta.arg).toEqual(stubTodoPatch);
    expect(fulfilledAction.payload).toEqual(stubTodo);
    expect(fulfilledAction.type).toEqual('todosApi/update/fulfilled');

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

    const store = mockStore({
      workspace: {
        labelTodoId: todoId,
      },
    });
    await store.dispatch(updateTodoLabels(newLabels));

    const actions = store.getActions();
    expect(actions.length).toEqual(2);

    // Verify the pending handler is called based on the patch argument
    const pendingAction = actions[0];
    expect(pendingAction.meta.arg).toEqual(payload);
    expect(pendingAction.type).toEqual('todosApi/update/pending');

    // Verify the fulfilled handler is called with the returned todo
    const fulfilledAction = actions[1];
    expect(fulfilledAction.meta.arg).toEqual(payload);
    expect(fulfilledAction.payload).toEqual(payload);
    expect(fulfilledAction.type).toEqual('todosApi/update/fulfilled');

    // Verify we make the server request
    expect(fetchMock).toBeDone();
  });

  it('should error if no Todo is being labeled', async function () {
    expect.assertions(1);

    const store = mockStore({
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
          'csrftoken=CSRFToken; Max-Age=31449600; Path=/; SameSite=Lax',
      },
    });

    const store = mockStore();
    await store.dispatch(completeAuthentication(token));

    const actions = store.getActions();
    expect(actions.length).toEqual(1);

    // Verify the pending handler is called based on the patch argument
    const pendingAction = actions[0];
    expect(pendingAction.type).toEqual('workspace/logIn');
    expect(pendingAction.payload).toEqual({
      loggedIn: true,
      csrfToken: 'CSRFToken',
    });

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

    const store = mockStore({
      shortcuts: {
        latestGeneration: 0,
      },
      todosApi: {
        loading: false,
      },
    });
    await store.dispatch(listTodos());

    const actions = store.getActions();
    expect(actions.length).toEqual(4);

    // Verify we increment the shortcut generation
    expect(actions[0]).toEqual({
      payload: undefined,
      type: 'shortcuts/incrementGenerations',
    });

    // Verify the pending handler is called
    const pendingAction = actions[1];
    expect(pendingAction.type).toEqual('todosApi/list/pending');

    // Verify the fulfilled handler is called
    const fulfilledAction = actions[2];
    expect(fulfilledAction.type).toEqual('todosApi/list/fulfilled');
    expect(fulfilledAction.payload).toEqual(response);

    expect(actions[3]).toEqual({
      payload: 0,
      type: 'shortcuts/clearOperationsUpThroughGeneration',
    });

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

    const store = mockStore({
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
      workspace: {},
    });
    await store.dispatch(moveTodo(moveOperation));

    const actions = store.getActions();
    expect(actions.length).toEqual(4);

    // Verify we show a notification
    expect(actions[0]).toEqual({
      payload: 'Reordering Todo: moving todo',
      type: 'notifications/addNotification',
    });

    // Verify we create a shortcut operation for the move
    expect(actions[1]).toEqual({
      payload: moveOperation,
      type: 'shortcuts/addMoveTodoOperation',
    });

    // Verify the pending handler is called with the operation
    const pendingAction = actions[2];
    expect(pendingAction.meta.arg).toEqual(moveOperation);
    expect(pendingAction.type).toEqual('todosApi/move/pending');

    // Verify the fulfilled handler is called
    const fulfilledAction = actions[3];
    expect(fulfilledAction.meta.arg).toEqual(moveOperation);
    expect(fulfilledAction.type).toEqual('todosApi/move/fulfilled');

    // Verify we make the server request
    expect(fetchMock).toBeDone();
  });
});

export {};
