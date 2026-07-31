import { renderHook } from '@testing-library/react-hooks';
import offlineQueueSlice from '../redux/offlineQueueSlice';
import { useOfflineQueueSync } from './useOfflineQueueSync.web';

const mockDispatch = jest.fn();
jest.mock('./hooks', () => ({
  useAppDispatch: () => mockDispatch,
}));

function dispatchStorageEvent(key: string | null, newValue: string | null) {
  window.dispatchEvent(
    new StorageEvent('storage', { key: key ?? undefined, newValue }),
  );
}

describe('useOfflineQueueSync', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should replace the queue when another tab updates the persisted offline queue', () => {
    renderHook(() => useOfflineQueueSync());

    const pendingOps = [{ type: 'update', payload: { id: 1 } }];
    dispatchStorageEvent(
      'persist:offlineQueue',
      JSON.stringify({ pendingOps: JSON.stringify(pendingOps) }),
    );

    expect(mockDispatch).toHaveBeenCalledWith(
      offlineQueueSlice.actions.replaceQueue(pendingOps),
    );
  });

  it('should replace with an empty queue when another tab flushes to empty', () => {
    renderHook(() => useOfflineQueueSync());

    dispatchStorageEvent(
      'persist:offlineQueue',
      JSON.stringify({ pendingOps: JSON.stringify([]) }),
    );

    expect(mockDispatch).toHaveBeenCalledWith(
      offlineQueueSlice.actions.replaceQueue([]),
    );
  });

  it('should ignore storage events for unrelated keys', () => {
    renderHook(() => useOfflineQueueSync());

    dispatchStorageEvent('persist:todosApi', JSON.stringify({}));

    expect(mockDispatch).not.toHaveBeenCalled();
  });

  it('should ignore storage clear events (newValue is null)', () => {
    renderHook(() => useOfflineQueueSync());

    dispatchStorageEvent('persist:offlineQueue', null);

    expect(mockDispatch).not.toHaveBeenCalled();
  });

  it('should not throw and should not dispatch on malformed storage values', () => {
    renderHook(() => useOfflineQueueSync());

    expect(() =>
      dispatchStorageEvent('persist:offlineQueue', 'not-json'),
    ).not.toThrow();
    expect(mockDispatch).not.toHaveBeenCalled();
  });

  it('should remove the storage listener on unmount', () => {
    const { unmount } = renderHook(() => useOfflineQueueSync());
    unmount();

    const pendingOps = [{ type: 'update', payload: { id: 1 } }];
    dispatchStorageEvent(
      'persist:offlineQueue',
      JSON.stringify({ pendingOps: JSON.stringify(pendingOps) }),
    );

    expect(mockDispatch).not.toHaveBeenCalled();
  });
});
