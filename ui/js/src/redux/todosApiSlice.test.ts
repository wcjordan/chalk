import '../__mocks__/matchMediaMock';
import fetchMock from 'fetch-mock-jest';
import {
  createTodo,
  getTodosApi,
  listTodos,
  todosApiSlice,
} from './todosApiSlice';
import { setupStore } from './store';
import { FILTER_STATUS } from './types';

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

    const store = setupStore({
      workspace: {
        filterLabels: {},
      },
    });
    await store.dispatch(createTodo(stubDescription));

    // Verify todo is created and in the store
    expect(store.getState().todosApi.entries).toEqual([stubTodo]);

    // Verify the POST request included empty labels since no filters are active
    verifyRequestIncludesLabels([]);

    // Verify we make the server request
    expect(fetchMock).toBeDone();
  });

  it('should create todo with active filter labels', async function () {
    const stubDescription = 'test todo with labels';
    const stubTodo = getStubTodo({
      description: stubDescription,
      labels: ['work', 'urgent'],
    });
    fetchMock.postOnce(getTodosApi(), {
      body: stubTodo,
    });

    const store = setupStore({
      workspace: {
        filterLabels: {
          work: FILTER_STATUS.Active,
          urgent: FILTER_STATUS.Active,
        },
      },
    });
    await store.dispatch(createTodo(stubDescription));

    // Verify todo is created with labels
    expect(store.getState().todosApi.entries).toEqual([stubTodo]);

    // Verify the POST request included empty labels since no filters are active
    verifyRequestIncludesLabels(['work', 'urgent']);

    // Verify we make the server request
    expect(fetchMock).toBeDone();
  });

  it('should create todo with empty labels when only Unlabeled filter active', async function () {
    const stubDescription = 'test unlabeled todo';
    const stubTodo = getStubTodo({ description: stubDescription, labels: [] });
    fetchMock.postOnce(getTodosApi(), {
      body: stubTodo,
    });

    const store = setupStore({
      workspace: {
        filterLabels: {
          Unlabeled: FILTER_STATUS.Active,
        },
      },
    });
    await store.dispatch(createTodo(stubDescription));

    // Verify the POST request included empty labels since no filters are active
    verifyRequestIncludesLabels([]);

    // Verify we make the server request
    expect(fetchMock).toBeDone();
  });

  it('should create todo with only active labels, excluding inverted', async function () {
    const stubDescription = 'test todo with mixed filters';
    const stubTodo = getStubTodo({
      description: stubDescription,
      labels: ['work'],
    });
    fetchMock.postOnce(getTodosApi(), {
      body: stubTodo,
    });

    const store = setupStore({
      workspace: {
        filterLabels: {
          work: FILTER_STATUS.Active,
          backlog: FILTER_STATUS.Inverted,
        },
      },
    });
    await store.dispatch(createTodo(stubDescription));

    // Verify the POST request included empty labels since no filters are active
    verifyRequestIncludesLabels(['work']);

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
    pendingCreates: [],
    pendingArchives: [],
  };

  it('should return the initial state', function () {
    expect(todosApiSlice.reducer(undefined, {})).toEqual(initialState);
  });

  describe('todosApi/create/fulfilled', function () {
    it('should add new todo to entries and track as pending create', function () {
      const result = todosApiSlice.reducer(initialState, {
        type: 'todosApi/create/fulfilled',
        payload: getStubTodo(),
      });
      expect(result).toEqual({
        entries: [getStubTodo()],
        initialLoad: true,
        loading: false,
        pendingCreates: [1],
        pendingArchives: [],
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
          pendingCreates: [],
          pendingArchives: [],
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
        pendingCreates: [3],
        pendingArchives: [],
      });
    });

    it('should filter out archived todos', function () {
      const result = todosApiSlice.reducer(
        {
          entries: [],
          initialLoad: false,
          loading: false,
          pendingCreates: [],
          pendingArchives: [],
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
        pendingCreates: [1],
        pendingArchives: [],
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
        pendingCreates: [],
        pendingArchives: [],
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
          pendingCreates: [],
          pendingArchives: [],
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
        pendingCreates: [],
        pendingArchives: [],
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
          pendingCreates: [],
          pendingArchives: [],
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
        pendingCreates: [],
        pendingArchives: [],
      });
    });

    it('should replace entries with loaded todos', function () {
      const result = todosApiSlice.reducer(
        {
          entries: [getStubTodo({ id: 1, description: 'overwritten' })],
          initialLoad: true,
          loading: true,
          pendingCreates: [],
          pendingArchives: [],
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
        pendingCreates: [],
        pendingArchives: [],
      });
    });

    it('should sort todos with completed todos at the end maintaining the order for the others', function () {
      const result = todosApiSlice.reducer(
        {
          entries: [],
          initialLoad: true,
          loading: true,
          pendingCreates: [],
          pendingArchives: [],
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
        pendingCreates: [],
        pendingArchives: [],
      });
    });

    it('should filter out archived todos', function () {
      const result = todosApiSlice.reducer(
        {
          entries: [],
          initialLoad: true,
          loading: true,
          pendingCreates: [],
          pendingArchives: [],
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
        pendingCreates: [],
        pendingArchives: [],
      });
    });

    it('should preserve local changes when server has stale version', function () {
      const localTodo = getStubTodo({
        id: 1,
        description: 'local changes',
        version: 3,
      });
      const staleTodo = getStubTodo({
        id: 1,
        description: 'old server state',
        version: 2,
      });
      const result = todosApiSlice.reducer(
        {
          entries: [localTodo],
          initialLoad: false,
          loading: true,
          pendingCreates: [],
          pendingArchives: [],
        },
        {
          type: 'todosApi/list/fulfilled',
          payload: [staleTodo],
        },
      );
      // Local todo should be preserved (stale update skipped)
      expect(result).toEqual({
        entries: [localTodo],
        initialLoad: false,
        loading: false,
        pendingCreates: [],
        pendingArchives: [],
      });
    });

    it('should apply server updates when version is fresh', function () {
      const localTodo = getStubTodo({
        id: 1,
        description: 'local state',
        version: 2,
      });
      const freshTodo = getStubTodo({
        id: 1,
        description: 'new server state',
        version: 3,
      });
      const result = todosApiSlice.reducer(
        {
          entries: [localTodo],
          initialLoad: false,
          loading: true,
          pendingCreates: [],
          pendingArchives: [],
        },
        {
          type: 'todosApi/list/fulfilled',
          payload: [freshTodo],
        },
      );
      // Todo should be updated with fresh server data
      expect(result).toEqual({
        entries: [freshTodo],
        initialLoad: false,
        loading: false,
        pendingCreates: [],
        pendingArchives: [],
      });
    });

    it('should preserve locally-created todo when stale list response does not include it', function () {
      const localTodo = getStubTodo({ id: 99, description: 'new local todo' });
      const serverTodo = getStubTodo({ id: 1, description: 'server todo' });
      const result = todosApiSlice.reducer(
        {
          entries: [serverTodo, localTodo],
          initialLoad: false,
          loading: true,
          pendingCreates: [99],
          pendingArchives: [],
        },
        {
          type: 'todosApi/list/fulfilled',
          payload: [serverTodo],
        },
      );
      // Locally-created todo should be preserved
      expect(result).toEqual({
        entries: [serverTodo, localTodo],
        initialLoad: false,
        loading: false,
        pendingCreates: [99],
        pendingArchives: [],
      });
    });

    it('should clear pendingCreates when server list includes the todo', function () {
      const localTodo = getStubTodo({ id: 99, description: 'new local todo' });
      const result = todosApiSlice.reducer(
        {
          entries: [localTodo],
          initialLoad: false,
          loading: true,
          pendingCreates: [99],
          pendingArchives: [],
        },
        {
          type: 'todosApi/list/fulfilled',
          payload: [localTodo],
        },
      );
      // pendingCreates should be cleared since server now includes the todo
      expect(result).toEqual({
        entries: [localTodo],
        initialLoad: false,
        loading: false,
        pendingCreates: [],
        pendingArchives: [],
      });
    });

    it('should suppress archived todo from stale list response', function () {
      const staleTodo = getStubTodo({
        id: 1,
        description: 'archived todo',
        archived: false,
        version: 1,
      });
      const result = todosApiSlice.reducer(
        {
          entries: [],
          initialLoad: false,
          loading: true,
          pendingCreates: [],
          pendingArchives: [1],
        },
        {
          type: 'todosApi/list/fulfilled',
          payload: [staleTodo],
        },
      );
      // Archived todo should not reappear
      expect(result).toEqual({
        entries: [],
        initialLoad: false,
        loading: false,
        pendingCreates: [],
        pendingArchives: [1],
      });
    });

    it('should clear pendingArchives when server catches up', function () {
      const result = todosApiSlice.reducer(
        {
          entries: [],
          initialLoad: false,
          loading: true,
          pendingCreates: [],
          pendingArchives: [1],
        },
        {
          type: 'todosApi/list/fulfilled',
          // Server no longer includes the todo (it was archived server-side)
          payload: [],
        },
      );
      // pendingArchives should be cleared since server has caught up
      expect(result).toEqual({
        entries: [],
        initialLoad: false,
        loading: false,
        pendingCreates: [],
        pendingArchives: [],
      });
    });

    it('should clear pendingArchives when server shows todo as archived', function () {
      const archivedTodo = getStubTodo({
        id: 1,
        description: 'archived todo',
        archived: true,
        version: 2,
      });
      const result = todosApiSlice.reducer(
        {
          entries: [],
          initialLoad: false,
          loading: true,
          pendingCreates: [],
          pendingArchives: [1],
        },
        {
          type: 'todosApi/list/fulfilled',
          payload: [archivedTodo],
        },
      );
      // pendingArchives should be cleared and archived todo filtered out
      expect(result).toEqual({
        entries: [],
        initialLoad: false,
        loading: false,
        pendingCreates: [],
        pendingArchives: [],
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
          pendingCreates: [],
          pendingArchives: [],
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
        pendingCreates: [],
        pendingArchives: [],
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
          pendingCreates: [],
          pendingArchives: [],
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
        pendingCreates: [],
        pendingArchives: [],
      });
    });

    it('should filter out archived todos and track as pending archive', function () {
      const result = todosApiSlice.reducer(
        {
          entries: [getStubTodo()],
          initialLoad: false,
          loading: false,
          pendingCreates: [],
          pendingArchives: [],
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
        pendingCreates: [],
        pendingArchives: [1],
      });
    });

    it('should skip stale updates (server version < local version)', function () {
      const localTodo = getStubTodo({
        id: 1,
        description: 'local changes',
        version: 3,
      });
      const staleUpdate = getStubTodo({
        id: 1,
        description: 'old server state',
        version: 2,
      });
      const result = todosApiSlice.reducer(
        {
          entries: [localTodo],
          initialLoad: false,
          loading: false,
          pendingCreates: [],
          pendingArchives: [],
        },
        {
          type: 'todosApi/update/fulfilled',
          payload: staleUpdate,
        },
      );
      // Local todo should remain unchanged (stale update skipped)
      expect(result).toEqual({
        entries: [localTodo],
        initialLoad: false,
        loading: false,
        pendingCreates: [],
        pendingArchives: [],
      });
    });

    it('should apply fresh updates (server version >= local version)', function () {
      const localTodo = getStubTodo({
        id: 1,
        description: 'local state',
        version: 2,
      });
      const freshUpdate = getStubTodo({
        id: 1,
        description: 'new server state',
        version: 3,
      });
      const result = todosApiSlice.reducer(
        {
          entries: [localTodo],
          initialLoad: false,
          loading: false,
          pendingCreates: [],
          pendingArchives: [],
        },
        {
          type: 'todosApi/update/fulfilled',
          payload: freshUpdate,
        },
      );
      // Todo should be updated with fresh server data
      expect(result).toEqual({
        entries: [freshUpdate],
        initialLoad: false,
        loading: false,
        pendingCreates: [],
        pendingArchives: [],
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
      version: 1,
    },
    todoPatch,
  );
}

/**
 * Check that the body of the last call to the todos API includes the expected labels.
 * This is used to verify that when we create a todo, we include the correct labels based on the active filters.
 *
 * @param {string[]} expectedLabels - The labels that we expect to be included in the request body of the last call to the todos API.
 */
function verifyRequestIncludesLabels(expectedLabels) {
  const lastCall = fetchMock.lastCall(getTodosApi());
  const requestBody = JSON.parse(lastCall[1].body);
  expect(requestBody.labels).toEqual(expectedLabels);
}

export {};
