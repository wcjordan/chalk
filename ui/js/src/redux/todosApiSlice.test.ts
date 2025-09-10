import '../__mocks__/matchMediaMock';
import fetchMock from 'fetch-mock-jest';
import {
  createTodo,
  getTodosApi,
  listTodos,
  todosApiSlice,
} from './todosApiSlice';
import { setupStore } from './store';

// NOTE (jordan) updateTodo tested in reducers.test.ts
describe('createTodo', function () {
  afterEach(function () {
    fetchMock.restore();
  });

  it('should make a POST request and dispatch actions', async function () {
    const stubDescription = 'test todo';
    const stubTodo = getStubTodo({ description: stubDescription });
    fetchMock.postOnce(getTodosApi(), {
      body: stubTodo,
    });

    const store = setupStore();
    await store.dispatch(createTodo(stubDescription));

    // Verify todo is created and in the store
    expect(store.getState().todosApi.entries).toEqual([stubTodo]);

    // Verify we make the server request
    expect(fetchMock).toBeDone();
  });
});

describe('listTodos', function () {
  afterEach(function () {
    fetchMock.restore();
  });

  it('should make a GET request and dispatch actions', async function () {
    const stubTodos = [
      getStubTodo({ id: 1, description: 'todo 1' }),
      getStubTodo({ id: 2, description: 'todo 2' }),
    ];
    fetchMock.getOnce(getTodosApi(), {
      body: stubTodos,
    });

    const store = setupStore();
    await store.dispatch(listTodos());

    // Verify todos are loaded
    expect(store.getState().todosApi.loading).toEqual(false);
    expect(store.getState().todosApi.entries).toEqual(stubTodos);

    // Verify we make the server request
    expect(fetchMock).toBeDone();
  });

  it('should do nothing if todos are already loading', async function () {
    fetchMock.mock('*', 200);
    const store = setupStore({ todosApi: { loading: true } });
    await store.dispatch(listTodos());

    // Verify we make the server request
    expect(fetchMock).not.toHaveFetched('*');
  });
});

describe('todosApiSlice reducer', function () {
  const initialState = {
    entries: [],
    initialLoad: true,
    loading: false,
  };

  it('should return the initial state', function () {
    expect(todosApiSlice.reducer(undefined, {})).toEqual(initialState);
  });

  describe('todosApi/create/fulfilled', function () {
    it('should add new todo to entries', function () {
      const result = todosApiSlice.reducer(initialState, {
        type: 'todosApi/create/fulfilled',
        payload: getStubTodo(),
      });
      expect(result).toEqual({
        entries: [getStubTodo()],
        initialLoad: true,
        loading: false,
      });
    });

    it('should sort todos with completed todos at the end maintaining the order for the others', function () {
      const result = todosApiSlice.reducer(
        {
          entries: [
            getStubTodo({ id: 2 }),
            getStubTodo({ id: 1, completed: true }),
          ],
          initialLoad: false,
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
        initialLoad: false,
        loading: false,
      });
    });

    it('should filter out archived todos', function () {
      const result = todosApiSlice.reducer(
        {
          entries: [],
          initialLoad: false,
          loading: false,
        },
        {
          type: 'todosApi/create/fulfilled',
          payload: getStubTodo({ id: 1, archived: true }),
        },
      );
      expect(result).toEqual({
        entries: [],
        initialLoad: false,
        loading: false,
      });
    });
  });

  describe('todosApi/list/pending', function () {
    it('should mark loading as in progress', function () {
      const result = todosApiSlice.reducer(initialState, {
        type: 'todosApi/list/pending',
      });
      expect(result).toEqual({
        entries: [],
        initialLoad: true,
        loading: true,
      });
    });
  });

  describe('todosApi/list/rejected', function () {
    let spy;

    beforeEach(function () {
      spy = jest.spyOn(console, 'warn').mockImplementation();
    });

    afterEach(function () {
      spy.mockRestore();
    });

    it('should mark loading as no longer in progress', function () {
      const result = todosApiSlice.reducer(
        {
          entries: [],
          initialLoad: true,
          loading: true,
        },
        {
          error: { message: 'test error' },
          type: 'todosApi/list/rejected',
        },
      );
      expect(result).toEqual({
        entries: [],
        initialLoad: false,
        loading: false,
      });
      expect(console.warn).toHaveBeenCalledWith(
        'Loading Todo failed. test error',
      );
    });
  });

  describe('todosApi/list/fulfilled', function () {
    it('should mark loading as no longer in progress', function () {
      const result = todosApiSlice.reducer(
        {
          entries: [],
          initialLoad: true,
          loading: true,
        },
        {
          type: 'todosApi/list/fulfilled',
          payload: [],
        },
      );
      expect(result).toEqual({
        entries: [],
        initialLoad: false,
        loading: false,
      });
    });

    it('should replace entries with loaded todos', function () {
      const result = todosApiSlice.reducer(
        {
          entries: [getStubTodo({ id: 1, description: 'overwritten' })],
          initialLoad: true,
          loading: true,
        },
        {
          type: 'todosApi/list/fulfilled',
          payload: [getStubTodo({ id: 2 }), getStubTodo({ id: 3 })],
        },
      );
      expect(result).toEqual({
        entries: [getStubTodo({ id: 2 }), getStubTodo({ id: 3 })],
        initialLoad: false,
        loading: false,
      });
    });

    it('should sort todos with completed todos at the end maintaining the order for the others', function () {
      const result = todosApiSlice.reducer(
        {
          entries: [],
          initialLoad: true,
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
          getStubTodo({ id: 3 }),
          getStubTodo({ id: 2 }),
          getStubTodo({ id: 1, completed: true }),
        ],
        initialLoad: false,
        loading: false,
      });
    });

    it('should filter out archived todos', function () {
      const result = todosApiSlice.reducer(
        {
          entries: [],
          initialLoad: true,
          loading: true,
        },
        {
          type: 'todosApi/list/fulfilled',
          payload: [getStubTodo({ archived: true })],
        },
      );
      expect(result).toEqual({
        entries: [],
        initialLoad: false,
        loading: false,
      });
    });
  });

  describe('todosApi/update/fulfilled', function () {
    it('update existing todos', function () {
      const updatedTodo = getStubTodo({
        id: 1,
        description: 'new description',
      });
      const result = todosApiSlice.reducer(
        {
          entries: [getStubTodo({ id: 1 }), getStubTodo({ id: 2 })],
          initialLoad: false,
          loading: false,
        },
        {
          type: 'todosApi/update/fulfilled',
          payload: updatedTodo,
        },
      );
      expect(result).toEqual({
        entries: [updatedTodo, getStubTodo({ id: 2 })],
        initialLoad: false,
        loading: false,
      });
    });

    it('should sort todos with completed todos at the end maintaining the order for the others', function () {
      const completedTodo = getStubTodo({ id: 1, completed: true });
      const result = todosApiSlice.reducer(
        {
          entries: [
            getStubTodo({ id: 1 }),
            getStubTodo({ id: 2 }),
            getStubTodo({ id: 3 }),
          ],
          initialLoad: false,
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
        initialLoad: false,
        loading: false,
      });
    });

    it('should filter out archived todos', function () {
      const result = todosApiSlice.reducer(
        {
          entries: [getStubTodo()],
          initialLoad: false,
          loading: false,
        },
        {
          type: 'todosApi/update/fulfilled',
          payload: getStubTodo({ archived: true }),
        },
      );
      expect(result).toEqual({
        entries: [],
        initialLoad: false,
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
