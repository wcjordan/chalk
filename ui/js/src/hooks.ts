import { useEffect } from 'react';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import { record } from 'rrweb';

import type { RootState, AppDispatch } from './redux/store';
import { listLabels, listTodos, recordSessionEvents } from './redux/reducers';
import { getEnvFlags } from './helpers';

export function useDataLoader() {
  if (getEnvFlags().ENVIRONMENT === 'test') {
    return;
  }

  const dispatch = useAppDispatch();
  useEffect(() => {
    dispatch(listLabels());
    dispatch(listTodos());

    const intervalId = window.setInterval(
      () => dispatch(listTodos()),
      10000,
    );

    return () => {
      window.clearInterval(intervalId);
    };
  }, []);
}

export function useSessionRecorder() {
  if (getEnvFlags().ENVIRONMENT === 'test') {
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

// Use throughout your app instead of plain `useDispatch` and `useSelector`
export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
