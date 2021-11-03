import '../__mocks__/matchMediaMock';
import configureMockStore from 'redux-mock-store';
import fetchMock from 'fetch-mock-jest';
import thunk from 'redux-thunk';
import reducers, { updateTodo } from './reducers';
import { getTodosApi } from './todosApiSlice';

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

    const store = mockStore();
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

describe('workspace reducer', function () {
  it('should return the initial state', function () {
    expect(reducers.workspace(undefined, {})).toEqual({
      editId: null,
      filterLabels: [],
      labelTodoId: null,
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
