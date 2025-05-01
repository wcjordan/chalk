import { useEffect } from 'react';
import { Platform } from 'react-native';
import { record } from 'rrweb';
import { recordSessionEvents } from '../redux/reducers';
import { useAppDispatch } from './hooks';
import { getEnvFlags } from '../helpers';

export function useSessionRecorder() {
  // Don't record on mobile or when running unit tests
  // This is because rrweb is not supported on mobile
  if (getEnvFlags().ENVIRONMENT === 'test' || Platform.OS !== 'web') {
    return;
  }

  const dispatch = useAppDispatch();
  useEffect(() => {
    let events: object[] = [];
    const sessionGuid: string = crypto.randomUUID();

    record({
      emit(event) {
        events.push(event);
      },
    });

    // save events every 10 seconds
    const intervalId = setInterval(
      () => {
        dispatch(recordSessionEvents(sessionGuid, events))
        // reset the events array
        events = [];
      },
    10 * 1000);

    return () => {
      clearInterval(intervalId);
    };
  }, []);
}
