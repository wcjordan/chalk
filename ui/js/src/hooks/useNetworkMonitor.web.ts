import { useEffect } from 'react';
import { setOnlineStatus } from '../redux/networkSlice';
import { useAppDispatch } from './hooks';

export function useNetworkMonitor() {
  const dispatch = useAppDispatch();

  useEffect(() => {
    dispatch(setOnlineStatus(navigator.onLine));

    const handleOnline = () => dispatch(setOnlineStatus(true));
    const handleOffline = () => dispatch(setOnlineStatus(false));

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
}
