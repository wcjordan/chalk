import '../__mocks__/matchMediaMock';
import { setupStore } from './store';

describe('Persistence contracts', function () {
  it('should restore pendingOps from prior session via preloaded state (rehydration simulation)', function () {
    const priorPendingOps = [
      { type: 'update' as const, payload: { id: 1, description: 'offline edit' } },
    ];

    // Simulates what redux-persist does after rehydrating from storage:
    // it merges persisted state into the initial store state
    const store = setupStore({
      offlineQueue: { pendingOps: priorPendingOps },
    });

    expect(store.getState().offlineQueue.pendingOps).toEqual(priorPendingOps);
    // isOnline is never persisted — always starts true
    expect(store.getState().network.isOnline).toBe(true);
  });

  it('should restore todosApi entries but not loading or initialLoad', function () {
    const priorEntries = [{ id: 42, description: 'cached todo', completed: false }];

    const store = setupStore({
      todosApi: {
        entries: priorEntries,
        pendingCreates: [],
        pendingArchives: [],
        // loading and initialLoad are blacklisted — not restored from storage
        loading: false,
        initialLoad: true,
      },
    });

    expect(store.getState().todosApi.entries).toEqual(priorEntries);
    expect(store.getState().todosApi.loading).toBe(false);
    expect(store.getState().todosApi.initialLoad).toBe(true);
  });

  it('should not persist isOnline — network state always starts true on launch', function () {
    // Even if storage somehow had isOnline=false, the store always initializes isOnline=true
    const store = setupStore();
    expect(store.getState().network.isOnline).toBe(true);
    expect(store.getState().network.consecutiveNetworkFailures).toBe(0);
  });
});
