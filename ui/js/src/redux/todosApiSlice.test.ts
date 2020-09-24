import configureMockStore from 'redux-mock-store';
import fetchMock from 'fetch-mock-jest';
import thunk from 'redux-thunk';
import todosApiSlice, { createTodo, listTodos } from './todosApiSlice';

// NOTE (jordan) updateTodo tested in reducers.test.ts
const mockStore = configureMockStore([thunk]);

describe('createTodo', function() {
  afterEach(function() {
    fetchMock.restore();
  });

  it('should make a POST request and dispatch actions', async function() {
    const stubDescription = 'test todo';
    const stubTodo = getStubTodo({ description: stubDescription });
    fetchMock.postOnce('/api/todos/todos/', {
      body: stubTodo,
    });

    const store = mockStore();
    await store.dispatch(createTodo(stubDescription));

    const actions = store.getActions();
    expect(actions.length).toEqual(2);

    // Verify the pending handler is called based on the patch argument
    const pendingAction = actions[0];
    expect(pendingAction.meta.arg).toEqual(stubDescription);
    expect(pendingAction.type).toEqual('todosApi/create/pending');

    // Verify the fulfilled handler is called with the returned todo
    const fulfilledAction = actions[1];
    expect(fulfilledAction.meta.arg).toEqual(stubDescription);
    expect(fulfilledAction.payload).toEqual(stubTodo);
    expect(fulfilledAction.type).toEqual('todosApi/create/fulfilled');

    // Verify we make the server request
    expect(fetchMock).toBeDone();
  });
});

describe('listTodos', function() {
  afterEach(function() {
    fetchMock.restore();
  });

  it('should make a GET request and dispatch actions', async function() {
    const stubTodos = [
      getStubTodo({ id: 1, description: 'todo 1' }),
      getStubTodo({ id: 2, description: 'todo 2' }),
    ];
    fetchMock.getOnce('/api/todos/todos/', {
      body: stubTodos,
    });

    const store = mockStore({ todosApi: { loading: false } });
    await store.dispatch(listTodos());

    const actions = store.getActions();
    expect(actions.length).toEqual(2);

    // Verify the pending handler is called based on the patch argument
    const pendingAction = actions[0];
    expect(pendingAction.type).toEqual('todosApi/list/pending');

    // Verify the fulfilled handler is called with the returned todo
    const fulfilledAction = actions[1];
    expect(fulfilledAction.payload).toEqual(stubTodos);
    expect(fulfilledAction.type).toEqual('todosApi/list/fulfilled');

    // Verify we make the server request
    expect(fetchMock).toBeDone();
  });

  it('should do nothing if todos are already loading', async function() {
    fetchMock.mock('*', 200);
    const store = mockStore({ todosApi: { loading: true } });
    await store.dispatch(listTodos());

    const actions = store.getActions();
    expect(actions.length).toEqual(0);

    // Verify we make the server request
    expect(fetchMock).not.toHaveFetched('*');
  });
});

describe('todosApiSlice reducer', function() {
  const initialState = {
    entries: [],
    loading: false,
  };

  it('should return the initial state', function() {
    expect(todosApiSlice.reducer(undefined, {})).toEqual(initialState);
  });

  describe('todosApi/create/fulfilled', function() {
    it('should add new todo to entries', function() {
      const result = todosApiSlice.reducer(initialState, {
        type: 'todosApi/create/fulfilled',
        payload: getStubTodo(),
      });
      expect(result).toEqual({
        entries: [getStubTodo()],
        loading: false,
      });
    });

    it('should sort todos by id with completed todos at the end', function() {
      const result = todosApiSlice.reducer(
        {
          entries: [
            getStubTodo({ id: 2 }),
            getStubTodo({ id: 1, completed: true }),
          ],
          loading: false,
        },
        {
          type: 'todosApi/create/fulfilled',
          payload: getStubTodo({ id: 3 }),
        },
      );
      expect(result).toEqual({
        entries: [
          getStubTodo({ id: 2 }),
          getStubTodo({ id: 3 }),
          getStubTodo({ id: 1, completed: true }),
        ],
        loading: false,
      });
    });

    it('should filter out archived todos', function() {
      const result = todosApiSlice.reducer(
        {
          entries: [],
          loading: false,
        },
        {
          type: 'todosApi/create/fulfilled',
          payload: getStubTodo({ id: 1, archived: true }),
        },
      );
      expect(result).toEqual({
        entries: [],
        loading: false,
      });
    });
  });

  describe('todosApi/list/pending', function() {
    it('should mark loading as in progress', function() {
      const result = todosApiSlice.reducer(initialState, {
        type: 'todosApi/list/pending',
      });
      expect(result).toEqual({
        entries: [],
        loading: true,
      });
    });
  });

  describe('todosApi/list/rejected', function() {
    let spy;

    beforeEach(function() {
      spy = jest.spyOn(console, 'warn').mockImplementation();
    });

    afterEach(function() {
      spy.mockRestore();
    });

    it('should mark loading as no longer in progress', function() {
      const result = todosApiSlice.reducer(
        {
          entries: [],
          loading: true,
        },
        {
          error: { message: 'test error' },
          type: 'todosApi/list/rejected',
        },
      );
      expect(result).toEqual({
        entries: [],
        loading: false,
      });
      expect(console.warn).toHaveBeenCalledWith(
        'Loading Todo failed. test error',
      );
    });
  });

  describe('todosApi/list/fulfilled', function() {
    it('should mark loading as no longer in progress', function() {
      const result = todosApiSlice.reducer(
        {
          entries: [],
          loading: true,
        },
        {
          type: 'todosApi/list/fulfilled',
          payload: [],
        },
      );
      expect(result).toEqual({
        entries: [],
        loading: false,
      });
    });

    it('should replace entries with loaded todos', function() {
      const result = todosApiSlice.reducer(
        {
          entries: [getStubTodo({ id: 1, description: 'overwritten' })],
          loading: true,
        },
        {
          type: 'todosApi/list/fulfilled',
          payload: [getStubTodo({ id: 2 }), getStubTodo({ id: 3 })],
        },
      );
      expect(result).toEqual({
        entries: [getStubTodo({ id: 2 }), getStubTodo({ id: 3 })],
        loading: false,
      });
    });

    it('should sort todos by id with completed todos at the end', function() {
      const result = todosApiSlice.reducer(
        {
          entries: [],
          loading: true,
        },
        {
          type: 'todosApi/list/fulfilled',
          payload: [
            getStubTodo({ id: 1, completed: true }),
            getStubTodo({ id: 3 }),
            getStubTodo({ id: 2 }),
          ],
        },
      );
      expect(result).toEqual({
        entries: [
          getStubTodo({ id: 2 }),
          getStubTodo({ id: 3 }),
          getStubTodo({ id: 1, completed: true }),
        ],
        loading: false,
      });
    });

    it('should filter out archived todos', function() {
      const result = todosApiSlice.reducer(
        {
          entries: [],
          loading: true,
        },
        {
          type: 'todosApi/list/fulfilled',
          payload: [getStubTodo({ archived: true })],
        },
      );
      expect(result).toEqual({
        entries: [],
        loading: false,
      });
    });
  });

  describe('todosApi/update/fulfilled', function() {
    it('update existing todos', function() {
      const updatedTodo = getStubTodo({
        id: 1,
        description: 'new description',
      });
      const result = todosApiSlice.reducer(
        {
          entries: [getStubTodo({ id: 1 }), getStubTodo({ id: 2 })],
          loading: false,
        },
        {
          type: 'todosApi/update/fulfilled',
          payload: updatedTodo,
        },
      );
      expect(result).toEqual({
        entries: [updatedTodo, getStubTodo({ id: 2 })],
        loading: false,
      });
    });

    it('should sort todos by id with completed todos at the end', function() {
      const completedTodo = getStubTodo({ id: 1, completed: true });
      const result = todosApiSlice.reducer(
        {
          entries: [
            getStubTodo({ id: 1 }),
            getStubTodo({ id: 2 }),
            getStubTodo({ id: 3 }),
          ],
          loading: false,
        },
        {
          type: 'todosApi/update/fulfilled',
          payload: completedTodo,
        },
      );
      expect(result).toEqual({
        entries: [
          getStubTodo({ id: 2 }),
          getStubTodo({ id: 3 }),
          completedTodo,
        ],
        loading: false,
      });
    });

    it('should filter out archived todos', function() {
      const result = todosApiSlice.reducer(
        {
          entries: [getStubTodo()],
          loading: false,
        },
        {
          type: 'todosApi/update/fulfilled',
          payload: getStubTodo({ archived: true }),
        },
      );
      expect(result).toEqual({
        entries: [],
        loading: false,
      });
    });
  });
});

function getStubTodo(todoPatch = {}) {
  return Object.assign(
    {
      id: 1,
      description: 'stub todo',
      completed: false,
    },
    todoPatch,
  );
}

export {};
