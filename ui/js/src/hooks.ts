import { useEffect } from 'react';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';

import type { RootState, AppDispatch } from './redux/store';
import { listLabels, listTodos } from './redux/reducers';
import { getEnvFlags } from './helpers';

export function useDataLoader() {
  if (getEnvFlags().ENVIRONMENT === 'test') {
    return;
  }

  const dispatch = useAppDispatch();
  useEffect(() => {
    dispatch(listLabels());

    const intervalId = window.setInterval(
      () => dispatch(listTodos()),
      10000,
    );

    return () => {
      window.clearInterval(intervalId);
    };
  }, []);
}

// Use throughout your app instead of plain `useDispatch` and `useSelector`
export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
