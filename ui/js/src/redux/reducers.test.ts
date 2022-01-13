import '../__mocks__/matchMediaMock';
import configureMockStore from 'redux-mock-store';
import fetchMock from 'fetch-mock-jest';
import thunk from 'redux-thunk';
import reducers, {
  completeAuthentication,
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
    expect(actions.length).toEqual(3);

    // Verify we stop editing the todo
    expect(actions[0]).toEqual({
      payload: null,
      type: 'workspace/setTodoEditId',
    });

    // Verify the pending handler is called based on the patch argument
    const pendingAction = actions[1];
    expect(pendingAction.meta.arg).toEqual(stubTodoPatch);
    expect(pendingAction.type).toEqual('todosApi/update/pending');

    // Verify the fulfilled handler is called with the returned todo
    const fulfilledAction = actions[2];
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

describe('workspace reducer', function () {
  it('should return the initial state', function () {
    expect(reducers.workspace(undefined, {})).toEqual({
      csrfToken: null,
      editId: null,
      filterLabels: [],
      labelTodoId: null,
      loggedIn: false,
    });
  });

  describe('workspace/filterByLabels', function () {
    it('should update the filterLabels', function () {
      const result = reducers.workspace(
        {
          filterLabels: ['old'],
        },
        {
          type: 'workspace/filterByLabels',
          payload: ['new', 'otherNew'],
        },
      );
      expect(result).toEqual({
        filterLabels: ['new', 'otherNew'],
      });
    });
  });

  describe('workspace/setTodoLabelingId', function () {
    it('should update the labeling id', function () {
      const result = reducers.workspace(
        {
          labelTodoId: 1,
        },
        {
          type: 'workspace/setTodoLabelingId',
          payload: 2,
        },
      );
      expect(result).toEqual({
        labelTodoId: 2,
      });
    });

    it('should support cancelling a labeling', function () {
      const result = reducers.workspace(
        {
          labelTodoId: 1,
        },
        {
          type: 'workspace/setTodoLabelingId',
          payload: null,
        },
      );
      expect(result).toEqual({
        labelTodoId: null,
      });
    });
  });

  describe('workspace/setTodoEditId', function () {
    it('should update the edit id', function () {
      const result = reducers.workspace(
        {
          editId: 1,
        },
        {
          type: 'workspace/setTodoEditId',
          payload: 2,
        },
      );
      expect(result).toEqual({
        editId: 2,
      });
    });

    it('should support cancelling an edit', function () {
      const result = reducers.workspace(
        {
          editId: 1,
        },
        {
          type: 'workspace/setTodoEditId',
          payload: null,
        },
      );
      expect(result).toEqual({
        editId: null,
      });
    });
  });
});

export {};
