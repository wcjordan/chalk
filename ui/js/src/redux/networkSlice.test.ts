import '../__mocks__/matchMediaMock';
import fetchMock from 'fetch-mock-jest';
import networkSlice, { setOnlineStatus } from './networkSlice';
import { listTodos as listTodosApi } from './todosApiSlice';
import { getTodosApi } from './todosApiSlice';
import { setupStore } from './store';

describe('networkSlice reducer', function () {
  it('should initialise with isOnline: true and consecutiveNetworkFailures: 0', function () {
    expect(networkSlice.reducer(undefined, { type: '@@INIT' })).toEqual({
      isOnline: true,
      consecutiveNetworkFailures: 0,
    });
  });

  describe('setOnlineStatus', function () {
    it('should set isOnline to false', function () {
      const result = networkSlice.reducer(
        { isOnline: true, consecutiveNetworkFailures: 0 },
        setOnlineStatus(false),
      );
      expect(result.isOnline).toBe(false);
    });

    it('should set isOnline to true and reset consecutiveNetworkFailures', function () {
      const result = networkSlice.reducer(
        { isOnline: false, consecutiveNetworkFailures: 3 },
        setOnlineStatus(true),
      );
      expect(result.isOnline).toBe(true);
      expect(result.consecutiveNetworkFailures).toBe(0);
    });
  });
});

describe('networkSlice extraReducers', function () {
  afterEach(function () {
    fetchMock.restore();
  });

  it('listTodos.fulfilled resets consecutiveNetworkFailures and sets isOnline: true', async function () {
    fetchMock.getOnce(getTodosApi(), { body: [] });

    const store = setupStore({
      network: { isOnline: false, consecutiveNetworkFailures: 3 },
    });
    await store.dispatch(listTodosApi());

    expect(store.getState().network.isOnline).toBe(true);
    expect(store.getState().network.consecutiveNetworkFailures).toBe(0);
  });

  it('listTodos.rejected with TypeError increments consecutiveNetworkFailures', async function () {
    fetchMock.getOnce(getTodosApi(), { throws: new TypeError('Network error') });

    const store = setupStore({
      network: { isOnline: true, consecutiveNetworkFailures: 0 },
    });
    await store.dispatch(listTodosApi());

    expect(store.getState().network.consecutiveNetworkFailures).toBe(1);
    expect(store.getState().network.isOnline).toBe(true);
  });

  it('listTodos.rejected with TypeError sets isOnline: false at 2 consecutive failures', async function () {
    fetchMock.get(getTodosApi(), { throws: new TypeError('Network error') });

    const store = setupStore({
      network: { isOnline: true, consecutiveNetworkFailures: 0 },
    });

    await store.dispatch(listTodosApi());
    expect(store.getState().network.consecutiveNetworkFailures).toBe(1);
    expect(store.getState().network.isOnline).toBe(true);

    await store.dispatch(listTodosApi());
    expect(store.getState().network.consecutiveNetworkFailures).toBe(2);
    expect(store.getState().network.isOnline).toBe(false);
  });

  it('listTodos.rejected with non-TypeError does NOT change isOnline or consecutiveNetworkFailures', async function () {
    fetchMock.getOnce(getTodosApi(), { status: 500 });

    const store = setupStore({
      network: { isOnline: true, consecutiveNetworkFailures: 0 },
    });
    await store.dispatch(listTodosApi());

    expect(store.getState().network.isOnline).toBe(true);
    expect(store.getState().network.consecutiveNetworkFailures).toBe(0);
  });
});

export {};
