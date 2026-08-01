import { useEffect } from 'react';
import offlineQueueSlice from '../redux/offlineQueueSlice';
import { OfflineOperation } from '../redux/types';
import { useAppDispatch } from './hooks';

const OFFLINE_QUEUE_STORAGE_KEY = 'persist:offlineQueue';

// redux-persist stores each slice as a JSON string of an object whose values
// are themselves JSON strings (see createPersistoid's per-key `serialize`),
// so decoding requires unwrapping two layers of JSON.
function parsePendingOps(rawValue: string): OfflineOperation[] {
  const outer = JSON.parse(rawValue) as { pendingOps?: string };
  return outer.pendingOps ? JSON.parse(outer.pendingOps) : [];
}

// Keeps this tab's offline queue in sync with other tabs' writes to the
// shared persisted queue, so a tab doesn't resend an op another tab already
// flushed. Paired with the navigator.locks usage in flushOfflineQueue.
export function useOfflineQueueSync() {
  const dispatch = useAppDispatch();

  useEffect(() => {
    const handleStorage = (event: StorageEvent) => {
      if (event.key !== OFFLINE_QUEUE_STORAGE_KEY || event.newValue === null) {
        return;
      }

      try {
        const pendingOps = parsePendingOps(event.newValue);
        dispatch(offlineQueueSlice.actions.replaceQueue(pendingOps));
      } catch (error) {
        console.warn('Failed to sync offline queue across tabs', error);
      }
    };

    window.addEventListener('storage', handleStorage);
    return () => {
      window.removeEventListener('storage', handleStorage);
    };
  }, [dispatch]);
}
